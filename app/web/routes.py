from flask import Blueprint, current_app, render_template, request

from app.assessment.loader import load_assessment
from app.evaluation.engine import evaluate

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def index():
    data = load_assessment()
    return render_template("assessment.html", data=data)


@web_bp.post("/sonuc")
def result():
    data = load_assessment()
    responses = {
        question["id"]: request.form.get(question["id"], "")
        for question in data["questions"]
    }

    try:
        evaluation = evaluate(responses)
    except ValueError as exc:
        return (
            render_template(
                "assessment.html",
                data=data,
                error=str(exc),
                previous=responses,
            ),
            400,
        )

    findings = [
        {
            "id": question["id"],
            "text": question["text"],
            "response": responses[question["id"]],
        }
        for question in data["questions"]
        if responses[question["id"]] in {"hayir", "kismen"}
    ]

    return render_template(
        "result.html",
        data=data,
        responses=responses,
        evaluation=evaluation,
        findings=findings,
        cta_url=current_app.config["CTA_URL"],
        cta_label=current_app.config["CTA_LABEL"],
    )
