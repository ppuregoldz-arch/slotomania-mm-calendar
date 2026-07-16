# CUPED Variables and Statistical Measures Explained

## Overview
This document explains the key variables and statistical measures used in the CUPED (Controlled-experiment Using Pre-Experiment Data) daily average revenue analysis.

## Core CUPED Variables

### Average Revenue Metrics

#### `avg_rev_before`
- **Definition**: Average daily revenue per user during the pre-experiment period (14 days)
- **Period**: May 6-19, 2024
- **Purpose**: Establishes baseline revenue patterns for each user
- **Formula**: AVG(daily revenue) over pre-experiment period

#### `avg_rev_during`
- **Definition**: Average daily revenue per user during the experiment period (7 days)
- **Period**: May 20-26, 2024
- **Purpose**: Measures actual experiment period performance
- **Formula**: AVG(daily revenue) over experiment period

### Population Averages

#### `overall_avg_rev_before`
- **Definition**: Average of all users' pre-experiment revenue across the entire population
- **Purpose**: Used to calculate individual user deviations from population mean
- **Calculation**: Single value applied to all users via window function

#### `overall_avg_rev_during`
- **Definition**: Average of all users' experiment period revenue across the entire population
- **Purpose**: Used to calculate individual user deviations from population mean
- **Calculation**: Single value applied to all users via window function

### Deviation Metrics

#### `deviation_before`
- **Definition**: How much each user's pre-experiment revenue differs from the population average
- **Formula**: `avg_rev_before - overall_avg_rev_before`
- **Purpose**: Measures individual user's baseline performance relative to population
- **Range**: Can be positive (above average) or negative (below average)

#### `deviation_during`
- **Definition**: How much each user's experiment revenue differs from the population average
- **Formula**: `avg_rev_during - overall_avg_rev_during`
- **Purpose**: Measures individual user's experiment performance relative to population
- **CUPED Usage**: This is the metric that gets adjusted using the theta coefficient

## Statistical Measures for CUPED

