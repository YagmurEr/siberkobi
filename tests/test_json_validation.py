"""JSON contract checks, including duplicate keys and invalid assessment data."""
import json

import pytest

from scripts.validate_json import no_duplicate_keys, validate_json_file


def test_valid_assessment_json(tmp_path):
    from app.assessment.loader import load_assessment

    target = tmp_path / "questions.json"
    target.write_text(json.dumps(load_assessment(), ensure_ascii=False), encoding="utf-8")
    validate_json_file(target)


def test_duplicate_json_keys_rejected(tmp_path):
    target = tmp_path / "questions.json"
    target.write_text('{"questions": [], "questions": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON property"):
        validate_json_file(target)


def test_malformed_json_rejected(tmp_path):
    target = tmp_path / "questions.json"
    target.write_text('{"questions":', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        validate_json_file(target)


def test_invalid_assessment_contract_rejected(tmp_path):
    target = tmp_path / "questions.json"
    target.write_text('{"questions": [], "categories": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="25 questions"):
        validate_json_file(target)


def test_duplicate_object_hook():
    with pytest.raises(ValueError, match="Duplicate JSON property"):
        no_duplicate_keys([("id", 1), ("id", 2)])
