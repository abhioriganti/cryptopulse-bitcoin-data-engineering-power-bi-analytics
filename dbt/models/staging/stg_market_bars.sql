with source as (
    select * from {{ source('raw', 'market_bars') }}
)

select
    {{ surrogate_key(['provider', 'symbol', 'interval', 'bar_start']) }} as market_bar_key,
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
