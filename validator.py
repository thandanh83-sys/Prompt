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
        raise ReportValidationError("Trường 'scores' phải là dict.")
        
    expected_ids = set(criteria.keys())
    
    for crit_id, score in ai_scores.items():
        try:
            val = float(score) if not isinstance(score, bool) else 0
        except (ValueError, TypeError):
            val = 1.0
        val = max(0.0, min(10.0, val))
        ai_scores[crit_id] = val
        
    # Tự động bù điểm nếu AI thiếu
    for k in expected_ids:
        if k not in ai_scores:
            ai_scores[k] = 1.0
            
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): 
        raise ReportValidationError("Dữ liệu AI không phải JSON.")
        
    if "scores" not in ai_json or not isinstance(ai_json["scores"], dict):
        raise ReportValidationError("AI thiếu trường 'scores'.")
    if "rewrite" not in ai_json or not isinstance(ai_json["rewrite"], dict):
        raise ReportValidationError("AI thiếu trường 'rewrite'.")
    if "errors" not in ai_json or not isinstance(ai_json["errors"], list): 
        ai_json["errors"] = []

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    # Đơn giản hóa việc kiểm tra lỗi, không bắt bẻ bằng chứng quá khắt khe
    valid_errors = []
    for err in ai_json["errors"]:
        if isinstance(err, dict) and err.get("code") in rules_v38.VALID_ERROR_CODES:
            valid_errors.append({"code": err["code"], "evidence": str(err.get("evidence", ""))})
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
            val_text = found_val.strip()
            # Format lại cho đẹp (thêm gạch đầu dòng nếu có)
            if not val_text.startswith("-") and not val_text.startswith("*"):
                val_text = val_text.replace(" - ", "\n- ").replace(" + ", "\n+ ")
            normalized_rewrite[expected] = val_text
        else:
            raise ReportValidationError(f"AI bỏ sót hoặc viết rỗng mục {expected}.")
            
    ai_json["rewrite"] = normalized_rewrite
    return True

def _calc_tier_score(ai_scores: dict, criteria: dict) -> Decimal:
    total_weight = Decimal("0")
    weighted_score = Decimal("0")
    for crit_id, info in criteria.items():
        score_dec = Decimal(str(ai_scores.get(crit_id, 1.0)))
        weight = Decimal(str(info["weight"]))
        total_weight += weight
        weighted_score += score_dec * weight
    return weighted_score / total_weight if total_weight > 0 else Decimal("0")

def calculate_final_score(ai_scores: dict, main_criteria: dict, tech_criteria: dict) -> float:
    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_scores, all_criteria)
    weighted_score = _calc_tier_score(ai_scores, all_criteria)
    return float(weighted_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))