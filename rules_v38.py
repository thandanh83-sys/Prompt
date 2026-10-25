import math

TYPE_PROMPT = "PROMPT"
TYPE_TEMPLATE = "TEMPLATE"
TYPE_PROMPT_META = "PROMPT META"
TYPE_TABLE = "TABLE"
TYPE_STEM = "STEM"
TYPE_EMPTY = "EMPTY"
TYPE_IMAGE = "IMAGE"

TECH_ROLE_PLAY = "ROLE_PLAY"
TECH_FEW_SHOT = "FEW_SHOT"
TECH_COT = "CHAIN_OF_THOUGHT"
TECH_FORMAT = "FORMATTED_OUTPUT"
TECH_CREATIVE = "CREATIVE_GEN"

class ConfigurationError(Exception):
    pass

VALID_ERROR_CODES = {
    "A01": "Lỗi chính tả", "A02": "Thiếu dấu câu", "A03": "Lặp lại",
    "B01": "Thiếu thành phần cấu trúc", "B02": "Mục không logic", "B03": "Sai phân cấp", "B04": "Chưa quy định định dạng đầu ra",
    "C01": "Đối tượng chưa rõ", "C02": "Thiếu bối cảnh", "C03": "Yêu cầu chung chung", "C04": "Thiếu ví dụ",
    "D01": "Mâu thuẫn nội bộ", "D02": "Yêu cầu bất khả thi", "D03": "Vai trò không phù hợp",
    "E01": "Trộn lĩnh vực", "E02": "Thuật ngữ không nhất quán", "E03": "Thiếu tính đặc thù lĩnh vực"
}

# BỘ TIÊU CHÍ LÕI (Dùng chung cho mọi Prompt)
CRITERIA_CORE = {
    "P01": {"name": "Độ rõ nhiệm vụ", "weight": 1.2, "rubric": "0-2: Không có động từ hành động. 3-4: Động từ mơ hồ. 5-6: Rõ hành động. 7-10: Rõ hành động, rõ kết quả."},
    "P02": {"name": "Đối tượng tác động", "weight": 1.2, "rubric": "0-2: Không có đối tượng. 3-4: Đối tượng chung chung. 5-6: Đối tượng cụ thể. 7-10: Đối tượng rất chi tiết."},
    "P03": {"name": "Bối cảnh", "weight": 0.8, "rubric": "0-2: Không có bối cảnh. 3-4: Bối cảnh sơ sài. 5-6: Có bối cảnh rõ. 7-10: Bối cảnh phong phú."},
    "P04": {"name": "Định dạng đầu ra", "weight": 0.8, "rubric": "0-2: Không yêu cầu định dạng. 3-4: Yêu cầu chung chung. 5-6: Có yêu cầu cụ thể. 7-10: Yêu cầu rất chi tiết."},
    "P05": {"name": "Độ chi tiết và ví dụ", "weight": 1.6, "rubric": "0-2: Không có ví dụ. 3-4: Ít chi tiết. 5-6: Có ví dụ cơ bản. 7-10: Nhiều ví dụ và chi tiết."},
    "P06": {"name": "Không mơ hồ", "weight": 0.2, "rubric": "0-2: Rất mơ hồ. 3-4: Có từ mơ hồ. 5-6: Ít mơ hồ. 7-10: Hoàn toàn rõ ràng."},
    "P07": {"name": "Không chung chung", "weight": 0.2, "rubric": "0-2: Rất chung chung. 3-4: Còn chung chung. 5-6: Khá cụ thể. 7-10: Rất cụ thể."},
    "P08": {"name": "Có cấu trúc", "weight": 0.2, "rubric": "0-2: Không cấu trúc. 3-4: Cấu trúc lộn xộn. 5-6: Có cấu trúc cơ bản. 7-10: Cấu trúc chặt chẽ."},
    "P09": {"name": "Phù hợp nhiệm vụ", "weight": 0.5, "rubric": "0-2: Sai lệch nhiệm vụ. 3-4: Chưa phù hợp. 5-6: Khá phù hợp. 7-10: Rất phù hợp."},
    "P14": {"name": "Không mâu thuẫn", "weight": 0.2, "rubric": "0-2: Nhiều mâu thuẫn. 3-4: Có mâu thuẫn. 5-6: Ít mâu thuẫn. 7-10: Không mâu thuẫn."}
}

