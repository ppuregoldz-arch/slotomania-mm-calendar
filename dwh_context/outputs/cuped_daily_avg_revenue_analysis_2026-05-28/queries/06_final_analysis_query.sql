/*
FINAL ANALYSIS QUERY - Complete CUPED vs Regular Comparison
==========================================================
Test ID: ahhcuJnMV1
Purpose: Single comprehensive query that produces complete analysis results
- Pure CUPED methodology (direct Y_CUPED comparison)
- Regular methodology (direct Y_during comparison) 
- Treatment effects and confidence intervals for both methods
- Percentage-based CIs using control group means as baselines

CRITICAL METHODOLOGY:
1. TRUE daily average calculation (SUM/days not AVG of active days)
2. Include full experimental population (no NULL filters)
3. Users without pre-period activity = 0 baseline (proper CUPED)
4. Pure CUPED: Direct comparison of Y_CUPED values between groups
5. Percentage CIs: ((CI_bounds) / Control_Mean) * 100 (Dashboard Method)

Output Format:
- method: 'Pure CUPED' or 'Regular'
- test_group_mean: Average value for test group
- control_group_mean: Average value for control group  
- treatment_effect: Test - Control (absolute)
- treatment_effect_pct: (Test - Control) / Control * 100
- ci_lower_pct: Lower bound of 95% CI in percentage
- ci_upper_pct: Upper bound of 95% CI in percentage
- statistical_significance: 'Significant' or 'Not Significant'
- n_test: Sample size test group
- n_control: Sample size control group
*/

WITH 

/* ══════════════════════════════════════════════════════════════════════════
   1. BASE DATA - User-level metrics for both periods
   ══════════════════════════════════════════════════════════════════════════ */
base_data AS (
    SELECT 
        user_id,
        group_name,
        
        /*TRUE average daily revenue during pre-experiment period (14 days)*/
        COALESCE(avg_rev_before, 0) AS avg_rev_before,
        
        /*TRUE average daily revenue during experiment period (7 days)*/
        COALESCE(avg_rev_during, 0) AS avg_rev_during,
        
        /*overall averages across all users*/
        AVG(COALESCE(avg_rev_before, 0)) OVER () AS overall_avg_rev_before,
        AVG(COALESCE(avg_rev_during, 0)) OVER () AS overall_avg_rev_during,
        
        /*deviations from overall averages*/
        COALESCE(avg_rev_before, 0) - AVG(COALESCE(avg_rev_before, 0)) OVER () AS deviation_before,
        COALESCE(avg_rev_during, 0) - AVG(COALESCE(avg_rev_during, 0)) OVER () AS deviation_during

    FROM (
        SELECT 
            user_id,
            group_name,
            
            /*FIXED: calculate TRUE daily average revenue during pre-experiment period*/
            SUM(CASE WHEN promo_date BETWEEN '2026-05-06' AND '2026-05-19' 
                     THEN COALESCE(gross_rev, 0) 
                     ELSE 0 END) / 14 AS avg_rev_before,
            
            /*FIXED: calculate TRUE daily average revenue during experiment period*/
            SUM(CASE WHEN promo_date BETWEEN '2026-05-20' AND '2026-05-26' 
                     THEN COALESCE(gross_rev, 0) 
                     ELSE 0 END) / 7 AS avg_rev_during
            
        FROM (
            /*main data with test group assignments*/
            SELECT 
                a.user_id,
                a.promo_date,
                a.gross_rev,
                COALESCE(t.group_name, 'Not_In_Test') AS group_name
                
            FROM agg.agg_sm_daily_promotion_stats a
            
            /*test group assignments*/
            LEFT JOIN (
                SELECT 
                    a.user_id,
                    g.group_name
                FROM sm_ds.abtest_user_allocations a
                    LEFT JOIN sm_ds.abtest_dim_test t ON a.test_id = t.ab_test_id
                    LEFT JOIN sm_ds.abtest_dim_group g ON a.group_test_id = g.test_group_id
                WHERE a.test_id = 'ahhcuJnMV1'
            ) t ON a.user_id = t.user_id
            
            /*filter to users active during experiment period (during users)*/
            INNER JOIN (
                SELECT DISTINCT user_id
                FROM agg.agg_sm_daily_promotion_stats
                WHERE promo_date BETWEEN '2026-05-20' AND '2026-05-26'
            ) during_users ON a.user_id = during_users.user_id
            
            WHERE 1 = 1
                /*include both pre-experiment and experiment periods*/
                AND promo_date BETWEEN '2026-05-06' AND '2026-05-26'
                /*only include users assigned to the test*/
                AND t.user_id IS NOT NULL
                
        ) raw_data
        
        GROUP BY 1, 2
        
    ) user_averages
    
    /*FIXED: NO NULL FILTER - include all during users for proper CUPED methodology*/
),

/* ══════════════════════════════════════════════════════════════════════════
   2. CUPED THETA COEFFICIENT - Single pooled theta for all users
   ══════════════════════════════════════════════════════════════════════════ */
theta_coefficient AS (
    SELECT 
        (SUM(deviation_before * deviation_during) / (COUNT(*) - 1)) / 
        NULLIF(SUM(deviation_before * deviation_before) / (COUNT(*) - 1), 0) AS theta
    FROM base_data
),

/* ══════════════════════════════════════════════════════════════════════════
   3. Y_CUPED CALCULATION - Apply theta adjustment to each user
   ══════════════════════════════════════════════════════════════════════════ */
