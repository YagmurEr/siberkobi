from __future__ import annotations

import ipaddress
import socket
import ssl
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlsplit

WEB_PORTS = (
    22, 53, 80, 88, 135, 139, 389, 443, 445, 464, 636,
    1433, 1521, 2049, 2375, 2376, 3000, 3306, 3389, 5432,
    5900, 5985, 5986, 6379, 8000, 8080, 8443, 8888, 9200,
    11211, 27017,
)
SECURITY_HEADERS = {
    "strict-transport-security": "HSTS",
    "content-security-policy": "Content-Security-Policy",
    "x-content-type-options": "X-Content-Type-Options",
    "x-frame-options": "X-Frame-Options",
    "referrer-policy": "Referrer-Policy",
    "permissions-policy": "Permissions-Policy",
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


def fetch_http_headers(host: str, use_tls: bool, port: int, timeout: float = 3.0) -> dict:
    connection_cls = HTTPSConnection if use_tls else HTTPConnection
    context = ssl.create_default_context() if use_tls else None
    kwargs = {"host": host, "port": port, "timeout": timeout}
    if use_tls:
        kwargs["context"] = context

    conn = connection_cls(**kwargs)
    try:
        conn.request(
            "HEAD",
            "/",
            headers={
                "Host": host,
                "User-Agent": "SiberKOBI-WebAnaliz/0.2",
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


def build_findings(report: dict) -> list[dict]:
    findings: list[dict] = []

    open_ports = [p["port"] for p in report["ports"] if p["open"]]
    if 80 in open_ports and 443 not in open_ports:
        findings.append(
            {
                "severity": "high",
                "title": "HTTPS servisi görünmüyor",
                "detail": "HTTP erişilebilir ancak 443/TCP kapalı görünüyor.",
            }
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
                {
                    "severity": "high",
                    "title": f"{service} portu internete açık görünüyor",
                    "detail": (
                        f"{port}/TCP erişilebilir. İnternete açık yönetim, dosya paylaşımı "
                        "veya veri servisleri erişim kontrolü açısından gözden geçirilmelidir. "
                        "Bu sonuç ürün/sürüm doğrulaması değildir."
                    ),
                }
            )

    tls = report["tls"]
    if tls.get("ok") and tls.get("days_remaining") is not None:
        days = tls["days_remaining"]
        if days < 0:
            findings.append(
                {
                    "severity": "critical",
                    "title": "TLS sertifikasının süresi dolmuş",
                    "detail": f"Sertifika {abs(days)} gün önce sona ermiş.",
                }
            )
        elif days < 30:
            findings.append(
                {
                    "severity": "high",
                    "title": "TLS sertifikası yakında sona erecek",
                    "detail": f"Sertifikanın bitmesine yaklaşık {days} gün kaldı.",
                }
            )

    https_headers = report["https"].get("headers", {})
    for item in evaluate_headers(https_headers, https=True):
        if not item["present"]:
            findings.append(
                {
                    "severity": item["severity"],
                    "title": f"{item['control']} başlığı bulunamadı",
                    "detail": "Yanıt üzerinde bu güvenlik başlığı görülmedi.",
                }
            )

    server = https_headers.get("server") or report["http"].get("headers", {}).get("server")
    if server:
        findings.append(
            {
                "severity": "info",
                "title": "Sunucu bilgisi yanıt başlığında görünüyor",
                "detail": f"Server: {server}",
            }
        )

    return findings


def run_web_analysis(raw_target: str) -> dict:
    host = normalize_target(raw_target)
    ips = resolve_public_ips(host)
    ports = [asdict(item) for item in scan_web_ports(host)]

    http = fetch_http_headers(host, use_tls=False, port=80)
    https = fetch_http_headers(host, use_tls=True, port=443)
    tls = inspect_tls(host)

    report = {
        "target": host,
        "resolved_ips": ips,
        "ports": ports,
        "http": http,
        "https": https,
        "tls": tls,
        "cve": {
            "status": "not_evaluated",
            "reason": (
                "CVE eşleştirmesi yalnız güvenilir ürün+sürüm kanıtı varsa yapılır. "
                "Sadece port veya Server başlığı CVE kanıtı sayılmaz."
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
        "critical": sum(1 for f in report["findings"] if f["severity"] == "critical"),
        "high": sum(1 for f in report["findings"] if f["severity"] == "high"),
        "medium": sum(1 for f in report["findings"] if f["severity"] == "medium"),
        "info": sum(1 for f in report["findings"] if f["severity"] == "info"),
    }
    return report
