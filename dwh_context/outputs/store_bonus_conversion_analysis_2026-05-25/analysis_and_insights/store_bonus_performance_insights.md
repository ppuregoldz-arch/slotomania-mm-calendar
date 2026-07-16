# Store Bonus Conversion Analysis - Performance Insights

**Analysis Period:** April 25 - May 24, 2026 (30 days)  
**Analysis Date:** May 25, 2026

## Executive Summary

Store Bonus demonstrates strong user engagement with **54.7% average conversion rate** and **0.595 collections per DAU**, but shows significant daily variation indicating potential feature availability cycles or promotional periods.

## Key Performance Metrics - 30-Day Summary

| Metric | Average | Minimum | Maximum | Range |
|--------|---------|---------|---------|-------|
| **DAU** | 419,937 | 414,020 | 427,192 | 13,172 |
| **Store Bonus Collectors** | 229,652 | 77,774 | 255,394 | 177,620 |
| **Store Bonus Events** | 249,827 | 77,774 | 306,326 | 228,552 |
| **Conversion Rate** | **54.66%** | **18.79%** | **60.58%** | **41.79%** |
| **Collection Frequency** | **0.595** | **0.188** | **0.727** | **0.539** |

## Daily Performance Patterns

### High Performing Days (55%+ Conversion)
- **Peak Performance**: May 11 (60.58% conversion, 0.727 frequency)
- **Consistent High Performers**: May 12-23 (55-58% conversion range)
- **Strong Volume**: 228K-255K daily collectors during peak periods

### Lower Performing Days
- **Minimum Performance**: May 24 (18.79% conversion, 0.188 frequency)
- **Secondary Low**: May 10 (30.71% conversion, 0.334 frequency)
- **Reduced Volume**: 77K-128K collectors on low-performance days

### Collection Behavior Analysis
- **Multiple Collections**: Users collect 1.09 store bonuses per collector on average
- **Peak Multi-Collection**: May 11 shows highest frequency (0.727 vs 0.606 baseline)
- **Consistency Pattern**: Most days show 0.61-0.63 frequency (±8% variation)

## Key Insights

### 1. **Feature Availability Patterns**
- **Strong Baseline**: ~55-58% conversion when fully available
- **Potential Downtime**: May 10 and May 24 suggest limited availability periods
- **Consistent Engagement**: When available, users show reliable engagement patterns

### 2. **User Engagement Quality**
- **High Penetration**: Over half of DAU engages with Store Bonus daily
- **Multiple Usage**: ~9% of collectors return for additional collections same day
- **Stable Behavior**: Conversion rates cluster around 55-58% during normal operation

### 3. **Operational Insights**
- **Daily Volume**: 230K+ collectors represents significant engagement infrastructure
- **Usage Frequency**: 0.6 collections per DAU indicates healthy feature utilization
- **Scalability**: Feature handles 250K+ daily events consistently

## Business Implications

### User Experience Impact
- **High Feature Value**: 55%+ daily conversion indicates strong user appreciation
- **Reliable Engagement**: Consistent usage patterns suggest integrated user behavior
- **Retention Driver**: Daily collection creates habitual engagement touchpoints

### Revenue & Monetization Context
- **Engagement Foundation**: High store bonus usage may correlate with increased session time
- **Economy Health**: 250K+ daily bonus distributions require careful economic balancing
- **Cross-Feature Synergy**: Store bonus may support other monetization features

### Feature Performance Health
- **Normal Operation**: 55-60% conversion represents healthy feature performance
- **Availability Monitoring**: Significant drops (below 35%) may indicate technical issues
- **Capacity Planning**: Peak days (306K events) set infrastructure requirements

## Recommendations

### 1. **Performance Monitoring**
- **Alert Thresholds**: Monitor for conversion drops below 45% as potential availability issues
- **Daily Tracking**: Track both conversion rate and frequency for complete picture
- **Peak Capacity**: Ensure infrastructure supports 300K+ daily events

### 2. **Feature Optimization**
- **Availability Maximization**: Investigate May 10 and May 24 patterns to prevent downtime
- **Multi-Collection Analysis**: Understand drivers of higher frequency days (like May 11)
- **User Journey Integration**: Leverage high engagement for cross-feature promotion

### 3. **Business Intelligence Integration**
- **Retention Correlation**: Analyze store bonus users' long-term engagement patterns
- **Revenue Attribution**: Measure indirect monetization impact through increased session activity
- **Feature Sequencing**: Optimize store bonus timing with other promotional features

## Data Quality & Methodology Notes

### Data Sources & Validation
- **Store Bonus Events**: `dwh.fact_sm_bonus_history` with `bonus_type_id = 43`
- **DAU Calculation**: `agg.agg_sm_daily_users_stats` with standard exclusions
- **Time Zone**: Asia/Jerusalem (-14h offset) for consistent promo date alignment
- **User Exclusions**: Playtika employees and test users (step_id = 539265) excluded

### Analysis Assumptions
- **Feature Identification**: All bonus_type_id = 43 events represent Store Bonus collections
- **Daily Availability**: Conversion rate variations reflect feature availability rather than user preference changes
- **User Behavior**: Multiple daily collections by same user represent legitimate usage patterns

---

**Key Finding**: Store Bonus maintains excellent 55%+ baseline conversion when available, with significant operational impact requiring continued performance monitoring and infrastructure support.