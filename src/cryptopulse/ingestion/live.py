"""Long-running live producer, separately supervised from Airflow batch DAGs."""

import argparse
import asyncio

from cryptopulse.common.config import get_settings
from cryptopulse.ingestion.coinbase_websocket import CoinbaseWebSocketProvider
from cryptopulse.ingestion.publisher import RedpandaPublisher


async def run_live(symbol: str, max_events: int | None = None) -> None:
    settings = get_settings()
    provider = CoinbaseWebSocketProvider()
    publisher = RedpandaPublisher(settings.kafka_bootstrap_servers, settings.kafka_topic)
    published = 0
    async for event in provider.stream_market_data(symbol):
        publisher.publish(event)
        published += 1
        print(f"published event={event.event_id} key={event.deduplication_key}")
        if max_events is not None and published >= max_events:
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream canonical Coinbase trades to Redpanda")
    parser.add_argument("--symbol", default="BTC-USD")
    parser.add_argument("--max-events", type=int, default=None)
    args = parser.parse_args()
    if args.max_events is not None and args.max_events < 1:
        parser.error("--max-events must be positive")
    asyncio.run(run_live(args.symbol, args.max_events))


if __name__ == "__main__":
    main()
