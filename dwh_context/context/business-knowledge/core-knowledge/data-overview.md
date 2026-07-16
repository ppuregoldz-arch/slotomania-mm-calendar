# Slotomania Management Report - Data Sources Context

## Overview
This document provides comprehensive context for all Slotomania data sources available in the Management Report embedded queries. All queries follow non-CTE patterns and use direct JOIN/subquery approaches for optimal performance.

## ⚠️ Important Query Rules

### 1. DO NOT Use CTEs (Common Table Expressions)
- **Never use `WITH` clauses** in queries
- Use **nested subqueries** instead of CTEs
- Use **table aliases** for complex multi-level joins
- Apply **direct filtering in subqueries** rather than WITH clauses

```sql
-- ❌ WRONG - Do NOT use CTEs
WITH user_data AS (
    SELECT user_id, SUM(amount) as total
    FROM payments
    GROUP BY user_id
)
SELECT * FROM user_data;

-- ✅ CORRECT - Use subqueries instead
SELECT * FROM (
    SELECT user_id, SUM(amount) as total
    FROM payments
    GROUP BY user_id
) user_data;
```

### 2. ALWAYS Exclude Internal/Test Users
Apply these exclusions in **every query** to filter out Playtika employees and test users:

```sql
-- Exclude internal/test users (Playtika employees)
AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.playtika_users)

-- Exclude journey step users
AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_fact_journey_state_notifications WHERE step_id = 539265)
```

## Core Data Warehouses & Tables

### Primary Data Sources

#### 1. **User Daily Statistics** 
- `agg.agg_sm_daily_users_stats` - Core daily user activity aggregation
- `agg.agg_sm_daily_users_stats_by_platform` - Daily user stats broken down by platform
- **Key Fields**: `calc_date`, `user_id`, `daily_Net_revenue`, `daily_gross_rev`, `balance_start_day`, `balance_end_day`, `bet_coins`, `win_coins`, `last_session_tier`, `first_session_tier`, `tier_id_end_day`, `cz_deluxe_weekly_update`, `platform_id`, `spins`, `daily_payments`

#### 2. **Payment Systems**
- `dwh.sm_fact_payments` - Real money transactions (has `price` column)
- `dwh.sm_fact_all_payments` - All payments consolidated (no `price` column, use `gross_amount`)
- `dwh.sm_fact_virtual_payment_slotobucks` - SlotoBucks virtual currency payments
- **Key Fields**: `tran_date`, `user_id`, `gross_amount`, `net_amount`, `price`, `sku_id`, `tier_id`, `platform_id`, `tran_status_id`

#### 2a. **Product Dimension Table**
- `sm_draft.SM_DIM_Products` - Product names and categories
- **Key Fields**: `sku_id`, `transaction_source_type_id`, `Product_Name`, `product_group`, `sku_name`
- **Join Pattern**: Join to payments on `sku_id` AND `transaction_source_type_id`

```sql
-- Example: Join payments to products
FROM dwh.sm_fact_payments a
LEFT JOIN sm_draft.SM_DIM_Products b
    ON a.sku_id = b.sku_id 
    AND a.transaction_source_type_id = b.transaction_source_type_id
```

**Product Name Classification Logic:**
```sql
-- Classify products based on payment_page_type_id
CASE
    WHEN Product_Name = 'Payment Page' AND payment_page_type_id = 30 THEN 'Payment Page'
    WHEN Product_Name = 'Payment Page' AND payment_page_type_id != 30 THEN 'ROOC'
    WHEN Product_Name = 'Gems' AND payment_page_type_id = 62 THEN 'Gems Payment Page'
    WHEN Product_Name = 'Gems' AND payment_page_type_id != 62 THEN 'ROOG'
    ELSE Product_Name 
END AS Product_Name
```

