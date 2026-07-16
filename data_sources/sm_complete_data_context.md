# Slotomania (SM) - Complete Data Context
*AI-Optimized Business Analysis Guide*

## Executive Summary

**Studio Overview**: Slotomania (SM) - Premier Slot Machine Casino Game  
**Data Maturity**: **D+ Rating** - CRITICAL IMPROVEMENT NEEDED  
**Domain Assets**: **1,019 entities** in SM domain (INCOMPLETE - 6,557 total scattered)  
**Revenue Model**: In-App Purchases (IAP) with virtual coin economy  
**Last Updated**: January 2025

### Critical AI Guidance
- **Revenue Authority**: ONLY use `agg.agg_sm_daily_users_stats.daily_Net_revenue`
- **NEVER use**: `dwh.sm_fact_payments` without `tran_status_id = 2` filter (18-25x inflated due to unapproved transactions)
- **User Identity**: `user_id` is primary key across all tables
- **Data Quality**: Poor - extensive domain fragmentation and missing documentation
- **Two-Step Aggregation**: MANDATORY for all KPI calculations

---

## Data Architecture Overview

### Data Flow Architecture (FRAGMENTED)
```
Game Events → Multiple Ingestion Points → Scattered Schemas → Limited Analytics
     ↓                  ↓                      ↓                    ↓
   Real-time        Inconsistent          Fragmented          Missing Dashboards
```

### Schema Organization (PROBLEMATIC)
- **`agg.*`** - Aggregated daily KPIs ⭐ (MOST RELIABLE)
- **`dwh.*`** - Raw transaction data ⚠️ (USE WITH EXTREME CAUTION)
- **`sm.*`** - Core business tables (LIMITED COVERAGE)
- **`sm_draft.*`** - Draft/dimension tables (PRODUCT MAPPING)
- **`stg.*`** - Staging tables (MIXED QUALITY)

### Domain Fragmentation Issue
```
SM Assets Distribution (BROKEN):
├── SM Domain: 1,019 assets (15% - INCOMPLETE)
├── CC Domain: 1,246 SM assets (MISPLACED)
├── Redecor Domain: 978 SM assets (MISPLACED)
├── BK Domain: 734 SM assets (MISPLACED)
├── WSOP Domain: 648 SM assets (MISPLACED)
└── Other Domains: 2,952 SM assets (MISPLACED)
```

---

## Critical Tables Inventory

### Revenue & Payments

#### PRIMARY: `agg.agg_sm_daily_users_stats` ⭐⭐⭐
**Purpose**: **AUTHORITATIVE REVENUE SOURCE** - Daily aggregated approved metrics  
**Refresh**: Daily  
**Grain**: user_id + calc_date  
**Data Quality**: GOOD (Only reliable SM revenue source)

**Critical Revenue Fields**:
```sql
calc_date               DATE         -- Business calculation date
user_id                 INTEGER      -- User identifier (primary key with date)
daily_Net_revenue       DECIMAL      -- 🚨 APPROVED REVENUE (USE THIS)
daily_gross_rev         DECIMAL      -- Gross revenue before adjustments
daily_payments          INTEGER      -- Number of approved transactions
is_paying_user          BOOLEAN      -- Made any purchase this day (1/0)
```

**Player Activity Fields**:
```sql
spins                   INTEGER      -- Daily slot machine spins
win_coins               DECIMAL      -- Virtual currency won
bet_coins               DECIMAL      -- Virtual currency wagered
balance_start_day       DECIMAL      -- Coin balance at day start
balance_end_day         DECIMAL      -- Coin balance at day end
daily_sessions_amount   INTEGER      -- Number of game sessions
friends_count           INTEGER      -- Social connections count
actual_median_bet       DECIMAL      -- Median bet amount
gems_end_of_day_balance DECIMAL      -- Gems balance at end of day
daily_bonus_coins       DECIMAL      -- Bonus coins received
```

**Critical Revenue Calculation**:
```sql
-- CORRECT Daily Revenue Query
SELECT 
  calc_date,
  SUM(daily_Net_revenue) as approved_revenue,
  COUNT(DISTINCT user_id) as total_users,
  COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) as paying_users
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date = '2025-06-10';
-- Result: $695,867 (CORRECT)
```

