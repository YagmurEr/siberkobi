import copy

import pytest

from app.assessment.loader import _validate_assessment, load_assessment


def test_assessment_dataset_is_valid() -> None:
    _validate_assessment(load_assessment())


def test_assessment_requires_exact_question_ids() -> None:
    data = copy.deepcopy(load_assessment())
    data["questions"][0]["id"] = "SK-T99"

    with pytest.raises(ValueError):
        _validate_assessment(data)


def test_assessment_na_configuration_must_match_questions() -> None:
    data = copy.deepcopy(load_assessment())
    data["na_allowed"] = ["SK-T01"]

    with pytest.raises(ValueError):
        _validate_assessment(data)


def test_assessment_scoring_model_is_fixed() -> None:
    data = copy.deepcopy(load_assessment())
    data["response_values"]["evet"] = 3

    with pytest.raises(ValueError):
        _validate_assessment(data)
