/*
PURE CUPED Treatment Effect Analysis (FIXED V2)
==============================================
Test ID: ahhcuJnMV1
Purpose: Calculate treatment effects using PURE CUPED methodology
- Direct comparison of Y_CUPED values between groups
- NO reintroduction of pre-period metrics after CUPED adjustment
- Aligns with dashboard implementation and standard CUPED practice

CRITICAL METHODOLOGY CORRECTION:
- Previous: Y_CUPED - avg_rev_before (reintroduces pre-period bias)
- Corrected: Direct comparison of Y_CUPED values between Test vs Control

VALIDATION DOCUMENTATION
========================
Validation Performed: [To be completed after execution]
Validation Entities: [To be specified]
Validation Date Range: [To be specified]
Raw Data Source: CUPED-adjusted Y_CUPED values only
Expected Result: [To be calculated manually]
Actual Query Result: [To be verified]
Validation Status: [Pending - PURE CUPED methodology]
Notes: [To be added after validation]
*/

with base_data as (
    select 
        user_id,
        group_name,
        
        /*TRUE average daily revenue during pre-experiment period (14 days)*/
        coalesce(avg_rev_before, 0) as avg_rev_before,
        
        /*TRUE average daily revenue during experiment period (7 days)*/
        coalesce(avg_rev_during, 0) as avg_rev_during,
        
        /*overall average of avg_rev_before across all users*/
        avg(coalesce(avg_rev_before, 0)) over () as overall_avg_rev_before,
        
        /*overall average of avg_rev_during across all users*/
        avg(coalesce(avg_rev_during, 0)) over () as overall_avg_rev_during,
        
        /*deviation from overall average before period*/
        coalesce(avg_rev_before, 0) - avg(coalesce(avg_rev_before, 0)) over () as deviation_before,
        
        /*deviation from overall average during period*/
        coalesce(avg_rev_during, 0) - avg(coalesce(avg_rev_during, 0)) over () as deviation_during

    from (
        select 
            user_id,
            group_name,
            
            /*FIXED: calculate TRUE daily average revenue during pre-experiment period*/
            sum(case when promo_date between '2026-05-06' and '2026-05-19' 
                     then coalesce(gross_rev, 0) 
                     else 0 end) / 14 as avg_rev_before,
            
            /*FIXED: calculate TRUE daily average revenue during experiment period*/
            sum(case when promo_date between '2026-05-20' and '2026-05-26' 
                     then coalesce(gross_rev, 0) 
                     else 0 end) / 7 as avg_rev_during
            
        from (
            /*main data with test group assignments*/
            select 
                a.user_id,
                a.promo_date,
                a.gross_rev,
                coalesce(t.group_name, 'Not_In_Test') as group_name
                
            from agg.agg_sm_daily_promotion_stats a
            
            /*test group assignments*/
            left join (
                select 
                    a.user_id,
                    g.group_name
                from sm_ds.abtest_user_allocations a
                    left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
                    left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                where a.test_id = 'ahhcuJnMV1'
            ) t on a.user_id = t.user_id
            
            /*filter to users active during experiment period (during users)*/
            inner join (
                select distinct user_id
                from agg.agg_sm_daily_promotion_stats
                where promo_date between '2026-05-20' and '2026-05-26'
            ) during_users on a.user_id = during_users.user_id
            
            where 1 = 1
                /*include both pre-experiment and experiment periods*/
                and promo_date between '2026-05-06' and '2026-05-26'
                /*only include users assigned to the test*/
                and t.user_id is not null
                
        ) raw_data
        
        group by 1, 2
        
    ) user_averages
    
    /*FIXED: NO NULL FILTER - include all during users for proper CUPED methodology*/
),

theta_coefficient as (
    /*get the theta coefficient calculated from all users pooled using FIXED methodology*/
    select 
        (sum(deviation_before * deviation_during) / (count(*) - 1)) / 
        nullif(sum(deviation_before * deviation_before) / (count(*) - 1), 0) as theta
    from base_data
),

y_cuped_data as (
    select 
        b.user_id,
        b.group_name,
        
        /*original metrics (for reference only)*/
        b.avg_rev_before,
        b.avg_rev_during as original_avg_rev_during,
        b.deviation_before,
        b.deviation_during,
        
        /*theta coefficient applied to all users*/
        t.theta as theta_coefficient,
        
        /*Y-CUPED calculation: Y_CUPED = Y - θ × (X - X̄)*/
        /*This is the FINAL variance-reduced metric for analysis*/
        b.avg_rev_during - (t.theta * b.deviation_before) as Y_CUPED

    from base_data b
    cross join theta_coefficient t
)

/*
PURE CUPED ANALYSIS: Direct comparison of Y_CUPED values between groups
NO reintroduction of pre-period metrics after CUPED adjustment
*/
select 
    group_name,
    
    /*PURE CUPED group-level statistics*/
    count(*) as n_users,
    avg(Y_CUPED) as avg_Y_CUPED,
    variance(Y_CUPED) as var_Y_CUPED,
    sqrt(variance(Y_CUPED)) as sd_Y_CUPED,
    sqrt(variance(Y_CUPED) / count(*)) as se_Y_CUPED,
    
    /*original metrics (for comparison/reference only)*/
    avg(original_avg_rev_during) as avg_original_during,
    avg(avg_rev_before) as avg_before

from y_cuped_data
group by 1
order by group_name;