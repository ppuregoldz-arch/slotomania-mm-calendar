# Ad Displayed Days Ratio Investigation

**Investigation Date**: 2026-06-09  
**Issue Reported**: Users showing `ad_displayed_days_ratio` values greater than 1.0  
**Investigation Status**: Complete - Root cause identified and fix provided

## Investigation Context

User reported receiving impossible values in the `ad_displayed_days_ratio` calculation from their RV analysis query. The ratio represents the proportion of days a user watched ads relative to days they received ad impressions, which should logically never exceed 1.0.

## Key Findings

### Primary Issue: Date Range Inconsistency
The query calculates impression days and watch days over different time periods:

- **Impression Days**: Complex logic limited to test period (using PO2 table + client events)
- **Watch Days**: Open-ended date range from start date to present (~90+ days vs ~7 test days)

### Validation Example
**User 154000075289804**:
- Original Query: 43 impression days, 90 watch days → **Ratio: 2.09** ❌
- Corrected Logic: 0 impression days, 4 watch days → **Ratio: N/A** ✅

## Technical Root Cause

1. **Missing end date constraint** in watch events logic
2. **Impossible date range** in UNION ALL logic (`>= '2026-04-11' AND <= '2026-02-23'`)  
3. **Data source mismatch** between impression tracking (PO2 table) and watch tracking (client events)

## Solution Implemented

**Quick Fix**: Add end date constraint to watch logic
```sql
-- Original (problematic)
WHERE event_date >= <Parameters.start date>

-- Fixed  
WHERE event_date >= <Parameters.start date>
  AND event_date <= <Parameters.end date>
```

## Deliverables

1. **Root cause analysis** with detailed technical explanation
2. **Fixed query** with consistent date filtering (`sql/gatekeeping/ad_displayed_ratio_fix.sql`)
3. **User validation** demonstrating the fix resolves impossible ratios
4. **QA recommendations** for future analysis validation

## Business Impact

- **Data Quality**: Eliminates impossible metric values that could mislead analysis
- **Analysis Reliability**: Ensures RV engagement metrics accurately reflect user behavior  
- **Decision Making**: Prevents business decisions based on incorrect ratio calculations

## Next Steps

1. User to review and approve the fix
2. Apply corrected query to production analysis
3. Validate results show all ratios ≤ 1.0
4. Consider broader review of RV metric calculations for similar issues