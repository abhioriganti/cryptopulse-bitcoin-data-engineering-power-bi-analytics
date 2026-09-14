"""Credential-free Coinbase Exchange REST adapter for BTC-USD OHLCV backfills."""

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import httpx
import structlog

from cryptopulse.contracts import EventType, MarketEvent
from cryptopulse.ingestion.provider import MarketDataProvider

LOGGER = structlog.get_logger(__name__)
COINBASE_EXCHANGE_API = "https://api.exchange.coinbase.com"
GRANULARITY_SECONDS = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "6h": 21600, "1d": 86400}
MAX_CANDLES_PER_REQUEST = 300


class CoinbaseExchangeProvider(MarketDataProvider):
    """Public exchange adapter with chunked historical requests and bounded retries."""

    name = "coinbase_exchange"

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 20,
        max_attempts: int = 3,
    ) -> None:
        self._client = client or httpx.AsyncClient(timeout=timeout_seconds)
        self._owns_client = client is None
        self._max_attempts = max_attempts

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def get_historical_data(
        self, symbol: str, start: datetime, end: datetime, interval: str = "1h"
    ) -> list[MarketEvent]:
        """Fetch and normalize OHLCV bars without exceeding the exchange's candle limit."""
        granularity = GRANULARITY_SECONDS.get(interval)
        if granularity is None:
            raise ValueError(f"unsupported Coinbase interval: {interval}")
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("historical range must be timezone-aware")

        events: list[MarketEvent] = []
        window = timedelta(seconds=granularity * MAX_CANDLES_PER_REQUEST)
        cursor = start.astimezone(UTC)
        normalized_end = end.astimezone(UTC)
        while cursor < normalized_end:
            chunk_end = min(cursor + window, normalized_end)
            response = await self._request(
                f"/products/{symbol}/candles",
                {
                    "start": cursor.isoformat(),
                    "end": chunk_end.isoformat(),
                    "granularity": granularity,
                },
            )
            events.extend(self._to_events(symbol, interval, response.json()))
            cursor = chunk_end
        return sorted(
            {event.deduplication_key: event for event in events}.values(),
            key=lambda item: item.event_timestamp,
        )

    async def get_latest_quote(self, symbol: str) -> MarketEvent:
        response = await self._request(f"/products/{symbol}/ticker", {})
        payload = response.json()
        return MarketEvent(
            provider=self.name,
            symbol=symbol,
            event_type=EventType.QUOTE,
            event_timestamp=datetime.now(UTC),
            price=Decimal(str(payload["price"])),
            volume=Decimal(str(payload.get("volume", 0))),
            source_sequence=str(payload.get("trade_id", "")) or None,
            source_payload=payload,
        )

    def stream_market_data(self, symbol: str) -> AsyncIterator[MarketEvent]:
        raise NotImplementedError("CoinbaseExchangeProvider is REST-only")

    def _to_events(self, symbol: str, interval: str, rows: list[list[Any]]) -> list[MarketEvent]:
        """Convert Coinbase candles: [timestamp, low, high, open, close, volume]."""
        return [
            MarketEvent(
                provider=self.name,
                symbol=symbol,
                event_type=EventType.BAR,
                event_timestamp=datetime.fromtimestamp(int(row[0]), tz=UTC),
                low=Decimal(str(row[1])),
                high=Decimal(str(row[2])),
                open=Decimal(str(row[3])),
                close=Decimal(str(row[4])),
                volume=Decimal(str(row[5])),
                interval=interval,
                source_sequence=str(row[0]),
                source_payload={"candle": row},
            )
            for row in rows
        ]

    async def _request(self, path: str, params: dict[str, Any]) -> httpx.Response:
        response: httpx.Response | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                response = await self._client.get(f"{COINBASE_EXCHANGE_API}{path}", params=params)
                if response.status_code not in {429, 500, 502, 503, 504}:
                    response.raise_for_status()
                    return response
                retry_after = float(response.headers.get("Retry-After", 0))
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                retry_after = 0
                LOGGER.warning(
                    "provider_request_failed", provider=self.name, attempt=attempt, error=str(exc)
                )
            if attempt == self._max_attempts:
                if response is not None:
                    response.raise_for_status()
                raise RuntimeError(f"{self.name} request exhausted retries")
            delay = retry_after if retry_after > 0 else 2 ** (attempt - 1)
            LOGGER.warning(
                "provider_retry", provider=self.name, attempt=attempt, delay_seconds=delay
            )
            await asyncio.sleep(delay)
        raise AssertionError("unreachable")
