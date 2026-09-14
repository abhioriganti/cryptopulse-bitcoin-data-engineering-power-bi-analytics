"""Leakage-safe forecast evaluation for chronologically ordered observations."""

from collections.abc import Callable
from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class ForecastMetrics:
    mae: float
    rmse: float
    mape: float | None
    directional_accuracy: float | None


def evaluate_forecast(actual: list[float], predicted: list[float]) -> ForecastMetrics:
    """Evaluate aligned chronological values; callers must not randomly shuffle time series."""
    if not actual or len(actual) != len(predicted):
        raise ValueError("actual and predicted must be non-empty and equally sized")
    errors = [observed - estimate for observed, estimate in zip(actual, predicted, strict=True)]
    mae = sum(abs(error) for error in errors) / len(errors)
    rmse = sqrt(sum(error**2 for error in errors) / len(errors))
    nonzero = [
        abs(error / observed) for observed, error in zip(actual, errors, strict=True) if observed
    ]
    mape = sum(nonzero) / len(nonzero) if nonzero else None
    if len(actual) < 2:
        directional_accuracy = None
    else:
        matched = sum(
            (actual[index] - actual[index - 1]) * (predicted[index] - predicted[index - 1]) >= 0
            for index in range(1, len(actual))
        )
        directional_accuracy = matched / (len(actual) - 1)
    return ForecastMetrics(mae, rmse, mape, directional_accuracy)


def persistence_baseline(values: list[float]) -> list[float]:
    """One-step naive baseline using only the preceding observed value."""
    if len(values) < 2:
        raise ValueError("at least two values are required")
    return values[:-1]


def walk_forward(
    values: list[float],
    initial_train_size: int,
    forecaster: Callable[[list[float], int], list[float]],
) -> ForecastMetrics:
    """Evaluate one-step predictions by refitting only on observations available at each step."""
    if initial_train_size < 2 or initial_train_size >= len(values):
        raise ValueError("initial_train_size must leave at least one test observation")
    actual: list[float] = []
    predicted: list[float] = []
    for index in range(initial_train_size, len(values)):
        predicted.append(float(forecaster(values[:index], 1)[0]))
        actual.append(values[index])
    return evaluate_forecast(actual, predicted)
