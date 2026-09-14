"""Kafka-compatible publishing of canonical events to Redpanda."""

import json
from typing import Protocol

from confluent_kafka import KafkaError, Message, Producer

from cryptopulse.contracts import MarketEvent


class EventPublisher(Protocol):
    """Publishing boundary that keeps ingestion services independently testable."""

    def publish(self, event: MarketEvent) -> None:
        """Publish a validated canonical event with a deterministic message key."""


class RedpandaPublisher:
    """Synchronous delivery-confirmed Kafka producer for finite producer batches."""

    def __init__(self, bootstrap_servers: str, topic: str) -> None:
        self._producer = Producer(
            {"bootstrap.servers": bootstrap_servers, "enable.idempotence": True}
        )
        self._topic = topic

    def publish(self, event: MarketEvent) -> None:
        """Wait for broker acknowledgement so caller can safely record progress."""
        delivery_error: KafkaError | None = None

        def delivered(error: KafkaError | None, _: Message) -> None:
            nonlocal delivery_error
            delivery_error = error

        self._producer.produce(
            self._topic,
            key=event.deduplication_key.encode(),
            value=json.dumps(event.model_dump(mode="json"), sort_keys=True).encode(),
            on_delivery=delivered,
        )
        self._producer.flush(10)
        if delivery_error is not None:
            raise RuntimeError(f"broker did not accept market event: {delivery_error}")
