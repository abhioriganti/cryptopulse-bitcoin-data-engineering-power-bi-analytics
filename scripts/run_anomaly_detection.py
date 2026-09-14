"""Detect statistically unusual BTC returns from curated market bars."""

import argparse
from datetime import datetime
from uuid import uuid4

import psycopg

from cryptopulse.anomalies.persistence import persist_anomalies
from cryptopulse.anomalies.rolling_zscore import detect_rolling_zscore
from cryptopulse.common.config import get_settings


def simple_returns(bars: list[tuple[datetime, float]]) -> list[tuple[datetime, float]]:
    """Calculate returns at each timestamp from the preceding bar only."""
    return [
        (timestamp, (close - previous_close) / previous_close)
        for (_, previous_close), (timestamp, close) in zip(bars, bars[1:], strict=False)
        if previous_close != 0
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=3.0)
    args = parser.parse_args()
    settings = get_settings()
    with psycopg.connect(str(settings.postgres_dsn)) as connection:
        with connection.cursor() as cursor:
            cursor.execute("select bar_start, close from raw.market_bars order by bar_start")
            bars = [(row[0], float(row[1])) for row in cursor.fetchall()]
        anomalies = detect_rolling_zscore(simple_returns(bars), args.window, args.threshold)
        persisted = persist_anomalies(connection, uuid4(), anomalies)
    print(f"statistical_anomalies={persisted} window={args.window} threshold={args.threshold}")


if __name__ == "__main__":
    main()
