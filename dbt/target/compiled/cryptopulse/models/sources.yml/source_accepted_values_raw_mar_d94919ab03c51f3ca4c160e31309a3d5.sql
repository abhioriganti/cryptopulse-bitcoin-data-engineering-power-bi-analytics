
    
    

with all_values as (

    select
        interval as value_field,
        count(*) as n_records

    from "cryptopulse"."raw"."market_bars"
    group by interval

)

select *
from all_values
where value_field not in (
    '1 minute','5 minutes','15 minutes','1 hour'
)


