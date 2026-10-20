import rules_v38
from decimal import Decimal, ROUND_HALF_UP

def validate_scores_only(ai_scores: dict, content_type: str) -> bool:
    criteria = rules_v38.get_criteria_by_type(content_type)
    if criteria is None:
        raise ValueError(f"Loại '{content_type}' không hợp lệ.")
    if not isinstance(ai_scores, dict):
        raise ValueError("Trường 'scores' phải là dict.")
        
    expected_ids = set(criteria.keys())
    received_ids = set(ai_scores.keys())
    if received_ids != expected_ids:
        raise ValueError(f"ID điểm không khớp. Thừa: {received_ids - expected_ids}, Thiếu: {expected_ids - received_ids}")
        
    for crit_id, score in ai_scores.items():
        if type(score) is not int or not (0 <= score <= 10):
            raise ValueError(f"Điểm {crit_id} phải là số nguyên 0-10.")
    return True

def validate_full_report(ai_json: dict, content_type: str, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict):
        raise ValueError("Dữ liệu AI không phải JSON.")
    for k in ["scores", "errors", "rewrite"]:
        if k not in ai_json:
            raise ValueError(f"Thiếu trường '{k}'.")

    validate_scores_only(ai_json["scores"], content_type)

    errors = ai_json["errors"]
    if not isinstance(errors, list):
        raise ValueError("Trường 'errors' phải là list.")
        
    for err in errors:
        if not isinstance(err, dict) or "code" not in err or "evidence" not in err:
            raise ValueError("Mỗi lỗi phải là dict có 'code' và 'evidence'.")
        if err["code"] not in rules_v38.VALID_ERROR_CODES:
            raise ValueError(f"Mã lỗi '{err['code']}' không hợp lệ.")
            
        evidence = str(err["evidence"]).strip()
        # [SỬA LỖI TẠI ĐÂY]: Chấp nhận "Toàn bộ prompt" như một ngoại lệ hợp lệ
        if evidence and evidence.lower() != "toàn bộ prompt" and evidence not in original_prompt:
            raise ValueError(f"Bằng chứng '{evidence}' không có trong prompt gốc.")

    rewrite = ai_json["rewrite"]
    if not isinstance(rewrite, dict):
        raise ValueError("Trường 'rewrite' phải là dict.")
    expected_sections = set(rules_v38.REQUIRED_REWRITE_SECTIONS)
    received_sections = set(rewrite.keys())
    if received_sections != expected_sections:
        raise ValueError(f"Bản sửa thiếu mục: {expected_sections - received_sections}")
    return True

def calculate_final_score(ai_scores: dict, content_type: str) -> float:
    validate_scores_only(ai_scores, content_type)
    criteria = rules_v38.get_criteria_by_type(content_type)
    total_score = Decimal('0.0')
    for crit_id, info in criteria.items():
        total_score += Decimal(str(ai_scores[crit_id])) * Decimal(str(info["weight"]))
    return float((total_score / Decimal('10.0')).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
