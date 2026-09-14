# CryptoPulse status

Last updated: 2026-09-11

## Completed

- Phase 0 audit: project directory was empty.
- Architecture and phased plan documented.
- Phase 1: packaging, typed settings, canonical Pydantic event contract, provider abstraction,
  quality primitive, Compose configuration, API health endpoints, and unit-test foundation.
- Phase 2: credential-free Coinbase Exchange backfill, MinIO bucket provisioning, immutable Bronze
  writer, versioned generated JSON Schema, and idempotent replay validation.
- Phase 3: public Coinbase WebSocket adapter, exponential reconnect behavior, Redpanda producer,
  and live broker delivery verification.
- Phase 4: Docker-hosted Spark Structured Streaming from Redpanda to immutable Bronze Delta,
  validated/deduplicated Silver Delta, quarantine Delta, and event-time Gold bar handoff.

## In progress

- Phase 11: Prometheus/Grafana observability and application instrumentation.
- Phase 12: Power BI semantic-model assets and manual Desktop validation.
- Phase 15: CI/CD, replay/load testing, and failure recovery.
- Phase 16: documentation, governance, and portfolio polish.

### Phase 3 verification

- Coinbase Advanced Trade WebSocket subscription produced a real BTC-USD trade.
- `cryptopulse.ingestion.live --max-events 1` published the normalized event to Redpanda.
- `rpk topic consume market-events -n 1` confirmed the key and canonical JSON payload on 2026-09-10.

## Next task

Implement leakage-safe feature generation, time-based forecast baselines, evaluation, and local
MLflow experiment tracking. No trading or profitability claims will be made.

### Phase 5 progress

- PostgreSQL initializes the `raw.market_bars` source contract with a composite business key.
- dbt has typed staging, return calculation, dimensions, a market-bar fact, and an hourly mart.
- The dbt Docker service runs on the Compose network rather than relying on a potentially
  conflicting host PostgreSQL port.
- Verified: `docker compose run --rm dbt build --project-dir dbt --profiles-dir dbt` built 7
  models and passed 20 dbt tests. The source table was empty during this structural validation;
  no market-data or performance result is implied.
- Added `make load-gold`, which reads finalized one-minute Gold Delta bars and upserts them into
  PostgreSQL by `(provider, symbol, interval, bar_start)`. Verified on 2026-09-10: the loader
  connected successfully and completed with `upserted_market_bars=0`. This is expected because
  append-mode window results require the 15-minute event-time watermark to finalize; no synthetic
  market rows were inserted merely to populate the serving layer.
- Refactored Gold's local streaming handoff to a checkpointed update-mode `foreachBatch` Delta
  merge. Bar state is upserted by provider, symbol, currency, interval, and bar start; watermark
  and stateful aggregation remain in effect. This avoids local append-mode window finalization
  delays while retaining idempotent serving behavior.
- End-to-end replay validation passed: a controlled 20-event sequence reached the update-mode
  Gold Delta table (20 rows), `raw.market_bars` in PostgreSQL (20 rows), and dbt's
  `fact_market_bar` (20 rows). `dbt build` completed with 7 models and 20 tests passing.

### Phase 6 verification

- PostgreSQL now retains reconciliation outcomes by run ID, status, difference, and threshold.
- A reconciliation run against the controlled replay passed both critical comparisons: Bronze vs
  Silver plus quarantine, and Gold vs PostgreSQL serving. Both differences were zero.
- dbt's `mart_data_quality` materializes this history for reporting. Verified: dbt built 8 models
  and passed 27 tests, including the persisted reconciliation source and mart tests.

### Phase 7 verification

- The Docker Compose Airflow metadata migration completed successfully against local PostgreSQL.
- Airflow loaded `cryptopulse_daily_platform` from `airflow/dags/cryptopulse_batch.py`.
- The DAG covers finite backfill, reconciliation, dbt refresh, and dry-run storage maintenance;
  it intentionally does not start or stop the permanent Spark streaming service.

### Phase 8 progress

- Leakage-safe trailing features and chronological persistence-baseline evaluation are implemented
  and unit-tested. No random time-series split is used.
- ARIMA and XGBoost adapters now use expanding-window, one-step walk-forward evaluation only.
  The benchmark runner persists each scored prediction with its training window, model version,
  feature version, and run ID in `raw.forecasts`; the local table migration has been applied.
- Measured over ten controlled replay-data observations: ARIMA MAE `0.00012660146239795722`,
  RMSE `0.00015509977021322953`, MAPE `3.013328623873267e-09`; XGBoost MAE and RMSE
  `1.01171875`, MAPE `0.000024080228367073566`. ARIMA emitted convergence warnings on this
  deliberately tiny replay sample. These figures demonstrate persistence and evaluation flow only;
  they are not financial-model quality claims.
