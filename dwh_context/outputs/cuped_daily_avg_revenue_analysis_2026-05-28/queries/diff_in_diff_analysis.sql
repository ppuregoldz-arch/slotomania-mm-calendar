/*
DIFFERENCE-IN-DIFFERENCES ANALYSIS
=================================
Test ID: ahhcuJnMV1
Purpose: Pure Diff-in-Diff methodology for treatment effect estimation
Formula: Effect = (Test_During - Test_Before) - (Control_During - Control_Before)

METHODOLOGY:
- Calculate user-level change scores: user_diff = avg_rev_during - avg_rev_before
- Compare average change between Test and Control groups
- No CUPED adjustment, theta, covariance, or Y_CUPED involved
- Direct comparison of group-level change from baseline

BASELINE CALCULATION:
- avg_rev_before = SUM(gross_rev during before period) / 14 days
- avg_rev_during = SUM(gross_rev during experiment period) / 7 days
- Users without before activity: avg_rev_before = 0 (proper population inclusion)

STATISTICAL INFERENCE:
- Variance calculated on user_diff (change scores)
- Standard Error: SE = SQRT(var_test/n_test + var_control/n_control)
- 95% CI: effect ± 1.96 * SE
- Percentage metrics use Control baseline as denominator
*/

WITH 

/* ══════════════════════════════════════════════════════════════════════════
   1. BASE DATA - User-level metrics for both periods (Same as CUPED query)
   ══════════════════════════════════════════════════════════════════════════ */
base_data AS (
    SELECT 
        user_id,
        group_name,
        
        /*TRUE average daily revenue during pre-experiment period (14 days)*/
        COALESCE(avg_rev_before, 0) AS avg_rev_before,
        
        /*TRUE average daily revenue during experiment period (7 days)*/
        COALESCE(avg_rev_during, 0) AS avg_rev_during

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
    
    /*FIXED: NO NULL FILTER - include all during users for proper methodology*/
),

/* ══════════════════════════════════════════════════════════════════════════
   2. USER-LEVEL DIFF CALCULATION - Core of Diff-in-Diff methodology
   ══════════════════════════════════════════════════════════════════════════ */
user_diff_data AS (
    SELECT 
        user_id,
        group_name,
        avg_rev_before,
        avg_rev_during,
        
        /*DIFF-IN-DIFF: Calculate user-level change score*/
        avg_rev_during - avg_rev_before AS user_diff
        
    FROM base_data
),

/* ══════════════════════════════════════════════════════════════════════════
   3. GROUP STATISTICS - Aggregate user_diff by group for Diff-in-Diff
   ══════════════════════════════════════════════════════════════════════════ */
group_stats AS (
    SELECT 
        group_name,
        COUNT(*) AS n_users,
        
        /*Group-level period averages*/
        AVG(avg_rev_before) AS avg_before,
        AVG(avg_rev_during) AS avg_during,
        
        /*DIFF-IN-DIFF: Group-level change statistics*/
        AVG(user_diff) AS mean_user_diff,
        VARIANCE(user_diff) AS var_user_diff,
        SQRT(VARIANCE(user_diff)) AS sd_user_diff,
        SQRT(VARIANCE(user_diff) / COUNT(*)) AS se_user_diff
        
    FROM user_diff_data
    GROUP BY group_name
),

/* ══════════════════════════════════════════════════════════════════════════
   4. DIFF-IN-DIFF TREATMENT EFFECT - Calculate final treatment effect
   ══════════════════════════════════════════════════════════════════════════ */
