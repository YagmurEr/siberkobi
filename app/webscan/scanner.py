from __future__ import annotations

import ipaddress
import re
import socket
import ssl
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlsplit

WEB_PORTS = (
    22,
    53,
    80,
    88,
    135,
    139,
    389,
    443,
    445,
    464,
    636,
    1433,
    1521,
    2049,
    2375,
    2376,
    3000,
    3306,
    3389,
    5432,
    5900,
    5985,
    5986,
    6379,
    8000,
    8080,
    8443,
    8888,
    9200,
    11211,
    27017,
)
MAX_WEB_BODY_BYTES = 300_000
SECURITY_HEADERS = {
    "strict-transport-security": "HSTS",
    "content-security-policy": "Content-Security-Policy",
    "x-content-type-options": "X-Content-Type-Options",
    "x-frame-options": "X-Frame-Options",
    "referrer-policy": "Referrer-Policy",
    "permissions-policy": "Permissions-Policy",
}

HEADER_GUIDANCE = {
    "HSTS": (
        "HTTPS kullanan sitelerde tarayıcının sonraki bağlantıları yalnız HTTPS üzerinden yapmasına yardımcı olur.",
        "HTTPS tüm sitede zorunluysa Strict-Transport-Security başlığını uygun max-age değeriyle etkinleştirin.",
    ),
    "Content-Security-Policy": (
        "CSP, tarayıcıda hangi kaynakların çalıştırılabileceğini sınırlandırarak XSS etkisini azaltmaya yardımcı olur.",
        "Uygulamanıza uygun, test edilmiş bir Content-Security-Policy tanımlayın ve gereksiz geniş izinlerden kaçının.",
    ),
    "X-Content-Type-Options": (
        "Tarayıcının içerik türünü tahmin etmesini sınırlandırarak bazı içerik yorumlama risklerini azaltır.",
        "Yanıtlara X-Content-Type-Options: nosniff başlığını ekleyin.",
    ),
    "X-Frame-Options": (
        "Sayfanın başka sitelerde iframe içinde açılmasını kısıtlayarak clickjacking riskini azaltabilir.",
        "İhtiyacınıza göre X-Frame-Options: DENY veya SAMEORIGIN kullanın; modern uygulamalarda CSP frame-ancestors da değerlendirilmelidir.",
    ),
    "Referrer-Policy": (
        "Başka sitelere geçişte hangi yönlendiren URL bilgisinin gönderileceğini sınırlar.",
        "İş ihtiyacınıza uygun bir Referrer-Policy belirleyin; strict-origin-when-cross-origin yaygın bir başlangıç seçeneğidir.",
    ),
    "Permissions-Policy": (
        "Kamera, mikrofon ve konum gibi tarayıcı yeteneklerinin hangi bağlamlarda kullanılabileceğini sınırlar.",
        "Kullanılmayan tarayıcı yeteneklerini Permissions-Policy ile kapatın.",
    ),
}

