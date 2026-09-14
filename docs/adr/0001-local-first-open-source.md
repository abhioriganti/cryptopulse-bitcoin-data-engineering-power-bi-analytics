# ADR 0001: local-first platform with optional Fabric mapping

**Status:** Accepted (2026-09-10)

## Decision

The executable core uses open-source, locally runnable components: Redpanda, MinIO, Spark/Delta, PostgreSQL, dbt, Airflow, MLflow, Prometheus, and Grafana. Microsoft Fabric is documented as an isolated optional deployment path.

## Rationale

The project must be reproducible without paid cloud services or tenant access. This also keeps the core data contract and lakehouse design portable. Fabric remains relevant for an enterprise deployment and Power BI Direct Lake consumption, but it must not prevent local development or testing.

## Consequences

Fabric-specific artifacts must live under `fabric/` and cannot be required by local CI. Deployment documentation will map rather than duplicate core transformations where possible.
