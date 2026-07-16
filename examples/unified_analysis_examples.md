# SM Unified Analysis Examples

This document provides comprehensive examples of SM data analysis with complexity assessment and validation requirements.

---

## Example 1: Daily Revenue Report (VF$ Daily Pattern)

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Multi-table joins, product mapping, value-for-money calculations, tier/level multipliers

### **Business Context**
Analyze daily revenue performance by product group with value-for-money metrics to identify monetization opportunities and optimize product pricing strategies.

### **Data Sources**
- Primary: `dwh.sm_fact_payments`
- Dimensions: `sm_draft.SM_DIM_Products`, `dwh.Dim_Coins_Value`, `dwh.sm_user_profile_datamining_snapshot`
- Validation: `agg.agg_sm_daily_users_stats`

### **Analysis Approach**
1. Extract payment transactions with status filter (`tran_status_id = 2`)
2. Join with product dimensions for product group mapping
3. Join with coin value dimensions for tier/level multipliers
4. Join with user snapshot for BM multipliers
5. Calculate value-for-money metrics (actual vs dimension)
6. Calculate percent sale (discount percentage)
7. Cross-validate with aggregated revenue

### **Query Pattern**
```sql
SELECT
    Product_Name,
    tran_date,
    value_for_money_actual,
    value_for_money_dim_coin_value,
    (value_for_money_actual / value_for_money_dim_coin_value) - 1 as percent_sale
FROM (
    SELECT
        Product_Name,
        tran_date,
        SUM(payment_quantity) / SUM(gross_amount) as value_for_money_actual,
        SUM(dim_coins_value_amount_with_BM) / SUM(gross_amount) as value_for_money_dim_coin_value
    FROM (
        -- Complex product value calculation with tier/level/BM multipliers
        SELECT
            p.product_group as Product_Name,
            p.tran_date,
            p.gross_amount,
            p.payment_quantity,
            -- Value calculation with BM multipliers and tier logic
            p.value * CASE
                WHEN a.tier_id < 4 THEN BM_multiplier
                WHEN BM_multiplier = 1 AND a.tier_id >= 4 THEN 4200
                -- Additional tier/BM multiplier logic
                ELSE BM_multiplier
            END as dim_coins_value_amount_with_BM
        FROM dwh.sm_fact_payments p
        LEFT JOIN sm_draft.SM_DIM_Products pr
            ON p.sku_id = pr.sku_id
            AND p.transaction_source_type_id = pr.transaction_source_type_id
        LEFT JOIN dwh.Dim_Coins_Value x
            ON p.level_id BETWEEN x.Level_From AND x.Level_To
            AND p.tier_id = x.tier_id
        LEFT JOIN dwh.sm_user_profile_datamining_snapshot t
            ON p.user_id = t.user_id
            AND p.tran_date = DATE(t.snapshot_insert_ts)
        WHERE p.tran_date >= CURRENT_DATE - 180
          AND p.tran_status_id = 2  -- CRITICAL: Only approved
          AND p.artificial_ind = 0
          AND p.is_test = 0
    ) a
    GROUP BY Product_Name, tran_date
) a;
```

### **Validation Requirements**
- **Level 1**: Payment data completeness, product mapping accuracy
- **Level 2**: Value calculations, tier/level multiplier logic
- **Level 3**: Revenue totals match aggregated table
- **Level 4**: Value-for-money distributions, product performance patterns
- **Level 5**: Historical product benchmarks, pricing trends

---

## Example 2: User Behavior Analysis by CZ Deluxe Segment

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Multi-table joins, window functions, CZ deluxe segmentation, percentile calculations

### **Business Context**
Analyze user engagement patterns by CZ deluxe segment to identify retention opportunities and optimize engagement strategies for different user segments.

### **Data Sources**
- Primary: `agg.agg_sm_daily_users_stats`
- Attributes: `dwh.sm_user_profile_datamining_snapshot`
- Validation: `dwh.sm_fact_payments` (for paying user identification)

### **Analysis Approach**
1. Extract daily user stats with engagement metrics
2. Join with user snapshot for CZ deluxe segments
3. Identify paying users (recent purchases within 14 days)
4. Calculate median and percentile metrics by segment
5. Analyze engagement patterns (spins, bets, balance, revenue)

