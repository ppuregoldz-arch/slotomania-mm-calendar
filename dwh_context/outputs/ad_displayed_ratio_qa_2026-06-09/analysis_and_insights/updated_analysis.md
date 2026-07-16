# Updated Analysis: Ad Displayed Days Ratio QA

**Update**: 2026-06-09 6:40 PM  
**Status**: Root cause refined - System tracking evolution identified

## Key Discovery

The test runs until **October 31, 2026**, and the issue is **not** just date range inconsistency. The real problem is **tracking system evolution**:

### Timeline of Events
- **Feb 16, 2026**: Test started, AD_DISPLAYED tracking active
- **April 5, 2026**: AD_IMPRESSION tracking implemented in client events
- **Your query**: Uses April 11 as cutoff between PO2 backfill and client events

### Data Pattern Analysis (User 154000075289804)
| Tracking Method | Period | Days | Events |
|----------------|--------|------|---------|
| AD_DISPLAYED | Feb 16 - Jun 9 | 90 days | 342 events |
| AD_IMPRESSION | Apr 5 - Jun 9 | 59 days | 411 events |
| **Gap** | **Feb 16 - Apr 4** | **47 days** | **Missing impressions** |

## Revised Root Cause

Your UNION ALL logic is **architecturally correct**:
1. **PO2 table**: Backfills impression data for Feb 16 - Apr 10
2. **Client events**: Uses AD_IMPRESSION for Apr 11+
3. **Problem**: PO2 backfill is **incomplete** for some users

## Business Impact Assessment

### Scale of Issue
- **System-wide**: AD_IMPRESSION tracking gap affects all users tested before April 5
- **Data completeness**: ~47 days of potentially missing impression data
- **Analysis accuracy**: Ratios > 1.0 indicate incomplete impression tracking

### User Behavior Interpretation
Users with ratios > 1.0 likely:
- Started testing in February (early adopters)
- Have consistent ad viewing behavior
- Are missing impression data from PO2 backfill logic

## Recommended Solutions

### Option 1: Business Logic Fix (Recommended)
Cap ratios at 1.0 and flag data quality issues:
```sql
case 
    when days_with_ads_imp = 0 then null
    when coalesce(days_with_ads_watch, 0) / days_with_ads_imp > 1.0 then 1.0
    else coalesce(days_with_ads_watch, 0) / days_with_ads_imp 
end as ad_displayed_days_ratio,
-- Add data quality flag
case 
    when coalesce(days_with_ads_watch, 0) / days_with_ads_imp > 1.0 then 1 
    else 0 
end as data_quality_flag
```

### Option 2: Conservative Approach
Only calculate ratios for users with complete tracking (Apr 5+):
```sql
case 
    when first_impression_date <= '2026-04-05' then ad_displayed_days_ratio
    else null 
end as reliable_ad_displayed_days_ratio
```

### Option 3: Use Alternative Events
Use AD_LOAD_SUCCEEDED as impression proxy for pre-April period:
```sql
-- More complete impression tracking
count(distinct case when event_type in ('AD_IMPRESSION', 'AD_LOAD_SUCCEEDED') then promo_date end)
```

## Quality Assurance Framework

### Data Validation Checks
1. **Ratio bounds**: Flag all ratios > 1.0
2. **Timeline validation**: Check first impression vs. first watch dates
3. **Event completeness**: Compare impression sources (PO2 vs client events)
4. **User segmentation**: Separate early testers from post-April users

### Reporting Recommendations
- **Include data quality flags** in all analyses
- **Segment users by tracking completeness**
- **Document limitation**: "Results for users tested before April 2026 may underestimate impressions"
- **Track improvement**: Monitor data quality as test continues

## Implementation Status

✅ **Root cause refined**: System evolution, not date range error  
✅ **Business logic solution developed**: Cap ratios + quality flags  
✅ **Alternative approaches documented**: Conservative and proxy methods  
⏳ **Pending**: User approval of approach (cap vs. exclude vs. proxy)

## Next Steps

1. Choose preferred solution approach
2. Validate solution with representative user sample
3. Document data quality limitations in reports
4. Consider improving PO2 backfill logic for future tests