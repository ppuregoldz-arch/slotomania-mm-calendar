# **SLOTOMANIA (SM) - ANALYST DATA CONTEXT**
*AI-Optimized Daily Analysis Guide for Cursor*

## **🎯 QUICK START FOR ANALYSTS**

**Revenue Authority**: `agg.agg_sm_daily_users_stats.daily_Net_revenue` (ONLY trusted source)  
**Payment Filter**: ALWAYS use `tran_status_id = 2` in `dwh.sm_fact_payments`  
**User Exclusions**: Iraq users, test users, Playtika employees (see patterns below)  
**Primary Key**: `user_id` across all tables  
**Date Range**: Most analyses use 30-180 days for performance
**SQL**: Never use CTE in queries

---

## **📊 CORE TABLES & USAGE PATTERNS**

### **📏 CONVERSION RATE CALCULATIONS**
**Default Format**: Decimal ratio (0.0 - 1.0), NOT percentage  
**Formula**: `feature_users / dau` (no * 100 multiplication)  
**Example**: 0.55 means 55% conversion, but store as decimal  
**Only multiply by 100**: When explicitly requested for percentage display

### **🔄 DIMENSIONS vs METRICS**
**Dimensions**: Categorical grouping fields used in GROUP BY clauses
- Examples: `promo_date`, `clan_size`, `user_tier`, `product_category`
- Purpose: Define what to group/segment data by
- SQL Usage: `GROUP BY dimension_field`

**Metrics**: Quantitative measures calculated from data
- Examples: `dau`, `revenue`, `conversion_rate`, `store_bonus_collectors`
- Purpose: Numbers to analyze and compare across dimensions
- SQL Usage: `SUM()`, `COUNT()`, `AVG()` aggregations

**Key Distinction**: "Make X a dimension" = GROUP BY X, not add X as another metric

### **🥇 PRIMARY: `agg.agg_sm_daily_users_stats`**
**Purpose**: Daily user aggregated metrics - YOUR GO-TO TABLE  
**Grain**: user_id + calc_date  
**Refresh**: Daily

### **🎯 PROMO DATE AGGREGATION: `agg.agg_sm_daily_promotion_stats`**
**Purpose**: Daily promotion-level user aggregated metrics  
**Grain**: user_id + promo_date  
**Key Difference**: Use this for promo date analysis instead of calc_date aggregation
**DAU Calculation**: `COUNT(DISTINCT user_id)` per promo_date
**When to Use**: Feature conversion rates, promo date performance analysis  

**Key Fields for Analysis**:
```sql
-- Revenue & Monetization
daily_Net_revenue       DECIMAL      -- 🚨 ONLY trusted revenue source
daily_gross_rev         DECIMAL      -- Gross before adjustments
daily_payments          INTEGER      -- Transaction count
is_paying_user          BOOLEAN      -- Made any purchase this day

-- Player Activity & Engagement  
spins                   INTEGER      -- Slot machine spins
bet_coins               DECIMAL      -- Virtual currency wagered
win_coins               DECIMAL      -- Virtual currency won
balance_start_day       DECIMAL      -- Starting coin balance
balance_end_day         DECIMAL      -- Ending coin balance
daily_sessions_amount   INTEGER      -- Game sessions
actual_median_bet       DECIMAL      -- Median bet size

-- Premium Currency & Features
gems_end_of_day_balance DECIMAL      -- Premium currency balance
daily_bonus_coins       DECIMAL      -- Bonus coins received

-- User Characteristics
first_session_tier      INTEGER      -- Player progression tier
last_session_tier       INTEGER      -- Current progression tier
level_id               INTEGER      -- Player level
```