| Product | payment_page_type_id | Classification |
|---------|---------------------|----------------|
| Payment Page | 30 | Payment Page |
| Payment Page | other | ROOC (Rolling Offer On Coins) |
| Gems | 62 | Gems Payment Page |
| Gems | other | ROOG (Rolling Offer On Gems) |

#### 2b. **MGAP (Mini Game After Purchase)**
- `dwh.sm_fact_mgap_bonus_game_history` - MGAP bonus game events
- **Key Fields**: `event_date`, `user_id`, `game_type`, `transaction_id`, `orig_transaction_id`, `final_win_multiplier`
- **Description**: Optional mini-game offer after a user purchase, awarding extra coins percentage
- **Join Pattern**: Join to payments on `user_id` AND `orig_transaction_id = tran_id`

```sql
-- Example: Join MGAP to payments
LEFT JOIN (
    SELECT
        event_date,
        user_id,
        game_type AS MGAP_type,
        transaction_id,
        orig_transaction_id AS MGAP_source_tran_id,
        MAX(final_win_multiplier) AS final_win_multiplier
    FROM dwh.sm_fact_mgap_bonus_game_history
    WHERE event_date >= CURRENT_DATE - 14
    GROUP BY 1, 2, 3, 4, 5
) MGAP
    ON a.user_id = MGAP.user_id 
    AND MGAP.MGAP_source_tran_id = a.tran_id
```

#### 2c. **Currency Identification**
```sql
-- Identify payment currency type
CASE WHEN received_currency_id = 10005 THEN 'SB' ELSE 'real_money' END AS Source_currency
```

| received_currency_id | Currency Type |
|---------------------|---------------|
| 10005 | SlotoBucks (SB) |
| other | Real Money (USD) |

#### 3. **Game Activity**
- `dwh.fact_sm_spin_history_kafka` - All spin activities and game mechanics
- **Key Fields**: `spin_date`, `user_id`, `bet_amount`, `win_amount`, `machine_type_id`, `antebet_amounts_*` (multiple ante bet types)

#### 4. **Internal Economy**
- `dwh.sm_fact_internal_purchase_balance_update_slotobucks` - SlotoBucks balance changes
- `dwh.sm_fact_internal_purchase_balance_update` - Gems and other currency changes
- **Key Fields**: `timestamp`, `user_id`, `delta`, `new_balance`, `event_type`, `currency_id`

#### 5. **Bonus Systems**
- `dwh.fact_sm_bonus_history` - Bonus events and rewards
- **Key Fields**: `bonus_date`, `user_id`, `bonus_amount`, `bonus_type_id`

#### 6. **User Profiles**
- `dwh.sm_user_profile_datamining_snapshot` - User demographic and behavior snapshots
- **Key Fields**: `user_id`, `event_date_datamining`, `cz_deluxe_weekly_update`, `sq_wager`, `simple_median_bet`, `actual_median_bet`

#### 7. **A/B Test Tables**
- `sm_ds.abtest_user_allocations` - User test group assignments
- `sm_ds.abtest_dim_test` - Test definitions
- `sm_ds.abtest_dim_group` - Test group definitions
- `dwh.fact_sm_sessions_kafka` - Session data (used to identify "during" users)
- **Key Fields**: `test_id` (STRING), `user_id`, `group_test_id`, `group_name`, `allocation_percentage`, `ab_test_id`

**A/B Test Analysis Rules:**
- `test_id` is a **STRING** type (not integer)
- Only analyze **"during" users** - users who were active AFTER the test began
- Use `allocation_percentage` for group size **normalization** (group size in percentages)

