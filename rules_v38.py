import re
import math

# ==========================================
# KHAI BÁO CÁC HẰNG SỐ LOẠI PROMPT & KỸ THUẬT
# ==========================================
TYPE_PROMPT = "PROMPT"
TYPE_TEMPLATE = "TEMPLATE"
TYPE_PROMPT_META = "PROMPT META"
TYPE_TABLE = "TABLE"
TYPE_STEM = "STEM"
TYPE_EMPTY = "EMPTY"
TYPE_IMAGE = "IMAGE"
TYPE_CREATIVE = "CREATIVE" # Thêm hằng số cho loại sáng tạo

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
    "P01": {"name": "Độ rõ nhiệm vụ", "weight": 1.2, "rubric": "0-2: Không có động từ hành động. 3-4: Động từ mơ hồ. 5-6: Rõ hành động. 7-10: Rõ hành động, rõ kết quả."},
    "P02": {"name": "Đối tượng tác động", "weight": 1.2, "rubric": "0-2: Không có đối tượng. 3-4: Đối tượng chung chung. 5-6: Đối tượng cụ thể. 7-10: Đối tượng rất chi tiết."},
    "P03": {"name": "Bối cảnh", "weight": 0.8, "rubric": "0-2: Không có bối cảnh. 3-4: Bối cảnh sơ sài. 5-6: Có bối cảnh rõ. 7-10: Bối cảnh phong phú, phù hợp."},
    "P04": {"name": "Định dạng đầu ra", "weight": 0.8, "rubric": "0-2: Không yêu cầu định dạng. 3-4: Yêu cầu chung chung. 5-6: Có yêu cầu cụ thể. 7-10: Yêu cầu rất chi tiết."},
    "P05": {"name": "Độ chi tiết và ví dụ", "weight": 1.6, "rubric": "0-2: Không có ví dụ. 3-4: Ít chi tiết. 5-6: Có ví dụ cơ bản. 7-10: Nhiều ví dụ và chi tiết."},
    "P06": {"name": "Không mơ hồ", "weight": 0.2, "rubric": "0-2: Rất mơ hồ. 3-4: Có từ mơ hồ. 5-6: Ít mơ hồ. 7-10: Hoàn toàn rõ ràng."},
    "P07": {"name": "Không chung chung", "weight": 0.2, "rubric": "0-2: Rất chung chung. 3-4: Còn chung chung. 5-6: Khá cụ thể. 7-10: Rất cụ thể."},
    "P08": {"name": "Có cấu trúc", "weight": 0.2, "rubric": "0-2: Không cấu trúc. 3-4: Cấu trúc lộn xộn. 5-6: Có cấu trúc cơ bản. 7-10: Cấu trúc chặt chẽ."},
    "P09": {"name": "Phù hợp nhiệm vụ", "weight": 0.5, "rubric": "0-2: Sai lệch nhiệm vụ. 3-4: Chưa phù hợp. 5-6: Khá phù hợp. 7-10: Rất phù hợp."},
    "P10": {"name": "Chuyên môn có căn cứ", "weight": 1.0, "rubric": "0-2: Vô căn cứ. 3-4: Sơ sài. 5-6: Có kiến thức cơ bản. 7-10: Chuyên sâu, chính xác và có căn cứ."},
    "P11": {"name": "Nhất quán lĩnh vực", "weight": 0.8, "rubric": "0-2: Lạc đề. 3-4: Chưa nhất quán. 5-6: Tương đối nhất quán. 7-10: Nhất quán hoàn toàn."},
    "P12": {"name": "Yêu cầu khả thi", "weight": 0.5, "rubric": "0-2: Bất khả thi. 3-4: Khó thực hiện. 5-6: Có thể thực hiện. 7-10: Rất thực tế và dễ hiểu."},
    "P13": {"name": "Vai trò phù hợp", "weight": 1.0, "rubric": "0-2: Không có vai trò. 3-4: Vai trò mờ nhạt. 5-6: Vai trò rõ ràng. 7-10: Vai trò xuất sắc, tối ưu cho task."},
    "P14": {"name": "Không mâu thuẫn", "weight": 0.2, "rubric": "0-2: Nhiều mâu thuẫn. 3-4: Có mâu thuẫn. 5-6: Ít mâu thuẫn. 7-10: Không mâu thuẫn."}
}

# ==========================================
# BỘ TIÊU CHÍ KỸ THUẬT (TECHNIQUES)
# ==========================================
CRITERIA_ROLE_PLAY = {
    "R01": {"name": "Sự phù hợp của vai trò", "weight": 1.5, "rubric": "0-2: Vai trò không liên quan. 3-4: Vai trò chung chung. 5-6: Vai trò phù hợp. 7-10: Vai trò tối ưu cho nhiệm vụ."},
    "R02": {"name": "Mục tiêu hội thoại", "weight": 1.2, "rubric": "0-2: Không có mục tiêu. 3-4: Mục tiêu mơ hồ. 5-6: Mục tiêu rõ. 7-10: Mục tiêu cụ thể, đo lường được."},
    "R03": {"name": "Giới hạn hành vi", "weight": 0.8, "rubric": "0-2: Không có ràng buộc. 3-4: Ràng buộc chung. 5-6: Ràng buộc rõ. 7-10: Ràng buộc chi tiết."}
}

