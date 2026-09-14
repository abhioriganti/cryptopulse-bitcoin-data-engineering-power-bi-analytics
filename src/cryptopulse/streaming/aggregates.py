"""Event-time market-bar aggregates for the streaming Gold handoff."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def market_bars(events: DataFrame, interval: str, watermark: str = "15 minutes") -> DataFrame:
    """Build deterministic OHLCV/VWAP bars using only events available at event time."""
    priced = events.withColumn("bar_price", F.coalesce(F.col("price"), F.col("close"))).where(
        F.col("bar_price").isNotNull()
    )
    grouped = priced.withWatermark("event_timestamp", watermark).groupBy(
        F.window("event_timestamp", interval).alias("bar_window"),
        "provider",
        "symbol",
        "currency",
    )
    bars = grouped.agg(
        F.min_by("bar_price", F.struct("event_timestamp", "event_id")).alias("open"),
        F.max("bar_price").alias("high"),
        F.min("bar_price").alias("low"),
        F.max_by("bar_price", F.struct("event_timestamp", "event_id")).alias("close"),
        F.sum(F.coalesce("volume", F.lit(0))).alias("volume"),
        F.count(F.lit(1)).alias("trade_count"),
        F.sum(F.col("bar_price") * F.coalesce(F.col("volume"), F.lit(0))).alias("notional"),
    )
    return (
        bars.withColumn(
            "vwap",
            F.when(F.col("volume") > 0, F.col("notional") / F.col("volume")),
        )
        .withColumn("interval", F.lit(interval))
        .withColumn("bar_start", F.col("bar_window.start"))
        .withColumn("bar_end", F.col("bar_window.end"))
        .drop("bar_window", "notional")
    )
