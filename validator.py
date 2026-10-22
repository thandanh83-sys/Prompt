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

def validate_full_report(ai_json: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict):
        raise ReportValidationError("Dữ liệu AI không phải JSON Object.")
        
    required_keys = {"domain", "criteria", "scores", "errors", "rewrite"}
    if not required_keys.issubset(set(ai_json.keys())):
        raise ReportValidationError(f"JSON thiếu các key bắt buộc: {required_keys - set(ai_json.keys())}")

    criteria = ai_json["criteria"]
    if not isinstance(criteria, list) or len(criteria) < 3:
        criteria = [{"id": k, "name": v["name"], "weight": v["weight"], "rubric": "Chấm điểm"} for k, v in rules_v38.CRITERIA_GENERAL.items()]
        ai_json["criteria"] = criteria

    criteria_ids = set()
    for c in criteria:
        if "id" not in c or "name" not in c or "weight" not in c:
            raise ReportValidationError("Tiêu chí thiếu id, name hoặc weight.")
        criteria_ids.add(c["id"])

    scores = ai_json.get("scores", {})
    if not isinstance(scores, dict): scores = {}
        
    for cid in criteria_ids:
        if cid not in scores:
            scores[cid] = 0
            
    for cid, score in scores.items():
        if cid not in criteria_ids: continue
        if type(score) is not int:
            try: scores[cid] = int(score)
            except: scores[cid] = 0
        if not (0 <= scores[cid] <= 10):
            scores[cid] = max(0, min(10, scores[cid]))
    ai_json["scores"] = scores

    errors = ai_json.get("errors", [])
    if not isinstance(errors, list): errors = []
    valid_errors = []
    for err in errors:
        if isinstance(err, dict) and "code" in err and "evidence" in err:
            if err["code"] in rules_v38.VALID_ERROR_CODES:
                valid_errors.append(err)
    ai_json["errors"] = valid_errors

    rewrite = ai_json.get("rewrite", {})
    if not isinstance(rewrite, dict): rewrite = {}
    
    expected_sections = list(rules_v38.REQUIRED_REWRITE_SECTIONS)
    final_rewrite = {}
    
    for exp_sec in expected_sections:
        final_rewrite[exp_sec] = "Không có nội dung."
        norm_exp = re.sub(r'[^a-zA-Z0-9àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', '', exp_sec.lower())
        
        for rec_sec, val in rewrite.items():
            norm_rec = re.sub(r'[^a-zA-Z0-9àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', '', rec_sec.lower())
            if norm_exp in norm_rec or norm_rec in norm_exp:
                final_rewrite[exp_sec] = str(val)
                break
                
    ai_json["rewrite"] = final_rewrite
    return True

def calculate_final_score(ai_scores: dict, criteria: dict) -> float:
    if not criteria: return 0.0
    total_weight = Decimal('0.0')
    weighted_score = Decimal('0.0')
    
    for crit_id, info in criteria.items():
        weight = Decimal(str(info.get("weight", 1.0)))
        total_weight += weight
        score = Decimal(str(ai_scores.get(crit_id, 0)))
        weighted_score += score * weight
        
    if total_weight == 0: return 0.0
    final_score = weighted_score / total_weight
    return float(final_score.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))