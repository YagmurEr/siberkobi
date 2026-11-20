"""Small per-process scan admission guard; deploy a shared proxy limit for multi-worker setups."""
from collections import deque
from threading import BoundedSemaphore, Lock
from time import monotonic

from flask import current_app, g, request

SCAN_PATHS = frozenset({"/openscan/sonuc", "/web-seo-audit/sonuc"})


class ScanAdmission:
    def __init__(self, *, limit: int = 5, window_seconds: int = 60, concurrency: int = 2):
        self.limit = limit
        self.window_seconds = window_seconds
        self.events: dict[str, deque[float]] = {}
        self.lock = Lock()
        self.semaphore = BoundedSemaphore(concurrency)

    def admit(self, address: str) -> str | None:
        now = monotonic()
        with self.lock:
            # Keep memory bounded under many unique requesting addresses.
            if len(self.events) >= 10_000:
                expired = [
                    key for key, timestamps in self.events.items()
                    if not timestamps or timestamps[-1] <= now - self.window_seconds
                ]
                for key in expired:
                    del self.events[key]
                if len(self.events) >= 10_000 and address not in self.events:
                    return "busy"
            timestamps = self.events.setdefault(address, deque())
            while timestamps and timestamps[0] <= now - self.window_seconds:
                timestamps.popleft()
            if len(timestamps) >= self.limit:
                return "rate"
            if not self.semaphore.acquire(blocking=False):
                return "busy"
            timestamps.append(now)
        return None

    def release(self) -> None:
        self.semaphore.release()


def check_scan_admission():
    if request.method != "POST" or request.path not in SCAN_PATHS:
        return None
    guard: ScanAdmission = current_app.extensions["siberkobi_scan_guard"]
    # Do not trust X-Forwarded-For from untrusted clients.
    address = request.remote_addr or "unknown"
    failure = guard.admit(address)
    if failure:
        from flask import make_response
        status = 429 if failure == "rate" else 503
        message = (
            "Çok sık analiz isteği gönderildi. Daha sonra tekrar deneyin."
            if failure == "rate"
            else "Analiz kapasitesi dolu. Daha sonra tekrar deneyin."
        )
        response = make_response(message, status)
        response.headers["Retry-After"] = "60" if failure == "rate" else "10"
        return response
    g.siberkobi_scan_slot_held = True
    return None


def release_scan_admission(response):
    if getattr(g, "siberkobi_scan_slot_held", False):
        current_app.extensions["siberkobi_scan_guard"].release()
        g.siberkobi_scan_slot_held = False
    return response