### Covariance (`covariance_before_during`)
- **Definition**: Measures how the pre-experiment and experiment deviations move together
- **Formula**: `COV(X,Y) = Σ[(Xi - X̄)(Yi - Ȳ)] / (n-1)`
- **Sample vs Population**: Uses (n-1) denominator for sample covariance (Bessel's correction)
- **Purpose**: Essential for calculating the theta coefficient
- **Interpretation**: 
  - Positive: Users with higher pre-experiment revenue tend to have higher experiment revenue
  - Negative: Inverse relationship between pre and experiment performance
  - Zero: No linear relationship between periods

### Variance of Before Period (`variance_before`)
- **Definition**: Measures the spread of pre-experiment deviations
- **Formula**: `VAR(X) = Σ[(Xi - X̄)²] / (n-1)`
- **Purpose**: Denominator in theta coefficient calculation
- **Usage**: Higher variance means more spread in baseline performance

### Variance of During Period (`variance_during`)
- **Definition**: Measures the spread of experiment period deviations
- **Formula**: `VAR(Y) = Σ[(Yi - Ȳ)²] / (n-1)`
- **Purpose**: Used for validation and variance reduction assessment
- **CUPED Goal**: Post-CUPED variance should be lower than this original variance

### Theta Coefficient (`theta_coefficient`)
- **Definition**: The CUPED adjustment factor that optimally reduces variance
- **Formula**: `θ = COV(Y,X) / VAR(X)`
- **Key Property**: Minimizes the variance of the CUPED-adjusted metric
- **Usage**: Applied as: `CUPED_adjusted = Y - θ × X`
- **Where**: Y = experiment deviation, X = pre-experiment deviation
- **Calculation Method**: Uses all users pooled together (not per test group)

### Pearson Correlation Coefficient (`Pearson_Correlation_Coefficient`)
- **Definition**: Standardized measure of linear relationship strength between pre and experiment deviations
- **Formula**: `r = COV(X,Y) / (SD(X) × SD(Y))`
- **Range**: Always between -1 and +1
- **Interpretation**:
  - **+1**: Perfect positive linear relationship
  - **-1**: Perfect negative linear relationship
  - **0**: No linear relationship
  - **|r| > 0.7**: Strong relationship
  - **0.3 < |r| < 0.7**: Moderate relationship
  - **|r| < 0.3**: Weak relationship

## CUPED Methodology Requirements

### Key Assumptions
1. **Stable Relationship**: The relationship between pre-experiment and experiment metrics should be consistent across test groups
2. **Linear Relationship**: CUPED assumes a linear relationship between baseline and outcome metrics
3. **Same Population**: Pre-experiment and experiment periods should represent the same underlying population

### Quality Indicators
- **Strong Correlation**: |r| > 0.3 indicates CUPED will provide meaningful variance reduction
- **Consistent Theta**: Theta should be similar across different subgroups if calculated separately
- **Positive Variance Reduction**: Post-CUPED variance should be measurably lower than original variance

### Expected Variance Reduction
- **Formula**: `Variance Reduction = r² × 100%`
- **Example**: If r = 0.6, expect ~36% variance reduction
- **Benefit**: Smaller confidence intervals and higher statistical power for detecting treatment effects

## CUPED-Adjusted Metrics

### Y_CUPED (`Y_CUPED`)
- **Definition**: The variance-reduced, CUPED-adjusted experiment metric
- **Formula**: `Y_CUPED = Y - θ × (X - X̄)`
- **In our context**: `Y_CUPED = avg_rev_during - theta_coefficient × deviation_before`
- **Purpose**: Removes the predictable portion of variance based on pre-experiment performance
- **Expected outcome**: Lower variance compared to original `avg_rev_during`

### Components of Y_CUPED Formula
- **Y**: Original outcome metric (`avg_rev_during`)
- **θ (theta)**: Optimal coefficient that minimizes variance (`theta_coefficient`)
- **X**: Pre-experiment covariate metric (`avg_rev_before`)
- **X̄**: Population mean of pre-experiment metric (`overall_avg_rev_before`)
- **(X - X̄)**: Pre-experiment deviation (`deviation_before`)

### CUPED Adjustment (`cuped_adjustment`)
- **Definition**: The amount subtracted from the original metric to create Y_CUPED
- **Formula**: `theta_coefficient × deviation_before`
- **Interpretation**:
  - **Positive adjustment**: User performed above average pre-experiment, so we reduce their experiment metric
  - **Negative adjustment**: User performed below average pre-experiment, so we increase their experiment metric
  - **Zero adjustment**: User performed at population average pre-experiment

### Variance Reduction Effect (`variance_reduction_effect`)
- **Definition**: Measure of how much variance was reduced for each user
- **Purpose**: Diagnostic metric to validate CUPED effectiveness
- **Expected pattern**: Should show reduced spread compared to original deviations

### Key Properties of Y_CUPED
1. **Unbiased**: E[Y_CUPED] = E[Y] - treatment effects are preserved
2. **Reduced Variance**: VAR(Y_CUPED) ≤ VAR(Y) - statistical power is increased
3. **Same Treatment Effects**: Differences between test groups are maintained
4. **Better Precision**: Smaller confidence intervals for treatment effect estimates

## Treatment Effect Analysis (Difference Calculations)

### Group-Level Aggregated Metrics

#### `avg_Y_cuped_during`
- **Definition**: Average of CUPED-adjusted revenue across all users within each test group
- **Formula**: `AVG(Y_CUPED)` per test group
- **Purpose**: Provides the CUPED-adjusted group mean for treatment effect calculation
- **Expected outcome**: Should have lower variance than original group means

#### `original_avg_rev_during` (Group Level)
- **Definition**: Average of original experiment revenue across all users within each test group
- **Formula**: `AVG(original_avg_rev_during)` per test group
- **Purpose**: Provides the non-CUPED group mean for comparison
- **Usage**: Baseline for comparing CUPED effectiveness

#### `avg_rev_before` (Group Level)
- **Definition**: Average of pre-experiment revenue across all users within each test group
- **Formula**: `AVG(avg_rev_before)` per test group
- **Purpose**: Group-level baseline performance for treatment effect calculation
- **Assumption**: Should be similar across test groups (randomization check)

### Treatment Effects (Differences)

#### `diff_Y_cuped`
- **Definition**: CUPED-adjusted treatment effect per test group
- **Formula**: `avg_Y_cuped_during - avg_rev_before`
- **Purpose**: Measures the treatment impact using variance-reduced metrics
- **Benefits**: 
  - More precise estimate due to reduced variance
  - Higher statistical power for detecting true treatment effects
  - Smaller confidence intervals

#### `diff_regular`
- **Definition**: Regular (non-CUPED) treatment effect per test group
- **Formula**: `original_avg_rev_during - avg_rev_before`
- **Purpose**: Traditional treatment effect calculation for comparison
- **Usage**: Benchmark to demonstrate CUPED improvement

### Treatment Effect Comparison Analysis

#### Key Comparisons
1. **Effect Size**: `diff_Y_cuped` vs `diff_regular` - should show similar treatment effects
2. **Precision**: CUPED effects should have smaller standard errors
3. **Statistical Power**: CUPED analysis should detect significance with smaller sample sizes
4. **Variance Reduction**: Compare group-level variance between CUPED and regular metrics

#### Expected Patterns
- **Same Direction**: Both `diff_Y_cuped` and `diff_regular` should show same positive/negative direction
- **Similar Magnitude**: Treatment effects should be approximately equal (CUPED preserves treatment effects)
- **Reduced Variance**: CUPED differences should show less variability across repeated analyses
- **Improved Detection**: Significant effects may be detected with CUPED that weren't significant with regular analysis

#### Validation Checks
- **Randomization Balance**: `avg_rev_before` should be similar across test groups
- **Effect Preservation**: `diff_Y_cuped` ≈ `diff_regular` (treatment effects preserved)
- **Variance Reduction**: Standard deviation of CUPED metrics < standard deviation of regular metrics
- **Correlation Strength**: Higher correlation between before/during periods → better CUPED effectiveness

## Statistical Inference Measures

### Sample Size (`n_users`)
- **Definition**: Number of users in each test group
- **Purpose**: Required for standard error calculations and statistical power assessment
- **Usage**: Larger sample sizes → smaller standard errors → more precise estimates

### User-Level Difference Variances

#### `var_user_diff_cuped`
- **Definition**: Variance of CUPED user-level differences (Y_CUPED - avg_rev_before) within each group
- **Formula**: `VAR(Y_CUPED - avg_rev_before)` per test group
- **Purpose**: Measures spread of individual treatment responses using CUPED-adjusted metrics
- **Expected outcome**: Should be smaller than `var_user_diff_regular` (variance reduction)

#### `var_user_diff_regular`
- **Definition**: Variance of regular user-level differences (original_avg_rev_during - avg_rev_before) within each group
- **Formula**: `VAR(original_avg_rev_during - avg_rev_before)` per test group
- **Purpose**: Baseline variance for comparison with CUPED variance reduction
- **Usage**: Reference point to measure CUPED effectiveness

### Standard Errors

#### `se_cuped`
- **Definition**: Standard error of the CUPED-adjusted group mean
- **Formula**: `SQRT(var_user_diff_cuped / n_users)`
- **Purpose**: Measures precision of the CUPED treatment effect estimate
- **Expected outcome**: Should be smaller than `se_regular` (improved precision)

#### `se_regular`
- **Definition**: Standard error of the regular group mean
- **Formula**: `SQRT(var_user_diff_regular / n_users)`
- **Purpose**: Baseline precision measure for comparison with CUPED improvement
- **Usage**: Demonstrates CUPED's variance reduction benefit

### Standard Deviations (Reference Metrics)

#### `sd_user_diff_cuped`
- **Definition**: Standard deviation of CUPED user-level differences within each group
- **Formula**: `SQRT(var_user_diff_cuped)`
- **Purpose**: Shows spread of individual user responses after CUPED adjustment
- **Interpretation**: Lower values indicate more consistent treatment responses

#### `sd_user_diff_regular`
- **Definition**: Standard deviation of regular user-level differences within each group
- **Formula**: `SQRT(var_user_diff_regular)`
- **Purpose**: Baseline spread measure for comparison
- **CUPED Goal**: `sd_user_diff_cuped` should be smaller than `sd_user_diff_regular`

## Treatment Effect Confidence Intervals

### Confidence Interval Formula
**CI = Treatment_Effect ± (Critical_Value × SE_Treatment_Effect)**

### Treatment Effect Standard Error
**For comparing two groups (e.g., Test vs Control):**
**SE_Treatment_Effect = SQRT(SE_group1² + SE_group2²)**

### Example Calculation
```sql
-- For CUPED treatment effect CI:
SE_treatment_cuped = SQRT(se_cuped_test² + se_cuped_control²)
CI_lower_cuped = (diff_cuped_test - diff_cuped_control) - 1.96 * SE_treatment_cuped
CI_upper_cuped = (diff_cuped_test - diff_cuped_control) + 1.96 * SE_treatment_cuped

-- For regular treatment effect CI:
SE_treatment_regular = SQRT(se_regular_test² + se_regular_control²)
CI_lower_regular = (diff_regular_test - diff_regular_control) - 1.96 * SE_treatment_regular  
CI_upper_regular = (diff_regular_test - diff_regular_control) + 1.96 * SE_treatment_regular
```

### Expected CUPED Benefits
1. **Narrower Confidence Intervals**: CUPED CIs should be smaller than regular CIs
2. **Higher Statistical Power**: More likely to detect significant treatment effects
3. **Better Precision**: Smaller standard errors lead to more reliable estimates
4. **Reduced Sample Size Requirements**: May detect effects with fewer users

### Variance Reduction Assessment
**Variance Reduction Percentage = (1 - var_cuped/var_regular) × 100%**

**Expected reduction based on correlation:**
- If correlation = 0.5, expect ~25% variance reduction
- If correlation = 0.7, expect ~49% variance reduction
- Higher correlation → better CUPED performance

## Usage in Analysis Pipeline

1. **Step 1**: Calculate base data (deviations) → Query 01
2. **Step 2**: Calculate covariance and theta → Query 02  
3. **Step 3**: Apply theta to create CUPED-adjusted metrics → Query 03 (Y_cuped.sql)
4. **Step 4**: Calculate treatment effects using adjusted metrics → Query 04 (diff_calculation.sql)
5. **Step 5**: Statistical significance testing and confidence intervals → Query 05 (next step)
6. **Step 6**: Compare CUPED vs non-CUPED results for validation

## Validation Checklist

- [ ] Correlation coefficient shows meaningful relationship (|r| > 0.3)
- [ ] Theta coefficient is reasonable (typically between 0 and 1 for revenue metrics)
- [ ] Sample sizes are adequate for stable estimates
- [ ] Pre-experiment period captures stable baseline behavior
- [ ] No major external events during analysis periods