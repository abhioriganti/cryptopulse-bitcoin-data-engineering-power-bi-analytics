"""Batch orchestration only; the continuously-running Spark stream is intentionally excluded."""

from datetime import datetime, timedelta

from airflow.decorators import dag, task_group
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {"retries": 2, "retry_delay": timedelta(minutes=5)}


@dag(
    dag_id="cryptopulse_daily_platform",
    start_date=datetime(2024, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["cryptopulse", "batch"],
)
def cryptopulse_daily_platform() -> None:
    """Refresh batch assets; commands run in the project runtime image in deployment."""

    backfill = BashOperator(
        task_id="historical_backfill",
        bash_command="make backfill",
        execution_timeout=timedelta(hours=2),
    )

    @task_group(group_id="quality_and_serving")
    def quality_and_serving() -> list[BashOperator]:
        reconcile = BashOperator(task_id="reconcile", bash_command="make reconcile")
        dbt = BashOperator(task_id="dbt_refresh", bash_command="make dbt")
        reconcile >> dbt
        return [reconcile, dbt]

    maintenance = BashOperator(
        task_id="storage_maintenance",
        bash_command="python scripts/storage_maintenance.py --dry-run",
    )
    backfill >> quality_and_serving() >> maintenance


cryptopulse_daily_platform()
