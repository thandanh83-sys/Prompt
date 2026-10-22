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
    
    # Tự động điền 0 cho các tiêu chí bị thiếu thay vì báo lỗi
    for cid in expected_ids:
        if cid not in ai_scores:
            ai_scores[cid] = 0
            
    for crit_id, score in ai_scores.items():
        if crit_id not in expected_ids:
            continue
        if type(score) is not int:
            try: ai_scores[crit_id] = int(score)
            except: ai_scores[crit_id] = 0
        if not (0 <= ai_scores[crit_id] <= 10):
            ai_scores[crit_id] = max(0, min(10, ai_scores[crit_id]))
            
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict):
        raise ReportValidationError("Dữ liệu AI không phải JSON Object.")
        
    required_keys = {"scores", "errors", "rewrite"}
    if not required_keys.issubset(set(ai_json.keys())):
        raise ReportValidationError(f"JSON thiếu các key bắt buộc: {required_keys - set(ai_json.keys())}")

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    # Lọc lỗi (Bỏ qua nếu AI bịa mã lỗi không có trong rules)
    errors = ai_json.get("errors", [])
    if not isinstance(errors, list): errors = []
    valid_errors = []
    for err in errors:
        if isinstance(err, dict) and "code" in err and "evidence" in err:
            if err["code"] in rules_v38.VALID_ERROR_CODES:
                valid_errors.append(err)
    ai_json["errors"] = valid_errors

    # Tự động map tên mục (Kể cả AI viết sai hoa/thường, thiếu dấu cách)
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
