
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select close
from "cryptopulse"."analytics_analytics"."fact_market_bar"
where close is null



  
  
      
    ) dbt_internal_test