import re
import subprocess
from datetime import UTC, datetime

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from cryptopulse.streaming.aggregates import market_bars


def test_market_bars_calculates_ohlcv_and_vwap() -> None:
    """Gold handoff bars use event time and include every accepted trade."""
    result = subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
    match = re.search(r'"(\d+)', result.stderr)
    assert match is not None
    if int(match.group(1)) > 17:
        pytest.skip("PySpark 3.5 requires a supported Java runtime (Java 17 recommended)")

    schema = StructType(
        [
            StructField("event_id", StringType(), False),
            StructField("provider", StringType(), False),
            StructField("symbol", StringType(), False),
            StructField("currency", StringType(), False),
            StructField("event_timestamp", TimestampType(), False),
            StructField("price", DoubleType(), True),
            StructField("close", DoubleType(), True),
            StructField("volume", DoubleType(), True),
        ]
    )
    rows = [
        (
            "event-1",
            "test",
            "BTC-USD",
            "USD",
            datetime(2024, 1, 1, 0, 0, 5, tzinfo=UTC),
            100.0,
            None,
            2.0,
        ),
        (
            "event-2",
            "test",
            "BTC-USD",
            "USD",
            datetime(2024, 1, 1, 0, 0, 20, tzinfo=UTC),
            110.0,
            None,
            1.0,
        ),
        (
            "event-3",
            "test",
            "BTC-USD",
            "USD",
            datetime(2024, 1, 1, 0, 0, 40, tzinfo=UTC),
            90.0,
            None,
            3.0,
        ),
    ]
    spark = (
        SparkSession.builder.master("local[1]").appName("cryptopulse-aggregate-test").getOrCreate()
    )
    try:
        bar = market_bars(spark.createDataFrame(rows, schema), "1 minute").first()
        assert bar["open"] == 100.0
        assert bar["high"] == 110.0
        assert bar["low"] == 90.0
        assert bar["close"] == 90.0
        assert bar["volume"] == 6.0
        assert bar["trade_count"] == 3
        assert bar["vwap"] == pytest.approx(96.6666666667)
    finally:
        spark.stop()
