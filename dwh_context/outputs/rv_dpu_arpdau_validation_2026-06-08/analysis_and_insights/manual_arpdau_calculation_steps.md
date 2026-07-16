# Manual ARPDAU Calculation - 2026-06-01

## Problem Statement
Your original query is showing very high ARPDAU values that seem incorrect. We need to identify the source of the discrepancy between your dashboard values and the query results.

## Key Parameters Identified
- **test_id**: 'xmXDU4lG4J'
- **start_date**: '2026-05-17' (Parameter 1)
- **end_date**: '2026-06-08' (Parameter 2) 
- **Analysis Date**: '2026-06-01' (single day)

## Dashboard Values (Expected Results)
| Group | Segment | DAU | rev | RV_rev | ARPDAU |
|-------|---------|-----|-----|--------|--------|
| Control | DPU 90-180 | 2,025 | 1,409.7 | 0 | $0.70 |
| Control | DPU 180+ | 14,373 | 1,638.9 | 0 | $0.11 |
| Test_A | DPU 90-180 | 2,042 | 1,252.1 | 21.1 | $0.62 |
| Test_A | DPU 180+ | 14,209 | 1,303.9 | 181.3 | $0.10 |

## Key Issues Identified

### 1. **Date Range Problem** 
Your original query uses:
```sql
AND date(tran_ts...) BETWEEN date(<Parameters.start date>) - interval '14 days' 
                         AND date(<Parameters.end date>) + interval '14 days'
```
This captures ~50 days of revenue (2026-05-03 to 2026-06-22) while DAU is only from 2026-06-01.

**Fix**: Use single-day filtering for payments:
```sql
AND DATE(tran_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') = '2026-06-01'::date
```

### 2. **Potential During Users Filter**
Your dashboard might filter on `is_during_users = TRUE`, which would significantly reduce the population.

## Step-by-Step Validation Approach

### Step 1: Run Corrected Query
Run the query from `dashboard_replication_query.sql` with these key corrections:
- Single-day payment filtering
- Single-day RV revenue filtering
- Correct parameter substitution

### Step 2: Check During Users Filter Impact
Run the second query in the file that filters on `is_during_users = TRUE` to see if this matches your dashboard population.

### Step 3: Manual Validation
For each segment, manually verify:
1. **User count**: Does DAU match dashboard?
2. **Revenue totals**: Do rev and RV_rev match dashboard?
3. **ARPDAU calculation**: (rev + RV_rev) / DAU

## Expected Query Results vs Dashboard

If the corrected query matches your dashboard, you should see:
- **Population reduction**: From ~18K users to ~2-14K users per segment
- **Revenue reduction**: From ~65K-68K to ~1.3-1.6K per segment  
- **ARPDAU alignment**: Values around $0.10-$0.70 instead of $3.50+

## Root Cause Summary

The high ARPDAU in your original query is likely caused by:
1. **Multi-day revenue aggregation** (50 days) with **single-day DAU** (1 day)
2. **Missing during_users filter** that your dashboard applies
3. **Parameter date range** extending far beyond the analysis period

## Next Steps

1. **Run the corrected query** to verify if results match dashboard
2. **If still no match**: Check for additional dashboard filters or data source differences
3. **If matched**: Update your original query with single-day payment filtering

## Validation Status
- **Query Logic**: ✅ Correct (segments, joins, calculations)
- **Date Filtering**: ❌ Fixed (single day vs multi-day range)
- **Population Filtering**: ❓ Needs verification (during_users filter)
- **Revenue Sources**: ✅ Correct (net_amount + revenue)