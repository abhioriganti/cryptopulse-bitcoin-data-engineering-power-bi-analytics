
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select symbol
from "cryptopulse"."analytics_analytics"."dim_asset"
where symbol is null



  
  
      
    ) dbt_internal_test