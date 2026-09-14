# CryptoPulse semantic-model relationships

## Star schema

```mermaid
erDiagram
  DIM_ASSET ||--o{ FACT_MARKET_BAR : asset_key
  DIM_PROVIDER ||--o{ FACT_MARKET_BAR : provider_key
  DIM_DATE ||--o{ FACT_MARKET_BAR : bar_date
  DIM_DATE ||--o{ MART_MARKET_HOURLY : hour_date
  DIM_DATE ||--o{ RAW_FORECASTS : prediction_date
  DIM_DATE ||--o{ RAW_ANOMALIES : event_date
```

| From | Cardinality | To | Active relationship |
|---|---|---|---|
| `Dim Asset[asset_key]` | one-to-many | `Fact Market Bar[asset_key]` | Yes, single direction |
| `Dim Provider[provider_key]` | one-to-many | `Fact Market Bar[provider_key]` | Yes, single direction |
| `Dim Date[date]` | one-to-many | `Fact Market Bar[date_key]` | Yes, single direction |
| `Dim Date[date]` | one-to-many | `Mart Market Hourly[hour_date]` | Yes, single direction |
| `Dim Date[date]` | one-to-many | `Forecasts[prediction_date]` | Inactive if a second forecast date is added |
| `Dim Date[date]` | one-to-many | `Anomalies[event_date]` | Yes, single direction |

Do not create bidirectional fact-to-fact relationships. Use measures for cross-fact metrics. Keep
`Fact Market Bar` at its stated grain; do not relate `Mart Market Hourly` directly to it.
