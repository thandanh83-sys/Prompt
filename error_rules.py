# error_rules.py

ERROR_RULES = {
    # ==========================================
    # --- NHÓM A: HÌNH THỨC & NGÔN NGỮ (Linguistic) ---
    # ==========================================
    "A01": {
        "name": "Lỗi chính tả / Ngữ pháp",
        "description": "Sai chính tả, sai từ ngữ, chia động từ sai gây khó hiểu.",
        "conditions": ["Có từ viết sai chính tả rõ ràng hoặc ngữ pháp lủng củng."],
        "exclusions": ["Tên riêng nước ngoài, thuật ngữ chuyên ngành.", "Tiếng lóng, từ địa phương, viết tắt phổ biến."],
        "evidence_req": "Trích nguyên văn từ viết sai hoặc câu sai ngữ pháp.",
        "related_criteria": ["P06", "P07"],
        "overlap_rule": "Không gắn A02 nếu chỉ có 1 lỗi chính tả đơn lẻ.",
        "severity": "Thấp",
        "fix": "Sửa lại từ đúng chính tả, cấu trúc ngữ pháp.",
        "examples": {"positive": ["Viết bài văn tả mẹ thật xúc đông."], "negative": ["Hãy viết một API endpoint bằng Node.js."]}
    },
    "A02": {
        "name": "Thiếu dấu câu",
        "description": "Câu văn không có dấu chấm, phẩy gây khó hiểu, sai lệch nghĩa.",
        "conditions": ["Thiếu dấu câu ở vị trí bắt buộc khiến câu dài dòng."],
        "exclusions": ["Văn bản dạng danh sách (bullet points) không cần dấu chấm.", "Prompt viết theo phong cách thơ."],
        "evidence_req": "Trích đoạn thiếu dấu câu.",
        "related_criteria": ["P06", "P08"],
        "overlap_rule": "Không gắn nếu thiếu dấu câu do cố ý viết style.",
        "severity": "Thấp",
        "fix": "Thêm dấu câu phù hợp.",
        "examples": {"positive": ["Tôi muốn bạn viết code python và giải thích"], "negative": ["Tôi muốn bạn viết code Python, sau đó giải thích chi tiết."]}
    },
    "A03": {
        "name": "Lặp lại từ ngữ / Ý tưởng",
        "description": "Lặp từ, lặp ý không cần thiết gây nhàm chán.",
        "conditions": ["Cùng một từ/cụm từ lặp lại quá nhiều lần trong 1 câu/đoạn."],
        "exclusions": ["Lặp lại có chủ đích để nhấn mạnh (điệp ngữ)."],
        "evidence_req": "Trích đoạn lặp.",
        "related_criteria": ["P07", "P08"],
        "overlap_rule": "Không gắn nếu việc lặp lại là do yêu cầu định dạng.",
        "severity": "Thấp",
        "fix": "Dùng từ đồng nghĩa hoặc lược bỏ ý lặp.",
        "examples": {"positive": ["Hãy viết bài văn tả mẹ, bài văn tả mẹ phải hay."], "negative": ["Hãy viết bài văn tả mẹ thật cảm động."]}
    },

    # ==========================================
    # --- NHÓM B: CẤU TRÚC (Structural) ---
    # ==========================================
    "B01": {
        "name": "Thiếu thành phần cấu trúc",
        "description": "Thiếu các thành phần quan trọng như Vai trò, Mục tiêu, Định dạng.",
        "conditions": ["Nhiệm vụ phức tạp nhưng thiếu hụt nghiêm trọng thành phần chỉ dẫn."],
        "exclusions": ["Prompt ngắn, nhiệm vụ đơn giản.", "Prompt dạng câu hỏi trực tiếp."],
        "evidence_req": "Chỉ ra sự vắng mặt của thành phần đó (VD: Không có phần Yêu cầu).",
        "related_criteria": ["P01", "P02", "P03", "P04", "P13"],
        "overlap_rule": "Chỉ gắn 1 mã B01 chung, không gắn lặp.",
        "severity": "Cao",
        "fix": "Bổ sung thành phần còn thiếu vào prompt.",
        "examples": {"positive": ["Viết code web."], "negative": ["Viết hàm Python tính giai thừa."]}
    },
    "B02": {
        "name": "Sắp xếp không logic",
        "description": "Các phần trong prompt sắp xếp lộn xộn, không theo trình tự.",
        "conditions": ["Ý trước mâu thuẫn hoặc không dẫn dắt đến ý sau."],
        "exclusions": ["Prompt dùng biện pháp tu từ đảo ngữ."],
        "evidence_req": "Trích đoạn sắp xếp lộn xộn.",
        "related_criteria": ["P08"],
        "overlap_rule": "Không gắn B03 nếu chỉ là lộn xộn ý.",
        "severity": "Trung bình",
        "fix": "Sắp xếp lại theo trình tự chuẩn (Vai trò -> Bối cảnh -> Yêu cầu).",
        "examples": {"positive": ["Bối cảnh là tôi muốn ăn phở. Hãy viết code Python."], "negative": ["Bạn là đầu bếp. Hãy viết công thức nấu phở."]}
    },
    "B03": {
        "name": "Sai phân cấp",
        "description": "Ý lớn và ý nhỏ ngang hàng nhau gây hiểu lầm.",
        "conditions": ["Sử dụng sai heading, bullet points không đúng cấp bậc."],
        "exclusions": ["Prompt không sử dụng markdown/heading."],
        "evidence_req": "Trích đoạn phân cấp sai.",
        "related_criteria": ["P08"],
        "overlap_rule": "Không gắn B02 nếu vấn đề chỉ là cấp bậc.",
        "severity": "Thấp",
        "fix": "Chỉnh sửa lại heading/bullet point.",
        "examples": {"positive": ["- Yêu cầu 1\n-- Yêu cầu phụ 1.1\n- Yêu cầu 2"], "negative": ["1. Yêu cầu 1\n   - Yêu cầu phụ 1.1\n2. Yêu cầu 2"]}
    },
    "B04": {
        "name": "Chưa quy định định dạng đầu ra",
        "description": "Không yêu cầu AI trả về dạng gì (văn bản, bảng, JSON...).",
        "conditions": ["Nhiệm vụ yêu cầu xuất dữ liệu nhưng không có từ khóa chỉ định định dạng."],
        "exclusions": ["Prompt đơn giản mặc định là văn bản."],
        "evidence_req": "Prompt không nhắc đến 'format', 'bảng', 'json', v.v.",
        "related_criteria": ["P04"],
        "overlap_rule": "Có thể đi kèm C03.",
        "severity": "Trung bình",
        "fix": "Thêm yêu cầu định dạng cụ thể.",
        "examples": {"positive": ["Liệt kê 5 loại trái cây."], "negative": ["Liệt kê 5 loại trái cây dưới dạng bảng 2 cột."]}
    },

    # ==========================================
    # --- NHÓM C: NỘI DUNG & NGỮ CẢNH (Contextual) ---
    # ==========================================
    "C01": {
        "name": "Đối tượng chưa rõ",
        "description": "Không xác định được AI đang cần tác động vào ai, cái gì.",
        "conditions": ["Có danh từ chỉ đối tượng nhưng quá chung chung."],
        "exclusions": ["Prompt dạng template có placeholder [Đối tượng]."],
        "evidence_req": "Trích từ ngữ chỉ đối tượng mơ hồ.",
        "related_criteria": ["P02"],
        "overlap_rule": "Không gắn C02 nếu chỉ thiếu đối tượng.",
        "severity": "Cao",
        "fix": "Xác định rõ đối tượng cụ thể.",
        "examples": {"positive": ["Hãy viết thư cho người đó."], "negative": ["Hãy viết thư cho sếp nam 40 tuổi."]}
    },
    "C02": {
        "name": "Thiếu bối cảnh",
        "description": "Không có tình huống, không gian, thời gian hoặc mục đích.",
        "conditions": ["Không nêu mục đích hoặc hoàn cảnh sử dụng."],
        "exclusions": ["Prompt dạng câu hỏi kiến thức đơn thuần."],
        "evidence_req": "Chỉ ra sự thiếu vắng bối cảnh (VD: Không có thông tin về địa điểm).",
        "related_criteria": ["P03"],
        "overlap_rule": "Không gắn C01 nếu đối tượng đã rõ.",
        "severity": "Trung bình",
        "fix": "Thêm bối cảnh sử dụng.",
        "examples": {"positive": ["Viết một email xin nghỉ phép."], "negative": ["Viết email xin nghỉ phép gửi sếp, lý do bị ốm."]}
    },
    "C03": {
        "name": "Yêu cầu chung chung",
        "description": "Động từ hành động không rõ ràng, cho phép nhiều cách hiểu.",
        "conditions": ["Động từ hành động không rõ ràng (VD: 'giúp tôi', 'làm về')."],
        "exclusions": ["Prompt ngắn nhưng động từ rõ ràng."],
        "evidence_req": "Trích nguyên văn cụm từ chung chung.",
        "related_criteria": ["P01", "P07"],
        "overlap_rule": "Không gắn C01 nếu vấn đề là hành động.",
        "severity": "Cao",
        "fix": "Cụ thể hóa động từ hành động.",
        "examples": {"positive": ["Giúp tôi về văn học."], "negative": ["Viết đoạn văn 200 chữ phân tích nhân vật Lão Hạc."]}
    },
    "C04": {
        "name": "Thiếu ví dụ (Few-shot)",
        "description": "Không có ví dụ mẫu khiến AI khó bắt chước phong cách.",
        "conditions": ["Prompt yêu cầu bắt chước phong cách, cấu trúc cụ thể nhưng không cung cấp mẫu."],
        "exclusions": ["Prompt đơn giản không yêu cầu style đặc biệt."],
        "evidence_req": "Chỉ ra yêu cầu về style và sự thiếu vắng ví dụ.",
        "related_criteria": ["P05"],
        "overlap_rule": "Chỉ gắn khi thực sự cần thiết.",
        "severity": "Trung bình",
        "fix": "Thêm 1-2 ví dụ mẫu Input/Output.",
        "examples": {"positive": ["Hãy viết theo phong cách của Nam Cao."], "negative": ["Viết đoạn văn tả mẹ."]}
    },

    # ==========================================
    # --- NHÓM D: LOGIC & TÍNH KHẢ THI (Logical) ---
    # ==========================================
    "D01": {
        "name": "Mâu thuẫn nội bộ",
        "description": "Các yêu cầu đá nhau, không thể thỏa mãn đồng thời.",
        "conditions": ["Yêu cầu A và B trực tiếp phủ định nhau."],
        "exclusions": ["Mâu thuẫn do hiểu sai ngữ pháp."],
        "evidence_req": "Trích 2 vế mâu thuẫn.",
        "related_criteria": ["P14"],
        "overlap_rule": "Không gắn D02 nếu không phải bất khả thi.",
        "severity": "Nghiêm trọng",
        "fix": "Loại bỏ 1 trong 2 yêu cầu mâu thuẫn.",
        "examples": {"positive": ["Viết bài 1000 chữ nhưng dưới 100 chữ."], "negative": ["Viết bài 500-1000 chữ."]}
    },
    "D02": {
        "name": "Yêu cầu bất khả thi",
        "description": "Yêu cầu AI làm điều vượt khả năng thực tế (thời gian thực, đọc suy nghĩ).",
        "conditions": ["Yêu cầu truy cập thời gian thực, dữ liệu nội bộ."],
        "exclusions": ["Yêu cầu khó nhưng AI vẫn có thể giả lập."],
        "evidence_req": "Trích yêu cầu bất khả thi.",
        "related_criteria": ["P12"],
        "overlap_rule": "Không gắn D01 nếu chỉ là bất khả thi.",
        "severity": "Cao",
        "fix": "Điều chỉnh lại yêu cầu cho phù hợp với giới hạn của AI.",
        "examples": {"positive": ["Cho tôi biết giá vàng hiện tại."], "negative": ["Hướng dẫn tôi cách tra giá vàng."]}
    },
    "D03": {
        "name": "Vai trò không phù hợp",
        "description": "Giao vai trò trái ngược nhiệm vụ.",
        "conditions": ["Vai trò không có kỹ năng thực hiện yêu cầu."],
        "exclusions": ["Vai trò hư cấu nhưng có thể suy luận."],
        "evidence_req": "Trích vai trò và yêu cầu trái ngược.",
        "related_criteria": ["P13"],
        "overlap_rule": "Không gắn C03 nếu vai trò rõ nhưng sai.",
        "severity": "Cao",
        "fix": "Đổi vai trò phù hợp với nhiệm vụ.",
        "examples": {"positive": ["Bạn là bác sĩ. Viết code Python."], "negative": ["Bạn là lập trình viên. Viết code Python."]}
    },

    # ==========================================
    # --- NHÓM E: CHUYÊN MÔN & THUẬT NGỮ (Professional) ---
    # ==========================================
    "E01": {
        "name": "Trộn lẫn lĩnh vực",
        "description": "Gom nhiều lĩnh vực không liên quan vào 1 prompt.",
        "conditions": ["Prompt yêu cầu làm việc thuộc các lĩnh vực khác biệt, không liên kết."],
        "exclusions": ["Prompt đa nhiệm có chủ đích."],
        "evidence_req": "Trích các từ khóa của các lĩnh vực khác nhau.",
        "related_criteria": ["P09", "P11"],
        "overlap_rule": "Không gắn C03 nếu mỗi phần đều rõ.",
        "severity": "Trung bình",
        "fix": "Tách thành các prompt riêng.",
        "examples": {"positive": ["Viết code Python và nấu phở."], "negative": ["Viết code Python quản lý công thức nấu phở."]}
    },
    "E02": {
        "name": "Thuật ngữ không nhất quán",
        "description": "Dùng nhiều từ khác nhau cho cùng 1 khái niệm.",
        "conditions": ["Gọi 'khách hàng' lúc thì 'người dùng', lúc thì 'client'."],
        "exclusions": ["Sử dụng từ đồng nghĩa để tránh lặp từ."],
        "evidence_req": "Trích các thuật ngữ khác nhau.",
        "related_criteria": ["P11"],
        "overlap_rule": "Không gắn A03 nếu chỉ là trái nghĩa.",
        "severity": "Trung bình",
        "fix": "Thống nhất 1 thuật ngữ xuyên suốt.",
        "examples": {"positive": ["Gửi email cho khách hàng và client."], "negative": ["Gửi email cho khách hàng và họ."]}
    },
    "E03": {
        "name": "Thiếu tính đặc thù lĩnh vực",
        "description": "Prompt quá chung chung, không có thuật ngữ chuyên ngành.",
        "conditions": ["Prompt yêu cầu kiến thức chuyên sâu nhưng dùng từ ngữ đời thường."],
        "exclusions": ["Prompt dành cho đại chúng."],
        "evidence_req": "Chỉ ra sự thiếu vắng thuật ngữ.",
        "related_criteria": ["P10"],
        "overlap_rule": "Không gắn C03 nếu vấn đề là thiếu thuật ngữ.",
        "severity": "Thấp",
        "fix": "Thêm thuật ngữ chuyên ngành.",
        "examples": {"positive": ["Chữa bệnh đau đầu."], "negative": ["Tư vấn phác đồ điều trị Migraine."]}
    },

    # ==========================================
    # --- NHÓM F: KỸ THUẬT & ĐỊNH DẠNG DỮ LIỆU (Technical) ---
    # ==========================================
    "F01": {
        "name": "Lỗi cấu trúc dữ liệu (Schema)",
        "description": "Yêu cầu JSON, XML, bảng nhưng không cung cấp cấu trúc mẫu.",
        "conditions": ["Đòi hỏi định dạng phức tạp nhưng không có schema."],
        "exclusions": ["Yêu cầu văn bản thông thường."],
        "evidence_req": "Trích đoạn yêu cầu định dạng nhưng thiếu cấu trúc.",
        "related_criteria": ["P04"],
        "overlap_rule": "Không gắn B04 nếu đây là lỗi thiếu schema.",
        "severity": "Trung bình",
        "fix": "Thêm cấu trúc mẫu JSON/bảng vào prompt.",
        "examples": {"positive": ["Trả về JSON danh sách sản phẩm."], "negative": ["Trả về JSON dạng: {\"id\": 1, \"name\": \"...\"}"]}
    },
    "F02": {
        "name": "Sai thẻ Placeholder",
        "description": "Dùng biến giữ chỗ [Tên], {Sản phẩm} nhưng không giải thích.",
        "conditions": ["Có placeholder nhưng không có hướng dẫn điền."],
        "exclusions": ["Prompt không dùng placeholder."],
        "evidence_req": "Trích placeholder mơ hồ.",
        "related_criteria": ["P06"],
        "overlap_rule": "Không gắn C03 nếu đã có placeholder.",
        "severity": "Thấp",
        "fix": "Giải thích rõ các biến cần điền.",
        "examples": {"positive": ["Hãy viết cho [Tên]."], "negative": ["Hãy viết thư cho [Tên khách hàng]."]}
    },
    "F03": {
        "name": "Xung đột ngôn ngữ",
        "description": "Prompt và yêu cầu đầu ra khác ngôn ngữ mà không dặn dò.",
        "conditions": ["Prompt tiếng Việt yêu cầu output tiếng Anh (hoặc ngược lại)."],
        "exclusions": ["Có yêu cầu dịch thuật rõ ràng."],
        "evidence_req": "Trích đoạn yêu cầu ngôn ngữ.",
        "related_criteria": ["P09"],
        "overlap_rule": "Không gắn nếu có yêu cầu dịch.",
        "severity": "Thấp",
        "fix": "Ghi rõ ngôn ngữ đầu ra mong muốn.",
        "examples": {"positive": ["Viết bài bằng tiếng Anh."], "negative": ["Viết bài bằng tiếng Anh (Translate to English)."]}
    },

    # ==========================================
    # --- NHÓM G: TÍNH THỰC TIỄN & ỨNG DỤNG (Practical) ---
    # ==========================================
    "G01": {
        "name": "Thiếu tiêu chuẩn đánh giá (Rubric)",
        "description": "Yêu cầu chấm điểm, xếp hạng nhưng không có thang điểm.",
        "conditions": ["Yêu cầu đánh giá/xếp hạng nhưng không nêu tiêu chí."],
        "exclusions": ["Chỉ yêu cầu liệt kê."],
        "evidence_req": "Trích yêu cầu đánh giá nhưng thiếu tiêu chí.",
        "related_criteria": ["P08"],
        "overlap_rule": "Không gắn với C03.",
        "severity": "Trung bình",
        "fix": "Thêm thang điểm và tiêu chí đánh giá.",
        "examples": {"positive": ["Xếp hạng các hãng mỹ phẩm."], "negative": ["Xếp hạng các hãng mỹ phẩm theo 3 tiêu chí: giá, thành phần, độ phổ biến (thang 10)."]}
    },
    "G02": {
        "name": "Yêu cầu vượt quá giới hạn",
        "description": "Yêu cầu khối lượng công việc quá lớn cho một lần trả lời.",
        "conditions": ["Yêu cầu viết hàng chục ngàn chữ, hoặc dữ liệu thời gian thực."],
        "exclusions": ["Yêu cầu tóm tắt, liệt kê ngắn."],
        "evidence_req": "Trích đoạn yêu cầu quá dài.",
        "related_criteria": ["P12"],
        "overlap_rule": "Không gắn D02 nếu chỉ là vượt giới hạn độ dài.",
        "severity": "Cao",
        "fix": "Chia nhỏ yêu cầu thành các phần.",
        "examples": {"positive": ["Viết 10,000 chữ về lịch sử."], "negative": ["Viết dàn ý cho 10,000 chữ về lịch sử."]}
    },
    "G03": {
        "name": "Thiếu CTA (Call to Action)",
        "description": "Prompt về bán hàng/quảng cáo thiếu lời kêu gọi hành động.",
        "conditions": ["Prompt quảng cáo nhưng không yêu cầu CTA."],
        "exclusions": ["Prompt không mang tính bán hàng."],
        "evidence_req": "Trích đoạn yêu cầu quảng cáo thiếu CTA.",
        "related_criteria": ["P09"],
        "overlap_rule": "Không gắn nếu không có ngữ cảnh bán hàng.",
        "severity": "Trung bình",
        "fix": "Thêm yêu cầu CTA vào prompt.",
        "examples": {"positive": ["Viết quảng cáo bán áo thun."], "negative": ["Viết quảng cáo bán áo thun, kèm CTA 'Mua ngay'."]}
    },

    # ==========================================
    # --- NHÓM H: CHUYÊN NGÀNH SÂU (Domain-Specific) ---
    # ==========================================
    "H01": {
        "name": "Code: Thiếu xử lý ngoại lệ",
        "description": "Prompt yêu cầu viết code nhưng không yêu cầu xử lý lỗi (try/catch).",
        "conditions": ["Prompt lập trình nhưng không nhắc đến edge cases, try-catch."],
        "exclusions": ["Yêu cầu viết code đơn giản (Hello World)."],
        "evidence_req": "Trích đoạn yêu cầu code thiếu xử lý lỗi.",
        "related_criteria": ["P10", "P12"],
        "overlap_rule": "Không gắn D02.",
        "severity": "Trung bình",
        "fix": "Thêm yêu cầu xử lý ngoại lệ và dữ liệu đầu vào.",
        "examples": {"positive": ["Viết hàm chia 2 số."], "negative": ["Viết hàm chia 2 số, ném lỗi nếu mẫu số bằng 0."]}
    },
    "H02": {
        "name": "Mỹ phẩm: Thiếu cảnh báo an toàn",
        "description": "Prompt tư vấn mỹ phẩm nhưng không yêu cầu cảnh báo kích ứng.",
        "conditions": ["Prompt về sản phẩm bôi lên da nhưng thiếu cảnh báo rủi ro."],
        "exclusions": ["Prompt mua sắm quần áo, đồ gia dụng."],
        "evidence_req": "Trích đoạn tư vấn mỹ phẩm thiếu cảnh báo.",
        "related_criteria": ["P10"],
        "overlap_rule": "Không gắn E03.",
        "severity": "Cao",
        "fix": "Yêu cầu AI cảnh báo các thành phần dễ gây kích ứng.",
        "examples": {"positive": ["Tư vấn kem dưỡng da cho da dầu."], "negative": ["Tư vấn kem dưỡng da cho da dầu, cảnh báo nếu có cồn khô."]}
    },
    "H03": {
        "name": "Marketing: Thiếu Target Audience",
        "description": "Prompt viết content nhưng không xác định đối tượng độc giả.",
        "conditions": ["Prompt viết content/quảng cáo nhưng không nêu khách hàng mục tiêu."],
        "exclusions": ["Prompt viết văn học, thơ ca."],
        "evidence_req": "Trích đoạn yêu cầu viết content thiếu target.",
        "related_criteria": ["P02"],
        "overlap_rule": "Không gắn C01 nếu đã có sản phẩm.",
        "severity": "Trung bình",
        "fix": "Thêm thông tin về độ tuổi, giới tính, sở thích của độc giả.",
        "examples": {"positive": ["Viết bài quảng cáo nước hoa."], "negative": ["Viết bài quảng cáo nước hoa cho nam giới 25-35 tuổi."]}
    }
}