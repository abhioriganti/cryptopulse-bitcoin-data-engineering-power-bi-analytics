select distinct
    {{ surrogate_key(['symbol', 'currency']) }} as asset_key,
    symbol,
    currency,
    split_part(symbol, '-', 1) as asset_code
from {{ ref('stg_market_bars') }}
