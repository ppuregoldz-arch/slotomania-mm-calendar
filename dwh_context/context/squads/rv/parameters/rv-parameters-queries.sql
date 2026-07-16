/*
RV Parameters - SQL Query Repository
====================================
Contains all versions of RV parameter queries for version control and rollback capability.
Updated: 2026-05-26
*/

-- =============================================================================
-- 1. RV SEGMENT OPPORTUNISTIC
-- =============================================================================

/*
rv_segment_opportunistic - CURRENT VERSION (May 2026)
Purpose: User segmentation with expanded DPU buckets
Changes: Added DPU_30_60 and DPU_60_90 segments, renamed PUs_last_90D to PUs_last_30D
*/
select
    user_id,
    case
        when ltv = 0 and user_level >= 300 then 'NPU'
        when ltv > 0 and user_level > 100 and days_since_last_purchase <= 30 and coalesce(cz_price_cut_test, 0) <= 15
            then 'PUs_last_30D'
        when ltv > 0 and user_level > 100 and days_since_last_purchase >= 90 and coalesce(cz_price_cut_test, 0) <= 50
            then 'DPU_90+'
        when ltv > 0 and user_level > 100 and days_since_last_purchase >= 60 and coalesce(cz_price_cut_test, 0) <= 50
            then 'DPU_60_90'
        when ltv > 0 and user_level > 100 and days_since_last_purchase >= 30 and coalesce(cz_price_cut_test, 0) <= 50
            then 'DPU_30_60'
        else null end as rv_segment_opportunistic
from (select
          a.*,
          current_date - last_transaction_date as days_since_last_purchase,
          b.cz_price_cut_test
/*user profile - level, ltv*/
      from (select
                user_id,
                case when sum_net_amount < 0 then 0 else sum_net_amount end as ltv,
                user_level,
                last_transaction_ts::date                                   as last_transaction_date
            from dwh.sm_user_profile
            where 1 = 1) a
/*last cz value*/
               left join (select *
                          from stg.stg_smart_seg_sm_cz_price_cut_test) b
                         on a.user_id = b.user_id
      where 1 = 1) A;

/*
rv_segment_opportunistic - OLD VERSION (Pre-May 2026)
Purpose: Original 3-segment classification
Segments: NPU, PUs_last_90D, DPU_90+
*/
select
    user_id,
    case
        when ltv = 0 and user_level >= 300 then 'NPU'
        when ltv > 0 and user_level > 100 and days_since_last_purchase <= 90 and coalesce(cz_price_cut_test, 0) <= 15
            then 'PUs_last_90D'
        when ltv > 0 and user_level > 100 and days_since_last_purchase > 90 and coalesce(cz_price_cut_test, 0) <= 50
            then 'DPU_90+'
        else null end as rv_segment_opportunistic
from (select
          a.*,
          current_date - last_transaction_date as days_since_last_purchase,
          b.cz_price_cut_test
/*user profile - level, ltv*/
      from (select
                user_id,
                case when sum_net_amount < 0 then 0 else sum_net_amount end as ltv,
                user_level,
                last_transaction_ts::date                                   as last_transaction_date
            from dwh.sm_user_profile
            where 1 = 1) a
/*last cz value*/
               left join (select *
                          from stg.stg_smart_seg_sm_cz_price_cut_test) b
                         on a.user_id = b.user_id
      where 1 = 1) A;

-- =============================================================================
-- 2. RV OPPORTUNISTIC CONFIG BUCKETS  
-- =============================================================================

