"""Load finalized one-minute Gold Delta bars into PostgreSQL idempotently."""

import os
from pathlib import Path

import psycopg
from pyspark.sql import SparkSession

from cryptopulse.common.config import get_settings
from cryptopulse.serving.postgres import upsert_market_bars
from cryptopulse.streaming.spark import DELTA_CATALOG, DELTA_EXTENSION


def main() -> None:
    """Read the Gold Delta handoff and upsert its business-keyed rows."""
    settings = get_settings()
    root = Path(os.getenv("CRYPTOPULSE_LAKEHOUSE_ROOT", "data/lakehouse"))
    gold_path = root / "gold_streaming_bars/interval=1 minute"
    spark = (
        SparkSession.builder.appName("cryptopulse-gold-postgres-loader")
        .config("spark.sql.extensions", DELTA_EXTENSION)
        .config("spark.sql.catalog.spark_catalog", DELTA_CATALOG)
        .getOrCreate()
    )
    try:
        bars = spark.read.format("delta").load(str(gold_path))
        rows = (row.asDict(recursive=True) for row in bars.toLocalIterator())
        with psycopg.connect(str(settings.postgres_dsn)) as connection:
            count = upsert_market_bars(connection, rows)
        print(f"upserted_market_bars={count}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
