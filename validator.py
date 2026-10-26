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
        missing = required_ids - received_ids
        extra = received_ids - required_ids
        raise ReportValidationError(f"Sai tập tiêu chí. Thiếu: {sorted(missing)}; Thừa: {sorted(extra)}")
        
    for crit_id, score in ai_scores.items():
        if type(score) is not int:
            raise ReportValidationError(f"Điểm của '{crit_id}' phải là số nguyên.")
        if not (0 <= score <= 10):
            raise ReportValidationError(f"Điểm của '{crit_id}' phải nằm trong khoảng 0-10.")
    return True

def validate_full_report(ai_json: dict, main_criteria: dict, tech_criteria: dict, original_prompt: str) -> bool:
    if not isinstance(ai_json, dict): 
        raise ReportValidationError("Dữ liệu AI không phải JSON Object.")
        
    required_keys = {"scores", "errors", "rewrite", "identified_domain"}
    if set(ai_json.keys()) != required_keys:
        raise ReportValidationError(f"JSON phải có chính xác các key: {required_keys}. Nhận được: {set(ai_json.keys())}")

    # [FIX LỖI 1] Kiểm tra giao nhau giữa Main và Tech
    collision_ids = set(main_criteria.keys()).intersection(set(tech_criteria.keys()))
    if collision_ids:
        raise ReportValidationError(f"LỖI CẤU HÌNH: ID tiêu chí bị trùng giữa Main và Tech: {collision_ids}")

    domain = ai_json["identified_domain"]
    if not isinstance(domain, str) or len(domain.strip()) < 2:
        raise ReportValidationError("'identified_domain' phải là chuỗi có nghĩa (dài hơn 2 ký tự).")

    all_criteria = {**main_criteria, **tech_criteria}
    validate_scores_only(ai_json["scores"], all_criteria)

    errors = ai_json["errors"]
    if not isinstance(errors, list): 
        raise ReportValidationError("Trường 'errors' phải là list.")
    if len(errors) > 15:
        raise ReportValidationError("Quá nhiều lỗi (max 15). AI đang bịa lỗi để lấp đầy báo cáo.")
        
    prompt_norm = normalize_text(original_prompt)
    valid_error_codes = set(error_rules.ERROR_RULES.keys())
    
    # [FIX LỖI 4] Chống trùng lặp bằng chứng
    seen_evidence = set() 

    for err in errors:
        if not isinstance(err, dict):
            raise ReportValidationError("Mỗi lỗi phải là object.")
        
        if set(err.keys()) != {"code", "evidence", "hint"}:
            raise ReportValidationError("Mỗi lỗi phải có chính xác 'code', 'evidence', và 'hint'.")
            
        code = err["code"]
        evidence = err["evidence"]
        hint = err["hint"]
        
        if not isinstance(code, str) or code not in valid_error_codes:
            raise ReportValidationError(f"Mã lỗi không hợp lệ hoặc không tồn tại: {code!r}")
            
        if not isinstance(evidence, str) or not evidence.strip():
            raise ReportValidationError(f"Lỗi {code} thiếu bằng chứng hợp lệ.")
            
        # [FIX LỖI 2 & 3] Kiểm tra bằng chứng động dựa trên error_rules
        rule = error_rules.ERROR_RULES.get(code, {})
        require_quote = rule.get("require_quote", True) # Mặc định phải trích dẫn
        
        evidence_norm = normalize_text(evidence)
        
        if evidence_norm in seen_evidence:
            raise ReportValidationError(f"Bằng chứng bị trùng lặp cho nhiều mã lỗi: '{evidence}'. Hãy gộp lại hoặc làm rõ.")
        seen_evidence.add(evidence_norm)

        if require_quote:
            if len(evidence_norm) < 5:
                raise ReportValidationError(f"Bằng chứng của {code} quá ngắn, không đủ để chứng minh.")
            if evidence_norm not in prompt_norm:
                raise ReportValidationError(f"Bằng chứng của {code} không khớp với prompt gốc. Evidence: '{evidence}'")
        else:
            # Lỗi thiếu thông tin: Không cần trích dẫn, nhưng phải giải thích rõ
            if len(evidence_norm) < 15:
                raise ReportValidationError(f"Bằng chứng của {code} quá chung chung. Cần mô tả rõ thông tin bị thiếu (trên 15 ký tự).")
                
        if not isinstance(hint, str) or len(hint.strip()) < 10:
            raise ReportValidationError(f"Hint của {code} quá ngắn, cần hướng dẫn sửa cụ thể (trên 10 ký tự).")

    rewrite = ai_json["rewrite"]
    if not isinstance(rewrite, dict): 
        raise ReportValidationError("Trường 'rewrite' phải là dict.")
        
    required_sections = rules_v38.REQUIRED_REWRITE_SECTIONS
    if list(rewrite.keys()) != required_sections:
        raise ReportValidationError("Rewrite phải có đúng 11 mục theo đúng thứ tự backend quy định.")
        
    # [FIX LỖI 5] Kiểm tra chất lượng nội dung Rewrite
    forbidden_phrases = ["người dùng muốn", "người dùng cần", "tôi muốn", "hãy giúp tôi", "chưa cung cấp thông tin"]
    
    for section in required_sections:
        value = rewrite[section]
        if not isinstance(value, str) or not value.strip():
            raise ReportValidationError(f"Mục rewrite '{section}' bị thiếu hoặc rỗng.")
            
        if len(value.strip()) < 15:
            raise ReportValidationError(f"Mục rewrite '{section}' quá ngắn (dưới 15 ký tự). Cần viết chi tiết hơn.")
            
        value_lower = value.lower()
        for phrase in forbidden_phrases:
            # Ngoại trừ trường hợp "chưa cung cấp thông tin" được phép xuất hiện trong mục INPUT hoặc BỐI CẢNH như một placeholder
            if phrase == "chưa cung cấp thông tin" and section in ["3. INPUT", "2. BỐI CẢNH"]:
                continue
            if phrase in value_lower:
                raise ReportValidationError(f"Mục rewrite '{section}' vi phạm quy tắc viết mệnh lệnh. Không được dùng cụm từ tường thuật: '{phrase}'.")

    return True

