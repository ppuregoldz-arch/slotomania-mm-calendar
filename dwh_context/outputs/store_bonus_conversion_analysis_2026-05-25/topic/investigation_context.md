# Store Bonus Conversion Analysis - Investigation Context

## Investigation Purpose

This analysis was requested to measure Store Bonus engagement patterns over the past 30 days, focusing on conversion rates (distinct users collecting store bonus / DAU) and collection frequency (total events / DAU) to understand daily feature performance and user behavior patterns.

## Business Questions

**Primary Metrics Requested:**
1. **Conversion Rate**: Distinct users that collected store bonus / DAU (per promo date)
2. **Collection Frequency**: Number of store bonus collection events / DAU (per promo date)

**Time Frame**: Past 30 days (excluding today)

**Expected Outcomes**: Understanding daily variation in store bonus engagement and identifying performance patterns or potential availability issues.

## Analysis Methodology

### Data Source Identification
- **Store Bonus Events**: `dwh.fact_sm_bonus_history` with `bonus_type_id = 43`
- **DAU Calculation**: `agg.agg_sm_daily_users_stats` for daily active user counts
- **Time Alignment**: Asia/Jerusalem timezone (-14h offset) for consistent promo date calculation

### Metric Definitions
- **Conversion Rate**: `(Distinct Store Bonus Collectors / DAU) * 100`
- **Collection Frequency**: `Total Store Bonus Events / DAU`
- **Store Bonus Collectors**: Unique users who collected ≥1 store bonus per day
- **Store Bonus Events**: Total collection events (includes multiple collections by same user)

### User Exclusions Applied
Standard analytical exclusions for clean user base:
- Playtika employees (`dwh.playtika_users`)
- Test users (`dwh.sm_fact_journey_state_notifications` where `step_id = 539265`)
- Invalid user IDs (`user_id <= 0`)

## Key Findings Summary

### Performance Overview
- **30-Day Average Conversion**: 54.66% (range: 18.79% - 60.58%)
- **30-Day Average Frequency**: 0.595 collections per DAU (range: 0.188 - 0.727)
- **Daily Volume**: 230K average collectors, 250K average events
- **Multi-Collection Rate**: ~9% users collect multiple times per day

### Pattern Recognition
- **Normal Operation**: 55-58% conversion rate baseline
- **Potential Issues**: May 10 (30.71%) and May 24 (18.79%) show significant drops
- **Peak Performance**: May 11 achieved highest metrics (60.58%, 0.727)
- **Consistent Engagement**: Most days cluster around 0.61-0.63 frequency

## Business Context & Implications

### Store Bonus Feature Role
- **Daily Engagement Driver**: High conversion rates indicate important role in daily user experience
- **Retention Mechanism**: Free bonus every ~8-9 hours creates habitual return patterns
- **Economy Balancing**: 250K+ daily distributions represent significant virtual currency injection

### Performance Health Indicators
- **Healthy Range**: 55-60% conversion with 0.6+ frequency
- **Warning Signals**: <45% conversion may indicate availability or technical issues
- **Capacity Requirements**: Peak days require infrastructure for 300K+ events

### User Behavior Insights
- **High Feature Value**: Majority of DAU engages when available
- **Repeat Usage**: Some users return multiple times (respecting cooldown periods)
- **Stable Patterns**: Consistent behavior during normal operation periods

## Analysis Limitations & Considerations

### Data Assumptions
- **Feature Availability**: Conversion rate variations assumed to reflect availability rather than preference changes
- **Event Classification**: All bonus_type_id = 43 events represent legitimate Store Bonus collections
- **User Intent**: Multiple daily collections represent valid usage within cooldown restrictions

### Technical Considerations
- **Timezone Accuracy**: Jerusalem timezone conversion may introduce minor alignment variations
- **Data Completeness**: Analysis assumes complete event capture in fact tables
- **Real-time Lag**: Current day (May 25) excluded due to potential incomplete data

### Business Logic Validation
- **Cooldown Mechanics**: Store Bonus typically available every 8-9 hours, allowing 2-3 collections per day maximum
- **User Segmentation**: No tier or CZ-based filtering applied - represents all user segments equally
- **Feature Evolution**: Analysis captures current feature behavior, may not reflect historical changes

## Technical Implementation Notes

### Query Performance Optimization
- **Date Filtering**: Efficient date range filtering on both bonus history and daily user stats
- **Join Strategy**: LEFT JOIN ensures all DAU days appear even with zero store bonus activity
- **Aggregation Logic**: Separate counting of distinct users vs total events for accurate metrics

### Data Quality Validation
- **Baseline Verification**: 420K average DAU aligns with expected platform activity levels
- **Event Volume Reasonableness**: 250K daily events realistic for feature with 8-9h cooldown
- **Conversion Rate Sanity**: 54.7% average conversion indicates healthy feature engagement

### Future Enhancement Opportunities
1. **User Segmentation**: Analyze conversion by tier, CZ bucket, or engagement level
2. **Cooldown Analysis**: Measure time between collections to validate cooldown compliance
3. **Cross-Feature Correlation**: Examine store bonus usage correlation with other feature engagement
4. **Seasonal Patterns**: Extend analysis to identify weekly or monthly trends

## Operational Recommendations

### Immediate Actions
1. **Investigate Low-Performance Days**: Analyze May 10 and May 24 for potential availability issues
2. **Monitor Daily Performance**: Set up alerts for conversion rates below 45%
3. **Capacity Planning**: Ensure infrastructure supports observed peak volumes

### Strategic Considerations
1. **Feature Positioning**: High engagement suggests store bonus is well-integrated into user experience
2. **Economy Management**: Large daily bonus volumes require careful economic balancing
3. **Cross-Feature Synergy**: Leverage high store bonus engagement for other feature promotion

---

**Analysis Completed**: May 25, 2026  
**Data Coverage**: April 25 - May 24, 2026 (30 days)  
**Key Insight**: Store Bonus demonstrates excellent user engagement with clear operational impact requiring performance monitoring