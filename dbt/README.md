# dbt analytics layer

dbt owns SQL transformations and metric-ready serving models in PostgreSQL. It does not duplicate
Spark's raw-event validation: its input contract is the validated Gold bar handoff loaded into
`raw.market_bars`.

Set `CRYPTOPULSE_DBT_PASSWORD` in your shell before running `dbt debug`, `dbt build`, or
`make dbt`. The included `profiles.yml` contains connection settings but no password; teams may
instead place an equivalent profile under `%USERPROFILE%\.dbt`.

Model layers are `staging` (typed source projection), `intermediate` (returns), and `marts`
(dimensions, facts, and executive aggregates). Tests are deliberately attached to model grain and
business keys rather than treated as a generic SQL lint step.