#### SECONDARY: `dwh.sm_fact_payments` ⚠️
**Purpose**: Raw payment transactions - Use ONLY with proper filtering  
**Refresh**: Real-time  
**Grain**: Individual transaction  
**⚠️ MANDATORY FILTER**: `WHERE tran_status_id = 2` (approved only)

**Transaction Fields**:
```sql
tran_date               DATE         -- Transaction processing date
user_id                 INTEGER      -- Player identifier
net_amount              DECIMAL      -- Amount after fees
gross_amount            DECIMAL      -- Amount before fees
tran_status_id          INTEGER      -- 🚨 CRITICAL FILTER: 2=approved, 1=pending, 3=failed
is_test                 BOOLEAN      -- Test transaction flag
is_ftd_platform         BOOLEAN      -- First-time deposit indicator
platform_id             INTEGER      -- Platform source
product_sku             STRING       -- Product purchased
sku_id                  INTEGER      -- SKU identifier
transaction_source_type_id INTEGER   -- Transaction source type
tax_amount              DECIMAL      -- Tax portion
payment_quantity        DECIMAL      -- Virtual coins received by player
level_id                INTEGER      -- User level at transaction time
tier_id                 INTEGER      -- User tier at transaction time
price                   DECIMAL      -- Product price
```

**Transaction Status Meanings:**
- `tran_status_id = 1`: Pending/In-Progress (~96% of transactions)
- `tran_status_id = 2`: Approved/Completed ✅ (USE THIS)
- `tran_status_id = 3`: Failed/Rejected

**Valid Use Cases:**
- Detailed transaction analysis with status filter
- Revenue source breakdown by SKU/platform
- Cross-validation of aggregated results
- Payment method analysis
- Product performance analysis

**Critical Examples:**
```sql
-- ✅ CORRECT: Approved transactions only
SELECT SUM(net_amount) FROM dwh.sm_fact_payments 
WHERE tran_status_id = 2 AND tran_date = '2025-06-15';
-- Result: $836,391 (matches aggregated table)

-- ❌ WRONG: All transactions (18-25x inflated)
SELECT SUM(net_amount) FROM dwh.sm_fact_payments 
WHERE tran_date = '2025-06-15';
-- Result: $21.4M (includes 760K pending transactions)
```

#### Virtual Currency: `dwh.sm_fact_virtual_payment_slotobucks`
**Purpose**: Virtual currency redemption transactions (Slotobucks)  
**Refresh**: Real-time  
**Grain**: Individual redemption transaction  
**⚠️ MANDATORY FILTER**: `WHERE tran_status_id = 2` (approved only)

**Virtual Currency Fields**:
```sql
tran_date               DATE         -- Transaction processing date
user_id                 INTEGER      -- Player identifier
transaction_amount      DECIMAL      -- 🎫 VIRTUAL CURRENCY REDEMPTION (NOT USD)
payment_quantity        DECIMAL      -- Coins received from redemption
tran_status_id          INTEGER      -- Status filter (2=approved)
is_test                 BOOLEAN      -- Test transaction flag
sku_id                  INTEGER      -- SKU identifier
transaction_source_type_id INTEGER   -- Transaction source type
```

**Critical Distinction:**
- **Real Money Revenue**: Actual USD from `dwh.sm_fact_payments.net_amount`
- **Slotobucks Redemption**: Virtual currency from `dwh.sm_fact_virtual_payment_slotobucks.transaction_amount`
- **NEVER ADD**: Real money + slotobucks (different currencies, different purposes)

#### `dwh.sm_fact_internal_purchase_balance_update_slotobucks`
**Purpose**: Internal Slotobucks balance updates and events  
**Refresh**: Real-time  
**Grain**: Individual balance update event

**Slotobucks Balance Update Fields**:
```sql
timestamp               TIMESTAMP    -- Event timestamp
user_id                 INTEGER      -- Player identifier
delta                   DECIMAL      -- Balance change (positive = IN, negative = OUT)
event_type              STRING       -- Event type/category (exclude 'initialBalance' for flow analysis)
decorated_tier_id       INTEGER      -- VIP tier at time of event
currency_id             INTEGER      -- Currency identifier
```

