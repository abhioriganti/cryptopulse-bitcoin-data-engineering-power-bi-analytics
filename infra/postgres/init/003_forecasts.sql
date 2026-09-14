create table if not exists raw.forecasts (
    run_id uuid not null,
    model_name text not null,
    model_version text not null,
    feature_version text not null,
    training_start timestamptz not null,
    training_end timestamptz not null,
    prediction_timestamp timestamptz not null,
    actual double precision not null,
    predicted double precision not null,
    persisted_at timestamptz not null default now(),
    primary key (run_id, model_name, prediction_timestamp)
);
