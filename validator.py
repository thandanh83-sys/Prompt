import rules_v38
from decimal import Decimal, ROUND_HALF_UP

def validate_scores_only(ai_scores: dict, criteria: dict) -> bool:
    if not isinstance(ai_scores, dict): 
        raise ValueError("Trường 'scores' phải là dict.")
        
    expected_ids = set(criteria.keys())
    received_ids = set(ai_scores.keys())
    
    # Bỏ qua kiểm tra ID nếu AI trả về thừa (để Auto-Repair xử lý)
    if not expected_ids.issubset(received_ids):
        raise ValueError(f"ID điểm bị thiếu. Cần: {expected_ids - received_ids}")
        
    for crit_id, score in ai_scores.items():
        if crit_id in expected_ids:
            if type(score) is not int or not (0 <= score <= 10):
                raise ValueError(f"Điểm {crit_id} phải là số nguyên 0-10.")
    return True

def validate_full_report(ai_json: dict, criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): raise ValueError("Dữ liệu AI không phải JSON.")
    for k in ["scores", "errors", "rewrite"]:
        if k not in ai_json: raise ValueError(f"Thiếu trường '{k}'.")

    validate_scores_only(ai_json["scores"], criteria)

    errors = ai_json["errors"]
    if not isinstance(errors, list): raise ValueError("Trường 'errors' phải là list.")
        
    for err in errors:
        if not isinstance(err, dict) or "code" not in err or "evidence" not in err:
            raise ValueError("Mỗi lỗi phải là dict có 'code' và 'evidence'.")
        if err["code"] not in rules_v38.VALID_ERROR_CODES:
            raise ValueError(f"Mã lỗi '{err['code']}' không hợp lệ.")
            
        evidence = str(err["evidence"]).strip()
        if evidence and evidence.lower() not in ["toàn bộ", "toàn bộ prompt"] and evidence not in original_prompt:
            raise ValueError(f"Bằng chứng '{evidence}' không có trong prompt gốc.")

    rewrite = ai_json["rewrite"]
    if not isinstance(rewrite, dict): raise ValueError("Trường 'rewrite' phải là dict.")
    expected_sections = set(rules_v38.REQUIRED_REWRITE_SECTIONS)
    received_sections = set(rewrite.keys())
    if received_sections != expected_sections:
        raise ValueError(f"Bản sửa thiếu mục: {expected_sections - received_sections}")
    return True

def calculate_final_score(ai_scores: dict, criteria: dict) -> float:
    validate_scores_only(ai_scores, criteria)
    
    total_weight = Decimal('0.0')
    weighted_score = Decimal('0.0')
    
    for crit_id, info in criteria.items():
        weight = Decimal(str(info["weight"]))
        total_weight += weight
        
        # Nếu AI không trả điểm mục này thì mặc định 0
        score = Decimal(str(ai_scores.get(crit_id, 0)))
        weighted_score += score * weight
        
    if total_weight == 0:
        return 0.0
        
    # Chuẩn hóa về thang điểm 10
    final_score = (weighted_score / total_weight) * Decimal('10.0')
    return float(final_score.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))