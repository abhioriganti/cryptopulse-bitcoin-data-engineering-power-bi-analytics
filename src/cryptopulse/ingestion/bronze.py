"""Immutable raw-event persistence with deterministic idempotency keys."""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC
from typing import Protocol

from cryptopulse.contracts import MarketEvent


class ObjectStore(Protocol):
    """Small storage boundary, testable without a running MinIO instance."""

    def put_if_absent(self, key: str, payload: bytes) -> bool:
        """Persist a new object; return False when the immutable key already exists."""


@dataclass(frozen=True)
class BronzeWriteResult:
    persisted: int
    duplicates: int
    keys: list[str]


class BronzeWriter:
    """Writes one immutable canonical envelope per input event to S3-compatible storage."""

    def __init__(self, store: ObjectStore, bucket: str, prefix: str = "bronze") -> None:
        self._store = store
        self._bucket = bucket
        self._prefix = prefix.strip("/")

    def write_events(self, events: list[MarketEvent], run_id: str) -> BronzeWriteResult:
        persisted = 0
        duplicates = 0
        keys: list[str] = []
        for event in events:
            key = self._key_for(event)
            envelope = {
                "run_id": run_id,
                "ingestion_metadata": {
                    "provider": event.provider,
                    "schema_version": event.schema_version,
                    "ingested_at": event.ingested_at.isoformat(),
                },
                "event": event.model_dump(mode="json"),
            }
            created = self._store.put_if_absent(key, json.dumps(envelope, sort_keys=True).encode())
            if created:
                persisted += 1
                keys.append(key)
            else:
                duplicates += 1
        return BronzeWriteResult(persisted=persisted, duplicates=duplicates, keys=keys)

    def _key_for(self, event: MarketEvent) -> str:
        event_date = event.event_timestamp.astimezone(UTC).date().isoformat()
        stable_hash = hashlib.sha256(event.deduplication_key.encode()).hexdigest()
        return (
            f"{self._prefix}/provider={event.provider}/symbol={event.symbol}/"
            f"event_date={event_date}/{stable_hash}.json"
        )


class S3ObjectStore:
    """MinIO/S3 object store implementation created only in runtime environments."""

    def __init__(self, endpoint_url: str, bucket: str, access_key: str, secret_key: str) -> None:
        try:
            import boto3  # type: ignore[import-untyped]
            from botocore.exceptions import ClientError  # type: ignore[import-untyped]
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("boto3 is required to use MinIO/S3 persistence") from exc
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self._bucket = bucket
        self._client_error = ClientError

    def ensure_bucket(self) -> None:
        """Create the configured bucket when it does not yet exist."""
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except self._client_error as exc:
            if exc.response["Error"].get("Code") not in {"404", "NoSuchBucket", "NotFound"}:
                raise
            self._client.create_bucket(Bucket=self._bucket)

    def put_if_absent(self, key: str, payload: bytes) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except self._client_error as exc:
            if exc.response["Error"].get("Code") not in {"404", "NoSuchKey", "NotFound"}:
                raise
            self._client.put_object(
                Bucket=self._bucket, Key=key, Body=payload, ContentType="application/json"
            )
            return True
        return False
