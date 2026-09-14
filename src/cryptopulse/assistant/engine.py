"""Deterministic metric-template assistant with query provenance."""

from dataclasses import dataclass
from typing import Any

import psycopg
from psycopg.rows import dict_row

from cryptopulse.assistant.sql_safety import validate_read_only_sql


@dataclass(frozen=True)
class AssistantResponse:
    """An answer and the exact read-only query provenance used to produce it."""

    answer: str
    sql: str
    tables_used: list[str]
    metric_definition: str
    rows: list[dict[str, Any]]


METRIC_TEMPLATES: dict[str, tuple[str, str, list[str]]] = {
    "highest volatility": (
        """
        select bar_start::date as day, stddev_samp(simple_return) as realized_volatility
        from analytics.fact_market_bar
        where bar_start >= date_trunc('month', now()) and interval = '1 minute'
        group by 1 order by realized_volatility desc nulls last limit 1
        """,
        (
            "Realized volatility is the sample standard deviation of one-minute simple returns "
            "per day."
        ),
        ["analytics.fact_market_bar"],
    ),
    "data-quality failures": (
        """
        select count(*) as failures from raw.reconciliation_results
        where status = 'fail' and checked_at::date = current_date - interval '1 day' limit 1
        """,
        "A data-quality failure is a persisted reconciliation result whose status is fail.",
        ["raw.reconciliation_results"],
    ),
    "7-day return": (
        """
        with prices as (
          select bar_start, close from analytics.fact_market_bar
          where interval = '1 minute' and bar_start >= now() - interval '7 days'
        )
        select (last_value(close) over ordered - first_value(close) over ordered)
               / nullif(first_value(close) over ordered, 0) as return_7d
        from prices
        window ordered as (
          order by bar_start rows between unbounded preceding and unbounded following
        )
        order by bar_start desc limit 1
        """,
        (
            "Seven-day return is the percentage change from the first available one-minute close "
            "to the latest close."
        ),
        ["analytics.fact_market_bar"],
    ),
    "lowest mae": (
        """
        select model_name, avg(abs(actual - predicted)) as mae from raw.forecasts
        group by model_name order by mae asc limit 1
        """,
        (
            "Forecast MAE is the mean absolute difference between persisted actual and "
            "predicted values."
        ),
        ["raw.forecasts"],
    ),
}


def answer_question(question: str, dsn: str, row_limit: int = 100) -> AssistantResponse:
    """Answer a supported analytic question using a fixed query template and provenance."""
    if row_limit < 1 or row_limit > 1_000:
        raise ValueError("row_limit must be between 1 and 1000")
    normalized_question = question.casefold()
    matched = next((key for key in METRIC_TEMPLATES if key in normalized_question), None)
    if matched is None:
        raise ValueError(
            "question is unsupported; ask about volatility, quality failures, "
            "7-day return, or lowest MAE"
        )
    sql, definition, tables = METRIC_TEMPLATES[matched]
    safe_sql = validate_read_only_sql(sql)
    with psycopg.connect(dsn, row_factory=dict_row) as connection:
        connection.execute("set default_transaction_read_only = on")
        connection.execute("set local statement_timeout = '5s'")
        with connection.cursor() as cursor:
            cursor.execute(safe_sql)
            rows = list(cursor.fetchmany(row_limit))
    answer = "No matching rows were available." if not rows else f"{matched.title()}: {rows[0]}"
    return AssistantResponse(answer, safe_sql, tables, definition, rows)