/*
rv_opportunistic_config_buckets - CURRENT VERSION (May 2026)
Purpose: Bucket assignment with Control group inclusion
Changes: Added 'Control' to test group conditions
*/
select
    last_value_user_id as user_id,
    coalesce( -- coalesce- for new users in the relevant segment
            (case
                 when coalesce(group_name, 'NA') not in ('Test_A', 'Test_B', 'Control')
                     then last_value_parameter_value -- gatekeeper- only test groups- reduce parameter value logic
                 when group_name in ('Test_A', 'Test_B', 'Control') and
                      coalesce(parameter_value, 0) != coalesce(last_value_parameter_value, 0)
                     then last_value_parameter_value -- changed segment/CZ from the last ads event
                 when group_name in ('Test_A', 'Test_B', 'Control') and
                      (previous_parameter_value is null OR coalesce(parameter_value, 0) !=
                                                           coalesce(previous_parameter_value, 0))
                     then last_value_parameter_value -- changed segment/CZ OR have only 1 ads day data
                 when group_name in ('Test_A', 'Test_B', 'Control') and
                      coalesce(is_above_min_threshold_last_2_days, 1) > 0
                     then last_value_parameter_value -- pass min threshold at least 1 time at the past 2 days
                 when group_name in ('Test_A', 'Test_B', 'Control') and previous_bucket_min_rev is null
                     then last_value_parameter_value --- at the lowest bucket / NPU
                 when group_name in ('Test_A', 'Test_B', 'Control') and
                      max_ad_revenue_per_day >= previous_bucket_min_rev
                     then parameter_value - 1 * segment_multiplier -- move to the previous bucket
                 when group_name in ('Test_A', 'Test_B', 'Control') and (parameter_value - 2 * segment_multiplier <= 0)
                     then parameter_value - 1 * segment_multiplier-- if they in the 2nd bucket (cant go down more than 1 bucket)
                 when group_name in ('Test_A', 'Test_B', 'Control') and (parameter_value - 2 * segment_multiplier > 0)
                     then parameter_value - 2 * segment_multiplier -- max reduce - 2 buckets
                 else last_value_parameter_value
                end), a.last_value_parameter_value
    )                  as rv_opportunistic_config_buckets
-- [Rest of query structure same as OLD version - full query available in context/squads/rv/queries.md]
;

/*
rv_opportunistic_config_buckets - OLD VERSION (Pre-May 2026)  
Purpose: Bucket assignment without Control group
Test Groups: Test_A, Test_B only
*/
select
    last_value_user_id as user_id,
    coalesce( -- coalesce- for new users in the relevant segment
            (case
                 when coalesce(group_name, 'NA') not in ('Test_A', 'Test_B')
                     then last_value_parameter_value -- other test groups- without reduce parameter value logic
                 when group_name in ('Test_A', 'Test_B') and
                      coalesce(parameter_value, 0) != coalesce(last_value_parameter_value, 0)
                     then last_value_parameter_value -- changed segment/CZ from the last ads event
                 when group_name in ('Test_A', 'Test_B') and (previous_parameter_value is null OR coalesce(parameter_value, 0) !=
                                                                                        coalesce(previous_parameter_value, 0))
                     then last_value_parameter_value -- changed segment/CZ OR have only 1 ads day data
                 when group_name in ('Test_A', 'Test_B') and coalesce(is_above_min_threshold_last_2_days, 1) > 0
                     then last_value_parameter_value -- pass min threshold at least 1 time at the past 2 days
                 when group_name in ('Test_A', 'Test_B') and previous_bucket_min_rev is null
                     then last_value_parameter_value --- at the lowest bucket / NPU
                 when group_name in ('Test_A', 'Test_B') and max_ad_revenue_per_day >= previous_bucket_min_rev
                     then parameter_value - 1 * segment_multiplier -- move to the previous bucket
                 when group_name in ('Test_A', 'Test_B') and (parameter_value - 2 * segment_multiplier <= 0)
                     then parameter_value - 1 * segment_multiplier-- if they in the 2nd bucket (cant go down more than 1 bucket)
                 when group_name in ('Test_A', 'Test_B') and (parameter_value - 2 * segment_multiplier > 0)
                     then parameter_value - 2 * segment_multiplier -- max reduce - 2 buckets
                 else last_value_parameter_value
                end), a.last_value_parameter_value
    )                  as rv_opportunistic_config_buckets
-- [Rest of query structure - full query available in outputs/rv_parameter_changes_2026-05-26/ for reference]
;

-- =============================================================================
-- 3. RV OPPORTUNISTIC DYNAMIC ECPM
-- =============================================================================

