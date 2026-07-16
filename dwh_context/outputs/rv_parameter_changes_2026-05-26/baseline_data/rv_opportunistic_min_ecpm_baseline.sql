/*
BASELINE QUERY - RV_opportunistic_min_eCPM_per_segment table
Run Date: 2026-05-26
Purpose: Capture current state before parameter changes
*/

-- Full baseline query
select 
    rv_segment, 
    country, 
    config_cz_from, 
    config_cz_to, 
    config_promo_date_from, 
    config_promo_date_to, 
    min_ecpm, 
    min_ad_rev, 
    segment_multiplier, 
    parameter_value 
from sm_draft.RV_opportunistic_min_eCPM_per_segment 
order by rv_segment, country, config_cz_from, config_promo_date_from;

-- Summary by segment
select rv_segment, count(*) as row_count 
from sm_draft.RV_opportunistic_min_eCPM_per_segment 
group by rv_segment 
order by rv_segment;