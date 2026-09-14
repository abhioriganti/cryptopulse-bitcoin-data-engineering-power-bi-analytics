# Data governance

## Classification and retention

Bitcoin market data in this project is public market information. It is classified as **internal
analytics data** after ingestion because derived quality, model, and operational metadata belongs to
the project. API keys, passwords, and tokens are **secret** and must live only in environment
variables or managed secret stores.

Bronze raw events are retained long enough to support replay and incident investigation. Silver,
Gold, serving, and model records may be compacted only through an approved maintenance workflow.
Do not delete checkpoints or raw data to resolve a pipeline issue without first capturing evidence.

## Controls

- `.env` is excluded from source control; `.env.example` contains placeholders only.
- Pydantic validates source contracts, Spark validates event quality, dbt validates serving models,
  and reconciliation outcomes are persisted.
- Assistant queries are restricted to read-only, allowlisted relations with timeouts and row limits.
- Schema changes require an additive/compatible version where possible, generated JSON Schema, test
  coverage, a documented owner, and replay/backfill assessment.
- Power BI reports should use least-privilege database access and never embed credentials.

## Source inventory

| Source | Use | Credential status |
|---|---|---|
| Coinbase Exchange REST | Historical backfill | Public endpoint by default |
| Coinbase WebSocket | Live market events | Public endpoint by default |
| Optional alternate providers | Configurable adapters | Environment-managed if needed |
