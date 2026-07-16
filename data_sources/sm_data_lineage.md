# Slotomania (SM) - Data Lineage & Relationships

## Overview
This document describes the data flows, table relationships, and dependencies for Slotomania data analysis. Understanding data lineage is critical for accurate analysis and validation.

## Data Flow Architecture

### Revenue Pipeline

#### Primary Flow (RECOMMENDED):
```
Game Purchase Events 
  → Payment Processing System
  → dwh.sm_fact_payments (raw transactions)
  → Daily Aggregation Process
  → agg.agg_sm_daily_users_stats (approved revenue only)
  → Business Intelligence & Reporting
```

**Key Points:**
- `dwh.sm_fact_payments` contains ALL transactions (pending, approved, failed)
- Only approved transactions (`tran_status_id = 2`) flow to aggregated table
- Aggregated table is the AUTHORITATIVE source for revenue
- ~96% of transactions in fact table are pending/failed (excluded from aggregation)

#### Virtual Currency Flow:
```
Slotobucks Redemption Events
  → Virtual Payment Processing
  → dwh.sm_fact_virtual_payment_slotobucks (redemption transactions)
  → Coin Injection to User Accounts
  → User Activity Tracking
  → agg.agg_sm_daily_users_stats (activity metrics)
```

**Key Points:**
- Virtual currency redemptions are separate from real money revenue
- Slotobucks redemption injects coins into user accounts
- Tracked separately for economy balance analysis
- NEVER mix with real money revenue calculations

### User Activity Pipeline

#### Engagement Flow:
```
User Game Sessions
  → Spin Events & Gameplay
  → Activity Aggregation
  → agg.agg_sm_daily_users_stats (daily user metrics)
  → User Segmentation
  → dwh.sm_user_profile_datamining_snapshot (CZ deluxe segments)
```

**Key Points:**
- Daily user stats aggregated from real-time events
- User attributes updated in snapshot tables
- CZ deluxe segments calculated from engagement patterns
- Balance tracking includes start/end of day snapshots

### Bonus & Promotion Pipeline

#### Bonus Distribution Flow:
```
Bonus Events (Promotions, Rewards, etc.)
  → Bonus Processing System
  → dwh.fact_sm_bonus_history (bonus tracking)
  → Coin Injection to User Accounts
  → User Activity Impact
  → agg.agg_sm_daily_users_stats (bonus coins metrics)
```

**Key Points:**
- Bonuses can be transaction-linked or standalone
- Transaction-linked bonuses: `transaction_id IS NOT NULL`
- Standalone bonuses: `transaction_id IS NULL`
- Tracked separately for consumption analysis

## Table Relationships

### Primary Relationships

#### Revenue Tables:
```
agg.agg_sm_daily_users_stats (user_id, calc_date)
  ← dwh.sm_fact_payments (user_id, tran_date)
    → sm_draft.SM_DIM_Products (sku_id, transaction_source_type_id)
    → dwh.dim_sku_types (sku_id, transaction_source_type_id)
```

**Join Logic:**
- Revenue aggregation: `dwh.sm_fact_payments` → `agg.agg_sm_daily_users_stats` (by user_id and date)
- Product mapping: Join on `sku_id` + `transaction_source_type_id`
- Date alignment: `tran_date` in payments aligns with `calc_date` in aggregated stats

#### User Attribute Tables:
```
agg.agg_sm_daily_users_stats (user_id, calc_date)
  ← dwh.sm_user_profile_datamining_snapshot (user_id, snapshot_insert_ts)
    → sm.sm_user_profile (user_id) [LIMITED USE - STALE DATA]
```

**Join Logic:**
- Snapshot join: `user_id` + `DATE(snapshot_insert_ts) = calc_date`
- Profile join: `user_id` only (use with caution due to stale data)
- CZ deluxe segments: From snapshot table, not profile table

#### Virtual Currency Tables:
```
dwh.sm_fact_virtual_payment_slotobucks (user_id, tran_date)
  → sm_draft.SM_DIM_Products (sku_id, transaction_source_type_id)
  → Coin Injection Impact
  → agg.agg_sm_daily_users_stats (balance_end_day, activity metrics)
```