**✅ STANDARD DAILY QUERY PATTERN**:
```sql
SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as dau,
    SUM(daily_Net_revenue) as total_revenue,
    COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) as paying_users,
    SUM(spins) as total_spins,
    SUM(bet_coins) as total_bet_coins,
    SUM(win_coins) as total_win_coins,
    ROUND(SUM(daily_Net_revenue) / COUNT(DISTINCT user_id), 2) as arpu,
    ROUND(SUM(win_coins) / SUM(bet_coins) * 100, 2) as win_rate_pct
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date >= CURRENT_DATE - 30
    AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_user_profile WHERE country_name = 'Iraq')
GROUP BY calc_date 
ORDER BY calc_date;
```

### **💳 SECONDARY: `dwh.sm_fact_payments`** 
**Purpose**: Individual payment transactions  
**⚠️ CRITICAL**: Must filter `tran_status_id = 2` (approved only)  
**Grain**: Individual transaction

**Key Fields**:
```sql
tran_date               DATE         -- Transaction date
user_id                 INTEGER      -- Player identifier
net_amount              DECIMAL      -- Revenue after fees
gross_amount            DECIMAL      -- Revenue before fees
payment_quantity        DECIMAL      -- Coins purchased
tran_status_id          INTEGER      -- 🚨 MUST = 2 (approved)
sku_id                  INTEGER      -- Product identifier
transaction_source_type_id INTEGER   -- Platform identifier
price                   DECIMAL      -- USD price
level_id               INTEGER      -- Player level at purchase
tier_id                INTEGER      -- Player tier at purchase
is_test                BOOLEAN      -- Test transaction flag
artificial_ind         BOOLEAN      -- Artificial transaction flag
is_ftd_platform        BOOLEAN      -- First-time deposit flag
```

**✅ SAFE PAYMENT ANALYSIS PATTERN**:
```sql
SELECT 
    tran_date,
    COUNT(*) as approved_transactions,
    SUM(net_amount) as revenue,
    COUNT(DISTINCT user_id) as paying_users,
    SUM(payment_quantity) as coins_sold
FROM dwh.sm_fact_payments 
WHERE tran_status_id = 2  -- 🚨 CRITICAL FILTER
    AND is_test = 0
    AND artificial_ind = 0
    AND tran_date >= CURRENT_DATE - 30
GROUP BY tran_date;
```

**❌ NEVER DO THIS** (25x revenue inflation):
```sql
-- This will return $21M instead of $836K due to pending transactions
SELECT SUM(net_amount) FROM dwh.sm_fact_payments WHERE tran_date = '2025-06-15';
```

### **🎰 GAME ACTIVITY: `dwh.fact_sm_spin_history_kafka`**
**Purpose**: Individual slot machine spins  
**Grain**: Individual spin event

**Key Fields**:
```sql
user_id                 INTEGER      -- Player identifier
spin_date               DATE         -- Spin date
machine_type_id         INTEGER      -- Slot machine identifier
bet_amount              INTEGER      -- Coins wagered
win_amount              INTEGER      -- Coins won
raw_bet_amount          INTEGER      -- Original bet amount
antebet_amounts_*       INTEGER      -- Feature bet amounts (SlotoQuest, MegaPods, etc.)
```

### **🎁 BONUS SYSTEM: `dwh.fact_sm_bonus_history`**
**Purpose**: Bonus coin distributions  
**Grain**: Individual bonus event

**Key Fields**:
```sql
user_id                 INTEGER      -- Player identifier
bonus_date              DATE         -- Bonus distribution date
bonus_amount            DECIMAL      -- Coins awarded
bonus_type_id           INTEGER      -- Bonus category
transaction_id          STRING       -- Purchase-linked bonus (if applicable)
```

### **👥 CLAN SYSTEM TABLES**

#### **📊 `dwh.sm_clan_profile` - Clan Creation & Current State**
**Purpose**: Clan metadata with accurate creation timestamps and current status  
**Grain**: One record per clan
**Update**: Actively maintained with current data

**🔗 Related Tables**:
- `dwh.sm_clans_datamining` - Clan parameters and analytics (see below)

