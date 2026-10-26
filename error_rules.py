# error_rules.py

ERROR_RULES = {
    # ==========================================
    # NHÓM A: LỖI HÌNH THỨC (SYNTAX)
    # ==========================================
    "A01": {
        "name": "Lỗi chính tả",
        "description": "Sai chính tả hoặc viết hoa sai quy định gây khó hiểu.",
        "conditions": "Prompt chứa từ viết sai chính tả rõ ràng.",
        "exclusions": "Lỗi cố ý (teencode, viết tắt phổ thông) nhưng vẫn hiểu được.",
        "evidence_req": "Trích nguyên văn từ viết sai.",
        "severity": "Thấp"
    },
    "A02": {
        "name": "Thiếu dấu câu",
        "description": "Thiếu dấu chấm, phẩy gây hiểu lầm hoặc khó đọc.",
        "conditions": "Prompt dài nhưng không có dấu câu ngăn cách các ý.",
        "exclusions": "Prompt quá ngắn (dưới 10 từ) không cần dấu câu phức tạp.",
        "evidence_req": "Trích nguyên văn đoạn thiếu dấu câu.",
        "severity": "Thấp"
    },

    # ==========================================
    # NHÓM B: LỖI CẤU TRÚC (STRUCTURE)
    # ==========================================
    "B01": {
        "name": "Thiếu thành phần cấu trúc cốt lõi",
        "description": "Thiếu Vai trò, Mục tiêu hoặc các thành phần cơ bản khiến AI không hiểu phải làm gì.",
        "conditions": "Prompt không xác định được mục tiêu hành động (động từ) hoặc vai trò tối thiểu.",
        "exclusions": "Prompt ngắn nhưng mục tiêu rõ ràng (VD: 'Viết thơ về mùa thu').",
        "evidence_req": "Ghi rõ: 'Chưa xác định mục tiêu/vai trò' (Không trích dẫn).",
        "severity": "Cao"
    },
    "B04": {
        "name": "Chưa quy định định dạng đầu ra",
        "description": "Không yêu cầu rõ AI trả lời dạng gì (bảng, JSON, đoạn văn).",
        "conditions": "Nhiệm vụ yêu cầu độ chính xác cao về cấu trúc (VD: xuất dữ liệu, lập trình).",
        "exclusions": "Nhiệm vụ sáng tạo văn bản tự do (viết thơ, kể chuyện).",
        "evidence_req": "Ghi rõ: 'Chưa quy định định dạng đầu ra' (Không trích dẫn).",
        "severity": "Trung bình"
    },

    # ==========================================
    # NHÓM C: LỖI NGỮ CẢNH & ĐỘ RÕ RÀNG (CONTEXT & CLARITY)
    # ==========================================
    "C01": {
        "name": "Đối tượng tác động chưa rõ",
        "description": "Không xác định rõ AI cần xử lý cái gì (văn bản, bài toán, dữ liệu).",
        "conditions": "Có động từ hành động nhưng thiếu tân ngữ (VD: 'Hãy tóm tắt' - Tóm tắt cái gì?).",
        "exclusions": "Prompt đã có ngữ cảnh ngầm hiểu (VD: trả lời tin nhắn trước).",
        "evidence_req": "Trích nguyên văn câu thiếu đối tượng.",
        "severity": "Cao"
    },
    "C02": {
        "name": "Thiếu bối cảnh",
        "description": "Không nêu rõ mục đích, hoàn cảnh, đối tượng độc giả.",
        "conditions": "Prompt thiếu thông tin về người đọc, tình huống sử dụng khiến kết quả có thể lệch hướng.",
        "exclusions": "Các nhiệm vụ logic thuần túy (VD: 'Giải phương trình 2x=4').",
        "evidence_req": "Ghi rõ: 'Chưa cung cấp bối cảnh' (Không trích dẫn).",
        "severity": "Trung bình"
    },
    "C03": {
        "name": "Yêu cầu chung chung, mơ hồ",
        "description": "Dùng các từ như 'hay hơn', 'tốt hơn', 'chuyên nghiệp hơn' mà không có tiêu chí.",
        "conditions": "Có chứa các tính từ đánh giá chủ quan mà không định lượng.",
        "exclusions": "Từ ngữ chuyên ngành đã mang nghĩa xác định (VD: 'viết theo phong cách báo chí').",
        "evidence_req": "Trích nguyên văn từ ngữ mơ hồ.",
        "severity": "Trung bình"
    },
    "C04": {
        "name": "Thiếu ví dụ mẫu (Few-shot)",
        "description": "Cần ví dụ để AI bắt chước nhưng prompt không cung cấp.",
        "conditions": "Nhiệm vụ yêu cầu định dạng đặc thù, giọng điệu riêng hoặc cấu trúc phức tạp.",
        "exclusions": "Nhiệm vụ đơn giản hoặc đã được quy định rõ ràng bằng văn bản.",
        "evidence_req": "Ghi rõ: 'Chưa cung cấp ví dụ mẫu' (Không trích dẫn).",
        "severity": "Trung bình"
    },

    # ==========================================
    # NHÓM D: LỖI LOGIC & KHẢ THI (LOGIC & FEASIBILITY)
    # ==========================================
    "D01": {
        "name": "Mâu thuẫn nội bộ",
        "description": "Yêu cầu 'ngắn gọn' nhưng lại 'chi tiết', hoặc vừa 'vui vẻ' vừa 'nghiêm túc'.",
        "conditions": "Có 2 mệnh đề loại trừ lẫn nhau.",
        "exclusions": "Mâu thuẫn ngữ nghĩa tinh tế (VD: 'buồn nhưng hy vọng').",
        "evidence_req": "Trích nguyên văn cả 2 vế mâu thuẫn.",
        "severity": "Cao"
    },
    "D02": {
        "name": "Yêu cầu bất khả thi",
        "description": "Yêu cầu AI làm việc vượt quá khả năng (VD: đọc file chưa cung cấp, dự đoán tương lai).",
        "conditions": "Yêu cầu truy xuất thông tin thời gian thực hoặc dữ liệu ngoại vi không có sẵn.",
        "exclusions": "Yêu cầu mang tính sáng tạo/giả định (VD: 'Hãy tưởng tượng bạn là...').",
        "evidence_req": "Trích nguyên văn câu yêu cầu bất khả thi.",
        "severity": "Cao"
    },

    # ==========================================
    # NHÓM E: LỖI LĨNH VỰC (DOMAIN)
    # ==========================================
    "E01": {
        "name": "Trộn lẫn nhiều lĩnh vực không liên quan",
        "description": "Vừa yêu cầu giải toán vừa yêu cầu viết thơ trong cùng một câu lệnh thiếu liên kết.",
        "conditions": "Các mục tiêu không có mối quan hệ nhân quả hoặc bổ trợ.",
        "exclusions": "Đa nhiệm có chủ đích (VD: 'Viết code và giải thích code').",
        "evidence_req": "Trích nguyên văn các phần trộn lẫn.",
        "severity": "Trung bình"
    },
    "E03": {
        "name": "Thiếu tính đặc thù lĩnh vực (khi cần thiết)",
        "description": "Prompt quá chung chung, không dùng thuật ngữ chuyên ngành khi nhiệm vụ đòi hỏi.",
        "conditions": "Nhiệm vụ mang tính chuyên môn cao nhưng dùng từ ngữ đời thường.",
        "exclusions": "Nhiệm vụ phổ thông hoặc đang giải thích cho người mới.",
        "evidence_req": "Trích nguyên văn cụm từ chung chung.",
        "severity": "Thấp"
    }
}