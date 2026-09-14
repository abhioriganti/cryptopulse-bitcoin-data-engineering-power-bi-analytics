
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    market_bar_key as unique_field,
    count(*) as n_records

from "cryptopulse"."analytics_analytics"."fact_market_bar"
where market_bar_key is not null
group by market_bar_key
having count(*) > 1



  
  
      
    ) dbt_internal_test