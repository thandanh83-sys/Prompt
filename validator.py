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
    if not isinstance(ai_scores, dict): ai_scores = {}
    expected_ids = set(criteria.keys())
    
    for crit_id, score in ai_scores.items():
        try:
            val = float(score) if not isinstance(score, bool) else 0
        except (ValueError, TypeError):
            val = 1.0
        val = max(0.0, min(10.0, val))
        ai_scores[crit_id] = val
        
    for k in expected_ids:
        if k not in ai_scores:
            ai_scores[k] = 1.0 # Tự động điền nếu AI bỏ sót
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): ai_json = {}
        
    if "scores" not in ai_json or not isinstance(ai_json["scores"], dict): ai_json["scores"] = {}
    if "errors" not in ai_json or not isinstance(ai_json["errors"], list): ai_json["errors"] = []
    if "rewrite" not in ai_json or not isinstance(ai_json["rewrite"], dict): ai_json["rewrite"] = {}

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    valid_errors = []
    for err in ai_json["errors"]:
        if isinstance(err, dict) and err.get("code") in rules_v38.VALID_ERROR_CODES:
            valid_errors.append({"code": err["code"], "evidence": str(err.get("evidence", ""))})
    ai_json["errors"] = valid_errors

    expected_sections = rules_v38.REQUIRED_REWRITE_SECTIONS
    normalized_rewrite = {}
    
    for expected in expected_sections:
        found_val = ai_json["rewrite"].get(expected)
        if isinstance(found_val, str) and found_val.strip():
            # Format xuống dòng cho đẹp nếu AI viết dính chùm
            val_text = found_val.strip()
            if not val_text.startswith("-") and not val_text.startswith("*"):
                val_text = val_text.replace(" - ", "\n- ").replace(" + ", "\n+ ")
            normalized_rewrite[expected] = val_text
        else:
            normalized_rewrite[expected] = "Chưa cung cấp thông tin."
            
    ai_json["rewrite"] = normalized_rewrite
    return True

def _calc_tier_score(ai_scores: dict, criteria: dict) -> Decimal:
    total_weight = Decimal("0")
    weighted_score = Decimal("0")
    for crit_id, info in criteria.items():
        score = ai_scores.get(crit_id, 1.0)
        score_dec = Decimal(str(score))
        weight = Decimal(str(info["weight"]))
        total_weight += weight
        weighted_score += score_dec * weight
    return weighted_score / total_weight if total_weight > 0 else Decimal("0")

def calculate_final_score(ai_scores: dict, main_criteria: dict, tech_criteria: dict) -> float:
    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_scores, all_criteria)
    weighted_score = _calc_tier_score(ai_scores, all_criteria)
    return float(weighted_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))