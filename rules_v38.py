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
TYPE_GENERAL = "GENERAL" # <-- THÊM MỚI: Loại tổng quát cho mọi lĩnh vực

TECH_ROLE_PLAY = "ROLE_PLAY"
TECH_FEW_SHOT = "FEW_SHOT"
TECH_COT = "CHAIN_OF_THOUGHT"
TECH_FORMAT = "FORMATTED_OUTPUT"
TECH_CREATIVE = "CREATIVE_GEN"

class ConfigurationError(Exception):
    """Ngoại lệ cho lỗi cấu hình tiêu chí."""
    pass

VALID_ERROR_CODES = {
    "A01": "Lỗi chính tả", "A02": "Thiếu dấu câu", "A03": "Lặp lại",
    "B01": "Thiếu thành phần cấu trúc", "B02": "Mục không logic", "B03": "Sai phân cấp", "B04": "Chưa quy định định dạng đầu ra",
    "C01": "Đối tượng chưa rõ", "C02": "Thiếu bối cảnh", "C03": "Yêu cầu chung chung", "C04": "Thiếu ví dụ",
    "D01": "Mâu thuẫn nội bộ", "D02": "Yêu cầu bất khả thi", "D03": "Vai trò không phù hợp",
    "E01": "Trộn lĩnh vực", "E02": "Thuật ngữ không nhất quán", "E03": "Thiếu tính đặc thù lĩnh vực"
}

# --- BỘ TIÊU CHÍ TỔNG QUÁT (Áp dụng cho mọi lĩnh vực mới) ---
CRITERIA_GENERAL = {
    "G01": {"name": "Mục tiêu rõ ràng", "weight": 1.5, "rubric": "0-2: Không có mục tiêu. 5-6: Mục tiêu mơ hồ. 7-10: Mục tiêu rõ ràng, đo lường được."},
    "G02": {"name": "Bối cảnh và Đối tượng", "weight": 1.2, "rubric": "0-2: Thiếu bối cảnh. 5-6: Bối cảnh chung chung. 7-10: Bối cảnh chi tiết, xác định rõ đối tượng."},
    "G03": {"name": "Ràng buộc và Định dạng", "weight": 1.2, "rubric": "0-2: Không có ràng buộc. 5-6: Ràng buộc lỏng lẻo. 7-10: Ràng buộc chặt chẽ, định dạng đầu ra rõ ràng."},
    "G04": {"name": "Tính chuyên môn", "weight": 1.0, "rubric": "0-2: Sai kiến thức cơ bản. 5-6: Kiến thức chấp nhận được. 7-10: Sử dụng thuật ngữ chuyên ngành chính xác."},
    "G05": {"name": "Ví dụ và Dẫn chứng", "weight": 1.0, "rubric": "0-2: Không có ví dụ. 5-6: Có ví dụ nhưng sơ sài. 7-10: Ví dụ minh họa xuất sắc."}
}