**Critical Usage Notes**:
- **Slotobucks IN**: `SUM(CASE WHEN delta > 0 THEN delta END)` - Positive delta indicates Slotobucks added
- **Slotobucks OUT**: `SUM(CASE WHEN delta < 0 THEN delta END)` - Negative delta indicates Slotobucks redeemed/consumed
- **Event Type Filtering**: Exclude `event_type = 'initialBalance'` for flow analysis
- **Tier-Based Analysis**: Use `decorated_tier_id` for tier-based Slotobucks flow analysis
- **Event Categorization**: Event types include 'manual-bonus-group' and other categories for source breakdown

#### `dwh.v_fact_currency_transactions`
**Purpose**: Currency transaction view for First-Time Deposit (FTD) analysis  
**Refresh**: Real-time (view)  
**Grain**: Individual currency transaction

**Currency Transaction Fields**:
```sql
tran_date               DATE         -- Transaction date
user_id                 INTEGER      -- Player identifier
sku_id                  INTEGER      -- SKU identifier
transaction_source_type_id INTEGER   -- Transaction source type
game_tran_order_count   INTEGER      -- Transaction order number (1 = first transaction = FTD)
environment_id          INTEGER      -- Environment identifier (1 = production)
```

**Critical Usage Notes**:
- **FTD Identification**: `game_tran_order_count = 1` identifies first-time deposits
- **Environment Filtering**: Use `environment_id = 1` for production environment only
- **Product-Level FTD**: Join with product dimensions for FTD analysis by product
- **Typical Usage**: FTD analysis by product for last 30 days

### User Profiles & Attributes

#### `dwh.sm_user_profile_datamining_snapshot`
**Purpose**: User attributes and segmentation data  
**Refresh**: Daily snapshot  
**Grain**: user_id + snapshot_insert_ts  
**Data Quality**: GOOD (Used for CZ deluxe segmentation)

**Key Fields**:
```sql
user_id                 INTEGER      -- Player identifier
snapshot_insert_ts      TIMESTAMP    -- Snapshot timestamp
cz_deluxe_weekly_update DECIMAL      -- CZ deluxe segment value
bm_multiplier           DECIMAL      -- Bonus multiplier
tier_id                 INTEGER      -- VIP tier
level_id                INTEGER      -- User level
```

**CZ Deluxe Segments**:
- 0-5: Low engagement
- 5-10: Low-medium engagement
- 10-20: Medium engagement
- 20-40: Medium-high engagement
- 40-60: High engagement
- 60-80: Very high engagement
- 80-100: Extremely high engagement
- +100: Maximum engagement

#### `sm.sm_user_profile` (LIMITED USE)
**Purpose**: User demographics and lifetime value  
**Refresh**: Inconsistent (STALE DATA ISSUES)  
**Grain**: user_id  
**Data Quality**: POOR (Missing real-time updates)

**Profile Fields**:
```sql
user_id                 INTEGER      -- Player identifier (primary key)
current_level           INTEGER      -- Game progression level
total_coins_earned      BIGINT       -- Lifetime virtual currency
registration_date       DATE         -- Account creation
last_login_date         DATE         -- Most recent session (OFTEN STALE)
vip_tier                INTEGER      -- VIP status level
country_code            STRING       -- Player location
country_name            STRING       -- Country name
```

### Gaming & Engagement

#### `dwh.fact_sm_bonus_history`
**Purpose**: Bonus tracking and history  
**Refresh**: Real-time  
**Grain**: Individual bonus event

**Bonus Fields**:
```sql
bonus_date              DATE         -- Bonus date
bonus_ts                TIMESTAMP    -- Bonus timestamp
user_id                 INTEGER      -- Player identifier
bonus_amount            DECIMAL      -- Bonus coins amount
bonus_type_id           INTEGER      -- Bonus type identifier (links to dwh.dim_sm_bonus_type)
transaction_id          INTEGER      -- Related transaction (NULL for non-transaction bonuses)
```

#### `dwh.dim_sm_bonus_type`
**Purpose**: Bonus type dimension table  
**Refresh**: Periodic  
**Grain**: bonus_type_id

**Bonus Type Fields**:
```sql
bonus_type_id           INTEGER      -- Bonus type identifier (primary key)
bonus_type_name         STRING       -- Bonus type name/category
```

**Usage**: Join with `dwh.fact_sm_bonus_history` on `bonus_type_id` for bonus categorization and reporting.

#### `dwh.fact_sm_spin_history_kafka`
**Purpose**: Individual slot machine spin events with machine-level detail  
**Refresh**: Real-time (Kafka stream)  
**Grain**: Individual spin event  
**Data Quality**: GOOD (Primary source for machine-level analysis)