TECH_GUIDANCE = {
    "WordPress": "WordPress core, tema ve eklentileri desteklenen sürümlerde tutun; kullanılmayan tema ve eklentileri kaldırın.",
    "Drupal": "Drupal core, modül ve temaları desteklenen sürümlerde tutun; güvenlik duyurularını düzenli takip edin.",
    "Joomla": "Joomla core, eklenti ve şablonları güncel tutun; kullanılmayan uzantıları kaldırın.",
    "Shopify": "Platform çekirdeği yönetilen hizmettir; uygulama entegrasyonları, tema bileşenleri ve hesap güvenliğini düzenli gözden geçirin.",
    "Wix": "Platform çekirdeği yönetilen hizmettir; üçüncü taraf uygulamalar, alan adı ayarları ve hesap erişimlerini düzenli gözden geçirin.",
    "Webflow": "Platform çekirdeği yönetilen hizmettir; özel scriptler, form entegrasyonları ve üçüncü taraf bileşenleri gözden geçirin.",
    "Next.js": "Framework ve npm bağımlılıklarını desteklenen sürümlerde tutun; güvenlik güncellemelerini düzenli uygulayın.",
    "Nuxt": "Framework ve npm bağımlılıklarını desteklenen sürümlerde tutun; güvenlik güncellemelerini düzenli uygulayın.",
    "PHP": "Desteklenen PHP ana sürümünü kullanın ve güvenlik güncellemelerini düzenli uygulayın.",
    "LiteSpeed": "Web sunucusunu güncel tutun; gereksiz sürüm/banner bilgisini mümkünse sınırlandırın.",
    "nginx": "Web sunucusunu güncel tutun; gereksiz sürüm/banner bilgisini mümkünse sınırlandırın.",
    "Apache": "Web sunucusunu güncel tutun; gereksiz sürüm/banner bilgisini mümkünse sınırlandırın.",
    "Microsoft IIS": "IIS ve Windows güvenlik güncellemelerini düzenli uygulayın; gereksiz banner bilgisini sınırlandırın.",
    "Cloudflare": "Proxy, TLS, WAF ve erişim kurallarının ihtiyaca uygun yapılandırıldığını düzenli gözden geçirin.",
    "Plesk": "Plesk panelini güncel tutun, yönetim erişimini sınırlandırın ve MFA kullanın.",
}


class ScanValidationError(ValueError):
    pass


@dataclass
class PortResult:
    port: int
    open: bool
    service: str
    category: str


