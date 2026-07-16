# Difference-in-Differences (Diff-in-Diff) Methodology Summary

## What Diff-in-Diff Measures

**Difference-in-Differences** is a causal inference methodology that estimates treatment effects by comparing the change in outcomes between treatment and control groups over time.

**Core Principle**: The treatment effect is measured as the difference between:
- The change experienced by the treatment group (Test_During - Test_Before)
- The change experienced by the control group (Control_During - Control_Before)

**Formula**: 
```
Treatment Effect = (Test_During - Test_Before) - (Control_During - Control_Before)
                 = Mean_User_Diff_Test - Mean_User_Diff_Control
```

## Calculation Flow

### Step 1: User-Level Base Data
- Calculate `avg_rev_before = SUM(gross_rev during before period) / 14 days`
- Calculate `avg_rev_during = SUM(gross_rev during experiment period) / 7 days`
- Include only users active during the experiment period ("during users")
- Users without before activity receive `avg_rev_before = 0` (no exclusion bias)

### Step 2: User-Level Change Scores
For each user: `user_diff = avg_rev_during - avg_rev_before`

### Step 3: Group-Level Aggregation
For each group (Test/Control):
- `mean_user_diff = AVG(user_diff)`
- `var_user_diff = VARIANCE(user_diff)`
- `n_users = COUNT(*)`

### Step 4: Treatment Effect Calculation
```
Effect = mean_user_diff_test - mean_user_diff_control
```

### Step 5: Statistical Inference
- **Standard Error**: `SE = SQRT(var_test/n_test + var_control/n_control)`
- **95% Confidence Interval**: `Effect ± 1.96 × SE`
- **Percentage Metrics**: Use control baseline as denominator

## How It Differs from CUPED

| Aspect | Diff-in-Diff | CUPED |
|--------|---------------|-------|
| **Primary Goal** | Remove time trends and external factors | Reduce variance using pre-period correlation |
| **Adjustment Method** | Difference out common trends | Regression-based variance reduction |
| **Key Metric** | User-level change scores (`during - before`) | CUPED-adjusted outcome (`Y - θ×(X - X̄)`) |
| **Pre-period Role** | Direct subtraction from outcome | Covariance-weighted adjustment |
| **Statistical Focus** | Causal inference under parallel trends | Precision improvement in randomized experiments |
| **Variance Source** | Variance of user change scores | Variance of CUPED-adjusted outcomes |

### Key Methodological Differences:

1. **CUPED** uses the theta coefficient (θ = COV(Y,X)/VAR(X)) to optimally weight the pre-period adjustment
2. **Diff-in-Diff** uses a simple subtraction (coefficient = 1) assuming parallel trends
3. **CUPED** focuses on variance reduction in randomized experiments
4. **Diff-in-Diff** focuses on removing confounding from time-varying factors

## Why Calculate Variance on user_diff = during - before

The variance of user-level change scores (`user_diff`) is the correct statistical foundation for Diff-in-Diff because:

### Statistical Rationale:
1. **Direct Treatment Effect Measurement**: `user_diff` represents the individual-level change that we want to compare between groups
2. **Proper Uncertainty Quantification**: The variance of change scores captures the true uncertainty in treatment effect estimation
3. **Causal Inference Foundation**: Diff-in-Diff assumes that without treatment, both groups would experience parallel changes - variance of `user_diff` measures deviations from this assumption

### Why Not Other Metrics:
- **Variance of `during` alone**: Ignores baseline differences and time trends
- **Variance of `before` alone**: Not relevant for treatment effect during the experiment period
- **Separate variances**: Doesn't capture the correlation between before/during within users

## Formulas Used

### Treatment Effect:
```
Effect = AVG(user_diff_test) - AVG(user_diff_control)
       = (Test_During - Test_Before) - (Control_During - Control_Before)
```

### Standard Error:
```
SE = SQRT(VAR(user_diff_test)/n_test + VAR(user_diff_control)/n_control)
```

### 95% Confidence Interval:
```
CI_lower = Effect - 1.96 × SE
CI_upper = Effect + 1.96 × SE
```

### Percentage Metrics:
Using control baseline as denominator:
```
Effect_pct = (Effect / Control_Before_Avg) × 100
CI_lower_pct = (CI_lower / Control_Before_Avg) × 100  
CI_upper_pct = (CI_upper / Control_Before_Avg) × 100
```

## Key Assumptions

1. **Parallel Trends**: Without treatment, both groups would experience similar changes over time
2. **No Spillover Effects**: Treatment of one group doesn't affect the control group
3. **Stable Treatment**: Treatment effect is constant across the experiment period
4. **Proper Randomization**: Initial group assignment is random (for internal validity)

## Interpretation

A **positive treatment effect** indicates that the Test group experienced a larger increase (or smaller decrease) in daily average revenue compared to the Control group, after accounting for common time trends and external factors that affected both groups equally.

The **confidence interval** provides the range of plausible values for the true treatment effect, accounting for sampling uncertainty in the change score estimates.