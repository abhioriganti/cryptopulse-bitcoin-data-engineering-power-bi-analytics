from datetime import UTC, datetime
from decimal import Decimal

from cryptopulse.contracts import EventType, MarketEvent
from cryptopulse.ingestion.bronze import BronzeWriter


class InMemoryObjectStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put_if_absent(self, key: str, payload: bytes) -> bool:
        if key in self.objects:
            return False
        self.objects[key] = payload
        return True


def test_bronze_writer_is_idempotent_and_partitions_by_event_date() -> None:
    event = MarketEvent(
        provider="test",
        symbol="BTC-USD",
        event_type=EventType.QUOTE,
        event_timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        price=Decimal("42000"),
        source_sequence="source-1",
        source_payload={"original": "payload"},
    )
    store = InMemoryObjectStore()
    writer = BronzeWriter(store, bucket="ignored")

    first = writer.write_events([event], run_id="run-a")
    second = writer.write_events([event], run_id="run-b")

    assert first.persisted == 1
    assert second.duplicates == 1
    assert "provider=test/symbol=BTC-USD/event_date=2024-01-01" in first.keys[0]
    assert b'"original": "payload"' in store.objects[first.keys[0]]
