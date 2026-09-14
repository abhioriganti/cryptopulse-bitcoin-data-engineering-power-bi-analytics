
  
    

  create  table "cryptopulse"."analytics_analytics"."dim_asset__dbt_tmp"
  
  
    as
  
  (
    select distinct
    md5(concat_ws('||', coalesce(cast(symbol as text), '_null_'), coalesce(cast(currency as text), '_null_'))) as asset_key,
    symbol,
    currency,
    split_part(symbol, '-', 1) as asset_code
from "cryptopulse"."analytics_staging"."stg_market_bars"
  );
  