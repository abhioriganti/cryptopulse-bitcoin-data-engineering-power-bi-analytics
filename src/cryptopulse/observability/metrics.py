"""Prometheus metrics shared by the CryptoPulse HTTP service."""

from time import perf_counter

from prometheus_client import Counter, Gauge, Histogram

API_REQUESTS = Counter(
    "cryptopulse_api_requests_total",
    "HTTP requests completed by route and status.",
    ("method", "route", "status"),
)
API_LATENCY_SECONDS = Histogram(
    "cryptopulse_api_request_duration_seconds",
    "HTTP request duration by route.",
    ("method", "route"),
)
SERVING_STORE_UP = Gauge(
    "cryptopulse_serving_store_up", "Whether the PostgreSQL serving store was reachable."
)


def observe_request(method: str, route: str, status: int, started_at: float) -> None:
    """Record a completed HTTP request without capturing query values or user data."""
    API_REQUESTS.labels(method=method, route=route, status=str(status)).inc()
    API_LATENCY_SECONDS.labels(method=method, route=route).observe(perf_counter() - started_at)
