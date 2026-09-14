"""Fixed, parameterized read-only queries over CryptoPulse serving tables."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg.rows import dict_row


class MarketRepository:
    """Read-only access to curated PostgreSQL serving data."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    @contextmanager
    def _connection(self) -> Iterator[psycopg.Connection[Any]]:
        with psycopg.connect(self.dsn, row_factory=dict_row) as connection:
            connection.execute("set default_transaction_read_only = on")
            yield connection

    def ping(self) -> bool:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute("select 1")
            return cursor.fetchone() is not None

    def latest_market_bar(self) -> dict[str, Any] | None:
        return self._one("select * from raw.market_bars order by bar_start desc limit 1")

    def market_history(self, interval: str, limit: int, offset: int) -> list[dict[str, Any]]:
        return self._many(
            """
            select * from raw.market_bars where interval = %s
            order by bar_start desc limit %s offset %s
            """,
            (interval, limit, offset),
        )

    def latest_forecasts(self, limit: int) -> list[dict[str, Any]]:
        return self._many(
            "select * from raw.forecasts order by persisted_at desc limit %s", (limit,)
        )

    def anomalies(self, limit: int, offset: int) -> list[dict[str, Any]]:
        return self._many(
            "select * from raw.anomalies order by event_timestamp desc limit %s offset %s",
            (limit, offset),
        )

    def quality_results(self, limit: int) -> list[dict[str, Any]]:
        return self._many(
            "select * from raw.reconciliation_results order by checked_at desc limit %s", (limit,)
        )

    def pipeline_health(self) -> dict[str, Any]:
        return (
            self._one(
                """
            select max(bar_start) as latest_market_bar,
                   count(*) filter (where status = 'pass') as passed_reconciliations,
                   count(*) as reconciliation_count
            from raw.reconciliation_results full join raw.market_bars on false
            """
            )
            or {}
        )

    def _one(self, query: str, params: tuple[object, ...] = ()) -> dict[str, Any] | None:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def _many(self, query: str, params: tuple[object, ...]) -> list[dict[str, Any]]:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, params)
            return list(cursor.fetchall())
