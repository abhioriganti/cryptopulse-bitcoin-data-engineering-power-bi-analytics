"""Run and optionally track a chronological persistence forecast benchmark."""

import psycopg

from cryptopulse.common.config import get_settings
from cryptopulse.forecasting.benchmark import run_persistence_benchmark
from cryptopulse.forecasting.mlflow_tracking import log_benchmark


def main() -> None:
    settings = get_settings()
    with psycopg.connect(str(settings.postgres_dsn)) as connection:
        with connection.cursor() as cursor:
            cursor.execute("select close from raw.market_bars order by bar_start")
            closes = [float(row[0]) for row in cursor.fetchall()]
    metrics = run_persistence_benchmark(closes)
    try:
        import mlflow

        mlflow.set_tracking_uri(str(settings.mlflow_tracking_uri))
    except ImportError:
        pass
    print(f"mae={metrics.mae} rmse={metrics.rmse} mape={metrics.mape}")
    print(f"mlflow_logged={log_benchmark(metrics)}")


if __name__ == "__main__":
    main()
