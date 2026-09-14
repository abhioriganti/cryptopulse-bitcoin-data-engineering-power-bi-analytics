
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select reconciliation_id
from "cryptopulse"."analytics_analytics"."mart_data_quality"
where reconciliation_id is null



  
  
      
    ) dbt_internal_test