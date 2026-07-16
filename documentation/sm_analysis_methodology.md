# SM Analysis Methodology

**Note**: All SQL queries in this document use Vertica-compatible syntax. For detailed Vertica SQL syntax guidelines, see `documentation/sm_vertica_sql_compatibility.md`.

## Principles
- Business-first objectives
- Dual complexity assessment (query + request)
- Validation before presentation
- Two-step aggregation for all KPI calculations (MANDATORY)
- Revenue validation with status filters (MANDATORY)
- Currency separation (real money vs virtual currency)
- Data quality first, insights second
- Cross-table validation for accuracy
- Statistical validation for reliability

## Critical SM-Specific Rules

### Two-Step Aggregation (MANDATORY)
**ALL KPI calculations MUST use two-step aggregation to prevent 8-10x undercounting:**

#### Step 1: Calculate Daily Metrics
```sql
WITH daily_metrics AS (
    SELECT 
        calc_date,
        DATE_TRUNC('month', calc_date) as month,
        COUNT(DISTINCT user_id) as daily_dau,
        SUM(daily_Net_revenue) as daily_revenue,
        COUNT(DISTINCT CASE WHEN bet_coins > 0 THEN user_id END) as daily_spinners
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date BETWEEN :start_date AND :end_date
    GROUP BY calc_date, DATE_TRUNC('month', calc_date)
)
```

#### Step 2: Average Daily Metrics
```sql
SELECT 
    month,
    ROUND(AVG(daily_dau), 0) as avg_daily_dau,
    ROUND(AVG(daily_revenue), 2) as avg_daily_revenue
FROM daily_metrics
GROUP BY month
ORDER BY month;
```

**Why This Matters:**
- Single-step aggregation: `COUNT(DISTINCT user_id) / COUNT(DISTINCT calc_date)` severely undercounts
- Example: January 2025 wrong method = 81,092 users (8.6x undercount!)
- Correct method = 696,002 users ✅

### Revenue Validation (MANDATORY)
**ALWAYS use approved transactions only:**

#### Primary Source (RECOMMENDED):
```sql
-- Use aggregated table for revenue totals
SELECT 
    calc_date,
    SUM(daily_Net_revenue) as approved_revenue
FROM agg.agg_sm_daily_users_stats
WHERE calc_date = :date
GROUP BY calc_date;
```

#### Secondary Source (When Needed):
```sql
-- Use fact table ONLY with status filter
SELECT 
    tran_date,
    SUM(net_amount) as approved_revenue
FROM dwh.sm_fact_payments
WHERE tran_status_id = 2  -- CRITICAL: Only approved
  AND is_test = 0
  AND artificial_ind = 0
  AND tran_date = :date
GROUP BY tran_date;
```

**Critical Filters:**
- `tran_status_id = 2` (approved only - ~96% of transactions are pending/failed)
- `is_test = 0` (exclude test transactions)
- `artificial_ind = 0` (exclude artificial transactions)

**Inflation Warning:**
- Without status filter: 18-25x inflated revenue
- Example: $21.4M (all transactions) vs $836K (approved only)

### Currency Separation (MANDATORY)
**NEVER mix real money revenue with virtual currency redemption:**

#### Real Money Revenue:
```sql
-- Actual USD revenue
SELECT 
    SUM(net_amount) as real_money_revenue_usd
FROM dwh.sm_fact_payments
WHERE tran_status_id = 2
  AND tran_date = :date;
```

#### Virtual Currency Redemption:
```sql
-- Virtual currency (NOT USD)
SELECT 
    SUM(transaction_amount) as slotobucks_redeemed
FROM dwh.sm_fact_virtual_payment_slotobucks
WHERE tran_status_id = 2
  AND tran_date = :date;
```

**Report Separately:**
- Real money revenue = Financial KPI (USD)
- Slotobucks redemption = Currency injection analysis (Virtual Currency)
- NEVER ADD these together (different currencies, different purposes)

