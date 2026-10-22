from app import create_app


def test_health_endpoint() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_security_headers_are_present() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_result_page_is_not_cached() -> None:
    app = create_app()
    client = app.test_client()
    data = {f"SK-T{i:02d}": "evet" for i in range(1, 26)}
    data["authorization_confirmed"] = "yes"

    response = client.post("/sonuc", data=data)

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
