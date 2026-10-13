import pytest
from classifier import (
    TYPE_PROMPT,
    TYPE_TEMPLATE,
    TYPE_PROMPT_META,
)
from scorer import (
    CRITERIA_PROMPT,
    CRITERIA_TEMPLATE,
    CRITERIA_PROMPT_META,
    calculate_score,
    check_weights,
    get_criteria,
    round_score,
)


def test_prompt_weights_sum_to_ten():
    assert check_weights(CRITERIA_PROMPT) is True


def test_template_weights_sum_to_ten():
    assert check_weights(CRITERIA_TEMPLATE) is True


def test_prompt_meta_weights_sum_to_ten():
    assert check_weights(CRITERIA_PROMPT_META) is True


def test_get_criteria_prompt():
    assert get_criteria(TYPE_PROMPT) == CRITERIA_PROMPT


def test_get_criteria_unknown_returns_empty():
    assert get_criteria("KHÔNG TỒN TẠI") == {}


def test_round_score_up():
    assert round_score(8.45) == 8.5


def test_round_score_down():
    assert round_score(8.44) == 8.4


def test_round_score_integer():
    assert round_score(7.0) == 7.0


def test_round_score_half():
    assert round_score(8.5) == 8.5


def test_calculate_score_all_ten():
    scores = {name: 10 for name in CRITERIA_PROMPT}
    result = calculate_score(scores, TYPE_PROMPT)
    assert result["score"] == 10.0
    assert result["applicable_count"] == 14


def test_calculate_score_all_zero():
    scores = {name: 0 for name in CRITERIA_PROMPT}
    result = calculate_score(scores, TYPE_PROMPT)
    assert result["score"] == 0.0


def test_calculate_score_skips_none():
    scores = {name: 10 for name in CRITERIA_PROMPT}
    scores["Bối cảnh"] = None
    result = calculate_score(scores, TYPE_PROMPT)
    # Loại Bối cảnh khỏi tử số và mẫu số.
    assert result["score"] == 10.0
    assert result["applicable_count"] == 13
    assert "Bối cảnh" in result["skipped"]


def test_calculate_score_no_applicable():
    scores = {name: None for name in CRITERIA_PROMPT}
    result = calculate_score(scores, TYPE_PROMPT)
    assert result["score"] is None
    assert result["applicable_count"] == 0


def test_calculate_score_rejects_out_of_range():
    scores = {name: 5 for name in CRITERIA_PROMPT}
    scores["Bối cảnh"] = 11
    with pytest.raises(ValueError):
        calculate_score(scores, TYPE_PROMPT)


def test_calculate_score_rejects_invalid_type():
    scores = {name: 5 for name in CRITERIA_PROMPT}
    scores["Bối cảnh"] = "tốt"
    with pytest.raises(TypeError):
        calculate_score(scores, TYPE_PROMPT)


def test_calculate_score_template_works():
    scores = {name: 8 for name in CRITERIA_TEMPLATE}
    result = calculate_score(scores, TYPE_TEMPLATE)
    assert result["score"] == 8.0
    assert result["applicable_count"] == 9
