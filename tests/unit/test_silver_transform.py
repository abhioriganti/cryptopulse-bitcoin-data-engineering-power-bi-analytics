import re
import subprocess

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

from cryptopulse.transformations.silver import validate_and_deduplicate


def test_silver_transform_deduplicates_and_quarantines() -> None:
    result = subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
    match = re.search(r'"(\d+)', result.stderr)
    assert match is not None
    if int(match.group(1)) > 17:
        pytest.skip("PySpark 3.5 requires a supported Java runtime (Java 17 recommended)")
    spark = SparkSession.builder.master("local[1]").appName("cryptopulse-test").getOrCreate()
    try:
        rows = [
            (
                "event-1",
                "test",
                "BTC-USD",
                "trade",
                "2024-01-01T00:00:00Z",
                "2024-01-01T00:00:01Z",
                1.0,
                1.0,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
            (
                "event-1",
                "test",
                "BTC-USD",
                "trade",
                "2024-01-01T00:00:00Z",
                "2024-01-01T00:00:02Z",
                1.0,
                1.0,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
            (
                "event-2",
                "test",
                "BTC-USD",
                "trade",
                "2024-01-01T00:00:00Z",
                "2024-01-01T00:00:01Z",
                -1.0,
                1.0,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        ]
        schema = StructType(
            [
                StructField("event_id", StringType(), False),
                StructField("provider", StringType(), False),
                StructField("symbol", StringType(), False),
                StructField("event_type", StringType(), False),
                StructField("event_timestamp", StringType(), False),
                StructField("ingested_at", StringType(), False),
                StructField("price", DoubleType(), True),
                StructField("volume", DoubleType(), True),
                StructField("open", DoubleType(), True),
                StructField("high", DoubleType(), True),
                StructField("low", DoubleType(), True),
                StructField("close", DoubleType(), True),
                StructField("source_sequence", StringType(), True),
                StructField("interval", StringType(), True),
            ]
        )
        source = (
            spark.createDataFrame(rows, schema)
            .selectExpr(
                "*",
                "cast(event_timestamp as timestamp) event_timestamp_ts",
                "cast(ingested_at as timestamp) ingested_at_ts",
            )
            .drop("event_timestamp", "ingested_at")
            .withColumnRenamed("event_timestamp_ts", "event_timestamp")
            .withColumnRenamed("ingested_at_ts", "ingested_at")
        )
        accepted, quarantined = validate_and_deduplicate(source)
        assert accepted.count() == 1
        assert quarantined.count() == 1
        assert quarantined.first()["quality_failure_reason"] == "price_non_positive"
    finally:
        spark.stop()
