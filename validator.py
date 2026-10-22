import re
import unicodedata
import rules_v38
from decimal import Decimal, ROUND_HALF_UP

class ReportValidationError(Exception):
    """Ngoại lệ riêng cho lỗi dữ liệu báo cáo từ AI."""
    pass

def normalize_text(text: str) -> str:
    if not isinstance(text, str): return ""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip().casefold()

def validate_scores_only(ai_scores: dict, criteria: dict) -> bool:
    if not isinstance(ai_scores, dict): 
        raise ReportValidationError("Trường 'scores' phải là dict.")
        
    expected_ids = set(criteria.keys())
    received_ids = set(ai_scores.keys())
    
    if expected_ids != received_ids:
        missing = expected_ids - received_ids
        extra = received_ids - expected_ids
        raise ReportValidationError(f"ID điểm không khớp. Thiếu: {missing}, Thừa: {extra}")
        
    for crit_id, score in ai_scores.items():
        if type(score) is not int:
            raise ReportValidationError(f"Điểm của '{crit_id}' phải là số nguyên (nhận được {type(score).__name__}).")
        if not (0 <= score <= 10):
            raise ReportValidationError(f"Điểm của '{crit_id}' phải nằm trong khoảng 0-10.")
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): 
        raise ReportValidationError("Dữ liệu AI không phải JSON Object.")
        
    required_keys = {"scores", "errors", "rewrite"}
    if set(ai_json.keys()) != required_keys:
        raise ReportValidationError(f"JSON phải có chính xác các key: {required_keys}")

    if set(main_criteria.keys()) & set(tech_criteria.keys()):
        raise ReportValidationError("Lỗi hệ thống: ID tiêu chí bị trùng giữa Main và Tech.")

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    errors = ai_json["errors"]
    if not isinstance(errors, list): 
        raise ReportValidationError("Trường 'errors' phải là list.")
        
    for err in errors:
        if not isinstance(err, dict) or set(err.keys()) != {"code", "evidence"}:
            raise ReportValidationError("Mỗi lỗi phải là dict chứa chính xác 'code' và 'evidence'.")
        
        if not isinstance(err["code"], str):
            raise ReportValidationError("Trường 'code' phải là chuỗi.")
            
        if err["code"] not in rules_v38.VALID_ERROR_CODES:
            raise ReportValidationError(f"Mã lỗi '{err['code']}' không hợp lệ.")
            
        evidence = err["evidence"]
        if not isinstance(evidence, str):
            raise ReportValidationError("Trường 'evidence' phải là chuỗi.")
            
        ev_norm = normalize_text(evidence)
        if not ev_norm:
            raise ReportValidationError(f"Lỗi '{err['code']}' phải có bằng chứng trích dẫn.")
            
        # SỬA LỖI TẠI ĐÂY: Thêm ngoại lệ cho phép "toàn bộ"
        if ev_norm not in ["toàn bộ", "toàn bộ prompt"]:
            prompt_norm = normalize_text(original_prompt)
            if ev_norm not in prompt_norm:
                raise ReportValidationError(f"Bằng chứng '{evidence}' không có trong prompt gốc.")

    rewrite = ai_json["rewrite"]
    if not isinstance(rewrite, dict): 
        raise ReportValidationError("Trường 'rewrite' phải là dict.")
        
    expected_sections = set(rules_v38.REQUIRED_REWRITE_SECTIONS)
    received_sections = set(rewrite.keys())
    if received_sections != expected_sections:
        raise ReportValidationError(f"Bản sửa thiếu/thừa mục: {expected_sections.symmetric_difference(received_sections)}")
        
    for sec, val in rewrite.items():
        if not isinstance(val, str) or not val.strip():
            raise ReportValidationError(f"Mục '{sec}' trong bản sửa không được để trống.")
            
    return True

def _calc_tier_score(ai_scores: dict, criteria: dict) -> Decimal:
    if not criteria: return Decimal('0.0')
    
    total_weight = Decimal('0.0')
    weighted_score = Decimal('0.0')
    
    for crit_id, info in criteria.items():
        weight = Decimal(str(info["weight"]))
        total_weight += weight
        score = Decimal(str(ai_scores.get(crit_id, 0)))
        weighted_score += score * weight
        
    if total_weight == 0: return Decimal('0.0')
    return weighted_score / total_weight

def calculate_final_score(ai_scores: dict, main_criteria: dict, tech_criteria: dict) -> float:
    if not main_criteria:
        raise ValueError("Không thể tính điểm: Nhóm tiêu chí chính bị rỗng.")
        
    s_main = _calc_tier_score(ai_scores, main_criteria)
    
    if tech_criteria:
        s_tech = _calc_tier_score(ai_scores, tech_criteria)
        final_score = (Decimal('0.6') * s_main) + (Decimal('0.4') * s_tech)
    else:
        final_score = s_main
        
    return float(final_score.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