**Spin Fields**:
```sql
spin_date               DATE         -- Spin date
spin_timestamp          TIMESTAMP    -- When spin occurred
user_id                 INTEGER      -- Player identifier
machine_type_id         INTEGER      -- Slot machine type identifier (joins to sm_fact_machines_characteristics_data.machine_id)
bet_amount              DECIMAL      -- Coins wagered on spin
win_amount              DECIMAL      -- Coins won from spin
actual_raw_bet_amount   DECIMAL      -- Raw bet amount (before ante, if applicable)
reels                   STRING       -- Reel type (exclude 'dynamicJackpot', 'royalCommunalJackpot' for standard analysis)
```

**Critical Usage Notes**:
- **Machine RTP Analysis**: Use for calculating return-to-player rates by machine type
- **Exclusions**: Exclude test machines (IDs: 13522, 13569, 13626)
- **Reel Exclusions**: Exclude `reels IN ('dynamicJackpot', 'royalCommunalJackpot')` for standard machine analysis
- **Join Pattern**: Join with `dwh.sm_fact_machines_characteristics_data` on `machine_type_id = machine_id`

#### `dwh.sm_fact_machines_characteristics_data`
**Purpose**: Slot machine metadata and characteristics  
**Refresh**: Periodic (when machines are added/updated)  
**Grain**: machine_id

**Machine Fields**:
```sql
machine_id              INTEGER      -- Machine identifier (primary key, joins to fact_sm_spin_history_kafka.machine_type_id)
machine_name            STRING       -- Machine name/theme
launch_date             DATE         -- Machine launch date (critical for filtering active machines)
```

**Critical Usage Notes**:
- **Active Machine Filtering**: Use `launch_date <= CURRENT_DATE` to filter for active machines only
- **Machine Performance**: Join with `dwh.fact_sm_spin_history_kafka` for machine-level RTP and payout analysis
- **Machine Naming**: Use `machine_name` for reporting and categorization

### Product & Dimension Tables

#### `sm_draft.SM_DIM_Products`
**Purpose**: Product mapping and categorization  
**Refresh**: Periodic  
**Grain**: sku_id + transaction_source_type_id

**Product Fields**:
```sql
sku_id                  INTEGER      -- SKU identifier
transaction_source_type_id INTEGER   -- Transaction source type
product_group           STRING       -- Product group/category
sku_name                STRING       -- Product name
```

#### `dwh.dim_sku_types`
**Purpose**: Alternative SKU mapping (simpler approach)  
**Refresh**: Periodic  
**Grain**: sku_id + transaction_source_type_id

**SKU Fields**:
```sql
sku_id                  INTEGER      -- SKU identifier
transaction_source_type_id INTEGER   -- Transaction source type
sku_name                STRING       -- Product name
```

#### `dwh.sm_dim_transaction_source_type`
**Purpose**: Transaction source type dimension  
**Refresh**: Periodic  
**Grain**: transaction_source_type_id

**Transaction Source Fields**:
```sql
transaction_source_type_id INTEGER   -- Transaction source type identifier (primary key)
transaction_source_type_name STRING  -- Transaction source type name/category
```

**Usage**: Join with payment and virtual payment tables on `transaction_source_type_id` for revenue source breakdown and product analysis.

#### `dwh.Dim_Coins_Value`
**Purpose**: Coin value mapping by level, tier, and denomination  
**Refresh**: Periodic  
**Grain**: Multiple dimensions

**Coin Value Fields**:
```sql
value                   DECIMAL      -- Coin value multiplier
denomination            DECIMAL      -- Price denomination
next_denomination       DECIMAL      -- Next price tier
Level_multiplier        DECIMAL      -- Level-based multiplier
Tier_multiplier         DECIMAL      -- Tier-based multiplier
Level_From              INTEGER      -- Level range start
Level_To                INTEGER      -- Level range end
tier_id                 INTEGER      -- VIP tier
platform                STRING       -- Platform (Web, iOS, Android)
```

### Gaming Events (LIMITED USE)

#### `sm.sm_fact_game_spins` (LIMITED)
**Purpose**: Slot machine spin events  
**Refresh**: Real-time (when working)  
**Grain**: Individual spin  
**Data Quality**: POOR (Data quality issues reported)

