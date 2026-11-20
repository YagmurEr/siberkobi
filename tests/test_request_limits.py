from app import create_app
from app.request_limits import ScanAdmission


def test_scan_limit_returns_429_without_executing_scan(monkeypatch):
    app = create_app()
    app.extensions["siberkobi_scan_guard"] = ScanAdmission(limit=1)
    called = []
    monkeypatch.setattr("app.web.routes.run_web_analysis", lambda target: called.append(target))
    client = app.test_client()
    # The first request is rejected by authorization, but uses a rate-limit slot.
    first = client.post("/openscan/sonuc", data={"target": "example.com"})
    assert first.status_code == 400
    second = client.post("/openscan/sonuc", data={"target": "example.com", "authorization_confirmed": "yes"})
    assert second.status_code == 429
    assert second.headers["Retry-After"] == "60"
    assert not called


def test_seo_shares_scan_budget():
    app = create_app()
    app.extensions["siberkobi_scan_guard"] = ScanAdmission(limit=1)
    client = app.test_client()
    assert client.post("/openscan/sonuc", data={}).status_code == 400
    assert client.post("/web-seo-audit/sonuc", data={}).status_code == 429


def test_regular_pages_not_rate_limited():
    app = create_app()
    app.extensions["siberkobi_scan_guard"] = ScanAdmission(limit=1)
    client = app.test_client()
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200


def test_concurrency_limit():
    guard = ScanAdmission(limit=10, concurrency=1)
    assert guard.admit("203.0.113.10") is None
    assert guard.admit("203.0.113.11") == "busy"
    guard.release()
    assert guard.admit("203.0.113.11") is None
    guard.release()