### **Query Pattern**
```sql
SELECT DISTINCT
    calc_date,
    CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END as is_pu,
    CASE
        WHEN b.cz_deluxe_weekly_update >= 0 AND b.cz_deluxe_weekly_update < 5 THEN '0-5'
        WHEN b.cz_deluxe_weekly_update >= 5 AND b.cz_deluxe_weekly_update < 10 THEN '5-10'
        WHEN b.cz_deluxe_weekly_update >= 10 AND b.cz_deluxe_weekly_update < 20 THEN '10-20'
        WHEN b.cz_deluxe_weekly_update >= 20 AND b.cz_deluxe_weekly_update < 40 THEN '20-40'
        WHEN b.cz_deluxe_weekly_update >= 40 AND b.cz_deluxe_weekly_update < 60 THEN '40-60'
        WHEN b.cz_deluxe_weekly_update >= 60 AND b.cz_deluxe_weekly_update < 80 THEN '60-80'
        WHEN b.cz_deluxe_weekly_update >= 80 AND b.cz_deluxe_weekly_update < 100 THEN '80-100'
        WHEN b.cz_deluxe_weekly_update > 100 THEN '+100'
    END as CZ,
    MEDIAN(bet_coins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as median_wager,
    PERCENTILE_DISC(0.75) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as wager_Percentile_75,
    COUNT(CASE WHEN daily_gross_rev > 0 THEN a.user_id END) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as pu,
    MEDIAN(balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as balance_end_day,
    MEDIAN(spins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as median_spins,
    SUM(daily_Net_revenue) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as daily_net_revenue
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN dwh.sm_user_profile_datamining_snapshot b
    ON a.user_id = b.user_id
    AND a.calc_date = DATE(b.snapshot_insert_ts)
LEFT JOIN (
    SELECT DISTINCT user_id, tran_date
    FROM dwh.sm_fact_payments
    WHERE user_id > 0
      AND tran_status_id = 2
      AND artificial_ind = 0
      AND is_test = 0
      AND tran_ts >= CURRENT_DATE - 180
) x
    ON a.user_id = x.user_id
    AND x.tran_date BETWEEN a.calc_date - 14 AND a.calc_date
WHERE snapshot_insert_ts >= CURRENT_DATE - 180
  AND calc_date >= CURRENT_DATE - 180;
```

### **Validation Requirements**
- **Level 1**: User stats completeness, snapshot data accuracy
- **Level 2**: CZ segment assignment, paying user identification
- **Level 3**: Engagement metrics consistency, percentile calculations
- **Level 4**: Segment performance distributions, engagement patterns
- **Level 5**: Historical segment benchmarks, engagement trends

---

## Example 3: Consumption Analysis

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Multi-table joins, consumption rate calculations, economy balance analysis

### **Business Context**
Analyze coin consumption rates to monitor economy health and optimize currency injection strategies for sustainable game economy.

### **Data Sources**
- Primary: `dwh.sm_fact_payments`, `dwh.fact_sm_bonus_history`, `agg.agg_sm_daily_users_stats`
- Validation: Cross-check injection vs consumption totals

### **Analysis Approach**
1. Extract payment quantities (real money coin injection)
2. Extract bonus amounts (bonus coin injection)
3. Extract bet and win coins (consumption)
4. Calculate consumption rates (payment, bonus, total)
5. Analyze consumption patterns over time

### **Query Pattern**
```sql
SELECT
    a.tran_date,
    payment_quantity + bonus_amount as total_injection,
    bet_coins,
    win_coins,
    bet_coins - win_coins as bet_minus_win,
    (bet_coins - win_coins) / NULLIF(bonus_amount, 0) as consumption_bonus,
    (bet_coins - win_coins) / NULLIF(payment_quantity, 0) as consumption_payment,
    (bet_coins - win_coins) / NULLIF(payment_quantity + bonus_amount, 0) as consumption
FROM (
    SELECT
        tran_date,
        SUM(payment_quantity) as payment_quantity
    FROM dwh.sm_fact_payments
    WHERE tran_status_id = 2
      AND artificial_ind = 0
      AND is_test = 0
      AND tran_date >= CURRENT_DATE - 30
    GROUP BY tran_date
) a
LEFT JOIN (
    SELECT
        bonus_date,
        SUM(bonus_amount) as bonus_amount
    FROM dwh.fact_sm_bonus_history
    WHERE transaction_id IS NULL
      AND bonus_date >= CURRENT_DATE - 30
    GROUP BY bonus_date
) b
    ON a.tran_date = b.bonus_date
LEFT JOIN (
    SELECT
        calc_date,
        SUM(bet_coins) as bet_coins,
        SUM(win_coins) as win_coins
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date >= CURRENT_DATE - 30
    GROUP BY calc_date
) c
    ON a.tran_date = c.calc_date;
```

### **Validation Requirements**
- **Level 1**: Payment data completeness, bonus data accuracy
- **Level 2**: Consumption calculations, injection totals
- **Level 3**: Economy balance consistency, consumption rate logic
- **Level 4**: Consumption distributions, economy health patterns
- **Level 5**: Historical consumption benchmarks, economy trends

---

## Example 4: Churn Rate Analysis

### **Complexity Assessment**
- **Query Complexity**: 🔴 Complex
- **Request Complexity**: 🔍 Investigative
- **Rationale**: Complex cohort logic, churn identification, days from login calculations, retention analysis

### **Business Context**
Analyze churn rates by user segment and days from last login to identify at-risk users and inform retention campaigns.

### **Data Sources**
- Primary: `agg.agg_sm_daily_users_stats`
- Dimensions: `dwh.dim_dates`
- Validation: User activity patterns

### **Analysis Approach**
1. Create date grid for all dates in period
2. Cross join with all users active in period
3. Identify churn status (STAY vs CHURN) for each date
4. Calculate days from last login
5. Segment by login days and paying status
6. Analyze churn patterns by segment

