
  
    

  create  table "cryptopulse"."analytics_analytics"."dim_provider__dbt_tmp"
  
  
    as
  
  (
    select distinct
    md5(concat_ws('||', coalesce(cast(provider as text), '_null_'))) as provider_key,
    provider
from "cryptopulse"."analytics_staging"."stg_market_bars"
  );
  