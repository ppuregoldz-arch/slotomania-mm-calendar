# ARPDAU Validation Findings - June 1, 2026

## Executive Summary

**CRITICAL FINDING**: Significant discrepancy between dashboard ARPDAU values and query validation results for RV DPU segments on 2026-06-01. Dashboard shows values **3-5x higher** than validation query across all segments.

## Dashboard vs Validation Comparison

### Single Day Results (2026-06-01)

| Group | Segment | Dashboard ARPDAU | Validation ARPDAU | Difference | DAU (Validation) |
|-------|---------|------------------|-------------------|------------|------------------|
| **Control** | DPU 90-180 | $0.70 | $0.19 | **3.7x higher** | 1,253 |
| **Control** | DPU 180+ | $0.11 | $0.02 | **5.5x higher** | 12,878 |
| **Test_A** | DPU 90-180 | $0.62 | $0.14 | **4.4x higher** | 1,184 |
| **Test_A** | DPU 180+ | $0.10 | $0.03 | **3.3x higher** | 12,757 |

## Key Findings

### ✅ Query Logic Validated
- **Business logic is correct**: DPU 180+ (dormant payers) have lower ARPDAU than DPU 90-180 (recent payers)
- **Segmentation works properly**: Users are correctly classified by days since last purchase
- **No data duplication detected**: Each user appears only once per day
- **Revenue components working**: Both regular payments and RV revenue are captured

### ❌ Dashboard Discrepancy Identified
- **Systematic inflation**: All dashboard values are 3-5x higher than validation
- **Consistent pattern**: Ratio is similar across all segments, suggesting systematic issue
- **Not a logic error**: The relative relationships between segments are maintained

## Root Cause Analysis

### Most Likely Causes (In Priority Order)

1. **Different Parameter Values**
   - Dashboard using different `test_id` than 'xmXDU4lG4J'
   - Dashboard using different date range parameters (`start date`, `end date`)
   - Dashboard aggregating multiple days despite showing "6/1/2026"

2. **Dashboard Data Source Differences**
   - Different revenue field definitions (additional revenue types included)
   - Different payment safety filters or exclusion logic
   - Different user population (test group definitions)

3. **Dashboard Calculation Method**
   - Dashboard formula: `(ZN(SUM([RV_rev])) + ZN(SUM([rev]))) / SUM([DAU])`
   - Possible issue: `SUM([DAU])` aggregating incorrectly if underlying data has multiple rows per user

4. **Tableau Aggregation Issues**
   - Level of detail differences in Tableau vs SQL aggregation
   - Different granularity in underlying data source
   - Tableau-specific calculation behavior with NULL handling

## Revenue Component Analysis

### Test_A vs Control Differences
- **Test_A has RV revenue**: $178-$21 in RV revenue (as expected for RV test)
- **Control has minimal RV revenue**: $0 in RV revenue (as expected for control group)
- **Regular revenue similar**: Both groups have comparable payment revenue

### Revenue Distribution
- **DPU 180+ segments**: Lower ARPDAU due to dormant behavior (correct)
- **DPU 90-180 segments**: Higher ARPDAU due to more recent activity (correct)
- **Population sizes**: DPU 180+ ~10x larger than DPU 90-180 (typical distribution)

## Recommendations

### Immediate Actions

1. **Verify Dashboard Parameters**
   - Check exact `test_id` value used in dashboard
   - Verify `start date` and `end date` parameters
   - Confirm single-day vs multi-day aggregation

2. **Compare Data Sources**
   - Check if dashboard uses different revenue fields
   - Verify payment safety filters match query logic
   - Compare user populations between dashboard and query

3. **Test Dashboard Calculation**
   - Create test dashboard with known values to verify calculation logic
   - Check if Tableau `SUM([DAU])` behaves as expected
   - Verify NULL handling in dashboard vs query

### Investigation Query
Run the original query with the exact parameters used in the dashboard to isolate the source of discrepancy.

### Validation Status
- **Query Structure**: ✅ VALIDATED
- **Business Logic**: ✅ CORRECT
- **Dashboard Alignment**: ❌ REQUIRES INVESTIGATION

## Conclusion

The query logic and business definitions are correct. The issue lies in a **parameter, data source, or calculation method difference** between the dashboard and validation query. Priority should be placed on identifying the exact dashboard configuration causing the 3-5x inflation in ARPDAU values.