diff_in_diff_effect AS (
    SELECT 
        /*Group Statistics*/
        MAX(CASE WHEN group_name = 'Test' THEN n_users END) AS n_test,
        MAX(CASE WHEN group_name = 'Control' THEN n_users END) AS n_control,
        
        /*Period Averages by Group*/
        MAX(CASE WHEN group_name = 'Test' THEN avg_before END) AS test_before_avg,
        MAX(CASE WHEN group_name = 'Test' THEN avg_during END) AS test_during_avg,
        MAX(CASE WHEN group_name = 'Control' THEN avg_before END) AS control_before_avg,
        MAX(CASE WHEN group_name = 'Control' THEN avg_during END) AS control_during_avg,
        
        /*Group-level Change Scores*/
        MAX(CASE WHEN group_name = 'Test' THEN mean_user_diff END) AS test_mean_user_diff,
        MAX(CASE WHEN group_name = 'Control' THEN mean_user_diff END) AS control_mean_user_diff,
        
        /*Variance of User Differences*/
        MAX(CASE WHEN group_name = 'Test' THEN var_user_diff END) AS test_var_user_diff,
        MAX(CASE WHEN group_name = 'Control' THEN var_user_diff END) AS control_var_user_diff
        
    FROM group_stats
)

/* ══════════════════════════════════════════════════════════════════════════
   5. FINAL OUTPUT - Complete Diff-in-Diff Analysis Results
   ══════════════════════════════════════════════════════════════════════════ */
SELECT 
    'Diff-in-Diff' AS method,
    
    /*Group-level Period Averages*/
    ROUND(test_before_avg, 6) AS test_before_avg,
    ROUND(test_during_avg, 6) AS test_during_avg,
    ROUND(control_before_avg, 6) AS control_before_avg,
    ROUND(control_during_avg, 6) AS control_during_avg,
    
    /*Group-level Mean Change Scores*/
    ROUND(test_mean_user_diff, 6) AS test_mean_user_diff,
    ROUND(control_mean_user_diff, 6) AS control_mean_user_diff,
    
    /*DIFF-IN-DIFF TREATMENT EFFECT*/
    /*Effect = (Test_During - Test_Before) - (Control_During - Control_Before)*/
    /*       = mean_user_diff_test - mean_user_diff_control*/
    ROUND(test_mean_user_diff - control_mean_user_diff, 6) AS treatment_effect,
    
    /*Standard Error of Treatment Effect*/
    /*SE = SQRT(var_test/n_test + var_control/n_control)*/
    ROUND(SQRT(test_var_user_diff / n_test + control_var_user_diff / n_control), 8) AS se,
    
    /*95% Confidence Interval (Absolute)*/
    ROUND((test_mean_user_diff - control_mean_user_diff) - 1.96 * SQRT(test_var_user_diff / n_test + control_var_user_diff / n_control), 6) AS ci_lower,
    ROUND((test_mean_user_diff - control_mean_user_diff) + 1.96 * SQRT(test_var_user_diff / n_test + control_var_user_diff / n_control), 6) AS ci_upper,
    
    /*PERCENTAGE METRICS - Using Control Baseline as Denominator*/
    /*Treatment Effect as Percentage of Control Baseline*/
    ROUND((test_mean_user_diff - control_mean_user_diff) / NULLIF(control_before_avg, 0) * 100, 2) AS treatment_effect_pct,
    
    /*95% Confidence Interval (Percentage)*/
    ROUND(((test_mean_user_diff - control_mean_user_diff) - 1.96 * SQRT(test_var_user_diff / n_test + control_var_user_diff / n_control)) / NULLIF(control_before_avg, 0) * 100, 2) AS ci_lower_pct,
    ROUND(((test_mean_user_diff - control_mean_user_diff) + 1.96 * SQRT(test_var_user_diff / n_test + control_var_user_diff / n_control)) / NULLIF(control_before_avg, 0) * 100, 2) AS ci_upper_pct,
    
    /*Statistical Significance*/
    CASE WHEN ABS(test_mean_user_diff - control_mean_user_diff) > 1.96 * SQRT(test_var_user_diff / n_test + control_var_user_diff / n_control)
         THEN 'Significant'
         ELSE 'Not Significant'
    END AS statistical_significance,
    
    /*Sample Sizes*/
    n_test,
    n_control

FROM diff_in_diff_effect;