```sql
-- A/B Test User Groups Query Pattern
SELECT DISTINCT
    a.user_id,
    group_name,
    allocation_percentage,
    CASE WHEN during_users.user_id IS NOT NULL THEN true ELSE false END AS is_during_users
FROM sm_ds.abtest_user_allocations a
LEFT JOIN sm_ds.abtest_dim_test t 
    ON a.test_id = t.ab_test_id
LEFT JOIN sm_ds.abtest_dim_group g 
    ON a.group_test_id = g.test_group_id
LEFT JOIN (
    -- "During" users: active after test start date
    SELECT DISTINCT user_id
    FROM dwh.fact_sm_sessions_kafka
    WHERE date(session_creation_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') >= <test_start_date>
) during_users
    ON a.user_id = during_users.user_id
WHERE test_id = <test_id>  -- STRING parameter
```

## Data Exclusion Patterns

### Standard User Exclusions (Applied Consistently)
```sql
-- Test/Internal Users
user_id not in (select distinct user_id from dwh.playtika_users)

-- Journey Step Exclusions  
user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)

-- Country Exclusions
user_id not in (select distinct user_id from dwh.sm_user_profile where country_name ilike '%iraq%')

-- Standard Payment User Filter
user_id in (
    select distinct user_id 
    from dwh.sm_fact_payments 
    where user_id > 0 
    and tran_status_id = 2 
    and artificial_ind = 0 
    and is_test = 0 
    and tran_date >= [DATE_RANGE]
)
```

## Key Metrics & KPIs Available

### 1. **SlotoBucks Economy**
- **Balance Distributions**: 25th, 50th, 75th, 95th percentiles by CZ ranges
- **Consumption Patterns**: `SB_IN` (earned) vs `SB_OUT` (spent)
- **Balance Velocity**: `(bet_coins - win_coins) / balance_start_day`
- **Revenue Correlation**: SlotoBucks balance ranges vs daily net revenue

### 2. **Payment Analytics**
- **Real Money vs Virtual Currency**: Separate tracking for USD and SlotoBucks
- **Value for Money**: `payment_quantity / gross_amount` (coins per dollar)
- **Tier-Based Pricing**: Dynamic pricing based on user tier and level
- **CZ Range Segmentation**: Granular user spending brackets

#### Average Transaction Calculation
When calculating **average transaction value**, use the following columns based on the table:

| Table | Column to Use | Description |
|-------|---------------|-------------|
| `dwh.sm_fact_payments` | `price` | Money received in dollars (preferred) |
| `dwh.sm_fact_all_payments` | `gross_amount` | Fallback when `price` is unavailable |

```sql
-- Average transaction using price (preferred)
AVG(price) AS avg_transaction

-- Average transaction using gross_amount (fallback)
AVG(gross_amount) AS avg_transaction
```

### 3. **Game Mechanics & Payouts**
- **Payout Ratios**: `bonus_amount / bet_adjusted_according_to_bonus`
- **Ante Bet Categories**: Mega Pods, Winovate, Sloto Quest, Royal JP, Dynamic Jackpot
- **Machine Performance**: Win rates and payout distributions by machine type
- **Bonus Group Analysis**: Performance by bonus category

### 4. **User Engagement**
- **Churn Analysis**: Stay vs Churn based on login patterns
- **Tier Progression**: `first_session_tier` vs `last_session_tier`
- **Balance Index**: Normalized balance metric across tiers
- **Velocity Metrics**: Spending velocity by tier and engagement level

### 5. **Gems Economy**
- **Transaction Types**: Gems received vs gems used
- **Event Tracking**: Source attribution for gem transactions
- **Purchase Integration**: Gem purchases linked to SKU data

#### Gems Source Categorization
When analyzing gems usage by source, use the following CASE statement to group `transaction_source_type_name` from `dwh.dim_transaction_source_type`:

