
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select provider
from "cryptopulse"."raw"."market_bars"
where provider is null



  
  
      
    ) dbt_internal_test