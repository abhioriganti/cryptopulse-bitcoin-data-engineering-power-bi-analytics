# CryptoPulse implementation plan

## Audit summary (Phase 0)

Audited on 2026-09-10. The repository directory contained no files, source code, notebooks, Power BI assets, configuration, or Git repository metadata. There is therefore no reusable, obsolete, or misleading project material in this project directory. The build starts cleanly; no existing PBIX file exists to preserve.

## Phases

| Phase | Scope | Status |
|---|---|---|
| 0 | Audit, architecture, plan, status | Complete |
| 1 | Python skeleton, typed configuration, Compose, contracts, quality primitives, tests | Complete |
| 2 | REST historical ingestion and idempotent persistence | Complete |
| 3 | Streaming provider and Redpanda producer | Complete |
| 4 | Bronze/Silver Spark Structured Streaming | Complete |
| 5 | PostgreSQL serving layer and dbt marts | Complete |
| 6 | Quality history and reconciliation | Complete |
| 7 | Airflow batch orchestration | Complete |
| 8 | Features, forecasting benchmark, MLflow | Complete |
| 9 | Anomaly detection | Complete |
| 10 | FastAPI serving API | Complete |
| 11 | Prometheus/Grafana observability | Planned |
| 12 | Power BI semantic model, DAX, TMDL specifications | In progress |
| 13 | Optional Microsoft Fabric deployment design | Complete |
| 14 | Safe optional AI analytics assistant | Complete |
| 15 | CI/CD, replay/load testing, failure recovery | Complete |
| 16 | Documentation and portfolio polish | In progress |

## Delivery rules

Every phase must add tests, update `STATUS.md`, and record material design choices in `docs/adr/`. No claims about measured throughput, latency, or model accuracy will be added before evidence is produced.
