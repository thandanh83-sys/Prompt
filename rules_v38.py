import re
import math

# ==========================================
# HẰNG SỐ PHÂN LOẠI
# ==========================================
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

# ==========================================
# BỘ TIÊU CHÍ LÕI (CORE CRITERIA) - 14 TIÊU CHÍ
# ==========================================
CRITERIA_CORE = {
    "P01": {"name": "Độ rõ nhiệm vụ", "weight": 1.2, "rubric": "0-2: Không có động từ. 3-4: Động từ mơ hồ. 5-6: Rõ hành động. 7-10: Rõ hành động, rõ kết quả."},
    "P02": {"name": "Đối tượng tác động", "weight": 1.2, "rubric": "0-2: Không có. 3-4: Chung chung. 5-6: Cụ thể. 7-10: Rất chi tiết."},
    "P03": {"name": "Bối cảnh", "weight": 0.8, "rubric": "0-2: Không có. 3-4: Sơ sài. 5-6: Rõ ràng. 7-10: Phong phú, phù hợp."},
    "P04": {"name": "Định dạng đầu ra", "weight": 0.8, "rubric": "0-2: Không yêu cầu. 3-4: Chung chung. 5-6: Cụ thể. 7-10: Rất chi tiết."},
    "P05": {"name": "Độ chi tiết và ví dụ", "weight": 1.6, "rubric": "0-2: Không có. 3-4: Ít. 5-6: Cơ bản. 7-10: Chi tiết, ví dụ phù hợp."},
    "P06": {"name": "Không mơ hồ", "weight": 0.2, "rubric": "0-2: Rất mơ hồ. 3-4: Có từ mơ hồ. 5-6: Ít. 7-10: Rõ ràng."},
    "P07": {"name": "Không chung chung", "weight": 0.2, "rubric": "0-2: Chung chung. 3-4: Còn chung. 5-6: Khá cụ thể. 7-10: Rất cụ thể."},
    "P08": {"name": "Có cấu trúc", "weight": 0.2, "rubric": "0-2: Không. 3-4: Lộn xộn. 5-6: Cơ bản. 7-10: Chặt chẽ."},
    "P09": {"name": "Phù hợp nhiệm vụ", "weight": 0.5, "rubric": "0-2: Sai lệch. 3-4: Chưa phù hợp. 5-6: Khá. 7-10: Rất phù hợp."},
    "P10": {"name": "Chuyên môn có căn cứ", "weight": 1.0, "rubric": "0-2: Vô căn cứ. 3-4: Sơ sài. 5-6: Cơ bản. 7-10: Chuyên sâu."},
    "P11": {"name": "Nhất quán lĩnh vực", "weight": 0.8, "rubric": "0-2: Lạc đề. 3-4: Chưa nhất quán. 5-6: Tương đối. 7-10: Hoàn toàn."},
    "P12": {"name": "Yêu cầu khả thi", "weight": 0.5, "rubric": "0-2: Bất khả thi. 3-4: Khó. 5-6: Có thể. 7-10: Thực tế."},
    "P13": {"name": "Vai trò phù hợp", "weight": 1.0, "rubric": "0-2: Không có. 3-4: Mờ nhạt. 5-6: Rõ. 7-10: Xuất sắc."},
    "P14": {"name": "Không mâu thuẫn", "weight": 0.2, "rubric": "0-2: Nhiều mâu thuẫn. 3-4: Có mâu thuẫn. 5-6: Ít. 7-10: Không."}
}

# ==========================================
# BỘ TIÊU CHÍ KỸ THUẬT
# ==========================================
CRITERIA_ROLE_PLAY = {
    "R01": {"name": "Sự phù hợp của vai trò", "weight": 1.5, "rubric": "0-2: Không liên quan. 3-4: Chung chung. 5-6: Phù hợp. 7-10: Tối ưu."},
    "R02": {"name": "Mục tiêu hội thoại", "weight": 1.2, "rubric": "0-2: Không. 3-4: Mơ hồ. 5-6: Rõ. 7-10: Cụ thể."},
    "R03": {"name": "Giới hạn hành vi", "weight": 0.8, "rubric": "0-2: Không có. 3-4: Chung. 5-6: Rõ. 7-10: Chi tiết."}
}