def calculate_final_score(ai_scores: dict, main_criteria: dict, tech_criteria: dict) -> float:
    if not isinstance(ai_scores, dict):
        raise ValueError("Dữ liệu điểm không hợp lệ.")
        
    all_criteria_dict = {**main_criteria, **tech_criteria}
    criteria = [{"id": k, "weight": v["weight"]} for k, v in all_criteria_dict.items()]
    
    if not criteria:
        raise ValueError("Không có tiêu chí để chấm.")
        
    criteria_by_id = {}
    for criterion in criteria:
        if not isinstance(criterion, dict):
            raise ValueError("Cấu trúc tiêu chí không hợp lệ.")
        criterion_id = criterion.get("id")
        weight = criterion.get("weight")
        
        if not isinstance(criterion_id, str) or not criterion_id:
            raise ValueError("Tiêu chí thiếu ID hợp lệ.")
        if criterion_id in criteria_by_id:
            raise ValueError(f"ID tiêu chí bị trùng: {criterion_id}")
            
        if isinstance(weight, bool) or not isinstance(weight, (int, float, Decimal)):
            raise ValueError(f"Trọng số không hợp lệ: {criterion_id}")
            
        weight = Decimal(str(weight))
        if not weight.is_finite() or weight <= 0:
            raise ValueError(f"Trọng số phải hữu hạn và lớn hơn 0: {criterion_id}")
            
        criteria_by_id[criterion_id] = weight

    # [FIX LỖI 9] Kiểm tra kiểu dữ liệu của ai_scores trước khi tạo set
    if not all(isinstance(k, str) for k in ai_scores.keys()):
         raise ValueError("Các key của ai_scores phải là chuỗi.")

    expected_ids = set(criteria_by_id.keys())
    actual_ids = set(ai_scores.keys())
    
    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)
        extra = sorted(actual_ids - expected_ids)
        raise ValueError(f"Sai danh sách tiêu chí. Thiếu: {missing}; thừa: {extra}")

    weighted_sum = Decimal("0")
    total_weight = sum(criteria_by_id.values(), Decimal("0"))
    
    for criterion_id, weight in criteria_by_id.items():
        score = ai_scores[criterion_id]
        if isinstance(score, bool) or not isinstance(score, int):
            raise ValueError(f"Điểm phải là số nguyên: {criterion_id}")
        if not 0 <= score <= 10:
            raise ValueError(f"Điểm ngoài khoảng 0–10: {criterion_id}")
        weighted_sum += Decimal(score) * weight

    final_score = weighted_sum / total_weight
    return float(final_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))