### **Query Pattern**
```sql
SELECT
    CASE
        WHEN days_from_login <= 7 THEN '1 week last_login'
        WHEN days_from_login <= 14 THEN '2 weeks last_login'
        WHEN days_from_login <= 21 THEN '3 weeks last login'
        WHEN days_from_login >= 21 THEN 'more than 3 weeks'
    END as login_days,
    did_churn,
    date,
    is_pu,
    COUNT(DISTINCT user_id) as users
FROM (
    SELECT
        date,
        user_id,
        did_churn,
        is_pu,
        last_login_date,
        DATEDIFF('dd', last_login_date, date) as days_from_login
    FROM (
        SELECT
            did_churn,
            date,
            is_pu,
            a.user_id,
            MAX(calc_date) as last_login_date
        FROM (
            SELECT
                a.user_id,
                date,
                is_pu,
                CASE WHEN b.calc_date IS NOT NULL THEN 'STAY' ELSE 'CHURN' END as did_churn
            FROM (
                SELECT DISTINCT date
                FROM dwh.dim_dates
                WHERE date BETWEEN CURRENT_DATE - 180 AND CURRENT_DATE - 1
            ) a
            CROSS JOIN (
                SELECT DISTINCT
                    user_id,
                    MAX(CASE WHEN daily_Net_revenue > 0 THEN 1 ELSE 0 END) as is_pu
                FROM agg.agg_sm_daily_users_stats
                WHERE calc_date >= CURRENT_DATE - 364
                GROUP BY user_id
            ) b
            LEFT JOIN agg.agg_sm_daily_users_stats b
                ON a.user_id = b.user_id
                AND a.date = b.calc_date
        ) a
        LEFT JOIN agg.agg_sm_daily_users_stats c
            ON a.user_id = c.user_id
            AND c.calc_date < date
        GROUP BY did_churn, date, is_pu, a.user_id
    ) a
) b
GROUP BY login_days, did_churn, date, is_pu;
```

### **Validation Requirements**
- **Level 1**: User activity data completeness, date grid accuracy
- **Level 2**: Churn identification logic, days from login calculations
- **Level 3**: Churn rate consistency, user segment accuracy
- **Level 4**: Churn distributions, retention patterns
- **Level 5**: Historical churn benchmarks, retention trends
- **Level 6**: Edge case testing (promotional periods, system events)

---

## Example 5: Balance Index Analysis

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Window functions, percentile calculations, balance distribution analysis

### **Business Context**
Analyze balance distribution by user segment to monitor economy health and optimize currency injection strategies.

### **Data Sources**
- Primary: `agg.agg_sm_daily_users_stats`
- Validation: `dwh.sm_fact_payments` (for paying user identification)

### **Analysis Approach**
1. Extract daily user stats with balance metrics
2. Identify paying users (recent purchases within 14 days)
3. Calculate median and percentile balance distributions
4. Analyze balance patterns by paying status and tier
5. Monitor balance health indicators

### **Query Pattern**
```sql
SELECT DISTINCT
    first_session_tier,
    calc_date,
    CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END as is_pu,
    MEDIAN(balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) as balance_end_day,
    PERCENTILE_DISC(0.25) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS Balance_Percentile_25,
    PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS Balance_Percentile_50,
    PERCENTILE_DISC(0.75) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS Balance_Percentile_75,
    PERCENTILE_DISC(0.95) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS Balance_Percentile_95
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN (
    SELECT DISTINCT user_id, tran_date
    FROM dwh.sm_fact_payments
    WHERE tran_status_id = 2
      AND is_Test = 0
) b
    ON a.user_id = b.user_id
    AND b.tran_date BETWEEN a.calc_date - 14 AND a.calc_date
WHERE calc_date >= CURRENT_DATE - 365;
```

### **Validation Requirements**
- **Level 1**: Balance data completeness, paying user identification
- **Level 2**: Percentile calculations, balance distribution logic
- **Level 3**: Balance consistency, distribution patterns
- **Level 4**: Balance distributions, economy health indicators
- **Level 5**: Historical balance benchmarks, economy trends

---

## Example 6: Product Performance Analysis

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Product mapping, revenue breakdown, value-for-money analysis

### **Business Context**
Analyze product performance by product group to identify top-performing products and optimize product mix and pricing strategies.

### **Data Sources**
- Primary: `dwh.sm_fact_payments`
- Dimensions: `sm_draft.SM_DIM_Products` or `dwh.dim_sku_types`
- Validation: `agg.agg_sm_daily_users_stats`

### **Analysis Approach**
1. Extract payment transactions with status filter
2. Join with product dimensions for product group mapping
3. Calculate revenue, transactions, and coins by product
4. Analyze product performance trends
5. Cross-validate with aggregated revenue

### **Query Pattern**
```sql
SELECT
    COALESCE(pr.sku_name, 'Unknown') as product_name,
    COUNT(*) as transactions,
    SUM(p.net_amount) as revenue_usd,
    SUM(p.payment_quantity) as coins_purchased,
    AVG(p.payment_quantity) as avg_coins_per_purchase
FROM dwh.sm_fact_payments p
LEFT JOIN dwh.dim_sku_types pr
    ON p.sku_id = pr.sku_id
    AND p.transaction_source_type_id = pr.transaction_source_type_id
WHERE p.tran_date = CURRENT_DATE - 1
    AND p.tran_status_id = 2  -- CRITICAL: Only approved transactions
    AND p.is_test = 0
GROUP BY pr.sku_name
ORDER BY revenue_usd DESC;
```

