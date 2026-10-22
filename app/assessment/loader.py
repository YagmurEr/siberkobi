import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_FILE = Path(__file__).with_name("questions.json")
_EXPECTED_IDS = [f"SK-T{i:02d}" for i in range(1, 26)]
_EXPECTED_CATEGORY_IDS = ["A", "B", "C", "D", "E"]
_EXPECTED_RESPONSE_VALUES = {"evet": 2, "kismen": 1, "hayir": 0}


def _validate_assessment(data: dict[str, Any]) -> None:
    questions = data.get("questions")
    categories = data.get("categories")
    if not isinstance(questions, list) or len(questions) != 25:
        raise ValueError("Assessment must contain exactly 25 questions.")
    if not isinstance(categories, list) or len(categories) != 5:
        raise ValueError("Assessment must contain exactly 5 categories.")

    question_ids = [item.get("id") for item in questions]
    if question_ids != _EXPECTED_IDS:
        raise ValueError("Assessment question IDs must be SK-T01 through SK-T25 in order.")
    if len(set(question_ids)) != len(question_ids):
        raise ValueError("Assessment question IDs must be unique.")

    category_ids = [item.get("id") for item in categories]
    if category_ids != _EXPECTED_CATEGORY_IDS:
        raise ValueError("Assessment category IDs must be A through E in order.")

    if data.get("response_values") != _EXPECTED_RESPONSE_VALUES:
        raise ValueError("Assessment response scoring does not match the approved model.")

    allowed_na = set(data.get("na_allowed", []))
    declared_na = {item["id"] for item in questions if item.get("allow_na") is True}
    if allowed_na != declared_na:
        raise ValueError("na_allowed must match question-level allow_na declarations.")

    question_id_set = set(question_ids)
    category_question_ids: list[str] = []
    for category in categories:
        category_questions = category.get("questions")
        if not isinstance(category_questions, list):
            raise ValueError("Each category must list its question IDs.")
        category_question_ids.extend(category_questions)

    if category_question_ids != question_ids:
        raise ValueError("Category question ordering must match the approved question ordering.")

    valid_category_ids = set(category_ids)
    for question in questions:
        if question.get("category") not in valid_category_ids:
            raise ValueError(f"Unknown category for {question['id']}.")
        if not isinstance(question.get("text"), str) or not question["text"].strip():
            raise ValueError(f"Question text is required for {question['id']}.")
        if not isinstance(question.get("allow_na"), bool):
            raise ValueError(f"allow_na must be boolean for {question['id']}.")

    if set(category_question_ids) != question_id_set:
        raise ValueError("Categories must reference every assessment question exactly once.")


@lru_cache(maxsize=1)
def load_assessment() -> dict[str, Any]:
    with _DATA_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    _validate_assessment(data)
    return data


def question_map() -> dict[str, dict[str, Any]]:
    data = load_assessment()
    return {item["id"]: item for item in data["questions"]}