**Key Fields**:
```sql
clan_id                 VARCHAR      -- Clan identifier
clan_name               VARCHAR      -- Clan name
clan_creation_ts        TIMESTAMP    -- 🎯 ACCURATE clan creation timestamp
clan_type               VARCHAR      -- PUBLIC/PRIVATE
admin_user_id           BIGINT       -- Clan creator/admin user
members_count           INTEGER      -- Current member count
member_capacity         INTEGER      -- Maximum allowed members
clan_rank               INTEGER      -- Current clan ranking
updated_ts              TIMESTAMP    -- Last update timestamp
```

#### **👤 `dwh.sm_clan_user_profile` - Current Clan Membership**
**Purpose**: Current clan membership status (snapshot)  
**Grain**: One record per user currently in a clan

**Key Fields**:
```sql
user_id                 INTEGER      -- Player identifier
clan_id                 VARCHAR      -- Current clan identifier
join_clan_ts            TIMESTAMP    -- When user joined current clan
clan_role               VARCHAR      -- MEMBER/ADMIN role
source_of_join          VARCHAR      -- How user joined (Invite/List/etc.)
join_clan_tier_id       INTEGER      -- User tier when joined
previous_clan_id        VARCHAR      -- Previous clan (if any)
updated_ts              TIMESTAMP    -- Last update
```

#### **📈 `dwh.sm_fact_clan_user` - Clan Membership History**
**Purpose**: Historical clan join/leave events  
**Grain**: Individual clan join event
**Note**: 6-hour cooldown between clan movements allows multiple clans per day

**Key Fields**:
```sql
user_id                 INTEGER      -- Player identifier
join_clan_ts            TIMESTAMP    -- Clan join timestamp
clan_id                 INTEGER      -- Clan identifier (note: INTEGER type vs VARCHAR in profile tables)
-- Note: No leave_ts - new join implies previous clan exit
```

#### **📊 `dwh.sm_clans_datamining` - Comprehensive Clan Parameters & Analytics**
**Purpose**: Central datamining table with all clan parameter values and predictions  
**Grain**: One record per clan per day (event_date)
**Records**: 2M+ daily snapshots

**Key Structure**:
```sql
clan_id                      VARCHAR      -- Clan identifier
event_date                   DATE         -- Snapshot date
insert_ts                    TIMESTAMP    -- Record insertion timestamp
updated_ts                   TIMESTAMP    -- Last update timestamp
snapshot_insert_ts           TIMESTAMP    -- Snapshot creation timestamp

-- Clan Analytics Fields
clan_members                 INTEGER      -- Total clan members
active_members               INTEGER      -- Active clan members  
dead_clan                    INTEGER      -- Dead clan indicator
clan_clan_points_daily_predicted    NUMERIC -- Predicted daily points
clan_clan_points_weekly_predicted   NUMERIC -- Predicted weekly points
clan_tournament_prediction   NUMERIC      -- Tournament prediction

-- 35+ Clan Dash Parameters (clan_dash_daily_*)
-- All clan dash feature parameters stored as individual columns
```

**Usage Pattern**:
- **Clan-level parameters**: All parameters stored at clan level, not user level
- **User inheritance**: Users get parameter values through clan membership
- **Daily snapshots**: Current date for live analysis, historical for trends
- **Join pattern**: `clan_datamining` → `clan_user_profile` → user analysis

**Integration Example**:
```sql
-- Get current clan parameter values for users
SELECT u.user_id, u.clan_id, c.clan_dash_daily_[parameter_name]
FROM dwh.sm_clan_user_profile u
JOIN dwh.sm_clans_datamining c ON u.clan_id = c.clan_id  
WHERE c.event_date = current_date
```