**Join Logic:**
- Product mapping: Same as real money payments
- Date alignment: `tran_date` aligns with `calc_date`
- Balance impact: Tracked in daily stats balance fields

#### Bonus Tables:
```
dwh.fact_sm_bonus_history (user_id, bonus_date)
  → Coin Injection Impact
  → agg.agg_sm_daily_users_stats (daily_bonus_coins, balance metrics)
  ← dwh.sm_fact_payments (transaction_id) [for transaction-linked bonuses]
```

**Join Logic:**
- Transaction-linked: `transaction_id` links to payment transactions
- Standalone: `transaction_id IS NULL` for non-transaction bonuses
- Date alignment: `bonus_date` aligns with `calc_date`

### Dimension Tables

#### Product Dimensions:
```
sm_draft.SM_DIM_Products
  - Primary Key: (sku_id, transaction_source_type_id)
  - Provides: product_group, sku_name, product categorization
  
dwh.dim_sku_types
  - Primary Key: (sku_id, transaction_source_type_id)
  - Provides: sku_name (simpler alternative)
```

**Usage:**
- Use `SM_DIM_Products` for comprehensive product analysis
- Use `dim_sku_types` for simple SKU name lookups
- Always join on BOTH `sku_id` AND `transaction_source_type_id`

#### Coin Value Dimensions:
```
dwh.Dim_Coins_Value
  - Dimensions: level_id, tier_id, denomination, platform
  - Provides: value multipliers, coin value calculations
```

**Usage:**
- Used for value-for-money calculations
- Level and tier-based multipliers
- Platform-specific pricing

## Critical Business Rules

### Revenue Calculation Rules

#### Rule 1: Approved Transactions Only
- **Source**: `dwh.sm_fact_payments`
- **Filter**: `tran_status_id = 2` (MANDATORY)
- **Additional Filters**: `is_test = 0`, `artificial_ind = 0`
- **Result**: Matches `agg.agg_sm_daily_users_stats.daily_Net_revenue`

#### Rule 2: Aggregated Table Authority
- **Primary Source**: `agg.agg_sm_daily_users_stats.daily_Net_revenue`
- **Use For**: All revenue totals and KPIs
- **Cross-Validation**: Verify against filtered fact table

#### Rule 3: Currency Separation
- **Real Money**: `dwh.sm_fact_payments.net_amount` (USD)
- **Virtual Currency**: `dwh.sm_fact_virtual_payment_slotobucks.transaction_amount` (Virtual)
- **NEVER ADD**: These are different currencies with different purposes

### Aggregation Rules

#### Rule 4: Two-Step Aggregation (MANDATORY)
- **Step 1**: Calculate daily metrics with `GROUP BY calc_date`
- **Step 2**: Average daily metrics for period comparisons
- **Reason**: Prevents 8-10x undercounting of users

#### Rule 5: Date Alignment
- **Aggregated Stats**: Use `calc_date` (business calculation date)
- **Payments**: Use `tran_date` (transaction processing date)
- **Snapshots**: Use `DATE(snapshot_insert_ts)` for date alignment
- **Alignment**: Join on `user_id` + aligned date fields

### User Segmentation Rules

#### Rule 6: CZ Deluxe Segmentation
- **Source**: `dwh.sm_user_profile_datamining_snapshot.cz_deluxe_weekly_update`
- **Join**: `user_id` + `DATE(snapshot_insert_ts) = calc_date`
- **Segments**: 0-5, 5-10, 10-20, 20-40, 40-60, 60-80, 80-100, +100

#### Rule 7: VIP Tier Segmentation
- **Source**: `dwh.sm_user_profile_datamining_snapshot.tier_id` or `dwh.Dim_Coins_Value.tier_id`
- **Tiers**: 1-4 (lower), 4+ (higher)
- **Usage**: Tier-based multipliers and value calculations

### Data Quality Rules

#### Rule 8: Test User Exclusion
- **Filter**: `is_test = 0` in payment tables
- **Filter**: Exclude test countries (e.g., `country_name != 'Iraq'`)
- **Purpose**: Ensure production data only

#### Rule 9: Stale Data Handling
- **Avoid**: `sm.sm_user_profile` for real-time analysis
- **Use**: `dwh.sm_user_profile_datamining_snapshot` for current attributes
- **Note**: Profile table often has outdated `last_login_date`

