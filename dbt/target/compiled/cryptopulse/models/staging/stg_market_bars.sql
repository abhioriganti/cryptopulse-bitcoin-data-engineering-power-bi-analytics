with source as (
    select * from "cryptopulse"."raw"."market_bars"
)

select
    md5(concat_ws('||', coalesce(cast(provider as text), '_null_'), coalesce(cast(symbol as text), '_null_'), coalesce(cast(interval as text), '_null_'), coalesce(cast(bar_start as text), '_null_'))) as market_bar_key,
    provider,
    symbol,
    currency,
    interval,
    bar_start,
    bar_end,
    open::numeric(20, 8) as open,
    high::numeric(20, 8) as high,
    low::numeric(20, 8) as low,
    close::numeric(20, 8) as close,
    volume::numeric(28, 8) as volume,
    trade_count::bigint as trade_count,
    vwap::numeric(20, 8) as vwap,
    loaded_at
from source