### **Validation Requirements**
- **Level 1**: Payment data completeness, product mapping accuracy
- **Level 2**: Revenue calculations, product categorization
- **Level 3**: Product totals match aggregated revenue
- **Level 4**: Product performance distributions, revenue patterns
- **Level 5**: Historical product benchmarks, performance trends

---

## Example 7: Bonus Analysis

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Bonus tracking, consumption analysis, bonus effectiveness

### **Business Context**
Analyze bonus distribution and consumption to optimize bonus campaigns and improve bonus effectiveness.

### **Data Sources**
- Primary: `dwh.fact_sm_bonus_history`
- Validation: `agg.agg_sm_daily_users_stats` (for consumption)

### **Analysis Approach**
1. Extract bonus history with bonus types
2. Separate transaction-linked vs standalone bonuses
3. Calculate bonus amounts and distributions
4. Analyze bonus consumption rates
5. Evaluate bonus effectiveness

### **Query Pattern**
```sql
SELECT
    bonus_date,
    bonus_type_id,
    CASE WHEN transaction_id IS NOT NULL THEN 'Transaction-Linked' ELSE 'Standalone' END as bonus_type,
    COUNT(*) as bonus_count,
    SUM(bonus_amount) as total_bonus_amount,
    COUNT(DISTINCT user_id) as unique_users
FROM dwh.fact_sm_bonus_history
WHERE bonus_date >= CURRENT_DATE - 30
GROUP BY bonus_date, bonus_type_id, CASE WHEN transaction_id IS NOT NULL THEN 'Transaction-Linked' ELSE 'Standalone' END
ORDER BY bonus_date DESC, total_bonus_amount DESC;
```

### **Validation Requirements**
- **Level 1**: Bonus data completeness, bonus type accuracy
- **Level 2**: Bonus calculations, transaction linking logic
- **Level 3**: Bonus totals consistency, consumption patterns
- **Level 4**: Bonus distributions, effectiveness patterns
- **Level 5**: Historical bonus benchmarks, campaign trends

---

## Example 8: Virtual Currency Redemption Analysis

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Virtual currency tracking, product mapping, currency injection analysis

### **Business Context**
Analyze Slotobucks redemption patterns to understand virtual currency usage and optimize currency injection strategies.

### **Data Sources**
- Primary: `dwh.sm_fact_virtual_payment_slotobucks`
- Dimensions: `sm_draft.SM_DIM_Products`
- Validation: Separate from real money revenue

### **Analysis Approach**
1. Extract Slotobucks redemption transactions
2. Join with product dimensions for product group mapping
3. Calculate redemption amounts and coins by product
4. Analyze redemption patterns
5. **CRITICAL**: Report separately from real money revenue

### **Query Pattern**
```sql
SELECT
    COALESCE(p.product_group, 'Unknown') AS product_group,
    COUNT(*) AS sb_transactions,
    COUNT(DISTINCT f.user_id) AS sb_unique_users,
    SUM(f.transaction_amount) AS slotobucks_redeemed,  -- VIRTUAL CURRENCY (NOT USD)
    SUM(f.payment_quantity) AS coins_from_slotobucks
FROM dwh.sm_fact_virtual_payment_slotobucks f
LEFT JOIN sm_draft.SM_DIM_Products p
    ON f.transaction_source_type_id = p.transaction_source_type_id
    AND f.sku_id = p.sku_id
WHERE f.tran_date = CURRENT_DATE - 1
  AND f.tran_status_id = 2  -- CRITICAL: Only approved transactions
  AND f.is_test = 0
  AND f.user_id > 0
GROUP BY p.product_group
ORDER BY slotobucks_redeemed DESC;
```

### **Validation Requirements**
- **Level 1**: Virtual currency data completeness, product mapping accuracy
- **Level 2**: Redemption calculations, currency separation
- **Level 3**: Redemption totals consistency, currency injection patterns
- **Level 4**: Redemption distributions, usage patterns
- **Level 5**: Historical redemption benchmarks, currency trends
- **CRITICAL**: Verify virtual currency is NOT mixed with real money revenue

---

## Example 9: Comprehensive Revenue Analysis (Real Money + Virtual Currency)

### **Complexity Assessment**
- **Query Complexity**: 🔴 Complex
- **Request Complexity**: 🔍 Investigative
- **Rationale**: Multi-table joins, currency separation, comprehensive product analysis

### **Business Context**
Analyze both real money revenue and virtual currency redemption separately by product group to provide comprehensive monetization insights.

### **Data Sources**
- Primary: `dwh.sm_fact_payments`, `dwh.sm_fact_virtual_payment_slotobucks`
- Dimensions: `sm_draft.SM_DIM_Products`
- Validation: `agg.agg_sm_daily_users_stats`

### **Analysis Approach**
1. Extract real money payments with status filter
2. Extract virtual currency redemptions with status filter
3. Join both with product dimensions
4. Calculate metrics separately for each currency type
5. **CRITICAL**: Report separately, never add together

