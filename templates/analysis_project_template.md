# SM Analysis Project Template

## Project Overview

### Project Information
- **Project Name**: [SM Analysis Project Name]
- **Stakeholder**: [Primary stakeholder/role]
- **Business Objective**: [Clear statement of business goal]
- **Analysis Type**: [Revenue/Engagement/Economy/Churn/Product/Bonus/Virtual Currency]
- **Complexity Level**: [🟢 GREEN/🟡 YELLOW/🔴 RED/⚫ BLACK]
- **Expected Timeline**: [Estimated completion time]

### Business Context
**Why this analysis matters:**
[Explain the business impact and strategic importance of this analysis]

**Key Questions to Answer:**
1. [Primary research question]
2. [Secondary research question]
3. [Tertiary research question]

## Analysis Plan

### Phase 1: Problem Definition

#### Request Assessment
| Criterion | Score | Notes |
|-----------|-------|-------|
| **Clarity** | [1-5] | [Assessment notes] |
| **Scope** | [1-5] | [Assessment notes] |
| **Complexity** | [1-5] | [Assessment notes] |
| **Actionability** | [1-5] | [Assessment notes] |

#### Complexity Classification
- **Query Complexity**: [🟢 GREEN/🟡 YELLOW/🔴 RED/⚫ BLACK]
- **Request Complexity**: [📝 SIMPLE/📊 MODERATE/🔍 COMPLEX/🚀 ADVANCED]
- **Validation Requirements**: [Level 1/2/3/4/5 validation needed]

### Phase 2: Data Exploration

#### Data Sources Required
- **Primary Source**: `agg.agg_sm_daily_users_stats` (for revenue and user metrics)
- **Secondary Sources**: [List additional tables if needed]
  - `dwh.sm_fact_payments` (for detailed revenue breakdowns)
  - `dwh.sm_user_profile_datamining_snapshot` (for CZ deluxe segments)
  - `dwh.fact_sm_bonus_history` (for bonus analysis)
  - `dwh.sm_fact_virtual_payment_slotobucks` (for virtual currency)
- **Validation Sources**: [Cross-reference data sources]

#### Data Quality Assessment
```sql
-- SM Data Quality Check
SELECT 
    calc_date,
    COUNT(*) as total_records,
    COUNT(CASE WHEN user_id IS NOT NULL THEN 1 END) as complete_records,
    COUNT(CASE WHEN daily_Net_revenue IS NOT NULL THEN 1 END) as revenue_records,
    COUNT(CASE WHEN daily_Net_revenue IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as revenue_completeness_rate,
    MIN(calc_date) as earliest_date,
    MAX(calc_date) as latest_date
FROM agg.agg_sm_daily_users_stats
WHERE calc_date BETWEEN :start_date AND :end_date
GROUP BY calc_date
ORDER BY calc_date;
```

#### Revenue Validation Check
```sql
-- SM Revenue Cross-Validation
WITH fact_revenue AS (
    SELECT 
        tran_date,
        SUM(net_amount) as fact_revenue
    FROM dwh.sm_fact_payments
    WHERE tran_status_id = 2
      AND is_test = 0
      AND artificial_ind = 0
      AND tran_date BETWEEN :start_date AND :end_date
    GROUP BY tran_date
),
agg_revenue AS (
    SELECT 
        calc_date,
        SUM(daily_Net_revenue) as agg_revenue
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date BETWEEN :start_date AND :end_date
    GROUP BY calc_date
)
SELECT 
    COALESCE(f.tran_date, a.calc_date) as date,
    f.fact_revenue,
    a.agg_revenue,
    ABS(COALESCE(f.fact_revenue, 0) - COALESCE(a.agg_revenue, 0)) as difference,
    CASE 
        WHEN ABS(COALESCE(f.fact_revenue, 0) - COALESCE(a.agg_revenue, 0)) < 100 THEN 'MATCH'
        ELSE 'DISCREPANCY'
    END AS validation_status
FROM fact_revenue f
FULL OUTER JOIN agg_revenue a
    ON f.tran_date = a.calc_date
ORDER BY date;
```

### Phase 3: Analysis Execution

#### Primary Analysis Query
```sql
-- SM Primary Analysis
[Insert main analysis query here]
-- Remember: Use two-step aggregation for period comparisons
-- Remember: Use status filter (tran_status_id = 2) for payments
-- Remember: Separate real money revenue from virtual currency
```

#### Secondary Analysis Queries
```sql
-- SM Secondary Analysis
[Insert additional analysis queries if needed]
```

### Phase 4: Validation

#### Validation User Selection
- **User 1**: [User ID] - [Activity Level: High/Medium/Low]
- **User 2**: [User ID] - [Activity Level: High/Medium/Low]
- **User 3**: [User ID] - [Activity Level: High/Medium/Low]

#### Raw Data Extraction
```sql
-- SM Raw Data for Validation Users
SELECT 
    user_id,
    calc_date,
    spins,
    bet_coins,
    win_coins,
    daily_Net_revenue,
    balance_start_day,
    balance_end_day
FROM agg.agg_sm_daily_users_stats
WHERE user_id IN ([validation_user_ids])
  AND calc_date BETWEEN :start_date AND :end_date
ORDER BY user_id, calc_date;
```

#### Single-User Validation
```sql
-- SM Single-User Validation
SELECT [same_columns_as_main_query]
FROM [same_tables_as_main_query]
WHERE user_id = [validation_user_id]
  AND [same_conditions_as_main_query]
```

#### Cross-Table Validation
```sql
-- SM Cross-Table Validation
[Insert cross-validation query]
```

### Phase 5: Results & Insights

#### Key Findings
1. [Finding 1 with business impact]
2. [Finding 2 with business impact]
3. [Finding 3 with business impact]

#### Business Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

#### Validation Results
- **Complexity Assessment**: [Query Level] + [Request Level]
- **Validation Users**: [List of user IDs]
- **Raw Data Check**: [Summary]
- **Cross-Validation**: [Results]
- **Validation Status**: ✅ Validated / ❌ Issues Found
- **Confidence Level**: [High/Medium/Low]

## SM-Specific Considerations

### Revenue Analysis
- ✅ Use `agg.agg_sm_daily_users_stats.daily_Net_revenue` as primary source
- ✅ Use `dwh.sm_fact_payments` with `tran_status_id = 2` filter for detailed breakdowns
- ✅ Cross-validate fact table results with aggregated table
- ✅ Separate real money revenue from virtual currency redemption

### Aggregation Methodology
- ✅ Use two-step aggregation for all period comparisons
- ✅ Step 1: Calculate daily metrics with `GROUP BY calc_date`
- ✅ Step 2: Average daily metrics for period comparisons
- ✅ Validate results match simple daily queries

### Currency Separation
- ✅ Real Money Revenue: USD from `dwh.sm_fact_payments.net_amount`
- ✅ Virtual Currency: Virtual currency from `dwh.sm_fact_virtual_payment_slotobucks.transaction_amount`
- ✅ NEVER ADD: These are different currencies with different purposes

### User Segmentation
- ✅ CZ Deluxe Segments: Use `dwh.sm_user_profile_datamining_snapshot.cz_deluxe_weekly_update`
- ✅ VIP Tiers: Use `dwh.sm_user_profile_datamining_snapshot.tier_id`
- ✅ Paying Status: Use `daily_Net_revenue > 0` for current day status

This template provides a structured approach for SM data analysis projects with proper validation and SM-specific considerations.