```sql
CASE
    WHEN transaction_source_type_name ILIKE '%machine%' 
         OR transaction_source_type_name ILIKE '%spin%' 
         THEN 'machines'
    
    WHEN transaction_source_type_name ILIKE '%quest%' 
         THEN 'quest'
    
    WHEN transaction_source_type_name ILIKE '%blast%' 
         OR transaction_source_type_name ILIKE '%battle sheep%' 
         OR transaction_source_type_name ILIKE '%digging dog%' 
         OR transaction_source_type_name ILIKE '%snl%' 
         OR transaction_source_type_name ILIKE '%pick%' 
         THEN 'seasonals'
    
    WHEN transaction_source_type_name ILIKE '%shiny show%' 
         OR transaction_source_type_name ILIKE '%sloto show%' 
         OR transaction_source_type_name ILIKE '%slotoshow%' 
         THEN 'shiny show'
    
    WHEN transaction_source_type_name ILIKE '%gacha%' 
         OR transaction_source_type_name ILIKE '%album factory%' 
         THEN 'album factory'
    
    WHEN transaction_source_type_name ILIKE '%slotoheroes%' 
         THEN 'Figz/Globes'
    
    WHEN transaction_source_type_name ILIKE '%MWP%' 
         THEN 'Pods'
    
    WHEN transaction_source_type_name ILIKE '%winovate%' 
         THEN 'winovate'
    
    WHEN transaction_source_type_name ILIKE '%dash%' 
         OR transaction_source_type_name ILIKE '%clan%' 
         THEN 'dash/clan'
    
    ELSE 'other'
END AS transaction_source_type_name_grouped
```

**Gems Usage Analysis Pattern:**
```sql
SELECT
    year,
    quarter,
    year || ' - ' || quarter AS years_Q,
    transaction_source_type_name_grouped,
    SUM(cost) AS gems_used,
    COUNT(DISTINCT user_id) AS distinct_users,
    COUNT(DISTINCT event_date) AS distinct_days
FROM (
    SELECT
        user_id,
        b.transaction_source_type_name,
        timestamp::date AS event_date,
        MONTH(timestamp) AS month,
        YEAR(timestamp) AS year,
        CASE
            WHEN MONTH(timestamp) BETWEEN 1 AND 3 THEN 'Q1'
            WHEN MONTH(timestamp) BETWEEN 4 AND 6 THEN 'Q2'
            WHEN MONTH(timestamp) BETWEEN 7 AND 9 THEN 'Q3'
            WHEN MONTH(timestamp) BETWEEN 10 AND 12 THEN 'Q4'
        END AS quarter,
        cost
    FROM dwh.sm_fact_internal_purchases a
    LEFT JOIN dwh.dim_transaction_source_type b 
        USING (transaction_source_type_id)
    WHERE currency_id = 10000  -- Gems currency ID
        AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.playtika_users)
        AND user_id NOT IN (
            SELECT DISTINCT user_id 
            FROM dwh.sm_fact_journey_state_notifications 
            WHERE step_id = 539265
        )
        AND DATE(timestamp) >= CURRENT_DATE - 360
) A
GROUP BY 1, 2, 3, 4
```

**Key Points:**
- **Currency ID**: Use `currency_id = 10000` to filter for gems transactions in `dwh.sm_fact_internal_purchases`
- **Cost Column**: The `cost` column represents gems spent (negative values) or gems received (positive values)
- **Source Dimension**: Join to `dwh.dim_transaction_source_type` using `transaction_source_type_id` to get source names
- **Standard Exclusions**: Always exclude Playtika employees and journey test users when analyzing gems usage

## Query Pattern Analysis

### 1. **Window Functions for Percentile Analysis**
```sql
percentile_cont(0.50) within group (order by balance_end_day)
over (partition by calc_date, tier)
```

### 2. **Complex CASE Statements for Bucketing**
In the game pricing in gems and pricing in USD or Slotobucks are using two different parameters - form datamining tables

CZ for Gems Pricing

