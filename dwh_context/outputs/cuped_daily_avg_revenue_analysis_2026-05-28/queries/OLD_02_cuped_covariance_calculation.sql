/*
CUPED Covariance Calculation
============================
Test ID: ahhcuJnMV1
Purpose: Calculate covariance between pre-experiment and experiment deviations for CUPED analysis
Formula: COV(deviation_before, deviation_during) = Σ[(Xi - X̄)(Yi - Ȳ)] / (n-1)

This query calculates:
1. Sample covariance between before/during deviations
2. Variance of before period (needed for theta calculation)
3. CUPED theta coefficient = COV(Y,X) / VAR(X)

VALIDATION DOCUMENTATION
========================
Validation Performed: [To be completed after execution]
Validation Entities: [To be specified]
Validation Date Range: [To be specified]
Raw Data Source: Base data from 01_cuped_daily_avg_revenue_base_data.sql
Expected Result: [To be calculated manually]
Actual Query Result: [To be verified]
Validation Status: [Pending]
Notes: [To be added after validation]
*/

with base_data as (
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
)

select 
    count(*) as n_users,
    
    /*sample covariance calculation: COV(X,Y) = Σ[(Xi - X̄)(Yi - Ȳ)] / (n-1)*/
    /*calculated using ALL users pooled together for stable CUPED theta*/
    sum(deviation_before * deviation_during) / (count(*) - 1) as covariance_before_during,
    
    /*variance of before period: VAR(X) = Σ[(Xi - X̄)²] / (n-1)*/
    sum(deviation_before * deviation_before) / (count(*) - 1) as variance_before,
    
    /*variance of during period: VAR(Y) = Σ[(Yi - Ȳ)²] / (n-1)*/
    sum(deviation_during * deviation_during) / (count(*) - 1) as variance_during,
    
    /*CUPED theta coefficient: θ = COV(Y,X) / VAR(X)*/
    /*this single theta will be applied to all test groups*/
    (sum(deviation_before * deviation_during) / (count(*) - 1)) / 
    nullif(sum(deviation_before * deviation_before) / (count(*) - 1), 0) as theta_coefficient,
    
    /*Pearson correlation coefficient: r = COV(X,Y) / (SD(X) * SD(Y))*/
    (sum(deviation_before * deviation_during) / (count(*) - 1)) / 
    nullif(
        sqrt(sum(deviation_before * deviation_before) / (count(*) - 1)) * 
        sqrt(sum(deviation_during * deviation_during) / (count(*) - 1)), 
        0
    ) as Pearson_Correlation_Coefficient

from base_data;