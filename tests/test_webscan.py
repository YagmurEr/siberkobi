import socket

import pytest

from app.webscan.scanner import (
    ScanValidationError,
    detect_web_technologies,
    evaluate_headers,
    normalize_target,
    resolve_public_ips,
    scan_web_ports,
)


def test_normalize_target_accepts_domain_and_url() -> None:
    assert normalize_target("Example.COM") == "example.com"
    assert normalize_target("https://example.com/path") == "example.com"


@pytest.mark.parametrize("value", ["", "localhost", "intranet", "bad host.example"])
def test_normalize_target_rejects_invalid_targets(value: str) -> None:
    with pytest.raises(ScanValidationError):
        normalize_target(value)


def test_resolve_public_ips_rejects_private_resolution(monkeypatch) -> None:
    def fake_getaddrinfo(*args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    with pytest.raises(ScanValidationError):
        resolve_public_ips("example.com")


def test_evaluate_headers_marks_missing_controls() -> None:
    results = evaluate_headers({"x-content-type-options": "nosniff"}, https=True)
    by_name = {item["control"]: item for item in results}

    assert by_name["X-Content-Type-Options"]["present"] is True
    assert by_name["Content-Security-Policy"]["present"] is False


def test_scan_web_ports_includes_database_ports(monkeypatch) -> None:
    opened = {53, 80, 443, 1433, 2375, 3000, 3306, 3389, 5432, 6379, 9200}

    class FakeSocket:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_connection(address, timeout):
        if address[1] in opened:
            return FakeSocket()
        raise OSError("closed")

    monkeypatch.setattr(socket, "create_connection", fake_connection)
    results = scan_web_ports("example.com")
    by_port = {item.port: item for item in results}

    assert by_port[53].service == "DNS"
    assert by_port[1433].service == "MSSQL"
    assert by_port[2375].service == "Docker API"
    assert by_port[3000].service == "Grafana / Web App"
    assert by_port[3389].service == "RDP"
    assert by_port[6379].service == "Redis"
    assert by_port[9200].service == "Elasticsearch"
    assert by_port[1433].category == "Veritabanı"
    assert by_port[3389].category == "Windows / Uzak yönetim"
    assert by_port[1433].open is True
    assert by_port[1521].open is False


def test_free_webscan_port_set_is_bounded() -> None:
    from app.webscan.scanner import WEB_PORTS

    assert len(WEB_PORTS) == 31
    assert 67 not in WEB_PORTS
    assert 68 not in WEB_PORTS


def test_detect_web_technologies_from_html_and_headers() -> None:
    technologies = detect_web_technologies(
        {
            "ok": True,
            "headers": {
                "server": "LiteSpeed",
                "x-powered-by": "PHP/8.3",
                "cf-ray": "abc123",
            },
            "body": '<html><link href="/wp-content/theme.css"></html>',
        }
    )
    by_name = {item["name"]: item for item in technologies}

    assert "WordPress" in by_name
    assert "LiteSpeed" in by_name
    assert "PHP" in by_name
    assert "Cloudflare" in by_name
    assert by_name["WordPress"]["guidance"]
