"""Checkpointed Redpanda-to-Delta Bronze/Silver Structured Streaming job."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType, MapType, StringType, StructField, StructType

from cryptopulse.streaming.aggregates import market_bars
from cryptopulse.streaming.gold_sink import upsert_market_bars
from cryptopulse.streaming.spark import build_spark_session

MARKET_EVENT_SCHEMA = StructType(
    [
        StructField("event_id", StringType(), False),
        StructField("provider", StringType(), False),
        StructField("symbol", StringType(), False),
        StructField("currency", StringType(), False),
        StructField("event_type", StringType(), False),
        StructField("event_timestamp", StringType(), False),
        StructField("ingested_at", StringType(), False),
        StructField("open", DecimalType(30, 10), True),
        StructField("high", DecimalType(30, 10), True),
        StructField("low", DecimalType(30, 10), True),
        StructField("close", DecimalType(30, 10), True),
        StructField("price", DecimalType(30, 10), True),
        StructField("volume", DecimalType(30, 10), True),
        StructField("trade_count", StringType(), True),
        StructField("interval", StringType(), True),
        StructField("source_sequence", StringType(), True),
        StructField("schema_version", StringType(), False),
        StructField("source_payload", MapType(StringType(), StringType()), True),
    ]
)


@dataclass(frozen=True)
class StreamingPaths:
    bronze: str
    silver: str
    quarantine: str
    aggregates_root: str
    checkpoint_root: str


def gold_batch_writer(target_path: str) -> Callable[[DataFrame, int], None]:
    """Bind a Gold target path to Spark's typed foreach-batch callback."""

    def write_batch(batch: DataFrame, batch_id: int) -> None:
        upsert_market_bars(batch, batch_id, target_path)

    return write_batch


def kafka_source(spark: SparkSession, bootstrap_servers: str, topic: str) -> DataFrame:
    """Create a Kafka-compatible source; Redpanda is accessed through its Kafka API."""
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("subscribe", topic)
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )


def parsed_events(kafka_events: DataFrame) -> DataFrame:
    """Preserve raw broker value and project typed canonical fields."""
    raw = kafka_events.select(
        F.col("key").cast("string").alias("broker_key"),
        F.col("value").cast("string").alias("raw_payload"),
        F.col("timestamp").alias("broker_timestamp"),
    )
    return (
        raw.withColumn("event", F.from_json("raw_payload", MARKET_EVENT_SCHEMA))
        .select("broker_key", "raw_payload", "broker_timestamp", "event.*")
        .withColumn("event_timestamp", F.to_timestamp("event_timestamp"))
        .withColumn("ingested_at", F.to_timestamp("ingested_at"))
        .withColumn("event_date", F.to_date("event_timestamp"))
    )


def with_quality_flags(events: DataFrame) -> DataFrame:
    """Mark rather than discard records that fail Silver business rules."""
    failure = (
        F.when(F.col("event_id").isNull(), F.lit("event_id_missing"))
        .when(F.col("event_timestamp").isNull(), F.lit("timestamp_missing"))
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
    return events.withColumn("quality_failure_reason", failure)


def start_streams(
    bootstrap_servers: str, topic: str, paths: StreamingPaths, trigger_interval: str = "30 seconds"
) -> list[Any]:
    """Start independent checkpointed Bronze, Silver, and quarantine Delta sinks."""
    spark = build_spark_session("cryptopulse-bronze-silver")
    events = parsed_events(kafka_source(spark, bootstrap_servers, topic))
    bronze = (
        events.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{paths.checkpoint_root}/bronze")
        .partitionBy("provider", "symbol", "event_date")
        .trigger(processingTime=trigger_interval)
        .start(paths.bronze)
    )
    quality_checked = with_quality_flags(events)
    quarantine = (
        quality_checked.where(F.col("quality_failure_reason").isNotNull())
        .writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{paths.checkpoint_root}/quarantine")
        .trigger(processingTime=trigger_interval)
        .start(paths.quarantine)
    )
    accepted = (
        quality_checked.where(F.col("quality_failure_reason").isNull())
        .withWatermark("event_timestamp", "15 minutes")
        .dropDuplicates(["event_id"])
        .withColumn("quality_passed", F.lit(True))
    )
    silver = (
        accepted.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{paths.checkpoint_root}/silver")
        .partitionBy("provider", "symbol", "event_date")
        .trigger(processingTime=trigger_interval)
        .start(paths.silver)
    )
    aggregate_queries = [
        (
            market_bars(accepted, interval)
            .writeStream.outputMode("update")
            .option("checkpointLocation", f"{paths.checkpoint_root}/bars-{interval}")
            .trigger(processingTime=trigger_interval)
            .foreachBatch(gold_batch_writer(f"{paths.aggregates_root}/interval={interval}"))
            .start()
        )
        for interval in ("1 minute", "5 minutes", "15 minutes", "1 hour")
    ]
    return [bronze, quarantine, silver, *aggregate_queries]
