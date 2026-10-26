import re
import math
import unicodedata

# ==========================================
# KHAI BÁO CÁC HẰNG SỐ LOẠI PROMPT & KỸ THUẬT
# Giữ nguyên tên và giá trị để tương thích main.py
# ==========================================
TYPE_PROMPT = "PROMPT"
TYPE_TEMPLATE = "TEMPLATE"
TYPE_PROMPT_META = "PROMPT META"
TYPE_TABLE = "TABLE"
TYPE_STEM = "STEM"
TYPE_EMPTY = "EMPTY"
TYPE_IMAGE = "IMAGE"
TYPE_CREATIVE = "CREATIVE"

TECH_ROLE_PLAY = "ROLE_PLAY"
TECH_FEW_SHOT = "FEW_SHOT"
TECH_COT = "CHAIN_OF_THOUGHT"
TECH_FORMAT = "FORMATTED_OUTPUT"
TECH_CREATIVE = "CREATIVE_GEN"

class ConfigurationError(Exception):
    """Lỗi cấu hình bộ tiêu chí Prompt Linter."""
    pass

# ==========================================
# BỘ TIÊU CHÍ LÕI
# Giữ nguyên ID và trọng số.
# Rubric tập trung vào chất lượng, không chỉ hình thức.
# ==========================================
CRITERIA_CORE = {
    "P01": {
        "name": "Độ rõ nhiệm vụ",
        "weight": 1.2,
        "rubric": (
            "0-2: Không xác định được hành động chính. "
            "3-4: Hành động hoặc mục đích còn mơ hồ đáng kể. "
            "5-6: Xác định được hành động chính nhưng kết quả còn thiếu "
            "một phần. 7-8: Hành động và kết quả mong muốn rõ ràng. "
            "9-10: Nhiệm vụ chính xác, dễ hiểu, ít cần suy đoán."
        ),
    },
    "P02": {
        "name": "Đối tượng tác động",
        "weight": 1.2,
        "rubric": (
            "0-2: Không xác định được đối tượng cần xử lý khi đối tượng "
            "là thiết yếu. 3-4: Đối tượng quá rộng hoặc khó xác định. "
            "5-6: Đối tượng nhận diện được nhưng phạm vi chưa rõ hoàn toàn. "
            "7-8: Đối tượng và phạm vi phù hợp nhiệm vụ. "
            "9-10: Đối tượng, phạm vi và đặc điểm cần thiết được xác định "
            "chính xác. Không yêu cầu chi tiết không cần thiết."
        ),
    },
    "P03": {
        "name": "Bối cảnh",
        "weight": 0.8,
        "rubric": (
            "0-2: Thiếu bối cảnh thiết yếu khiến khó xác định cách làm. "
            "3-4: Thiếu thông tin có ảnh hưởng đáng kể đến kết quả. "
            "5-6: Có bối cảnh cơ bản nhưng còn thiếu một số thông tin hữu ích. "
            "7-8: Cung cấp đủ bối cảnh cần thiết cho nhiệm vụ. "
            "9-10: Bối cảnh liên quan, chính xác và giúp định hướng kết quả "
            "mà không chứa thông tin thừa. Với nhiệm vụ không cần bối cảnh, "
            "không tự động trừ điểm vì thiếu bối cảnh."
        ),
    },
    "P04": {
        "name": "Định dạng đầu ra",
        "weight": 0.8,
        "rubric": (
            "0-2: Thiếu định dạng khiến kết quả khó sử dụng khi định dạng "
            "là thiết yếu. 3-4: Định dạng chưa rõ hoặc chưa phù hợp. "
            "5-6: Có định hướng đầu ra nhưng thiếu một số yêu cầu quan trọng. "
            "7-8: Định dạng phù hợp và đủ rõ. "
            "9-10: Quy định chính xác cấu trúc và cách trình bày khi nhiệm vụ "
            "thực sự cần. Không bắt buộc chỉ định định dạng riêng cho mọi task."
        ),
    },
    "P05": {
        "name": "Độ chi tiết và ví dụ",
        "weight": 1.6,
        "rubric": (
            "0-2: Thiếu hướng dẫn thiết yếu khiến nhiệm vụ khó thực hiện đúng. "
            "3-4: Hướng dẫn còn thiếu hoặc chung chung ở những điểm quan trọng. "
            "5-6: Đủ hướng dẫn cơ bản nhưng còn thiếu tiêu chí hoặc chi tiết "
            "có ảnh hưởng đến kết quả. 7-8: Hướng dẫn đủ cụ thể, phù hợp "
            "với độ phức tạp của nhiệm vụ. 9-10: Chi tiết cần thiết được "
            "quy định tốt, ví dụ có giá trị nếu thực sự hữu ích. "
            "Không chấm thấp chỉ vì không có ví dụ; đánh giá giá trị thông tin, "
            "không đếm số lượng ví dụ."
        ),
    },
    "P06": {
        "name": "Không mơ hồ",
        "weight": 0.2,
        "rubric": (
            "0-2: Có nhiều cách hiểu khác nhau làm thay đổi đáng kể kết quả. "
            "3-4: Có điểm mơ hồ quan trọng chưa được giải quyết. "
            "5-6: Cơ bản hiểu được nhưng còn một vài cách diễn giải khác. "
            "7-8: Hầu hết yêu cầu đều có cách hiểu nhất quán. "
            "9-10: Không có sự mơ hồ đáng kể đối với nhiệm vụ."
        ),
    },
    "P07": {
        "name": "Không chung chung",
        "weight": 0.2,
        "rubric": (
            "0-2: Yêu cầu quá tổng quát để tạo ra kết quả hữu ích. "
            "3-4: Thiếu phạm vi hoặc định hướng quan trọng. "
            "5-6: Có định hướng nhưng còn rộng ở một số điểm. "
            "7-8: Phạm vi và yêu cầu đủ cụ thể cho mục đích. "
            "9-10: Mức độ cụ thể phù hợp tối ưu với nhiệm vụ, không thừa "
            "chi tiết không cần thiết."
        ),
    },
    "P08": {
        "name": "Có cấu trúc",
        "weight": 0.2,
        "rubric": (
            "0-2: Trình tự hoặc quan hệ giữa các yêu cầu gây khó hiểu. "
            "3-4: Các yêu cầu quan trọng chưa được tổ chức hợp lý. "
            "5-6: Có trình tự cơ bản nhưng một số phần chưa rõ quan hệ. "
            "7-8: Cấu trúc dễ theo dõi và hỗ trợ thực hiện nhiệm vụ. "
            "9-10: Các phần được tổ chức rõ ràng, đúng trình tự cần thiết. "
            "Không yêu cầu chia mục nếu nhiệm vụ đơn giản."
        ),
    },
    "P09": {
        "name": "Phù hợp nhiệm vụ",
        "weight": 0.5,
        "rubric": (
            "0-2: Yêu cầu hoặc phương pháp chính không phục vụ mục tiêu. "
            "3-4: Có nhiều yêu cầu lệch khỏi mục tiêu. "
            "5-6: Phần lớn phù hợp nhưng còn yếu tố chưa cần thiết. "
            "7-8: Các yêu cầu nhìn chung hỗ trợ mục tiêu. "
            "9-10: Phương pháp, yêu cầu và phạm vi đều phù hợp với nhiệm vụ."
        ),
    },
    "P10": {
        "name": "Chuyên môn có căn cứ",
        "weight": 1.0,
        "rubric": (
            "0-2: Có yêu cầu chuyên môn sai lệch hoặc thiếu căn cứ nghiêm trọng. "
            "3-4: Yêu cầu chuyên môn thiếu chính xác hoặc thiếu cơ sở cần thiết. "
            "5-6: Có định hướng chuyên môn cơ bản nhưng chưa nêu cách kiểm chứng "
            "khi việc kiểm chứng là cần thiết. 7-8: Yêu cầu chuyên môn phù hợp "
            "và có hướng dựa vào nguồn hoặc phương pháp đáng tin cậy khi cần. "
            "9-10: Tiêu chuẩn chuyên môn và cách kiểm chứng được xác định tốt "
            "đối với nhiệm vụ. Không đòi hỏi thuật ngữ chuyên ngành ở task phổ thông."
        ),
    },
    "P11": {
        "name": "Nhất quán lĩnh vực",
        "weight": 0.8,
        "rubric": (
            "0-2: Nội dung hoặc yêu cầu xung đột với lĩnh vực và mục tiêu chính. "
            "3-4: Có sự lệch hướng hoặc dùng thuật ngữ không nhất quán. "
            "5-6: Phần lớn nhất quán nhưng có điểm cần làm rõ. "
            "7-8: Nội dung và thuật ngữ nhất quán với nhiệm vụ. "
            "9-10: Các yêu cầu nhất quán, chính xác và phù hợp lĩnh vực. "
            "Không xem nhiệm vụ liên ngành có chủ đích là lỗi."
        ),
    },
    "P12": {
        "name": "Yêu cầu khả thi",
        "weight": 0.5,
        "rubric": (
            "0-2: Không thể thực hiện do yêu cầu mâu thuẫn hoặc thiếu điều kiện "
            "thiết yếu không thể khắc phục. 3-4: Khó thực hiện do giới hạn "
            "hoặc điều kiện chưa được xử lý. 5-6: Có thể thực hiện nhưng cần "
            "làm rõ một số giới hạn. 7-8: Khả thi với thông tin và năng lực "
            "được giả định hợp lý. 9-10: Có phạm vi và điều kiện thực hiện rõ. "
            "Không mặc định một yêu cầu là bất khả thi chỉ vì cần công cụ hoặc "
            "dữ liệu bổ sung."
        ),
    },
    "P13": {
        "name": "Vai trò phù hợp",
        "weight": 1.0,
        "rubric": (
            "0-2: Vai trò được nêu gây lệch hướng hoặc không phù hợp khi vai trò "
            "là cần thiết. 3-4: Vai trò quá rộng hoặc không hỗ trợ nhiệm vụ. "
            "5-6: Vai trò có liên quan nhưng chưa làm rõ cách đóng góp. "
            "7-8: Vai trò phù hợp với nhiệm vụ. "
            "9-10: Vai trò xác định đúng chuyên môn hoặc góc nhìn cần thiết. "
            "Không bắt buộc nêu vai trò riêng nếu không đem lại giá trị."
        ),
    },
    "P14": {
        "name": "Không mâu thuẫn",
        "weight": 0.2,
        "rubric": (
            "0-2: Có mâu thuẫn trực tiếp khiến không thể đáp ứng đồng thời "
            "các yêu cầu chính. 3-4: Có mâu thuẫn quan trọng chưa được giải quyết. "
            "5-6: Có điểm chưa thống nhất nhưng có thể diễn giải để xử lý. "
            "7-8: Không có mâu thuẫn đáng kể. "
            "9-10: Các yêu cầu nhất quán, có thể xác định cách ưu tiên nếu cần. "
            "Không nhầm sự khác biệt giữa các lựa chọn với mâu thuẫn."
        ),
    },
}

