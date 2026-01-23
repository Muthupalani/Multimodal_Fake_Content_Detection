# filename: backend/utils.py
import json
import os
from datetime import datetime

DATA_DIR = '../data'
FILE_1 = os.path.join(DATA_DIR, 'extracted_data.json')
FILE_2 = os.path.join(DATA_DIR, 'model_results.json')

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    for f_path in [FILE_1, FILE_2]:
        if not os.path.exists(f_path):
            with open(f_path, 'w') as f: json.dump([], f)

def save_extracted_data(post_id, image_url, caption, hashtags):
    ensure_data_dir()
    entry = {
        "post_id": post_id,
        "image_url": image_url,
        "caption": caption,
        "hashatag": hashtags,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    _append_to_json(FILE_1, entry)

def save_model_scores(image_url, img_score, img_res, caption, cap_score, cap_res, 
                      hashtags, hash_score, hash_res, final_res):
    ensure_data_dir()
    entry = {
        "image_url": image_url,
        "image_score": float(img_score),
        "image_result": img_res,
        "caption": caption,
        "caption_score": float(cap_score),
        "caption_results": cap_res,
        "hastag": hashtags,
        "hashtag_score": float(hash_score),
        "hashatag_results": hash_res,
        "final_verdict": final_res
    }
    _append_to_json(FILE_2, entry)

def _append_to_json(filepath, new_data):
    try:
        with open(filepath, 'r+') as f:
            try:
                data = json.load(f)
            except: data = []
            data.append(new_data)
            f.seek(0)
            json.dump(data, f, indent=4)
    except Exception as e: print(f"JSON Error: {e}")