**Spin Fields**:
```sql
user_id                 INTEGER      -- Player identifier
spin_timestamp          TIMESTAMP    -- When spin occurred
machine_id              STRING       -- Slot machine identifier
bet_amount              INTEGER      -- Coins wagered
win_amount              INTEGER      -- Coins won
spin_result             STRING       -- Outcome type
bonus_triggered         BOOLEAN      -- Special feature activated
```

---

## Critical: Daily Average Calculation Methodology

### FUNDAMENTAL RULE: Two-Step Aggregation Required

**ALL KPI calculations MUST follow this two-step process:**

#### CORRECT APPROACH: Two-Step Aggregation
```sql
-- Step 1: Calculate daily metrics for each date (GROUP BY calc_date)
WITH daily_metrics AS (
    SELECT 
        calc_date,
        DATE_TRUNC('month', calc_date) as month,
        COUNT(DISTINCT user_id) as daily_dau,
        SUM(daily_Net_revenue) as daily_revenue,
        COUNT(DISTINCT CASE WHEN bet_coins > 0 THEN user_id END) as daily_spinners,
        COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) as daily_payers,
        ROUND((SUM(win_coins) / NULLIF(SUM(bet_coins), 0)) * 100, 2) as daily_win_rate
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date BETWEEN '2025-01-01' AND '2025-06-22'
    GROUP BY calc_date, DATE_TRUNC('month', calc_date)
)
-- Step 2: Average the daily metrics by month (GROUP BY month)
SELECT 
    month,
    COUNT(*) as days_in_month,
    ROUND(AVG(daily_dau), 0) as avg_daily_dau,
    ROUND(AVG(daily_revenue), 2) as avg_daily_revenue,
    ROUND(AVG(daily_spinners), 0) as avg_daily_spinners,
    ROUND(AVG(daily_payers), 0) as avg_daily_payers,
    ROUND(AVG(daily_win_rate), 2) as avg_daily_win_rate,
    -- All ratios calculated from daily averages
    ROUND((AVG(daily_spinners) / AVG(daily_dau)) * 100, 1) as engagement_rate_pct,
    ROUND((AVG(daily_payers) / AVG(daily_dau)) * 100, 1) as conversion_rate_pct
FROM daily_metrics
GROUP BY month
ORDER BY month;
```

#### WRONG APPROACH: Single-Step Aggregation
```sql
-- ❌ THIS IS WRONG - Severely undercounts users due to double-distinct aggregation
SELECT 
    DATE_TRUNC('month', calc_date) as month,
    COUNT(DISTINCT user_id) / COUNT(DISTINCT calc_date) as avg_daily_dau, -- WRONG!
    SUM(daily_Net_revenue) / COUNT(DISTINCT calc_date) as avg_daily_revenue -- WRONG!
FROM agg.agg_sm_daily_users_stats
GROUP BY DATE_TRUNC('month', calc_date);
-- Results in 8-10x undercount of users!
```

### Why This Matters - Real Impact Example

**January 2025 Comparison:**
- **Wrong Method**: 81,092 daily users (8.6x undercount!)
- **Correct Method**: 696,002 daily users ✅

**The Error**: Single-step aggregation counts unique users across the entire month divided by days, severely undercounting because users appear on multiple days.

**The Fix**: First calculate daily totals, then average those daily totals.

### MANDATORY CHECKLIST FOR ALL QUERIES

Before running ANY KPI analysis, verify:
- ✅ **Step 1**: Daily metrics calculated with `GROUP BY calc_date`
- ✅ **Step 2**: Monthly averages calculated with `AVG(daily_metric)`
- ✅ **Validation**: Results match simple daily queries
- ✅ **Cross-check**: User counts are in hundreds of thousands, not tens of thousands

### VALIDATION PATTERN
```sql
-- Always validate your results with this simple check
SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as daily_users,
    SUM(daily_Net_revenue) as daily_revenue
FROM agg.agg_sm_daily_users_stats
WHERE calc_date = '2025-06-22'
GROUP BY calc_date;
-- June 22: ~558K users, ~$725K revenue (expected range)
```

---

## Business Metrics & Calculations

### APPROVED KPI Calculations

