select
    reconciliation_id,
    run_id,
    checked_at,
    reconciliation_name,
    left_count,
    right_count,
    difference,
    threshold,
    status,
    case when status = 'pass' then 1 else 0 end as passed_flag
from {{ source('raw', 'reconciliation_results') }}
