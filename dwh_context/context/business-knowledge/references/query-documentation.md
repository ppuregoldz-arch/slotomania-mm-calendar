# Slotomania Product Usage Analysis - Query Documentation

**Last Updated:** 2024-01-15  
**Version:** 1.0  
**Total Queries:** 2 (No CTEs Used)

---

## Query Overview

This document provides detailed explanations of the four strategic SQL queries designed to analyze product usage patterns, revenue impact, and user behavior in Slotomania.

### Query Architecture
- **Design Principle:** No CTEs - using subqueries and window functions only
- **Database:** Vertica 25.1.0 (optimized for column-store performance)
- **Sample Size Requirements:** Built-in minimum thresholds for statistical validity
- **Time Range:** 90-day lookback with 30-day vs 90-day comparison

---

## Query 1: Product Usage Analysis

### File Location
`queries/2024-01-15_product_usage_analysis.sql`

### Purpose & Objectives
Analyze user engagement and product adoption patterns to identify changes between recent (30-day) and extended (90-day) time periods.

### Core Business Questions Answered
1. Which products are gaining or losing user adoption?
2. How has user engagement depth changed over time?
3. Are there tier-specific usage pattern shifts?
4. What's the penetration rate of different products?

### Query Structure Analysis

#### 1. Time Period Classification
```sql
CASE 
    WHEN event_date >= CURRENT_DATE - 30 THEN '30_day_recent'
    WHEN event_date >= CURRENT_DATE - 90 THEN '90_day_extended'
    ELSE 'older'
END AS time_period
```

**Logic:** Creates temporal segments for comparison analysis
**Business Value:** Enables trend identification between short and long-term periods

#### 2. User Penetration Calculation
```sql
COUNT(DISTINCT user_id) * 100.0 / (
    SELECT COUNT(DISTINCT user_id) 
    FROM user_activity_table 
    WHERE event_date >= CURRENT_DATE - 90
) as user_penetration_pct
```

**Logic:** Calculates what percentage of total DAU uses each product
**Business Value:** Measures market penetration and adoption rates

#### 3. Engagement Metrics Framework
```sql
AVG(session_duration_seconds) as avg_session_duration,
COUNT(*) * 1.0 / COUNT(DISTINCT user_id) as interactions_per_user,
AVG(interactions_per_session) as avg_interactions_per_session
```

**Logic:** Multi-dimensional engagement measurement
**Business Value:** Quantifies engagement depth and user behavior intensity

#### 4. User Segmentation Logic
```sql
CASE 
    WHEN up.user_level BETWEEN 1 AND 50 THEN '1-50_beginner'
    WHEN up.user_level BETWEEN 51 AND 200 THEN '51-200_intermediate'
    WHEN up.user_level BETWEEN 201 AND 500 THEN '201-500_advanced'
    ELSE '500+_expert'
END AS user_level_bucket
```

**Logic:** Groups users by experience level for segmented analysis
**Business Value:** Identifies tier-specific behavior patterns

#### 5. Data Quality Filters
```sql
WHERE pue.event_date >= CURRENT_DATE - 90
    AND pue.interaction_type IN ('play', 'purchase', 'bonus_collection', 'feature_usage')
    AND up.user_status = 'active'
HAVING COUNT(DISTINCT user_id) >= 100
```

**Logic:** Ensures data quality and statistical significance
**Business Value:** Maintains analytical reliability and excludes noise

### Expected Output Structure
| Column | Description | Business Use |
|--------|-------------|--------------|
| time_period | 30_day_recent / 90_day_extended | Temporal comparison |
| product_name | Product identifier | Product performance tracking |
| unique_users | User count by segment | Adoption measurement |
| user_penetration_pct | Penetration rate | Market share analysis |
| avg_session_duration | Engagement depth | Quality of interaction |
| interactions_per_user | Usage intensity | User behavior pattern |

---

## Query 2: Revenue Metrics Analysis

### File Location
`queries/2024-01-15_revenue_metrics_analysis.sql`

### Purpose & Objectives
Quantify revenue impact of usage pattern changes and assess monetization effectiveness trends across time periods and user segments.

### Core Business Questions Answered
1. How has ARPPU changed between time periods?
2. Are players getting better or worse value for money?
3. Which user tiers drive the most revenue?
4. How effective are personal offers vs regular pricing?

### Query Structure Analysis

#### 1. ARPPU Calculation Framework
```sql
SUM(pt.usd_amount) / COUNT(DISTINCT pt.user_id) as arppu_usd,
COUNT(DISTINCT pt.transaction_id) as total_transactions,
AVG(pt.usd_amount) as avg_transaction_size_usd
```

**Logic:** Multi-faceted revenue measurement per paying user
**Business Value:** Core monetization effectiveness metric