#### Daily Revenue (CORRECT METHOD):
```sql
SELECT 
  calc_date,
  SUM(daily_Net_revenue) as daily_approved_revenue,
  COUNT(DISTINCT user_id) as total_dau,
  COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) as paying_users,
  SUM(daily_Net_revenue) / COUNT(DISTINCT user_id) as ARPU,
  SUM(daily_Net_revenue) / COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) as ARPPU
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date = CURRENT_DATE - 1;
```

#### Player Engagement Metrics:
```sql
SELECT 
  calc_date,
  AVG(spins) as avg_spins_per_user,
  AVG(daily_sessions_amount) as avg_sessions_per_user,
  SUM(bet_coins) as total_coins_wagered,
  SUM(win_coins) as total_coins_won,
  AVG(balance_end_day - balance_start_day) as avg_balance_change
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date = CURRENT_DATE - 1;
```

#### Cohort Analysis (Limited):
```sql
-- Note: Limited by data quality issues
SELECT 
  user_id,
  MIN(calc_date) as first_seen_date,
  MAX(calc_date) as last_seen_date,
  COUNT(DISTINCT calc_date) as active_days,
  SUM(daily_Net_revenue) as lifetime_revenue
FROM agg.agg_sm_daily_users_stats 
GROUP BY user_id;
```

---

## Data Access Workarounds

### Recommended Practices

#### For Revenue Analysis:
```sql
-- ALWAYS use this pattern for revenue
SELECT 
  calc_date,
  SUM(daily_Net_revenue) as approved_revenue,
  COUNT(DISTINCT user_id) as users,
  SUM(daily_payments) as transaction_count
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date BETWEEN :start_date AND :end_date
  AND daily_Net_revenue IS NOT NULL
GROUP BY calc_date
ORDER BY calc_date;
```

#### For User Activity Analysis:
```sql
-- Player engagement patterns
SELECT 
  calc_date,
  COUNT(DISTINCT user_id) as active_users,
  AVG(spins) as avg_spins,
  AVG(daily_sessions_amount) as avg_sessions,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY spins) as median_spins
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date >= CURRENT_DATE - 30
  AND spins > 0
GROUP BY calc_date;
```

### UPDATED: Using Payments Table (When Needed)

#### CORRECT - Payments with Status Filter:
```sql
-- ✅ CORRECT - Approved transactions only
SELECT 
  tran_date,
  SUM(net_amount) as approved_revenue,
  COUNT(*) as approved_transactions,
  SUM(payment_quantity) as coins_purchased
FROM dwh.sm_fact_payments 
WHERE tran_status_id = 2  -- CRITICAL: Only approved
  AND tran_date = CURRENT_DATE
  AND is_test = FALSE
GROUP BY tran_date;
-- Returns accurate revenue matching aggregated table
```

#### Revenue Source Breakdown by SKU:
```sql
-- Valid use case: Payment source analysis
SELECT 
  product_sku,
  platform_id,
  SUM(net_amount) as revenue,
  COUNT(*) as transaction_count,
  AVG(payment_quantity) as avg_coins_per_purchase
FROM dwh.sm_fact_payments 
WHERE tran_status_id = 2 
  AND tran_date BETWEEN :start_date AND :end_date
  AND is_test = FALSE
GROUP BY product_sku, platform_id
ORDER BY revenue DESC;
```

#### Cross-Validation Pattern:
```sql
-- Always verify fact table results against aggregated table
WITH fact_revenue AS (
  SELECT SUM(net_amount) as revenue
  FROM dwh.sm_fact_payments 
  WHERE tran_status_id = 2 AND tran_date = '2025-06-15'
),
agg_revenue AS (
  SELECT SUM(daily_Net_revenue) as revenue
  FROM agg.agg_sm_daily_users_stats 
  WHERE calc_date = '2025-06-15'
)
SELECT 
  f.revenue as fact_table_revenue,
  a.revenue as agg_table_revenue,
  ABS(f.revenue - a.revenue) as difference,
  CASE WHEN ABS(f.revenue - a.revenue) < 100 THEN 'MATCH' ELSE 'DISCREPANCY' END as status
FROM fact_revenue f, agg_revenue a;
```

