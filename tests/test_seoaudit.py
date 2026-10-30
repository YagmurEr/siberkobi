from app.seoaudit.ai_visibility import evaluate_ai_visibility
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



def test_ai_visibility_respects_bot_specific_robots_rules() -> None:
    robots = {
        "ok": True,
        "text": """
        User-agent: OAI-SearchBot
        Allow: /

        User-agent: GPTBot
        Disallow: /

        User-agent: Googlebot
        Allow: /

        User-agent: Bingbot
        Disallow: /
        """,
    }

    result = evaluate_ai_visibility(
        robots,
        json_ld_count=1,
        h1_count=1,
        h2_count=2,
        paragraph_count=4,
        semantic_tags=["main", "section"],
    )

    assert result["bots"]["OAI-SearchBot"]["status"] == "allowed"
    assert result["bots"]["GPTBot"]["status"] == "blocked"
    assert result["bots"]["Googlebot"]["status"] == "allowed"
    assert result["bots"]["Bingbot"]["status"] == "blocked"
    assert result["status"] == "Uygun"


def test_ai_visibility_marks_unavailable_robots_as_unknown() -> None:
    result = evaluate_ai_visibility(
        {"ok": False, "text": ""},
        json_ld_count=0,
        h1_count=0,
        h2_count=0,
        paragraph_count=0,
        semantic_tags=[],
    )

    assert all(item["status"] == "unknown" for item in result["bots"].values())
    assert result["status"] == "Geliştirilmeli"


def test_run_seo_audit_includes_ai_visibility_and_guidance(monkeypatch) -> None:
    root = b"""
    <html><head>
      <title>Example Site With A Useful Descriptive Title</title>
      <meta name="description" content="This is a sufficiently descriptive example meta description for deterministic SEO testing and analysis.">
      <meta name="viewport" content="width=device-width">
      <link rel="canonical" href="https://example.com/">
      <script type="application/ld+json">{"@context":"https://schema.org"}</script>
    </head><body>
      <main><h1>Main topic</h1><h2>Section</h2>
      <p>First readable paragraph.</p><p>Second readable paragraph.</p></main>
    </body></html>
    """

    def fake_fetch(url, **kwargs):
        return {
            "url": url,
            "final_url": "https://example.com/",
            "status": 200,
            "reason": "OK",
            "headers": {"content-type": "text/html; charset=utf-8"},
            "body": root if kwargs.get("method") != "HEAD" else b"",
            "elapsed_ms": 80,
        }

    def fake_optional(base, path):
        if path == "/robots.txt":
            return {
                "ok": True,
                "status": 200,
                "url": base + path,
                "text": "User-agent: OAI-SearchBot\nDisallow: /\nUser-agent: *\nAllow: /",
            }
        return {"ok": True, "status": 200, "url": base + path, "text": ""}

    monkeypatch.setattr("app.seoaudit.audit.normalize_url", lambda raw: "https://example.com/")
    monkeypatch.setattr("app.seoaudit.audit.fetch_url", fake_fetch)
    monkeypatch.setattr("app.seoaudit.audit._fetch_optional", fake_optional)

    report = run_seo_audit("example.com")

    assert report["ai_visibility"]["bots"]["OAI-SearchBot"]["status"] == "blocked"
    assert report["ai_visibility"]["json_ld_count"] == 1
    assert report["ai_visibility"]["content"]["paragraph_count"] == 2
    assert "main" in report["ai_visibility"]["content"]["semantic_tags"]
    finding = next(
        item for item in report["findings"] if item["title"] == "OAI-SearchBot erişimi engelli"
    )
    assert finding["why"]
    assert finding["fix"]



def test_llms_txt_is_optional_and_does_not_reduce_ai_score() -> None:
    robots = {
        "ok": True,
        "text": """
        User-agent: *
        Allow: /
        """,
    }

    without_llms = evaluate_ai_visibility(
        robots,
        json_ld_count=1,
        h1_count=1,
        h2_count=2,
        paragraph_count=4,
        semantic_tags=["main", "section"],
        llms_txt={"ok": False, "status": 404, "url": "https://example.com/llms.txt", "text": ""},
    )
    with_llms = evaluate_ai_visibility(
        robots,
        json_ld_count=1,
        h1_count=1,
        h2_count=2,
        paragraph_count=4,
        semantic_tags=["main", "section"],
        llms_txt={
            "ok": True,
            "status": 200,
            "url": "https://example.com/llms.txt",
            "text": "# Example\n\n> Site context for LLMs.",
        },
    )

    assert without_llms["score"] == with_llms["score"]
    assert without_llms["maximum"] == with_llms["maximum"] == 10
    assert without_llms["llms_txt"]["status"] == "missing"
    assert with_llms["llms_txt"]["status"] == "present"
    assert with_llms["llms_txt"]["present"] is True


def test_empty_llms_txt_is_not_treated_as_present() -> None:
    result = evaluate_ai_visibility(
        {"ok": True, "text": "User-agent: *\nAllow: /"},
        json_ld_count=1,
        h1_count=1,
        h2_count=1,
        paragraph_count=2,
        semantic_tags=["main"],
        llms_txt={"ok": True, "status": 200, "url": "https://example.com/llms.txt", "text": "   "},
    )

    assert result["llms_txt"]["status"] == "empty"
    assert result["llms_txt"]["present"] is False