CRITERIA_FEW_SHOT = {
    "F01": {"name": "Tính liên quan của ví dụ", "weight": 1.5, "rubric": "0-2: Ví dụ không liên quan. 3-4: Xa rời thực tế. 5-6: Sát với yêu cầu. 7-10: Ví dụ hoàn hảo."},
    "F02": {"name": "Độ bao quát của ví dụ", "weight": 1.2, "rubric": "0-2: Chỉ 1 ví dụ. 3-4: 1-2 ví dụ chưa bao quát. 5-6: Bao quát trường hợp phổ biến. 7-10: Bao quát cả ngoại lệ."},
    "F03": {"name": "Cấu trúc Input-Output", "weight": 0.8, "rubric": "0-2: Không cấu trúc. 3-4: Lỏng lẻo. 5-6: Rõ ràng, dễ hiểu. 7-10: Chuẩn hóa (delimiter rõ ràng)."}
}

CRITERIA_COT = {
    "C01": {"name": "Yêu cầu giải quyết có cấu trúc", "weight": 1.5, "rubric": "0-2: Không yêu cầu. 3-4: Chung chung. 5-6: Chia nhỏ vấn đề. 7-10: Quy trình từng bước rõ ràng."},
    "C02": {"name": "Khả năng kiểm tra lập luận", "weight": 1.2, "rubric": "0-2: Không có. 3-4: Sơ sài. 5-6: Yêu cầu giải thích lý do. 7-10: Yêu cầu chứng minh và kiểm tra chéo."},
    "C03": {"name": "Kết luận rõ ràng", "weight": 0.8, "rubric": "0-2: Không yêu cầu. 3-4: Mơ hồ. 5-6: Có đáp án cuối cùng. 7-10: Tách biệt rõ quá trình và kết quả."}
}

CRITERIA_FORMATTED_OUTPUT = {
    "FO01": {"name": "Schema và kiểu dữ liệu", "weight": 1.5, "rubric": "0-2: Không định dạng. 3-4: Xác định chung (JSON). 5-6: Cấu trúc cơ bản. 7-10: Schema chi tiết, rõ kiểu dữ liệu."},
    "FO02": {"name": "Trường bắt buộc", "weight": 1.0, "rubric": "0-2: Không có. 3-4: Có đề cập. 5-6: Liệt kê trường. 7-10: Chỉ định rõ bắt buộc/tùy chọn."},
    "FO03": {"name": "Quy tắc xử lý lỗi", "weight": 1.0, "rubric": "0-2: Không có. 3-4: Đề cập. 5-6: Hướng dẫn chung. 7-10: Quy định rõ cách xử lý lỗi (VD: trả về null)."}
}

CRITERIA_CREATIVE = {
    "CG01": {"name": "Mục tiêu sáng tạo", "weight": 1.5, "rubric": "0-2: Không mục tiêu. 3-4: Mơ hồ. 5-6: Rõ ràng. 7-10: Định nghĩa sắc nét, đo lường được."},
    "CG02": {"name": "Đối tượng độc giả", "weight": 1.2, "rubric": "0-2: Không có. 3-4: Chung. 5-6: Cụ thể. 7-10: Rất chi tiết (độ tuổi, sở thích...)."},
    "CG03": {"name": "Phong cách và ràng buộc", "weight": 1.0, "rubric": "0-2: Không ràng buộc. 3-4: Lỏng lẻo. 5-6: Có phong cách. 7-10: Rõ phong cách, tông giọng, số từ."}
}

# 11 Mục bắt buộc phải có trong Bản sửa (Rewrite)
REQUIRED_REWRITE_SECTIONS = [
    "1. VAI TRÒ", "2. BỐI CẢNH", "3. INPUT", "4. MỤC TIÊU", "5. YÊU CẦU", 
    "6. RÀNG BUỘC", "7. TASK", "8. ĐỊNH DẠNG ĐẦU RA", "9. NEVER DO", 
    "10. THỨ TỰ ƯU TIÊN", "11. XỬ LÝ NỘI BỘ"
]

def validate_config(main_criteria: dict, tech_criteria: dict):
    if not main_criteria:
        raise ConfigurationError("Nhóm tiêu chí chính bị rỗng.")
    all_criteria = {**main_criteria, **tech_criteria}
    if len(all_criteria) != len(main_criteria) + len(tech_criteria):
        raise ConfigurationError("Phát hiện ID tiêu chí bị trùng giữa Main và Tech.")
    for k, v in all_criteria.items():
        w = v.get("weight", 0)
        is_valid_type = type(w) in (int, float) and not isinstance(w, bool)
        if not is_valid_type or not math.isfinite(w) or w <= 0:
            raise ConfigurationError(f"Trọng số của '{k}' không hợp lệ.")

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

def match_keywords(text: str, keywords: list) -> bool:
    """Sử dụng Regex Word Boundaries để tránh khớp nhầm (VD: 'toán' trong 'toán loạn' thay vì 'toán học')."""
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
        main_task = TYPE_CREATIVE 
        
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