### Coin Hyperinflation Context - CRITICAL ⚠️
**SM operates with EXTREME hyperinflation in virtual currency (coins). Coin amounts that would be errors in other games are NORMAL and EXPECTED in SM.**

**Normal Coin Amount Ranges:**
- **Trillions (10^12)**: Common for median values (e.g., median balance ~73-99 trillion)
- **Sextillions (10^21)**: Common for payment quantities (e.g., median payment ~7.6 sextillion)
- **Septillions (10^24)**: Common for P95 percentiles (e.g., P95 balance ~8-10 septillion)
- **Undecillions (10^32)**: Common for maximum values (e.g., max balance ~460 undecillion)

**Analysis Guidelines:**
- ✅ **Use percentiles**: Focus on percentile analysis rather than absolute values
- ✅ **Use ratios**: Focus on ratios (win rate, consumption rate) rather than absolute amounts
- ✅ **Use trends**: Focus on relative changes rather than absolute values
- ❌ **DO NOT flag**: High coin amounts as errors or outliers
- ❌ **DO NOT suggest**: Data cleaning for large coin amounts
- ❌ **DO NOT question**: Data quality based on coin magnitude alone

**Valid Data Quality Checks:**
- ✅ Negative balances (may indicate data issue)
- ✅ Zero balances with activity (may indicate data issue)
- ✅ Logical relationships (win ≤ bet when no purchase, etc.)
- ❌ High coin amounts (trillions+ are normal)

**Reference**: See `data_sources/sm_coin_hyperinflation_context.md` for detailed ranges, validation guidelines, and example queries.

## Data Quality Targets & Standards

### Completeness Standards
- **Revenue Data**: >95% of expected daily records present
- **User Activity Data**: >90% of expected daily records present
- **Balance Data**: >95% of expected daily records present
- **Dimension Data**: 100% completeness for key dimensions
- **Missing Data Threshold**: Alert if >5% missing for critical metrics

### Data Quality Targets by Metric Type
- **User Metrics**: >98% accuracy in user identification and counting
- **Revenue Metrics**: >99% accuracy in financial calculations
- **Economy Metrics**: >95% accuracy in balance and consumption calculations
- **Time Metrics**: >99.5% accuracy in timestamp and date handling
- **Platform Metrics**: >99% accuracy in platform attribution
- **Segment Metrics**: >99% accuracy in CZ deluxe and VIP tier assignment

### Data Freshness Targets
- **Real-time Data**: <15 minutes delay for game events
- **Near Real-time Data**: <2 hours delay for payment transactions
- **Daily Aggregates**: <6 hours delay for daily KPI updates
- **Historical Data**: <24 hours delay for complete historical analysis

### Accuracy Standards
- **Cross-Table Validation**: Revenue totals within 1% between fact and aggregated tables
- **Temporal Consistency**: No gaps in daily data series
- **Dimensional Consistency**: Sum of percentages = 100% for share metrics
- **Logical Consistency**: Net amount ≤ Gross amount, PU ≤ DAU
- **Single-User Validation**: Raw data matches aggregated results exactly
- **Aggregation Validation**: Two-step aggregation results match daily query results

### Timeliness Standards
- **Daily Data**: Available by 6 AM UTC next day
- **Hourly Data**: Available within 2 hours of hour end
- **Real-time Data**: Available within 15 minutes
- **Data Freshness Alert**: Flag if data is >24 hours old

## Advanced Validation Patterns

### Multi-Level Validation Framework

