from app import create_app


def test_web_analysis_form_renders() -> None:
    client = create_app().test_client()
    response = client.get("/openscan")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Web Analiz" in body
    assert 'name="target"' in body
    assert 'name="authorization_confirmed"' in body


def test_web_analysis_rejects_missing_authorization() -> None:
    client = create_app().test_client()
    response = client.post("/openscan/sonuc", data={"target": "example.com"})

    assert response.status_code == 400
    assert "yetkili olduğunuzu onaylayın" in response.get_data(as_text=True)


def test_web_analysis_renders_report(monkeypatch) -> None:
    client = create_app().test_client()

    fake_report = {
        "target": "example.com",
        "resolved_ips": ["93.184.216.34"],
        "ports": [
            {"port": 80, "open": True, "service": "HTTP"},
            {"port": 443, "open": True, "service": "HTTPS"},
            {"port": 8080, "open": False, "service": "HTTP-alt"},
            {"port": 8443, "open": False, "service": "HTTPS-alt"},
        ],
        "http": {"ok": True, "status": 301, "reason": "Moved", "headers": {}},
        "https": {"ok": True, "status": 200, "reason": "OK", "headers": {}},
        "tls": {
            "ok": True,
            "version": "TLSv1.3",
            "cipher": "TLS_AES_256_GCM_SHA384",
            "subject_cn": "example.com",
            "issuer_cn": "Example CA",
            "days_remaining": 80,
        },
        "findings": [],
        "cve": {"status": "not_evaluated", "reason": "CVE doğrulanmadı."},
        "kev": {"status": "not_evaluated", "reason": "KEV doğrulanmadı."},
        "summary": {
            "open_web_ports": 2,
            "findings_total": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "info": 0,
        },
    }

    monkeypatch.setattr("app.web.routes.run_web_analysis", lambda target: fake_report)

    response = client.post(
        "/openscan/sonuc",
        data={"target": "example.com", "authorization_confirmed": "yes"},
    )

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "93.184.216.34" in body
    assert "TLSv1.3" in body
    assert "CVE doğrulanmadı." in body
    assert response.headers["Cache-Control"] == "no-store"
