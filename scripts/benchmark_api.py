"""Measure local API latency and write a timestamped benchmark artifact."""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import httpx


def percentile(values: list[float], percentile_value: float) -> float:
    """Return a nearest-rank percentile from an already measured sample."""
    if not values:
        raise ValueError("at least one measured latency is required")
    rank = max(0, min(len(values) - 1, round((len(values) - 1) * percentile_value)))
    return sorted(values)[rank]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000/health")
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    args = parser.parse_args()
    if args.requests < 1:
        raise SystemExit("--requests must be positive")
    latencies_ms: list[float] = []
    with httpx.Client(timeout=args.timeout_seconds) as client:
        for _ in range(args.requests):
            started_at = perf_counter()
            response = client.get(args.url)
            response.raise_for_status()
            latencies_ms.append((perf_counter() - started_at) * 1_000)
    report = {
        "measured_at": datetime.now(UTC).isoformat(),
        "target": args.url,
        "requests": args.requests,
        "latency_ms": {
            "min": min(latencies_ms),
            "mean": sum(latencies_ms) / len(latencies_ms),
            "p50": percentile(latencies_ms, 0.50),
            "p95": percentile(latencies_ms, 0.95),
            "max": max(latencies_ms),
        },
    }
    output_dir = Path("artifacts/benchmarks")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"api-latency-{datetime.now(UTC):%Y%m%dT%H%M%SZ}.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"benchmark_artifact": str(output), **report}, indent=2))


if __name__ == "__main__":
    main()