# ==========================================
# BỘ TIÊU CHÍ KỸ THUẬT
# Giữ nguyên ID, trọng số và cấu trúc.
# ==========================================
CRITERIA_ROLE_PLAY = {
    "R01": {
        "name": "Sự phù hợp của vai trò",
        "weight": 1.5,
        "rubric": (
            "0-2: Vai trò không liên quan hoặc gây sai hướng. "
            "3-4: Vai trò quá chung so với nhiệm vụ. "
            "5-6: Vai trò phù hợp cơ bản. "
            "7-8: Vai trò hỗ trợ rõ mục tiêu và cách thực hiện. "
            "9-10: Vai trò được xác định chính xác theo nhu cầu nhiệm vụ."
        ),
    },
    "R02": {
        "name": "Mục tiêu hội thoại",
        "weight": 1.2,
        "rubric": (
            "0-2: Không xác định mục tiêu tương tác khi mục tiêu là cần thiết. "
            "3-4: Mục tiêu còn mơ hồ. "
            "5-6: Mục tiêu cơ bản rõ. "
            "7-8: Mục tiêu và phạm vi tương tác cụ thể. "
            "9-10: Mục tiêu tương tác rõ, phù hợp và có tiêu chí kết quả "
            "khi việc đo lường có ý nghĩa."
        ),
    },
    "R03": {
        "name": "Giới hạn hành vi",
        "weight": 0.8,
        "rubric": (
            "0-2: Thiếu giới hạn thiết yếu dẫn đến nguy cơ lệch nhiệm vụ. "
            "3-4: Các giới hạn quan trọng chưa rõ. "
            "5-6: Có giới hạn cơ bản. "
            "7-8: Giới hạn phù hợp với nhiệm vụ. "
            "9-10: Quy định rõ phạm vi, điều cần tránh và cách xử lý ngoại lệ "
            "khi thực sự cần."
        ),
    },
}

