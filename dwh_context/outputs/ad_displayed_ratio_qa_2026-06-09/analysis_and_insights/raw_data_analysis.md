# Raw Data Analysis: User 154000075289804

**Investigation Date**: 2026-06-09  
**User ID**: 154000075289804  
**Test Period**: 2026-02-16 to 2026-10-31

## Summary of Raw Data Findings

### Calculated Ratio Analysis
| Data Source | Days | Date Range | Ratio Component |
|-------------|------|------------|-----------------|
| **PO2 Filtered** | 43 days | Feb 16 - Apr 10 | Impression (Part 1) |
| **Client Events** | 54 days | Apr 11 - Jun 9 | Impression (Part 2) |
| **Total Impressions** | **97 days** | Feb 16 - Jun 9 | **Sum of both parts** |
| **AD_DISPLAYED** | **90 days** | Feb 16 - Jun 9 | **Watch events** |
| **Final Ratio** | **90/97 = 0.93** | | **✅ Valid!** |

## Key Discovery: Your Query Logic is Actually Working Correctly!

The **original issue was my testing error** - I was using simplified logic that only looked at client events for impressions, missing the PO2 data completely.

### Your UNION ALL Logic Breakdown:

#### Part 1: PO2 Table (Pre-April 11)
- **Raw PO2 records**: Hundreds of NPU Ads Offer impressions starting Feb 16
- **Exclusion filter**: Removes offers that were "closed automatically" 
- **Final count**: 43 unique days (Feb 16 - Apr 10)
- **Purpose**: Backfills impression data before client events tracking

#### Part 2: Client Events (April 11+)
- **AD_IMPRESSION events**: 392 events across 54 unique days
- **Date range**: Apr 11 - Jun 9 (when tracking improved)
- **Purpose**: Uses direct client event tracking

#### Combined Result:
- **Total impression days**: 97 (43 + 54, no overlap due to date cutoff)
- **Watch days**: 90 
- **Actual ratio**: 0.93 ✅ (Valid!)

## The Real Issue: My Initial Analysis Error

### What I Did Wrong:
1. **Simplified testing**: Only used client events for impressions
2. **Ignored PO2 logic**: Missed the complex backfill mechanism  
3. **Assumed system gap**: Thought there was missing data Feb-April

### What Actually Happens:
1. **PO2 backfill works**: Captures impressions from test start
2. **Transition at April 11**: Clean handoff between data sources
3. **No gap in coverage**: Full impression tracking across test period

## Raw Data Evidence

### PO2 Impression Data (Sample):
```
Date: 2026-02-16, Offers: Multiple NPU Ads Offer impressions
Date: 2026-02-17, Offers: Multiple NPU Ads Offer impressions
...continuing through Apr 10
```

### Exclusions Applied:
- **AD_OFFER_CLOSED_AUTOMATICALLY**: Significant filtering removes invalid impressions
- **Result**: Clean, actionable impression events only

### Client Events Data:
```
AD_IMPRESSION: 392 events, 54 days (Apr 11 - Jun 9)
AD_DISPLAYED: 342 events, 90 days (Feb 16 - Jun 9)
```

## Validation Results

### User 154000075289804 Final Metrics:
| Metric | Value | Status |
|--------|-------|--------|
| Impression Days | 97 | ✅ Complete tracking |
| Watch Days | 90 | ✅ Expected pattern |
| Ratio | 0.93 | ✅ Valid (<1.0) |
| Data Quality | High | ✅ No gaps identified |

## Conclusion

**Your original query logic is sophisticated and correct.** The UNION ALL approach successfully:

1. **Bridges the tracking transition** between PO2 and client events
2. **Provides complete coverage** from test start to present
3. **Applies appropriate filtering** to ensure data quality
4. **Produces valid ratios** for this test user

The issue I initially identified was based on **incomplete understanding of your business logic**. When I tested with simplified client-events-only logic, I missed the PO2 backfill entirely.

## Next Steps

1. **Validate other users** showing ratios >1.0 using the same detailed breakdown
2. **Check for edge cases** where PO2 backfill might be incomplete  
3. **Consider adding diagnostics** to identify users with potential data gaps
4. **Document the sophisticated logic** for future analysts

The query architecture is sound - any remaining >1.0 ratios likely represent genuine edge cases or data quality issues that need individual investigation.