# --- BỘ TIÊU CHÍ CŨ (Giữ nguyên) ---
CRITERIA_PROMPT = {
    "P01": {"name": "Độ rõ nhiệm vụ", "weight": 1.2, "rubric": "0-2: Không có động từ hành động. 3-4: Động từ mơ hồ. 5-6: Rõ hành động. 7-10: Rõ hành động, rõ kết quả."},
    "P02": {"name": "Đối tượng tác động", "weight": 1.2, "rubric": "0-2: Không có đối tượng. 3-4: Đối tượng chung chung. 5-6: Đối tượng cụ thể. 7-10: Đối tượng rất chi tiết."},
    "P03": {"name": "Bối cảnh", "weight": 0.8, "rubric": "0-2: Không có bối cảnh. 3-4: Bối cảnh sơ sài. 5-6: Có bối cảnh rõ. 7-10: Bối cảnh phong phú."},
    "P04": {"name": "Định dạng đầu ra", "weight": 0.8, "rubric": "0-2: Không yêu cầu định dạng. 3-4: Yêu cầu chung chung. 5-6: Có yêu cầu cụ thể. 7-10: Yêu cầu rất chi tiết."},
    "P05": {"name": "Độ chi tiết và ví dụ", "weight": 1.6, "rubric": "0-2: Không có ví dụ. 3-4: Ít chi tiết. 5-6: Có ví dụ cơ bản. 7-10: Nhiều ví dụ và chi tiết."},
    "P06": {"name": "Không mơ hồ", "weight": 0.2, "rubric": "0-2: Rất mơ hồ. 3-4: Có từ mơ hồ. 5-6: Ít mơ hồ. 7-10: Hoàn toàn rõ ràng."},
    "P07": {"name": "Không chung chung", "weight": 0.2, "rubric": "0-2: Rất chung chung. 3-4: Còn chung chung. 5-6: Khá cụ thể. 7-10: Rất cụ thể."},
    "P08": {"name": "Có cấu trúc", "weight": 0.2, "rubric": "0-2: Không cấu trúc. 3-4: Cấu trúc lộn xộn. 5-6: Có cấu trúc cơ bản. 7-10: Cấu trúc chặt chẽ."},
    "P09": {"name": "Phù hợp nhiệm vụ", "weight": 0.5, "rubric": "0-2: Sai lệch nhiệm vụ. 3-4: Chưa phù hợp. 5-6: Khá phù hợp. 7-10: Rất phù hợp."},
    "P10": {"name": "Chuyên môn có căn cứ", "weight": 0.5, "rubric": "0-2: Không có căn cứ. 3-4: Căn cứ yếu. 5-6: Có căn cứ. 7-10: Căn cứ vững chắc."},
    "P11": {"name": "Nhất quán lĩnh vực", "weight": 1.0, "rubric": "0-2: Trộn lẫn lĩnh vực. 3-4: Chưa nhất quán. 5-6: Khá nhất quán. 7-10: Rất nhất quán."},
    "P12": {"name": "Yêu cầu khả thi", "weight": 0.8, "rubric": "0-2: Bất khả thi. 3-4: Khó thực hiện. 5-6: Có thể thực hiện. 7-10: Rất khả thi."},
    "P13": {"name": "Vai trò phù hợp", "weight": 0.8, "rubric": "0-2: Không có vai trò. 3-4: Vai trò mờ nhạt. 5-6: Vai trò rõ. 7-10: Vai trò rất phù hợp."},
    "P14": {"name": "Không mâu thuẫn", "weight": 0.2, "rubric": "0-2: Nhiều mâu thuẫn. 3-4: Có mâu thuẫn. 5-6: Ít mâu thuẫn. 7-10: Không mâu thuẫn."}
}

CRITERIA_STEM = {
    "S01": {"name": "Xác định dạng bài/dữ kiện", "weight": 1.5, "rubric": "0-2: Không rõ dạng bài. 7-10: Rõ ràng chi tiết."},
    "S02": {"name": "Yêu cầu tìm gì", "weight": 1.5, "rubric": "0-2: Không rõ cần tìm gì. 7-10: Rõ mục tiêu."},
    "S03": {"name": "Cung cấp đủ số liệu", "weight": 1.5, "rubric": "0-2: Thiếu số liệu. 7-10: Đầy đủ số liệu."},
    "S04": {"name": "Quy định đơn vị đo", "weight": 1.0, "rubric": "0-2: Không có đơn vị. 7-10: Đơn vị chuẩn."},
    "S05": {"name": "Yêu cầu trình bày các bước", "weight": 1.5, "rubric": "0-2: Không yêu cầu. 7-10: Yêu cầu chi tiết."},
    "S06": {"name": "Tránh gây nhiễu thông tin", "weight": 1.0, "rubric": "0-2: Nhiều thông tin nhiễu. 7-10: Không có nhiễu."},
    "S07": {"name": "Yêu cầu định dạng kết quả", "weight": 1.0, "rubric": "0-2: Không rõ định dạng. 7-10: Định dạng rõ."},
    "S08": {"name": "Tính khả thi của dữ kiện", "weight": 1.0, "rubric": "0-2: Dữ kiện vô lý. 7-10: Dữ kiện thực tế."}
}