CRITERIA_FEW_SHOT = {
    "F01": {
        "name": "Tính liên quan của ví dụ",
        "weight": 1.5,
        "rubric": (
            "0-2: Ví dụ được cung cấp gây hiểu sai hoặc không liên quan. "
            "3-4: Ví dụ chỉ liên quan một phần. "
            "5-6: Ví dụ minh họa được yêu cầu cơ bản. "
            "7-8: Ví dụ phù hợp và giúp làm rõ đầu ra mong muốn. "
            "9-10: Ví dụ thể hiện chính xác mẫu cần học, nếu có ví dụ. "
            "Không yêu cầu ví dụ khi prompt không sử dụng few-shot."
        ),
    },
    "F02": {
        "name": "Độ bao quát của ví dụ",
        "weight": 1.2,
        "rubric": (
            "0-2: Ví dụ không thể hiện được mẫu cần học hoặc gây hiểu sai. "
            "3-4: Ví dụ chưa bao quát khác biệt quan trọng. "
            "5-6: Ví dụ bao quát trường hợp chính. "
            "7-8: Ví dụ làm rõ các biến thể cần thiết. "
            "9-10: Ví dụ bao quát đúng phạm vi và ngoại lệ quan trọng khi cần. "
            "Không đánh giá bằng số lượng ví dụ đơn thuần."
        ),
    },
    "F03": {
        "name": "Cấu trúc Input-Output",
        "weight": 0.8,
        "rubric": (
            "0-2: Quan hệ giữa đầu vào và đầu ra mẫu không thể xác định. "
            "3-4: Phân biệt input/output chưa rõ. "
            "5-6: Có thể nhận diện đầu vào và đầu ra. "
            "7-8: Cặp đầu vào-đầu ra được trình bày rõ ràng. "
            "9-10: Cấu trúc mẫu nhất quán, dễ phân biệt và dễ áp dụng."
        ),
    },
}

