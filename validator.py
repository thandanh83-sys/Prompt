import re
import unicodedata
import rules_v38
from decimal import Decimal, ROUND_HALF_UP

class ReportValidationError(Exception):
    pass

def normalize_text(text: str) -> str:
    if not isinstance(text, str): return ""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip().casefold()

def validate_scores_only(ai_scores: dict, criteria: dict) -> bool:
    if not isinstance(ai_scores, dict): 
        raise ReportValidationError("Trường 'scores' phải là dict.") # Bắt buộc phải là dict
        
    expected_ids = set(criteria.keys())
    received_ids = set(ai_scores.keys())
    
    missing = expected_ids - received_ids
    if len(missing) > 3: # Nếu thiếu quá 3 tiêu chí thì báo lỗi
        raise ReportValidationError(f"AI thiếu quá nhiều điểm: {missing}")
        
    for crit_id, score in ai_scores.items():
        try:
            val = float(score) if not isinstance(score, bool) else 0
        except (ValueError, TypeError):
            raise ReportValidationError(f"Điểm của '{crit_id}' không hợp lệ.")
        
        val = max(0.0, min(10.0, val))
        ai_scores[crit_id] = val
        
    # Tự động bù điểm nếu AI thiếu 1-2 cái
    for k in expected_ids:
        if k not in ai_scores:
            ai_scores[k] = 1.0
            
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): 
        raise ReportValidationError("Dữ liệu AI không phải JSON.")
        
    if "scores" not in ai_json or not isinstance(ai_json["scores"], dict):
        raise ReportValidationError("AI thiếu trường 'scores' hoặc sai định dạng.")
    if "rewrite" not in ai_json or not isinstance(ai_json["rewrite"], dict):
        raise ReportValidationError("AI thiếu trường 'rewrite'.")
    if "errors" not in ai_json or not isinstance(ai_json["errors"], list): 
        ai_json["errors"] = []

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    valid_errors = []
    prompt_norm = normalize_text(original_prompt)
    for err in ai_json["errors"]:
        if not isinstance(err, dict): continue
        code = err.get("code", "")
        evidence = err.get("evidence", "")
        
        if code in rules_v38.VALID_ERROR_CODES and isinstance(evidence, str):
            valid_errors.append({"code": code, "evidence": evidence})
    
    ai_json["errors"] = valid_errors

    expected_sections = rules_v38.REQUIRED_REWRITE_SECTIONS
    normalized_rewrite = {}
    
    for expected in expected_sections:
        found_val = None
        for k, v in ai_json["rewrite"].items():
            if expected.lower() in k.lower() or k.lower() in expected.lower():
                found_val = v
                break
        
        if found_val and isinstance(found_val, str) and found_val.strip():
            # Đảm bảo có xuống dòng cho đẹp
            val_text = found_val.strip()
            if not val_text.startswith("-") and not val_text.startswith("*"):
                val_text = val_text.replace(" - ", "\n- ").replace(" + ", "\n+ ")
            normalized_rewrite[expected] = val_text
        else:
            normalized_rewrite[expected] = f"Hệ thống AI đang tự động bổ sung ngữ cảnh cho mục {expected}."
            
    ai_json["rewrite"] = normalized_rewrite
            
    return True

def _calc_tier_score(ai_scores: dict, criteria: dict) -> Decimal:
    if not isinstance(ai_scores, dict) or not isinstance(criteria, dict) or not criteria:
        raise ReportValidationError("Không thể tính điểm với dữ liệu rỗng.")
    total_weight = Decimal("0")
    weighted_score = Decimal("0")
    for crit_id, info in criteria.items():
        if crit_id not in ai_scores:
            ai_scores[crit_id] = 1.0
        score = ai_scores[crit_id]
        
        try:
            score_dec = Decimal(str(score))
        except:
            score_dec = Decimal("1.0")
            
        try:
            weight = Decimal(str(info["weight"]))
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            raise ReportValidationError(f"Trọng số của '{crit_id}' không hợp lệ.") from exc
        
        total_weight += weight
        weighted_score += score_dec * weight
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