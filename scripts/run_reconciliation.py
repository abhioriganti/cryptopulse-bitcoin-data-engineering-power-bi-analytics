"""Reconcile local lakehouse layers with the PostgreSQL serving table."""

import os
from pathlib import Path

import psycopg
from pyspark.sql import SparkSession

from cryptopulse.common.config import get_settings
from cryptopulse.quality.persistence import ReconciliationResult, persist_reconciliations
from cryptopulse.streaming.spark import DELTA_CATALOG, DELTA_EXTENSION


def delta_count(spark: SparkSession, path: Path) -> int:
    """Return the table count, or zero when the layer has not been created."""
    if not path.exists():
        return 0
    return spark.read.format("delta").load(str(path)).count()


def main() -> None:
    settings = get_settings()
    root = Path(os.getenv("CRYPTOPULSE_LAKEHOUSE_ROOT", "data/lakehouse"))
    spark = (
        SparkSession.builder.appName("cryptopulse-reconciliation")
        .config("spark.sql.extensions", DELTA_EXTENSION)
        .config("spark.sql.catalog.spark_catalog", DELTA_CATALOG)
        .getOrCreate()
    )
    try:
        bronze = delta_count(spark, root / "bronze")
        silver = delta_count(spark, root / "silver")
        quarantine = delta_count(spark, root / "quarantine")
        gold = delta_count(spark, root / "gold_streaming_bars/interval=1 minute")
        with psycopg.connect(str(settings.postgres_dsn)) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select count(*) from raw.market_bars")
                serving = int(cursor.fetchone()[0])
            results = [
                ReconciliationResult(
                    "bronze_vs_silver_plus_quarantine", bronze, silver + quarantine
                ),
                ReconciliationResult("gold_vs_postgres_serving", gold, serving),
            ]
            run_id = persist_reconciliations(connection, results)
        print(f"reconciliation_run_id={run_id}")
        for result in results:
            print(f"{result.name}={result.status} difference={result.difference}")
        if any(result.status == "fail" for result in results):
            raise SystemExit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