## Data Dependencies

### Critical Dependencies

#### Revenue Analysis Dependencies:
1. **Primary**: `agg.agg_sm_daily_users_stats` (must be refreshed daily)
2. **Secondary**: `dwh.sm_fact_payments` (for detailed breakdowns)
3. **Product Mapping**: `sm_draft.SM_DIM_Products` or `dwh.dim_sku_types`
4. **Validation**: Cross-check between primary and secondary sources

#### User Segmentation Dependencies:
1. **Activity Data**: `agg.agg_sm_daily_users_stats` (engagement metrics)
2. **Attributes**: `dwh.sm_user_profile_datamining_snapshot` (CZ deluxe segments)
3. **Profile Data**: `sm.sm_user_profile` (limited use, stale data warning)

#### Economy Analysis Dependencies:
1. **Balance Data**: `agg.agg_sm_daily_users_stats` (balance_start_day, balance_end_day)
2. **Coin Injection**: `dwh.sm_fact_payments.payment_quantity` (real money)
3. **Virtual Currency**: `dwh.sm_fact_virtual_payment_slotobucks.payment_quantity`
4. **Bonus Injection**: `dwh.fact_sm_bonus_history.bonus_amount`
5. **Consumption**: `agg.agg_sm_daily_users_stats.bet_coins` (wagered)

### Refresh Dependencies

#### Daily Refresh Cycle:
1. **Real-time Events**: Game events, transactions, bonuses
2. **Hourly Processing**: Payment processing, status updates
3. **Daily Aggregation**: `agg.agg_sm_daily_users_stats` (refreshed daily)
4. **Daily Snapshots**: `dwh.sm_user_profile_datamining_snapshot` (refreshed daily)

#### Periodic Refresh:
1. **Product Dimensions**: `sm_draft.SM_DIM_Products` (updated when products change)
2. **SKU Dimensions**: `dwh.dim_sku_types` (updated when SKUs change)
3. **Coin Value Dimensions**: `dwh.Dim_Coins_Value` (updated when pricing changes)

## Common Join Patterns

### Revenue Analysis Joins:
```sql
-- Revenue with product breakdown
SELECT ...
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN dwh.sm_fact_payments p
    ON a.user_id = p.user_id 
    AND a.calc_date = p.tran_date
LEFT JOIN sm_draft.SM_DIM_Products pr
    ON p.sku_id = pr.sku_id
    AND p.transaction_source_type_id = pr.transaction_source_type_id
WHERE p.tran_status_id = 2
```

### User Segmentation Joins:
```sql
-- User stats with CZ deluxe segments
SELECT ...
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN dwh.sm_user_profile_datamining_snapshot s
    ON a.user_id = s.user_id
    AND a.calc_date = DATE(s.snapshot_insert_ts)
```

### Economy Analysis Joins:
```sql
-- Balance and consumption analysis
SELECT ...
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN dwh.fact_sm_bonus_history b
    ON a.user_id = b.user_id
    AND a.calc_date = b.bonus_date
```

## Data Quality Considerations

### Known Issues:
1. **Domain Fragmentation**: 85% of SM assets misclassified across domains
2. **Stale Profile Data**: `sm.sm_user_profile` often outdated
3. **Transaction Status**: 96% of transactions pending/failed (must filter)
4. **Data Completeness**: Some tables have missing or incomplete data

### Workarounds:
1. **Use Aggregated Tables**: Primary source for all metrics
2. **Cross-Validate**: Always verify fact table results against aggregated table
3. **Document Limitations**: Flag data quality issues in analysis
4. **Use Snapshots**: Prefer snapshot tables over profile tables for current data

## Validation Patterns

### Revenue Validation:
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
    ABS(f.revenue - a.revenue) as difference
FROM fact_revenue f, agg_revenue a;
```

### User Count Validation:
```sql
-- Validate user counts are reasonable (hundreds of thousands, not tens of thousands)
SELECT 
    calc_date,
    COUNT(DISTINCT user_id) as daily_users
FROM agg.agg_sm_daily_users_stats
WHERE calc_date = :date
GROUP BY calc_date;
-- Expected: ~500K-700K users per day
```

This data lineage document provides the foundation for understanding SM data relationships and ensuring accurate analysis.

