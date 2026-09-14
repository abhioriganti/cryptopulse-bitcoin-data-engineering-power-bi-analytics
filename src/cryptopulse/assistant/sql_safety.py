"""Strict SQL safety controls for analytics-assistant queries."""

import re

ALLOWED_TABLES = {
    "analytics.fact_market_bar",
    "raw.anomalies",
    "raw.forecasts",
    "raw.reconciliation_results",
}
FORBIDDEN_TOKENS = {
    "alter",
    "copy",
    "create",
    "delete",
    "drop",
    "grant",
    "insert",
    "merge",
    "revoke",
    "truncate",
    "update",
}


def validate_read_only_sql(sql: str) -> str:
    """Accept one SELECT/CTE query referencing only approved curated relations."""
    normalized = " ".join(sql.strip().rstrip(";").split())
    lowered = normalized.lower()
    if not lowered.startswith(("select ", "with ")):
        raise ValueError("only SELECT or CTE queries are permitted")
    if ";" in normalized or "--" in normalized or "/*" in normalized:
        raise ValueError("multiple statements and SQL comments are not permitted")
    tokens = set(re.findall(r"\b[a-z]+\b", lowered))
    if tokens & FORBIDDEN_TOKENS:
        raise ValueError("DDL and DML are not permitted")
    referenced = set(re.findall(r"\b(?:analytics|raw)\.[a-z_]+\b", lowered))
    if not referenced or not referenced <= ALLOWED_TABLES:
        raise ValueError("query references a relation outside the analytics allowlist")
    if not re.search(r"\blimit\s+\d+\b", lowered):
        raise ValueError("queries must contain an explicit row limit")
    return normalized
