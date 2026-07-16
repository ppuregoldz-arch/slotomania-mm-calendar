/*
RV DPU Performance Analysis - CORRECTED Data Extraction
======================================================

VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Entities: Test_A vs Test_C cohorts (CORRECTED - Test_C is true control, no RV treatment)
Validation Date Range: 2026-02-16 to 2026-06-07
Raw Data Source: dwh.sm_fact_rv_client_events, dwh.sm_fact_payments, agg.agg_sm_daily_users_stats
Expected Result: Daily metrics for DPU_90+ users split by tenure comparing Test_A (RV treatment) vs Test_C (no RV)
Actual Query Result: [To be validated after execution]
Validation Status: Pending
Notes: CORRECTED to compare Test_A vs Test_C (true control with no RV treatment)

CRITICAL CORRECTION: 
- Test_A: Gets RV treatment
- Control group: Also gets RV treatment (added lately) 
- Test_C: TRUE control with NO RV treatment
- Previous analysis was WRONG - compared two RV treatment groups

Purpose: Extract RV performance data for DPU segments with Test_A vs Test_C comparison
Business Question: How does Test_A (RV treatment) perform vs Test_C (no RV treatment) in DPU segments?
Date Range: 2026-02-16 onwards (test activation date)
Key Insight: Uses fixed DPU_90+ cohort from 2026-02-16 with custom tenure splits
*/

select 
    promo_date,
    test_group,
    dpu_tenure_segment,
    
    -- DAU Metrics
    count(distinct user_id) as dau,
    count(distinct case when daily_net_revenue > 0 then user_id end) as paying_users,
    
    -- Revenue Metrics  
    sum(daily_net_revenue) as total_revenue,
    sum(daily_net_revenue) / count(distinct user_id) as arpu,
    sum(daily_net_revenue) / count(distinct case when daily_net_revenue > 0 then user_id end) as arppu,
    count(distinct case when daily_net_revenue > 0 then user_id end) / count(distinct user_id) as conversion_rate,
    
    -- Engagement Metrics
    sum(spins) as total_spins,
    sum(daily_sessions_amount) as total_sessions,
    sum(spins) / count(distinct user_id) as spins_per_user,
    sum(daily_sessions_amount) / count(distinct user_id) as sessions_per_user,
    
    -- RV Metrics (should be ZERO for Test_C since they don't get RV)
    sum(rv_revenue) as rv_revenue,
    sum(rv_events) as rv_events,
    count(distinct case when rv_events > 0 then user_id end) as rv_users,
    sum(rv_revenue) / nullif(count(distinct case when rv_events > 0 then user_id end), 0) as rv_revenue_per_user,
    count(distinct case when rv_events > 0 then user_id end) / count(distinct user_id) as rv_conversion_rate

/*core DPU performance data with tenure splits - CORRECTED*/
from (
    select 
        stats.user_id,
        stats.calc_date,
        date(stats.calc_date::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
        
        -- Test group assignment - CORRECTED TO USE Test_C as control
        coalesce(ab.group_name, 'Not_Allocated') as test_group,
        
        -- Custom DPU tenure segmentation within fixed 2026-02-16 cohort
        case 
            when profile.rv_segment_opportunistic = 'DPU_90+' 
                and ('2026-02-16'::date - main_profile.last_transaction_ts::date) between 90 and 180 
                then 'DPU_90-180'
            when profile.rv_segment_opportunistic = 'DPU_90+' 
                and ('2026-02-16'::date - main_profile.last_transaction_ts::date) > 180 
                then 'DPU_180+'
            else null
        end as dpu_tenure_segment,
        
        -- Core metrics from daily stats
        stats.daily_net_revenue,
        stats.spins,
        stats.daily_sessions_amount,
        
        -- RV metrics from RV events
        coalesce(rv.rv_revenue, 0) as rv_revenue,
        coalesce(rv.rv_events, 0) as rv_events
        
    /*daily user stats - base metrics*/
    from agg.agg_sm_daily_users_stats stats
    
    /*fixed DPU cohort from 2026-02-16*/
    inner join (
        select user_id, rv_segment_opportunistic
        from dwh.sm_user_profile_datamining_snapshot
        where event_date_datamining = '2026-02-16'
          and rv_segment_opportunistic = 'DPU_90+'
          and user_id > 0
          and user_id not in (select distinct user_id from dwh.playtika_users)
          and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
    ) profile on stats.user_id = profile.user_id
    
    /*tenure calculation from main profile*/
    inner join dwh.sm_user_profile main_profile 
        on stats.user_id = main_profile.user_id
        and main_profile.last_transaction_ts is not null
        and main_profile.last_transaction_ts::date <= '2026-02-16'
        and ('2026-02-16'::date - main_profile.last_transaction_ts::date) >= 90
    
    /*A/B test allocation - CORRECTED: Test_A vs Test_C*/  
    left join (
        select distinct
            a.user_id,
            g.group_name
        from sm_ds.abtest_user_allocations a
        left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
        left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
        where a.test_id = 'xmXDU4lG4J'
          and g.group_name in ('Test_A', 'Test_C')  -- CORRECTED: Test_C is true control
    ) ab on stats.user_id = ab.user_id
    
    /*RV performance aggregation by user/day*/
    left join (
        select 
            user_id,
            event_date,
            sum(case when event_type = 'AD_REWARDED' and transaction_id is not null then revenue else 0 end) as rv_revenue,
            count(case when event_type = 'AD_REWARDED' and transaction_id is not null then 1 end) as rv_events
        from dwh.sm_fact_rv_client_events
        where event_date >= '2026-02-16' 
          and event_date < current_date
          and user_id > 0
          and user_id not in (select distinct user_id from dwh.playtika_users)
          and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
        group by 1, 2
    ) rv on stats.user_id = rv.user_id and stats.calc_date = rv.event_date
    
    where stats.calc_date >= '2026-02-16'
      and stats.calc_date < current_date
      and stats.user_id > 0
      and stats.user_id not in (select distinct user_id from dwh.playtika_users)
      and stats.user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
) dpu_performance

/*final filtering and grouping - CORRECTED*/
where dpu_tenure_segment is not null
  and test_group in ('Test_A', 'Test_C')  -- CORRECTED: Test_C is true control
  and promo_date >= '2026-02-16'
  and promo_date < current_date

group by 1, 2, 3
order by 1, 2, 3;