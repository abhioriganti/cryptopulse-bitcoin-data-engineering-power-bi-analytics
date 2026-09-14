# Data dictionary

| Layer/table | Grain | Key fields | Purpose |
|---|---|---|---|
| Bronze Delta | One received source event | `event_id`, provider, ingested timestamp | Immutable raw replay source including payload/metadata |
| Silver Delta | One validated canonical market event | deterministic event key | Typed, normalized, deduplicated accepted event |
| Quarantine Delta | One rejected event | event ID + rejection reason | Retains contract/quality failures |
| Gold market bars | Provider + symbol + interval + bar start | provider, symbol, currency, interval, bar start | OHLCV, trade count, VWAP aggregation |
| `raw.market_bars` | Same as Gold bar | provider, symbol, interval, bar start | PostgreSQL serving handoff |
| `analytics.fact_market_bar` | Same as Gold bar | `market_bar_key` | dbt analytics fact with returns |
| `analytics.dim_asset` | Asset + currency | `asset_key` | Asset conformed dimension |
| `analytics.dim_provider` | Provider | `provider_key` | Provider conformed dimension |
| `analytics.dim_date` | Calendar date | `date_key` | Date dimension |
| `analytics.mart_market_hourly` | Provider + symbol + hour | provider, symbol, hour start | Hourly reporting aggregate |
| `analytics.mart_data_quality` | Reconciliation check/run | reconciliation ID | Historical layer-reconciliation outcomes |
| `raw.forecasts` | Forecast model + run + prediction timestamp | run ID, model, timestamp | Actual/predicted scored observations |
| `raw.anomalies` | Detector run + metric + timestamp | run ID, metric, timestamp | Statistical anomaly observations |
| `raw.reconciliation_results` | Reconciliation check/run | reconciliation ID | Count comparison, threshold, status |

## Canonical event fields

The authoritative Pydantic model and generated JSON Schema are in `src/cryptopulse/contracts/` and
`schemas/market_event.v1.json`. Required event identity/time fields are `event_id`, `provider`,
`symbol`, `event_type`, `event_timestamp`, `ingested_at`, and `schema_version`. Numeric market
fields are nullable where they do not apply to an event type.