CRITERIA_COT = {
    "C01": {
        "name": "Yêu cầu giải quyết có cấu trúc",
        "weight": 1.5,
        "rubric": (
            "0-2: Không có phương pháp xử lý phù hợp khi task cần quy trình. "
            "3-4: Cách thực hiện quá mơ hồ. "
            "5-6: Có các bước hoặc cách tiếp cận cơ bản. "
            "7-8: Quy trình phù hợp với độ phức tạp của nhiệm vụ. "
            "9-10: Quy trình rõ, hiệu quả và có thể kiểm tra kết quả."
        ),
    },
    "C02": {
        "name": "Khả năng kiểm tra lập luận",
        "weight": 1.2,
        "rubric": (
            "0-2: Không có yêu cầu kiểm tra trong task cần độ chính xác cao. "
            "3-4: Thiếu cách xác minh kết quả quan trọng. "
            "5-6: Có yêu cầu giải thích hoặc kiểm tra cơ bản. "
            "7-8: Có phương pháp xác minh phù hợp. "
            "9-10: Nêu rõ cách kiểm chứng kết quả, giả định và nguồn sai số "
            "khi phù hợp. Ưu tiên kết quả và giải thích có thể kiểm tra; "
            "không bắt buộc tiết lộ suy luận nội bộ chi tiết."
        ),
    },
    "C03": {
        "name": "Kết luận rõ ràng",
        "weight": 0.8,
        "rubric": (
            "0-2: Không thể nhận diện kết quả cần trả về. "
            "3-4: Kết luận chưa rõ hoặc bị lẫn với nội dung khác. "
            "5-6: Có kết quả cuối cơ bản. "
            "7-8: Kết quả được trình bày rõ và phù hợp yêu cầu. "
            "9-10: Kết luận, đáp án hoặc hành động tiếp theo được nêu chính xác "
            "theo mục tiêu. Không bắt buộc tách kết luận nếu task không cần."
        ),
    },
}

