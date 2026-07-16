# SM Complexity Assessment Examples

This document provides examples of SM query complexity assessment with validation requirements.

---

## 🟢 GREEN - Simple Queries

### Example 1: Daily Revenue Query
**Query Complexity**: 🟢 GREEN  
**Request Complexity**: 📝 SIMPLE  
**Combined Assessment**: 🟢 SIMPLE

**Query:**
```sql
SELECT 
    calc_date,
    SUM(daily_Net_revenue) as daily_revenue,
    COUNT(DISTINCT user_id) as dau
FROM agg.agg_sm_daily_users_stats
WHERE calc_date >= CURRENT_DATE - 30
GROUP BY calc_date
ORDER BY calc_date;
```

**Characteristics:**
- Single table query
- Simple aggregations (SUM, COUNT)
- Standard KPIs (revenue, DAU)
- No complex joins
- Pre-calculated metrics

**Validation Requirements:**
- 1-3 validation users
- Basic verification against raw data
- 1-2 hours validation time

---

## 🟡 YELLOW - Moderate Queries

### Example 2: Revenue by CZ Deluxe Segment
**Query Complexity**: 🟡 YELLOW  
**Request Complexity**: 📊 MODERATE  
**Combined Assessment**: 🟡 MODERATE

**Query:**
```sql
SELECT 
    CASE
        WHEN b.cz_deluxe_weekly_update >= 0 AND b.cz_deluxe_weekly_update < 5 THEN '0-5'
        WHEN b.cz_deluxe_weekly_update >= 5 AND b.cz_deluxe_weekly_update < 10 THEN '5-10'
        -- Additional segments
        ELSE 'Other'
    END as cz_segment,
    COUNT(DISTINCT a.user_id) as users,
    SUM(a.daily_Net_revenue) as total_revenue,
    AVG(a.daily_Net_revenue) as avg_revenue_per_user
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN dwh.sm_user_profile_datamining_snapshot b
    ON a.user_id = b.user_id
    AND a.calc_date = DATE(b.snapshot_insert_ts)
WHERE a.calc_date >= CURRENT_DATE - 30
GROUP BY cz_segment;
```

**Characteristics:**
- Multi-table join (2 tables)
- User segmentation analysis
- Moderate aggregations with grouping
- Cross-table validation required

**Validation Requirements:**
- 3-5 validation users
- Cross-table verification
- 0.5-1 day validation time

---

## 🔴 RED - Complex Queries

### Example 3: Churn Analysis with Cohorts
**Query Complexity**: 🔴 RED  
**Request Complexity**: 🔍 COMPLEX  
**Combined Assessment**: 🔴 COMPLEX

**Query:**
```sql
WITH user_cohorts AS (
    SELECT 
        user_id,
        MIN(calc_date) as first_date,
        DATE_TRUNC('month', MIN(calc_date)) as cohort_month
    FROM agg.agg_sm_daily_users_stats
    GROUP BY user_id
),
cohort_retention AS (
    SELECT 
        c.cohort_month,
        COUNT(DISTINCT c.user_id) as cohort_size,
        COUNT(DISTINCT CASE WHEN a.calc_date >= c.first_date + INTERVAL '1 day' THEN a.user_id END) as day_1_retained,
        COUNT(DISTINCT CASE WHEN a.calc_date >= c.first_date + INTERVAL '7 days' THEN a.user_id END) as day_7_retained,
        COUNT(DISTINCT CASE WHEN a.calc_date >= c.first_date + INTERVAL '30 days' THEN a.user_id END) as day_30_retained
    FROM user_cohorts c
    LEFT JOIN agg.agg_sm_daily_users_stats a
        ON c.user_id = a.user_id
    GROUP BY c.cohort_month
)
SELECT * FROM cohort_retention
ORDER BY cohort_month;
```

**Characteristics:**
- Multiple CTEs
- Complex cohort logic
- Window functions
- Cross-system validation required
- Two-step aggregation required

**Validation Requirements:**
- 5-10 validation users
- Comprehensive validation
- 1-3 days validation time

---

## ⚫ BLACK - Advanced Queries

### Example 4: Advanced LTV Prediction Model
**Query Complexity**: ⚫ BLACK  
**Request Complexity**: 🚀 ADVANCED  
**Combined Assessment**: ⚫ ADVANCED

**Query:**
```sql
WITH user_features AS (
    SELECT 
        user_id,
        AVG(spins) as avg_spins,
        AVG(daily_Net_revenue) as avg_revenue,
        COUNT(DISTINCT calc_date) as active_days,
        MAX(balance_end_day) as max_balance,
        SUM(CASE WHEN daily_Net_revenue > 0 THEN 1 ELSE 0 END) as paying_days
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date >= CURRENT_DATE - 90
    GROUP BY user_id
),
user_behavior AS (
    SELECT 
        uf.user_id,
        uf.avg_spins,
        uf.avg_revenue,
        uf.active_days,
        uf.max_balance,
        uf.paying_days,
        CASE 
            WHEN uf.avg_spins > 1000 AND uf.avg_revenue > 10 THEN 'High_Value'
            WHEN uf.avg_spins > 500 AND uf.avg_revenue > 1 THEN 'Medium_Value'
            ELSE 'Low_Value'
        END as user_segment
    FROM user_features uf
)
SELECT 
    user_segment,
    COUNT(*) as user_count,
    AVG(avg_revenue) as avg_revenue,
    AVG(active_days) as avg_active_days
FROM user_behavior
GROUP BY user_segment;
```

**Characteristics:**
- Multiple CTEs with complex logic
- Feature engineering
- Predictive modeling elements
- Expert-level analysis
- Complex two-step aggregations

**Validation Requirements:**
- 10+ validation users
- Expert validation
- 3+ days validation time

---

## Complexity Assessment Guidelines

### Query Complexity Factors
- **Data Volume**: Rows processed, table sizes
- **Join Complexity**: Number and type of joins
- **Calculation Complexity**: Aggregations, window functions, CTEs
- **Business Logic**: Custom calculations, segmentation logic
- **Aggregation Methodology**: Two-step aggregation requirements

### Request Complexity Factors
- **Token Usage**: Length and detail of request
- **Metrics Count**: Number of metrics requested
- **Segmentation**: Number of dimensions/segments
- **Timeframe**: Period length and granularity
- **Business Logic**: Complexity of business questions

### Combined Assessment Rules
- **🟢 SIMPLE**: Green query + Simple request
- **🟡 MODERATE**: Yellow query + Moderate request OR Green query + Complex request
- **🔴 COMPLEX**: Red query + Any request OR Yellow query + Advanced request
- **⚫ ADVANCED**: Black query + Any request OR Red query + Advanced request

These examples demonstrate the complexity assessment framework for SM data analysis.

