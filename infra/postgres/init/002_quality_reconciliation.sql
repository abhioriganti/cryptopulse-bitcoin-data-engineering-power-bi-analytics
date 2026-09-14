create table if not exists raw.reconciliation_results (
    reconciliation_id uuid primary key,
    run_id uuid not null,
    checked_at timestamptz not null default now(),
    reconciliation_name text not null,
    left_count bigint not null,
    right_count bigint not null,
    difference bigint not null,
    status text not null check (status in ('pass', 'fail')),
    threshold bigint not null default 0
);
