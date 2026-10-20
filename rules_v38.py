import hashlib
import json

TYPE_PROMPT = "PROMPT"
TYPE_TEMPLATE = "TEMPLATE"
TYPE_PROMPT_META = "PROMPT META"
TYPE_TABLE = "TABLE"
TYPE_STEM = "STEM"
TYPE_EMPTY = "EMPTY"
TYPE_IMAGE = "IMAGE"

VALID_ERROR_CODES = {
    "A01": "Lỗi chính tả", "A02": "Thiếu dấu câu", "A03": "Lặp lại",
    "B01": "Thiếu thành phần cấu trúc", "B02": "Mục không logic", "B03": "Sai phân cấp", "B04": "Chưa quy định định dạng đầu ra",
    "C01": "Đối tượng chưa rõ", "C02": "Thiếu bối cảnh", "C03": "Yêu cầu chung chung", "C04": "Thiếu ví dụ",
    "D01": "Mâu thuẫn nội bộ", "D02": "Yêu cầu bất khả thi", "D03": "Vai trò không phù hợp",
    "E01": "Trộn lĩnh vực", "E02": "Thuật ngữ không nhất quán", "E03": "Thiếu tính đặc thù lĩnh vực"
}

# [CẬP NHẬT]: Thêm Rubric chi tiết cho từng tiêu chí
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

REQUIRED_REWRITE_SECTIONS = [
    "1. VAI TRÒ", "2. BỐI CẢNH", "3. INPUT", "4. MỤC TIÊU", "5. YÊU CẦU", 
    "6. RÀNG BUỘC", "7. TASK", "8. ĐỊNH DẠNG ĐẦU RA", "9. NEVER DO", 
    "10. THỨ TỰ ƯU TIÊN", "11. XỬ LÝ NỘI BỘ"
]

def get_criteria_by_type(content_type):
    mapping = {
        TYPE_PROMPT: CRITERIA_PROMPT, TYPE_TEMPLATE: CRITERIA_TEMPLATE,
        TYPE_PROMPT_META: CRITERIA_PROMPT_META, TYPE_TABLE: CRITERIA_TABLE,
        TYPE_STEM: CRITERIA_STEM
    }
    return mapping.get(content_type, None)

def classify_prompt(prompt_text: str) -> str:
    text = prompt_text.strip()
    if not text: return TYPE_EMPTY
    lower_text = text.lower()
    stem_keywords = ["giải toán", "phương trình", "đạo hàm", "tích phân", "vật lý", "hóa học", "phản ứng", "tính vận tốc", "gia tốc", "nguyên tử"]
    if any(kw in lower_text for kw in stem_keywords): return TYPE_STEM
    if any(kw in lower_text for kw in ["http", "jpg", "png", "vẽ ảnh", "tạo ảnh", "hình ảnh"]): return TYPE_IMAGE
    if any(kw in lower_text for kw in ["[điền", "[thay", "[chọn", "___", "{}"]): return TYPE_TEMPLATE
    if any(kw in lower_text for kw in ["tạo bảng", "lập bảng", "dạng bảng", "cột", "hàng"]): return TYPE_TABLE
    if any(kw in lower_text for kw in ["đánh giá prompt", "viết prompt", "sửa prompt", "chấm điểm prompt", "tạo prompt"]): return TYPE_PROMPT_META
    return TYPE_PROMPT