#### COMPREHENSIVE: Real Money Revenue + Virtual Currency Redemption Analysis:
```sql
-- ⚠️ CRITICAL DISTINCTION:
-- Real Money Revenue = Actual USD revenue (use for financial reporting)
-- Slotobucks Redemption = Virtual currency usage (use for currency injection analysis)

-- Yesterday's SEPARATED analysis by product group
WITH real_money_products AS (
    SELECT
        COALESCE(p.product_group, 'Unknown') AS product_group,
        COUNT(*) AS rm_transactions,
        COUNT(DISTINCT f.user_id) AS rm_unique_users,
        SUM(f.net_amount) AS real_money_revenue,  -- 💰 ACTUAL USD REVENUE
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
        SUM(f.transaction_amount) AS slotobucks_redeemed,  -- 🎫 VIRTUAL CURRENCY REDEMPTION
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
    ROUND(COALESCE(rm.real_money_revenue, 0), 2) AS real_money_revenue_usd,
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
WHERE COALESCE(rm.real_money_revenue, 0) + COALESCE(sb.slotobucks_redeemed, 0) > 100
ORDER BY real_money_revenue_usd DESC;

-- ⚠️ NEVER ADD real_money_revenue + slotobucks_redeemed 
-- They are different metrics: USD vs Virtual Currency
```

