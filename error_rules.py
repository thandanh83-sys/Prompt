ERROR_RULES = {
    "A01": {"name": "Lỗi chính tả", "require_quote": True, "description": "Sai chính tả, viết hoa sai quy định.", "conditions": "Prompt chứa từ viết sai chính tả rõ ràng.", "exclusions": "Teencode, viết tắt phổ thông."},
    "A02": {"name": "Thiếu dấu câu", "require_quote": True, "description": "Thiếu dấu chấm, phẩy.", "conditions": "Prompt dài trên 2 câu nhưng không có dấu câu.", "exclusions": "Prompt quá ngắn dưới 10 từ."},
    "A03": {"name": "Lặp từ", "require_quote": True, "description": "Lặp lại cùng một từ quá nhiều.", "conditions": "Từ hoặc cụm từ lặp đi lặp lại.", "exclusions": "Lặp từ có chủ đích."},
    
    "B01": {"name": "Thiếu thành phần cấu trúc cốt lõi", "require_quote": False, "description": "Thiếu Vai trò, Mục tiêu.", "conditions": "Prompt không xác định được mục tiêu hành động.", "exclusions": "Prompt rất ngắn nhưng mục tiêu rõ ràng."},
    "B02": {"name": "Các mục không logic", "require_quote": True, "description": "Chắp vá, không trình tự.", "conditions": "Prompt nhảy từ ý này sang ý khác.", "exclusions": "Prompt dạng liệt kê có chủ đích."},
    "B03": {"name": "Sai phân cấp", "require_quote": True, "description": "Đánh số lộn xộn.", "conditions": "Sử dụng ký hiệu 1,2,a,b không đúng cấu trúc.", "exclusions": "Không sử dụng phân cấp."},
    "B04": {"name": "Chưa quy định định dạng đầu ra", "require_quote": False, "description": "Không yêu cầu rõ AI trả lời dạng gì.", "conditions": "Nhiệm vụ yêu cầu độ chính xác cao về cấu trúc.", "exclusions": "Nhiệm vụ sáng tạo văn bản tự do."},

    "C01": {"name": "Đối tượng tác động chưa rõ", "require_quote": False, "description": "Không rõ AI xử lý cái gì.", "conditions": "Có động từ hành động nhưng thiếu tân ngữ.", "exclusions": "Prompt đã có ngữ cảnh ngầm hiểu."},
    "C02": {"name": "Thiếu bối cảnh", "require_quote": False, "description": "Không nêu rõ mục đích, đối tượng độc giả.", "conditions": "Thiếu thông tin người đọc, tình huống sử dụng.", "exclusions": "Nhiệm vụ logic thuần túy."},
    "C03": {"name": "Yêu cầu chung chung, mơ hồ", "require_quote": True, "description": "Dùng từ 'hay hơn', 'tốt hơn' mà không có tiêu chí.", "conditions": "Chứa tính từ đánh giá chủ quan không định lượng.", "exclusions": "Từ ngữ chuyên ngành mang nghĩa xác định."},
    "C04": {"name": "Thiếu ví dụ mẫu (Few-shot)", "require_quote": False, "description": "Cần ví dụ bắt chước nhưng không cung cấp.", "conditions": "Nhiệm vụ yêu cầu định dạng đặc thù, giọng điệu riêng.", "exclusions": "Nhiệm vụ đơn giản đã quy định rõ bằng văn bản."},

    "D01": {"name": "Mâu thuẫn nội bộ", "require_quote": True, "description": "Yêu cầu trái ngược nhau.", "conditions": "Có 2 mệnh đề loại trừ lẫn nhau.", "exclusions": "Mâu thuẫn ngữ nghĩa tinh tế (nghệ thuật)."},
    "D02": {"name": "Yêu cầu bất khả thi", "require_quote": True, "description": "Vượt quá khả năng AI.", "conditions": "Yêu cầu truy xuất thông tin thời gian thực.", "exclusions": "Yêu cầu mang tính sáng tạo/giả định."},
    "D03": {"name": "Vai trò không phù hợp", "require_quote": True, "description": "Gán vai trò không liên quan.", "conditions": "Vai trò không có kỹ năng thực hiện nhiệm vụ.", "exclusions": "Vai trò đa năng có thể đảm nhận."},

    "E01": {"name": "Trộn lẫn nhiều lĩnh vực", "require_quote": True, "description": "Vừa toán vừa văn.", "conditions": "Các mục tiêu không có mối quan hệ.", "exclusions": "Đa nhiệm có chủ đích."},
    "E02": {"name": "Thuật ngữ không nhất quán", "require_quote": True, "description": "Dùng nhiều từ đồng nghĩa cho 1 khái niệm.", "conditions": "Cùng 1 đối tượng gọi bằng 2-3 tên khác nhau.", "exclusions": "Sử dụng từ đồng nghĩa có chủ đích."},
    "E03": {"name": "Thiếu tính đặc thù lĩnh vực", "require_quote": True, "description": "Quá chung chung, thiếu thuật ngữ chuyên ngành.", "conditions": "Nhiệm vụ chuyên môn cao nhưng dùng từ đời thường.", "exclusions": "Nhiệm vụ phổ thông hoặc giải thích cho người mới."}
}