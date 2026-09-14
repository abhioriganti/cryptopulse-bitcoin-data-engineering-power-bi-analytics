
  
    

  create  table "cryptopulse"."analytics_analytics"."fact_market_bar__dbt_tmp"
  
  
    as
  
  (
    select
    bars.market_bar_key,
    md5(concat_ws('||', coalesce(cast(bars.symbol as text), '_null_'), coalesce(cast(bars.currency as text), '_null_'))) as asset_key,
    md5(concat_ws('||', coalesce(cast(bars.provider as text), '_null_'))) as provider_key,
    bars.bar_start::date as date_key,
    bars.provider,
    bars.symbol,
    bars.currency,
    bars.interval,
    bars.bar_start,
    bars.bar_end,
    bars.open,
    bars.high,
    bars.low,
    bars.close,
    bars.volume,
    bars.trade_count,
    bars.vwap,
    bars.simple_return,
    bars.log_return,
    bars.loaded_at
from "cryptopulse"."analytics_intermediate"."int_market_returns" as bars
  );
  