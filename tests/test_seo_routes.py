from app import create_app


def test_seo_form_renders() -> None:
    client = create_app().test_client()
    response = client.get("/web-seo-audit")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "SEO Analiz" in body
    assert 'name="target"' in body
    assert 'name="authorization_confirmed"' in body


def test_seo_rejects_missing_authorization() -> None:
    client = create_app().test_client()
    response = client.post("/web-seo-audit/sonuc", data={"target": "example.com"})

    assert response.status_code == 400
    assert "yetkili olduğunuzu onaylayın" in response.get_data(as_text=True)


def test_seo_renders_report(monkeypatch) -> None:
    fake = {
        "target": "https://example.com/",
        "final_url": "https://example.com/",
        "status": 200,
        "elapsed_ms": 120,
        "content_length": 1000,
        "title": "Example",
        "title_length": 7,
        "description": "Description",
        "description_length": 11,
        "headings": {"h1": ["Main"], "h2": ["Section"]},
        "canonical": "https://example.com/",
        "viewport": "width=device-width",
        "robots_meta": "index,follow",
        "robots_meta_status": "Özel robots direktifi tanımlı",
        "analytics": {"detected": True, "status": "Google Analytics / Tag Manager etiketi tespit edildi"},
        "robots": {"ok": True, "status": 200},
        "sitemap": {"ok": True, "status": 200},
        "og": {"title": "OG", "description": "OG desc"},
        "twitter_card": "summary",
        "json_ld_count": 1,
        "images_total": 2,
        "images_missing_alt": 0,
        "links_checked": [{"url": "https://example.com/about", "status": 200, "broken": False}],
        "findings": [],
        "summary": {"findings_total": 0, "high": 0, "medium": 0, "info": 0, "broken_links": 0},
    }

    monkeypatch.setattr("app.web.routes.run_seo_audit", lambda target: fake)
    client = create_app().test_client()
    response = client.post(
        "/web-seo-audit/sonuc",
        data={"target": "example.com", "authorization_confirmed": "yes"},
    )

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "https://example.com/" in body
    assert "JSON-LD" in body
    assert response.headers["Cache-Control"] == "no-store"