**✅ CLAN CREATION ANALYSIS**:
```sql
-- Clan creation trends with current status
SELECT 
    date(clan_creation_ts) as creation_date,
    COUNT(*) as clans_created,
    AVG(members_count) as avg_current_members,
    COUNT(CASE WHEN members_count > 0 THEN 1 END) as active_clans
FROM dwh.sm_clan_profile
WHERE clan_creation_ts >= current_date - 30
GROUP BY date(clan_creation_ts)
ORDER BY creation_date;
```

**✅ CURRENT CLAN MEMBERSHIP ANALYSIS**:
```sql
-- Current clan membership status (use for snapshot analysis)
SELECT 
    clan_profile.clan_id,
    clan_profile.clan_name,
    clan_profile.clan_creation_ts,
    COUNT(DISTINCT user_profile.user_id) as current_members,
    clan_profile.member_capacity,
    clan_profile.clan_type
FROM dwh.sm_clan_profile clan_profile
LEFT JOIN dwh.sm_clan_user_profile user_profile 
    ON clan_profile.clan_id = user_profile.clan_id
GROUP BY 1, 2, 3, 5, 6
ORDER BY current_members DESC;
```

**✅ HISTORICAL CLAN MOVEMENT ANALYSIS**:
```sql
-- Last clan per user per day (handles multiple movements)
SELECT 
    user_id,
    date(join_clan_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as join_promo_date,
    clan_id
FROM dwh.sm_fact_clan_user
WHERE join_clan_ts >= current_date - 30
  AND join_clan_ts < current_date
  AND user_id > 0
  -- Standard user exclusions
  AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.playtika_users)
  AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_fact_journey_state_notifications WHERE step_id = 539265)
LIMIT 1 OVER (PARTITION BY user_id, date(join_clan_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') ORDER BY join_clan_ts DESC)
```

---

## **🧩 COMMON JOIN PATTERNS**

### **Product Information**:
```sql
-- Join payments with product names
FROM dwh.sm_fact_payments p
LEFT JOIN sm_draft.SM_DIM_Products prod
    ON p.sku_id = prod.sku_id 
    AND p.transaction_source_type_id = prod.transaction_source_type_id
```

### **Player Profiles** (Use with caution - often stale):
```sql
-- Join with user demographics
FROM agg.agg_sm_daily_users_stats stats
LEFT JOIN dwh.sm_user_profile_datamining_snapshot profile
    ON stats.user_id = profile.user_id 
    AND stats.calc_date = DATE(profile.snapshot_insert_ts)
```

### **Bonus Categories**:
```sql
-- Join bonuses with categories
FROM dwh.fact_sm_bonus_history bonus
LEFT JOIN sm_draft.SM_dim_Bonus_groups groups
    ON bonus.bonus_type_id = groups.bonus_type_id
```

---

## **🚫 CRITICAL USER EXCLUSIONS**

**Standard exclusion pattern used in all production queries**:
```sql
WHERE user_id > 0  -- Valid user IDs only
    AND user_id NOT IN (
        -- Iraq users (regulatory restriction)
        SELECT DISTINCT user_id FROM dwh.sm_user_profile 
        WHERE country_name = 'Iraq'
    )
    AND user_id NOT IN (
        -- Test users / internal accounts
        SELECT DISTINCT user_id FROM dwh.sm_fact_journey_state_notifications 
        WHERE step_id = 539265
    )
    AND user_id NOT IN (
        -- Playtika employees
        SELECT DISTINCT user_id FROM dwh.playtika_users
    )
```

---

## **📈 BUSINESS METRICS CALCULATIONS**

### **Daily Active Users (DAU)**:
```sql
SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as dau
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date = CURRENT_DATE - 1
    -- Add standard exclusions
```

### **Revenue Metrics**:
```sql
SELECT 
    calc_date,
    SUM(daily_Net_revenue) as total_revenue,
    COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) as paying_users,
    SUM(daily_Net_revenue) / COUNT(DISTINCT user_id) as arpu,
    SUM(daily_Net_revenue) / COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) as arppu,
    COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) / COUNT(DISTINCT user_id) * 100 as conversion_rate
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date = CURRENT_DATE - 1;
```

