"""PostgreSQL persistence for reproducible forecast observations."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import psycopg


@dataclass(frozen=True)
class ForecastRecord:
    """One scored one-step forecast at a known market-bar timestamp."""

    run_id: UUID
    model_name: str
    model_version: str
    feature_version: str
    training_start: datetime
    training_end: datetime
    prediction_timestamp: datetime
    actual: float
    predicted: float


def persist_forecasts(connection: psycopg.Connection, records: list[ForecastRecord]) -> int:
    """Upsert scored forecasts so rerunning a run is idempotent."""
    if not records:
        return 0
    rows = [
        (
            record.run_id,
            record.model_name,
            record.model_version,
            record.feature_version,
            record.training_start,
            record.training_end,
            record.prediction_timestamp,
            record.actual,
            record.predicted,
        )
        for record in records
    ]
    with connection.cursor() as cursor:
        cursor.executemany(
            """
            insert into raw.forecasts (
                run_id, model_name, model_version, feature_version, training_start, training_end,
                prediction_timestamp, actual, predicted
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            on conflict (run_id, model_name, prediction_timestamp) do update set
                actual = excluded.actual,
                predicted = excluded.predicted,
                training_start = excluded.training_start,
                training_end = excluded.training_end,
                persisted_at = now()
            """,
            rows,
        )
    connection.commit()
    return len(rows)