CRITERIA_FORMATTED_OUTPUT = {
    "FO01": {
        "name": "Schema và kiểu dữ liệu",
        "weight": 1.5,
        "rubric": (
            "0-2: Định dạng có cấu trúc là thiết yếu nhưng không thể xác định "
            "được cấu trúc mong muốn. "
            "3-4: Chỉ nêu tên định dạng nhưng còn thiếu yêu cầu quan trọng. "
            "5-6: Có cấu trúc cơ bản. "
            "7-8: Cấu trúc và kiểu dữ liệu đủ rõ cho mục đích sử dụng. "
            "9-10: Schema rõ, nhất quán và có thể kiểm tra khi cần. "
            "Không bắt buộc schema chi tiết cho yêu cầu định dạng đơn giản."
        ),
    },
    "FO02": {
        "name": "Trường bắt buộc",
        "weight": 1.0,
        "rubric": (
            "0-2: Thiếu trường thiết yếu trong đầu ra có cấu trúc. "
            "3-4: Một số trường quan trọng chưa rõ. "
            "5-6: Các trường chính được nêu. "
            "7-8: Trường cần thiết và mục đích sử dụng được xác định. "
            "9-10: Phân biệt rõ trường bắt buộc, tùy chọn và điều kiện áp dụng "
            "khi schema cần các phân biệt đó."
        ),
    },
    "FO03": {
        "name": "Quy tắc xử lý lỗi",
        "weight": 1.0,
        "rubric": (
            "0-2: Không quy định cách xử lý lỗi trong tác vụ mà lỗi cần được "
            "xử lý theo quy tắc cụ thể. "
            "3-4: Cách xử lý còn thiếu hoặc khó áp dụng. "
            "5-6: Có hướng xử lý cơ bản. "
            "7-8: Có hướng xử lý phù hợp với các lỗi thường gặp. "
            "9-10: Quy định rõ lỗi, trường hợp ngoại lệ và cách phản hồi khi "
            "điều đó cần thiết. Không bắt buộc quy tắc xử lý lỗi cho mọi task."
        ),
    },
}

