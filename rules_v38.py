import hashlib
import json

TYPE_PROMPT = "PROMPT"
TYPE_TEMPLATE = "TEMPLATE"
TYPE_PROMPT_META = "PROMPT META"
TYPE_TABLE = "TABLE"
TYPE_EMPTY = "EMPTY"
TYPE_IMAGE = "IMAGE"

VALID_ERROR_CODES = {
    "A01": "Lỗi chính tả", "A02": "Thiếu dấu câu", "A03": "Lặp lại",
    "B01": "Thiếu thành phần cấu trúc", "B02": "Mục không logic", "B03": "Sai phân cấp", "B04": "Chưa quy định định dạng đầu ra",
    "C01": "Đối tượng chưa rõ", "C02": "Thiếu bối cảnh", "C03": "Yêu cầu chung chung", "C04": "Thiếu ví dụ",
    "D01": "Mâu thuẫn nội bộ", "D02": "Yêu cầu bất khả thi", "D03": "Vai trò không phù hợp",
    "E01": "Trộn lĩnh vực", "E02": "Thuật ngữ không nhất quán", "E03": "Thiếu tính đặc thù lĩnh vực"
}

CRITERIA_PROMPT = {
    "P01": {"name": "Độ rõ nhiệm vụ", "weight": 1.2}, "P02": {"name": "Đối tượng tác động", "weight": 1.2},
    "P03": {"name": "Bối cảnh", "weight": 0.8}, "P04": {"name": "Định dạng đầu ra", "weight": 0.8},
    "P05": {"name": "Độ chi tiết và ví dụ", "weight": 1.6}, "P06": {"name": "Không mơ hồ", "weight": 0.2},
    "P07": {"name": "Không chung chung", "weight": 0.2}, "P08": {"name": "Có cấu trúc", "weight": 0.2},
    "P09": {"name": "Phù hợp nhiệm vụ", "weight": 0.5}, "P10": {"name": "Chuyên môn có căn cứ", "weight": 0.5},
    "P11": {"name": "Nhất quán lĩnh vực", "weight": 1.0}, "P12": {"name": "Yêu cầu khả thi", "weight": 0.8},
    "P13": {"name": "Vai trò phù hợp", "weight": 0.8}, "P14": {"name": "Không mâu thuẫn", "weight": 0.2}
}

CRITERIA_TEMPLATE = {
    "T01": {"name": "Đủ mục", "weight": 1.5}, "T02": {"name": "Mục hợp lý", "weight": 1.0},
    "T03": {"name": "Hướng dẫn điền", "weight": 1.5}, "T04": {"name": "Ví dụ mẫu", "weight": 1.0},
    "T05": {"name": "Phân cấp", "weight": 1.0}, "T06": {"name": "Quy tắc cấm", "weight": 1.0},
    "T07": {"name": "Quy tắc ưu tiên", "weight": 1.0}, "T08": {"name": "Quy trình xử lý", "weight": 1.0},
    "T09": {"name": "Chất lượng placeholder", "weight": 1.0}
}

CRITERIA_PROMPT_META = {
    "M01": {"name": "Cấu trúc", "weight": 1.5}, "M02": {"name": "Chi tiết", "weight": 2.0},
    "M03": {"name": "Định dạng", "weight": 1.0}, "M04": {"name": "Nhất quán", "weight": 1.0},
    "M05": {"name": "Khả thi", "weight": 1.0}, "M06": {"name": "Vai trò", "weight": 0.5},
    "M07": {"name": "Mở rộng", "weight": 1.0}, "M08": {"name": "Ứng dụng", "weight": 1.0},
    "M09": {"name": "Quy trình", "weight": 1.0}
}

CRITERIA_TABLE = {
    "TB01": {"name": "Đủ cột và hàng", "weight": 1.5}, "TB02": {"name": "Header rõ ràng", "weight": 1.0},
    "TB03": {"name": "Dữ liệu nhất quán định dạng", "weight": 1.5}, "TB04": {"name": "Không có ô trống bất thường", "weight": 1.0},
    "TB05": {"name": "Có ghi chú đơn vị nếu cần", "weight": 1.0}, "TB06": {"name": "Khả năng đọc hiểu", "weight": 1.0},
    "TB07": {"name": "Tính ứng dụng thực tế", "weight": 1.0}, "TB08": {"name": "Khả năng mở rộng phù hợp", "weight": 1.0},
    "TB09": {"name": "Mức độ chi tiết dữ liệu", "weight": 1.0}
}

REQUIRED_REWRITE_SECTIONS = [
    "1. VAI TRÒ", "2. BỐI CẢNH", "3. INPUT", "4. MỤC TIÊU", "5. YÊU CẦU", 
    "6. RÀNG BUỘC", "7. TASK", "8. ĐỊNH DẠNG ĐẦU RA", "9. NEVER DO", 
    "10. THỨ TỰ ƯU TIÊN", "11. XỬ LÝ NỘI BỘ"
]

def get_criteria_by_type(content_type):
    mapping = {
        TYPE_PROMPT: CRITERIA_PROMPT,
        TYPE_TEMPLATE: CRITERIA_TEMPLATE,
        TYPE_PROMPT_META: CRITERIA_PROMPT_META,
        TYPE_TABLE: CRITERIA_TABLE
    }
    return mapping.get(content_type, None)

def classify_prompt(prompt_text: str) -> str:
    text = prompt_text.strip()
    if not text: return TYPE_EMPTY
    lower_text = text.lower()
    if any(kw in lower_text for kw in ["http", "jpg", "png", "vẽ ảnh", "tạo ảnh", "hình ảnh"]): return TYPE_IMAGE
    if any(kw in lower_text for kw in ["tạo bảng", "lập bảng", "dạng bảng", "cột", "hàng"]): return TYPE_TABLE
    if any(kw in lower_text for kw in ["đánh giá prompt", "viết prompt", "sửa prompt", "chấm điểm prompt", "tạo prompt"]): return TYPE_PROMPT_META
    if any(kw in lower_text for kw in ["[điền", "[thay", "[chọn", "___", "{}"]): return TYPE_TEMPLATE
    return TYPE_PROMPT

def generate_rules_hash():
    rules_snapshot = {
        "error_codes": VALID_ERROR_CODES, "criteria_prompt": CRITERIA_PROMPT,
        "criteria_template": CRITERIA_TEMPLATE, "criteria_meta": CRITERIA_PROMPT_META,
        "criteria_table": CRITERIA_TABLE, "rewrite_sections": REQUIRED_REWRITE_SECTIONS
    }
    json_str = json.dumps(rules_snapshot, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

def verify_rules_integrity():
    for name, crit in [("PROMPT", CRITERIA_PROMPT), ("TEMPLATE", CRITERIA_TEMPLATE), 
                       ("PROMPT_META", CRITERIA_PROMPT_META), ("TABLE", CRITERIA_TABLE)]:
        total = sum(item["weight"] for item in crit.values())
        if abs(total - 10.0) > 0.001:
            raise RuntimeError(f"Lỗi toàn vẹn: Tổng trọng số {name} khác 10.0")
    return True