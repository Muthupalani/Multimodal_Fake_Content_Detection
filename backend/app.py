# filename: backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from utils import save_extracted_data, save_model_scores
from image_model import analyze_image
from text_model import analyze_caption
from hashtag_model import analyze_hashtags
from decision_engine import get_final_verdict

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_content():
    try:
        data = request.json
        image_url = data.get('image_url', '')
        caption = data.get('caption', '')
        hashtags = data.get('hashtags', []) 
        
        post_id = str(uuid.uuid4())[:8]
        print(f"[*] Post ID: {post_id} | Analyzing...")

        # 1. Save Raw Data
        save_extracted_data(post_id, image_url, caption, hashtags)

        # 2. Run High-Accuracy Models
        img_score, img_result = analyze_image(image_url)
        cap_score, cap_result = analyze_caption(caption)
        hash_score, hash_result = analyze_hashtags(hashtags, image_url)

        # 3. Decision
        final_result = get_final_verdict(img_result, cap_result, hash_result)

        # 4. Save Scores
        save_model_scores(
            image_url, img_score, img_result, 
            caption, cap_score, cap_result, 
            hashtags, hash_score, hash_result, 
            final_result
        )

        return jsonify({
            "post_id": post_id,
            "final_decision": final_result,
            "image_analysis": {"result": img_result},
            "caption_analysis": {"result": cap_result},
            "hashtag_analysis": {"result": hash_result}
        }), 200

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 HIGH ACCURACY SERVER STARTING...")
    app.run(debug=True, port=5000)