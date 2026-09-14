"""Idempotent PostgreSQL upsert for finalized Gold market bars."""

from collections.abc import Iterable
from typing import Any

UPSERT_MARKET_BARS = """
insert into raw.market_bars (
    provider, symbol, currency, interval, bar_start, bar_end,
    open, high, low, close, volume, trade_count, vwap
)
values (
    %(provider)s, %(symbol)s, %(currency)s, %(interval)s, %(bar_start)s, %(bar_end)s,
    %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s, %(trade_count)s, %(vwap)s
)
on conflict (provider, symbol, interval, bar_start) do update set
bar_end = excluded.bar_end, open = excluded.open, high = excluded.high, low = excluded.low,
close = excluded.close, volume = excluded.volume, trade_count = excluded.trade_count,
vwap = excluded.vwap, loaded_at = now()
"""


def upsert_market_bars(connection: Any, rows: Iterable[dict[str, Any]]) -> int:
    """Upsert a batch using the Gold table's deterministic business key."""
    payload = list(rows)
    if not payload:
        return 0
    with connection.cursor() as cursor:
        cursor.executemany(UPSERT_MARKET_BARS, payload)
    connection.commit()
    return len(payload)