- The MLflow client is pinned below version 3 to remain compatible with the local MLflow 2.16
  service. A compatibility-aligned tracking smoke test created a run and then read it back
  successfully. The minimal image emits a missing-Git metadata warning only; metrics persist.

### Phase 8 completion

- Forecast observations are persisted in `raw.forecasts` with run ID, model and feature versions,
  training window, prediction timestamp, actual, and predicted values.
- Persistence, moving-average, ARIMA, and XGBoost benchmarks are evaluated by chronological
  expanding windows. The optional `--skip-mlflow` flag keeps persistence usable if experiment
  tracking is unavailable.

### Phase 9 completion

- A prior-only rolling z-score detector flags unusual simple returns and persists them in
  `raw.anomalies` by detector run ID. It deliberately makes no investment recommendation.
- Controlled replay verification with a demonstration threshold of `1.0` and a three-observation
  window persisted 16 statistical anomalies. This is a detector-path test on replay data, not a
  statement about the real Bitcoin market. Production-like defaults remain a 20-observation window
  and a z-score threshold of 3.0.

### Phase 10 completion

- The local API is a Compose service at `http://localhost:8000`, built from a lightweight API image.
  It exposes health, market, forecast, anomaly, data-quality, and pipeline-health endpoints.
- Serving queries are fixed and parameterized, transaction scope is read-only, endpoints validate
  pagination and intervals, and dependency failures return structured HTTP 503 responses.
- All database-backed endpoints returned HTTP 200 against local PostgreSQL; the host-facing
  `/ready` and `/market/latest` Compose endpoints also returned HTTP 200.

### Phase 11 progress

- The API emits Prometheus request-count and latency histograms with bounded route labels, plus a
  serving-store availability gauge. Metrics are available at `/metrics`.
- Prometheus now scrapes the Compose service directly at `api:8000`, and Grafana provisions the
  `CryptoPulse API Overview` dashboard with request-rate, p95 latency, and serving-store panels.
- Verified: Prometheus queried `cryptopulse_api_requests_total` after collecting real `/ready` and
  `/market/latest` requests. Grafana and Prometheus are available locally at ports 3000 and 9090.

### Phase 12 progress

- Added source-controlled Power BI assets: semantic-model relationship specification, professional
  theme, requested DAX measure definitions, TMDL measure fragment, page specification, and exact
  Desktop/PBIP setup instructions. No `.pbix` has been fabricated.

### Phase 13 completion

- Added an isolated optional Fabric design including Eventstream, Eventhouse/KQL, Lakehouse/OneLake,
  Direct Lake, Real-Time Hub, Queryset, and Activator mapping. KQL operational/data-quality queries
  and a deployment checklist are versioned under `fabric/`. Fabric credentials and access remain an
  external/manual requirement; local execution has no Fabric dependency.

### Phase 14 completion

- Added a no-credential, template-based Analytics Assistant at `POST /assistant/query`. It returns
  answer, exact SQL, tables, metric definition, and result rows for supported curated metrics.
- SQL validation enforces a relation allowlist, one read-only statement, explicit LIMIT, no SQL
  comments, no DDL/DML, transaction read-only mode, and a five-second query timeout. Investment
  advice requests are rejected. The live lowest-MAE query returned the persisted ARIMA result with
  query provenance.

### Phase 15 progress

- Added GitHub Actions CI for Ruff, formatting, mypy, unit tests, and dbt parse. It uses no
  repository secrets; dbt parse receives a non-secret placeholder only because no connection is
  required for parsing.
- Added `scripts/benchmark_api.py`, which writes a timestamped JSON artifact only after real local
  requests complete. The recorded 25-request `/health` benchmark is
  `artifacts/benchmarks/api-latency-20260911T214031Z.json`; it reports measured local latency, not
  throughput or production performance.
- Added `docs/FAILURE_RECOVERY.md` covering restart, duplicate, malformed, late-event, rate-limit,
  and missing-interval experiments. Only previously executed scenarios are marked verified.
- Added a manually triggered Docker Compose integration workflow and pre-commit configuration. The
  integration workflow starts PostgreSQL/API and checks `/ready`; it is intentionally separate from
  the fast PR unit-test workflow.

### Phase 16 progress

- Replaced the early placeholder README with an implementation-accurate overview, local quick start,
  architecture, commands, quality/BI/ML/assistant sections, and measured-evidence caveats.
