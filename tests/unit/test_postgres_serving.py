from cryptopulse.serving.postgres import UPSERT_MARKET_BARS, upsert_market_bars


class Cursor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[dict[str, object]]]] = []

    def __enter__(self) -> "Cursor":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def executemany(self, sql: str, rows: list[dict[str, object]]) -> None:
        self.calls.append((sql, rows))


class Connection:
    def __init__(self) -> None:
        self.cursor_value = Cursor()
        self.committed = False

    def cursor(self) -> Cursor:
        return self.cursor_value

    def commit(self) -> None:
        self.committed = True


def test_upsert_market_bars_uses_business_key_and_commits() -> None:
    connection = Connection()
    assert upsert_market_bars(connection, [{"provider": "test"}]) == 1
    assert connection.committed
    assert "on conflict (provider, symbol, interval, bar_start)" in UPSERT_MARKET_BARS


def test_upsert_market_bars_skips_empty_batches() -> None:
    connection = Connection()
    assert upsert_market_bars(connection, []) == 0
    assert not connection.committed