CRITERIA_CREATIVE = {
    "CG01": {
        "name": "Mục tiêu sáng tạo",
        "weight": 1.5,
        "rubric": (
            "0-2: Không xác định được mục tiêu sáng tạo chính. "
            "3-4: Mục tiêu quá rộng hoặc khó hiểu. "
            "5-6: Mục tiêu cơ bản rõ. "
            "7-8: Mục tiêu và phạm vi sáng tạo cụ thể. "
            "9-10: Mục tiêu định hướng tốt sản phẩm sáng tạo mà vẫn giữ không "
            "gian sáng tạo cần thiết."
        ),
    },
    "CG02": {
        "name": "Đối tượng độc giả",
        "weight": 1.2,
        "rubric": (
            "0-2: Không xác định được độc giả khi điều đó ảnh hưởng thiết yếu "
            "đến nội dung. "
            "3-4: Độc giả mô tả quá rộng hoặc không phù hợp. "
            "5-6: Độc giả cơ bản xác định được. "
            "7-8: Độc giả và nhu cầu liên quan được mô tả đủ rõ. "
            "9-10: Định hướng độc giả phù hợp chính xác với mục đích. "
            "Không bắt buộc nêu tuổi hoặc sở thích nếu không cần thiết."
        ),
    },
    "CG03": {
        "name": "Phong cách và ràng buộc",
        "weight": 1.0,
        "rubric": (
            "0-2: Thiếu định hướng phong cách thiết yếu hoặc có yêu cầu "
            "làm lệch sản phẩm. "
            "3-4: Phong cách còn mơ hồ. "
            "5-6: Có định hướng phong cách cơ bản. "
            "7-8: Phong cách, giọng điệu và giới hạn quan trọng được xác định. "
            "9-10: Định hướng phong cách rõ, phù hợp mục tiêu và đủ linh hoạt. "
            "Không bắt buộc giới hạn số từ nếu nhiệm vụ không cần."
        ),
    },
}

# ==========================================
# 11 MỤC REWRITE
# Giữ nguyên chính xác tên và thứ tự.
# ==========================================
REQUIRED_REWRITE_SECTIONS = [
    "1. VAI TRÒ",
    "2. BỐI CẢNH",
    "3. INPUT",
    "4. MỤC TIÊU",
    "5. YÊU CẦU",
    "6. RÀNG BUỘC",
    "7. TASK",
    "8. ĐỊNH DẠNG ĐẦU RA",
    "9. NEVER DO",
    "10. THỨ TỰ ƯU TIÊN",
    "11. XỬ LÝ NỘI BỘ",
]

# ==========================================
# KIỂM TRA CẤU HÌNH
# Không đổi schema tiêu chí hiện tại.
# ==========================================
def validate_config(main_criteria: dict, tech_criteria: dict):
    if not isinstance(main_criteria, dict) or not main_criteria:
        raise ConfigurationError("Nhóm tiêu chí chính bị rỗng hoặc sai kiểu.")
    if not isinstance(tech_criteria, dict):
        raise ConfigurationError("Nhóm tiêu chí kỹ thuật phải là dict.")
    duplicate_ids = set(main_criteria) & set(tech_criteria)
    if duplicate_ids:
        raise ConfigurationError(
            f"Phát hiện ID tiêu chí bị trùng giữa Main và Tech: "
            f"{sorted(duplicate_ids)}"
        )
    all_criteria = {**main_criteria, **tech_criteria}
    for criterion_id, criterion in all_criteria.items():
        if not isinstance(criterion_id, str) or not criterion_id.strip():
            raise ConfigurationError("ID tiêu chí phải là chuỗi không rỗng.")
        if not isinstance(criterion, dict):
            raise ConfigurationError(
                f"Cấu hình tiêu chí '{criterion_id}' phải là dict."
            )
        name = criterion.get("name")
        rubric = criterion.get("rubric")
        weight = criterion.get("weight")
        if not isinstance(name, str) or not name.strip():
            raise ConfigurationError(
                f"Tiêu chí '{criterion_id}' thiếu tên hợp lệ."
            )
        if not isinstance(rubric, str) or not rubric.strip():
            raise ConfigurationError(
                f"Tiêu chí '{criterion_id}' thiếu rubric hợp lệ."
            )
        if isinstance(weight, bool) or type(weight) not in (int, float):
            raise ConfigurationError(
                f"Trọng số của '{criterion_id}' phải là số."
            )
        if not math.isfinite(weight) or weight <= 0:
            raise ConfigurationError(
                f"Trọng số của '{criterion_id}' phải hữu hạn và lớn hơn 0."
            )
    if len(REQUIRED_REWRITE_SECTIONS) != 11:
        raise ConfigurationError("Danh sách rewrite phải có đúng 11 mục.")
    if len(set(REQUIRED_REWRITE_SECTIONS)) != 11:
        raise ConfigurationError("Tên các mục rewrite không được trùng.")

