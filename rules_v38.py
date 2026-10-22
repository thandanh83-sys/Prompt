import math
import hashlib
import json

TYPE_PROMPT = "PROMPT"
TYPE_TEMPLATE = "TEMPLATE"
TYPE_PROMPT_META = "PROMPT META"
TYPE_TABLE = "TABLE"
TYPE_STEM = "STEM"
TYPE_EMPTY = "EMPTY"
TYPE_IMAGE = "IMAGE"
TYPE_GENERAL = "GENERAL"

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

CRITERIA_GENERAL = {
    "G01": {"name": "Mục tiêu rõ ràng", "weight": 1.5, "rubric": "0-2: Không có mục tiêu. 5-6: Mục tiêu mơ hồ. 7-10: Mục tiêu rõ ràng."},
    "G02": {"name": "Bối cảnh và Đối tượng", "weight": 1.2, "rubric": "0-2: Thiếu bối cảnh. 5-6: Bối cảnh chung chung. 7-10: Bối cảnh chi tiết."},
    "G03": {"name": "Ràng buộc và Định dạng", "weight": 1.2, "rubric": "0-2: Không có ràng buộc. 5-6: Ràng buộc lỏng lẻo. 7-10: Ràng buộc chặt chẽ."},
    "G04": {"name": "Tính chuyên môn", "weight": 1.0, "rubric": "0-2: Sai kiến thức. 5-6: Chấp nhận được. 7-10: Chính xác chuyên ngành."},
    "G05": {"name": "Ví dụ và Dẫn chứng", "weight": 1.0, "rubric": "0-2: Không có ví dụ. 5-6: Sơ sài. 7-10: Minh họa xuất sắc."}
}

REQUIRED_REWRITE_SECTIONS = [
    "1. VAI TRÒ", "2. BỐI CẢNH", "3. INPUT", "4. MỤC TIÊU", "5. YÊU CẦU", 
    "6. RÀNG BUỘC", "7. TASK", "8. ĐỊNH DẠNG ĐẦU RA", "9. NEVER DO", 
    "10. THỨ TỰ ƯU TIÊN", "11. XỬ LÝ NỘI BỘ"
]

def classify_prompt(prompt_text: str) -> dict:
    text = prompt_text.strip()
    if not text: return {"main_task": TYPE_EMPTY, "techniques": []}
    return {"main_task": TYPE_GENERAL, "techniques": []}