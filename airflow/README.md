# Airflow

Airflow orchestrates finite, retryable batch operations only. The continuously-running Redpanda to
Spark Structured Streaming job is launched separately with `make stream`; scheduling it in an
Airflow task would create duplicate consumers and unreliable lifecycle management.

`cryptopulse_daily_platform` defines historical backfill, reconciliation, dbt refresh, and dry-run
storage maintenance as a dependency graph. The production Airflow image must include the project
runtime and invoke the same Make targets used locally. DAG loading is intentionally a later Docker
integration step; no claim is made that an Airflow scheduler has been started yet.
