
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    reconciliation_id as unique_field,
    count(*) as n_records

from "cryptopulse"."analytics_analytics"."mart_data_quality"
where reconciliation_id is not null
group by reconciliation_id
having count(*) > 1



  
  
      
    ) dbt_internal_test