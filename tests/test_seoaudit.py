from app.seoaudit.audit import _SEOParser, normalize_url, run_seo_audit


def test_parser_extracts_core_seo_fields() -> None:
    parser = _SEOParser()
    parser.feed(
        """
        <html><head>
          <title>Example Site</title>
          <meta name="description" content="Example description">
          <meta name="viewport" content="width=device-width">
          <meta property="og:title" content="OG title">
          <link rel="canonical" href="https://example.com/">
          <script type="application/ld+json">{}</script>
        </head>
        <body>
          <h1>Main</h1><h2>Section</h2>
          <img src="a.jpg" alt="A">
          <img src="b.jpg">
          <a href="/about">About</a>
        </body></html>
        """
    )

    assert parser.title == "Example Site"
    assert parser.meta["description"] == "Example description"
    assert parser.canonical == "https://example.com/"
    assert parser.headings["h1"] == ["Main"]
    assert parser.images_total == 2
    assert parser.images_missing_alt == 1
    assert parser.json_ld_count == 1


def test_normalize_url_defaults_to_https(monkeypatch) -> None:
    monkeypatch.setattr("app.seoaudit.audit.resolve_public_ips", lambda host: ["93.184.216.34"])
    assert normalize_url("example.com/path") == "https://example.com/path"


def test_run_seo_audit_builds_findings(monkeypatch) -> None:
    html = b"<html><head><title>X</title></head><body><img src='a.jpg'></body></html>"

    def fake_fetch(url, **kwargs):
        if kwargs.get("method") == "HEAD":
            return {
                "url": url,
                "final_url": url,
                "status": 200,
                "reason": "OK",
                "headers": {},
                "body": b"",
                "elapsed_ms": 20,
            }
        return {
            "url": url,
            "final_url": "https://example.com/",
            "status": 200,
            "reason": "OK",
            "headers": {"content-type": "text/html; charset=utf-8"},
            "body": html,
            "elapsed_ms": 120,
        }

    monkeypatch.setattr("app.seoaudit.audit.normalize_url", lambda raw: "https://example.com/")
    monkeypatch.setattr("app.seoaudit.audit.fetch_url", fake_fetch)
    monkeypatch.setattr(
        "app.seoaudit.audit._fetch_optional",
        lambda base, path: {"ok": False, "status": 404, "url": base + path, "text": ""},
    )

    report = run_seo_audit("example.com")

    titles = {item["title"] for item in report["findings"]}
    assert "H1 başlığı yok" in titles
    assert "Meta description yok" in titles
    assert "Canonical etiketi yok" in titles
    assert report["images_missing_alt"] == 1
