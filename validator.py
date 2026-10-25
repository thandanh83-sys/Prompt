import re
import unicodedata
import rules_v38
from decimal import Decimal, ROUND_HALF_UP

class ReportValidationError(Exception): pass

def normalize_text(text: str) -> str:
    if not isinstance(text, str): return ""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip().casefold()

def validate_scores_only(ai_scores: dict, criteria: dict) -> bool:
    if not isinstance(ai_scores, dict): 
        raise ReportValidationError("Trường 'scores' phải là dict.")
        
    expected_ids = set(criteria.keys())
    received_ids = set(ai_scores.keys())
    
    # [QUAN TRỌNG] Bỏ qua các mã DYN khi kiểm tra tính khớp của Core Criteria
    received_core_ids = {k for k in received_ids if not k.startswith("DYN")}
    
    if expected_ids != received_core_ids:
        missing = expected_ids - received_core_ids
        extra = received_core_ids - expected_ids
        raise ReportValidationError(f"ID điểm lõi không khớp. Thiếu: {missing}, Thừa: {extra}")
        
    for crit_id, score in ai_scores.items():
        if type(score) is not int:
            raise ReportValidationError(f"Điểm của '{crit_id}' phải là số nguyên.")
        if not (0 <= score <= 10):
            raise ReportValidationError(f"Điểm của '{crit_id}' phải nằm trong khoảng 0-10.")
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): raise ReportValidationError("Dữ liệu không phải JSON Object.")
        
    required_keys = {"scores", "errors", "rewrite"}
    if not required_keys.issubset(set(ai_json.keys())):
        raise ReportValidationError(f"JSON phải có ít nhất các key: {required_keys}")

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    errors = ai_json["errors"]
    if not isinstance(errors, list): raise ReportValidationError("Trường 'errors' phải là list.")
        
    prompt_norm = normalize_text(original_prompt)
    MISSING_INFO_ERRORS = {"B01", "C02", "C04"}

    for err in errors:
        # Đã sửa để chấp nhận thêm trường "hint"
        if not isinstance(err, dict) or not {"code", "evidence"}.issubset(set(err.keys())):
            raise ReportValidationError("Mỗi lỗi phải chứa ít nhất 'code' và 'evidence'.")
        
        if not isinstance(err["code"], str) or err["code"] not in rules_v38.VALID_ERROR_CODES:
            raise ReportValidationError(f"Mã lỗi '{err['code']}' không hợp lệ.")
            
        evidence = err["evidence"]
        ev_norm = normalize_text(evidence)
        if not ev_norm:
            raise ReportValidationError(f"Lỗi '{err['code']}' phải có bằng chứng.")
            
        if err["code"] not in MISSING_INFO_ERRORS:
            ev_clean = evidence.strip(' "\'\n\r\t')
            ev_clean_norm = normalize_text(ev_clean)
            if ev_clean_norm not in prompt_norm and prompt_norm not in ev_clean_norm:
                raise ReportValidationError(f"Bằng chứng '{evidence}' không có trong prompt gốc.")

    rewrite = ai_json["rewrite"]
    expected_sections = rules_v38.REQUIRED_REWRITE_SECTIONS
    if list(rewrite.keys()) != expected_sections:
        raise ReportValidationError("Bản sửa phải có đúng 11 mục theo thứ tự.")
        
    for sec, val in rewrite.items():
        if not isinstance(val, str) or not val.strip():
            raise ReportValidationError(f"Mục '{sec}' không được để trống.")
    return True

def _calc_tier_score(ai_scores: dict, criteria: dict) -> Decimal:
    total_weight = Decimal("0")
    weighted_score = Decimal("0")
    for crit_id, info in criteria.items():
        score = ai_scores[crit_id]
        weight = Decimal(str(info["weight"]))
        total_weight += weight
        weighted_score += Decimal(score) * weight
    return weighted_score / total_weight if total_weight > 0 else Decimal("0")

def calculate_final_score(ai_scores: dict, main_criteria: dict, tech_criteria: dict) -> float:
    all_criteria = {**main_criteria, **tech_criteria}
    
    # [QUAN TRỌNG] Gán trọng số = 1.0 cho các tiêu chí động do AI tự sinh
    for key in ai_scores.keys():
        if key.startswith("DYN") and key not in all_criteria:
            all_criteria[key] = {"name": "Tiêu chí chuyên ngành", "weight": 1.0}
            
    validate_scores_only(ai_scores, all_criteria)
    weighted_score = _calc_tier_score(ai_scores, all_criteria)
    return float(weighted_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))