### **Query Pattern**
```sql
WITH real_money_products AS (
    SELECT
        COALESCE(p.product_group, 'Unknown') AS product_group,
        COUNT(*) AS rm_transactions,
        COUNT(DISTINCT f.user_id) AS rm_unique_users,
        SUM(f.net_amount) AS real_money_revenue_usd,  -- ACTUAL USD REVENUE
        SUM(f.payment_quantity) AS coins_from_real_money
    FROM dwh.sm_fact_payments f
    LEFT JOIN sm_draft.SM_DIM_Products p
        ON f.transaction_source_type_id = p.transaction_source_type_id
        AND f.sku_id = p.sku_id
    WHERE f.tran_date = CURRENT_DATE - 1
      AND f.tran_status_id = 2  -- CRITICAL: Only approved transactions
      AND f.is_test = 0
    GROUP BY p.product_group
),
slotobucks_products AS (
    SELECT
        COALESCE(p.product_group, 'Unknown') AS product_group,
        COUNT(*) AS sb_transactions,
        COUNT(DISTINCT f.user_id) AS sb_unique_users,
        SUM(f.transaction_amount) AS slotobucks_redeemed,  -- VIRTUAL CURRENCY REDEMPTION
        SUM(f.payment_quantity) AS coins_from_slotobucks
    FROM dwh.sm_fact_virtual_payment_slotobucks f
    LEFT JOIN sm_draft.SM_DIM_Products p
        ON f.transaction_source_type_id = p.transaction_source_type_id
        AND f.sku_id = p.sku_id
    WHERE f.tran_date = CURRENT_DATE - 1
      AND f.tran_status_id = 2  -- CRITICAL: Only approved transactions
      AND f.is_test = 0
      AND f.user_id > 0
    GROUP BY p.product_group
)
SELECT
    COALESCE(rm.product_group, sb.product_group, 'Unknown') AS product_group,
    -- REAL MONEY METRICS (Actual Revenue)
    ROUND(COALESCE(rm.real_money_revenue_usd, 0), 2) AS real_money_revenue_usd,
    COALESCE(rm.rm_transactions, 0) AS real_money_transactions,
    COALESCE(rm.rm_unique_users, 0) AS real_money_users,
    COALESCE(rm.coins_from_real_money, 0) AS coins_from_real_money,
    -- VIRTUAL CURRENCY METRICS (Redemption Analysis)
    ROUND(COALESCE(sb.slotobucks_redeemed, 0), 2) AS slotobucks_redeemed,
    COALESCE(sb.sb_transactions, 0) AS slotobucks_transactions,
    COALESCE(sb.sb_unique_users, 0) AS slotobucks_users,
    COALESCE(sb.coins_from_slotobucks, 0) AS coins_from_slotobucks
FROM real_money_products rm
FULL OUTER JOIN slotobucks_products sb
    ON rm.product_group = sb.product_group
WHERE COALESCE(rm.real_money_revenue_usd, 0) + COALESCE(sb.slotobucks_redeemed, 0) > 100
ORDER BY real_money_revenue_usd DESC;

-- CRITICAL: NEVER ADD real_money_revenue + slotobucks_redeemed
-- They are different metrics: USD vs Virtual Currency
```

### **Validation Requirements**
- **Level 1**: Payment data completeness, virtual currency data accuracy
- **Level 2**: Currency separation, product mapping accuracy
- **Level 3**: Revenue totals match aggregated table, currency separation verified
- **Level 4**: Product performance distributions, currency usage patterns
- **Level 5**: Historical benchmarks, monetization trends
- **CRITICAL**: Verify currencies are reported separately, never combined

---

## Common Validation Patterns

### Revenue Validation
```sql
-- Cross-validate revenue between fact and aggregated tables
WITH fact_revenue AS (
    SELECT SUM(net_amount) as revenue
    FROM dwh.sm_fact_payments
    WHERE tran_status_id = 2 AND tran_date = :date
),
agg_revenue AS (
    SELECT SUM(daily_Net_revenue) as revenue
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date = :date
)
SELECT
    f.revenue as fact_revenue,
    a.revenue as agg_revenue,
    ABS(f.revenue - a.revenue) as difference,
    CASE WHEN ABS(f.revenue - a.revenue) < 100 THEN 'MATCH' ELSE 'DISCREPANCY' END as status
FROM fact_revenue f, agg_revenue a;
```

### Two-Step Aggregation Validation
```sql
-- Validate two-step aggregation methodology
WITH daily_metrics AS (
    SELECT
        calc_date,
        COUNT(DISTINCT user_id) as daily_dau
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date BETWEEN :start_date AND :end_date
    GROUP BY calc_date
),
two_step_avg AS (
    SELECT ROUND(AVG(daily_dau), 0) as avg_dau_two_step
    FROM daily_metrics
),
single_step_avg AS (
    SELECT COUNT(DISTINCT user_id) / COUNT(DISTINCT calc_date) as avg_dau_single_step
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date BETWEEN :start_date AND :end_date
)
SELECT
    t.avg_dau_two_step as correct_method,
    s.avg_dau_single_step as wrong_method,
    ROUND((t.avg_dau_two_step / NULLIF(s.avg_dau_single_step, 0)), 2) as inflation_factor
FROM two_step_avg t, single_step_avg s;
```