def normalize_target(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        raise ScanValidationError("Hedef alan adı boş olamaz.")

    if "://" in value:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
    else:
        host = value.split("/", 1)[0].split(":", 1)[0]

    host = host.strip().rstrip(".").lower()
    if not host or len(host) > 253:
        raise ScanValidationError("Geçerli bir alan adı girin.")

    if host == "localhost":
        raise ScanValidationError("Localhost hedefleri desteklenmiyor.")

    try:
        ipaddress.ip_address(host)
    except ValueError:
        labels = host.split(".")
        if len(labels) < 2:
            raise ScanValidationError("Tam alan adı girin (ör. example.com).")
        for label in labels:
            if not label or len(label) > 63:
                raise ScanValidationError("Geçerli bir alan adı girin.")
            if label[0] == "-" or label[-1] == "-":
                raise ScanValidationError("Geçerli bir alan adı girin.")
            if not all(ch.isalnum() or ch == "-" for ch in label):
                raise ScanValidationError("Geçerli bir alan adı girin.")

    return host


def resolve_public_ips(host: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise ScanValidationError("Alan adı çözümlenemedi.") from exc

    ips = sorted({item[4][0] for item in infos})
    if not ips:
        raise ScanValidationError("Alan adı için IP adresi bulunamadı.")

    public_ips = []
    for raw_ip in ips:
        ip = ipaddress.ip_address(raw_ip)
        if not ip.is_global:
            raise ScanValidationError(
                "Private, loopback, link-local veya rezerve hedefler Web Analiz ile taranmaz."
            )
        public_ips.append(raw_ip)
    return public_ips


def scan_web_ports(host: str, timeout: float = 1.0) -> list[PortResult]:
    services = {
        22: ("SSH", "Uzak yönetim"),
        53: ("DNS", "Temel altyapı"),
        80: ("HTTP", "Web"),
        88: ("Kerberos", "Windows / Kimlik"),
        135: ("MS RPC", "Windows / Yönetim"),
        139: ("NetBIOS", "Windows / Dosya paylaşımı"),
        389: ("LDAP", "Windows / Kimlik"),
        443: ("HTTPS", "Web"),
        445: ("SMB", "Windows / Dosya paylaşımı"),
        464: ("Kerberos password", "Windows / Kimlik"),
        636: ("LDAPS", "Windows / Kimlik"),
        1433: ("MSSQL", "Veritabanı"),
        1521: ("Oracle DB", "Veritabanı"),
        2049: ("NFS", "Dosya paylaşımı"),
        2375: ("Docker API", "DevOps / Yönetim"),
        2376: ("Docker API TLS", "DevOps / Yönetim"),
        3000: ("Grafana / Web App", "DevOps / Web"),
        3306: ("MySQL", "Veritabanı"),
        3389: ("RDP", "Windows / Uzak yönetim"),
        5432: ("PostgreSQL", "Veritabanı"),
        5900: ("VNC", "Uzak yönetim"),
        5985: ("WinRM HTTP", "Windows / Uzak yönetim"),
        5986: ("WinRM HTTPS", "Windows / Uzak yönetim"),
        6379: ("Redis", "Cache / Veri"),
        8000: ("HTTP-alt", "Web"),
        8080: ("HTTP-alt", "Web"),
        8443: ("HTTPS-alt", "Web"),
        8888: ("HTTP-alt", "Web"),
        9200: ("Elasticsearch", "Arama / Veri"),
        11211: ("Memcached", "Cache / Veri"),
        27017: ("MongoDB", "Veritabanı"),
    }
    results: list[PortResult] = []
    for port in WEB_PORTS:
        opened = False
        try:
            with socket.create_connection((host, port), timeout=timeout):
                opened = True
        except (OSError, TimeoutError):
            opened = False
        service, category = services[port]
        results.append(
            PortResult(port=port, open=opened, service=service, category=category)
        )
    return results


def _connection(host: str, use_tls: bool, port: int, timeout: float):
    if use_tls:
        return HTTPSConnection(
            host=host,
            port=port,
            timeout=timeout,
            context=ssl.create_default_context(),
        )
    return HTTPConnection(host=host, port=port, timeout=timeout)


def fetch_http_headers(host: str, use_tls: bool, port: int, timeout: float = 3.0) -> dict:
    conn = _connection(host, use_tls, port, timeout)
    try:
        conn.request(
            "HEAD",
            "/",
            headers={
                "Host": host,
                "User-Agent": "SiberKOBI-WebAnaliz/0.4",
                "Connection": "close",
            },
        )
        response = conn.getresponse()
        headers = {k.lower(): v for k, v in response.getheaders()}
        return {
            "ok": True,
            "status": response.status,
            "reason": response.reason,
            "headers": headers,
        }
    except (OSError, ssl.SSLError) as exc:
        return {"ok": False, "error": type(exc).__name__, "headers": {}}
    finally:
        conn.close()


def fetch_web_document(
    host: str,
    *,
    use_tls: bool,
    port: int,
    timeout: float = 4.0,
) -> dict:
    conn = _connection(host, use_tls, port, timeout)
    try:
        conn.request(
            "GET",
            "/",
            headers={
                "Host": host,
                "User-Agent": "SiberKOBI-WebAnaliz/0.4",
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                "Connection": "close",
            },
        )
        response = conn.getresponse()
        headers = {k.lower(): v for k, v in response.getheaders()}
        raw = response.read(MAX_WEB_BODY_BYTES)
        content_type = headers.get("content-type", "")
        charset = "utf-8"
        match = re.search(r"charset=([^;\s]+)", content_type, flags=re.IGNORECASE)
        if match:
            charset = match.group(1).strip("\"'")
        try:
            body = raw.decode(charset, errors="replace")
        except LookupError:
            body = raw.decode("utf-8", errors="replace")
        return {
            "ok": True,
            "status": response.status,
            "reason": response.reason,
            "headers": headers,
            "body": body,
        }
    except (OSError, ssl.SSLError) as exc:
        return {
            "ok": False,
            "error": type(exc).__name__,
            "headers": {},
            "body": "",
        }
    finally:
        conn.close()


def _technology_item(
    name: str,
    category: str,
    confidence: str,
    evidence: str,
) -> dict:
    return {
        "name": name,
        "category": category,
        "confidence": confidence,
        "evidence": evidence,
        "guidance": TECH_GUIDANCE.get(name, ""),
    }


def detect_web_technologies(document: dict) -> list[dict]:
    if not document.get("ok"):
        return []

    body = document.get("body", "")
    body_lower = body.lower()
    headers = document.get("headers", {})
    server = headers.get("server", "")
    powered = headers.get("x-powered-by", "")
    cookie = headers.get("set-cookie", "")
    found: list[dict] = []
    names: set[str] = set()

    def add(name: str, category: str, confidence: str, evidence: str) -> None:
        if name in names:
            return
        names.add(name)
        found.append(_technology_item(name, category, confidence, evidence))

    generator_match = re.search(
        r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)',
        body,
        flags=re.IGNORECASE,
    )
    generator = generator_match.group(1) if generator_match else ""

    if any(marker in body_lower for marker in ("wp-content/", "wp-includes/")):
        add("WordPress", "CMS", "yüksek", "HTML içinde wp-content/wp-includes izi")
    elif "wordpress" in generator.lower():
        add("WordPress", "CMS", "yüksek", f"Generator: {generator}")

    if any(
        marker in body_lower
        for marker in ("drupalsettings", "drupal-settings-json", "/sites/default/files/")
    ):
        add("Drupal", "CMS", "yüksek", "HTML içinde Drupal varlık izi")
    elif "drupal" in generator.lower():
        add("Drupal", "CMS", "yüksek", f"Generator: {generator}")

    if any(marker in body_lower for marker in ("option=com_", "/media/system/js/")):
        add("Joomla", "CMS", "yüksek", "HTML içinde Joomla varlık izi")
    elif "joomla" in generator.lower():
        add("Joomla", "CMS", "yüksek", f"Generator: {generator}")

    if any(
        marker in body_lower
        for marker in ("cdn.shopify.com", "shopify.theme", "myshopify.com")
    ):
        add("Shopify", "Yönetilen platform", "yüksek", "HTML içinde Shopify izi")

    if any(
        marker in body_lower
        for marker in ("static.parastorage.com", "wixstatic.com", "wix-code-sdk")
    ):
        add("Wix", "Yönetilen platform", "yüksek", "HTML içinde Wix izi")

    if any(
        marker in body_lower
        for marker in ("assets.website-files.com", "data-wf-page=", "webflow.js")
    ):
        add("Webflow", "Yönetilen platform", "yüksek", "HTML içinde Webflow izi")

    if any(marker in body_lower for marker in ("__next_data__", "/_next/static/")):
        add("Next.js", "Web framework", "yüksek", "HTML içinde Next.js izi")

    if any(marker in body_lower for marker in ("__nuxt__", "/_nuxt/")):
        add("Nuxt", "Web framework", "yüksek", "HTML içinde Nuxt izi")

    if "php" in powered.lower():
        add("PHP", "Uygulama çalışma zamanı", "orta", f"X-Powered-By: {powered}")

    server_lower = server.lower()
    if "litespeed" in server_lower:
        add("LiteSpeed", "Web sunucusu", "yüksek", f"Server: {server}")
    elif "nginx" in server_lower:
        add("nginx", "Web sunucusu", "yüksek", f"Server: {server}")
    elif "apache" in server_lower:
        add("Apache", "Web sunucusu", "yüksek", f"Server: {server}")
    elif "microsoft-iis" in server_lower:
        add("Microsoft IIS", "Web sunucusu", "yüksek", f"Server: {server}")

    if "cloudflare" in server_lower or headers.get("cf-ray"):
        add("Cloudflare", "CDN / Proxy", "yüksek", "Cloudflare yanıt başlığı tespit edildi")

    if "plesk" in powered.lower() or "plesk" in cookie.lower():
        add("Plesk", "Hosting / Yönetim", "orta", "Plesk yanıt izi tespit edildi")

    return found


def inspect_tls(host: str, timeout: float = 3.0) -> dict:
    context = ssl.create_default_context()
    try:
        with (
            socket.create_connection((host, 443), timeout=timeout) as sock,
            context.wrap_socket(sock, server_hostname=host) as tls,
        ):
            cert = tls.getpeercert()
            cipher = tls.cipher()
            not_after = cert.get("notAfter")
            expires_at = None
            days_remaining = None
            if not_after:
                expires_at = datetime.strptime(
                    not_after, "%b %d %H:%M:%S %Y %Z"
                ).replace(tzinfo=UTC)
                days_remaining = (expires_at - datetime.now(UTC)).days

            subject = {}
            for group in cert.get("subject", ()):
                for key, value in group:
                    subject[key] = value

            issuer = {}
            for group in cert.get("issuer", ()):
                for key, value in group:
                    issuer[key] = value

            return {
                "ok": True,
                "version": tls.version(),
                "cipher": cipher[0] if cipher else None,
                "subject_cn": subject.get("commonName"),
                "issuer_cn": issuer.get("commonName"),
                "expires_at": expires_at.isoformat() if expires_at else None,
                "days_remaining": days_remaining,
            }
    except (OSError, ssl.SSLError, ValueError) as exc:
        return {"ok": False, "error": type(exc).__name__}


def evaluate_headers(headers: dict[str, str], https: bool) -> list[dict]:
    findings: list[dict] = []
    for header, display in SECURITY_HEADERS.items():
        present = bool(headers.get(header))
        severity = "info" if present else "medium"
        if header == "strict-transport-security" and not https:
            severity = "info"
        findings.append(
            {
                "control": display,
                "present": present,
                "value": headers.get(header),
                "severity": severity,
            }
        )
    return findings


def _finding(
    severity: str,
    title: str,
    detail: str,
    why: str,
    fix: str,
) -> dict:
    return {
        "severity": severity,
        "title": title,
        "detail": detail,
        "why": why,
        "fix": fix,
    }


def build_findings(report: dict) -> list[dict]:
    findings: list[dict] = []

    open_ports = [p["port"] for p in report["ports"] if p["open"]]
    if 80 in open_ports and 443 not in open_ports:
        findings.append(
            _finding(
                "high",
                "HTTPS servisi görünmüyor",
                "HTTP erişilebilir ancak 443/TCP kapalı görünüyor.",
                "HTTPS, web trafiğinin ağ üzerinde şifrelenmesini sağlar.",
                "Web uygulaması yayınlanıyorsa HTTPS'i etkinleştirin ve HTTP isteklerini HTTPS'e yönlendirin.",
            )
        )

    sensitive_ports = {
        135: "MS RPC",
        139: "NetBIOS",
        389: "LDAP",
        445: "SMB",
        464: "Kerberos password",
        636: "LDAPS",
        1433: "MSSQL",
        1521: "Oracle DB",
        2049: "NFS",
        2375: "Docker API",
        2376: "Docker API TLS",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        5985: "WinRM HTTP",
        5986: "WinRM HTTPS",
        6379: "Redis",
        9200: "Elasticsearch",
        11211: "Memcached",
        27017: "MongoDB",
    }
    for port, service in sensitive_ports.items():
        if port in open_ports:
            findings.append(
                _finding(
                    "high",
                    f"{service} portu internete açık görünüyor",
                    (
                        f"{port}/TCP erişilebilir. Bu sonuç ürün/sürüm doğrulaması "
                        "değildir."
                    ),
                    (
                        "İnternete açık yönetim, dosya paylaşımı veya veri servisleri "
                        "gereksiz saldırı yüzeyi oluşturabilir."
                    ),
                    (
                        "Servisin internetten erişilmesi gerçekten gerekiyorsa erişimi "
                        "kaynak IP, VPN veya güvenli erişim katmanıyla sınırlandırın; "
                        "gerekmiyorsa dış erişimi firewall seviyesinde kapatın."
                    ),
                )
            )

    tls = report["tls"]
    if tls.get("ok") and tls.get("days_remaining") is not None:
        days = tls["days_remaining"]
        if days < 0:
            findings.append(
                _finding(
                    "critical",
                    "TLS sertifikasının süresi dolmuş",
                    f"Sertifika {abs(days)} gün önce sona ermiş.",
                    "Süresi dolmuş sertifika tarayıcı güven uyarılarına ve hizmet güveni kaybına neden olur.",
                    "Sertifikayı yenileyin ve otomatik yenileme/izleme mekanizmasını doğrulayın.",
                )
            )
        elif days < 30:
            findings.append(
                _finding(
                    "high",
                    "TLS sertifikası yakında sona erecek",
                    f"Sertifikanın bitmesine yaklaşık {days} gün kaldı.",
                    "Sertifika süresinin dolması HTTPS hizmetinde güven uyarılarına neden olabilir.",
                    "Sertifika yenilemesini planlayın ve otomatik yenilemenin çalıştığını doğrulayın.",
                )
            )

    https_headers = report["https"].get("headers", {})
    for item in evaluate_headers(https_headers, https=True):
        if not item["present"]:
            why, fix = HEADER_GUIDANCE[item["control"]]
            findings.append(
                _finding(
                    item["severity"],
                    f"{item['control']} başlığı bulunamadı",
                    "Yanıt üzerinde bu güvenlik başlığı görülmedi.",
                    why,
                    fix,
                )
            )

    server = https_headers.get("server") or report["http"].get("headers", {}).get("server")
    if server:
        findings.append(
            _finding(
                "info",
                "Sunucu bilgisi yanıt başlığında görünüyor",
                f"Server: {server}",
                "Banner bilgisi doğrudan zafiyet değildir ancak teknoloji parmak izini kolaylaştırabilir.",
                "İşlevi bozmadan gereksiz ürün/sürüm bilgisini yanıt başlıklarından kaldırmayı değerlendirin.",
            )
        )

    return findings


def run_web_analysis(raw_target: str) -> dict:
    host = normalize_target(raw_target)
    ips = resolve_public_ips(host)
    ports = [asdict(item) for item in scan_web_ports(host)]
    open_ports = {item["port"] for item in ports if item["open"]}

    http = fetch_http_headers(host, use_tls=False, port=80)
    https = fetch_http_headers(host, use_tls=True, port=443)
    tls = inspect_tls(host)

    if 443 in open_ports:
        document = fetch_web_document(host, use_tls=True, port=443)
    elif 80 in open_ports:
        document = fetch_web_document(host, use_tls=False, port=80)
    else:
        document = {"ok": False, "headers": {}, "body": ""}

    technology = detect_web_technologies(document)

    report = {
        "target": host,
        "resolved_ips": ips,
        "ports": ports,
        "http": http,
        "https": https,
        "tls": tls,
        "technology": technology,
        "technology_source_status": document.get("status"),
        "cve": {
            "status": "not_evaluated",
            "reason": (
                "CVE eşleştirmesi yalnız güvenilir ürün+sürüm kanıtı varsa yapılır. "
                "Sadece port, HTML izi veya Server başlığı CVE kanıtı sayılmaz."
            ),
        },
        "kev": {
            "status": "not_evaluated",
            "reason": (
                "CISA KEV kontrolü için önce güvenilir bir CVE eşleşmesi gerekir."
            ),
        },
    }
    report["findings"] = build_findings(report)
    report["summary"] = {
        "open_web_ports": sum(1 for item in ports if item["open"]),
        "findings_total": len(report["findings"]),
        "technology_count": len(technology),
        "critical": sum(
            1 for finding in report["findings"] if finding["severity"] == "critical"
        ),
        "high": sum(
            1 for finding in report["findings"] if finding["severity"] == "high"
        ),
        "medium": sum(
            1 for finding in report["findings"] if finding["severity"] == "medium"
        ),
        "info": sum(
            1 for finding in report["findings"] if finding["severity"] == "info"
        ),
    }
    return report
