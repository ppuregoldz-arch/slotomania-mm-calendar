/*
PURE CUPED Treatment Effect Calculation
======================================
Test ID: ahhcuJnMV1
Purpose: Calculate treatment effect using PURE CUPED methodology
Formula: Effect = AVG(Y_CUPED)_Test - AVG(Y_CUPED)_Control
Standard Error: SE = SQRT(VAR_Test/N_Test + VAR_Control/N_Control)

This follows standard CUPED practice and dashboard methodology:
- Direct comparison of CUPED-adjusted values
- No reintroduction of pre-period metrics
- Proper statistical inference on variance-reduced outcome
*/

with pure_cuped_results as (
    -- Results from the PURE CUPED analysis
    select 'Control' as group_name, 111917 as n_users, 1.35087827486576 as avg_Y_CUPED, 47.9612589293266 as var_Y_CUPED, 0.0207012827430419 as se_Y_CUPED
    union all
    select 'Test' as group_name, 447513 as n_users, 1.34039848891315 as avg_Y_CUPED, 65.6872707234454 as var_Y_CUPED, 0.0121154006562787 as se_Y_CUPED
),

treatment_effect_calculation as (
    select
        max(case when group_name = 'Test' then avg_Y_CUPED end) as test_avg_Y_CUPED,
        max(case when group_name = 'Control' then avg_Y_CUPED end) as control_avg_Y_CUPED,
        max(case when group_name = 'Test' then var_Y_CUPED end) as test_var_Y_CUPED,
        max(case when group_name = 'Control' then var_Y_CUPED end) as control_var_Y_CUPED,
        max(case when group_name = 'Test' then n_users end) as test_n_users,
        max(case when group_name = 'Control' then n_users end) as control_n_users,
        max(case when group_name = 'Test' then se_Y_CUPED end) as test_se_Y_CUPED,
        max(case when group_name = 'Control' then se_Y_CUPED end) as control_se_Y_CUPED
    from pure_cuped_results
)

select
    /*Group-level results*/
    test_avg_Y_CUPED,
    control_avg_Y_CUPED,
    test_n_users,
    control_n_users,
    
    /*PURE CUPED Treatment Effect*/
    test_avg_Y_CUPED - control_avg_Y_CUPED as treatment_effect,
    
    /*Standard Error calculation: SE = SQRT(VAR_Test/N_Test + VAR_Control/N_Control)*/
    sqrt(test_var_Y_CUPED / test_n_users + control_var_Y_CUPED / control_n_users) as treatment_effect_se,
    
    /*Alternative SE calculation using group SEs: SQRT(SE_Test² + SE_Control²)*/
    sqrt(test_se_Y_CUPED * test_se_Y_CUPED + control_se_Y_CUPED * control_se_Y_CUPED) as treatment_effect_se_alternative,
    
    /*95% Confidence Interval (Absolute)*/
    (test_avg_Y_CUPED - control_avg_Y_CUPED) - 1.96 * sqrt(test_var_Y_CUPED / test_n_users + control_var_Y_CUPED / control_n_users) as ci_lower,
    (test_avg_Y_CUPED - control_avg_Y_CUPED) + 1.96 * sqrt(test_var_Y_CUPED / test_n_users + control_var_Y_CUPED / control_n_users) as ci_upper,
    
    /*95% Confidence Interval (Percentage) - Dashboard Method*/
    (((test_avg_Y_CUPED - control_avg_Y_CUPED) - 1.96 * sqrt(test_var_Y_CUPED / test_n_users + control_var_Y_CUPED / control_n_users)) / control_avg_Y_CUPED * 100) as ci_lower_pct,
    (((test_avg_Y_CUPED - control_avg_Y_CUPED) + 1.96 * sqrt(test_var_Y_CUPED / test_n_users + control_var_Y_CUPED / control_n_users)) / control_avg_Y_CUPED * 100) as ci_upper_pct,
    
    /*Relative Lift: Effect / Control_Mean * 100*/
    (test_avg_Y_CUPED - control_avg_Y_CUPED) / control_avg_Y_CUPED * 100 as relative_lift_percent,
    
    /*Statistical significance check (|effect| > 1.96 * SE)*/
    case when abs(test_avg_Y_CUPED - control_avg_Y_CUPED) > 1.96 * sqrt(test_var_Y_CUPED / test_n_users + control_var_Y_CUPED / control_n_users)
         then 'Significant'
         else 'Not Significant'
    end as statistical_significance,
    
    /*Individual group variances and SEs for reference*/
    test_var_Y_CUPED,
    control_var_Y_CUPED,
    test_se_Y_CUPED,
    control_se_Y_CUPED

from treatment_effect_calculation;