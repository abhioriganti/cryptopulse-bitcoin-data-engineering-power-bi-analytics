# ADR 0003: PostgreSQL serving layer and dbt analytics marts

## Status

Accepted.

## Context and decision

Delta is the processing/lakehouse format, while local Power BI and API development benefit from a
simple relational serving surface. PostgreSQL receives idempotent Gold bar upserts. dbt owns the
SQL-based dimensions, facts, returns, and reporting marts on PostgreSQL.

## Consequences

This adds a serving handoff to operate and reconcile, but makes SQL testing, API queries, and Power
BI connections approachable. Delta remains the replayable processing truth; PostgreSQL is not used
as the raw ingestion source.
