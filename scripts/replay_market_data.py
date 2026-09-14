"""Publish a deterministic historical trade sequence for local pipeline demonstrations."""

import argparse
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from cryptopulse.common.config import get_settings
from cryptopulse.contracts import EventType, MarketEvent
from cryptopulse.ingestion.publisher import RedpandaPublisher


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=int, default=20)
    args = parser.parse_args()
    if args.minutes < 16:
        raise SystemExit("--minutes must be at least 16 to advance the 15-minute watermark")
    settings = get_settings()
    publisher = RedpandaPublisher(settings.kafka_bootstrap_servers, settings.kafka_topic)
    # A local replay must be newer than the stream's current watermark. The sequence deliberately
    # advances event time beyond now so append-mode windows can be finalized in one demonstration.
    start = datetime.now(UTC).replace(second=0, microsecond=0)
    run_id = int(start.timestamp())
    for minute in range(args.minutes):
        publisher.publish(
            MarketEvent(
                provider="replay",
                symbol="BTC-USD",
                event_type=EventType.TRADE,
                event_timestamp=start + timedelta(minutes=minute),
                price=Decimal("42000") + Decimal(minute),
                volume=Decimal("1"),
                source_sequence=f"replay-{run_id}-{minute}",
            )
        )
    print(f"published_replay_events={args.minutes}")


if __name__ == "__main__":
    main()
