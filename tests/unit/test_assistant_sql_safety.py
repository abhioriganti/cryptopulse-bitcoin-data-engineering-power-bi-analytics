import pytest

from cryptopulse.assistant.sql_safety import validate_read_only_sql


def test_safe_query_requires_allowlisted_relation_and_limit() -> None:
    query = validate_read_only_sql("select * from raw.forecasts limit 10")
    assert query == "select * from raw.forecasts limit 10"


@pytest.mark.parametrize(
    "sql",
    [
        "delete from raw.forecasts",
        "select * from pg_catalog.pg_tables limit 1",
        "select * from raw.forecasts",
        "select * from raw.forecasts; drop table raw.forecasts",
    ],
)
def test_unsafe_sql_is_rejected(sql: str) -> None:
    with pytest.raises(ValueError):
        validate_read_only_sql(sql)
