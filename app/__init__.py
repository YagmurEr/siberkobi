import logging
import time

from flask import Flask, g, request

from app.web.routes import web_bp


def create_app() -> Flask:
    """Application factory for SiberKOBİ."""
    app = Flask(__name__)
    app.config.from_mapping(
        CTA_URL="https://eclipta.tr",
        CTA_LABEL="Eclipta ile detaylı değerlendirme",
    )

    app.register_blueprint(web_bp)

    @app.before_request
    def start_request_timer() -> None:
        g.siberkobi_started_at = time.monotonic()

    @app.after_request
    def apply_response_controls(response):
        started_at = getattr(g, "siberkobi_started_at", None)
        duration_ms = (
            round((time.monotonic() - started_at) * 1000, 2)
            if started_at is not None
            else None
        )

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self'; "
            "script-src 'self'; "
            "img-src 'self' data:; "
            "base-uri 'self'; "
            "frame-ancestors 'none'"
        )

        if request.path == "/sonuc":
            response.headers["Cache-Control"] = "no-store"

        app.logger.info(
            "request_completed method=%s path=%s status=%s duration_ms=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    if not app.debug:
        app.logger.setLevel(logging.INFO)

    return app