---

## Example 10: Machine RTP Analysis

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Multi-table joins, machine-level aggregations, exclusion filters, RTP calculations

### **Business Context**
Analyze slot machine performance by calculating return-to-player (RTP) rates and payout amounts to identify top-performing machines, optimize machine mix, and monitor machine performance over time.

### **Data Sources**
- Primary: `dwh.fact_sm_spin_history_kafka` (spin events)
- Metadata: `dwh.sm_fact_machines_characteristics_data` (machine names, launch dates)
- Validation: `agg.agg_sm_daily_users_stats` (aggregated spin totals)

### **Analysis Approach**
1. Join spin data with machine metadata
2. Filter for active machines only (launch_date <= CURRENT_DATE)
3. Exclude test machines and special reel types
4. Calculate machine-level RTP (win_amount / bet_amount)
5. Aggregate by machine type, date, and launch date
6. Cross-validate totals with aggregated data

### **Query Pattern**
```sql
-- Machine-level RTP and payout analysis
SELECT
    spin_date,
    launch_date,
    a.machine_type_id,
    b.machine_name,
    SUM(win_amount) as total_wins,
    SUM(bet_amount) as total_bets,
    SUM(COALESCE(actual_raw_bet_amount, bet_amount)) as no_ante_bet,
    COUNT(DISTINCT user_id) as users,
    COUNT(*) as spins,
    CASE 
        WHEN SUM(bet_amount) > 0 
        THEN SUM(win_amount) / SUM(bet_amount) 
        ELSE NULL 
    END as machine_rtp
FROM dwh.fact_sm_spin_history_kafka a
JOIN dwh.sm_fact_machines_characteristics_data b
    ON a.machine_type_id = b.machine_id
WHERE b.launch_date <= CURRENT_DATE  -- Active machines only
  AND spin_date >= CURRENT_DATE - 60
  AND a.machine_type_id NOT IN (13522, 13569, 13626)  -- Exclude test machines
  AND reels NOT IN ('dynamicJackpot', 'royalCommunalJackpot')  -- Exclude special reels
  AND user_id NOT IN (
      SELECT DISTINCT user_id 
      FROM dwh.sm_fact_journey_state_notifications
      WHERE step_id = 539265
  )
  AND user_id NOT IN (
      SELECT DISTINCT user_id 
      FROM dwh.playtika_users
  )
GROUP BY spin_date, launch_date, a.machine_type_id, b.machine_name
ORDER BY spin_date DESC, machine_rtp DESC;
```

### **Validation Requirements**
- **Level 1**: Verify machine metadata completeness, spin data quality
- **Level 2**: Validate RTP calculations for sample machines
- **Level 3**: Cross-validate machine totals with aggregated spin data
- **Level 4**: Verify exclusion filters (test machines, special reels)
- **Level 5**: Compare RTP trends over time, validate against expected ranges

### **Business Insights**
- Identify top-performing machines by RTP and user engagement
- Monitor machine performance trends over time
- Optimize machine mix based on performance data
- Identify underperforming machines for optimization

---

## Example 11: Slotobucks Flow Analysis (IN/OUT)

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Balance update analysis, event type categorization, tier-based segmentation

### **Business Context**
Track Slotobucks balance changes (injection and redemption) by event type and VIP tier to understand Slotobucks sources, usage patterns, and optimize Slotobucks campaigns and promotions.

### **Data Sources**
- Primary: `dwh.sm_fact_internal_purchase_balance_update_slotobucks` (balance updates)
- Validation: `dwh.sm_fact_payments` (for user filtering)
- Cross-check: `dwh.sm_fact_virtual_payment_slotobucks` (redemption totals)

### **Analysis Approach**
1. Filter balance updates (exclude initialBalance)
2. Calculate IN flow (positive delta) and OUT flow (negative delta)
3. Group by event type for source breakdown
4. Group by tier for tier-based analysis
5. Filter to paying users (optional)
6. Cross-validate with redemption data

### **Query Pattern**
```sql
-- Slotobucks flow analysis (IN/OUT)
SELECT
    DATE(timestamp) as event_date,
    event_type,
    decorated_tier_id,
    SUM(CASE WHEN delta > 0 THEN delta END) as SB_IN,
    SUM(CASE WHEN delta < 0 THEN ABS(delta) END) as SB_OUT,
    SUM(delta) as net_flow,
    COUNT(*) as events,
    COUNT(DISTINCT user_id) as users
FROM dwh.sm_fact_internal_purchase_balance_update_slotobucks
WHERE timestamp >= CURRENT_DATE - 60
  AND event_type <> 'initialBalance'  -- Exclude initial balance
  AND user_id IN (
      -- Filter to paying users only
      SELECT DISTINCT user_id
      FROM dwh.sm_fact_payments
      WHERE user_id > 0
        AND tran_status_id = 2
        AND artificial_ind = 0
        AND is_test = 0
        AND tran_date >= CURRENT_DATE - 180
  )
GROUP BY DATE(timestamp), event_type, decorated_tier_id
ORDER BY event_date DESC, SB_IN DESC;
```

