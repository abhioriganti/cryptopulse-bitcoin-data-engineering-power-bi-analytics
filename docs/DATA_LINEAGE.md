# Data lineage

```mermaid
flowchart LR
  C[Coinbase REST/WebSocket] --> I[Async provider adapters]
  I --> K[Redpanda market-events]
  K --> B[Bronze Delta]
  K --> S[Silver Delta]
  S --> Q[Quarantine Delta]
  S --> G[Gold OHLCV bars]
  G --> P[raw.market_bars]
  P --> D[dbt dimensions, facts, marts]
  D --> BI[Power BI semantic model]
  P --> F[Forecast scoring]
  F --> FR[raw.forecasts / MLflow]
  P --> A[Rolling anomaly detector]
  A --> AR[raw.anomalies]
  B --> R[Reconciliation results]
  S --> R
  G --> R
  R --> D
```

## Ownership

| Asset | Owner role | Change control |
|---|---|---|
| Event contract | Data engineering | Versioned JSON Schema and Pydantic tests |
| Silver rules/checkpoints | Streaming engineering | Code review plus Spark/replay validation |
| dbt marts | Analytics engineering | dbt parse/build/tests |
| Forecast/anomaly outputs | ML engineering | time-ordered evaluation and persisted provenance |
| Semantic model/DAX | BI engineering | PBIP/TMDL review and Desktop validation |
