# CryptoPulse portfolio case study

## Problem and constraints

CryptoPulse demonstrates how a local, reproducible market-data platform can support real-time
engineering, analytics, BI, and time-series experimentation without paid cloud infrastructure.
The project deliberately avoids presenting Bitcoin forecasts as trading advice.

## Architecture and trade-offs

Redpanda provides a Kafka-compatible local broker; MinIO and Delta retain replayable lakehouse
layers; Docker Spark handles event-time transformations; PostgreSQL/dbt provide a familiar serving
surface; Power BI consumes a documented star schema. Airflow schedules finite work rather than
operating a permanent streaming process. Fabric is documented as an isolated optional path.

The main local trade-off is operational simplicity over distributed-scale benchmarking. No claim is
made about production throughput, availability, or cloud cost.

## Data quality and reliability

The contract validates incoming events, Silver applies deterministic deduplication and OHLC checks,
and invalid rows go to quarantine. Reconciliation compares Bronze/Silver/quarantine and Gold/serving
counts. A malformed fixture was verified in quarantine; a controlled replay reconciliation passed
with zero count difference.

## Forecasting and anomalies

Features use trailing information only. Persistence, moving-average, ARIMA, and XGBoost evaluation
use chronological expanding windows. Replay-data results are stored with model/run/feature/training
provenance and must not be interpreted as market performance. A rolling z-score detector persists
statistical return anomalies.

## Measured evidence

The repository contains one actual local API latency artifact under `artifacts/benchmarks/` from 25
health requests. It records the machine-local execution time and is not a benchmark of full
end-to-end stream throughput. The README and status file distinguish measured evidence from planned
capabilities.

## What would change at larger scale

At larger scale, separate Spark executors/storage from developer Compose, use managed secret
rotation, introduce data contracts in a registry, run dedicated load tests, deploy private networked
serving/BI access, and add formal alert SLOs after collecting an operational baseline.
