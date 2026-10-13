
"""Kiểm tra và chuẩn hóa đầu vào cho Prompt Evaluator v38."""

MAX_CODE_POINTS = 5000


def count_code_points(text: str) -> int:
    """Đếm số code point Unicode."""
    if not isinstance(text, str):
        raise TypeError("text phải là chuỗi str")
    return len(text)


def normalize(text: str) -> str:
    """Loại khoảng trắng ở hai đầu."""
    if not isinstance(text, str):
        raise TypeError("text phải là chuỗi str")
    return text.strip()


def smart_truncate(
    text: str,
    limit: int = MAX_CODE_POINTS,
) -> str:
    """Cắt tại ranh giới khoảng trắng gần nhất phía trước."""
    if not isinstance(text, str):
        raise TypeError("text phải là chuỗi str")

    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit phải là số nguyên")

    if limit < 0:
        raise ValueError("limit không được âm")

    if len(text) <= limit:
        return text

    if limit == 0:
        return ""

    prefix = text[:limit]

    if prefix[-1].isspace():
        return prefix.rstrip()

    boundary = max(
        prefix.rfind(" "),
        prefix.rfind("\t"),
        prefix.rfind("\n"),
        prefix.rfind("\r"),
        prefix.rfind("\v"),
        prefix.rfind("\f"),
    )

    if boundary == -1:
        # MVP: chưa tìm được ranh giới phù hợp.
        # Cần xem xét thêm theo đặc tả v38.
        return prefix

    return prefix[:boundary].rstrip()


def truncate_code_points(
    text: str,
    limit: int = MAX_CODE_POINTS,
) -> str:
    """Giữ hàm cắt cũ để tương thích."""
    if not isinstance(text, str):
        raise TypeError("text phải là chuỗi str")

    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit phải là số nguyên")

    if limit < 0:
        raise ValueError("limit không được âm")

    return text[:limit]


def prepare_input(
    prompt: str,
    limit: int = MAX_CODE_POINTS,
) -> dict:
    """Chuẩn bị dữ liệu và ghi nhận phạm vi nội dung."""
    if not isinstance(prompt, str):
        raise TypeError("prompt phải là chuỗi str")

    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit phải là số nguyên")

    if limit < 0:
        raise ValueError("limit không được âm")

    normalized = normalize(prompt)
    n = count_code_points(normalized)

    if n > limit:
        processed = smart_truncate(normalized, limit)
    else:
        processed = normalized

    m = count_code_points(processed)

    return {
        "original": prompt,
        "normalized": normalized,
        "processed": processed,
        "N": n,
        "M": m,
        "truncated": n > limit,
        "scope": f"1-{m}" if n > limit else f"1-{n}",
    }


def validate_input(prompt: str) -> list[str]:
    """Kiểm tra đầu vào; chưa quyết định điều kiện chấm."""
    if not isinstance(prompt, str):
        return ["Đầu vào phải là văn bản."]

    if not normalize(prompt):
        return ["Prompt không được để trống."]

    return []
