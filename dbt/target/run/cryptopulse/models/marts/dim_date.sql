
  
    

  create  table "cryptopulse"."analytics_analytics"."dim_date__dbt_tmp"
  
  
    as
  
  (
    select distinct
    bar_start::date as date_key,
    extract(isodow from bar_start)::integer as iso_day_of_week,
    extract(month from bar_start)::integer as month_number,
    extract(year from bar_start)::integer as year_number
from "cryptopulse"."analytics_staging"."stg_market_bars"
  );
  