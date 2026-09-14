select distinct
    {{ surrogate_key(['provider']) }} as provider_key,
    provider
from {{ ref('stg_market_bars') }}
