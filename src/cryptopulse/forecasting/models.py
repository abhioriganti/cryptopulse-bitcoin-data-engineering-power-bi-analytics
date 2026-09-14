"""Optional statistical and gradient-boosted forecasting adapters."""


def arima_forecast(train: list[float], horizon: int) -> list[float]:
    """Fit ARIMA only on the chronological training window."""
    try:
        from statsmodels.tsa.arima.model import ARIMA  # type: ignore[import-not-found]
    except ImportError as error:
        raise RuntimeError("Install cryptopulse[ml] with statsmodels to run ARIMA") from error
    return list(ARIMA(train, order=(1, 1, 1)).fit().forecast(steps=horizon))


def xgboost_forecast(train: list[float], horizon: int, lags: int = 3) -> list[float]:
    """Recursive XGBoost forecast using only lagged training observations."""
    if len(train) <= lags:
        raise ValueError("training history must exceed lags")
    try:
        from xgboost import XGBRegressor
    except ImportError as error:
        raise RuntimeError("Install cryptopulse[ml] to run XGBoost") from error
    features = [train[index - lags : index] for index in range(lags, len(train))]
    targets = train[lags:]
    model = XGBRegressor(n_estimators=50, max_depth=3, random_state=42)
    model.fit(features, targets)
    history = train.copy()
    forecast: list[float] = []
    for _ in range(horizon):
        value = float(model.predict([history[-lags:]])[0])
        forecast.append(value)
        history.append(value)
    return forecast