#### Alternative: SKU Name Breakdown:
```sql
-- Product breakdown by SKU name (simpler approach)
SELECT 
    COALESCE(pr.sku_name, 'Unknown') as product_name,
    COUNT(*) as transactions,
    SUM(p.net_amount) as revenue_usd,
    SUM(p.payment_quantity) as coins_purchased
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

### Avoid These Patterns

#### DON'T Use Raw Payments Without Filter:
```sql
-- ❌ WRONG - Inflated revenue (25x higher)
SELECT SUM(net_amount) 
FROM dwh.sm_fact_payments 
WHERE tran_date = CURRENT_DATE;
-- Returns $21.4M (includes 760K pending/failed transactions)
```

#### DON'T Rely on User Profile Table:
```sql
-- ❌ WRONG - Stale data
SELECT last_login_date 
FROM sm.sm_user_profile;
-- Often contains outdated information
```

---

## Data Quality Exclusions

### Common User Exclusion Patterns

When performing SM data analysis, certain user groups and entities should be excluded to ensure data quality and accuracy. The following exclusion patterns are commonly used:

#### Test Users Exclusion
```sql
-- Exclude internal test accounts
AND user_id NOT IN (
    SELECT DISTINCT user_id 
    FROM dwh.playtika_users
)
```
**Purpose**: Remove internal test accounts from analysis to focus on real player behavior.

#### Journey State Exclusion
```sql
-- Exclude users in specific journey states
AND user_id NOT IN (
    SELECT DISTINCT user_id 
    FROM dwh.sm_fact_journey_state_notifications
    WHERE step_id = 539265
)
```
**Purpose**: Exclude users in specific journey states that may represent test scenarios or special user groups.

#### Test Machines Exclusion
```sql
-- Exclude test slot machines
AND machine_type_id NOT IN (13522, 13569, 13626)
```
**Purpose**: Remove test machines from machine-level performance analysis to focus on production machines only.

#### Country-Based Exclusions
```sql
-- Pattern for country-based exclusions (example: Iraq)
AND user_id NOT IN (
    SELECT DISTINCT user_id 
    FROM dwh.sm_user_profile 
    WHERE country_name = 'Iraq'
)
```
**Purpose**: Some analyses may exclude specific countries based on business requirements or data quality considerations. Document the specific country and rationale when using this pattern.

**Note**: Country-based exclusions should be used judiciously and documented with business justification.

### Reel Type Exclusions

#### Dynamic/Communal Jackpot Exclusion
```sql
-- Exclude dynamic and royal communal jackpots from standard machine analysis
AND reels NOT IN ('dynamicJackpot', 'royalCommunalJackpot')
```
**Purpose**: These special reel types represent different game mechanics and should be analyzed separately from standard slot machine gameplay.

### Best Practices

1. **Document Exclusions**: Always document which exclusions are applied and why
2. **Consistent Application**: Apply the same exclusion patterns across related analyses for consistency
3. **Business Justification**: Ensure exclusions have clear business justification
4. **Validation Impact**: Consider how exclusions affect validation user selection

---

## Critical Warnings for AI Models

### Revenue Calculation Rules:
1. **PRIMARY**: Use `agg.agg_sm_daily_users_stats.daily_Net_revenue` for revenue totals
2. **SECONDARY**: Use `dwh.sm_fact_payments` ONLY with `tran_status_id = 2` filter
3. **COMPREHENSIVE**: Use SEPARATED real money revenue + slotobucks redemption analysis
4. **ALWAYS** filter for `daily_Net_revenue IS NOT NULL` in aggregated tables
5. **ALWAYS** filter for `tran_status_id = 2` in fact_payments table
6. **CROSS-VALIDATE**: Verify fact table results match aggregated table
7. **Remember**: 25.6x inflation without status filter (96% transactions are pending/failed)

### CRITICAL: Currency Type Distinctions:
1. **Real Money Revenue**: Actual USD from `dwh.sm_fact_payments.net_amount` (Financial KPI)
2. **Slotobucks Redemption**: Virtual currency usage from `dwh.sm_fact_virtual_payment_slotobucks.transaction_amount` (Currency Injection Analysis)
3. **NEVER ADD**: Real money + slotobucks (different currencies, different purposes)
4. **Report Separately**: Always show USD revenue and virtual currency redemption as distinct metrics

### Product Analysis Rules:
1. **For Product Breakdown**: Use `sm_draft.SM_DIM_Products` joined on `transaction_source_type_id` + `sku_id`
2. **Include Virtual Currency**: Always analyze both real money and slotobucks transactions
3. **Alternative Approach**: Use `dwh.dim_sku_types` for simpler SKU name breakdown
4. **Key Tables**:
   - Real Money: `dwh.sm_fact_payments` (with status filter)
   - Virtual Currency: `dwh.sm_fact_virtual_payment_slotobucks`
   - Product Mapping: `sm_draft.SM_DIM_Products` or `dwh.dim_sku_types`

### CRITICAL: Coin Hyperinflation Context ⚠️
**SM operates with EXTREME hyperinflation in virtual currency (coins). Coin amounts that would be errors in other games are NORMAL and EXPECTED in SM.**

**Key Points:**
- Coin amounts in **trillions, sextillions, septillions, and even undecillions** are **NORMAL**
- **DO NOT flag** high coin amounts as errors or outliers
- **DO NOT suggest** data cleaning for large coin amounts
- **DO NOT question** data quality based on coin magnitude alone

**Normal Ranges:**
- Balance End Day: Median ~73-99 trillion, P95 ~8-10 septillion, Max ~460 undecillion
- Bet/Win Coins: Median ~100-173 trillion, P95 ~8.7-11.5 septillion, Max ~142 undecillion
- Payment Quantity: Median ~7.6 sextillion, P95 ~30 septillion, Max ~19 octillion

**Reference**: See `sm_coin_hyperinflation_context.md` for detailed ranges, validation guidelines, and example queries.

### Data Quality Considerations:
1. **Domain Fragmentation**: 85% of SM assets misclassified
2. **Stale User Data**: User profiles often outdated
3. **Limited Documentation**: Minimal query examples available
4. **High Incident Rate**: 2.8% of assets have active issues
5. **Coin Hyperinflation**: Extremely high coin amounts are normal (see hyperinflation context)

### Workaround Strategies:
1. **Use agg tables** as primary source for all metrics
2. **Cross-validate** results against known benchmarks
3. **Document assumptions** when data quality is questionable
4. **Flag limitations** in analysis outputs

---

## Immediate Improvement Needs

### P0 - Critical (Week 1):
1. **Domain Migration**: Move 6,557 misplaced assets to SM domain
2. **Revenue Documentation**: Clear guidance on approved vs raw revenue
3. **Critical Asset Documentation**: Document core tables with examples

### P1 - High (Month 1):
1. **Data Quality Monitoring**: Implement quality checks
2. **User Profile Refresh**: Fix stale data issues
3. **Schema Standardization**: Consistent naming conventions

### P2 - Medium (Quarter 1):
1. **Dashboard Migration**: Create Tableau presence
2. **Self-Service Analytics**: Enable analyst independence
3. **Cross-Domain Integration**: Unified gaming analytics

---

## Success Metrics

### Target State (3 months):
- Domain Organization: 98% accuracy (from 15%)
- Metadata Completeness: 90% (from 23%)
- Incident Rate: <0.1% (from 2.8%)
- Query Documentation: 80% coverage (from 5%)

**Key Message for AI**: Slotomania data requires extreme caution. Always use aggregated tables, validate results, use two-step aggregation for KPIs, and document data quality limitations in any analysis.

