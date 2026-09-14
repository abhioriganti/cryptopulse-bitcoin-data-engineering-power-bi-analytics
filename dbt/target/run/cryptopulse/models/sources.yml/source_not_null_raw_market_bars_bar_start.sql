
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select bar_start
from "cryptopulse"."raw"."market_bars"
where bar_start is null



  
  
      
    ) dbt_internal_test