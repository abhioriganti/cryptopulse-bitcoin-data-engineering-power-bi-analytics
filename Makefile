.DEFAULT_GOAL := help

PYTHON ?= python

.PHONY: help setup up down test lint format api stream backfill replay schema load-gold reconcile anomalies quality dbt train benchmark demo
help:
	@echo "Targets: setup up down test lint format api stream backfill replay schema load-gold reconcile anomalies dbt train benchmark demo"

setup:
	$(PYTHON) -m pip install -e ".[dev]"

up:
	docker compose up -d

down:
	docker compose down

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m ruff format --check src tests

format:
	$(PYTHON) -m ruff check --fix src tests
	$(PYTHON) -m ruff format src tests

api:
	$(PYTHON) -m uvicorn cryptopulse.api.main:app --reload --port 8000

backfill:
	$(PYTHON) -m cryptopulse.ingestion.backfill --help

replay:
	$(PYTHON) scripts/replay_market_data.py --minutes 20

schema:
	$(PYTHON) scripts/export_contract_schema.py

stream:
	docker compose exec spark spark-submit --packages io.delta:delta-spark_2.12:3.3.3,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.9 scripts/run_streaming_pipeline.py

load-gold:
	docker compose exec spark spark-submit --packages io.delta:delta-spark_2.12:3.3.3 scripts/load_gold_bars.py

reconcile:
	docker compose exec spark spark-submit --packages io.delta:delta-spark_2.12:3.3.3 scripts/run_reconciliation.py

quality train demo:
	@echo "$@ is planned; see IMPLEMENTATION_PLAN.md and STATUS.md"

benchmark:
	$(PYTHON) scripts/benchmark_api.py

anomalies:
	docker compose exec spark python scripts/run_anomaly_detection.py

dbt:
	docker compose run --rm dbt build --project-dir dbt --profiles-dir dbt
