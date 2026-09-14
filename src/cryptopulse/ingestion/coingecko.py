"""CoinGecko REST adapter for credential-free historical Bitcoin backfills."""

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import httpx
import structlog

from cryptopulse.contracts import EventType, MarketEvent
from cryptopulse.ingestion.provider import MarketDataProvider

LOGGER = structlog.get_logger(__name__)
COINGECKO_API = "https://api.coingecko.com/api/v3"
ASSET_IDS = {"BTC-USD": "bitcoin"}


class CoinGeckoProvider(MarketDataProvider):
    """REST adapter with bounded exponential retry for transient provider failures."""

    name = "coingecko"

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
        self, symbol: str, start: datetime, end: datetime, interval: str = "raw"
    ) -> list[MarketEvent]:
        """Fetch price/volume observations normalized as canonical quote events."""
        asset_id = self._asset_id(symbol)
        response = await self._request(
            f"/coins/{asset_id}/market_chart/range",
            {"vs_currency": "usd", "from": int(start.timestamp()), "to": int(end.timestamp())},
        )
        payload = response.json()
        volumes = {int(timestamp): value for timestamp, value in payload.get("total_volumes", [])}
        return [
            MarketEvent(
                provider=self.name,
                symbol=symbol,
                event_type=EventType.QUOTE,
                event_timestamp=datetime.fromtimestamp(timestamp / 1000, tz=UTC),
                price=Decimal(str(price)),
                volume=Decimal(str(volumes.get(timestamp, 0))),
                interval=interval,
                source_sequence=str(timestamp),
                source_payload={"price": [timestamp, price], "volume": volumes.get(timestamp)},
            )
            for timestamp, price in payload.get("prices", [])
        ]

    async def get_latest_quote(self, symbol: str) -> MarketEvent:
        """Fetch one current USD quote."""
        asset_id = self._asset_id(symbol)
        response = await self._request(
            "/simple/price",
            {"ids": asset_id, "vs_currencies": "usd", "include_24hr_vol": "true"},
        )
        quote = response.json()[asset_id]
        return MarketEvent(
            provider=self.name,
            symbol=symbol,
            event_type=EventType.QUOTE,
            event_timestamp=datetime.now(UTC),
            price=Decimal(str(quote["usd"])),
            volume=Decimal(str(quote.get("usd_24h_vol", 0))),
            source_payload=quote,
        )

    def stream_market_data(self, symbol: str) -> AsyncIterator[MarketEvent]:
        """REST is intentionally non-streaming; a WebSocket adapter arrives in Phase 3."""
        raise NotImplementedError("CoinGeckoProvider is REST-only")

    @staticmethod
    def _asset_id(symbol: str) -> str:
        try:
            return ASSET_IDS[symbol]
        except KeyError as exc:
            raise ValueError(f"unsupported CoinGecko symbol: {symbol}") from exc

    async def _request(self, path: str, params: dict[str, Any]) -> httpx.Response:
        for attempt in range(1, self._max_attempts + 1):
            try:
                response = await self._client.get(f"{COINGECKO_API}{path}", params=params)
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
                response.raise_for_status() if "response" in locals() else None
                raise RuntimeError(f"{self.name} request exhausted retries")
            delay = retry_after if retry_after > 0 else 2 ** (attempt - 1)
            LOGGER.warning(
                "provider_retry", provider=self.name, attempt=attempt, delay_seconds=delay
            )
            await asyncio.sleep(delay)
        raise AssertionError("unreachable")
