"""Deterministic Spark transformations from canonical Bronze events to Silver records."""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


def validate_and_deduplicate(events: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Return accepted and quarantined events without silently discarding invalid rows.

    The required deterministic key is `event_id` when supplied by the producer. The fallback key
    uses provider, symbol, type, source sequence, timestamp, and interval. Ties are resolved by
    earliest ingestion timestamp.
    """
    normalized = events.withColumn(
        "dedup_key",
        F.coalesce(
            F.col("event_id"),
            F.concat_ws(
                ":",
                F.col("provider"),
                F.col("symbol"),
                F.col("event_type"),
                F.coalesce(F.col("source_sequence"), F.lit("")),
                F.col("event_timestamp").cast("string"),
                F.coalesce(F.col("interval"), F.lit("")),
            ),
        ),
    )
    invalid_reason = (
        F.when(F.col("event_timestamp").isNull(), F.lit("timestamp_missing"))
        .when((F.col("price").isNotNull()) & (F.col("price") <= 0), F.lit("price_non_positive"))
        .when((F.col("volume").isNotNull()) & (F.col("volume") < 0), F.lit("volume_negative"))
        .when(
            F.col("event_type").eqNullSafe("bar")
            & (
                F.col("open").isNull()
                | F.col("high").isNull()
                | F.col("low").isNull()
                | F.col("close").isNull()
            ),
            F.lit("ohlc_missing"),
        )
        .when(
            F.col("event_type").eqNullSafe("bar")
            & (
                (F.col("high") < F.greatest("open", "close"))
                | (F.col("low") > F.least("open", "close"))
            ),
            F.lit("ohlc_inconsistent"),
        )
    )
    checked = normalized.withColumn("quality_failure_reason", invalid_reason)
    quarantined = checked.where(F.col("quality_failure_reason").isNotNull())
    valid = checked.where(F.col("quality_failure_reason").isNull())
    ranking = Window.partitionBy("dedup_key").orderBy(F.col("ingested_at").asc())
    accepted = valid.withColumn("dedup_rank", F.row_number().over(ranking)).where("dedup_rank = 1")
    return accepted.drop("dedup_rank"), quarantined