cuped_data AS (
    SELECT 
        b.user_id,
        b.group_name,
        b.avg_rev_before,
        b.avg_rev_during,
        
        /*Y-CUPED calculation: Y_CUPED = Y - θ × (X - X̄)*/
        b.avg_rev_during - (t.theta * b.deviation_before) AS Y_CUPED
        
    FROM base_data b
    CROSS JOIN theta_coefficient t
),

/* ══════════════════════════════════════════════════════════════════════════
   4. GROUP STATISTICS - Calculate stats for both Regular and CUPED methods
   ══════════════════════════════════════════════════════════════════════════ */
group_stats AS (
    SELECT 
        group_name,
        COUNT(*) AS n_users,
        
        /*Regular Method Statistics (Y_during)*/
        AVG(avg_rev_during) AS avg_regular,
        VARIANCE(avg_rev_during) AS var_regular,
        SQRT(VARIANCE(avg_rev_during) / COUNT(*)) AS se_regular,
        
        /*CUPED Method Statistics (Y_CUPED)*/
        AVG(Y_CUPED) AS avg_cuped,
        VARIANCE(Y_CUPED) AS var_cuped,
        SQRT(VARIANCE(Y_CUPED) / COUNT(*)) AS se_cuped
        
    FROM cuped_data
    GROUP BY group_name
),

/* ══════════════════════════════════════════════════════════════════════════
   5. TREATMENT EFFECTS - Calculate effects and CIs for both methods
   ══════════════════════════════════════════════════════════════════════════ */
treatment_effects AS (
    SELECT 
        /*Group Statistics*/
        MAX(CASE WHEN group_name = 'Test' THEN n_users END) AS n_test,
        MAX(CASE WHEN group_name = 'Control' THEN n_users END) AS n_control,
        
        /*Regular Method Results*/
        MAX(CASE WHEN group_name = 'Test' THEN avg_regular END) AS test_avg_regular,
        MAX(CASE WHEN group_name = 'Control' THEN avg_regular END) AS control_avg_regular,
        MAX(CASE WHEN group_name = 'Test' THEN var_regular END) AS test_var_regular,
        MAX(CASE WHEN group_name = 'Control' THEN var_regular END) AS control_var_regular,
        
        /*CUPED Method Results*/
        MAX(CASE WHEN group_name = 'Test' THEN avg_cuped END) AS test_avg_cuped,
        MAX(CASE WHEN group_name = 'Control' THEN avg_cuped END) AS control_avg_cuped,
        MAX(CASE WHEN group_name = 'Test' THEN var_cuped END) AS test_var_cuped,
        MAX(CASE WHEN group_name = 'Control' THEN var_cuped END) AS control_var_cuped
        
    FROM group_stats
)

/* ══════════════════════════════════════════════════════════════════════════
   6. FINAL OUTPUT - Both methods with complete statistics
   ══════════════════════════════════════════════════════════════════════════ */
SELECT 
    'Pure CUPED' AS method,
    ROUND(test_avg_cuped, 6) AS test_group_mean,
    ROUND(control_avg_cuped, 6) AS control_group_mean,
    ROUND(test_avg_cuped - control_avg_cuped, 6) AS treatment_effect,
    ROUND((test_avg_cuped - control_avg_cuped) / control_avg_cuped * 100, 2) AS treatment_effect_pct,
    
    /*95% Confidence Interval (Percentage) - Dashboard Method*/
    ROUND((((test_avg_cuped - control_avg_cuped) - 1.96 * SQRT(test_var_cuped / n_test + control_var_cuped / n_control)) / control_avg_cuped * 100), 2) AS ci_lower_pct,
    ROUND((((test_avg_cuped - control_avg_cuped) + 1.96 * SQRT(test_var_cuped / n_test + control_var_cuped / n_control)) / control_avg_cuped * 100), 2) AS ci_upper_pct,
    
    CASE WHEN ABS(test_avg_cuped - control_avg_cuped) > 1.96 * SQRT(test_var_cuped / n_test + control_var_cuped / n_control)
         THEN 'Significant'
         ELSE 'Not Significant'
    END AS statistical_significance,
    
    n_test,
    n_control
    
FROM treatment_effects

UNION ALL

SELECT 
    'Regular' AS method,
    ROUND(test_avg_regular, 6) AS test_group_mean,
    ROUND(control_avg_regular, 6) AS control_group_mean,
    ROUND(test_avg_regular - control_avg_regular, 6) AS treatment_effect,
    ROUND((test_avg_regular - control_avg_regular) / control_avg_regular * 100, 2) AS treatment_effect_pct,
    
    /*95% Confidence Interval (Percentage) - Dashboard Method*/
    ROUND((((test_avg_regular - control_avg_regular) - 1.96 * SQRT(test_var_regular / n_test + control_var_regular / n_control)) / control_avg_regular * 100), 2) AS ci_lower_pct,
    ROUND((((test_avg_regular - control_avg_regular) + 1.96 * SQRT(test_var_regular / n_test + control_var_regular / n_control)) / control_avg_regular * 100), 2) AS ci_upper_pct,
    
    CASE WHEN ABS(test_avg_regular - control_avg_regular) > 1.96 * SQRT(test_var_regular / n_test + control_var_regular / n_control)
         THEN 'Significant'
         ELSE 'Not Significant'
    END AS statistical_significance,
    
    n_test,
    n_control
    
FROM treatment_effects

ORDER BY method DESC; -- Pure CUPED first, then Regular