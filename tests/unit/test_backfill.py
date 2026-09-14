from datetime import UTC, datetime
from decimal import Decimal

import pytest

from cryptopulse.contracts import EventType, MarketEvent
from cryptopulse.ingestion.backfill import finalized_bar_rows, parse_utc_datetime


def test_backfill_parser_normalizes_to_utc() -> None:
    assert parse_utc_datetime("2024-01-01T01:00:00+01:00") == datetime(2024, 1, 1, tzinfo=UTC)


def test_backfill_parser_rejects_naive_timestamp() -> None:
    with pytest.raises(Exception, match="timezone"):
        parse_utc_datetime("2024-01-01T00:00:00")


def test_finalized_bar_rows_maps_validated_rest_candle_to_serving_grain() -> None:
    event = MarketEvent(
        provider="coinbase_exchange",
        symbol="BTC-USD",
        event_type=EventType.BAR,
        event_timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        open=Decimal("42000"),
        high=Decimal("42500"),
        low=Decimal("41900"),
        close=Decimal("42300"),
        volume=Decimal("12.5"),
        interval="1h",
    )

    assert finalized_bar_rows([event], "1h") == [
        {
            "provider": "coinbase_exchange",
            "symbol": "BTC-USD",
            "currency": "USD",
            "interval": "1 hour",
            "bar_start": datetime(2024, 1, 1, tzinfo=UTC),
            "bar_end": datetime(2024, 1, 1, 1, tzinfo=UTC),
            "open": 42000.0,
            "high": 42500.0,
            "low": 41900.0,
            "close": 42300.0,
            "volume": 12.5,
            "trade_count": 0,
            "vwap": 42300.0,
        }
    ]
