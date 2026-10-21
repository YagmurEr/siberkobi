from flask import Flask


def create_app() -> Flask:
    """Application factory for SiberKOBİ."""
    app = Flask(__name__)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
