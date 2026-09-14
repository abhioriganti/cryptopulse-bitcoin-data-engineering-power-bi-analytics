
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select interval
from "cryptopulse"."raw"."market_bars"
where interval is null



  
  
      
    ) dbt_internal_test