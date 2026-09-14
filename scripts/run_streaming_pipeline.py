"""Launch checkpointed local Bronze/Silver stream processing."""

import os
from pathlib import Path

from cryptopulse.common.config import get_settings
from cryptopulse.streaming.silver_stream import StreamingPaths, start_streams


def main() -> None:
    settings = get_settings()
    root = Path(os.getenv("CRYPTOPULSE_LAKEHOUSE_ROOT", "data/lakehouse"))
    queries = start_streams(
        settings.kafka_bootstrap_servers,
        settings.kafka_topic,
        StreamingPaths(
            bronze=str(root / "bronze"),
            silver=str(root / "silver"),
            quarantine=str(root / "quarantine"),
            aggregates_root=str(root / "gold_streaming_bars"),
            checkpoint_root=str(root / "checkpoints"),
        ),
    )
    for query in queries:
        query.awaitTermination()


if __name__ == "__main__":
    main()
