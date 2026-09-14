"""Leakage-safe rolling z-score anomaly detection."""

from dataclasses import dataclass
from datetime import datetime
from math import sqrt


@dataclass(frozen=True)
class StatisticalAnomaly:
    """A return whose magnitude is unusual relative to its prior rolling history."""

    timestamp: datetime
    metric_name: str
    value: float
    z_score: float
    threshold: float


def detect_rolling_zscore(
    observations: list[tuple[datetime, float]], window: int = 20, threshold: float = 3.0
) -> list[StatisticalAnomaly]:
    """Flag observations against a prior-only rolling mean and sample standard deviation."""
    if window < 2:
        raise ValueError("window must be at least two")
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    anomalies: list[StatisticalAnomaly] = []
    for index, (timestamp, value) in enumerate(observations):
        history = [prior_value for _, prior_value in observations[max(0, index - window) : index]]
        if len(history) < window:
            continue
        mean = sum(history) / len(history)
        variance = sum((item - mean) ** 2 for item in history) / (len(history) - 1)
        if variance == 0:
            continue
        z_score = (value - mean) / sqrt(variance)
        if abs(z_score) >= threshold:
            anomalies.append(
                StatisticalAnomaly(timestamp, "simple_return", value, z_score, threshold)
            )
    return anomalies
