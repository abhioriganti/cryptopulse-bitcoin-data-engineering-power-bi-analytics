
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select reconciliation_id
from "cryptopulse"."raw"."reconciliation_results"
where reconciliation_id is null



  
  
      
    ) dbt_internal_test