# filename: backend/decision_engine.py

def get_final_verdict(img_res, cap_res, hash_res):
    """
    Implements the strict decision logic:
    If ANY component is fake/misleading -> BLUR.
    Only if ALL are safe -> VISIBLE.
    """
    
    # 1. Define "Unsafe" flags
    unsafe_image_statuses = ["fake", "ai_generated"]
    unsafe_caption_statuses = ["fake"]
    unsafe_hashtag_statuses = ["mislead", "violation"]

    # 2. Check Image
    if img_res in unsafe_image_statuses:
        return "BLUR"

    # 3. Check Caption
    if cap_res in unsafe_caption_statuses:
        return "BLUR"

    # 4. Check Hashtags
    if hash_res in unsafe_hashtag_statuses:
        return "BLUR"

    # 5. If we passed all checks
    return "VISIBLE"