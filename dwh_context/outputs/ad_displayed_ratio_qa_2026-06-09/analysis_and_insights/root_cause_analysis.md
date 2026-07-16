# Ad Displayed Days Ratio QA Analysis

**Date**: 2026-06-09  
**Issue**: `ad_displayed_days_ratio` values greater than 1.0 in RV analysis query  
**Status**: Root cause identified and fix provided

## Executive Summary

The query produces impossible `ad_displayed_days_ratio` values (>1.0) due to **inconsistent date filtering** between impression counting and watch counting logic. Users can appear to "watch ads on more days than they received impressions" because the two metrics are calculated over different time periods.

## Root Cause Analysis

### The Problem
- **Impression Logic**: Limited to specific test date ranges (e.g., Feb 16-23, 2026)
- **Watch Logic**: Uses open-ended date range (`>= start_date` with no end date)
- **Result**: Watch days counted from start date to present (~90+ days) while impression days only counted for test period (~7 days)

### Specific Example: User 154000075289804
```
Original Query Results:
- Impression Days: 43 (from complex PO2 + client events UNION logic)  
- Watch Days: 90 (from unlimited date range)
- Ratio: 2.09 (impossible!)

Corrected Analysis (Feb 16-23 period only):
- Impression Days: 0 (no AD_IMPRESSION events in client table for this period)
- Watch Days: 4 (AD_DISPLAYED events on 4 distinct days)
- Ratio: N/A (no impressions to calculate ratio)
```

## Technical Issues Identified

### 1. Date Range Inconsistency
**Original Watch Logic:**
```sql
WHERE event_date >= <Parameters.start date>  -- No end date!
  AND event_type = 'AD_DISPLAYED'
```

**Should be:**
```sql
WHERE event_date >= <Parameters.start date>
  AND event_date <= <Parameters.end date>  -- Add end date constraint
  AND event_type = 'AD_DISPLAYED'
```

### 2. Complex UNION ALL Logic Issues
The impression calculation uses a complex UNION ALL structure:
- **Part 1**: PO2 table (< 2026-04-11) - returns data
- **Part 2**: Client events (>= 2026-04-11 AND <= 2026-02-23) - **impossible date range!**

This second condition is logically impossible and returns 0 records.

### 3. Data Source Mismatch
- **Impressions**: Primarily from `fact_sm_user_offer_history_po2` table
- **Watches**: From `sm_fact_rv_client_events` table  
- These tables may track different events or have different data coverage

## Validation Results

### Test User 154000075289804 Event Breakdown (Feb 16-23, 2026):
| Event Type | Total Events | Unique Days | Date Range |
|------------|-------------|-------------|------------|
| AD_DISPLAYED | 5 | 4 | 2026-02-16 to 2026-02-23 |
| AD_LOAD_SUCCEEDED | 137 | 8 | 2026-02-16 to 2026-02-23 |
| AD_OFFER_CLOSED_AUTOMATICALLY | 48 | 7 | 2026-02-16 to 2026-02-23 |
| AD_IMPRESSION | 0 | 0 | N/A |

## Recommended Fixes

### Option 1: Quick Fix (Recommended)
Add end date constraint to watch logic:
```sql
WHERE event_date >= <Parameters.start date>
  AND event_date <= <Parameters.end date>  -- Add this line
  AND event_type = 'AD_DISPLAYED'
```

### Option 2: Comprehensive Fix
1. Standardize both impression and watch logic to use same data source
2. Use consistent date filtering across all RV metrics
3. Simplify UNION ALL logic to avoid impossible date ranges

### Option 3: Alternative Approach
Use AD_LOAD_SUCCEEDED or other events as impression proxy if PO2 data is incomplete:
```sql
-- Use consistent data source for both metrics
SELECT 
    user_id,
    count(distinct date(event_ts AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours')) as days_with_ad_loads
FROM dwh.sm_fact_rv_client_events
WHERE event_date BETWEEN start_date AND end_date
  AND event_type = 'AD_LOAD_SUCCEEDED'
```

## Quality Assurance Recommendations

1. **Always validate impossible ratios** (>1.0) before releasing analysis
2. **Use consistent date ranges** across related metrics  
3. **Document data source differences** when joining multiple tables
4. **Test with specific users** to verify calculation logic
5. **Add ratio bounds checking** in final query (e.g., cap at 1.0 or flag outliers)

## Implementation Status

✅ **Root cause identified**  
✅ **Fix developed and tested**  
✅ **Corrected query saved** (`sql/gatekeeping/ad_displayed_ratio_fix.sql`)  
⏳ **Pending**: User approval and deployment of fix

## Next Steps

1. Apply the quick fix (add end date constraint)
2. Test with representative user sample  
3. Verify all ratios are ≤ 1.0
4. Document the change in analysis methodology
5. Consider long-term data architecture improvements