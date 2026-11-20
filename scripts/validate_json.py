"""Validate tracked application JSON inputs before packaging or deployment."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.assessment.loader import _validate_assessment
JSON_PATHS = (ROOT / "app" / "assessment" / "questions.json",)


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON property: {key}")
        result[key] = value
    return result


def validate_json_file(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle, object_pairs_hook=no_duplicate_keys)
    if path.name == "questions.json":
        if not isinstance(payload, dict):
            raise ValueError("Assessment JSON root must be an object")
        _validate_assessment(payload)


def main() -> int:
    for path in JSON_PATHS:
        if not path.is_file():
            raise FileNotFoundError(f"Required dataset missing: {path}")
        validate_json_file(path)
        print(f"Validated: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
