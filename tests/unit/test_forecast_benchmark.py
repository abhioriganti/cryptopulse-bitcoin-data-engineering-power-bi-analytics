from cryptopulse.forecasting.benchmark import (
    moving_average_baseline,
    run_persistence_benchmark,
)


def test_persistence_benchmark_uses_chronological_baseline() -> None:
    metrics = run_persistence_benchmark([100.0, 110.0, 121.0])
    assert metrics.mae == 10.5


def test_moving_average_uses_only_prior_values() -> None:
    assert moving_average_baseline([1.0, 2.0, 3.0, 9.0], window=3) == [2.0]
