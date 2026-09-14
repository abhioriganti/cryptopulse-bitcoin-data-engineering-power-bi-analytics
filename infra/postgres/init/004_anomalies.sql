create table if not exists raw.anomalies (
    run_id uuid not null,
    metric_name text not null,
    event_timestamp timestamptz not null,
    value double precision not null,
    z_score double precision not null,
    threshold double precision not null,
    persisted_at timestamptz not null default now(),
    primary key (run_id, metric_name, event_timestamp)
);
