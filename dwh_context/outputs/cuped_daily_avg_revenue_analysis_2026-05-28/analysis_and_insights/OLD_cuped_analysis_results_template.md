# CUPED Analysis Results Template

## Test Configuration
- **Test ID**: [Test_ID]
- **Pre-experiment Period**: [Start_Date] to [End_Date] ([X] days)
- **Experiment Period**: [Start_Date] to [End_Date] ([X] days)  
- **Population**: "During" users only - users who were active during the experiment period
- **Population Definition**: Only includes users with activity/engagement during the test period, excluding users who were assigned to test but remained inactive
- **Total Sample Size**: [Total_Users]

## Key Findings Summary

**[🔴/🟡/🟢] CUPED Analysis Result: [UNSUCCESSFUL/PARTIALLY SUCCESSFUL/SUCCESSFUL]**

- **CUPED Effectiveness**: [Successful/Unsuccessful] - [X]% variance [reduction/increase]
- **Treatment Effect Detection**: [Significant/Not Significant] difference between test groups  
- **Methodology Recommendation**: [Use CUPED/Use Regular] analysis for final results
- **Correlation Strength**: [Strong/Moderate/Weak] (r=[value])
- **Business Impact**: [Treatment effect size and significance for decision making]

## Summary of Main Results

| Method | Treatment Effect (Test vs Control) | 95% Confidence Interval | Statistical Significance |
|--------|-------------------------------------|-------------------------|-------------------------|
| Regular | [diff_Test - diff_Control]         | ([Lower], [Upper])      | [Significant/Not Significant] |
| CUPED   | [diff_cuped_Test - diff_cuped_Control] | ([Lower], [Upper])   | [Significant/Not Significant] |

**Treatment Effect Calculation**: Difference-in-differences (Test group change - Control group change)

## Detailed Statistical Results

### Sample Sizes per Test Group

| Test Group | Sample Size (n_users) |
|------------|----------------------|
| Control    | [TBD]               |
| Test       | [TBD]               |
| **Total**  | [TBD]               |

### Treatment Effects by Method

#### Regular Method (diff_regular per group)

| Test Group | Baseline Revenue | Experiment Revenue | Treatment Effect | Standard Error |
|------------|------------------|--------------------|--------------------|----------------|
| Control    | [TBD]           | [TBD]              | [TBD]             | [TBD]          |
| Test       | [TBD]           | [TBD]              | [TBD]             | [TBD]          |

#### CUPED Method (diff_Y_cuped per group)

| Test Group | Baseline Revenue | CUPED Experiment Revenue | CUPED Treatment Effect | Standard Error |
|------------|------------------|--------------------------|------------------------|----------------|
| Control    | [TBD]           | [TBD]                   | [TBD]                 | [TBD]          |
| Test       | [TBD]           | [TBD]                   | [TBD]                 | [TBD]          |

### Variance Reduction Analysis

| Test Group | Regular Variance | CUPED Variance | Variance Reduction % | Interpretation |
|------------|------------------|----------------|---------------------|----------------|
| Control    | [TBD]           | [TBD]          | [TBD]%             | [Assessment]   |
| Test       | [TBD]           | [TBD]          | [TBD]%             | [Assessment]   |
| **Average**| [TBD]           | [TBD]          | [TBD]%             | [Overall Assessment] |

## CUPED Effectiveness Assessment

### Theta Coefficient
- **Value**: [TBD] 
- **Interpretation**: For every $1 above average in pre-period performance, CUPED adjusts experiment revenue by $[theta_coefficient]

### Pearson Correlation Coefficient
- **Value**: [TBD]
- **Interpretation**: [Strong/Moderate/Weak] correlation - [Expected CUPED effectiveness level]

### Variance Reduction Metrics
- **Value**: [TBD]% 
- **Interpretation**: CUPED [reduced/increased] measurement uncertainty by [X]%, [enabling/hindering] precise treatment effect detection

## Execution Instructions

**To populate this template:**

1. **Run Query 02** (`02_cuped_covariance_calculation.sql`) to get theta coefficient and Pearson correlation
2. **Run Query 04** (`04_diff_calculation.sql`) to get all group-level statistics
3. **Calculate confidence intervals** using: `CI = Treatment_Effect ± 1.96 × SE_treatment_effect`
4. **Calculate variance reduction**: `(1 - var_cuped/var_regular) × 100%`
5. **Replace all [TBD] placeholders** with actual values from query results

---
*Template for CUPED Analysis Results*  
*Update placeholders with actual data from query execution*