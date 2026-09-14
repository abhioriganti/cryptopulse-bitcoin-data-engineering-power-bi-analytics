# Metric catalog

| Metric | Definition | Source | Notes |
|---|---|---|---|
| Latest BTC Price | Latest available one-minute close | `fact_market_bar` | Not a quoted executable price |
| N-day return | Close change from first available close in period to latest close | `fact_market_bar` | Display as percent; no trading guidance |
| VWAP | Sum(price × volume) / sum(volume) | Gold bar / fact | Null when volume is zero |
| Realized volatility | Standard deviation of simple returns over selected lookback | `fact_market_bar` | Historical statistical measure |
| Forecast MAE | Mean absolute actual-minus-predicted error | `raw.forecasts` | Evaluate with time-ordered windows only |
| Forecast RMSE | Root mean squared actual-minus-predicted error | `raw.forecasts` | More sensitive to large errors |
| Anomaly Count | Count of rolling-z-score flags | `raw.anomalies` | Statistical anomaly, not recommendation |
| Data freshness | Minutes since most recent market bar | serving/semantic model | Depends on selected interval/source |
| Pipeline Success % | Passing reconciliation outcomes / all outcomes | `mart_data_quality` | Run-level quality signal |
| Rejected Record Count | Persisted failed reconciliation/check outcomes | `mart_data_quality` | Not a source-system error total |

All metric definitions are reflected in the Power BI DAX source under `powerbi/dax/`. Measured
benchmark/model values must name their data set, observation window, and execution time.