### **Player Engagement**:
```sql
SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT CASE WHEN spins > 0 THEN user_id END) as spinning_users,
    SUM(spins) / COUNT(DISTINCT CASE WHEN spins > 0 THEN user_id END) as avg_spins_per_spinner,
    SUM(daily_sessions_amount) / COUNT(DISTINCT user_id) as avg_sessions_per_user,
    ROUND(SUM(win_coins) / SUM(bet_coins) * 100, 2) as overall_win_rate_pct
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date = CURRENT_DATE - 1;
```

### **Virtual Currency Economy**:
```sql
-- Consumption Analysis
SELECT 
    calc_date,
    SUM(bet_coins - win_coins) as net_coin_consumption,
    SUM(daily_bonus_coins) as bonus_coins_distributed,
    SUM(bet_coins - win_coins) / SUM(daily_bonus_coins) as consumption_to_bonus_ratio
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date >= CURRENT_DATE - 7
GROUP BY calc_date;
```

---

## **🎯 SPECIALIZED ANALYSIS PATTERNS**

### **Player Behavior by Tier**:
```sql
SELECT 
    last_session_tier,
    COUNT(DISTINCT user_id) as users,
    PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY balance_end_day) as median_balance,
    PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY spins) as median_spins,
    PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY actual_median_bet) as median_bet_size
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date = CURRENT_DATE - 1
    AND last_session_tier >= 1
GROUP BY last_session_tier
ORDER BY last_session_tier;
```

### **Product Performance** (Value for Money):
```sql
SELECT 
    prod.Product_Name,
    COUNT(*) as transactions,
    SUM(p.gross_amount) as gross_revenue,
    SUM(p.payment_quantity) as coins_sold,
    SUM(p.payment_quantity) / SUM(p.gross_amount) as coins_per_dollar
FROM dwh.sm_fact_payments p
LEFT JOIN sm_draft.SM_DIM_Products prod
    ON p.sku_id = prod.sku_id 
    AND p.transaction_source_type_id = prod.transaction_source_type_id
WHERE p.tran_status_id = 2 
    AND p.is_test = 0
    AND p.artificial_ind = 0
    AND p.tran_date >= CURRENT_DATE - 30
GROUP BY prod.Product_Name
ORDER BY gross_revenue DESC;
```

### **Bonus Analysis by Type**:
```sql
SELECT 
    groups.Bonus_group,
    DATE(bonus_ts) as bonus_date,
    COUNT(DISTINCT b.user_id) as recipients,
    SUM(bonus_amount) as total_bonus_coins,
    CASE WHEN transaction_id IS NOT NULL THEN 'Purchase-Linked' ELSE 'Free' END as bonus_category
FROM dwh.fact_sm_bonus_history b
LEFT JOIN sm_draft.SM_dim_Bonus_groups groups
    ON b.bonus_type_id = groups.bonus_type_id
WHERE bonus_ts >= CURRENT_DATE - 30
    -- Add standard user exclusions
GROUP BY groups.Bonus_group, DATE(bonus_ts), CASE WHEN transaction_id IS NOT NULL THEN 'Purchase-Linked' ELSE 'Free' END
ORDER BY bonus_date DESC, total_bonus_coins DESC;
```

