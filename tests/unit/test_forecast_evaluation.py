import pytest

from cryptopulse.forecasting.evaluation import evaluate_forecast, persistence_baseline, walk_forward


def test_evaluate_forecast_calculates_metrics() -> None:
    metrics = evaluate_forecast([100.0, 110.0], [90.0, 120.0])
    assert metrics.mae == 10.0
    assert metrics.rmse == 10.0
    assert metrics.directional_accuracy == 1.0


def test_persistence_baseline_requires_history() -> None:
    with pytest.raises(ValueError):
        persistence_baseline([100.0])


def test_walk_forward_trains_on_chronological_prefix_only() -> None:
    seen_training_sizes: list[int] = []

    def forecaster(train: list[float], _: int) -> list[float]:
        seen_training_sizes.append(len(train))
        return [train[-1]]

    walk_forward([1.0, 2.0, 3.0, 4.0], initial_train_size=2, forecaster=forecaster)
    assert seen_training_sizes == [2, 3]
