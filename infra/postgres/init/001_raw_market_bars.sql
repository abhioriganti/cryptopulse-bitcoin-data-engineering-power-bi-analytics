create schema if not exists raw;

create table if not exists raw.market_bars (
    provider text not null,
    symbol text not null,
    currency text not null,
    interval text not null,
    bar_start timestamptz not null,
    bar_end timestamptz not null,
    open double precision not null,
    high double precision not null,
    low double precision not null,
    close double precision not null,
    volume double precision not null,
    trade_count bigint not null,
    vwap double precision,
    loaded_at timestamptz not null default now(),
    primary key (provider, symbol, interval, bar_start)
);
