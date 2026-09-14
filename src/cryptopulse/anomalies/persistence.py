"""PostgreSQL persistence for statistical anomaly records."""

from uuid import UUID

import psycopg

from cryptopulse.anomalies.rolling_zscore import StatisticalAnomaly


def persist_anomalies(
    connection: psycopg.Connection, run_id: UUID, anomalies: list[StatisticalAnomaly]
) -> int:
    """Persist a deterministic detector run without silently discarding observations."""
    if not anomalies:
        return 0
    with connection.cursor() as cursor:
        cursor.executemany(
            """
            insert into raw.anomalies (
                run_id, metric_name, event_timestamp, value, z_score, threshold
            )
            values (%s, %s, %s, %s, %s, %s)
            on conflict (run_id, metric_name, event_timestamp) do update set
                value = excluded.value,
                z_score = excluded.z_score,
                threshold = excluded.threshold,
                persisted_at = now()
            """,
            [
                (run_id, item.metric_name, item.timestamp, item.value, item.z_score, item.threshold)
                for item in anomalies
            ],
        )
    connection.commit()
    return len(anomalies)
