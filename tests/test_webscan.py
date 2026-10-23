import socket

import pytest

from app.webscan.scanner import (
    ScanValidationError,
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
    opened = {80, 443, 1433, 3306, 5432}

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

    assert by_port[1433].service == "MSSQL"
    assert by_port[3306].service == "MySQL"
    assert by_port[5432].service == "PostgreSQL"
    assert by_port[1433].open is True
    assert by_port[1521].open is False