#### 2. Value for Money (VFM) Analysis
```sql
AVG(pt.coins_purchased / pt.usd_amount) as avg_coins_per_dollar,
AVG(pt.coins_purchased / pt.usd_amount) / (
    SELECT AVG(coins_purchased / usd_amount) 
    FROM payment_transactions_table 
    WHERE payment_date >= CURRENT_DATE - 365
) as vfm_vs_yearly_avg
```

**Logic:** Measures value proposition trends against historical baseline
**Business Value:** Tracks player value perception and pricing effectiveness

#### 3. Revenue Distribution Analysis
```sql
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pt.usd_amount) as median_transaction_usd,
PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY pt.usd_amount) as p90_transaction_usd
```

**Logic:** Statistical distribution analysis of transaction sizes
**Business Value:** Identifies spending patterns and whale behavior

#### 4. Promotion Impact Assessment
```sql
SUM(CASE WHEN pt.promotion_type = 'personal_offer' THEN pt.usd_amount ELSE 0 END) as po_revenue_usd,
SUM(CASE WHEN pt.promotion_type = 'personal_offer' THEN pt.usd_amount ELSE 0 END) * 100.0 / SUM(pt.usd_amount) as po_revenue_share_pct
```

**Logic:** Measures personal offer effectiveness and revenue contribution
**Business Value:** Evaluates personalization strategy impact

#### 5. User Lifecycle Metrics
```sql
SUM(CASE WHEN up.payment_history = 'first_time' THEN pt.usd_amount ELSE 0 END) as ftd_revenue_usd,
COUNT(DISTINCT CASE WHEN up.payment_history = 'first_time' THEN pt.user_id END) as ftd_count
```

**Logic:** Tracks first-time vs returning payer contribution
**Business Value:** Measures user lifecycle monetization effectiveness

#### 6. Retention Impact Analysis
```sql
COUNT(DISTINCT CASE WHEN pt.days_since_last_payment <= 7 THEN pt.user_id END) as frequent_payers,
COUNT(DISTINCT CASE WHEN pt.days_since_last_payment <= 7 THEN pt.user_id END) * 100.0 / COUNT(DISTINCT pt.user_id) as frequent_payer_rate_pct
```

**Logic:** Identifies high-frequency payment behavior
**Business Value:** Measures payment behavior sustainability

### Expected Output Structure
| Column | Description | Business Use |
|--------|-------------|--------------|
| time_period | 30_day_recent / 90_day_extended | Revenue trend analysis |
| arppu_usd | Revenue per paying user | Monetization efficiency |
| avg_coins_per_dollar | Value for money ratio | Player value perception |
| vfm_vs_yearly_avg | VFM trend indicator | Pricing strategy effectiveness |
| po_revenue_share_pct | Personal offer impact | Personalization ROI |
| frequent_payer_rate_pct | Payment frequency | User loyalty indicator |

---

## Query 3: User Behavior Analysis

### File Location
`queries/2024-01-15_user_behavior_analysis.sql`

### Purpose & Objectives
Analyze user engagement patterns and behavioral characteristics from daily user statistics to understand player types, session patterns, and overall game engagement quality.

### Core Business Questions Answered
1. What are the key behavioral differences between time periods?
2. How do session patterns vary by user tier and level?
3. What defines heavy vs casual vs light users?
4. Are weekend vs weekday behaviors significantly different?

### Key SQL Components

#### 1. Time Period Segmentation
**Logic:** Same 30-day vs 90-day comparison framework
**Business Value:** Identifies recent behavioral shifts

#### 2. User Type Classification
```sql
AVG(CASE 
    WHEN sessions_count >= 5 AND session_length_minutes >= 30 THEN 1 
    ELSE 0 
END) as heavy_user_rate
```
**Logic:** Defines user engagement levels based on session frequency and duration
**Business Value:** Enables targeted user retention strategies

#### 3. Behavioral Pattern Analysis
**Logic:** Calculates spins per session, bet per spin, and engagement consistency
**Business Value:** Identifies optimal game flow and monetization opportunities

### Expected Output Structure
| Column | Description | Business Use |
|--------|-------------|--------------|
| time_period | 30_day_recent / 90_day_extended | Behavioral trend analysis |
| tier_group | User tier grouping | Segment-specific patterns |
| avg_daily_sessions | Session frequency | Engagement measurement |
| avg_spins_per_session | Game intensity | Player involvement |
| heavy_user_rate | High-engagement percentage | Retention targeting |
| weekend_vs_weekday | Temporal behavior patterns | Content scheduling |

---

## Query 4: User Retention & Churn Analysis

### File Location
`queries/2024-01-15_user_retention_analysis.sql`

### Purpose & Objectives
Analyze user retention patterns, churn risk indicators, and player lifecycle progression to identify at-risk segments and optimization opportunities.

### Core Business Questions Answered
1. Which user segments have the highest retention rates?
2. What are the early warning signs of churn?
3. How does player maturity affect retention patterns?
4. Are there specific days or patterns that predict user drop-off?

### Key SQL Components

