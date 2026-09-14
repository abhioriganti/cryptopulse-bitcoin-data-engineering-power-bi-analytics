from datetime import UTC, datetime

import httpx
import pytest

from cryptopulse.ingestion.coinbase_exchange import CoinbaseExchangeProvider


@pytest.mark.asyncio
async def test_historical_data_normalizes_ohlcv_candles() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200, json=[[1_704_067_200, 40_000, 43_000, 41_000, 42_000, 12.5]]
        )
    )
    async with httpx.AsyncClient(transport=transport) as client:
        provider = CoinbaseExchangeProvider(client=client)
        rows = await provider.get_historical_data(
            "BTC-USD", datetime(2024, 1, 1, tzinfo=UTC), datetime(2024, 1, 1, 1, tzinfo=UTC)
        )
    assert len(rows) == 1
    assert str(rows[0].close) == "42000"
    assert rows[0].event_type.value == "bar"


@pytest.mark.asyncio
async def test_latest_quote_normalizes_ticker() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"price": "42000", "volume": "12", "trade_id": 42})
    )
    async with httpx.AsyncClient(transport=transport) as client:
        quote = await CoinbaseExchangeProvider(client=client).get_latest_quote("BTC-USD")
    assert str(quote.price) == "42000"
    assert quote.source_sequence == "42"
