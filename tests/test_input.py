
from rules_v38 import (
    MAX_CODE_POINTS,
    count_code_points,
    normalize,
    prepare_input,
    smart_truncate,
    validate_input,
)


def test_empty_input_is_rejected():
    assert validate_input("")


def test_whitespace_input_is_rejected():
    assert validate_input("   \n\t")


def test_normal_input_is_accepted():
    assert validate_input("Hãy đánh giá prompt này.") == []


def test_normalize_removes_whitespace_at_both_ends():
    assert normalize(" \n Xin chào \t ") == "Xin chào"


def test_normalize_preserves_internal_whitespace():
    assert normalize("Xin  chào\nbạn") == "Xin  chào\nbạn"


def test_exact_limit_is_accepted():
    prompt = "a" * MAX_CODE_POINTS
    result = prepare_input(prompt)

    assert count_code_points(prompt) == MAX_CODE_POINTS
    assert result["M"] == MAX_CODE_POINTS


def test_over_limit_is_prepared():
    prompt = "abc " * 1300
    result = prepare_input(prompt)

    assert result["N"] > MAX_CODE_POINTS
    assert result["M"] <= MAX_CODE_POINTS
    assert result["truncated"] is True
    assert result["scope"] == f"1-{result['M']}"


def test_smart_truncate_prefers_previous_word_boundary():
    assert smart_truncate("hello world again", 8) == "hello"


def test_smart_truncate_keeps_short_text():
    assert smart_truncate("Xin chào", 100) == "Xin chào"


def test_smart_truncate_handles_no_space():
    assert smart_truncate("abcdefgh", 4) == "abcd"


def test_smart_truncate_returns_empty_when_boundary_at_start():
    assert smart_truncate(" abc", 3) == ""


def test_unicode_emoji_count():
    assert count_code_points("😀") == 1


def test_combining_character_counts_as_two_code_points():
    assert count_code_points("e\u0301") == 2


def test_negative_limit_is_rejected():
    try:
        smart_truncate("abc", -1)
    except ValueError:
        return

    assert False, "Phải phát sinh ValueError"


def test_non_string_input_is_rejected():
    assert validate_input(None)


def test_original_prompt_is_preserved():
    original = "  Xin chào  "
    result = prepare_input(original)

    assert result["original"] == original
    assert result["normalized"] == "Xin chào"
