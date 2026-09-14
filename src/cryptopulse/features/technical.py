"""Features calculated from trailing observations only."""

from math import log, sqrt


def trailing_features(closes: list[float], window: int = 7) -> list[dict[str, float | None]]:
    """Return features at each timestamp without referencing a future close."""
    if window < 2:
        raise ValueError("window must be at least two")
    features: list[dict[str, float | None]] = []
    for index, close in enumerate(closes):
        prior = closes[index - 1] if index else None
        simple_return = (close / prior) - 1 if prior else None
        history = closes[max(0, index - window + 1) : index + 1]
        sma = sum(history) / len(history)
        returns = [
            log(history[position] / history[position - 1])
            for position in range(1, len(history))
            if history[position - 1] > 0
        ]
        volatility = (
            sqrt(
                sum((value - sum(returns) / len(returns)) ** 2 for value in returns) / len(returns)
            )
            if returns
            else None
        )
        features.append(
            {"close": close, "simple_return": simple_return, "sma": sma, "volatility": volatility}
        )
    return features
