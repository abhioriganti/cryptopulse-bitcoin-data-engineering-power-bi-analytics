"""Chronological baseline benchmark; no random time-series splitting."""

from cryptopulse.forecasting.evaluation import (
    ForecastMetrics,
    evaluate_forecast,
    persistence_baseline,
)


def run_persistence_benchmark(closes: list[float]) -> ForecastMetrics:
    """Predict each close from its preceding observed close and evaluate chronologically."""
    return evaluate_forecast(closes[1:], persistence_baseline(closes))


def moving_average_baseline(values: list[float], window: int = 3) -> list[float]:
    """One-step trailing moving-average predictions without future observations."""
    if len(values) <= window:
        raise ValueError("values must exceed the moving-average window")
    return [sum(values[index - window : index]) / window for index in range(window, len(values))]


def run_moving_average_benchmark(closes: list[float], window: int = 3) -> ForecastMetrics:
    """Evaluate a trailing moving-average baseline on the chronological holdout."""
    return evaluate_forecast(closes[window:], moving_average_baseline(closes, window))
