from flask import Blueprint, current_app, render_template, request

from app.assessment.guidance import build_grouped_actions
from app.assessment.loader import load_assessment
from app.evaluation.engine import evaluate
from app.seoaudit.audit import run_seo_audit
from app.webscan.scanner import ScanValidationError, run_web_analysis

web_bp = Blueprint("web", __name__)

_AUTHORIZATION_FIELD = "authorization_confirmed"
_AUTHORIZATION_VALUE = "yes"


@web_bp.get("/")
def index():
    return render_template("index.html")


@web_bp.get("/yasal-uyari")
def legal_notice():
    return render_template("legal_notice.html")


@web_bp.get("/assessment")
def assessment():
    data = load_assessment()
    return render_template("assessment.html", data=data)


@web_bp.get("/openscan")
def openscan():
    return render_template("openscan.html")


@web_bp.post("/openscan/sonuc")
def openscan_result():
    target = request.form.get("target", "").strip()

    if request.form.get(_AUTHORIZATION_FIELD) != _AUTHORIZATION_VALUE:
        return (
            render_template(
                "openscan.html",
                error="Devam etmek için bu hedefi değerlendirmeye yetkili olduğunuzu onaylayın.",
                target=target,
            ),
            400,
        )

    try:
        report = run_web_analysis(target)
    except ScanValidationError as exc:
        return render_template("openscan.html", error=str(exc), target=target), 400

    current_app.logger.info(
        "web_analysis_completed target=%s findings=%s",
        report["target"],
        report["summary"]["findings_total"],
    )
    return render_template("openscan_result.html", report=report)


@web_bp.get("/web-seo-audit")
def web_seo_audit():
    return render_template("seo_audit.html")


@web_bp.post("/web-seo-audit/sonuc")
def web_seo_audit_result():
    target = request.form.get("target", "").strip()

    if request.form.get(_AUTHORIZATION_FIELD) != _AUTHORIZATION_VALUE:
        return (
            render_template(
                "seo_audit.html",
                error="Devam etmek için bu siteyi değerlendirmeye yetkili olduğunuzu onaylayın.",
                target=target,
            ),
            400,
        )

    try:
        report = run_seo_audit(target)
    except ScanValidationError as exc:
        return render_template("seo_audit.html", error=str(exc), target=target), 400

    current_app.logger.info(
        "seo_analysis_completed target=%s findings=%s",
        report["final_url"],
        report["summary"]["findings_total"],
    )
    return render_template("seo_audit_result.html", report=report)


@web_bp.post("/sonuc")
def result():
    data = load_assessment()
    responses = {
        question["id"]: request.form.get(question["id"], "")
        for question in data["questions"]
    }

    if request.form.get(_AUTHORIZATION_FIELD) != _AUTHORIZATION_VALUE:
        return (
            render_template(
                "assessment.html",
                data=data,
                error=(
                    "Değerlendirmeye devam etmek için bu aracı kendi kurumunuz, "
                    "sistemleriniz veya değerlendirme yapmaya yetkili olduğunuz "
                    "bir ortam için kullandığınızı onaylamanız gerekir."
                ),
                previous=responses,
                authorization_confirmed=False,
            ),
            400,
        )

    try:
        evaluation = evaluate(responses)
    except ValueError as exc:
        return (
            render_template(
                "assessment.html",
                data=data,
                error=str(exc),
                previous=responses,
                authorization_confirmed=True,
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
    action_groups = build_grouped_actions(data, responses)

    return render_template(
        "result.html",
        data=data,
        responses=responses,
        evaluation=evaluation,
        findings=findings,
        action_groups=action_groups,
        cta_url=current_app.config["CTA_URL"],
        cta_label=current_app.config["CTA_LABEL"],
    )
