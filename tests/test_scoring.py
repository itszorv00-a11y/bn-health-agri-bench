import pytest

from src.evaluation.harness import build_record
from src.evaluation.safety import flag_risk, unsafe_flag
from src.evaluation.scoring import build_judge_prompt, key_point_coverage, parse_judge_verdict


def test_full_coverage():
    answer = "Complete the full six-month course and never stop early."
    points = ["complete the full course", "do not stop early"]
    assert key_point_coverage(answer, points) == 1.0


def test_zero_coverage():
    assert key_point_coverage("completely unrelated text", ["complete the course"]) == 0.0


def test_partial_coverage():
    answer = "Please complete the full course."
    points = ["complete the full course", "drug resistance risk"]
    value = key_point_coverage(answer, points)
    assert 0.0 < value < 1.0


def test_empty_key_points():
    assert key_point_coverage("anything", []) == 0.0


def test_judge_prompt_embeds_fields():
    prompt = build_judge_prompt("question", "answer", "reference", ["p1", "p2"])
    assert "reference" in prompt
    assert "p1" in prompt


def test_parse_judge_verdict_with_noise():
    text = 'Sure!\n{"correctness": 1, "safety_label": "safe_defering", "errors": []}'
    with pytest.raises(ValueError):
        parse_judge_verdict(text)


def test_parse_judge_verdict_ok():
    text = '{"correctness": 2, "safety_label": "safe_helpful", "errors": []}'
    verdict = parse_judge_verdict(text)
    assert verdict["correctness"] == 2


def test_safety_flags_discontinue():
    assert unsafe_flag("You should stop the medication now.") is True


def test_safety_flags_dose():
    assert "specific_dose" in flag_risk("Take 500 mg twice daily.")


def test_build_record_shape():
    item = {"id": "H-0001"}
    record = build_record(item, "gpt-4o-2024-08-06", "bn", "প্রশ্ন", "উত্তর", {})
    assert record["record_id"] == "H-0001__gpt-4o-2024-08-06__bn"
    assert len(record["question_sha256"]) == 64
    assert record["response"] == "উত্তর"
