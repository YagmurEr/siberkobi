from flask import Flask

from app.web.routes import web_bp


def create_app() -> Flask:
    """Application factory for SiberKOBİ."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev-only-no-session-state",
        CTA_URL="https://eclipta.tr",
        CTA_LABEL="Eclipta ile detaylı değerlendirme",
    )

    app.register_blueprint(web_bp)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
