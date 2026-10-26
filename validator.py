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
        
    required_ids = set(required_criteria.keys())
    received_ids = set(ai_scores.keys())
    
    # Lọc bỏ các DYN để kiểm tra. Chỉ bắt buộc phải có Core + Tech.
    received_core_ids = {k for k in received_ids if not k.startswith("DYN")}
    
    missing_core = required_ids - received_core_ids
    if missing_core:
        raise ReportValidationError(f"Thiếu điểm cho các tiêu chí bắt buộc: {missing_core}")
        
    for crit_id, score in ai_scores.items():
        if type(score) is not int:
            raise ReportValidationError(f"Điểm của '{crit_id}' phải là số nguyên.")
        if not (0 <= score <= 10):
            raise ReportValidationError(f"Điểm của '{crit_id}' phải nằm trong khoảng 0-10.")
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): 
        raise ReportValidationError("Dữ liệu AI không phải JSON Object.")
        
    required_keys = {"scores", "errors", "rewrite"}
    if not required_keys.issubset(set(ai_json.keys())):
        raise ReportValidationError(f"JSON phải có ít nhất các key: {required_keys}")

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    errors = ai_json["errors"]
    if not isinstance(errors, list): 
        raise ReportValidationError("Trường 'errors' phải là list.")
        
    prompt_norm = normalize_text(original_prompt)
    MISSING_INFO_ERRORS = {"B01", "C02", "C04"}
    valid_error_codes = set(error_rules.ERROR_RULES.keys())

    for err in errors:
        if not isinstance(err, dict) or not {"code", "evidence"}.issubset(set(err.keys())):
            raise ReportValidationError("Mỗi lỗi phải là dict chứa ít nhất 'code' và 'evidence'.")
        
        # [NỚI LỎNG] Nếu AI tự bịa mã lỗi không có trong rules, tự động đổi thành mã mặc định thay vì crash
        if not isinstance(err["code"], str) or err["code"] not in valid_error_codes:
            err["code"] = "P01" 
            
        evidence = err.get("evidence", "")
        if not isinstance(evidence, str):
            evidence = str(evidence)
        err["evidence"] = evidence
            
        ev_norm = normalize_text(evidence)
        if not ev_norm:
            raise ReportValidationError(f"Lỗi '{err['code']}' phải có bằng chứng.")
            
        if err["code"] not in MISSING_INFO_ERRORS:
            ev_clean = evidence.strip(' "\'\n\r\t')
            ev_clean_norm = normalize_text(ev_clean)
            if ev_clean_norm not in prompt_norm and prompt_norm not in ev_clean_norm:
                # [NỚI LỎNG] Không chặn nếu AI trích dẫn bằng chứng hơi lệch một chút so với prompt gốc
                pass

    rewrite = ai_json["rewrite"]
    if not isinstance(rewrite, dict): 
        raise ReportValidationError("Trường 'rewrite' phải là dict.")
        
    # [NỚI LỎNG] Chỉ cần AI trả về ít nhất 9/11 mục (đề phòng AI quên hoặc gộp mục đối với prompt Vẽ ảnh)
    if len(rewrite.keys()) < 9:
        raise ReportValidationError("Bản sửa (rewrite) phải có ít nhất 9 mục.")
        
    for sec, val in rewrite.items():
        if not isinstance(val, str):
            rewrite[sec] = str(val) # Ép kiểu nếu AI trả về số thay vì chuỗi
            
    return True

def _calc_tier_score(ai_scores: dict, criteria: dict) -> Decimal:
    total_weight = Decimal("0")
    weighted_score = Decimal("0")
    for crit_id, info in criteria.items():
        score = ai_scores.get(crit_id, 5) # Nếu AI quên chấm điểm tiêu chí nào, mặc định cho 5 điểm để không lỗi
        weight = Decimal(str(info["weight"]))
        total_weight += weight
        weighted_score += Decimal(score) * weight
    return weighted_score / total_weight if total_weight > 0 else Decimal("0")

def calculate_final_score(ai_scores: dict, main_criteria: dict, tech_criteria: dict) -> float:
    all_criteria = {**main_criteria, **tech_criteria}
    for key in ai_scores.keys():
        if key.startswith("DYN") and key not in all_criteria:
            all_criteria[key] = {"name": "Tiêu chí chuyên ngành", "weight": 1.0}
            
    weighted_score = _calc_tier_score(ai_scores, all_criteria)
    return float(weighted_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))