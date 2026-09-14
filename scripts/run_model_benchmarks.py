"""Run chronological ARIMA and XGBoost benchmark forecasts and persist observations."""

import argparse
from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

import psycopg

from cryptopulse.common.config import get_settings
from cryptopulse.forecasting.evaluation import ForecastMetrics, evaluate_forecast
from cryptopulse.forecasting.mlflow_tracking import log_benchmark
from cryptopulse.forecasting.models import arima_forecast, xgboost_forecast
from cryptopulse.forecasting.persistence import ForecastRecord, persist_forecasts

Forecaster = Callable[[list[float], int], list[float]]


def score_model(
    bars: list[tuple[datetime, float]],
    model_name: str,
    forecaster: Forecaster,
    initial_train_size: int,
) -> tuple[ForecastMetrics, list[ForecastRecord]]:
    """Perform leakage-safe one-step walk-forward scoring for a model."""
    if initial_train_size < 2 or initial_train_size >= len(bars):
        raise ValueError("initial_train_size must leave at least one bar for scoring")
    run_id = uuid4()
    actual: list[float] = []
    predicted: list[float] = []
    records: list[ForecastRecord] = []
    for index in range(initial_train_size, len(bars)):
        train = [close for _, close in bars[:index]]
        estimate = float(forecaster(train, 1)[0])
        timestamp, observed = bars[index]
        actual.append(observed)
        predicted.append(estimate)
        records.append(
            ForecastRecord(
                run_id=run_id,
                model_name=model_name,
                model_version="1",
                feature_version="close_lag_v1",
                training_start=bars[0][0],
                training_end=bars[index - 1][0],
                prediction_timestamp=timestamp,
                actual=observed,
                predicted=estimate,
            )
        )
    return evaluate_forecast(actual, predicted), records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial-train-size", type=int, default=10)
    parser.add_argument(
        "--models", nargs="+", choices=["arima", "xgboost"], default=["arima", "xgboost"]
    )
    parser.add_argument(
        "--skip-mlflow",
        action="store_true",
        help="Persist evaluations without optional MLflow logging",
    )
    args = parser.parse_args()
    settings = get_settings()
    model_functions: dict[str, Forecaster] = {"arima": arima_forecast, "xgboost": xgboost_forecast}
    with psycopg.connect(str(settings.postgres_dsn)) as connection:
        with connection.cursor() as cursor:
            cursor.execute("select bar_start, close from raw.market_bars order by bar_start")
            bars = [(row[0], float(row[1])) for row in cursor.fetchall()]
        for model_name in args.models:
            metrics, records = score_model(
                bars, model_name, model_functions[model_name], args.initial_train_size
            )
            persisted = persist_forecasts(connection, records)
            mlflow_logged = False if args.skip_mlflow else log_benchmark(metrics, model_name)
            print(
                f"model={model_name} observations={persisted} mae={metrics.mae} "
                f"rmse={metrics.rmse} mape={metrics.mape} "
                f"mlflow_logged={mlflow_logged}"
            )


if __name__ == "__main__":
    main()
