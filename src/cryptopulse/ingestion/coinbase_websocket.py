"""Public Coinbase Advanced Trade WebSocket adapter for live BTC-USD trades."""

import asyncio
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import structlog
from websockets.asyncio.client import connect

from cryptopulse.contracts import EventType, MarketEvent
from cryptopulse.ingestion.provider import MarketDataProvider

LOGGER = structlog.get_logger(__name__)
COINBASE_WS_URL = "wss://advanced-trade-ws.coinbase.com"


class CoinbaseWebSocketProvider(MarketDataProvider):
    """Reconnects indefinitely and exposes only validated market-trade events."""

    name = "coinbase_advanced_trade"

    async def get_historical_data(
        self, symbol: str, start: datetime, end: datetime, interval: str
    ) -> list[MarketEvent]:
        raise NotImplementedError("CoinbaseWebSocketProvider is streaming-only")

    async def get_latest_quote(self, symbol: str) -> MarketEvent:
        raise NotImplementedError("consume stream_market_data for live quotes")

    async def stream_market_data(self, symbol: str) -> AsyncIterator[MarketEvent]:
        reconnect_delay = 1
        while True:
            try:
                async with connect(COINBASE_WS_URL) as websocket:
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "subscribe",
                                "product_ids": [symbol],
                                "channel": "market_trades",
                            }
                        )
                    )
                    reconnect_delay = 1
                    async for message in websocket:
                        for event in self.events_from_message(message, symbol):
                            yield event
            except Exception as exc:  # provider failures must not kill the ingestion process
                LOGGER.warning(
                    "websocket_reconnecting",
                    provider=self.name,
                    delay_seconds=reconnect_delay,
                    error=str(exc),
                )
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 60)

    def events_from_message(self, message: str | bytes, symbol: str) -> list[MarketEvent]:
        """Parse a Coinbase channel message, discarding heartbeats/subscription acknowledgements."""
        payload: dict[str, Any] = json.loads(message)
        if payload.get("channel") != "market_trades":
            return []
        events: list[MarketEvent] = []
        for update in payload.get("events", []):
            for trade in update.get("trades", []):
                if trade.get("product_id") != symbol:
                    continue
                events.append(
                    MarketEvent(
                        provider=self.name,
                        symbol=symbol,
                        event_type=EventType.TRADE,
                        event_timestamp=datetime.fromisoformat(
                            trade["time"].replace("Z", "+00:00")
                        ).astimezone(UTC),
                        price=Decimal(str(trade["price"])),
                        volume=Decimal(str(trade["size"])),
                        source_sequence=str(trade["trade_id"]),
                        source_payload=trade,
                    )
                )
        return events