CRITERIA_FEW_SHOT = {
    "F01": {"name": "Tính liên quan của ví dụ", "weight": 1.5, "rubric": "0-2: Không liên quan. 3-4: Xa rời. 5-6: Sát. 7-10: Hoàn hảo."},
    "F02": {"name": "Độ bao quát của ví dụ", "weight": 1.2, "rubric": "0-2: Chỉ 1. 3-4: Chưa bao quát. 5-6: Phổ biến. 7-10: Cả ngoại lệ."},
    "F03": {"name": "Cấu trúc Input-Output", "weight": 0.8, "rubric": "0-2: Không. 3-4: Lỏng lẻo. 5-6: Rõ. 7-10: Chuẩn hóa."}
}

CRITERIA_COT = {
    "C01": {"name": "Yêu cầu giải quyết có cấu trúc", "weight": 1.5, "rubric": "0-2: Không. 3-4: Chung chung. 5-6: Chia nhỏ. 7-10: Từng bước rõ ràng."},
    "C02": {"name": "Khả năng kiểm tra lập luận", "weight": 1.2, "rubric": "0-2: Không. 3-4: Sơ sài. 5-6: Giải thích. 7-10: Chứng minh, kiểm tra chéo."},
    "C03": {"name": "Kết luận rõ ràng", "weight": 0.8, "rubric": "0-2: Không. 3-4: Mơ hồ. 5-6: Đáp án. 7-10: Tách biệt quá trình/kết quả."}
}

CRITERIA_FORMATTED_OUTPUT = {
    "FO01": {"name": "Schema và kiểu dữ liệu", "weight": 1.5, "rubric": "0-2: Không. 3-4: Xác định chung. 5-6: Cơ bản. 7-10: Chi tiết, rõ kiểu."},
    "FO02": {"name": "Trường bắt buộc", "weight": 1.0, "rubric": "0-2: Không. 3-4: Có đề cập. 5-6: Liệt kê. 7-10: Bắt buộc/tùy chọn."},
    "FO03": {"name": "Quy tắc xử lý lỗi", "weight": 1.0, "rubric": "0-2: Không. 3-4: Đề cập. 5-6: Hướng dẫn. 7-10: Quy định rõ."}
}

CRITERIA_CREATIVE = {
    "CG01": {"name": "Mục tiêu sáng tạo", "weight": 1.5, "rubric": "0-2: Không. 3-4: Mơ hồ. 5-6: Rõ. 7-10: Sắc nét."},
    "CG02": {"name": "Đối tượng độc giả", "weight": 1.2, "rubric": "0-2: Không. 3-4: Chung. 5-6: Cụ thể. 7-10: Rất chi tiết."},
    "CG03": {"name": "Phong cách và ràng buộc", "weight": 1.0, "rubric": "0-2: Không. 3-4: Lỏng lẻo. 5-6: Có phong cách. 7-10: Rõ ràng."}
}

REQUIRED_REWRITE_SECTIONS = [
    "1. VAI TRÒ", "2. BỐI CẢNH", "3. INPUT", "4. MỤC TIÊU", "5. YÊU CẦU", 
    "6. RÀNG BUỘC", "7. TASK", "8. ĐỊNH DẠNG ĐẦU RA", "9. NEVER DO", 
    "10. THỨ TỰ ƯU TIÊN", "11. XỬ LÝ NỘI BỘ"
]

# ==========================================
# HÀM KIỂM TRA CẤU HÌNH (CHẠY KHI KHỞI ĐỘNG)
# ==========================================
def validate_startup_config():
    if len(REQUIRED_REWRITE_SECTIONS) != 11:
        raise ConfigurationError("REQUIRED_REWRITE_SECTIONS phải có đúng 11 mục.")
    if len(set(REQUIRED_REWRITE_SECTIONS)) != 11:
        raise ConfigurationError("REQUIRED_REWRITE_SECTIONS bị trùng tên.")
        
    all_groups = [CRITERIA_CORE, CRITERIA_ROLE_PLAY, CRITERIA_FEW_SHOT, CRITERIA_COT, CRITERIA_FORMATTED_OUTPUT, CRITERIA_CREATIVE]
    seen_ids = set()
    for group in all_groups:
        for k, v in group.items():
            if k in seen_ids:
                raise ConfigurationError(f"Trùng ID tiêu chí: {k}")
            seen_ids.add(k)
            if not v.get("name") or not v.get("rubric"):
                raise ConfigurationError(f"Tiêu chí {k} thiếu tên hoặc rubric.")
            if not isinstance(v.get("weight"), (int, float)) or v["weight"] <= 0:
                raise ConfigurationError(f"Trọng số của {k} không hợp lệ.")

# Gọi hàm kiểm tra ngay khi import module
validate_startup_config()

