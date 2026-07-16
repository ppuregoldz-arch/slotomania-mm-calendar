/*
CUPED Daily Average Revenue Analysis - Base Data Query
=====================================================
Test ID: ahhcuJnMV1
Pre-experiment Period: 2024-05-06 to 2024-05-19 (14 days)
Experiment Period: 2024-05-20 to 2024-05-26 (7 days)
Population: "During" users only (active during experiment period)

Purpose: Calculate average daily revenue per user for both pre-experiment and experiment periods,
along with overall averages needed for CUPED variance reduction calculations.

VALIDATION DOCUMENTATION
========================
Validation Performed: [To be completed after execution]
Validation Entities: [To be specified]
Validation Date Range: [To be specified]
Raw Data Source: agg.agg_sm_daily_promotion_stats - gross_rev field
Expected Result: [To be calculated manually]
Actual Query Result: [To be verified]
Validation Status: [Pending]
Notes: [To be added after validation]
*/

select 
    user_id,
    group_name,
    
    /*average revenue during pre-experiment period (14 days)*/
    coalesce(avg_rev_before, 0) as avg_rev_before,
    
    /*average revenue during experiment period (7 days)*/
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
        
        /*calculate average daily revenue during pre-experiment period*/
        avg(case when promo_date between '2024-05-06' and '2024-05-19' 
                 then coalesce(gross_rev, 0) 
                 else null end) as avg_rev_before,
        
        /*calculate average daily revenue during experiment period*/
        avg(case when promo_date between '2024-05-20' and '2024-05-26' 
                 then coalesce(gross_rev, 0) 
                 else null end) as avg_rev_during
        
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
            where promo_date between '2024-05-20' and '2024-05-26'
        ) during_users on a.user_id = during_users.user_id
        
        where 1 = 1
            /*include both pre-experiment and experiment periods*/
            and promo_date between '2024-05-06' and '2024-05-26'
            /*only include users assigned to the test*/
            and t.user_id is not null
            
    ) base_data
    
    group by 1, 2
    
) user_averages

/*ensure we have both pre and during period data*/
where avg_rev_before is not null 
    and avg_rev_during is not null

order by user_id;