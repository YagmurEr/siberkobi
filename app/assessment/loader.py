import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_FILE = Path(__file__).with_name("questions.json")


@lru_cache(maxsize=1)
def load_assessment() -> dict[str, Any]:
    with _DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def question_map() -> dict[str, dict[str, Any]]:
    data = load_assessment()
    return {item["id"]: item for item in data["questions"]}
