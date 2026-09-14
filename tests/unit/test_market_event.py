from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from cryptopulse.contracts import EventType, MarketEvent


def test_bar_contract_accepts_valid_ohlc() -> None:
    event = MarketEvent(
        provider="test",
        symbol="BTC-USD",
        event_type=EventType.BAR,
        event_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("2"),
        interval="1m",
    )
    assert event.deduplication_key.endswith(":1m")


def test_contract_rejects_invalid_ohlc() -> None:
    with pytest.raises(ValidationError, match="high must"):
        MarketEvent(
            provider="test",
            symbol="BTC-USD",
            event_type=EventType.BAR,
            event_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            open=Decimal("100"),
            high=Decimal("99"),
            low=Decimal("90"),
            close=Decimal("105"),
        )


def test_contract_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        MarketEvent(
            provider="test",
            symbol="BTC-USD",
            event_type=EventType.QUOTE,
            event_timestamp=datetime(2026, 1, 1),
            price=Decimal("1"),
        )
