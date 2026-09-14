# Data contract and schema evolution

`MarketEvent` is the versioned, provider-neutral contract at the boundary between ingestion and the broker. Its Pydantic JSON Schema is generated from `cryptopulse.contracts.MarketEvent` and committed at `schemas/market_event.v1.json`. Regenerate it with `make schema`. The current contract version is `1.0.0`.

## Compatibility rules

- Additive optional fields are backward compatible in a minor version.
- Removing a field, changing its meaning, or making an optional field required is a breaking major-version change.
- Producers set `schema_version`; consumers validate it and route unsupported versions to quarantine.
- Raw Bronze payloads are retained so events can be replayed through a newer normalizer.

## Validation path

Pydantic rejects malformed source-normalized events before publish. Spark repeats type and business-rule checks in Silver, preserving failures with a reason code and run identifier in a quarantine table. dbt and batch expectations later record quality outcomes historically in Gold.
