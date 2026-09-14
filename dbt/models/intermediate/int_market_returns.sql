with bars as (
    select * from {{ ref('stg_market_bars') }}
), enriched as (
    select
        *,
        lag(close) over (
            partition by provider, symbol, interval
            order by bar_start
        ) as prior_close
    from bars
)

select
    *,
    case when prior_close > 0 then (close / prior_close) - 1 end as simple_return,
    case when prior_close > 0 then ln(close / prior_close) end as log_return
from enriched