### **Churn Analysis**:
```sql
-- Users who haven't returned in 7+ days
WITH last_activity AS (
    SELECT 
        user_id,
        MAX(calc_date) as last_active_date,
        DATEDIFF('day', MAX(calc_date), CURRENT_DATE) as days_since_last_activity
    FROM agg.agg_sm_daily_users_stats 
    WHERE calc_date >= CURRENT_DATE - 60
    GROUP BY user_id
)
SELECT 
    CASE 
        WHEN days_since_last_activity <= 7 THEN 'Active (0-7 days)'
        WHEN days_since_last_activity <= 14 THEN 'At Risk (8-14 days)'
        WHEN days_since_last_activity <= 30 THEN 'Dormant (15-30 days)'
        ELSE 'Churned (30+ days)'
    END as user_status,
    COUNT(DISTINCT user_id) as user_count
FROM last_activity
GROUP BY CASE 
    WHEN days_since_last_activity <= 7 THEN 'Active (0-7 days)'
    WHEN days_since_last_activity <= 14 THEN 'At Risk (8-14 days)'
    WHEN days_since_last_activity <= 30 THEN 'Dormant (15-30 days)'
    ELSE 'Churned (30+ days)'
END;
```

---

## **⚠️ CRITICAL DATA WARNINGS**

### **🚨 Revenue Calculation Rules**:
1. **PRIMARY**: Always use `agg.agg_sm_daily_users_stats.daily_Net_revenue`
2. **SECONDARY**: If using `dwh.sm_fact_payments`, MUST filter `tran_status_id = 2`
3. **NEVER**: Use raw payments table without status filter (25x inflation)
4. **VALIDATION**: Cross-check results between both tables

### **🚨 Two-Step Aggregation Rule**:
For monthly averages, ALWAYS:
1. First calculate daily metrics (`GROUP BY calc_date`)
2. Then average the daily results (`AVG(daily_metric)`)

**❌ WRONG** (severe undercount):
```sql
SELECT COUNT(DISTINCT user_id) / COUNT(DISTINCT calc_date) as avg_dau
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date >= '2025-01-01';
```

**✅ CORRECT**:
```sql
WITH daily_metrics AS (
    SELECT calc_date, COUNT(DISTINCT user_id) as daily_dau
    FROM agg.agg_sm_daily_users_stats 
    WHERE calc_date >= '2025-01-01'
    GROUP BY calc_date
)
SELECT AVG(daily_dau) as avg_dau FROM daily_metrics;
```

### **🚨 Virtual Currency Types**:
- **Coins**: Primary game currency (`bet_coins`, `win_coins`, `balance_end_day`)
- **Gems**: Premium currency (`gems_end_of_day_balance`)
- **SlotoBucks**: Special redemption currency (separate tables)

### **💎 Gems Source Categorization**:
When analyzing gems usage by source, group `transaction_source_type_name` using this CASE statement:

```sql
CASE
    WHEN transaction_source_type_name ILIKE '%machine%' OR transaction_source_type_name ILIKE '%spin%' 
         THEN 'machines'
    WHEN transaction_source_type_name ILIKE '%quest%' THEN 'quest'
    WHEN transaction_source_type_name ILIKE '%blast%' OR transaction_source_type_name ILIKE '%battle sheep%' 
         OR transaction_source_type_name ILIKE '%digging dog%' OR transaction_source_type_name ILIKE '%snl%' 
         OR transaction_source_type_name ILIKE '%pick%' THEN 'seasonals'
    WHEN transaction_source_type_name ILIKE '%shiny show%' OR transaction_source_type_name ILIKE '%sloto show%' 
         OR transaction_source_type_name ILIKE '%slotoshow%' THEN 'shiny show'
    WHEN transaction_source_type_name ILIKE '%gacha%' OR transaction_source_type_name ILIKE '%album factory%' 
         THEN 'album factory'
    WHEN transaction_source_type_name ILIKE '%slotoheroes%' THEN 'Figz/Globes'
    WHEN transaction_source_type_name ILIKE '%MWP%' THEN 'Pods'
    WHEN transaction_source_type_name ILIKE '%winovate%' THEN 'winovate'
    WHEN transaction_source_type_name ILIKE '%dash%' OR transaction_source_type_name ILIKE '%clan%' 
         THEN 'dash/clan'
    ELSE 'other'
END AS transaction_source_type_name_grouped
```

