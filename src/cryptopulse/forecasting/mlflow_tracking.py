"""Optional MLflow logging for measured forecasting benchmarks."""

import logging

from cryptopulse.forecasting.evaluation import ForecastMetrics

logger = logging.getLogger(__name__)


def log_benchmark(metrics: ForecastMetrics, model_name: str = "persistence") -> bool:
    """Log a benchmark when MLflow is installed and reachable; otherwise return false."""
    try:
        import mlflow

        with mlflow.start_run():
            mlflow.log_param("model_name", model_name)
            mlflow.log_metrics({"mae": metrics.mae, "rmse": metrics.rmse})
            if metrics.mape is not None:
                mlflow.log_metric("mape", metrics.mape)
        return True
    except ImportError:
        return False
    except Exception:  # MLflow is optional and must not invalidate persisted evaluation results.
        logger.warning("MLflow benchmark logging failed", exc_info=True)
        return False
