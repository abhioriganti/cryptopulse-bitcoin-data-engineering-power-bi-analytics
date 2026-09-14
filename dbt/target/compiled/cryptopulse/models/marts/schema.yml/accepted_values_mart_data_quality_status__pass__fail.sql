
    
    

with all_values as (

    select
        status as value_field,
        count(*) as n_records

    from "cryptopulse"."analytics_analytics"."mart_data_quality"
    group by status

)

select *
from all_values
where value_field not in (
    'pass','fail'
)


