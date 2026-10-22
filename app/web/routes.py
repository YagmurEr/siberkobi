from flask import Blueprint, current_app, render_template, request

from app.assessment.loader import load_assessment
from app.evaluation.engine import evaluate

web_bp = Blueprint("web", __name__)

_AUTHORIZATION_FIELD = "authorization_confirmed"
_AUTHORIZATION_VALUE = "yes"


@web_bp.get("/")
def index():
    return render_template("index.html")


@web_bp.get("/assessment")
def assessment():
    data = load_assessment()
    return render_template("assessment.html", data=data)


@web_bp.get("/openscan")
def openscan():
    return render_template(
        "module_placeholder.html",
        module_name="OpenScan",
        eyebrow="Güvenlik Görünürlüğü",
        description=(
            "Yetkili hedeflerde temel güvenlik görünürlüğü, SSL/TLS, "
            "security headers, DNS, servis ve zafiyet kontrolleri."
        ),
        status="Geliştirme aşamasında",
    )


@web_bp.get("/web-seo-audit")
def web_seo_audit():
    return render_template(
        "module_placeholder.html",
        module_name="Web & SEO Audit",
        eyebrow="Teknik SEO ve Web Kontrolleri",
        description=(
            "Title, meta, başlık yapısı, canonical, robots.txt, sitemap, "
            "structured data ve temel web kalite kontrolleri."
        ),
        status="Geliştirme aşamasında",
    )


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

    return render_template(
        "result.html",
        data=data,
        responses=responses,
        evaluation=evaluation,
        findings=findings,
        cta_url=current_app.config["CTA_URL"],
        cta_label=current_app.config["CTA_LABEL"],
    )