### **Validation Requirements**
- **Level 1**: Verify balance update data completeness
- **Level 2**: Validate IN/OUT calculations for sample users
- **Level 3**: Cross-validate OUT flow with redemption data
- **Level 4**: Verify event type categorization, tier assignments
- **Level 5**: Compare flow patterns over time, validate against campaigns

### **Business Insights**
- Understand Slotobucks injection sources (event types)
- Monitor Slotobucks redemption rates and patterns
- Analyze tier-based Slotobucks behavior
- Optimize Slotobucks campaigns based on flow data

---

## Example 12: Consumption Rate Analysis

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Multi-table joins, consumption rate calculations, injection vs consumption analysis

### **Business Context**
Calculate coin consumption rates relative to currency injection to monitor economy health, understand user spending patterns, and optimize currency injection strategies.

### **Data Sources**
- Primary: `agg.agg_sm_daily_users_stats` (consumption: bet_coins, win_coins)
- Injection: `dwh.sm_fact_payments` (payment_quantity), `dwh.fact_sm_bonus_history` (bonus_amount)
- Validation: Balance changes in daily stats

### **Analysis Approach**
1. Calculate daily payment injection (approved transactions only)
2. Calculate daily bonus injection (non-transaction bonuses)
3. Calculate daily consumption (bet_coins - win_coins)
4. Calculate consumption rates (total, payment, bonus)
5. Cross-validate with balance changes

### **Query Pattern**
```sql
-- Consumption rate analysis
SELECT
    a.tran_date,
    payment_quantity + bonus_amount as total_injection,
    bet_coins,
    win_coins,
    bet_coins - win_coins as net_consumption,
    (bet_coins - win_coins) / (bonus_amount) as consumption_bonus,
    (bet_coins - win_coins) / (payment_quantity) as consumption_payment,
    (bet_coins - win_coins) / (payment_quantity + bonus_amount) as total_consumption_rate
FROM (
    -- Payment injection (approved transactions only)
    SELECT
        tran_date,
        SUM(payment_quantity) as payment_quantity
    FROM dwh.sm_fact_payments
    WHERE tran_status_id = 2  -- CRITICAL: Only approved transactions
      AND artificial_ind = 0
      AND is_test = 0
      AND tran_date >= CURRENT_DATE - 30
    GROUP BY tran_date
) a
LEFT JOIN (
    -- Bonus injection (non-transaction bonuses only)
    SELECT
        bonus_date,
        SUM(bonus_amount) as bonus_amount
    FROM dwh.fact_sm_bonus_history
    WHERE transaction_id IS NULL  -- Non-transaction bonuses only
      AND bonus_date >= CURRENT_DATE - 30
    GROUP BY bonus_date
) b
    ON a.tran_date = b.bonus_date
LEFT JOIN (
    -- Consumption (bets and wins)
    SELECT
        calc_date,
        SUM(bet_coins) as bet_coins,
        SUM(win_coins) as win_coins
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date >= CURRENT_DATE - 30
    GROUP BY calc_date
) c
    ON a.tran_date = c.calc_date
ORDER BY a.tran_date DESC;
```

### **Validation Requirements**
- **Level 1**: Verify payment and bonus data completeness
- **Level 2**: Validate consumption calculations for sample dates
- **Level 3**: Cross-validate consumption with balance changes
- **Level 4**: Verify status filters, bonus filtering logic
- **Level 5**: Compare consumption rates over time, validate against economy targets

### **Business Insights**
- Monitor economy health through consumption rates
- Understand user spending patterns (payment vs bonus consumption)
- Optimize currency injection strategies
- Balance economy to prevent inflation or deflation

---

## Example 13: CZ Deluxe Segment Analysis with Recent Payer Flag

### **Complexity Assessment**
- **Query Complexity**: 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: Multi-table joins, window functions, dual segmentation, percentile calculations

### **Business Context**
Analyze user behavior by CZ deluxe segment and recent payer status to compare behavior between recent payers and non-payers within the same engagement segment, identify monetization opportunities, and optimize targeting strategies.

### **Data Sources**
- Primary: `agg.agg_sm_daily_users_stats` (user metrics)
- Attributes: `dwh.sm_user_profile_datamining_snapshot` (CZ deluxe segments)
- Recent Payer: `dwh.sm_fact_payments` (payment history for 14-day window)

### **Analysis Approach**
1. Join daily stats with CZ deluxe snapshot
2. Flag recent payers (payment in last 14 days)
3. Bin CZ deluxe values into standard segments
4. Calculate percentiles (median, P75, P95) by segment and payer flag
5. Analyze key metrics (bets, balances, spins, wins, revenue)