#### Level 1: Raw Data Validation
```sql
-- Raw data quality check
WITH raw_validation AS (
  SELECT 
    calc_date,
    COUNT(*) AS total_records,
    COUNT(CASE WHEN user_id IS NULL THEN 1 END) AS null_user_ids,
    COUNT(CASE WHEN daily_Net_revenue IS NULL THEN 1 END) AS null_revenue,
    COUNT(CASE WHEN spins IS NULL THEN 1 END) AS null_spins,
    COUNT(CASE WHEN balance_end_day IS NULL THEN 1 END) AS null_balance
  FROM agg.agg_sm_daily_users_stats
  WHERE calc_date >= CURRENT_DATE - 7
  GROUP BY calc_date
)
SELECT 
  calc_date,
  total_records,
  ROUND((CAST(null_user_ids AS FLOAT) / CAST(total_records AS FLOAT)) * 100, 2) AS null_user_id_pct,
  ROUND((CAST(null_revenue AS FLOAT) / CAST(total_records AS FLOAT)) * 100, 2) AS null_revenue_pct,
  CASE 
    WHEN null_user_ids > 0 THEN 'CRITICAL: Missing user IDs'
    WHEN null_revenue > 0 THEN 'WARNING: Missing revenue data'
    ELSE 'OK'
  END AS validation_status
FROM raw_validation
ORDER BY calc_date DESC;
```

#### Level 2: Single-User Validation
```sql
-- Single-user data consistency check
WITH user_validation AS (
  SELECT 
    user_id,
    COUNT(*) AS active_days,
    SUM(daily_Net_revenue) AS total_revenue,
    SUM(spins) AS total_spins,
    SUM(bet_coins) AS total_bet,
    SUM(win_coins) AS total_win,
    AVG(balance_end_day) AS avg_balance
  FROM agg.agg_sm_daily_users_stats
  WHERE calc_date >= CURRENT_DATE - 30
  GROUP BY user_id
)
SELECT 
  user_id,
  active_days,
  total_revenue,
  total_spins,
  total_bet,
  total_win,
  avg_balance,
  CASE 
    WHEN total_bet < total_win AND total_revenue = 0 THEN 'Inconsistent: Win > Bet without revenue'
    WHEN total_spins > 0 AND total_bet = 0 THEN 'Inconsistent: Spins without bets'
    ELSE 'OK'
  END AS validation_status
FROM user_validation
WHERE total_spins > 0
LIMIT 10;
```

#### Level 3: Cross-Table Validation
```sql
-- Cross-validate revenue between fact and aggregated tables
WITH fact_revenue AS (
  SELECT 
    tran_date,
    SUM(net_amount) as fact_revenue
  FROM dwh.sm_fact_payments
  WHERE tran_status_id = 2
    AND is_test = 0
    AND artificial_ind = 0
    AND tran_date >= CURRENT_DATE - 7
  GROUP BY tran_date
),
agg_revenue AS (
  SELECT 
    calc_date,
    SUM(daily_Net_revenue) as agg_revenue
  FROM agg.agg_sm_daily_users_stats
  WHERE calc_date >= CURRENT_DATE - 7
  GROUP BY calc_date
)
SELECT 
  COALESCE(f.tran_date, a.calc_date) as date,
  f.fact_revenue,
  a.agg_revenue,
  ABS(COALESCE(f.fact_revenue, 0) - COALESCE(a.agg_revenue, 0)) as difference,
  ROUND((ABS(COALESCE(f.fact_revenue, 0) - COALESCE(a.agg_revenue, 0)) / NULLIF(COALESCE(a.agg_revenue, 1), 0)) * 100, 2) as difference_pct,
  CASE 
    WHEN ABS(COALESCE(f.fact_revenue, 0) - COALESCE(a.agg_revenue, 0)) < 100 THEN 'MATCH'
    WHEN ABS(COALESCE(f.fact_revenue, 0) - COALESCE(a.agg_revenue, 0)) / NULLIF(COALESCE(a.agg_revenue, 1), 0) < 0.01 THEN 'MATCH (<1% diff)'
    ELSE 'DISCREPANCY'
  END AS validation_status
FROM fact_revenue f
FULL OUTER JOIN agg_revenue a
  ON f.tran_date = a.calc_date
ORDER BY date DESC;
```

