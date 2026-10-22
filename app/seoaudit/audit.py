from __future__ import annotations

import html
import time
from html.parser import HTMLParser
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urljoin, urlsplit

from app.webscan.scanner import ScanValidationError, normalize_target, resolve_public_ips

MAX_BODY_BYTES = 1_000_000
MAX_REDIRECTS = 3
MAX_LINK_CHECKS = 12
USER_AGENT = "SiberKOBI-SEOAnaliz/0.2"


class _SEOParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str | None = None
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.headings: dict[str, list[str]] = {"h1": [], "h2": []}
        self._heading: str | None = None
        self.links: list[str] = []
        self.images_total = 0
        self.images_missing_alt = 0
        self.canonical: str | None = None
        self.json_ld_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        data = {k.lower(): (v or "") for k, v in attrs}

        if tag == "title":
            self._in_title = True
        elif tag in {"h1", "h2"}:
            self._heading = tag
        elif tag == "meta":
            key = (data.get("name") or data.get("property") or "").lower()
            if key:
                self.meta[key] = data.get("content", "").strip()
        elif tag == "link":
            rel = data.get("rel", "").lower().split()
            href = data.get("href", "").strip()
            if "canonical" in rel and href:
                self.canonical = href
        elif tag == "a":
            href = data.get("href", "").strip()
            if href:
                self.links.append(href)
        elif tag == "img":
            self.images_total += 1
            if not data.get("alt", "").strip():
                self.images_missing_alt += 1
        elif tag == "script":
            if data.get("type", "").lower() == "application/ld+json":
                self.json_ld_count += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        if tag == self._heading:
            self._heading = None

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if not value:
            return
        if self._in_title:
            self.title = f"{self.title or ''} {value}".strip()
        elif self._heading:
            self.headings[self._heading].append(value)


