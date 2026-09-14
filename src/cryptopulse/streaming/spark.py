"""Spark session construction with Delta Lake extensions for local execution."""

from pyspark.sql import SparkSession

DELTA_EXTENSION = "io.delta.sql.DeltaSparkSessionExtension"
DELTA_CATALOG = "org.apache.spark.sql.delta.catalog.DeltaCatalog"
KAFKA_CONNECTOR = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.9"


def build_spark_session(application_name: str) -> SparkSession:
    """Create a Delta-enabled session; package resolution happens only at job startup."""
    from delta import configure_spark_with_delta_pip

    builder = (
        SparkSession.builder.master("local[2]")
        .appName(application_name)
        .config("spark.sql.extensions", DELTA_EXTENSION)
        .config("spark.sql.catalog.spark_catalog", DELTA_CATALOG)
        .config("spark.sql.session.timeZone", "UTC")
        # Keep the local development runtime responsive without changing
        # production-scale deployment settings.
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.default.parallelism", "2")
    )
    return configure_spark_with_delta_pip(builder, extra_packages=[KAFKA_CONNECTOR]).getOrCreate()
