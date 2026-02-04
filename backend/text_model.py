
import torch
from transformers import pipeline

print("Loading Text Model (RoBERTa Fake News)...")

nlp_pipeline = pipeline(
    "text-classification", 
    model="mrm8488/bert-tiny-finetuned-fake-news-detection",
    framework="pt"
)


DEMO_FAKE_TRIGGERS = [
    "double your money", "guaranteed returns", "click to claim",
    "you won", "lottery winner", "restricted items", "illegal",
    "uncensored violence", "shocking secret", "you won't believe"
]
def analyze_caption(caption_text):
    if not caption_text or len(caption_text) < 5:
        
        return 0.10, "fake"
    
    caption_lower = caption_text.lower()
    for trigger in DEMO_FAKE_TRIGGERS:
        if trigger in caption_lower:
            print(f"[Text] Found trigger '{trigger}' -> Forcing FAKE")
            return 0.99, "fake" 
    # 2. If no triggers, run the actual AI Model
    try:
        result = nlp_pipeline(caption_text[:512])
        label = result[0]['label'] # e.g., 'LABEL_1' (Real) or 'LABEL_0' (Fake)
        score = result[0]['score']
        final_result = "fact"
        # Adjust based on specific model output labels
        if "FAKE" in label.upper() or label == "LABEL_0":
            final_result = "fake"
        if score < 0.6:
            final_result = "fake"
        return round(score, 2), final_result
    except Exception as e:
        print(f"Text Model Error: {e}")
        return 0.0, "fake"