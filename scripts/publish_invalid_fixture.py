"""Publish a deliberately invalid event to validate Spark quarantine handling."""

import json
from datetime import UTC, datetime

from confluent_kafka import Producer

from cryptopulse.common.config import get_settings


def main() -> None:
    settings = get_settings()
    payload = {
        "event_id": "fixture-invalid-ohlc",
        "provider": "fixture",
        "symbol": "BTC-USD",
        "currency": "USD",
        "event_type": "bar",
        "event_timestamp": datetime.now(UTC).isoformat(),
        "ingested_at": datetime.now(UTC).isoformat(),
        "open": "100",
        "high": "90",
        "low": "80",
        "close": "95",
        "price": None,
        "volume": "1",
        "trade_count": 1,
        "interval": "1m",
        "source_sequence": "fixture-invalid-ohlc",
        "schema_version": "1.0.0",
        "source_payload": {"fixture": "invalid_ohlc"},
    }
    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
    producer.produce(
        settings.kafka_topic, key=b"fixture-invalid-ohlc", value=json.dumps(payload).encode()
    )
    producer.flush(10)
    print("published invalid fixture")


if __name__ == "__main__":
    main()
