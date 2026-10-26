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
    if received_ids != required_ids:
        raise ReportValidationError(f"Sai tập tiêu chí. Thiếu: {sorted(required_ids - received_ids)}; Thừa: {sorted(received_ids - required_ids)}")
    for crit_id, score in ai_scores.items():
        if type(score) is not int: raise ReportValidationError(f"Điểm của '{crit_id}' phải là số nguyên.")
        if not (0 <= score <= 10): raise ReportValidationError(f"Điểm của '{crit_id}' phải nằm trong khoảng 0-10.")
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): raise ReportValidationError("Dữ liệu AI không phải JSON Object.")
    required_keys = {"scores", "errors", "rewrite", "identified_domain"}
    if set(ai_json.keys()) != required_keys:
        raise ReportValidationError(f"JSON phải có chính xác các key: {required_keys}. Nhận được: {set(ai_json.keys())}")
    
    domain = ai_json["identified_domain"]
    if not isinstance(domain, str) or len(domain.strip()) < 2:
        raise ReportValidationError("'identified_domain' phải là chuỗi có nghĩa.")

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    errors = ai_json["errors"]
    if not isinstance(errors, list): raise ReportValidationError("Trường 'errors' phải là list.")
    if len(errors) > 15: raise ReportValidationError("Quá nhiều lỗi (max 15).")
        
    prompt_norm = normalize_text(original_prompt)
    valid_error_codes = set(error_rules.ERROR_RULES.keys())
    seen_evidence = set() 

    for err in errors:
        if not isinstance(err, dict): raise ReportValidationError("Mỗi lỗi phải là object.")
        if set(err.keys()) != {"code", "evidence", "hint"}: raise ReportValidationError("Mỗi lỗi phải có chính xác 'code', 'evidence', và 'hint'.")
            
        code = err["code"]
        evidence = err["evidence"]
        hint = err["hint"]
        
        if not isinstance(code, str) or code not in valid_error_codes: raise ReportValidationError(f"Mã lỗi không hợp lệ: {code!r}")
        if not isinstance(evidence, str) or not evidence.strip(): raise ReportValidationError(f"Lỗi {code} thiếu bằng chứng.")
            
        rule = error_rules.ERROR_RULES.get(code, {})
        require_quote = rule.get("require_quote", True)
        evidence_norm = normalize_text(evidence)
        
        if evidence_norm in seen_evidence: raise ReportValidationError(f"Bằng chứng bị trùng lặp: '{evidence}'.")
        seen_evidence.add(evidence_norm)

        if require_quote:
            if len(evidence_norm) < 5: raise ReportValidationError(f"Bằng chứng của {code} quá ngắn.")
            if evidence_norm not in prompt_norm: raise ReportValidationError(f"Bằng chứng của {code} không khớp với prompt gốc. Evidence: '{evidence}'")
        else:
            if len(evidence_norm) < 15: raise ReportValidationError(f"Bằng chứng của {code} quá ngắn (dưới 15 ký tự). Cần giải thích rõ.")
            valid_missing_keywords = ["không", "thiếu", "chưa", "không có", "chưa rõ", "mơ hồ"]
            if not any(kw in evidence_norm for kw in valid_missing_keywords):
                raise ReportValidationError(f"Bằng chứng của {code} cần nêu rõ thông tin bị thiếu (VD: 'Thiếu...').")
                
        if not isinstance(hint, str) or len(hint.strip()) < 10: raise ReportValidationError(f"Hint của {code} quá ngắn.")

    rewrite = ai_json["rewrite"]
    if not isinstance(rewrite, dict): raise ReportValidationError("Trường 'rewrite' phải là dict.")
        
    required_sections = rules_v38.REQUIRED_REWRITE_SECTIONS
    if list(rewrite.keys()) != required_sections: raise ReportValidationError("Rewrite phải có đúng 11 mục theo đúng thứ tự.")
        
    forbidden_phrases = ["người dùng muốn", "người dùng cần", "tôi muốn", "hãy giúp tôi"]
    for section in required_sections:
        value = rewrite[section]
        if not isinstance(value, str) or not value.strip(): raise ReportValidationError(f"Mục rewrite '{section}' bị thiếu hoặc rỗng.")
        if len(value.strip()) < 10: raise ReportValidationError(f"Mục rewrite '{section}' quá ngắn.")
            
        value_lower = value.lower()
        for phrase in forbidden_phrases:
            if phrase in value_lower: raise ReportValidationError(f"Mục rewrite '{section}' vi phạm quy tắc mệnh lệnh: '{phrase}'.")

    return True

def calculate_final_score(ai_scores: dict, main_criteria: dict, tech_criteria: dict) -> float:
    if not isinstance(ai_scores, dict): raise ValueError("Dữ liệu điểm không hợp lệ.")
    all_criteria_dict = {**main_criteria, **tech_criteria}
    criteria = [{"id": k, "weight": v["weight"]} for k, v in all_criteria_dict.items()]
    criteria_by_id = {c["id"]: Decimal(str(c["weight"])) for c in criteria}
    weighted_sum = Decimal("0")
    total_weight = sum(criteria_by_id.values(), Decimal("0"))
    for cid, w in criteria_by_id.items():
        weighted_sum += Decimal(ai_scores[cid]) * w
    return float((weighted_sum / total_weight).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))