# ==========================================
# LẤY TIÊU CHÍ THEO KỸ THUẬT
# Giữ nguyên hành vi chọn nhóm kỹ thuật theo classification.
# ==========================================
def get_criteria_by_type(classification: dict) -> dict:
    if not isinstance(classification, dict):
        raise ConfigurationError("classification phải là dict.")
    techniques = classification.get("techniques", [])
    if not isinstance(techniques, list):
        raise ConfigurationError("classification['techniques'] phải là list.")
    
    main_criteria = dict(CRITERIA_CORE)
    tech_criteria = {}
    
    if TECH_ROLE_PLAY in techniques:
        tech_criteria.update(CRITERIA_ROLE_PLAY)
    if TECH_FEW_SHOT in techniques:
        tech_criteria.update(CRITERIA_FEW_SHOT)
    if TECH_COT in techniques:
        tech_criteria.update(CRITERIA_COT)
    if TECH_FORMAT in techniques:
        tech_criteria.update(CRITERIA_FORMATTED_OUTPUT)
    if TECH_CREATIVE in techniques:
        tech_criteria.update(CRITERIA_CREATIVE)
        
    validate_config(main_criteria, tech_criteria)
    return {
        "main": main_criteria,
        "tech": tech_criteria,
    }

# ==========================================
# CHUẨN HÓA VÀ NHẬN DIỆN KEYWORD
# ==========================================
def normalize_for_matching(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.casefold()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def match_keywords(text: str, keywords: list) -> bool:
    """
    So khớp cụm từ theo ranh giới từ.
    Tránh khớp một từ khóa nằm bên trong từ dài hơn.
    """
    if not isinstance(text, str) or not text.strip():
        return False
    normalized_text = normalize_for_matching(text)
    for keyword in keywords:
        normalized_keyword = normalize_for_matching(keyword)
        if not normalized_keyword:
            continue
        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_keyword)
            + r"(?!\w)"
        )
        if re.search(pattern, normalized_text, flags=re.UNICODE):
            return True
    return False

def _starts_with_any(text: str, phrases: list) -> bool:
    """Kiểm tra cụm từ mở đầu, hữu ích cho ý định chính của prompt."""
    for phrase in phrases:
        normalized_phrase = normalize_for_matching(phrase)
        if text.startswith(normalized_phrase):
            return True
    return False

