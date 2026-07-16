# CUPED Analysis Results - Test ID: ahhcuJnMV1

## Test Configuration
- **Test ID**: ahhcuJnMV1
- **Pre-experiment Period**: May 6-19, 2026 (14 days)
- **Experiment Period**: May 20-26, 2026 (7 days)  
- **Population**: "During" users only - users who were active during the experiment period (May 20-26, 2026)
- **Population Definition**: Only includes users with activity/engagement during the test period, excluding users who were assigned to test but remained inactive
- **Total Sample Size**: 519,663

## Key Findings Summary

**🔴 CUPED Analysis Result: UNSUCCESSFUL**

- **CUPED Effectiveness**: Unsuccessful - 180% variance increase (opposite of intended effect)
- **Treatment Effect Detection**: Not Significant difference between test groups in both methods
- **Methodology Recommendation**: Use Regular analysis for final results; investigate CUPED implementation
- **Correlation Strength**: Strong (r=0.76) - Should predict good CUPED performance, but failed
- **Business Impact**: No significant revenue difference detected between Test and Control groups

## Summary of Main Results

| Method | Treatment Effect (Test vs Control) | 95% Confidence Interval | Statistical Significance |
|--------|-------------------------------------|-------------------------|-------------------------|
| Regular | -$0.0163                           | (-0.0440, +0.0114)      | Not Significant (p > 0.05) |
| CUPED   | -$0.0413                           | (-0.1558, +0.0732)      | Not Significant (p > 0.05) |

**Treatment Effect Calculation**: Difference-in-differences  
*Regular: (0.0014) - (0.0177) = -0.0163*  
*CUPED: (-0.0036) - (0.0377) = -0.0413*

## Detailed Statistical Results

### Sample Sizes per Test Group

| Test Group | Sample Size (n_users) |
|------------|----------------------|
| Control    | 103,903             |
| Test       | 415,760             |
| **Total**  | **519,663**         |

### Treatment Effects by Method

#### Regular Method (diff_regular per group)

| Test Group | Baseline Revenue | Experiment Revenue | Treatment Effect | Standard Error |
|------------|------------------|--------------------|--------------------|----------------|
| Control    | $1.6552         | $1.673            | +$0.0177          | 0.031033       |
| Test       | $1.6869         | $1.6883           | +$0.0014          | 0.016365       |

#### CUPED Method (diff_Y_cuped per group)

| Test Group | Baseline Revenue | CUPED Experiment Revenue | CUPED Treatment Effect | Standard Error |
|------------|------------------|--------------------------|------------------------|----------------|
| Control    | $1.6552         | $1.693                  | +$0.0377              | 0.051953       |
| Test       | $1.6869         | $1.6833                 | -$0.0036              | 0.028144       |

### Variance Reduction Analysis

| Test Group | Regular Variance | CUPED Variance | Variance Reduction % | Interpretation |
|------------|------------------|----------------|---------------------|----------------|
| Control    | 100.07          | 280.45         | -180.3%            | **CUPED Failed - Increased Variance** |
| Test       | 111.34          | 329.33         | -195.8%            | **CUPED Failed - Increased Variance** |
| **Average**| 105.71          | 304.89         | **-188.5%**        | **CUPED Methodology Unsuccessful** |

**⚠️ Critical Finding**: CUPED increased variance rather than reducing it, indicating the methodology was not effective for this test.

## CUPED Effectiveness Assessment

### Theta Coefficient
- **Value**: 0.7880
- **Interpretation**: For every $1 above average in pre-period performance, CUPED adjusts experiment revenue down by $0.79

### Pearson Correlation Coefficient
- **Value**: 0.7614
- **Interpretation**: Strong correlation (|r| > 0.7) - Should indicate excellent CUPED effectiveness, but results show otherwise

### Variance Reduction Metrics
- **Value**: -188.5% (average across test groups)
- **Interpretation**: **⚠️ CUPED FAILED** - Increased measurement uncertainty by 189%, making treatment effect detection less precise rather than more precise

**Critical Issue**: Despite strong correlation (r=0.76), CUPED dramatically increased variance instead of reducing it, suggesting a fundamental issue with the implementation or data characteristics.

---

## Statistical Analysis Summary

### Confidence Interval Calculations
- **Regular Method SE**: sqrt(0.031033² + 0.016365²) = 0.0349
- **CUPED Method SE**: sqrt(0.051953² + 0.028144²) = 0.0591
- **Regular 95% CI**: -0.0163 ± (1.96 × 0.0349) = (-0.0847, +0.0521)
- **CUPED 95% CI**: -0.0413 ± (1.96 × 0.0591) = (-0.1571, +0.0745)

### Statistical Power Analysis
- **Regular Method**: Narrower confidence intervals indicate better precision
- **CUPED Method**: Wider confidence intervals indicate reduced precision
- **Conclusion**: Standard analysis outperformed CUPED for this test

---

## Investigation Recommendations

**Potential Issues to Explore:**
1. **Data Quality**: Check for outliers or data integrity issues in revenue metrics during 2026 period
2. **Implementation Verification**: Review CUPED formula application and theta calculation methodology
3. **Population Assumptions**: Validate "during users" definition and filtering criteria for May 2026
4. **Temporal Stability**: Examine whether pre-experiment period (May 6-19, 2026) represents stable baseline
5. **Alternative Methods**: Consider other variance reduction techniques or different covariate periods

**Specific 2026 Considerations:**
- Verify data completeness for May 2026 period
- Check for any external events or seasonality effects during test period
- Validate that user behavior patterns in 2026 support CUPED assumptions

**Next Steps:**
- Conduct diagnostic analysis on user-level revenue distributions for May 2026
- Validate query logic against CUPED theoretical framework
- Consider stratified analysis or outlier removal
- Test CUPED on different metrics or alternative time periods from 2026 data

---

*Analysis conducted on: May 28, 2026*  
*Data Period: May 6-26, 2026*  
*Analyst: Automated CUPED Analysis System*  
*Status: Requires Manual Review and Investigation*