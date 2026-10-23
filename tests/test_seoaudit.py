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


def test_findings_include_deterministic_guidance(monkeypatch) -> None:
    html = b"<html><head><title>X</title></head><body><h1>A</h1><h1>B</h1></body></html>"

    def fake_fetch(url, **kwargs):
        return {
            "url": url,
            "final_url": "https://example.com/",
            "status": 200,
            "reason": "OK",
            "headers": {"content-type": "text/html; charset=utf-8"},
            "body": html if kwargs.get("method") != "HEAD" else b"",
            "elapsed_ms": 120,
        }

    monkeypatch.setattr("app.seoaudit.audit.normalize_url", lambda raw: "https://example.com/")
    monkeypatch.setattr("app.seoaudit.audit.fetch_url", fake_fetch)
    monkeypatch.setattr(
        "app.seoaudit.audit._fetch_optional",
        lambda base, path: {"ok": True, "status": 200, "url": base + path, "text": ""},
    )

    report = run_seo_audit("example.com")
    finding = next(item for item in report["findings"] if item["title"] == "Birden fazla H1 var")

    assert finding["why"]
    assert finding["fix"]
    assert report["robots_meta_status"].startswith("Normal")
    assert report["analytics"]["detected"] is False


def test_ga4_gtm_and_h1_page_evidence(monkeypatch) -> None:
    root = b"""
    <html><head>
      <title>Example Site With A Useful Descriptive Title</title>
      <meta name="description" content="This is a sufficiently descriptive example meta description for the page and the test case.">
      <meta name="viewport" content="width=device-width">
      <link rel="canonical" href="https://example.com/">
      <script src="https://www.googletagmanager.com/gtag/js?id=G-ABC12345"></script>
      <script>window.dataLayer=window.dataLayer||[]; gtag('config','G-ABC12345');</script>
    </head><body>
      <h1>Main</h1>
      <a href="/about">About</a>
    </body></html>
    """
    about = b"<html><head><title>About Example Company</title></head><body><h1>About</h1><h1>Team</h1></body></html>"

    def fake_fetch(url, **kwargs):
        body = about if "/about" in url else root
        return {
            "url": url,
            "final_url": url,
            "status": 200,
            "reason": "OK",
            "headers": {"content-type": "text/html; charset=utf-8"},
            "body": b"" if kwargs.get("method") == "HEAD" else body,
            "elapsed_ms": 80,
        }

    monkeypatch.setattr("app.seoaudit.audit.normalize_url", lambda raw: "https://example.com/")
    monkeypatch.setattr("app.seoaudit.audit.fetch_url", fake_fetch)
    monkeypatch.setattr(
        "app.seoaudit.audit._fetch_optional",
        lambda base, path: {"ok": True, "status": 200, "url": base + path, "text": ""},
    )

    report = run_seo_audit("example.com")

    assert report["analytics"]["detected"] is True
    assert "G-ABC12345" in report["analytics"]["ga4_ids"]
    about_page = next(item for item in report["page_structure"] if "/about" in item["url"])
    assert about_page["h1_count"] == 2
    titles = {item["title"] for item in report["findings"]}
    assert "H1 yapısı örnekleminde sorun var" in titles
