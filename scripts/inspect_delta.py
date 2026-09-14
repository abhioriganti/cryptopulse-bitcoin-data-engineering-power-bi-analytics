"""Print the row count for a local Delta table, for operational verification."""

import argparse

from pyspark.sql import SparkSession

DELTA_EXTENSION = "io.delta.sql.DeltaSparkSessionExtension"
DELTA_CATALOG = "org.apache.spark.sql.delta.catalog.DeltaCatalog"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    spark = (
        SparkSession.builder.config("spark.sql.extensions", DELTA_EXTENSION)
        .config("spark.sql.catalog.spark_catalog", DELTA_CATALOG)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    print(f"row_count={spark.read.format('delta').load(args.path).count()}")
    spark.stop()


if __name__ == "__main__":
    main()
