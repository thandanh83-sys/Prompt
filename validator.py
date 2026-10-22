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
            
        prompt_norm = normalize_text(original_prompt)
        if not prompt_norm:
            raise ReportValidationError("Prompt gốc không hợp lệ để đối chiếu bằng chứng.")
        if ev_norm not in prompt_norm:
            raise ReportValidationError(f"Bằng chứng '{evidence}' không có trong prompt gốc.")

    rewrite = ai_json["rewrite"]
    if not isinstance(rewrite, dict): 
        raise ReportValidationError("Trường 'rewrite' phải là dict.")
        
    expected_sections = rules_v38.REQUIRED_REWRITE_SECTIONS
    received_sections = list(rewrite.keys())
    if received_sections != expected_sections:
        raise ReportValidationError("Bản sửa phải có đúng 11 mục theo thứ tự quy định; cần kiểm tra mục thiếu, thừa hoặc sai thứ tự.")
        
    for sec, val in rewrite.items():
        if not isinstance(val, str) or not val.strip():
            raise ReportValidationError(f"Mục '{sec}' trong bản sửa không được để trống.")
            
    return True

def _calc_tier_score(ai_scores: dict, criteria: dict) -> Decimal:
    if not isinstance(ai_scores, dict) or not isinstance(criteria, dict) or not criteria:
        raise ReportValidationError("Không thể tính điểm với dữ liệu điểm hoặc tiêu chí rỗng/không hợp lệ.")
    total_weight = Decimal("0")
    weighted_score = Decimal("0")
    for crit_id, info in criteria.items():
        if crit_id not in ai_scores:
            raise ReportValidationError(f"Thiếu điểm cho tiêu chí '{crit_id}'.")
        score = ai_scores[crit_id]
        if type(score) is not int or not 0 <= score <= 10:
            raise ReportValidationError(f"Điểm của '{crit_id}' phải là số nguyên từ 0 đến 10.")
        try:
            weight = Decimal(str(info["weight"]))
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            raise ReportValidationError(f"Trọng số của '{crit_id}' không hợp lệ.") from exc
        if not weight.is_finite() or weight <= 0:
            raise ReportValidationError(f"Trọng số của '{crit_id}' phải hữu hạn và lớn hơn 0.")
        total_weight += weight
        weighted_score += Decimal(score) * weight
    if total_weight <= 0:
        raise ReportValidationError("Tổng trọng số phải lớn hơn 0.")
    return weighted_score / total_weight


def calculate_final_score(ai_scores: dict, main_criteria: dict, tech_criteria: dict) -> float:
    if not isinstance(main_criteria, dict) or not main_criteria:
        raise ValueError("Không thể tính điểm: Nhóm tiêu chí chính bị rỗng.")
    if not isinstance(tech_criteria, dict):
        raise ValueError("Nhóm tiêu chí kỹ thuật không hợp lệ.")
    if set(main_criteria) & set(tech_criteria):
        raise ReportValidationError("ID tiêu chí bị trùng giữa Main và Tech.")
    rules_v38.validate_config(main_criteria, tech_criteria)
    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_scores, all_criteria)
    weighted_score = _calc_tier_score(ai_scores, all_criteria)
    return float(weighted_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