/*
RV_opportunistic_dynamic_ecpm - CURRENT VERSION (May 2026)
Purpose: Dynamic eCPM multiplier with Control group inclusion  
Changes: Added 'Control' to test group conditions
*/
select
    a_user_id      as user_id,
    case
        when coalesce(group_name, 'NA') not in ('Test_A', 'Test_B', 'Control') then 1
        when coalesce(last_value_rv_segment_opportunistic, 'NA') != 'NPU' then 1 -- Only for current NPU users
        when coalesce(last_value_rv_opportunistic_config_buckets, 0) != coalesce(parameter_value, 0)
            then 1 -- changed bucket (segment/country) from last ad event to today
        when coalesce(parameter_value, 0) != coalesce(lag_parameter_value, 0)
            then 1 -- changed bucket (segment/country) between 2 last ad events
        when coalesce(is_above_threshold_days, 1) >= 1
            then 1 -- pass min eCPM threshold at least 1 time / another check for users without RV events (above threshold=NULL)
        when ratio >= 1 then 1
--min reduce - by country (current reduce- 30% to all countries)
        when country_group_actual = 'US' and ratio >= 0.7 then ratio
        when country_group_actual = 'US' and ratio < 0.7 then 0.7
        when country_group_actual = 'Tier_1' and ratio >= 0.7 then ratio
        when country_group_actual = 'Tier_1' and ratio < 0.7 then 0.7
        when country_group_actual = 'Other' and ratio >= 0.7 then ratio
        when country_group_actual = 'Other' and ratio < 0.7 then 0.7
        else 1 end as RV_opportunistic_dynamic_ecpm
-- [Rest of query structure same as OLD version - full query provided by user]
;

/*
RV_opportunistic_dynamic_ecpm - OLD VERSION (Pre-May 2026)
Purpose: Dynamic eCPM multiplier without Control group
Test Groups: Test_A, Test_B only
*/
select
    a_user_id      as user_id,
    case
        when coalesce(group_name, 'NA') not in ('Test_A', 'Test_B') then 1
        when coalesce(last_value_rv_segment_opportunistic, 'NA') != 'NPU' then 1 -- Only for current NPU users
        when coalesce(last_value_rv_opportunistic_config_buckets, 0) != coalesce(parameter_value, 0)
            then 1 -- changed bucket (segment/country) from last ad event to today
        when coalesce(parameter_value, 0) != coalesce(lag_parameter_value, 0)
            then 1 -- changed bucket (segment/country) between 2 last ad events
        when coalesce(is_above_threshold_days, 1) >= 1
            then 1 -- pass min eCPM threshold at least 1 time / another check for users without RV events (above threshold=NULL)
        when ratio >= 1 then 1
--min reduce - by country (current reduce- 30% to all countries)
        when country_group_actual = 'US' and ratio >= 0.7 then ratio
        when country_group_actual = 'US' and ratio < 0.7 then 0.7
        when country_group_actual = 'Tier_1' and ratio >= 0.7 then ratio
        when country_group_actual = 'Tier_1' and ratio < 0.7 then 0.7
        when country_group_actual = 'Other' and ratio >= 0.7 then ratio
        when country_group_actual = 'Other' and ratio < 0.7 then 0.7
        else 1 end as RV_opportunistic_dynamic_ecpm
-- [Rest of query structure - full query provided by user]
;

-- =============================================================================
-- 4. VALIDATION QUERIES
-- =============================================================================

/*
Baseline Data Capture Query
Purpose: Capture current state before parameter changes
*/
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

/*
Segment Summary Query
Purpose: Quick segment overview and row counts
*/
select rv_segment, count(*) as row_count 
from sm_draft.RV_opportunistic_min_eCPM_per_segment 
group by rv_segment 
order by rv_segment;

/*
Configuration Validation Query
Purpose: Validate parameter value progression within segments
*/
select 
    rv_segment,
    config_cz_from,
    config_cz_to,
    parameter_value,
    min_ecpm,
    min_ad_rev,
    config_promo_date_from,
    config_promo_date_to
from sm_draft.RV_opportunistic_min_eCPM_per_segment
where rv_segment in ('DPU_30_60', 'DPU_60_90', 'PUs_last_30D')
order by rv_segment, config_cz_from;