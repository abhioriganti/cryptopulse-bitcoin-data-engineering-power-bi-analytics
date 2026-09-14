from datetime import UTC, datetime, timedelta

import pytest

from cryptopulse.anomalies.rolling_zscore import detect_rolling_zscore


def test_detect_rolling_zscore_uses_only_prior_window() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    observations = [
        (start + timedelta(minutes=index), value) for index, value in enumerate([1, 2, 1, 10])
    ]

    anomalies = detect_rolling_zscore(observations, window=3, threshold=2.0)

    assert len(anomalies) == 1
    assert anomalies[0].timestamp == observations[-1][0]
    assert anomalies[0].z_score > 2.0


def test_detect_rolling_zscore_validates_parameters() -> None:
    with pytest.raises(ValueError):
        detect_rolling_zscore([], window=1)
