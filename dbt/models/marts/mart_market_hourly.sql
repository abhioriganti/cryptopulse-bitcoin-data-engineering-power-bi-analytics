select
    provider,
    symbol,
    currency,
    date_trunc('hour', bar_start) as hour_start,
    (array_agg(open order by bar_start))[1] as open,
    max(high) as high,
    min(low) as low,
    (array_agg(close order by bar_start desc))[1] as close,
    sum(volume) as volume,
    sum(trade_count) as trade_count,
    sum(vwap * volume) / nullif(sum(volume), 0) as vwap
from {{ ref('fact_market_bar') }}
where interval = '1 minute'
group by provider, symbol, currency, date_trunc('hour', bar_start)
