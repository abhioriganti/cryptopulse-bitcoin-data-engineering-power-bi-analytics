from datetime import UTC, datetime

import httpx
import pytest

from cryptopulse.ingestion.coingecko import CoinGeckoProvider


@pytest.mark.asyncio
async def test_historical_data_normalizes_provider_payload() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "prices": [[1_704_067_200_000, 42_000.5]],
                "total_volumes": [[1_704_067_200_000, 12.2]],
            },
        )
    )
    async with httpx.AsyncClient(transport=transport) as client:
        provider = CoinGeckoProvider(client=client)
        rows = await provider.get_historical_data(
            "BTC-USD", datetime(2024, 1, 1, tzinfo=UTC), datetime(2024, 1, 2, tzinfo=UTC)
        )
    assert len(rows) == 1
    assert str(rows[0].price) == "42000.5"
    assert rows[0].deduplication_key.endswith(":1704067200000")


@pytest.mark.asyncio
async def test_latest_quote_normalizes_provider_payload() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"bitcoin": {"usd": 42_000}})
    )
    async with httpx.AsyncClient(transport=transport) as client:
        quote = await CoinGeckoProvider(client=client).get_latest_quote("BTC-USD")
    assert quote.symbol == "BTC-USD"
    assert str(quote.price) == "42000"
