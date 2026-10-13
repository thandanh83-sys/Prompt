"""Phân loại prompt cho Prompt Evaluator v38.

Đây là bộ phân loại MVP bằng từ khóa.
Chưa phải phân loại chính thức theo v38.
Sẽ được thay thế bằng model AI ở giai đoạn sau.
"""

from rules_v38 import normalize, count_code_points


# Các loại nội dung theo v38
TYPE_EMPTY = "EMPTY"
TYPE_PROMPT_META = "PROMPT META"
TYPE_TEMPLATE = "TEMPLATE"
TYPE_PROMPT = "PROMPT"


# Từ khóa nhận diện PROMPT META.
# Đây là danh sách gợi ý, không phải điều kiện tuyệt đối.
PROMPT_META_KEYWORDS = (
    "đánh giá prompt",
    "chấm điểm prompt",
    "viết prompt",
    "tạo prompt",
    "sửa prompt",
    "cải thiện prompt",
    "phân tích prompt",
    "linter",
)


# Dấu hiệu placeholder cho TEMPLATE.
# Chỉ xét khi có cấu trúc gợi ý điền, không chỉ vì có ngoặc vuông.
TEMPLATE_MARKERS = (
    "[điền",
    "[thay",
    "[chọn",
    "[nhập",
    "[đặt",
    "___",
)


def is_empty(text: str) -> bool:
    """Trả về True nếu sau khi chuẩn hóa không còn nội dung."""
    if not isinstance(text, str):
        return True
    return count_code_points(normalize(text)) == 0


def has_template_markers(text: str) -> bool:
    """Phát hiện dấu hiệu placeholder cần điền."""
    if not isinstance(text, str):
        return False
    lowered = text.lower()
    return any(marker in lowered for marker in TEMPLATE_MARKERS)


def has_prompt_meta_keywords(text: str) -> bool:
    """Phát hiện từ khóa gợi ý PROMPT META."""
    if not isinstance(text, str):
        return False
    lowered = text.lower()
    return any(keyword in lowered for keyword in PROMPT_META_KEYWORDS)


def classify(prompt: str) -> str:
    """Phân loại prompt thành một trong bốn loại.

    Thứ tự xét:
    1. EMPTY nếu rỗng.
    2. PROMPT META nếu có từ khóa meta.
    3. TEMPLATE nếu có dấu hiệu placeholder.
    4. PROMPT cho mọi trường hợp còn lại.
    """
    if not isinstance(prompt, str):
        return TYPE_EMPTY
    normalized = normalize(prompt)
    if not normalized:
        return TYPE_EMPTY
    if has_prompt_meta_keywords(normalized):
        return TYPE_PROMPT_META
    if has_template_markers(normalized):
        return TYPE_TEMPLATE
    return TYPE_PROMPT


def explain(prompt: str) -> dict:
    """Trả về loại kèm lý do ngắn để dễ debug."""
    result = {
        "type": classify(prompt),
        "is_empty": is_empty(prompt),
        "has_template_markers": has_template_markers(prompt),
        "has_meta_keywords": has_prompt_meta_keywords(prompt),
    }
    return result
