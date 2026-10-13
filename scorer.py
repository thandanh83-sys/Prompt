"""Bộ tiêu chí và tính điểm cho Prompt Evaluator v38.

Scorer KHÔNG tự chấm điểm tiêu chí.
Điểm tiêu chí do AI cung cấp (0-10).
Scorer chỉ áp trọng số, loại N/A và làm tròn.
"""

from classifier import (
    TYPE_PROMPT,
    TYPE_TEMPLATE,
    TYPE_PROMPT_META,
)


# Bộ tiêu chí PROMPT — 14 tiêu chí, tổng trọng số 10
CRITERIA_PROMPT = {
    "Độ rõ nhiệm vụ": 1.2,
    "Đối tượng tác động": 1.2,
    "Bối cảnh": 0.8,
    "Định dạng đầu ra": 0.8,
    "Độ chi tiết và ví dụ": 1.6,
    "Không mơ hồ": 0.2,
    "Không chung chung": 0.2,
    "Có cấu trúc": 0.2,
    "Phù hợp nhiệm vụ": 0.5,
    "Chuyên môn có căn cứ": 0.5,
    "Nhất quán lĩnh vực": 1.0,
    "Yêu cầu khả thi": 0.8,
    "Vai trò phù hợp": 0.8,
    "Không mâu thuẫn": 0.2,
}


# Bộ tiêu chí TEMPLATE — 9 tiêu chí, tổng trọng số 10
CRITERIA_TEMPLATE = {
    "Đủ mục": 1.5,
    "Mục hợp lý": 1.0,
    "Hướng dẫn điền": 1.5,
    "Ví dụ mẫu": 1.0,
    "Phân cấp": 1.0,
    "Quy tắc cấm": 1.0,
    "Quy tắc ưu tiên": 1.0,
    "Quy trình xử lý": 1.0,
    "Chất lượng placeholder": 1.0,
}


# Bộ tiêu chí PROMPT META — 9 tiêu chí, tổng trọng số 10
CRITERIA_PROMPT_META = {
    "Cấu trúc": 1.5,
    "Chi tiết": 2.0,
    "Định dạng": 1.0,
    "Nhất quán": 1.0,
    "Khả thi": 1.0,
    "Vai trò": 0.5,
    "Mở rộng": 1.0,
    "Ứng dụng": 1.0,
    "Quy trình": 1.0,
}


def get_criteria(content_type: str) -> dict:
    """Trả về bộ tiêu chí tương ứng với loại nội dung."""
    if content_type == TYPE_PROMPT:
        return CRITERIA_PROMPT
    if content_type == TYPE_TEMPLATE:
        return CRITERIA_TEMPLATE
    if content_type == TYPE_PROMPT_META:
        return CRITERIA_PROMPT_META
    return {}


def check_weights(criteria: dict) -> bool:
    """Kiểm tra tổng trọng số có bằng 10 hay không."""
    return abs(sum(criteria.values()) - 10.0) < 1e-9


def round_score(value: float) -> float:
    """Làm tròn 1 chữ số thập phân theo quy tắc v38.

    Chữ số thập phân thứ 2 từ 5 trở lên thì tăng chữ số thứ nhất.
    Python round() dùng banker's rounding, không khớp quy tắc này.
    """
    if not isinstance(value, (int, float)):
        raise TypeError("value phải là số")
    # Nhân 10, dùng floor(x + 0.5) để tránh banker's rounding.
    import math
    scaled = value * 10
    rounded = math.floor(scaled + 0.5)
    return rounded / 10


def calculate_score(
    criteria_scores: dict,
    content_type: str,
) -> dict:
    """Tính điểm tổng từ điểm tiêu chí.

    criteria_scores: dict {tên tiêu chí: điểm 0-10 hoặc None}
        None nghĩa là tiêu chí không áp dụng, bị loại khỏi tử số và mẫu số.
    content_type: một trong TYPE_PROMPT, TYPE_TEMPLATE, TYPE_PROMPT_META.
    """
    weights = get_criteria(content_type)
    if not weights:
        raise ValueError(f"Không có bộ tiêu chí cho loại: {content_type}")

    applicable = {}
    for name, score in criteria_scores.items():
        if name not in weights:
            continue
        if score is None:
            continue
        if not isinstance(score, (int, float)):
            raise TypeError(f"Điểm tiêu chí '{name}' phải là số hoặc None")
        if score < 0 or score > 10:
            raise ValueError(f"Điểm tiêu chí '{name}' ngoài miền 0-10: {score}")
        applicable[name] = score

    if not applicable:
        return {
            "score": None,
            "applicable_count": 0,
            "message": "Không có tiêu chí nào áp dụng.",
        }

    numerator = 0.0
    denominator = 0.0
    for name, score in applicable.items():
        weight = weights[name]
        numerator += score * weight
        denominator += weight

    if denominator == 0:
        return {
            "score": None,
            "applicable_count": 0,
            "message": "Tổng trọng số áp dụng bằng 0.",
        }

    raw = numerator / denominator
    final = round_score(raw)

    return {
        "score": final,
        "raw_score": raw,
        "applicable_count": len(applicable),
        "total_criteria": len(weights),
        "skipped": [name for name in weights if name not in applicable],
    }