CRITERIA_TEMPLATE = {
    "T01": {"name": "Đủ mục", "weight": 1.5, "rubric": "0-2: Thiếu nhiều mục. 7-10: Đủ mục."},
    "T02": {"name": "Mục hợp lý", "weight": 1.0, "rubric": "0-2: Mục vô lý. 7-10: Mục hợp lý."},
    "T03": {"name": "Hướng dẫn điền", "weight": 1.5, "rubric": "0-2: Không có hướng dẫn. 7-10: Hướng dẫn rõ."},
    "T04": {"name": "Ví dụ mẫu", "weight": 1.0, "rubric": "0-2: Không có ví dụ. 7-10: Có ví dụ."},
    "T05": {"name": "Phân cấp", "weight": 1.0, "rubric": "0-2: Không phân cấp. 7-10: Phân cấp tốt."},
    "T06": {"name": "Quy tắc cấm", "weight": 1.0, "rubric": "0-2: Không có quy tắc. 7-10: Quy tắc rõ."},
    "T07": {"name": "Quy tắc ưu tiên", "weight": 1.0, "rubric": "0-2: Không có ưu tiên. 7-10: Ưu tiên rõ."},
    "T08": {"name": "Quy trình xử lý", "weight": 1.0, "rubric": "0-2: Không có quy trình. 7-10: Quy trình rõ."},
    "T09": {"name": "Chất lượng placeholder", "weight": 1.0, "rubric": "0-2: Placeholder kém. 7-10: Placeholder tốt."}
}

CRITERIA_PROMPT_META = {
    "M01": {"name": "Cấu trúc", "weight": 1.5, "rubric": "0-2: Không cấu trúc. 7-10: Cấu trúc tốt."},
    "M02": {"name": "Chi tiết", "weight": 2.0, "rubric": "0-2: Quá sơ sài. 7-10: Rất chi tiết."},
    "M03": {"name": "Định dạng", "weight": 1.0, "rubric": "0-2: Không định dạng. 7-10: Định dạng đẹp."},
    "M04": {"name": "Nhất quán", "weight": 1.0, "rubric": "0-2: Mâu thuẫn. 7-10: Nhất quán."},
    "M05": {"name": "Khả thi", "weight": 1.0, "rubric": "0-2: Bất khả thi. 7-10: Khả thi."},
    "M06": {"name": "Vai trò", "weight": 0.5, "rubric": "0-2: Không có vai trò. 7-10: Vai trò tốt."},
    "M07": {"name": "Mở rộng", "weight": 1.0, "rubric": "0-2: Không mở rộng. 7-10: Mở rộng tốt."},
    "M08": {"name": "Ứng dụng", "weight": 1.0, "rubric": "0-2: Không ứng dụng. 7-10: Ứng dụng tốt."},
    "M09": {"name": "Quy trình", "weight": 1.0, "rubric": "0-2: Không quy trình. 7-10: Quy trình tốt."}
}

CRITERIA_TABLE = {
    "TB01": {"name": "Đủ cột và hàng", "weight": 1.5, "rubric": "0-2: Thiếu cột/hàng. 7-10: Đầy đủ."},
    "TB02": {"name": "Header rõ ràng", "weight": 1.0, "rubric": "0-2: Không header. 7-10: Header rõ."},
    "TB03": {"name": "Dữ liệu nhất quán", "weight": 1.5, "rubric": "0-2: Dữ liệu lộn xộn. 7-10: Nhất quán."},
    "TB04": {"name": "Không ô trống bất thường", "weight": 1.0, "rubric": "0-2: Nhiều ô trống. 7-10: Không có."},
    "TB05": {"name": "Ghi chú đơn vị", "weight": 1.0, "rubric": "0-2: Không ghi chú. 7-10: Ghi chú rõ."},
    "TB06": {"name": "Khả năng đọc hiểu", "weight": 1.0, "rubric": "0-2: Khó đọc. 7-10: Dễ đọc."},
    "TB07": {"name": "Tính ứng dụng", "weight": 1.0, "rubric": "0-2: Không thực tế. 7-10: Rất thực tế."},
    "TB08": {"name": "Khả năng mở rộng", "weight": 1.0, "rubric": "0-2: Khó mở rộng. 7-10: Dễ mở rộng."},
    "TB09": {"name": "Mức độ chi tiết", "weight": 1.0, "rubric": "0-2: Quá sơ sài. 7-10: Rất chi tiết."}
}

CRITERIA_ROLE_PLAY = {
    "R01": {"name": "Sự phù hợp của vai trò", "weight": 1.5, "rubric": "0-2: Vai trò không liên quan. 3-4: Vai trò chung chung. 5-6: Vai trò phù hợp với nhiệm vụ. 7-10: Vai trò được chọn lọc, tối ưu cho nhiệm vụ."},
    "R02": {"name": "Mục tiêu hội thoại", "weight": 1.2, "rubric": "0-2: Không có mục tiêu. 3-4: Mục tiêu mơ hồ. 5-6: Mục tiêu rõ ràng. 7-10: Mục tiêu cụ thể, có thể đo lường được."},
    "R03": {"name": "Giới hạn hành vi", "weight": 0.8, "rubric": "0-2: Không có ràng buộc. 3-4: Ràng buộc chung. 5-6: Ràng buộc rõ ràng. 7-10: Ràng buộc chi tiết (được làm gì, không được làm gì)."}
}

