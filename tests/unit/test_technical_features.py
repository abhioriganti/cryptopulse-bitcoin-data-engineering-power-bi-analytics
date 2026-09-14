import pytest

from cryptopulse.features.technical import trailing_features


def test_features_do_not_need_future_observations() -> None:
    result = trailing_features([100.0, 110.0, 121.0], window=2)
    assert result[0]["sma"] == 100.0
    assert result[1]["simple_return"] == pytest.approx(0.1)
    assert result[1]["sma"] == 105.0