# ==========================================
# PHÂN LOẠI PROMPT
# Giữ nguyên schema trả về:
# {"main_task": ..., "techniques": [...]}
# ==========================================
def classify_prompt(prompt_text: str) -> dict:
    if not isinstance(prompt_text, str):
        return {"main_task": TYPE_EMPTY, "techniques": []}
        
    text = normalize_for_matching(prompt_text)
    if not text:
        return {"main_task": TYPE_EMPTY, "techniques": []}
        
    techniques = []
    
    # --------------------------------------
    # 1. Nhận diện kỹ thuật
    # Giảm khớp nhầm từ khóa quá rộng.
    # --------------------------------------
    role_phrases = [
        "đóng vai", "hãy vào vai", "giả sử bạn là", "bạn hãy đóng vai",
        "act as", "role:", "vai trò:",
    ]
    # "Bạn là" chỉ được xem là dấu hiệu vai trò khi đứng đầu
    # hoặc xuất hiện như một chỉ dẫn độc lập.
    role_detected = (
        match_keywords(text, role_phrases)
        or _starts_with_any(text, ["bạn là"])
    )
    if role_detected:
        techniques.append(TECH_ROLE_PLAY)
        
    few_shot_phrases = [
        "ví dụ 1:", "ví dụ mẫu:", "dưới đây là ví dụ",
        "few-shot", "input example:", "output example:",
    ]
    # Input:/Output: riêng lẻ có thể chỉ là nhãn văn bản,
    # vì vậy không tự động xem từng nhãn là few-shot.
    has_input_output_pair = (
        match_keywords(text, ["input:", "đầu vào:"])
        and match_keywords(text, ["output:", "đầu ra:"])
    )
    if match_keywords(text, few_shot_phrases) or has_input_output_pair:
        techniques.append(TECH_FEW_SHOT)
        
    cot_phrases = [
        "từng bước", "giải thích từng bước", "trình bày các bước giải",
        "suy luận từng bước", "chain of thought", "step-by-step", "cot",
    ]
    if match_keywords(text, cot_phrases):
        techniques.append(TECH_COT)
        
    format_phrases = [
        "json", "xml", "định dạng bảng", "markdown",
        "output format:", "yaml", "csv",
    ]
    if match_keywords(text, format_phrases):
        techniques.append(TECH_FORMAT)
        
    creative_phrases = [
        "viết truyện", "làm thơ", "sáng tác", "viết kịch bản",
        "viết quảng cáo", "viết content", "story", "poem", "script",
    ]
    if match_keywords(text, creative_phrases):
        techniques.append(TECH_CREATIVE)

    # --------------------------------------
    # 2. Nhận diện loại nhiệm vụ chính
    # Ưu tiên ý định chính thay vì chỉ dựa vào
    # sự xuất hiện của một từ khóa chuyên ngành.
    # --------------------------------------
    meta_phrases = [
        "viết prompt", "tạo prompt", "meta prompt", "prompt engineering",
        "cải thiện prompt", "tối ưu prompt", "đánh giá prompt", "chấm điểm prompt",
    ]
    creative_main_phrases = [
        "viết truyện", "làm thơ", "sáng tác", "viết bài văn", "viết kịch bản",
    ]
    image_phrases = [
        "vẽ ảnh", "tạo ảnh", "midjourney", "stable diffusion", "dall-e", "bức tranh",
    ]
    table_phrases = [
        "dạng bảng", "tạo bảng", "lập bảng", "excel", "markdown table",
    ]
    stem_phrases = [
        "toán", "vật lý", "hóa học", "phương trình", "tích phân", "thuật toán",
        "python", "javascript", "c++", "java", "lập trình", "viết code", "debug code",
    ]
    template_phrases = [
        "mẫu sau", "theo mẫu", "template", "điền vào chỗ trống",
    ]
    
    # Phân loại theo thứ tự ưu tiên.
    if match_keywords(text, meta_phrases):
        main_task = TYPE_PROMPT_META
    elif match_keywords(text, creative_main_phrases):
        main_task = TYPE_CREATIVE
    elif match_keywords(text, image_phrases):
        main_task = TYPE_IMAGE
    elif match_keywords(text, table_phrases):
        main_task = TYPE_TABLE
    # Template được ưu tiên trước STEM để tránh phân loại
    # nhầm yêu cầu "điền vào mẫu phương trình" thành STEM
    # chỉ vì có từ chuyên ngành.
    elif match_keywords(text, template_phrases):
        main_task = TYPE_TEMPLATE
    elif match_keywords(text, stem_phrases):
        main_task = TYPE_STEM
    else:
        main_task = TYPE_PROMPT

    # Loại bỏ kỹ thuật trùng lặp, giữ nguyên thứ tự.
    techniques = list(dict.fromkeys(techniques))
    
    return {
        "main_task": main_task,
        "techniques": techniques,
    }