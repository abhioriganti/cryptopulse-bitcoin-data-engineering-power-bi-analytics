
    
    

with child as (
    select asset_key as from_field
    from "cryptopulse"."analytics_analytics"."fact_market_bar"
    where asset_key is not null
),

parent as (
    select asset_key as to_field
    from "cryptopulse"."analytics_analytics"."dim_asset"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


