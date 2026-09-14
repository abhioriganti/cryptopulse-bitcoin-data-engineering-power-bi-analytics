"""Finite historical backfill command; streaming is intentionally not orchestrated here."""

import argparse
import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import psycopg

from cryptopulse.common.config import get_settings
from cryptopulse.contracts import MarketEvent
from cryptopulse.ingestion.bronze import BronzeWriter, S3ObjectStore
from cryptopulse.ingestion.coinbase_exchange import CoinbaseExchangeProvider
from cryptopulse.serving.postgres import upsert_market_bars

INTERVAL_DURATIONS = {"1h": timedelta(hours=1)}


def parse_utc_datetime(value: str) -> datetime:
    """Parse an ISO-8601 instant, requiring a timezone to prevent ambiguous backfills."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError(
            "timestamps must include a timezone, e.g. 2024-01-01T00:00:00Z"
        )
    return parsed.astimezone(UTC)


def finalized_bar_rows(events: list[MarketEvent], interval: str) -> list[dict[str, object]]:
    """Map provider OHLCV bars to the idempotent historical serving grain.

    Coinbase REST returns completed source candles, so these are already finalized
    interval bars.  The raw payload remains in Bronze for replay/audit; this path
    only makes the same validated source bars queryable by local dbt and Power BI.
    """
    duration = INTERVAL_DURATIONS[interval]
    return [
        {
            "provider": event.provider,
            "symbol": event.symbol,
            "currency": event.currency,
            "interval": "1 hour",
            "bar_start": event.event_timestamp,
            "bar_end": event.event_timestamp + duration,
            "open": float(event.open),
            "high": float(event.high),
            "low": float(event.low),
            "close": float(event.close),
            "volume": float(event.volume or 0),
            "trade_count": int(event.trade_count or 0),
            "vwap": float(event.close),
        }
        for event in events
    ]


async def run_backfill(
    start: datetime, end: datetime, symbol: str, interval: str, load_serving: bool
) -> None:
    settings = get_settings()
    if end <= start:
        raise ValueError("end must be after start")
    if not settings.s3_access_key or not settings.s3_secret_key:
        raise RuntimeError(
            "CRYPTOPULSE_S3_ACCESS_KEY and CRYPTOPULSE_S3_SECRET_KEY must be configured"
        )
    provider = CoinbaseExchangeProvider(timeout_seconds=settings.provider_timeout_seconds)
    try:
        events = await provider.get_historical_data(symbol, start, end, interval=interval)
    finally:
        await provider.aclose()
    store = S3ObjectStore(
        endpoint_url=str(settings.s3_endpoint),
        bucket=settings.s3_bucket,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
    )
    store.ensure_bucket()
    result = BronzeWriter(store, settings.s3_bucket).write_events(events, run_id=str(uuid4()))
    print(f"backfill complete: persisted={result.persisted} duplicates={result.duplicates}")
    if load_serving:
        with psycopg.connect(str(settings.postgres_dsn)) as connection:
            count = upsert_market_bars(connection, finalized_bar_rows(events, interval))
        print(f"historical_serving_load complete: upserted_market_bars={count}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill canonical BTC market observations into Bronze storage"
    )
    parser.add_argument("--start", type=parse_utc_datetime, required=True)
    parser.add_argument("--end", type=parse_utc_datetime, required=True)
    parser.add_argument("--symbol", default="BTC-USD")
    parser.add_argument("--interval", default="1h", choices=INTERVAL_DURATIONS)
    parser.add_argument(
        "--load-serving",
        action="store_true",
        help="Upsert finalized REST OHLCV bars into local PostgreSQL for dbt/Power BI.",
    )
    args = parser.parse_args()
    asyncio.run(run_backfill(args.start, args.end, args.symbol, args.interval, args.load_serving))


if __name__ == "__main__":
    main()