- Added data dictionary, metric catalog, lineage, governance, portfolio case study, and additional
  architectural decision records. Power BI Desktop and Fabric remain documented manual/external
  steps rather than implied verification.
- A measured replay-data persistence benchmark ran against PostgreSQL: MAE 1.0, RMSE 1.0, and
  MAPE 0.0000238038566293432. These are replay-data baseline results, not trading metrics.
- MLflow local tracking was verified with a successful experiment run. Git metadata warnings from
  the minimal Spark image do not affect the stored parameters or metrics.

### Phase 4 environment finding

- The Silver validation/deduplication transform is implemented and its Spark test is present.
- Java 17 is configured successfully. Apache Spark issue SPARK-53759 caused PySpark 3.5.5 to
  crash under Windows/Python 3.13; the project now requires PySpark 3.5.9 or later.
- Verified on 2026-09-10: PySpark 3.5.9 + Java 17 passed
  `tests/unit/test_silver_transform.py`.
- Delta's package-loading path requires Windows Hadoop `winutils.exe`; CryptoPulse does not ship
  that unverified third-party binary. The executable Delta stream is therefore being moved to the
  project-managed Linux `spark` Compose service, built from Python 3.11 Bookworm plus Java 17.
- Verified: the Compose Spark service starts with Spark 3.5.9 / Java 17, resolves the Delta and
  Kafka connectors, and initializes checkpointed Bronze, Silver, and quarantine Delta locations.
- Live verification: a real Coinbase BTC-USD trade was published to Redpanda while the stream was
  active. Bronze and Silver Delta transaction logs advanced afterward, confirming end-to-end
  persistence. This is functional validation, not a performance benchmark.
- Added checkpointed event-time bar definitions for 1-minute, 5-minute, 15-minute, and hourly
  OHLCV/VWAP outputs under `data/lakehouse/gold_streaming_bars`. They use a 15-minute watermark;
  append-mode rows are emitted only when Spark can finalize the event-time window.
- DLQ verification passed: the malformed OHLC fixture was published to Redpanda and the quarantine
  Delta table contains exactly one row. The fixture was therefore retained rather than silently
  discarded.
- Aggregate verification passed: an explicit-schema Spark test validates one-minute OHLC, volume,
  trade count, and VWAP calculations. Open/close have an event-id tie-breaker for deterministic
  results at equal timestamps.

## Latest validation

- `docker compose config --quiet` passed.
- `py -3.13 -m ruff check src tests` passed.
- `py -3.13 -m ruff format --check src tests` passed.
- `py -3.13 -m mypy src` passed.
- Final Java 17-enabled unit validation passed: 39 tests. The only output warning is an upstream
  FastAPI/Starlette TestClient deprecation warning; no project test failed or skipped.
- `python -m cryptopulse.ingestion.backfill --help` passed.
- `scripts/export_contract_schema.py` generated a 4,248-byte JSON Schema artifact.
- Historical backfill persisted 25 bars to MinIO; immediate replay persisted 0 and detected 25
  duplicates. This is a functional result, not a throughput benchmark.
- Redpanda live integration delivered and consumed one real BTC-USD trade. This is functional
  validation, not a throughput benchmark.
- Phase 4 quality gate with Java 17: Ruff checks and format check passed, mypy passed, and the
  complete unit suite passed: 17 tests (one unrelated FastAPI dependency deprecation warning).
- Phase 5 dbt structural validation passed: 7 models built and 20 tests passed against an empty
  initialized PostgreSQL source table.
- Historical-serving validation on 2026-09-13: a bounded Coinbase BTC-USD backfill for
  2024-01-01 through 2024-01-08 persisted 144 new Bronze events (25 were prior duplicates) and
  idempotently upserted 169 one-hour serving bars. dbt then rebuilt successfully with 35 passing
  tests. This is functional data-path evidence, not a throughput benchmark.
- The bounded backfill command now exposes `--load-serving` for the explicit local historical
  serving path. A dbt uniqueness failure exposed an `hour_of_day` attribute incorrectly included
  in the date dimension's distinct projection; it was removed so `dim_date` is one row per date.
- Manual Power BI validation completed with four saved report pages: Executive Market Overview,
  Data Quality & Reliability, Forecasting, and Volatility & Risk. Their real Desktop screenshots
  are versioned under `powerbi/screenshots/`; forecasting and anomaly pages carry controlled-replay
  disclaimers where applicable.

## Known external/manual requirements

- Docker Desktop is required to start the local platform.
- Power BI Desktop is required to create/validate a report; no `.pbix` will be fabricated.
- Microsoft Fabric access is only needed for the optional Fabric deployment path.