### **Query Pattern**
```sql
-- CZ deluxe segment analysis with recent payer flag
SELECT DISTINCT
    calc_date,
    CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END as is_recent_payer,
    CASE
        WHEN b.cz_deluxe_weekly_update >= 0 AND b.cz_deluxe_weekly_update < 5 THEN '0-5'
        WHEN b.cz_deluxe_weekly_update >= 5 AND b.cz_deluxe_weekly_update < 10 THEN '5-10'
        WHEN b.cz_deluxe_weekly_update >= 10 AND b.cz_deluxe_weekly_update < 20 THEN '10-20'
        WHEN b.cz_deluxe_weekly_update >= 20 AND b.cz_deluxe_weekly_update < 40 THEN '20-40'
        WHEN b.cz_deluxe_weekly_update >= 40 AND b.cz_deluxe_weekly_update < 60 THEN '40-60'
        WHEN b.cz_deluxe_weekly_update >= 60 AND b.cz_deluxe_weekly_update < 80 THEN '60-80'
        WHEN b.cz_deluxe_weekly_update >= 80 AND b.cz_deluxe_weekly_update < 100 THEN '80-100'
        WHEN b.cz_deluxe_weekly_update > 100 THEN '+100'
    END as CZ_segment,
    MEDIAN(bet_coins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END, CZ_segment) as median_wager,
    PERCENTILE_DISC(0.75) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END, CZ_segment) as wager_Percentile_75,
    PERCENTILE_DISC(0.95) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END, CZ_segment) as wager_Percentile_95,
    COUNT(CASE WHEN daily_gross_rev > 0 THEN a.user_id END) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END, CZ_segment) as paying_users,
    MEDIAN(balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END, CZ_segment) as median_balance,
    PERCENTILE_DISC(0.75) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END, CZ_segment) as balance_Percentile_75,
    PERCENTILE_DISC(0.95) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END, CZ_segment) as balance_Percentile_95,
    MEDIAN(spins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END, CZ_segment) as median_spins,
    SUM(daily_Net_revenue) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END, CZ_segment) as daily_net_revenue
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN dwh.sm_user_profile_datamining_snapshot b
    ON a.user_id = b.user_id
    AND a.calc_date = DATE(b.snapshot_insert_ts)
LEFT JOIN (
    -- Recent payer flag (payment in last 14 days)
    SELECT DISTINCT
        user_id,
        tran_date
    FROM dwh.sm_fact_payments
    WHERE user_id > 0
      AND tran_status_id = 2
      AND artificial_ind = 0
      AND is_test = 0
      AND tran_ts >= CURRENT_DATE - 180
) x
    ON a.user_id = x.user_id
    AND x.tran_date BETWEEN a.calc_date - 14 AND a.calc_date
WHERE snapshot_insert_ts >= CURRENT_DATE - 180
  AND calc_date >= CURRENT_DATE - 180;
```

### **Validation Requirements**
- **Level 1**: Verify CZ deluxe snapshot data completeness
- **Level 2**: Validate recent payer flag logic for sample users
- **Level 3**: Cross-validate segment totals with aggregated data
- **Level 4**: Verify percentile calculations, segment binning
- **Level 5**: Compare behavior patterns between recent payers and non-payers

### **Business Insights**
- Compare behavior between recent payers and non-payers within same CZ segment
- Identify monetization opportunities in high-engagement non-payers
- Understand payment patterns by engagement level
- Optimize targeting strategies for different segment combinations

---

## Example 14: FTD (First-Time Deposit) Analysis by Product

### **Complexity Assessment**
- **Query Complexity**: 🟢 Simple to 🟡 Moderate
- **Request Complexity**: 📊 Analytical
- **Rationale**: View-based FTD identification, product mapping, simple aggregations

### **Business Context**
Analyze first-time deposits by product to understand which products drive new payer acquisition, optimize product mix for FTD conversion, and track FTD trends over time.

### **Data Sources**
- Primary: `dwh.v_fact_currency_transactions` (FTD identification)
- Product Mapping: `sm_draft.SM_DIM_Products` (product groups)
- Validation: `dwh.sm_fact_payments` (cross-check FTD counts)

### **Analysis Approach**
1. Filter for FTDs (`game_tran_order_count = 1`)
2. Filter production environment (`environment_id = 1`)
3. Join with product dimensions for product breakdown
4. Aggregate FTDs by product and date
5. Cross-validate with payment transaction data

### **Query Pattern**
```sql
-- FTD analysis by product
SELECT
    tran_date,
    COALESCE(b.product_group, 'Unknown') as Product_Name,
    COUNT(DISTINCT user_id) as FTDS,
    COUNT(*) as ftd_transactions
FROM dwh.v_fact_currency_transactions a
LEFT JOIN sm_draft.SM_DIM_Products b
    ON a.sku_id = b.sku_id 
    AND a.transaction_source_type_id = b.transaction_source_type_id
WHERE game_tran_order_count = 1  -- First transaction = FTD
  AND environment_id = 1  -- Production environment only
  AND tran_date >= CURRENT_DATE - 30
GROUP BY tran_date, b.product_group
ORDER BY tran_date DESC, FTDS DESC;
```

### **Validation Requirements**
- **Level 1**: Verify FTD identification logic (`game_tran_order_count = 1`)
- **Level 2**: Validate FTD counts for sample users
- **Level 3**: Cross-validate FTD totals with payment transaction data
- **Level 4**: Verify product mapping completeness
- **Level 5**: Compare FTD trends over time, validate against acquisition campaigns

### **Business Insights**
- Identify top-performing products for FTD conversion
- Track FTD trends by product over time
- Optimize product mix for new payer acquisition
- Understand product preferences of first-time payers

---

These examples provide comprehensive patterns for SM data analysis with proper validation and SM-specific considerations.