# ==========================================
# HÀM XỬ LÝ
# ==========================================
def get_criteria_by_type(classification: dict) -> dict:
    techniques = classification.get("techniques", [])
    
    main_criteria = CRITERIA_CORE.copy()
    tech_criteria = {}
    
    if TECH_ROLE_PLAY in techniques: tech_criteria.update(CRITERIA_ROLE_PLAY)
    if TECH_FEW_SHOT in techniques: tech_criteria.update(CRITERIA_FEW_SHOT)
    if TECH_COT in techniques: tech_criteria.update(CRITERIA_COT)
    if TECH_FORMAT in techniques: tech_criteria.update(CRITERIA_FORMATTED_OUTPUT)
    if TECH_CREATIVE in techniques: tech_criteria.update(CRITERIA_CREATIVE)

    return {"main": main_criteria, "tech": tech_criteria}

def match_keywords(text: str, keywords: list) -> bool:
    """Sử dụng Regex Word Boundaries để tránh khớp nhầm (VD: 'toán' trong 'toán học' ok, nhưng không khớp trong 'toán loạn')."""
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", text):
            return True
    return False

def classify_prompt(prompt_text: str) -> dict:
    if not isinstance(prompt_text, str): return {"main_task": TYPE_EMPTY, "techniques": []}
    text = prompt_text.strip()
    if not text: return {"main_task": TYPE_EMPTY, "techniques": []}
    
    lower_text = text.lower()
    techniques = []
    
    # 1. NHẬN DIỆN KỸ THUẬT (Siết chặt bằng Regex)
    if match_keywords(lower_text, ["đóng vai", "bạn là", "hãy vào vai", "giả sử bạn là", "act as", "role:", "vai trò:"]):
        techniques.append(TECH_ROLE_PLAY)
    if match_keywords(lower_text, ["ví dụ 1:", "ví dụ mẫu", "input:", "output:", "dưới đây là ví dụ", "few-shot"]):
        techniques.append(TECH_FEW_SHOT)
    if match_keywords(lower_text, ["từng bước", "suy luận", "giải thích từng bước", "chain of thought", "step-by-step", "cot"]):
        techniques.append(TECH_COT)
    if match_keywords(lower_text, ["json", "xml", "định dạng bảng", "markdown", "output format:", "yaml", "csv"]):
        techniques.append(TECH_FORMAT)
    if match_keywords(lower_text, ["viết truyện", "làm thơ", "sáng tác", "kịch bản", "viết quảng cáo", "viết content", "story", "poem", "script"]):
        techniques.append(TECH_CREATIVE)

    # 2. NHẬN DIỆN LOẠI PROMPT (Ưu tiên Động từ hành động chính)
    main_task = TYPE_PROMPT
    
    # Ưu tiên 1: Meta Prompt (Thường bắt đầu bằng "Viết prompt")
    if match_keywords(lower_text, ["viết prompt", "tạo prompt", "meta prompt", "prompt engineering", "cải thiện prompt"]):
        main_task = TYPE_PROMPT_META
        
    # Ưu tiên 2: Creative (Nếu có động từ sáng tạo, nó đè lên các từ khóa toán/lý)
    elif match_keywords(lower_text, ["viết truyện", "làm thơ", "sáng tác", "viết bài văn", "viết kịch bản"]):
        main_task = TYPE_CREATIVE if 'TYPE_CREATIVE' in globals() else TYPE_PROMPT # Fallback to PROMPT if CREATIVE type isn't mapped
        
    # Ưu tiên 3: Image
    elif match_keywords(lower_text, ["vẽ ảnh", "tạo ảnh", "midjourney", "stable diffusion", "dall-e", "bức tranh"]):
        main_task = TYPE_IMAGE
        
    # Ưu tiên 4: Table
    elif match_keywords(lower_text, ["dạng bảng", "tạo bảng", "lập bảng", "excel", "markdown table"]):
        main_task = TYPE_TABLE
        
    # Ưu tiên 5: STEM (Chỉ nhận nếu không rơi vào các case trên)
    elif match_keywords(lower_text, ["toán", "vật lý", "hóa học", "phương trình", "tích phân", "thuật toán", "code", "python", "javascript", "c++", "java"]):
        main_task = TYPE_STEM
        
    # Ưu tiên 6: Template
    elif match_keywords(lower_text, ["mẫu sau", "theo mẫu", "template", "điền vào chỗ trống"]):
        main_task = TYPE_TEMPLATE

    return {"main_task": main_task, "techniques": techniques}