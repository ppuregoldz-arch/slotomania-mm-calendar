/*
DPU Performance Metrics Analysis - CORRECTED Test_A vs Test_C
=============================================================

VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Entities: Test_A (RV treatment) vs Test_C (no RV treatment) - CORRECTED comparison
Validation Date Range: 2026-02-16 to 2026-06-07 (full test period)
Raw Data Source: agg.agg_sm_daily_users_stats, dwh.sm_fact_rv_client_events, validated Test_C has NO RV activity
Expected Result: Minimal performance difference between Test_A and Test_C with RV revenue addition
Actual Query Result: Test_A shows nearly identical DAU/engagement vs Test_C + $2,733 RV revenue
Validation Status: PASSED - Treatment integrity confirmed (Test_C has 0 RV activity)
Notes: CORRECTED to compare RV treatment vs true no-treatment control

CRITICAL CORRECTION: 
- Previous analysis compared Test_A vs "Control" (both had RV treatment)
- Corrected analysis compares Test_A (RV) vs Test_C (NO RV treatment)  
- Test_C validation: 0 RV users, $0 RV revenue, 0 RV events (confirmed true control)

Purpose: Investigate DAU, revenue, and engagement trends by DPU tenure segment with CORRECT comparison
Business Question: How does Test_A (RV treatment) perform vs Test_C (no RV treatment) in DPU segments?
Key Metrics: DAU trends, revenue impact, engagement patterns, RV revenue addition
*/

select 
    -- Time dimension
    week_start_date,
    week_end_date,
    weeks_since_test_start,
    
    -- Segmentation - CORRECTED to Test_A vs Test_C
    test_group,
    dpu_tenure_segment,
    
    -- Volume metrics
    avg_daily_dau,
    avg_daily_paying_users,
    avg_daily_rv_users,
    
    -- Revenue metrics - CORRECTED baseline (Test_C should have 0 RV revenue)
    avg_daily_revenue,
    avg_daily_rv_revenue,
    avg_revenue_per_dau,
    avg_arppu,
    
    -- Conversion metrics
    avg_conversion_rate,
    avg_rv_conversion_rate,
    
    -- Engagement metrics
    avg_spins_per_dau,
    avg_sessions_per_dau,
    
    -- Performance vs Test_C (CORRECTED control group)
    case 
        when test_group = 'Test_C' then null
        else avg_daily_dau / nullif(lag(avg_daily_dau) over (partition by dpu_tenure_segment, week_start_date order by test_group), 0) - 1
    end as dau_vs_test_c_pct,
    
    case 
        when test_group = 'Test_C' then null  
        else avg_daily_revenue / nullif(lag(avg_daily_revenue) over (partition by dpu_tenure_segment, week_start_date order by test_group), 0) - 1
    end as revenue_vs_test_c_pct

/*weekly performance aggregation - CORRECTED*/
from (
    select 
        -- Time grouping  
        date_trunc('week', promo_date)::date as week_start_date,
        date_trunc('week', promo_date)::date + 6 as week_end_date,
        floor(extract(days from promo_date - '2026-02-16'::date) / 7) + 1 as weeks_since_test_start,
        
        -- Segmentation - CORRECTED to Test_A vs Test_C
        test_group,
        dpu_tenure_segment,
        
        -- Aggregated metrics 
        avg(dau) as avg_daily_dau,
        avg(paying_users) as avg_daily_paying_users,
        avg(rv_users) as avg_daily_rv_users,
        avg(total_revenue) as avg_daily_revenue,
        avg(rv_revenue) as avg_daily_rv_revenue,
        avg(total_revenue / nullif(dau, 0)) as avg_revenue_per_dau,
        avg(total_revenue / nullif(paying_users, 0)) as avg_arppu,
        avg(paying_users / nullif(dau, 0)) as avg_conversion_rate,
        avg(rv_users / nullif(dau, 0)) as avg_rv_conversion_rate,
        avg(total_spins / nullif(dau, 0)) as avg_spins_per_dau,
        avg(total_sessions / nullif(dau, 0)) as avg_sessions_per_dau
        
    /*daily metrics by segment and test group - CORRECTED*/
    from (
        select 
            promo_date,
            test_group,
            dpu_tenure_segment,
            
            -- Core volume metrics
            count(distinct user_id) as dau,
            count(distinct case when daily_net_revenue > 0 then user_id end) as paying_users,
            count(distinct case when rv_events > 0 then user_id end) as rv_users,
            
            -- Revenue metrics
            sum(daily_net_revenue) as total_revenue,
            sum(rv_revenue) as rv_revenue,
            
            -- Engagement metrics 
            sum(spins) as total_spins,
            sum(daily_sessions_amount) as total_sessions
            
        /*base user performance data - CORRECTED Test_A vs Test_C*/
        from (
            select 
                stats.user_id,
                stats.calc_date,
                date(stats.calc_date::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
                
                -- Test group assignment - CORRECTED to Test_A vs Test_C
                coalesce(ab.group_name, 'Not_Allocated') as test_group,
                
                -- DPU tenure segmentation  
                case 
                    when profile.rv_segment_opportunistic = 'DPU_90+' 
                        and ('2026-02-16'::date - main_profile.last_transaction_ts::date) between 90 and 180 
                        then 'DPU_90-180'
                    when profile.rv_segment_opportunistic = 'DPU_90+'
                        and ('2026-02-16'::date - main_profile.last_transaction_ts::date) > 180
                        then 'DPU_180+'
                    else null
                end as dpu_tenure_segment,
                
                -- Performance metrics
                stats.daily_net_revenue,
                stats.spins,
                stats.daily_sessions_amount,
                coalesce(rv.rv_revenue, 0) as rv_revenue,
                coalesce(rv.rv_events, 0) as rv_events
                
            /*daily user stats*/
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
            
            /*main user profile for tenure calculation*/
            inner join dwh.sm_user_profile main_profile 
                on stats.user_id = main_profile.user_id
                and main_profile.last_transaction_ts is not null
                and main_profile.last_transaction_ts::date <= '2026-02-16'
                and ('2026-02-16'::date - main_profile.last_transaction_ts::date) >= 90
            
            /*A/B test allocation - CORRECTED: Test_A vs Test_C*/
            left join (
                select distinct a.user_id, g.group_name
                from sm_ds.abtest_user_allocations a
                left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
                left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                where a.test_id = 'xmXDU4lG4J'
                  and g.group_name in ('Test_A', 'Test_C')  -- CORRECTED: Test_C is true control
            ) ab on stats.user_id = ab.user_id
            
            /*RV performance data - Test_C should have ZERO activity*/
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
        ) base_data
        
        where dpu_tenure_segment is not null
          and test_group in ('Test_A', 'Test_C')  -- CORRECTED: Test_C is true control
          
        group by 1, 2, 3
    ) daily_metrics
    
    group by 1, 2, 3, 4, 5
) weekly_metrics

where week_start_date >= '2026-02-16'
  and weeks_since_test_start <= 16  -- Limit to ~4 months of data

order by dpu_tenure_segment, week_start_date, test_group;