```sql
case
        when coalesce(cz_deluxe_weekly_update, 0) < 3 then '0-2.99'
        when cz_deluxe_weekly_update < 5 then '3-4.99'
        when cz_deluxe_weekly_update < 10 then '5-9.99'
        when cz_deluxe_weekly_update < 15 then '10-14.99'
        when cz_deluxe_weekly_update < 20 then '15-19.99'
        when cz_deluxe_weekly_update < 25 then '20-24.99'
        when cz_deluxe_weekly_update < 30 then '25-29.99'
        when cz_deluxe_weekly_update < 35 then '30-35.99'
        when cz_deluxe_weekly_update < 40 then '35-39.99'
        when cz_deluxe_weekly_update < 45 then '40-44.99'
        when cz_deluxe_weekly_update < 50 then '45-49.99'
        when cz_deluxe_weekly_update < 60 then '50-59.99'
        when cz_deluxe_weekly_update < 70 then '60-69.99'
        when cz_deluxe_weekly_update < 80 then '70-79.99'
        when cz_deluxe_weekly_update < 90 then '80-89.99'
        when cz_deluxe_weekly_update < 100 then '90-99.99'
        when cz_deluxe_weekly_update < 130 then '100-129.99'
        when cz_deluxe_weekly_update < 160 then '130-159.99'
        when cz_deluxe_weekly_update < 200 then '160-199.99'
        when cz_deluxe_weekly_update < 400 then '200-399.99'
        when cz_deluxe_weekly_update < 600 then '400-599.99'
        when cz_deluxe_weekly_update < 10000 then '600-9999.99'
        end as Gems_cz_range,
```


CZ for Regular pricing (USD) & Slotobucks purchases

```sql
    case
        when coalesce(cz_price_cut_test, 0) < 3 then '0-2.99'
        when cz_price_cut_test < 5 then '3-4.99'
        when cz_price_cut_test < 10 then '5-9.99'
        when cz_price_cut_test < 15 then '10-14.99'
        when cz_price_cut_test < 20 then '15-19.99'
        when cz_price_cut_test < 25 then '20-24.99'
        when cz_price_cut_test < 30 then '25-29.99'
        when cz_price_cut_test < 35 then '30-35.99'
        when cz_price_cut_test < 40 then '35-39.99'
        when cz_price_cut_test < 45 then '40-44.99'
        when cz_price_cut_test < 50 then '45-49.99'
        when cz_price_cut_test < 60 then '50-59.99'
        when cz_price_cut_test < 70 then '60-69.99'
        when cz_price_cut_test < 80 then '70-79.99'
        when cz_price_cut_test < 90 then '80-89.99'
        when cz_price_cut_test < 100 then '90-99.99'
        when cz_price_cut_test < 130 then '100-129.99'
        when cz_price_cut_test < 160 then '130-159.99'
        when cz_price_cut_test < 200 then '160-199.99'
        when cz_price_cut_test < 400 then '200-399.99'
        when cz_price_cut_test < 600 then '400-599.99'
        when cz_price_cut_test < 10000 then '600-9999.99'
        end as old_cz_range,
```


### 3. **ROW_NUMBER for Latest Records**
```sql
row_number() over (
    partition by user_id, date(timestamp) 
    order by timestamp desc
) rn
```

### 4. **Subquery Patterns Instead of CTEs**
- Nested subqueries for data preparation
- Table aliases for complex multi-level joins
- Direct filtering in subqueries rather than WITH clauses

### 5. **UNION Patterns for Multiple Metrics**
- Combining different bonus categories
- Merging real money and virtual currency data
- Aggregating multiple machine types

## Date Range Patterns

### Standard Time Windows
- **Short-term Analysis**: `current_date - 30` to `current_date - 60`
- **Medium-term Analysis**: `current_date - 90` to `current_date - 180`
- **Long-term Analysis**: `current_date - 364` for yearly comparisons
- **Historical Baseline**: `>= '2024-01-01'` for year-over-year analysis

### Promo Date vs Calendar Date

**Promo Date** is the promotional calendar day used for features like Daily Dash, Reveal Your Deal, etc. The promo day **starts at 12:00 UTC** (noon UTC), not midnight.