#### Level 4: Business Logic Validation
```sql
-- Validate business logic rules
WITH business_logic_check AS (
  SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as dau,
    COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) as paying_users,
    SUM(daily_Net_revenue) as total_revenue,
    SUM(bet_coins) as total_bet,
    SUM(win_coins) as total_win,
    AVG(balance_end_day) as avg_balance
  FROM agg.agg_sm_daily_users_stats
  WHERE calc_date >= CURRENT_DATE - 7
  GROUP BY calc_date
)
SELECT 
  calc_date,
  dau,
  paying_users,
  total_revenue,
  total_bet,
  total_win,
  avg_balance,
  CASE 
    WHEN paying_users > dau THEN 'ERROR: Paying users > DAU'
    WHEN total_revenue < 0 THEN 'ERROR: Negative revenue'
    WHEN total_bet < total_win AND total_revenue = 0 THEN 'WARNING: Win > Bet without revenue'
    ELSE 'OK'
  END AS validation_status
FROM business_logic_check
ORDER BY calc_date DESC;
```

#### Level 5: Aggregation Methodology Validation
```sql
-- Validate two-step aggregation methodology
WITH daily_metrics AS (
  SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as daily_dau
  FROM agg.agg_sm_daily_users_stats
  WHERE calc_date BETWEEN '2025-01-01' AND '2025-01-31'
  GROUP BY calc_date
),
two_step_avg AS (
  SELECT 
    ROUND(AVG(daily_dau), 0) as avg_dau_two_step
  FROM daily_metrics
),
single_step_avg AS (
  SELECT 
    COUNT(DISTINCT user_id) / COUNT(DISTINCT calc_date) as avg_dau_single_step
  FROM agg.agg_sm_daily_users_stats
  WHERE calc_date BETWEEN '2025-01-01' AND '2025-01-31'
)
SELECT 
  t.avg_dau_two_step as correct_method,
  s.avg_dau_single_step as wrong_method,
  ROUND((t.avg_dau_two_step / NULLIF(s.avg_dau_single_step, 0)), 2) as inflation_factor,
  CASE 
    WHEN ABS(t.avg_dau_two_step - s.avg_dau_single_step) / NULLIF(t.avg_dau_two_step, 0) > 0.1 THEN 'CRITICAL: Single-step undercounts significantly'
    ELSE 'OK'
  END AS validation_status
FROM two_step_avg t, single_step_avg s;
```

## Query Patterns from Daily Reports

### VF$ Daily Pattern (Product Performance)
```sql
-- Product performance with value-for-money analysis
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
        -- Complex product value calculation with tier/level multipliers
        SELECT
            p.product_group as Product_Name,
            p.tran_date,
            p.gross_amount,
            p.payment_quantity,
            -- Value calculation with BM multipliers and tier logic
            p.value * CASE
                WHEN a.tier_id < 4 THEN BM_multiplier
                WHEN BM_multiplier = 1 AND a.tier_id >= 4 THEN 4200
                -- ... additional tier/BM multiplier logic
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
          AND p.tran_status_id = 2
          AND p.artificial_ind = 0
          AND p.is_test = 0
    ) a
    GROUP BY Product_Name, tran_date
) a;
```

