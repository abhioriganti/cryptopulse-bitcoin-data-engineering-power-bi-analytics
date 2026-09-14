"""Idempotent Delta sink for update-mode streaming aggregates."""

from pyspark.sql import DataFrame


def upsert_market_bars(batch: DataFrame, _: int, target_path: str) -> None:
    """Persist current aggregate state by its deterministic bar business key."""
    if batch.rdd.isEmpty():
        return
    from delta.tables import DeltaTable

    keys = " and ".join(
        f"target.{column} = source.{column}"
        for column in ("provider", "symbol", "currency", "interval", "bar_start")
    )
    if not DeltaTable.isDeltaTable(batch.sparkSession, target_path):
        batch.write.format("delta").mode("append").save(target_path)
        return
    (
        DeltaTable.forPath(batch.sparkSession, target_path)
        .alias("target")
        .merge(batch.alias("source"), keys)
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
