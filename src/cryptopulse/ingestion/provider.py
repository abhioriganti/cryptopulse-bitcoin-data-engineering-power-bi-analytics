"""Provider abstraction; adapters convert source formats to MarketEvent."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from cryptopulse.contracts import MarketEvent


class MarketDataProvider(ABC):
    """Contract implemented by REST and streaming market-data adapters."""

    @abstractmethod
    async def get_historical_data(
        self, symbol: str, start: datetime, end: datetime, interval: str
    ) -> list[MarketEvent]:
        """Return normalized historical bars for an inclusive time range."""

    @abstractmethod
    async def get_latest_quote(self, symbol: str) -> MarketEvent:
        """Return the current normalized quote."""

    @abstractmethod
    def stream_market_data(self, symbol: str) -> AsyncIterator[MarketEvent]:
        """Yield normalized live events until the consumer stops."""
