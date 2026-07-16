/*
DPU 60-90 Gatekeeping Query 2: Min eCPM Threshold Validation
===========================================================
Purpose: Validate DPU_60_90 users meet minimum eCPM thresholds
Expected Thresholds: $0.04-$0.40 (based on CZ buckets 1000-6000)

EXECUTION: Run ON LAUNCH DAY (2026-05-27) when DPU_60_90 users have AD_DISPLAYED events
Expected: All revenue >= min_ad_rev thresholds (100% compliance)
Based on: Dynamic eCPM Threshold Validation pattern
*/

select
    a.user_id,
    a.event_date,
    a.event_ts,
    a.placement,
    a.placement_trigger,
    a.revenue,
    b.rv_segment_opportunistic,
    b.rv_opportunistic_config_buckets,
    b.RV_opportunistic_dynamic_ecpm,
    c.cz_price_cut_test,
    g.rv_segment as config_segment,
    g.parameter_value as config_parameter_value,
    g.min_ecpm,
    g.min_ad_rev,
    g.segment_multiplier,
    t.group_name as test_group,
    up.country_name,
    
    -- eCPM validation calculations
    g.min_ad_rev * coalesce(b.RV_opportunistic_dynamic_ecpm, 1) as min_ad_rev_with_param,
    
    case
        when a.revenue >= g.min_ad_rev * coalesce(b.RV_opportunistic_dynamic_ecpm, 1) then 'ok'
        else 'wrong'
    end as min_eCPM_validation,
    
    a.revenue / (g.min_ad_rev * coalesce(b.RV_opportunistic_dynamic_ecpm, 1)) as revenue_ratio,
    
    case 
        when g.min_ad_rev is null then 'wrong'
        when b.rv_segment_opportunistic != 'DPU_60_90' then 'wrong'
        when t.group_name not in ('Test_A', 'Test_B', 'Control') then 'wrong'
        when g.parameter_value not between 1000 and 6000 then 'wrong'
        else 'ok'
    end as config_validation

from (
    select
        user_id,
        event_date,
        event_ts,
        placement,
        placement_trigger,
        revenue,
        date(event_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '13 hours') as promo_date
    from dwh.sm_fact_rv_client_events
    where 1 = 1
      and user_id not in (select distinct user_id from dwh.playtika_users)
      and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
      and event_type = 'AD_DISPLAYED'
      and event_date = current_date  -- Today only (run tomorrow when DPU_60_90 should have events)
      and revenue > 0
) a

-- User segmentation and parameters
left join (
    select
        user_id,
        rv_segment_opportunistic,
        coalesce(cz_price_cut_test, 0) as cz_price_cut_test,
        rv_opportunistic_config_buckets,
        RV_opportunistic_dynamic_ecpm
    from dwh.sm_user_profile_datamining_snapshot
    where event_date_datamining = current_date
      and rv_segment_opportunistic = 'DPU_60_90'  -- Focus on DPU_60_90 only
) b on a.user_id = b.user_id

-- CZ data from datamining table
left join (
    select user_id, cz_price_cut_test
    from dwh.sm_user_profile_datamining_snapshot
    where event_date_datamining = current_date
) c on a.user_id = c.user_id

-- Configuration thresholds using promo_date
left join (
    select *
    from sm_draft.RV_opportunistic_min_eCPM_per_segment
    where rv_segment = 'DPU_60_90'
) g on b.rv_opportunistic_config_buckets = g.parameter_value
    and c.cz_price_cut_test between g.config_cz_from and g.config_cz_to
    and a.promo_date >= g.config_promo_date_from
    and a.promo_date < g.config_promo_date_to

-- Test group allocation
left join (
    select distinct
        a.user_id as t_user_id,
        group_name
    from sm_ds.abtest_user_allocations a
    left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
    left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
    where test_id = 'xmXDU4lG4J'
) t on a.user_id = t.t_user_id

-- User profile for country
left join (
    select user_id as up_user_id, country_name 
    from dwh.sm_user_profile
) up on a.user_id = up.up_user_id

where b.user_id is not null  -- Ensure we have DPU_60_90 users only

order by a.event_ts desc;