### Behavior Pattern (User Engagement by CZ Segment)
```sql
-- User behavior analysis by CZ deluxe segment
SELECT DISTINCT
    calc_date,
    CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END as is_pu,
    CASE
        WHEN b.cz_deluxe_weekly_update >= 0 AND b.cz_deluxe_weekly_update < 5 THEN '0-5'
        WHEN b.cz_deluxe_weekly_update >= 5 AND b.cz_deluxe_weekly_update < 10 THEN '5-10'
        -- ... additional CZ segments
        WHEN b.cz_deluxe_weekly_update > 100 THEN '+100'
    END as CZ,
    -- Vertica-compatible: Use PERCENTILE_CONT(0.5) instead of MEDIAN() window function
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as median_wager,
    -- Vertica-compatible: Use PERCENTILE_CONT instead of PERCENTILE_DISC for window functions
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as wager_Percentile_75,
    COUNT(CASE WHEN daily_gross_rev > 0 THEN a.user_id END) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as pu,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as balance_end_day,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY spins) OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as median_spins,
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

### Consumption Rate Calculation Pattern
**Purpose**: Calculate coin consumption rates relative to currency injection

**Methodology:**
1. **Calculate Daily Injection**: Sum payment_quantity and bonus_amount by date
2. **Calculate Daily Consumption**: Sum bet_coins and win_coins by date
3. **Calculate Net Consumption**: bet_coins - win_coins
4. **Calculate Consumption Rates**: Net consumption divided by injection amounts

**Key Formulas:**
- **Total Consumption Rate**: `(bet_coins - win_coins) / (payment_quantity + bonus_amount)`
- **Payment Consumption Rate**: `(bet_coins - win_coins) / payment_quantity`
- **Bonus Consumption Rate**: `(bet_coins - win_coins) / bonus_amount`

**Query Pattern:**
```sql
-- Coin consumption rate analysis
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
    ON a.tran_date = c.calc_date;
```

**Validation Requirements:**
- Verify payment injection uses `tran_status_id = 2` filter
- Verify bonus injection excludes transaction-based bonuses (`transaction_id IS NULL`)
- Cross-validate consumption totals with balance changes
- Check for NULL handling in division operations

### Machine RTP Analysis Pattern
**Purpose**: Calculate return-to-player (RTP) rates by slot machine type

**Methodology:**
1. **Join Spin Data with Machine Metadata**: Link spin events to machine characteristics
2. **Filter Active Machines**: Use `launch_date <= CURRENT_DATE` for active machines only
3. **Exclude Test Machines**: Remove test machine IDs (13522, 13569, 13626)
4. **Exclude Special Reels**: Remove dynamic/communal jackpot reels for standard analysis
5. **Calculate RTP**: `SUM(win_amount) / SUM(bet_amount)` by machine

**Query Pattern:**
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

**Validation Requirements:**
- Verify machine launch date filtering excludes future machines
- Verify test machine exclusion
- Verify special reel exclusion
- Cross-validate machine-level totals with aggregated spin data

### Slotobucks Flow Analysis Pattern
**Purpose**: Track Slotobucks balance changes (IN/OUT flow) by event type and tier

**Methodology:**
1. **Filter Balance Updates**: Exclude `event_type = 'initialBalance'` for flow analysis
2. **Calculate IN Flow**: Sum positive delta values
3. **Calculate OUT Flow**: Sum negative delta values (absolute value)
4. **Group by Event Type**: Categorize by event_type for source breakdown
5. **Group by Tier**: Analyze by decorated_tier_id for tier-based patterns

**Query Pattern:**
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
      -- Filter to paying users only (optional)
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

**Validation Requirements:**
- Verify initialBalance exclusion
- Verify user filtering logic (if applied)
- Cross-validate flow totals with Slotobucks redemption data
- Check for logical consistency (IN + OUT should match total flow)

### FTD (First-Time Deposit) Analysis Pattern
**Purpose**: Identify and analyze first-time deposits by product

**Methodology:**
1. **Identify FTDs**: Use `game_tran_order_count = 1` to identify first transactions
2. **Filter Production Environment**: Use `environment_id = 1` for production only
3. **Join Product Dimensions**: Link to product tables for product breakdown
4. **Group by Product**: Aggregate FTDs by product name/group

**Query Pattern:**
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

**Validation Requirements:**
- Verify FTD identification logic (`game_tran_order_count = 1`)
- Verify environment filtering (`environment_id = 1`)
- Cross-validate FTD counts with payment transaction data
- Check product mapping completeness

### Bonus Analysis with Purchase Flag Pattern
**Purpose**: Analyze bonus distribution and effectiveness by bonus type and purchase status

**Methodology:**
1. **Flag Purchase-Based Bonuses**: Use `CASE WHEN transaction_id IS NOT NULL THEN 1 ELSE 0 END`
2. **Join Bonus Type Dimension**: Link to `dwh.dim_sm_bonus_type` for bonus names
3. **Filter Paying Users**: Only include users with payments in last 180 days
4. **Exclude Journey State Users**: Remove users with `step_id = 539265`
5. **Group by Bonus Type and Purchase Flag**: Analyze by both dimensions

**Query Pattern:**
```sql
-- Bonus analysis with purchase flag
SELECT
    a.bonus_type_id,
    b.bonus_type_name,
    CASE WHEN transaction_id IS NOT NULL THEN 1 ELSE 0 END as is_purchase_bonus,
    DATE(bonus_ts) as calc_date,
    SUM(bonus_amount) as bonus_amounts,
    COUNT(DISTINCT user_id) as users,
    COUNT(*) as bonus_events
