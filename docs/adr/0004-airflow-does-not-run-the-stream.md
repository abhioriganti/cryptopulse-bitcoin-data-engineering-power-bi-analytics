# ADR 0004: Airflow does not operate the permanent stream

## Status

Accepted.

## Decision

Airflow schedules finite backfills, quality checks, dbt refreshes, forecasting, reconciliation, and
maintenance. The continuously running Spark streaming query is independently managed through its
checkpoint and container lifecycle.

## Rationale

Airflow task retries and DAG lifecycle do not replace streaming checkpoint/recovery semantics.
Separating these concerns prevents a scheduler retry from being mistaken for streaming correctness.
