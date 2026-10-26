# error_rules.py
# Danh mục quy tắc phát hiện lỗi Prompt.
# Lưu ý: 
# - require_quote: True (Phải trích nguyên văn từ prompt gốc), False (Chỉ cần mô tả thiếu hụt).
# - severity: Chỉ mang tính chất metadata, KHÔNG dùng để trừ điểm tự động.

ERROR_RULES = {
    # ==========================================
    # NHÓM A: LỖI HÌNH THỨC (SYNTAX)
    # ==========================================
    "A01": {
        "name": "Lỗi chính tả",
        "require_quote": True,
        "description": "Sai chính tả hoặc viết hoa sai quy định gây khó hiểu.",
        "conditions": "Prompt chứa từ viết sai chính tả rõ ràng, làm ảnh hưởng đến nghĩa của câu.",
        "exclusions": "Teencode, viết tắt phổ thông, hoặc lỗi cố ý nhưng ngữ cảnh vẫn hiểu được rõ ràng.",
        "severity": "Thấp",
        "fix_hint": "Sửa lại các từ viết sai chính tả hoặc viết hoa đúng chuẩn tiếng Việt."
    },
    "A02": {
        "name": "Thiếu dấu câu",
        "require_quote": True,
        "description": "Thiếu dấu chấm, phẩy gây hiểu lầm hoặc khó đọc.",
        "conditions": "Prompt dài (trên 2 câu) nhưng không có dấu câu ngăn cách các ý.",
        "exclusions": "Prompt quá ngắn (dưới 10 từ) không cần dấu câu phức tạp.",
        "severity": "Thấp",
        "fix_hint": "Thêm dấu chấm, phẩy hoặc các dấu phân cách để tách biệt các ý."
    },
    "A03": {
        "name": "Lặp từ",
        "require_quote": True,
        "description": "Lặp lại cùng một từ hoặc cụm từ quá nhiều lần trong một câu.",
        "conditions": "Một từ hoặc cụm từ xuất hiện lặp đi lặp lại gây nhàm chán.",
        "exclusions": "Lặp từ có chủ đích để nhấn mạnh (VD: 'rất rất quan trọng').",
        "severity": "Thấp",
        "fix_hint": "Sử dụng từ đồng nghĩa hoặc lược bỏ các từ lặp không cần thiết."
    },

    # ==========================================
    # NHÓM B: LỖI CẤU TRÚC (STRUCTURE)
    # ==========================================
    "B01": {
        "name": "Thiếu thành phần cấu trúc cốt lõi",
        "require_quote": False, # Lỗi thiếu thông tin -> Không cần trích dẫn
        "description": "Thiếu Vai trò, Mục tiêu hoặc các thành phần cơ bản khiến AI không hiểu phải làm gì.",
        "conditions": "Prompt không xác định được mục tiêu hành động (động từ) hoặc vai trò tối thiểu.",
        "exclusions": "Prompt rất ngắn nhưng mục tiêu vẫn rõ ràng (VD: 'Viết thơ về mùa thu').",
        "severity": "Cao",
        "fix_hint": "Bổ sung vai trò (VD: 'Bạn là...') và mục tiêu cụ thể để AI hiểu rõ nhiệm vụ."
    },
    "B02": {
        "name": "Các mục không logic",
        "require_quote": True,
        "description": "Các phần trong prompt bị chắp vá, không theo một trình tự hợp lý.",
        "conditions": "Prompt nhảy từ ý này sang ý khác thiếu sự liên kết.",
        "exclusions": "Prompt dạng liệt kê (bullet points) có chủ đích.",
        "severity": "Trung bình",
        "fix_hint": "Tổ chức lại thông tin theo thứ tự: Bối cảnh -> Mục tiêu -> Yêu cầu -> Định dạng."
    },
    "B03": {
        "name": "Sai phân cấp",
        "require_quote": True,
        "description": "Đánh số thứ tự hoặc phân cấp thông tin lộn xộn.",
        "conditions": "Prompt sử dụng các ký hiệu (1, 2, a, b) nhưng không đúng cấu trúc.",
        "exclusions": "Prompt không sử dụng phân cấp.",
        "severity": "Thấp",
        "fix_hint": "Đánh số lại thứ tự hoặc sử dụng cấu trúc Markdown để phân cấp rõ ràng."
    },
    "B04": {
        "name": "Chưa quy định định dạng đầu ra",
        "require_quote": False, # Lỗi thiếu thông tin -> Không cần trích dẫn
        "description": "Không yêu cầu rõ AI trả lời dạng gì (bảng, JSON, đoạn văn).",
        "conditions": "Nhiệm vụ yêu cầu độ chính xác cao về cấu trúc hoặc cần xuất dữ liệu.",
        "exclusions": "Nhiệm vụ sáng tạo văn bản tự do (viết thơ, kể chuyện).",
        "severity": "Trung bình",
        "fix_hint": "Thêm yêu cầu định dạng đầu ra (VD: 'Trả về dạng bảng', 'Xuất JSON', 'Viết thành đoạn văn')."
    },

    # ==========================================
    # NHÓM C: LỖI NGỮ CẢNH & ĐỘ RÕ RÀNG
    # ==========================================
    "C01": {
        "name": "Đối tượng tác động chưa rõ",
        "require_quote": False, # Lỗi thiếu thông tin -> Không cần trích dẫn
        "description": "Không xác định rõ AI cần xử lý cái gì (văn bản, bài toán, dữ liệu).",
        "conditions": "Có động từ hành động nhưng thiếu tân ngữ (VD: 'Hãy tóm tắt' - Tóm tắt cái gì?).",
        "exclusions": "Prompt đã có ngữ cảnh ngầm hiểu rõ ràng.",
        "severity": "Cao",
        "fix_hint": "Nêu rõ đối tượng cần xử lý (VD: 'Tóm tắt đoạn văn sau...', 'Giải phương trình...')."
    },
    "C02": {
        "name": "Thiếu bối cảnh",
        "require_quote": False, # Lỗi thiếu thông tin -> Không cần trích dẫn
        "description": "Không nêu rõ mục đích, hoàn cảnh, đối tượng độc giả.",
        "conditions": "Prompt thiếu thông tin về người đọc, tình huống sử dụng khiến kết quả có thể lệch hướng.",
        "exclusions": "Các nhiệm vụ logic thuần túy (VD: 'Giải phương trình 2x=4').",
        "severity": "Trung bình",
        "fix_hint": "Cung cấp thêm bối cảnh (VD: 'Dành cho học sinh cấp 2', 'Dùng trong email công việc')."
    },
    "C03": {
        "name": "Yêu cầu chung chung, mơ hồ",
        "require_quote": True,
        "description": "Dùng các từ như 'hay hơn', 'tốt hơn', 'chuyên nghiệp hơn' mà không có tiêu chí.",
        "conditions": "Có chứa các tính từ đánh giá chủ quan mà không định lượng.",
        "exclusions": "Từ ngữ chuyên ngành đã mang nghĩa xác định (VD: 'viết theo phong cách báo chí').",
        "severity": "Trung bình",
        "fix_hint": "Thay thế bằng các tiêu chí cụ thể (VD: 'Giọng văn trang trọng, độ dài 200 từ')."
    },
    "C04": {
        "name": "Thiếu ví dụ mẫu (Few-shot)",
        "require_quote": False, # Lỗi thiếu thông tin -> Không cần trích dẫn
        "description": "Cần ví dụ để AI bắt chước nhưng prompt không cung cấp.",
        "conditions": "Nhiệm vụ yêu cầu định dạng đặc thù, giọng điệu riêng hoặc cấu trúc phức tạp.",
        "exclusions": "Nhiệm vụ đơn giản hoặc đã được quy định rõ ràng bằng văn bản.",
        "severity": "Trung bình",
        "fix_hint": "Thêm 1-2 ví dụ mẫu (Input - Output) để AI hiểu rõ định dạng bạn mong muốn."
    },

    # ==========================================
    # NHÓM D: LỖI LOGIC & KHẢ THI
    # ==========================================
    "D01": {
        "name": "Mâu thuẫn nội bộ",
        "require_quote": True,
        "description": "Yêu cầu 'ngắn gọn' nhưng lại 'chi tiết', hoặc vừa 'vui vẻ' vừa 'nghiêm túc'.",
        "conditions": "Có 2 mệnh đề loại trừ lẫn nhau trong cùng một prompt.",
        "exclusions": "Mâu thuẫn ngữ nghĩa tinh tế mang tính nghệ thuật (VD: 'buồn nhưng hy vọng').",
        "severity": "Cao",
        "fix_hint": "Loại bỏ một trong hai yêu cầu mâu thuẫn hoặc làm rõ ngữ cảnh áp dụng của từng yêu cầu."
    },
    "D02": {
        "name": "Yêu cầu bất khả thi",
        "require_quote": True,
        "description": "Yêu cầu AI làm việc vượt quá khả năng (VD: đọc file chưa cung cấp, dự đoán tương lai).",
        "conditions": "Yêu cầu truy xuất thông tin thời gian thực hoặc dữ liệu ngoại vi không có sẵn.",
        "exclusions": "Yêu cầu mang tính sáng tạo/giả định (VD: 'Hãy tưởng tượng bạn là...').",
        "severity": "Cao",
        "fix_hint": "Cung cấp dữ liệu cần thiết hoặc thay đổi yêu cầu cho phù hợp với khả năng của AI."
    },
    "D03": {
        "name": "Vai trò không phù hợp",
        "require_quote": True,
        "description": "Gán vai trò không liên quan đến nhiệm vụ.",
        "conditions": "Vai trò được yêu cầu không có kỹ năng để thực hiện nhiệm vụ đi kèm.",
        "exclusions": "Vai trò đa năng có thể đảm nhận được nhiều nhiệm vụ.",
        "severity": "Trung bình",
        "fix_hint": "Thay đổi vai trò phù hợp hơn với chuyên môn cần thiết cho nhiệm vụ."
    },

    # ==========================================
    # NHÓM E: LỖI LĨNH VỰC
    # ==========================================
    "E01": {
        "name": "Trộn lẫn nhiều lĩnh vực không liên quan",
        "require_quote": True,
        "description": "Vừa yêu cầu giải toán vừa yêu cầu viết thơ trong cùng một câu lệnh thiếu liên kết.",
        "conditions": "Các mục tiêu không có mối quan hệ nhân quả hoặc bổ trợ.",
        "exclusions": "Đa nhiệm có chủ đích (VD: 'Viết code và giải thích code').",
        "severity": "Trung bình",
        "fix_hint": "Tách thành các prompt riêng biệt hoặc làm rõ mối liên kết giữa các nhiệm vụ."
    },
    "E02": {
        "name": "Thuật ngữ không nhất quán",
        "require_quote": True,
        "description": "Dùng nhiều từ đồng nghĩa cho cùng một khái niệm gây rối AI.",
        "conditions": "Cùng một đối tượng được gọi bằng 2-3 tên khác nhau.",
        "exclusions": "Sử dụng từ đồng nghĩa có chủ đích để làm phong phú ngôn ngữ.",
        "severity": "Trung bình",
        "fix_hint": "Thống nhất sử dụng một thuật ngữ duy nhất cho mỗi khái niệm."
    },
    "E03": {
        "name": "Thiếu tính đặc thù lĩnh vực (khi cần thiết)",
        "require_quote": True,
        "description": "Prompt quá chung chung, không dùng thuật ngữ chuyên ngành khi nhiệm vụ đòi hỏi.",
        "conditions": "Nhiệm vụ mang tính chuyên môn cao nhưng dùng từ ngữ đời thường.",
        "exclusions": "Nhiệm vụ phổ thông hoặc đang giải thích cho người mới.",
        "severity": "Thấp",
        "fix_hint": "Sử dụng các thuật ngữ chuyên ngành phù hợp để AI hiểu chính xác yêu cầu."
    }
}