CRITERIA_FEW_SHOT = {
    "F01": {"name": "Tính liên quan của ví dụ", "weight": 1.5, "rubric": "0-2: Ví dụ không liên quan. 3-4: Ví dụ xa rời thực tế. 5-6: Ví dụ sát với yêu cầu. 7-10: Ví dụ hoàn hảo, trực tiếp giải quyết vấn đề."},
    "F02": {"name": "Độ bao quát của ví dụ", "weight": 1.2, "rubric": "0-2: Chỉ có 1 ví dụ đơn giản. 3-4: 1-2 ví dụ, chưa bao quát. 5-6: 2-3 ví dụ bao quát các trường hợp phổ biến. 7-10: Ví dụ bao quát cả các trường hợp ngoại lệ/khó."},
    "F03": {"name": "Cấu trúc Input-Output", "weight": 0.8, "rubric": "0-2: Không có cấu trúc. 3-4: Cấu trúc lỏng lẻo. 5-6: Cấu trúc rõ ràng, dễ hiểu. 7-10: Cấu trúc chuẩn hóa (delimiter rõ ràng, phân tách mạch lạc)."}
}

CRITERIA_COT = {
    "C01": {"name": "Yêu cầu giải quyết có cấu trúc", "weight": 1.5, "rubric": "0-2: Không yêu cầu. 3-4: Yêu cầu chung chung. 5-6: Yêu cầu chia nhỏ vấn đề. 7-10: Yêu cầu quy trình giải quyết từng bước rõ ràng, có thể theo dõi."},
    "C02": {"name": "Khả năng kiểm tra lập luận", "weight": 1.2, "rubric": "0-2: Không có. 3-4: Yêu cầu kiểm tra sơ sài. 5-6: Yêu cầu giải thích lý do. 7-10: Yêu cầu phép tính/lập luận phải được chứng minh và có bước kiểm tra chéo."},
    "C03": {"name": "Kết luận rõ ràng", "weight": 0.8, "rubric": "0-2: Không yêu cầu. 3-4: Kết luận mơ hồ. 5-6: Yêu cầu đưa ra đáp án cuối cùng. 7-10: Yêu cầu tách biệt rõ ràng giữa quá trình suy luận và kết quả cuối cùng."}
}

CRITERIA_FORMATTED_OUTPUT = {
    "FO01": {"name": "Schema và kiểu dữ liệu", "weight": 1.5, "rubric": "0-2: Không xác định định dạng. 3-4: Xác định chung (VD: JSON). 5-6: Xác định cấu trúc cơ bản. 7-10: Cung cấp schema chi tiết, quy định rõ kiểu dữ liệu (string, int, array...)."},
    "FO02": {"name": "Trường bắt buộc", "weight": 1.0, "rubric": "0-2: Không có. 3-4: Có đề cập. 5-6: Liệt kê các trường. 7-10: Chỉ định rõ trường nào là bắt buộc, trường nào là tùy chọn."},
    "FO03": {"name": "Quy tắc xử lý lỗi", "weight": 1.0, "rubric": "0-2: Không có. 3-4: Có đề cập. 5-6: Hướng dẫn chung. 7-10: Quy định rõ cách xử lý nếu AI không thể tạo ra định dạng đó (VD: trả về lỗi null)."}
}