**Gems Analysis Table**: `dwh.sm_fact_internal_purchases`  
**Key Filter**: `currency_id = 10000` (gems only)  
**Source Join**: `LEFT JOIN dwh.dim_transaction_source_type USING (transaction_source_type_id)`

---

## **🔍 VALIDATION PATTERNS**

### **Cross-Validate Revenue**:
```sql
-- Both should match within $100
WITH agg_revenue AS (
    SELECT SUM(daily_Net_revenue) as revenue 
    FROM agg.agg_sm_daily_users_stats 
    WHERE calc_date = '2025-06-15'
),
fact_revenue AS (
    SELECT SUM(net_amount) as revenue 
    FROM dwh.sm_fact_payments 
    WHERE tran_status_id = 2 AND tran_date = '2025-06-15'
)
SELECT 
    a.revenue as agg_revenue,
    f.revenue as fact_revenue,
    ABS(a.revenue - f.revenue) as difference
FROM agg_revenue a, fact_revenue f;
```

### **Validate User Counts**:
```sql
-- Sanity check - SM typically has 500K-700K daily users
SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as dau
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date = CURRENT_DATE - 1;
-- Expected: ~558K users for recent dates
```

---

## **📋 DAILY REPORT QUERIES**

### **Executive Summary**:
```sql
-- Yesterday's key metrics
SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as dau,
    SUM(daily_Net_revenue) as revenue,
    COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) as paying_users,
    ROUND(SUM(daily_Net_revenue) / COUNT(DISTINCT user_id), 2) as arpu,
    ROUND(COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) / COUNT(DISTINCT user_id) * 100, 2) as conversion_rate_pct,
    SUM(spins) as total_spins,
    ROUND(SUM(win_coins) / SUM(bet_coins) * 100, 2) as win_rate_pct
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date = CURRENT_DATE - 1
    AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_user_profile WHERE country_name = 'Iraq')
GROUP BY calc_date;
```

### **Weekly Trending**:
```sql
-- Last 7 days trending
SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as dau,
    SUM(daily_Net_revenue) as revenue,
    LAG(SUM(daily_Net_revenue)) OVER (ORDER BY calc_date) as prev_day_revenue,
    ROUND((SUM(daily_Net_revenue) / LAG(SUM(daily_Net_revenue)) OVER (ORDER BY calc_date) - 1) * 100, 1) as revenue_change_pct
FROM agg.agg_sm_daily_users_stats 
WHERE calc_date >= CURRENT_DATE - 7
    AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_user_profile WHERE country_name = 'Iraq')
GROUP BY calc_date 
ORDER BY calc_date;
```

---

## **🛠️ CURSOR AI TIPS**

### **Quick Analysis Prompts**:
- "Show me yesterday's revenue and DAU for SM"
- "Compare this week vs last week revenue trends"
- "Analyze player behavior by tier for the last 30 days"
- "Show me the top performing products by revenue"
- "Calculate churn rate for different user segments"

### **Always Specify**:
- Date range (performance impact)
- User exclusions (Iraq, test users, employees)
- Revenue filter (`tran_status_id = 2` for payments)
- Validation needs (cross-check critical metrics)

### **Performance Tips**:
- Limit to 30-180 days for large queries
- Use `calc_date` for time filtering (indexed)
- Add user exclusions early in WHERE clause
- Use DISTINCT carefully (performance impact)

---

## **🚀 SUCCESS METRICS TO TRACK**

- **DAU**: 500K-700K (healthy range)
- **Revenue**: $600K-800K daily (typical range)
- **Conversion Rate**: 12-15% (paying users / total users)
- **Win Rate**: 85-95% (coins won / coins bet)
- **ARPU**: $1.00-1.50 (revenue per user)
- **ARPPU**: $8.00-12.00 (revenue per paying user)

---

*Remember: Always validate your queries with known data points and use the standard exclusion patterns. When in doubt, cross-reference with the aggregated table.* 