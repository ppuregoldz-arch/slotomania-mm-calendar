# Album Stickiness Analysis - Investigation Context

## Investigation Purpose

This analysis was commissioned to understand the impact of album launches on user engagement patterns, specifically measuring whether new album content drives increased user activity frequency.

## Business Question

**Primary Question:** Do album launches increase user stickiness (active days per week per active user)?

**Secondary Questions:**
- How consistent is the stickiness impact across different albums?
- Is there a pattern in user base size changes around album launches?
- What does baseline user stickiness look like for Slotomania?

## Context & Background

### Why This Analysis Matters
- **Content ROI:** Understanding whether album development drives meaningful engagement increases
- **Feature Planning:** Informing future album launch strategies and timing
- **Engagement Benchmarking:** Establishing baseline stickiness metrics for comparison

### Analysis Approach
- **Time Periods:** Compared week before launch (days -7 to -1) vs. week after (days +1 to +7)
- **Scope:** Last 5 album launches for comprehensive view
- **Exclusions:** Day 0 (launch day) excluded to avoid launch-day noise
- **User Filtering:** Standard exclusions for employees and test users

## Key Assumptions Made

1. **One-Week Periods Sufficient:** 7-day windows capture relevant engagement patterns
2. **Launch Day Exclusion:** Day 0 excluded as potentially anomalous
3. **User Base Consistency:** Same user filtering applied to both periods
4. **Stickiness Definition:** Active days per active user per week is meaningful engagement metric

## Important Decisions During Investigation

### Metric Definition
- **Stickiness = Login Frequency / WAU**
- **Login Frequency:** Count of distinct user_id + date combinations
- **WAU:** Weekly Active Users (distinct users in 7-day period)

### Data Source Selection
- **Primary Table:** `agg.agg_sm_daily_users_stats`
- **Rationale:** Most reliable source for daily user activity
- **Alternative Considered:** `dwh.fact_sm_sessions_kafka` (rejected due to complexity)

### Album Selection Criteria
- **Source:** `sm_draft.ariel_dim_albums_info`
- **Filter:** `album_type <> 'Communal'` (focused on standard albums)
- **Scope:** Last 5 launches by launch date

## Key Findings Summary

### Main Result
- **Stickiness remains stable** around album launches (4.4-4.6 days/week)
- **No consistent increase/decrease** pattern post-launch
- **High baseline engagement** already present in user base

### Unexpected Discovery
- **WAU changes more than stickiness** - suggesting albums impact user acquisition/retention more than session frequency
- **Newer albums** (2026) show positive WAU growth, older ones show decline

## Business Impact

This analysis suggests:
1. **Albums maintain engagement** rather than boost frequency
2. **User base already highly engaged** (4.5+ days/week is excellent)
3. **Focus should shift** to user acquisition and monetization rather than frequency increases

## Next Steps & Follow-up Questions

### Immediate Actions
1. Share findings with album product team
2. Establish 4.5+ days/week as engagement benchmark
3. Consider shifting album KPIs to WAU growth and monetization

### Future Analysis Opportunities
1. **Extended time periods:** 2-4 weeks post-launch impact
2. **User segmentation:** Stickiness by tier, CZ bucket, or engagement level
3. **Cross-feature analysis:** Album interaction with other engagement features
4. **Monetization correlation:** Revenue impact vs. stickiness changes

## Technical Notes

### Query Performance
- **Memory management:** Used optimized joins to avoid memory errors
- **Execution time:** ~30 seconds for full 5-album analysis
- **Validation:** Manual calculation verified for sample album

### Data Quality
- **Completeness:** All 5 albums had full data coverage
- **Accuracy:** Standard user exclusions applied consistently
- **Timeliness:** Analysis includes data through May 23, 2026