
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select provider_key
from "cryptopulse"."analytics_analytics"."dim_provider"
where provider_key is null



  
  
      
    ) dbt_internal_test