#### 1. Retention Rate Calculation
```sql
COUNT(DISTINCT CASE WHEN sessions_count > 0 THEN date_key END) * 1.0 / 
COUNT(DISTINCT date_key) as daily_retention_rate
```
**Logic:** Measures percentage of tracked days with user activity
**Business Value:** Core retention metric for user lifecycle management

#### 2. Churn Risk Indicators
**Logic:** Uses window functions to detect consecutive activity and drop-off patterns
**Business Value:** Enables proactive churn prevention

#### 3. Cohort Analysis by Player Maturity
**Logic:** Segments users by experience level (using user_level as proxy for tenure)
**Business Value:** Identifies retention patterns by player lifecycle stage

### Expected Output Structure
| Column | Description | Business Use |
|--------|-------------|--------------|
| player_maturity | Experience-based cohorts | Lifecycle optimization |
| daily_retention_rate | Activity consistency | Retention measurement |
| consecutive_day_rate | Engagement momentum | Habit formation tracking |
| drop_off_rate | Churn risk indicator | Risk identification |
| progression_engagement_rate | Growth-focused retention | Feature effectiveness |

---

## Cross-Query Analysis Framework

### Comparative Analysis Approach
1. **Usage vs Revenue Correlation:** Compare engagement changes with revenue impact
2. **Segment Performance:** Analyze tier-specific patterns across both queries
3. **Product Effectiveness:** Cross-reference product usage with monetization success
4. **Time Trend Validation:** Ensure consistency in temporal patterns

### Key Correlation Metrics
- **Engagement-Revenue Relationship:** Higher usage → Higher ARPPU?
- **VFM-Adoption Relationship:** Better value → Higher adoption?
- **Tier Behavior Consistency:** Similar patterns across usage and revenue?

---

## Query Performance Optimization

### Vertica-Specific Optimizations
1. **Column Selection:** Only necessary columns to minimize I/O
2. **Filter Pushdown:** WHERE clauses applied early in execution
3. **Join Strategy:** Inner joins for performance, appropriate join order
4. **Aggregation Efficiency:** Grouped aggregations for column-store benefits

### Performance Expectations
- **Query 1 Runtime:** 3-5 minutes (product usage analysis)
- **Query 2 Runtime:** 4-6 minutes (revenue metrics with joins)
- **Query 3 Runtime:** 5-8 minutes (behavioral analysis with complex aggregations)
- **Query 4 Runtime:** 8-12 minutes (retention analysis with window functions)
- **Resource Usage:** Moderate to high memory consumption due to complex aggregations and window functions

---

## Data Quality & Validation

### Built-in Validations
1. **Sample Size Filters:** Minimum user counts (100 for usage, 50 for revenue)
2. **Data Freshness:** 90-day maximum lookback
3. **Status Filters:** Active users and completed transactions only
4. **Amount Validation:** Positive USD amounts only

### Quality Checkpoints
- [ ] Sample sizes meet statistical requirements
- [ ] Time period distributions are reasonable
- [ ] ARPPU values fall within expected ranges
- [ ] User penetration percentages are logical

---

## Error Handling & Troubleshooting

### Common Issues
1. **Zero Division Errors:** Handled with COUNT filters in HAVING clauses
2. **NULL Values:** Managed through careful join strategies and WHERE clauses
3. **Data Type Mismatches:** Explicit casting for calculations
4. **Performance Issues:** Optimized for Vertica column-store architecture

### Debugging Approaches
- **Sample Data Testing:** Use LIMIT clauses for query validation
- **Intermediate Results:** Break complex calculations into steps
- **Statistical Validation:** Check results against known benchmarks

---

## Output Analysis Guidelines

### Statistical Significance
- **Minimum Sample Sizes:** Enforced in query logic
- **Confidence Intervals:** 95% confidence level recommended
- **Trend Validation:** Compare multiple metrics for consistency

### Business Interpretation
- **Percentage Changes:** Material (>10%), Significant (>20%), Major (>50%)
- **ARPPU Trends:** Consider seasonality and promotional calendars
- **VFM Changes:** Validate against known pricing changes

---

## Maintenance & Updates

### Version Control
- **File Naming:** Date-stamped for historical tracking
- **Query Comments:** Detailed inline documentation
- **Change Log:** Track modifications and reasons

### Future Enhancements
- **Additional Metrics:** Can be added through SELECT clause modifications
- **Extended Time Periods:** Adjust date filters for longer analysis
- **New Segmentations:** Add dimensions through GROUP BY modifications

---

## Change Log
- **2024-01-15:** Initial query documentation created (Query 1 & 2)
- **2024-01-15:** Added Query 3 (User Behavior Analysis) and Query 4 (User Retention Analysis)
- **2024-01-15:** Updated performance expectations for all four queries
- **2024-01-15:** Added comprehensive documentation for behavioral and retention analysis

**Next Review:** 2024-01-20 