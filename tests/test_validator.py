import pytest

import rules_v38
from validator import (
    ReportValidationError,
    calculate_final_score,
    validate_full_report,
)


def _valid_report(prompt, main, tech=None):
    criteria = {**main, **(tech or {})}
    return {
        "scores": {key: 8 for key in criteria},
        "errors": [],
        "rewrite": {section: "Nội dung mẫu" for section in rules_v38.REQUIRED_REWRITE_SECTIONS},
    }


def test_rules_and_validator_are_separate_modules():
    assert hasattr(rules_v38, "classify_prompt")
    assert hasattr(rules_v38, "CRITERIA_PROMPT")
    assert hasattr(rules_v38, "REQUIRED_REWRITE_SECTIONS")
    assert hasattr(__import__("validator"), "validate_full_report")


def test_table_request_uses_shared_prompt_criteria():
    result = rules_v38.classify_prompt("Hãy tạo bảng so sánh hai phương án")
    assert result["main_task"] == rules_v38.TYPE_PROMPT
    criteria = rules_v38.get_criteria_by_type(result)
    assert criteria["main"] == rules_v38.CRITERIA_PROMPT


def test_non_string_prompt_is_treated_as_empty():
    assert rules_v38.classify_prompt(None)["main_task"] == rules_v38.TYPE_EMPTY


def test_rewrite_requires_exact_order_and_all_eleven_sections():
    main = {"P01": {"name": "Task", "weight": 1.0, "rubric": "test"}}
    report = _valid_report("Viết tóm tắt", main)
    validate_full_report(report, main, {}, "Viết tóm tắt")
    report["rewrite"] = dict(reversed(list(report["rewrite"].items())))
    with pytest.raises(ReportValidationError):
        validate_full_report(report, main, {}, "Viết tóm tắt")


def test_evidence_must_be_found_in_original_prompt():
    main = {"P01": {"name": "Task", "weight": 1.0, "rubric": "test"}}
    report = _valid_report("Viết tóm tắt", main)
    report["errors"] = [{"code": "C02", "evidence": "Toàn bộ prompt"}]
    with pytest.raises(ReportValidationError):
        validate_full_report(report, main, {}, "Viết tóm tắt")


def test_score_uses_one_global_weighted_average():
    main = {
        "P01": {"name": "Main", "weight": 1.0, "rubric": "test"},
    }
    tech = {
        "R01": {"name": "Technique", "weight": 3.0, "rubric": "test"},
    }
    # (10*1 + 0*3) / (1+3) = 2.5; there is no separate 60/40 blend.
    assert calculate_final_score({"P01": 10, "R01": 0}, main, tech) == 2.5


def test_score_rejects_missing_criteria():
    main = {"P01": {"name": "Main", "weight": 1.0, "rubric": "test"}}
    with pytest.raises(ReportValidationError):
        calculate_final_score({}, main, {})
