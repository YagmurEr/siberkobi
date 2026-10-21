import pytest

from app.assessment.loader import load_assessment
from app.evaluation.engine import evaluate


def _responses(value: str = "evet") -> dict[str, str]:
    return {q["id"]: value for q in load_assessment()["questions"]}


def test_all_yes_is_100_percent() -> None:
    result = evaluate(_responses("evet"))
    assert result.earned_points == 50
    assert result.maximum_points == 50
    assert result.percentage == 100.0
    assert result.band == "Temel güvenlik kontrollerinde olumlu görünüm"


def test_all_no_is_zero_percent() -> None:
    result = evaluate(_responses("hayir"))
    assert result.percentage == 0.0
    assert result.band == "Temel güvenlik kontrolleri geliştirilmeli"


def test_not_applicable_is_excluded_from_maximum() -> None:
    responses = _responses("evet")
    responses["SK-T01"] = "uygulanamaz"
    result = evaluate(responses)
    assert result.earned_points == 48
    assert result.maximum_points == 48
    assert result.percentage == 100.0
    assert result.not_applicable == 1


def test_not_applicable_rejected_when_not_allowed() -> None:
    responses = _responses("evet")
    responses["SK-T02"] = "uygulanamaz"
    with pytest.raises(ValueError):
        evaluate(responses)


def test_missing_response_is_rejected() -> None:
    responses = _responses("evet")
    responses.pop("SK-T25")
    with pytest.raises(ValueError):
        evaluate(responses)


def test_invalid_response_is_rejected() -> None:
    responses = _responses("evet")
    responses["SK-T25"] = "belki"
    with pytest.raises(ValueError):
        evaluate(responses)
