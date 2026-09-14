"""Versioned canonical data contract for normalized market events."""

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EventType(StrEnum):
    TRADE = "trade"
    QUOTE = "quote"
    BAR = "bar"


class MarketEvent(BaseModel):
    """Provider-neutral market event, validated before publishing downstream."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    event_id: UUID = Field(default_factory=uuid4)
    provider: str = Field(min_length=1, max_length=100)
    symbol: str = Field(pattern=r"^[A-Z0-9]+-[A-Z0-9]+$")
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    event_type: EventType
    event_timestamp: datetime
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    open: Decimal | None = Field(default=None, ge=0)
    high: Decimal | None = Field(default=None, ge=0)
    low: Decimal | None = Field(default=None, ge=0)
    close: Decimal | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, gt=0)
    volume: Decimal | None = Field(default=None, ge=0)
    trade_count: int | None = Field(default=None, ge=0)
    interval: str | None = Field(default=None, max_length=20)
    source_sequence: str | None = Field(default=None, max_length=255)
    schema_version: str = "1.0.0"
    source_payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_timestamp", "ingested_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_market_values(self) -> "MarketEvent":
        ohlc = (self.open, self.high, self.low, self.close)
        if any(value is not None for value in ohlc) and any(value is None for value in ohlc):
            raise ValueError("OHLC bars require open, high, low, and close")
        if (
            self.high is not None
            and self.open is not None
            and self.close is not None
            and self.low is not None
        ):
            if self.high < max(self.open, self.close):
                raise ValueError("high must be at least open and close")
            if self.low > min(self.open, self.close):
                raise ValueError("low must be at most open and close")
        if self.event_type is EventType.BAR and self.open is None:
            raise ValueError("bar events require OHLC values")
        if self.event_type in {EventType.TRADE, EventType.QUOTE} and self.price is None:
            raise ValueError("trade and quote events require price")
        return self

    @property
    def deduplication_key(self) -> str:
        """Stable fallback identity for sources that lack a durable event ID."""
        if self.source_sequence:
            return f"{self.provider}:{self.symbol}:{self.event_type}:{self.source_sequence}"
        return ":".join(
            (
                self.provider,
                self.symbol,
                self.event_type,
                self.event_timestamp.isoformat(),
                self.interval or "",
            )
        )
