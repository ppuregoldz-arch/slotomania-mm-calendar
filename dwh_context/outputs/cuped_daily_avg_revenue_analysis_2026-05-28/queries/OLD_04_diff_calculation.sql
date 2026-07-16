/*
Difference Calculation - CUPED vs Regular Treatment Effects
==========================================================
Test ID: ahhcuJnMV1
Purpose: Calculate treatment effects (differences) by test group comparing CUPED-adjusted vs regular metrics
Compares: avg_during - avg_before for both CUPED and original metrics

VALIDATION DOCUMENTATION
========================
Validation Performed: [To be completed after execution]
Validation Entities: [To be specified]
Validation Date Range: [To be specified]
Raw Data Source: Y_CUPED results from 03_Y_cuped.sql
Expected Result: [To be calculated manually]
Actual Query Result: [To be verified]
Validation Status: [Pending]
Notes: [To be added after validation]
*/

with y_cuped_data as (
    select 
        b.user_id,
        b.group_name,
        
        /*original metrics*/
        b.avg_rev_before,
        b.avg_rev_during as original_avg_rev_during,
        b.deviation_before,
        b.deviation_during,
        
        /*theta coefficient applied to all users*/
        t.theta as theta_coefficient,
        
        /*Y-CUPED calculation: Y_CUPED = Y - θ × (X - X̄)*/
        b.avg_rev_during - (t.theta * b.deviation_before) as Y_CUPED,
        
        /*variance reduction check - difference between original and adjusted*/
        b.deviation_during - (b.avg_rev_during - (t.theta * b.deviation_before) - b.overall_avg_rev_during) as variance_reduction_effect

    from (
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
                    
            ) raw_data
            
            group by 1, 2
            
        ) user_averages
        
        /*ensure we have both pre and during period data*/
        where avg_rev_before is not null 
            and avg_rev_during is not null
    ) b

    cross join (
        /*get the theta coefficient calculated from all users pooled*/
        select 
            (sum(deviation_before * deviation_during) / (count(*) - 1)) / 
            nullif(sum(deviation_before * deviation_before) / (count(*) - 1), 0) as theta
        from (
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
                        
                ) raw_data
                
                group by 1, 2
                
            ) user_averages
            
            /*ensure we have both pre and during period data*/
            where avg_rev_before is not null 
                and avg_rev_during is not null
        ) base_data
    ) t
)

select 
    group_name,
    
    /*CUPED-adjusted average revenue during experiment period*/
    avg(Y_CUPED) as avg_Y_cuped_during,
    
    /*original average revenue during experiment period*/
    avg(original_avg_rev_during) as original_avg_rev_during,
    
    /*average revenue during pre-experiment period (baseline)*/
    avg(avg_rev_before) as avg_rev_before,
    
    /*CUPED treatment effect: difference between CUPED-adjusted during and before periods*/
    avg(Y_CUPED) - avg(avg_rev_before) as diff_Y_cuped,
    
    /*regular treatment effect: difference between original during and before periods*/
    avg(original_avg_rev_during) - avg(avg_rev_before) as diff_regular,
    
    /*sample sizes per group*/
    count(*) as n_users,
    
    /*variance of user-level differences - needed for treatment effect standard errors*/
    var(Y_CUPED - avg_rev_before) as var_user_diff_cuped,
    var(original_avg_rev_during - avg_rev_before) as var_user_diff_regular,
    
    /*standard errors for group means*/
    sqrt(var(Y_CUPED - avg_rev_before) / count(*)) as se_cuped,
    sqrt(var(original_avg_rev_during - avg_rev_before) / count(*)) as se_regular,
    
    /*standard deviations for reference*/
    sqrt(var(Y_CUPED - avg_rev_before)) as sd_user_diff_cuped,
    sqrt(var(original_avg_rev_during - avg_rev_before)) as sd_user_diff_regular

from y_cuped_data
group by 1
order by 1;