| Date Type | Day Boundary | Use Case |
|-----------|--------------|----------|
| `tran_date` | Midnight UTC | Standard calendar day analysis |
| `promo_date` | 12:00 UTC (noon) | Promotional features analysis |

**Promo Date Calculation:**
```sql
-- Convert transaction timestamp to promo_date (day starts at 12:00 UTC)
date(tran_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date
```

**Example:**
| Actual Time (UTC) | Promo Day |
|-------------------|-----------|
| Dec 3, 11:59 AM | Dec 2 promo |
| Dec 3, 12:00 PM | Dec 3 promo |
| Dec 4, 11:59 AM | Dec 3 promo |

## Performance Optimization Techniques

### 1. **Filtering Strategies**
- Early filtering in subqueries to reduce data volume
- Index-friendly date range filtering
- User ID filtering applied at lowest query level

### 2. **Aggregation Patterns**
- Pre-aggregation in subqueries before joins
- Grouping optimization to minimize result sets
- Strategic use of DISTINCT to eliminate duplicates

### 3. **Join Optimization**
- LEFT JOINs used where data may not exist
- Partition-based joins for time-series data
- Multiple join conditions to ensure data accuracy

## Currency Systems

### 1. **SlotoBucks (Primary Virtual Currency)**
- Currency ID: Not explicitly defined in queries
- Balance tracking via `sm_fact_internal_purchase_balance_update_slotobucks`
- Real-time balance updates with delta tracking

### 2. **Gems**
- Currency ID: 10000
- Event-based tracking with source attribution
- Purchase integration through SKU system

### 3. **Real Money**
- USD-based transactions through `sm_fact_payments`
- Tier-based pricing with dynamic multipliers
- Platform-specific handling (Web, iOS, Android, etc.)

## User Segmentation Framework

### 1. **CZ (Customer Zone) Ranges**
- Granular spending brackets from 0-2.99 to 500+
- Weekly update tracking for progression analysis
- Revenue correlation and behavior patterns

### 2. **Tier System**
- `first_session_tier` and `last_session_tier` tracking
- Tier-based game mechanics and pricing
- Progression analysis and retention correlation

### 3. **Platform Classification**
Use this CASE statement with any table containing `platform_id` field:

```sql
CASE
    WHEN Platform_id = 0 THEN 'Web'
    WHEN Platform_id = 1 THEN 'iOS'
    WHEN Platform_id = 2 THEN 'Android'
    WHEN Platform_id = 3 AND tier_id_end_day >= 5 THEN 'PRAS Web'
    WHEN Platform_id = 3 THEN '.Com'
    WHEN Platform_id = 6 THEN 'Amazon'
    WHEN Platform_id = 8 THEN 'Win8'
    WHEN Platform_id = 9 THEN 'Win10'
    WHEN platform_id = 11 THEN 'PRAS'
    ELSE 'Other'
END AS Platform
```

| platform_id | Platform Name | Notes |
|-------------|---------------|-------|
| 0 | Web | Facebook Web |
| 1 | iOS | Apple mobile |
| 2 | Android | Google Play |
| 3 | .Com / PRAS Web | PRAS Web if tier >= 5 |
| 6 | Amazon | Amazon Appstore |
| 8 | Win8 | Windows 8 |
| 9 | Win10 | Windows 10 |
| 11 | PRAS | Direct web platform |

### 3. **Payment Behavior**
- Paying vs Non-paying user classification
- Purchase frequency and amount patterns
- Lifetime value calculations

## Data Quality & Validation

### 1. **Standard Validations**
- `user_id > 0` for valid users
- `tran_status_id = 2` for successful transactions
- `artificial_ind = 0` to exclude test data
- `is_test = 0` for production data only

### 2. **Balance Consistency**
- End-of-day balance validation
- Delta calculation verification
- Cross-system balance reconciliation

This context provides the foundation for writing efficient, consistent queries across all Slotomania management reporting needs. 