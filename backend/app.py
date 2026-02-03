from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import torch
from transformers import (
    CLIPProcessor, CLIPModel, 
    pipeline, AutoTokenizer, AutoModelForSequenceClassification,
    AutoModel
)
from sentence_transformers import SentenceTransformer
import requests
from PIL import Image
import io
import numpy as np
from torchvision.transforms import Compose, Resize, CenterCrop, Normalize, ToTensor

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["chrome-extension://*"], allow_methods=["*"], allow_headers=["*"])
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
roberta_tokenizer = AutoTokenizer.from_pretrained("roberta-large-mnli")
roberta_model = AutoModelForSequenceClassification.from_pretrained("roberta-large-mnli").to(device)
sentence_bert = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
clip_model_st = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)  
clip_processor_st = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
transform = Compose([
    Resize((224, 224)), CenterCrop(224), ToTensor(),
    Normalize(mean=[0.48145466, 0.4578275, 0.40821073], std=[0.26862954, 0.26130258, 0.27577711])
])
class AnalyzeRequest(BaseModel):
    image_url: str
    caption: str
    hashtags: List[str]
class AnalyzeResponse(BaseModel):
    image_score: float  # 0-1 real <0.7 fake
    caption_score: float  # 0-1 real <0.65 fake
    hashtag_score: float  # 0-1 relevant <0.6 fake
    final_score: float  # Weighted <0.65 blur all
    actions: dict
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_post(request: AnalyzeRequest):
    try:

        image = Image.open(io.BytesIO(requests.get(request.image_url).content))
        image_input = transform(image).unsqueeze(0).to(device)
        real_prompt = "a real photograph taken by camera"
        ai_prompt = "an AI generated image"
        text_inputs = clip_processor(text=[real_prompt, ai_prompt], return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            img_emb = clip_model.get_image_features(image_input)
            text_emb = clip_model.get_text_features(**text_inputs)
            probs = torch.softmax((img_emb @ text_emb.T)[0], dim=0)
            image_score = probs[0].item()  
        inputs = roberta_tokenizer(f"{request.caption} This is real content.", "This is misleading or fake.", return_tensors="pt", truncation=True, padding=True).to(device)
        with torch.no_grad():
            logits = roberta_model(**inputs).logits
            probs = torch.softmax(logits, dim=1)
            caption_score = probs[2].item() if len(probs[0]) > 2 else probs[0][1].item()  # Entailment/real [web:12][web:23]
        # 3. Hashtag relevance (Sentence-BERT caption-hashtags + CLIP img-hashtags)
        if request.hashtags:
            # Text sim: caption vs joined hashtags
            caption_emb = sentence_bert.encode(request.caption)
            ht_emb = sentence_bert.encode(" ".join(request.hashtags))
            text_sim = np.dot(caption_emb, ht_emb) / (np.linalg.norm(caption_emb) * np.linalg.norm(ht_emb))
            # Img-text sim
            ht_text = clip_processor_st(" ".join(request.hashtags), return_tensors="pt").to(device)
            with torch.no_grad():
                ht_emb_clip = clip_model_st.get_text_features(**ht_text)
                img_emb_clip = clip_model_st.get_image_features(image_input)
                img_sim = img_emb_clip @ ht_emb_clip.T
                img_sim = img_sim.softmax(dim=1).cpu().numpy()[0][0]
            hashtag_score = (text_sim + img_sim) / 2
        else:
            hashtag_score = 1.0
        # Weighted final + actions
        final_score = 0.5 * image_score + 0.3 * caption_score + 0.2 * hashtag_score
        actions = {
            "blur_image": image_score < 0.7,
            "hide_caption": caption_score < 0.65,
            "hide_hashtags": hashtag_score < 0.6,
            "blur_post": final_score < 0.65
        }
        return AnalyzeResponse(image_score=image_score, caption_score=caption_score, hashtag_score=hashtag_score,
                               final_score=final_score, actions=actions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