FROM dwh.fact_sm_bonus_history a
LEFT JOIN dwh.dim_sm_bonus_type b
    ON a.bonus_type_id = b.bonus_type_id
WHERE bonus_ts >= CURRENT_DATE - 180
  AND user_id NOT IN (
      -- Exclude journey state users
      SELECT DISTINCT user_id
      FROM dwh.sm_fact_journey_state_notifications
      WHERE step_id = 539265
  )
  AND user_id IN (
      -- Only paying users
      SELECT DISTINCT user_id
      FROM dwh.sm_fact_payments
      WHERE user_id > 0
        AND tran_status_id = 2
        AND artificial_ind = 0
        AND is_test = 0
        AND tran_date >= CURRENT_DATE - 180
  )
GROUP BY a.bonus_type_id, b.bonus_type_name, is_purchase_bonus, DATE(bonus_ts)
ORDER BY calc_date DESC, bonus_amounts DESC;
```

**Validation Requirements:**
- Verify purchase flag logic (transaction_id IS NOT NULL)
- Verify user filtering (paying users only)
- Verify journey state exclusion
- Cross-validate bonus totals with aggregated bonus data

### Churn Pattern
```sql
-- Churn rate analysis
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
        -- Vertica-compatible: Use 'day' instead of 'dd' for DATEDIFF
        DATEDIFF('day', last_login_date, date) as days_from_login
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

### Balance Pattern
```sql
-- Balance distribution analysis
SELECT DISTINCT
    first_session_tier,
    calc_date,
    CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END as is_pu,
    -- Vertica-compatible: Use PERCENTILE_CONT instead of MEDIAN() and PERCENTILE_DISC for window functions
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) as balance_end_day,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS Balance_Percentile_25,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS Balance_Percentile_50,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS Balance_Percentile_75,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY balance_end_day) OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS Balance_Percentile_95
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

## Best Practices

### Query Construction
1. **Always use two-step aggregation** for period comparisons
2. **Always filter revenue** with `tran_status_id = 2`
3. **Always separate currencies** (real money vs virtual currency)
4. **Always validate results** against known benchmarks
5. **Always document assumptions** and data quality limitations

### Performance Optimization
1. **Use aggregated tables** for primary metrics
2. **Filter early** in query execution
3. **Limit date ranges** to necessary periods
4. **Use appropriate indexes** (user_id, calc_date, tran_date)
5. **Test query performance** before production use

### Validation Requirements
1. **Raw data validation** for data quality
2. **Single-user validation** for calculation accuracy
3. **Cross-table validation** for consistency
4. **Business logic validation** for correctness
5. **Aggregation methodology validation** for two-step process

This methodology ensures accurate, reliable, and validated SM data analysis with proper handling of SM-specific data patterns and business rules.

