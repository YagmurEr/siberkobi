from dataclasses import dataclass
from typing import Mapping

from app.assessment.loader import load_assessment, question_map

VALID_RESPONSES = {"evet", "kismen", "hayir", "uygulanamaz"}


@dataclass(frozen=True)
class EvaluationResult:
    earned_points: int
    maximum_points: int
    percentage: float
    band: str
    answered: int
    not_applicable: int
    by_category: dict[str, dict[str, float | int]]


def _band_for(percentage: float) -> str:
    if percentage <= 33.33:
        return "Temel güvenlik kontrolleri geliştirilmeli"
    if percentage <= 66.66:
        return "Güvenlik hazırlığı kısmen sağlanmış"
    return "Temel güvenlik kontrollerinde olumlu görünüm"


def evaluate(responses: Mapping[str, str]) -> EvaluationResult:
    data = load_assessment()
    qmap = question_map()
    expected = set(qmap)

    if set(responses) != expected:
        missing = sorted(expected - set(responses))
        extra = sorted(set(responses) - expected)
        raise ValueError(f"Eksik veya bilinmeyen soru yanıtı: missing={missing}, extra={extra}")

    values = data["response_values"]
    earned = 0
    maximum = 0
    na_count = 0
    category_scores: dict[str, dict[str, int]] = {
        category["id"]: {"earned": 0, "maximum": 0}
        for category in data["categories"]
    }

    for question_id, response in responses.items():
        if response not in VALID_RESPONSES:
            raise ValueError(f"Geçersiz yanıt: {question_id}={response}")

        question = qmap[question_id]
        category = question["category"]

        if response == "uygulanamaz":
            if not question["allow_na"]:
                raise ValueError(f"Uygulanamaz seçeneğine izin verilmiyor: {question_id}")
            na_count += 1
            continue

        points = int(values[response])
        earned += points
        maximum += 2
        category_scores[category]["earned"] += points
        category_scores[category]["maximum"] += 2

    if maximum <= 0:
        raise ValueError("Değerlendirilebilir soru bulunamadı")

    percentage = round((earned / maximum) * 100, 2)
    by_category: dict[str, dict[str, float | int]] = {}
    for category in data["categories"]:
        cid = category["id"]
        score = category_scores[cid]
        cat_max = score["maximum"]
        cat_pct = round((score["earned"] / cat_max) * 100, 2) if cat_max else 0.0
        by_category[cid] = {
            "earned": score["earned"],
            "maximum": cat_max,
            "percentage": cat_pct,
        }

    return EvaluationResult(
        earned_points=earned,
        maximum_points=maximum,
        percentage=percentage,
        band=_band_for(percentage),
        answered=len(responses) - na_count,
        not_applicable=na_count,
        by_category=by_category,
    )
