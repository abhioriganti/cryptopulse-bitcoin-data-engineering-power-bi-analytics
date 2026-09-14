
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select market_bar_key
from "cryptopulse"."analytics_analytics"."fact_market_bar"
where market_bar_key is null



  
  
      
    ) dbt_internal_test