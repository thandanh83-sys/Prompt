import pytest
from classifier import (
    TYPE_EMPTY,
    TYPE_PROMPT,
    TYPE_PROMPT_META,
    TYPE_TEMPLATE,
    classify,
    explain,
    has_prompt_meta_keywords,
    has_template_markers,
    is_empty,
)


def test_empty_string_is_empty():
    assert is_empty("") is True


def test_whitespace_is_empty():
    assert is_empty("   \n\t") is True


def test_normal_text_is_not_empty():
    assert is_empty("Xin chào") is False


def test_none_is_empty():
    assert is_empty(None) is True


def test_classify_empty_returns_empty_type():
    assert classify("") == TYPE_EMPTY


def test_classify_whitespace_returns_empty_type():
    assert classify("   ") == TYPE_EMPTY


def test_classify_simple_prompt():
    assert classify("Viết đoạn văn ngắn về mẹ.") == TYPE_PROMPT


def test_classify_prompt_meta_by_keyword():
    text = "Hãy đánh giá prompt sau: viết văn về mẹ."
    assert classify(text) == TYPE_PROMPT_META


def test_classify_template_by_marker():
    text = "Viết văn về [điền chủ đề] với độ dài 500 từ."
    assert classify(text) == TYPE_TEMPLATE


def test_classify_template_marker_detection():
    assert has_template_markers("[điền chủ đề]") is True
    assert has_template_markers("không có gì đặc biệt") is False


def test_classify_prompt_meta_detection():
    assert has_prompt_meta_keywords("chấm điểm prompt này") is True
    assert has_prompt_meta_keywords("viết văn tả mẹ") is False


def test_prompt_meta_takes_priority_over_template():
    # Có cả từ khóa meta và dấu hiệu template: ưu tiên meta.
    text = |
| Kh "Đánh giá prompt sau: [điền chủ đề]"
    assert classify(text) == TYPE_PROMPT_META


def test_explain_returns_reasoning():
    result = explain("Viết văn tả mẹ")
    assert result["type"] == TYPE_PROMPT
    assert result["is_empty"] is False
    assert result["has_template_markers"] is False
    assert result["has_meta_keywords"] is False


def test_classify_non_string_returns_empty():
    assert classify(None) == TYPE_EMPTY
    assert classify(123) == TYPE_EMPTY