# BỘ TIÊU CHÍ KỸ THUẬT
CRITERIA_ROLE_PLAY = {
    "R01": {"name": "Sự phù hợp của vai trò", "weight": 1.5, "rubric": "0-2: Vai trò không liên quan. 7-10: Vai trò tối ưu."},
    "R02": {"name": "Mục tiêu hội thoại", "weight": 1.2, "rubric": "0-2: Không có mục tiêu. 7-10: Mục tiêu cụ thể."},
}
CRITERIA_FEW_SHOT = {
    "F01": {"name": "Tính liên quan của ví dụ", "weight": 1.5, "rubric": "0-2: Không liên quan. 7-10: Ví dụ hoàn hảo."},
    "F02": {"name": "Độ bao quát của ví dụ", "weight": 1.2, "rubric": "0-2: Chỉ 1 ví dụ. 7-10: Bao quát ngoại lệ."},
}
CRITERIA_COT = {
    "C01": {"name": "Yêu cầu giải quyết có cấu trúc", "weight": 1.5, "rubric": "0-2: Không yêu cầu. 7-10: Quy trình từng bước rõ ràng."},
}
CRITERIA_FORMATTED_OUTPUT = {
    "FO01": {"name": "Schema và kiểu dữ liệu", "weight": 1.5, "rubric": "0-2: Không xác định. 7-10: Schema chi tiết."},
}
CRITERIA_CREATIVE = {
    "CG01": {"name": "Mục tiêu sáng tạo", "weight": 1.5, "rubric": "0-2: Không có. 7-10: Định nghĩa sắc nét."},
}

REQUIRED_REWRITE_SECTIONS = [
    "1. VAI TRÒ", "2. BỐI CẢNH", "3. INPUT", "4. MỤC TIÊU", "5. YÊU CẦU", 
    "6. RÀNG BUỘC", "7. TASK", "8. ĐỊNH DẠNG ĐẦU RA", "9. NEVER DO", 
    "10. THỨ TỰ ƯU TIÊN", "11. XỬ LÝ NỘI BỘ"
]

def validate_config(main_criteria: dict, tech_criteria: dict):
    if not main_criteria: raise ConfigurationError("Rỗng.")
    all_criteria = {**main_criteria, **tech_criteria}
    for k, v in all_criteria.items():
        w = v.get("weight", 0)
        if type(w) not in (int, float) or not math.isfinite(w) or w <= 0:
            raise ConfigurationError(f"Trọng số '{k}' không hợp lệ.")

def get_criteria_by_type(classification: dict) -> dict:
    techniques = classification.get("techniques", [])
    main_criteria = CRITERIA_CORE.copy()
    tech_criteria = {}
    
    if TECH_ROLE_PLAY in techniques: tech_criteria.update(CRITERIA_ROLE_PLAY)
    if TECH_FEW_SHOT in techniques: tech_criteria.update(CRITERIA_FEW_SHOT)
    if TECH_COT in techniques: tech_criteria.update(CRITERIA_COT)
    if TECH_FORMAT in techniques: tech_criteria.update(CRITERIA_FORMATTED_OUTPUT)
    if TECH_CREATIVE in techniques: tech_criteria.update(CRITERIA_CREATIVE)

    validate_config(main_criteria, tech_criteria)
    return {"main": main_criteria, "tech": tech_criteria}

def classify_prompt(prompt_text: str) -> dict:
    if not isinstance(prompt_text, str): return {"main_task": TYPE_EMPTY, "techniques": []}
    text = prompt_text.strip()
    if not text: return {"main_task": TYPE_EMPTY, "techniques": []}
    
    lower_text = text.lower()
    techniques = []
    
    if any(kw in lower_text for kw in ["đóng vai", "bạn là", "act as", "role:"]): techniques.append(TECH_ROLE_PLAY)
    if any(kw in lower_text for kw in ["ví dụ 1:", "few-shot"]): techniques.append(TECH_FEW_SHOT)
    if any(kw in lower_text for kw in ["từng bước", "step-by-step", "quy trình"]): techniques.append(TECH_COT)
    if any(kw in lower_text for kw in ["json", "xml", "markdown", "output format:"]): techniques.append(TECH_FORMAT)
    if any(kw in lower_text for kw in ["viết truyện", "làm thơ", "sáng tác", "story"]): techniques.append(TECH_CREATIVE)

    return {"main_task": TYPE_PROMPT, "techniques": techniques}