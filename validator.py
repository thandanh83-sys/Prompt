import re
import unicodedata
import rules_v38
import error_rules
from decimal import Decimal, ROUND_HALF_UP

class ReportValidationError(Exception):
    pass

def normalize_text(text: str) -> str:
    if not isinstance(text, str): return ""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip().casefold()

def validate_scores_only(ai_scores: dict, required_criteria: dict) -> bool:
    if not isinstance(ai_scores, dict): 
        raise ReportValidationError("Trường 'scores' phải là dict.")
        
    # [LỚP BẢO VỆ] Tự động lọc bỏ các DYN nếu AI lỡ sinh ra, không làm crash hệ thống
    filtered_scores = {k: v for k, v in ai_scores.items() if not k.startswith("DYN")}
        
    required_ids = set(required_criteria.keys())
    received_ids = set(filtered_scores.keys())
    
    if received_ids != required_ids:
        missing = required_ids - received_ids
        extra = received_ids - required_ids
        raise ReportValidationError(f"Sai tập tiêu chí. Thiếu: {sorted(missing)}; Thừa: {sorted(extra)}")
        
    for crit_id, score in filtered_scores.items():
        if type(score) is not int:
            raise ReportValidationError(f"Điểm của '{crit_id}' phải là số nguyên.")
        if not (0 <= score <= 10):
            raise ReportValidationError(f"Điểm của '{crit_id}' phải nằm trong khoảng 0-10.")
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): 
        raise ReportValidationError("Dữ liệu AI không phải JSON Object.")
        
    # Chấp nhận thêm identified_domain
    required_keys = {"scores", "errors", "rewrite", "identified_domain"}
    if not required_keys.issubset(set(ai_json.keys())):
        raise ReportValidationError(f"JSON phải có ít nhất các key: {required_keys}")

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    errors = ai_json["errors"]
    if not isinstance(errors, list): 
        raise ReportValidationError("Trường 'errors' phải là list.")
        
    prompt_norm = normalize_text(original_prompt)
    missing_info_codes = {"B01", "C02", "C04"}
    valid_error_codes = set(error_rules.ERROR_RULES.keys())

    for err in errors:
        if not isinstance(err, dict):
            raise ReportValidationError("Mỗi lỗi phải là object.")
        # Chấp nhận thêm key 'hint'
        if set(err.keys()) - {"code", "evidence", "hint"}:
            raise ReportValidationError("Lỗi chứa trường không được hỗ trợ.")
        if not {"code", "evidence"}.issubset(err.keys()):
            raise ReportValidationError("Lỗi phải có code và evidence.")
            
        code = err["code"]
        evidence = err["evidence"]
        
        if not isinstance(code, str) or code not in valid_error_codes:
            raise ReportValidationError(f"Mã lỗi không hợp lệ: {code!r}")
            
        if not isinstance(evidence, str) or not evidence.strip():
            raise ReportValidationError(f"Lỗi {code} thiếu bằng chứng hợp lệ.")
            
        if code in missing_info_codes:
            # Nới lỏng độ dài tối thiểu cho lỗi thiếu thông tin (VD: "Thiếu ảnh", "Thiếu file")
            if len(evidence.strip()) < 3:
                raise ReportValidationError(f"Bằng chứng của {code} quá chung chung.")
        else:
            evidence_norm = normalize_text(evidence)
            if evidence_norm not in prompt_norm:
                raise ReportValidationError(f"Bằng chứng của {code} không khớp prompt gốc.")
                
        if "hint" in err and not isinstance(err["hint"], str):
            raise ReportValidationError(f"hint của {code} phải là chuỗi.")

    rewrite = ai_json["rewrite"]
    if not isinstance(rewrite, dict): 
        raise ReportValidationError("Trường 'rewrite' phải là dict.")
        
    required_sections = rules_v38.REQUIRED_REWRITE_SECTIONS
    if list(rewrite.keys()) != required_sections:
        raise ReportValidationError("Rewrite phải có đúng 11 mục theo đúng thứ tự backend.")
        
    for section in required_sections:
        value = rewrite[section]
        if not isinstance(value, str) or not value.strip():
            raise ReportValidationError(f"Mục rewrite '{section}' bị thiếu hoặc rỗng.")
            
    return True

def _calc_tier_score(ai_scores: dict, criteria: dict) -> Decimal:
    total_weight = Decimal("0")
    weighted_score = Decimal("0")
    for crit_id, info in criteria.items():
        if crit_id not in ai_scores:
            raise ReportValidationError(f"Thiếu điểm cho tiêu chí {crit_id}.")
        score = ai_scores[crit_id]
        weight = Decimal(str(info["weight"]))
        total_weight += weight
        weighted_score += Decimal(score) * weight
    return weighted_score / total_weight if total_weight > 0 else Decimal("0")

def calculate_final_score(ai_scores: dict, main_criteria: dict, tech_criteria: dict) -> float:
    all_criteria = {**main_criteria, **tech_criteria}
    weighted_score = _calc_tier_score(ai_scores, all_criteria)
    return float(weighted_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))