def normalize_url(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        raise ScanValidationError("Hedef URL boş olamaz.")

    if "://" not in value:
        value = f"https://{value}"

    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        raise ScanValidationError("Yalnızca http ve https URL'leri desteklenir.")

    host = normalize_target(parsed.hostname or "")
    resolve_public_ips(host)

    path = parsed.path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{parsed.scheme}://{host}{path}{query}"


def _safe_url(url: str) -> tuple[str, str, int, str]:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ScanValidationError("Desteklenmeyen URL şeması.")

    host = normalize_target(parsed.hostname or "")
    resolve_public_ips(host)

    default_port = 443 if parsed.scheme == "https" else 80
    port = parsed.port or default_port
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return parsed.scheme, host, port, path


def fetch_url(
    url: str,
    *,
    method: str = "GET",
    timeout: float = 4.0,
    redirects_left: int = MAX_REDIRECTS,
) -> dict:
    scheme, host, port, path = _safe_url(url)
    connection_cls = HTTPSConnection if scheme == "https" else HTTPConnection
    conn = connection_cls(host=host, port=port, timeout=timeout)

    started = time.monotonic()
    try:
        conn.request(
            method,
            path,
            headers={
                "Host": host,
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                "Connection": "close",
            },
        )
        response = conn.getresponse()
        elapsed_ms = round((time.monotonic() - started) * 1000, 2)
        headers = {k.lower(): v for k, v in response.getheaders()}

        if response.status in {301, 302, 303, 307, 308} and headers.get("location"):
            if redirects_left <= 0:
                raise ScanValidationError("Çok fazla yönlendirme tespit edildi.")
            redirected = urljoin(url, headers["location"])
            response.read(0)
            return fetch_url(
                redirected,
                method=method,
                timeout=timeout,
                redirects_left=redirects_left - 1,
            )

        body = b""
        if method != "HEAD":
            body = response.read(MAX_BODY_BYTES + 1)
            if len(body) > MAX_BODY_BYTES:
                body = body[:MAX_BODY_BYTES]

        return {
            "url": url,
            "final_url": f"{scheme}://{host}{path}",
            "status": response.status,
            "reason": response.reason,
            "headers": headers,
            "body": body,
            "elapsed_ms": elapsed_ms,
        }
    except OSError as exc:
        raise ScanValidationError(f"URL alınamadı: {type(exc).__name__}") from exc
    finally:
        conn.close()


def _decode_body(payload: dict) -> str:
    content_type = payload["headers"].get("content-type", "")
    charset = "utf-8"
    for part in content_type.split(";")[1:]:
        if "charset=" in part.lower():
            charset = part.split("=", 1)[1].strip().strip('"') or "utf-8"
            break
    try:
        return payload["body"].decode(charset, errors="replace")
    except LookupError:
        return payload["body"].decode("utf-8", errors="replace")


def _fetch_optional(base_url: str, path: str) -> dict:
    target = urljoin(base_url, path)
    try:
        response = fetch_url(target)
        return {
            "ok": 200 <= response["status"] < 400,
            "status": response["status"],
            "url": target,
            "text": _decode_body(response)[:100_000],
        }
    except ScanValidationError:
        return {"ok": False, "status": None, "url": target, "text": ""}


def _check_links(base_url: str, links: list[str]) -> list[dict]:
    base_host = normalize_target(urlsplit(base_url).hostname or "")
    candidates: list[str] = []
    seen: set[str] = set()

    for raw in links:
        if raw.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(base_url, raw)
        parsed = urlsplit(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        try:
            host = normalize_target(parsed.hostname or "")
        except ScanValidationError:
            continue
        if host != base_host:
            continue
        clean = absolute.split("#", 1)[0]
        if clean not in seen:
            seen.add(clean)
            candidates.append(clean)
        if len(candidates) >= MAX_LINK_CHECKS:
            break

    results = []
    for url in candidates:
        try:
            response = fetch_url(url, method="HEAD", timeout=3.0, redirects_left=2)
            status = response["status"]
        except ScanValidationError:
            status = None
        results.append(
            {
                "url": url,
                "status": status,
                "broken": status is None or status >= 400,
            }
        )
    return results


def _finding(severity: str, title: str, detail: str) -> dict:
    return {"severity": severity, "title": title, "detail": detail}


def run_seo_audit(raw_target: str) -> dict:
    start_url = normalize_url(raw_target)
    page = fetch_url(start_url)
    html_text = _decode_body(page)

    parser = _SEOParser()
    parser.feed(html_text)

    final_url = page["final_url"]
    title = html.unescape(parser.title or "").strip()
    description = parser.meta.get("description", "")
    viewport = parser.meta.get("viewport", "")
    robots_meta = parser.meta.get("robots", "")
    og_title = parser.meta.get("og:title", "")
    og_description = parser.meta.get("og:description", "")
    twitter_card = parser.meta.get("twitter:card", "")

    robots = _fetch_optional(final_url, "/robots.txt")
    sitemap = _fetch_optional(final_url, "/sitemap.xml")
    links = _check_links(final_url, parser.links)

    findings: list[dict] = []

    if not title:
        findings.append(_finding("high", "Title etiketi yok", "Ana sayfada title etiketi bulunamadı."))
    elif not 30 <= len(title) <= 65:
        findings.append(
            _finding(
                "medium",
                "Title uzunluğu iyileştirilebilir",
                f"Title uzunluğu {len(title)} karakter. Genellikle 30–65 karakter aralığı daha kullanışlıdır.",
            )
        )

    if not description:
        findings.append(
            _finding("medium", "Meta description yok", "Ana sayfada meta description bulunamadı.")
        )
    elif not 70 <= len(description) <= 170:
        findings.append(
            _finding(
                "info",
                "Meta description uzunluğu gözden geçirilmeli",
                f"Description uzunluğu {len(description)} karakter.",
            )
        )

    if len(parser.headings["h1"]) == 0:
        findings.append(_finding("high", "H1 başlığı yok", "Sayfada H1 etiketi bulunamadı."))
    elif len(parser.headings["h1"]) > 1:
        findings.append(
            _finding(
                "medium",
                "Birden fazla H1 var",
                f"Sayfada {len(parser.headings['h1'])} adet H1 etiketi bulundu.",
            )
        )

    if not parser.canonical:
        findings.append(
            _finding("medium", "Canonical etiketi yok", "Ana sayfada canonical link bulunamadı.")
        )

    if not viewport:
        findings.append(
            _finding("medium", "Viewport meta etiketi yok", "Mobil görünüm için viewport bulunamadı.")
        )

    if not robots["ok"]:
        findings.append(
            _finding(
                "medium",
                "robots.txt erişilemiyor",
                "Kök dizinde erişilebilir bir robots.txt bulunamadı.",
            )
        )

    if not sitemap["ok"]:
        findings.append(
            _finding(
                "medium",
                "sitemap.xml erişilemiyor",
                "Kök dizinde erişilebilir bir sitemap.xml bulunamadı.",
            )
        )

    if parser.images_missing_alt:
        findings.append(
            _finding(
                "medium",
                "Alt metni eksik görseller var",
                f"{parser.images_missing_alt}/{parser.images_total} görselde alt metni bulunamadı.",
            )
        )

    if not og_title or not og_description:
        findings.append(
            _finding(
                "info",
                "Open Graph alanları eksik",
                "og:title veya og:description alanlarından en az biri bulunamadı.",
            )
        )

    if not twitter_card:
        findings.append(
            _finding("info", "Twitter/X card meta etiketi yok", "twitter:card bulunamadı.")
        )

    if parser.json_ld_count == 0:
        findings.append(
            _finding("info", "JSON-LD bulunamadı", "Sayfada application/ld+json script'i bulunamadı.")
        )

    broken_links = [item for item in links if item["broken"]]
    if broken_links:
        findings.append(
            _finding(
                "medium",
                "Kontrol edilen iç bağlantılarda hata var",
                f"Sınırlı örneklemde {len(broken_links)} bağlantı 4xx/5xx veya bağlantı hatası verdi.",
            )
        )

    content_length = len(page["body"])
    if page["elapsed_ms"] > 1500:
        findings.append(
            _finding(
                "info",
                "Ana sayfa yanıt süresi yüksek",
                f"İlk HTTP yanıtı yaklaşık {page['elapsed_ms']} ms sürdü.",
            )
        )

    summary = {
        "findings_total": len(findings),
        "high": sum(1 for item in findings if item["severity"] == "high"),
        "medium": sum(1 for item in findings if item["severity"] == "medium"),
        "info": sum(1 for item in findings if item["severity"] == "info"),
        "broken_links": len(broken_links),
    }

    return {
        "target": start_url,
        "final_url": final_url,
        "status": page["status"],
        "elapsed_ms": page["elapsed_ms"],
        "content_length": content_length,
        "title": title,
        "title_length": len(title),
        "description": description,
        "description_length": len(description),
        "headings": parser.headings,
        "canonical": parser.canonical,
        "viewport": viewport,
        "robots_meta": robots_meta,
        "robots": robots,
        "sitemap": sitemap,
        "og": {
            "title": og_title,
            "description": og_description,
        },
        "twitter_card": twitter_card,
        "json_ld_count": parser.json_ld_count,
        "images_total": parser.images_total,
        "images_missing_alt": parser.images_missing_alt,
        "links_checked": links,
        "findings": findings,
        "summary": summary,
    }