CRITERIA_CREATIVE = {
    "CG01": {"name": "Mục tiêu sáng tạo", "weight": 1.5, "rubric": "0-2: Không có mục tiêu. 3-4: Mục tiêu mơ hồ. 5-6: Mục tiêu rõ ràng. 7-10: Mục tiêu được định nghĩa sắc nét, có thể đo lường (VD: viết truyện cười, viết kịch bản 3 hồi)."},
    "CG02": {"name": "Đối tượng độc giả", "weight": 1.2, "rubric": "0-2: Không có. 3-4: Đối tượng chung. 5-6: Đối tượng cụ thể. 7-10: Đối tượng chi tiết (độ tuổi, sở thích, trình độ)."},
    "CG03": {"name": "Phong cách và ràng buộc", "weight": 0.8, "rubric": "0-2: Không có ràng buộc. 3-4: Ràng buộc lỏng lẻo. 5-6: Chỉ định phong cách (VD: hài hước). 7-10: Chỉ định rõ phong cách, tông giọng và các ràng buộc (số từ, vần điệu)."}
}

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
    main_task = classification.get("main_task", TYPE_GENERAL)
    techniques = classification.get("techniques", [])
    
    mapping = {
        TYPE_PROMPT: CRITERIA_PROMPT, 
        TYPE_TEMPLATE: CRITERIA_TEMPLATE,
        TYPE_PROMPT_META: CRITERIA_PROMPT_META, 
        TYPE_TABLE: CRITERIA_TABLE,
        TYPE_STEM: CRITERIA_STEM, 
        TYPE_IMAGE: CRITERIA_PROMPT, 
        TYPE_EMPTY: {},
        TYPE_GENERAL: CRITERIA_GENERAL # <-- Fallback cho lĩnh vực mới
    }
    main_criteria = mapping.get(main_task, CRITERIA_GENERAL).copy()

    tech_criteria = {}
    if TECH_ROLE_PLAY in techniques: tech_criteria.update(CRITERIA_ROLE_PLAY)
    if TECH_FEW_SHOT in techniques: tech_criteria.update(CRITERIA_FEW_SHOT)
    if TECH_COT in techniques: tech_criteria.update(CRITERIA_COT)
    if TECH_FORMAT in techniques: tech_criteria.update(CRITERIA_FORMATTED_OUTPUT)
    if TECH_CREATIVE in techniques: tech_criteria.update(CRITERIA_CREATIVE)

    validate_config(main_criteria, tech_criteria)
    return {"main": main_criteria, "tech": tech_criteria}

def classify_prompt(prompt_text: str) -> dict:
    text = prompt_text.strip()
    if not text: return {"main_task": TYPE_EMPTY, "techniques": []}
    
    lower_text = text.lower()
    techniques = []
    
    if any(kw in lower_text for kw in ["đóng vai", "bạn là", "hãy vào vai", "giả sử bạn là", "act as"]):
        techniques.append(TECH_ROLE_PLAY)
    if any(kw in lower_text for kw in ["ví dụ 1:", "ví dụ mẫu", "input:", "output:", "dưới đây là ví dụ", "ví dụ như sau"]):
        techniques.append(TECH_FEW_SHOT)
    if any(kw in lower_text for kw in ["từng bước", "suy luận", "giải thích từng bước", "chain of thought", "các bước sau", "quy trình"]):
        techniques.append(TECH_COT)
    if any(kw in lower_text for kw in ["json", "xml", "định dạng bảng", "markdown", "trả về dạng", "cấu trúc dữ liệu"]):
        techniques.append(TECH_FORMAT)
    if any(kw in lower_text for kw in ["viết truyện", "làm thơ", "sáng tác", "kịch bản", "viết quảng cáo", "brainstorm", "viết content"]):
        techniques.append(TECH_CREATIVE)

    if any(kw in lower_text for kw in ["[điền", "[thay", "[chọn", "___", "{}"]):
        return {"main_task": TYPE_TEMPLATE, "techniques": techniques}
    if text.count('[') >= 3 and text.count(']') >= 3:
        return {"main_task": TYPE_TEMPLATE, "techniques": techniques}

    stem_keywords = ["giải toán", "phương trình", "đạo hàm", "tích phân", "vật lý", "hóa học", "phản ứng", "tính vận tốc", "gia tốc", "nguyên tử"]
    if any(kw in lower_text for kw in stem_keywords): 
        return {"main_task": TYPE_STEM, "techniques": techniques}
    
    if any(kw in lower_text for kw in ["http", "jpg", "png", "vẽ ảnh", "tạo ảnh", "hình ảnh"]): 
        return {"main_task": TYPE_IMAGE, "techniques": techniques}
    
    if any(kw in lower_text for kw in ["tạo bảng", "lập bảng", "dạng bảng", "cột", "hàng"]): 
        return {"main_task": TYPE_TABLE, "techniques": techniques}
    
    if any(kw in lower_text for kw in ["đánh giá prompt", "viết prompt", "sửa prompt", "chấm điểm prompt", "tạo prompt"]): 
        return {"main_task": TYPE_PROMPT_META, "techniques": techniques}
    
    # Nếu không khớp bất kỳ loại cụ thể nào -> Trả về GENERAL
    return {"main_task": TYPE_GENERAL, "techniques": techniques}
