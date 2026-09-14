from datetime import UTC, datetime, timedelta
from decimal import Decimal

from cryptopulse.contracts import EventType, MarketEvent
from cryptopulse.quality.rules import QualityStatus, validate_event


def test_future_event_is_flagged() -> None:
    now = datetime.now(UTC)
    event = MarketEvent(
        provider="test",
        symbol="BTC-USD",
        event_type=EventType.QUOTE,
        event_timestamp=now,
        ingested_at=now - timedelta(seconds=1),
        price=Decimal("1"),
    )
    assert validate_event(event)[0].status is QualityStatus.FAIL
