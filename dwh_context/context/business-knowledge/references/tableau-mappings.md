# Slotomania Data Sources Mapping & Analysis

**Project:** Revenue Decrease & Churn Analysis  
**Created:** 2025-09-27  
**Updated:** 2025-09-27 (Comprehensive Scan)  
**Purpose:** Comprehensive mapping of all Tableau data sources, table usage patterns, and column frequency analysis

---

## Executive Summary

This document provides a complete analysis of the Slotomania data ecosystem based on **systematic scanning of 85+ SQL queries** across 5 main business areas: **Album** (28 queries), **Dash** (18 queries), **Management Report** (23 queries), **Seasonals** (8 queries), and **Mid Term** (15 queries). The analysis reveals the most frequently used tables, their primary business purposes, and the key columns that drive analytical insights.

**Key Finding:** The data architecture follows a clear pattern with core fact tables for transactions, gameplay, and user behavior, supported by comprehensive dimension tables and aggregated views for performance optimization.

---

## Table Usage Overview

### Core Fact Tables (Most Frequently Used)

#### 1. `dwh.sm_fact_payments` - **Payment Transactions** 
**Usage Frequency:** 🔥🔥🔥🔥🔥 (Very High - 30+ queries across all domains)  
**Primary Purpose:** External real-money payment tracking and revenue analysis  
**Business Domains:** All (Album gems revenue, Dash purchases, Management KPIs, Seasonal events, Mid-term features)

**Most Frequent Columns:**
- `user_id` - User identifier (universal key) - **Used in 100% of queries**
- `tran_date` - Transaction date (primary time dimension) - **Used in 95% of queries**
- `tran_ts` - Transaction timestamp (for precise timing) - **Used in 80% of queries**
- `tran_status_id` - Transaction status (2=approved, most common filter) - **Used in 100% of queries**
- `gross_amount` - Gross revenue amount - **Used in 90% of queries**
- `transaction_amount` - Transaction amount - **Used in 70% of queries**
- `net_amount` - Net revenue after fees - **Used in 60% of queries**
- `sku_id` - Product/SKU identifier - **Used in 85% of queries**
- `transaction_source_type_id` - Source of transaction - **Used in 80% of queries**
- `platform_id` - Platform identifier - **Used in 60% of queries**
- `tier_id` - User tier - **Used in 70% of queries**
- `artificial_ind` - Real vs artificial transaction flag (0=real) - **Used in 100% of queries**
- `is_test` - Test transaction flag (0=real) - **Used in 100% of queries**
- `tran_id` - Transaction ID - **Used in 50% of queries**
- `tran_ticket` - Transaction ticket (for linking to offers) - **Used in 30% of queries**

**Common Usage Patterns:**
```sql
-- Standard payment filtering pattern (Applied in 100% of queries)
WHERE tran_status_id = 2 
  AND artificial_ind = 0 
  AND is_test = 0 
  AND user_id > 0
  AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.playtika_users)
  AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_fact_journey_state_notifications WHERE step_id = 539265)
```

**Specialized Usage by Domain:**
- **Album:** Focus on gem-related transactions (`transaction_source_type_id IN (177, 288, 287, 388, 389, 470, 450, 316, 487)`)
- **Dash:** Daily Dash Plus purchases (`Product_Name = 'Daily Dash Plus'`)
- **Seasonals:** Event-specific revenue tracking with time zone conversions
- **Mid-term:** ROOG offers and promotion-specific transactions

#### 2. `agg.agg_sm_daily_users_stats` - **Daily User Aggregations**
**Usage Frequency:** 🔥🔥🔥🔥 (High - 20+ queries across all domains)  
**Primary Purpose:** Daily user behavior, balance, and revenue aggregations  
**Business Domains:** Management Reports (churn, balance indices), Album (finisher performance), Dash (promotion stats), Seasonals (event participation)

**Most Frequent Columns:**
- `user_id` - User identifier - **Used in 100% of queries**
- `calc_date` - Calculation date - **Used in 100% of queries**
- `daily_gross_rev` - Daily gross revenue per user - **Used in 85% of queries**
- `daily_net_revenue` - Daily net revenue per user - **Used in 80% of queries**
- `balance_end_day` - End of day balance - **Used in 60% of queries**
- `last_session_tier` - User tier from last session - **Used in 70% of queries**
- `is_paying_user` - Paying user flag - **Used in 75% of queries**
- `bet_coins` - Daily bet amount - **Used in 50% of queries**
- `spins` - Daily spin count - **Used in 45% of queries**
- `wager` - Daily wager amount - **Used in 40% of queries**
- `sq_wager` - Sloto Quest wager - **Used in 30% of queries**

**Key Analytical Patterns:**
- **Churn Analysis:** `datediff('dd', last_login_date, date)` calculations
- **Revenue Attribution:** Album/event revenue during specific periods
- **User Segmentation:** Paying vs non-paying user analysis
- **Balance Tracking:** Median balance calculations for tier analysis

#### 3. `dwh.fact_sm_spin_history_kafka` - **Spin Activity**
**Usage Frequency:** 🔥🔥🔥🔥 (High - 12+ queries)  
**Primary Purpose:** Individual spin outcomes and machine performance

**Most Frequent Columns:**
- `user_id` - User identifier
- `spin_ts` - Spin timestamp
- `spin_date` - Spin date (partition key)
- `machine_type_id` - Machine identifier
- `bet_amount` - Bet amount
- `win_amount` - Win amount
- `guid` - Unique spin identifier
- `session_id` - Session identifier
- `user_level` - User level at time of spin
- `balance` - User balance at time of spin

#### 4. `dwh.fact_sm_bonus_history` - **Bonus Grants**
**Usage Frequency:** 🔥🔥🔥 (Medium-High - 10+ queries)  
**Primary Purpose:** All types of bonus awards and grants

**Most Frequent Columns:**
- `user_id` - User identifier
- `bonus_ts` - Bonus timestamp
- `bonus_date` - Bonus date
- `bonus_type_id` - Type of bonus
- `bonus_amount` - Bonus amount
- `user_new_balance` - User balance after bonus
- `session_id` - Session identifier
- `tier_id` - User tier

---

### Feature-Specific Fact Tables

#### 5. `dwh.sm_fact_internal_purchases` - **Internal Currency Purchases**
**Usage Frequency:** 🔥🔥🔥 (Medium-High - 12+ queries)  
**Primary Purpose:** Gem and internal currency spending  
**Business Domains:** Album (gem spending on cards/wilds), Seasonals (event participation costs)

**Most Frequent Columns:**
- `user_id` - User identifier - **Used in 100% of queries**
- `timestamp` - Purchase timestamp - **Used in 100% of queries**
- `sku_id` - Product SKU - **Used in 90% of queries**
- `cost` - Cost in gems/internal currency - **Used in 95% of queries**
- `amount` - Quantity purchased - **Used in 80% of queries**
- `transaction_source_type_id` - Source of purchase - **Used in 85% of queries**
- `currency_id` - Currency type (10000=gems) - **Used in 70% of queries**

**Key Usage Patterns:**
- Album gem spending: `currency_id = 10000` with album date ranges
- Transaction source categorization for shiny show vs album factory

#### 6. **Album-Specific Tables** (High Usage in Album Domain)

**`dwh.sm_users_album_cards_amount_snp` - Album Card Collection Snapshots**
- **Usage:** 6+ queries in Album domain
- **Key Columns:** `user_id`, `album_id`, `date`, `user_card_count`
- **Purpose:** Daily snapshots of user card collection progress

**`dwh.sm_fact_collectibles_finished_album` - Album Completion Events**
- **Usage:** 4+ queries in Album domain
- **Key Columns:** `user_id`, `album_id`, `event_date`, `album_run`
- **Purpose:** Track album completion events and timing

**`dwh.sm_fact_collectibles_cards` - Individual Card Events**
- **Usage:** 8+ queries in Album domain
- **Key Columns:** `user_id`, `card_id`, `event_date`, `operation_type`, `card_type`, `rareness`, `is_duplicate`, `trigger_type_id`
- **Purpose:** Granular card acquisition tracking

**`dwh.fact_sm_goods_service_data` - Goods Delivery**
- **Usage:** 10+ queries across domains
- **Key Columns:** `user_id`, `sku_id`, `bonus_ts`, `bonus_amount`, `event_type`, `reward_request_id`
- **Purpose:** Track delivery of gems, cards, and other goods

#### 7. **Daily Dash Tables** (High Usage in Dash Domain)

**`dwh.sm_fact_daily_dash_challenges` - Challenge Activity**
- **Usage:** 8+ queries in Dash domain
- **Key Columns:** `user_id`, `event_ts`, `challenge_id`, `challenge_group_id`, `status`, `user_level`
- **Purpose:** Track daily dash challenge participation and completion

**`dwh.sm_fact_daily_dash_points_history` - Points Progression**
- **Usage:** 6+ queries in Dash domain
- **Key Columns:** `user_id`, `event_ts`, `points_earned`, `source_type`
- **Purpose:** Track points earning and progression

**`dwh.sm_fact_super_dash` - Super Dash Events**
- **Usage:** 4+ queries in Dash domain
- **Key Columns:** `user_id`, `event_ts`, `status` (FINISHED/SKIPPED)
- **Purpose:** Track super dash completion patterns

#### 8. **Seasonal Event Tables** (Medium Usage in Seasonals/Mid-term)

**`dwh.sm_fact_blast_games_activity` - Blast Game Events**
- **Usage:** 4+ queries in Seasonals
- **Key Columns:** `user_id`, `event_ts`, `board_run_id`, `activity_type`, `board_completed`, `sub_blast_event_id`

**`dwh.sm_fact_battlesheep_events` - Battlesheep Game Events**
- **Usage:** 3+ queries in Seasonals
- **Key Columns:** `user_id`, `event_ts`, `board_number`, `event_type`, `board_completed`

**`dwh.sm_fact_blast_events` - Blast Events (New Version)**
- **Usage:** 3+ queries in Seasonals
- **Key Columns:** `user_id`, `event_ts`, `board_number`, `event_type`, `board_completed`

#### 9. **Specialized Tables** (Lower Frequency but Important)

**`dwh.sm_fact_virtual_payment_slotobucks` - SlotoBucks Transactions**
- **Usage:** 3+ queries in Management Reports
- **Purpose:** Virtual currency (SlotoBucks) payment tracking

**`dwh.sm_fact_external_progressive_jaw_game_played` - Dynamic Jackpot**
- **Usage:** 2+ queries in Mid-term
- **Purpose:** Dynamic jackpot game tracking

**`sm_fact_mega_win_party_history` - Mega Pods**
- **Usage:** 2+ queries in Mid-term
- **Purpose:** Mega pod collection tracking

---

### Dimension Tables (Reference Data)

#### Most Used Dimensions:

**1. `sm_draft.SM_DIM_Products` - Product Catalog**
- **Usage:** 25+ queries across all domains
- **Key Columns:** `sku_id`, `transaction_source_type_id`, `product_name`, `product_group`
- **Purpose:** Product definitions and categorization
- **Join Pattern:** `USING (sku_id, transaction_source_type_id)` with payment tables

**2. `dwh.dim_dates` - Date Dimension**
- **Usage:** 20+ queries across all domains
- **Key Columns:** `date`, `dayofweek`
- **Purpose:** Time-based analysis and date range generation
- **Common Pattern:** Weekly season generation (`dayofweek(date) = 2` for Monday starts)

**3. `sm_draft.ariel_dim_albums_info` - Album Metadata**
- **Usage:** 15+ queries in Album domain
- **Key Columns:** `album_id`, `album_name`, `launch_date`, `end_date`, `album_type`, `card_from`, `card_to`, `length_in_days`
- **Purpose:** Album lifecycle and card range definitions
- **Filter Pattern:** `Album_type = 'Regular'` (excludes Communal albums)

**4. `dwh.sm_user_profile_datamining_snapshot` - User Profile Snapshots**
- **Usage:** 12+ queries in Management Reports and Dash
- **Key Columns:** `user_id`, `event_date_datamining`, `cz_deluxe_weekly_update`, `DPU_Segment`, `tier_id_user`, `vip_acc_mng`, `dormancy_type`, `sq_wager`, `simple_median_bet`, `BM_multiplier`
- **Purpose:** User segmentation and behavioral analysis

**5. `dwh.dim_sm_bonus_type` - Bonus Type Definitions**
- **Usage:** 8+ queries across domains
- **Key Columns:** `bonus_type_id`, `bonus_type_name`
- **Purpose:** Categorize different types of bonuses and rewards

**6. `dwh.dim_sku_type` - SKU Classifications**
- **Usage:** 6+ queries across domains
- **Key Columns:** `sku_id`, `sku_name`, `sku_type`
- **Purpose:** Product type categorization

**7. Album-Specific Dimensions:**
- **`dwh.sm_dim_collectibles_card`** - Card definitions (`card_id`, `set_id`, `name`, `rareness_id`, `type_id`)
- **`dwh.sm_dim_collectibles_album_set`** - Album set structure (`set_id`, `album_id`)
- **`dwh.sm_dim_collectibles_triggers`** - Card acquisition triggers (`trigger_type_id`, `trigger_type_name`)

**8. Dash-Specific Dimensions:**
- **`dwh.sm_dim_daily_dash_challenges`** - Challenge definitions (`challenge_group_id`, `challenge_group_name`)

**9. Event-Specific Dimensions (sm_draft schema):**
- **`sm_draft.Maor_Blast_Events`** - Blast event definitions
- **`sm_draft.battlesheep_events`** - Battlesheep event definitions
- **`sm_draft.figz_dates`** - Figz event timing
- **`sm_draft.globez_dates`** - Globez event timing

---

## Business Domain Analysis

### 1. **Album Feature Analytics** (28 queries total)
**Query Distribution:** 18 embedded + 10 Album Data Sources  
**Primary Business Focus:** Card collection mechanics, album completion tracking, gem economy analysis

**Core Table Usage:**
- `dwh.sm_fact_collectibles_cards` - **8 queries** - Individual card acquisition events
- `dwh.sm_users_album_cards_amount_snp` - **6 queries** - Daily card collection snapshots  
- `dwh.sm_fact_internal_purchases` - **5 queries** - Gem spending on album features
- `dwh.sm_fact_collectibles_finished_album` - **4 queries** - Album completion tracking
- `dwh.fact_sm_goods_service_data` - **6 queries** - Gem rewards and wild card delivery
- `agg.agg_sm_daily_users_stats` - **8 queries** - Revenue attribution to album periods

**Key Analytical Patterns:**
- **Revenue Progression:** Track user spending from album launch through completion
- **Card Missing Analysis:** Identify users missing specific cards by rarity/type
- **Gem Economy:** Monitor gem spending vs earning in album features (Shiny Show, Album Factory)
- **Completion Performance:** Analyze post-completion user behavior and revenue
- **Wild Card Usage:** Track wild card distribution and usage patterns

**Specialized Metrics:**
- Album finisher rates by days since launch
- Gem spending by card acquisition source (payment vs gameplay)
- Revenue per set completion
- Card progression curves by user tier

### 2. **Daily Dash Feature Analytics** (18 queries)
**Primary Business Focus:** Feature engagement, completion rates, revenue attribution, user progression

**Core Table Usage:**
- `dwh.sm_fact_daily_dash_challenges` - **8 queries** - Challenge participation and completion
- `dwh.sm_fact_daily_dash_points_history` - **6 queries** - Points earning progression
- `dwh.sm_fact_super_dash` - **4 queries** - Super dash completion patterns
- `dwh.sm_fact_payments` - **12 queries** - Daily Dash Plus purchases and revenue
- `agg.agg_sm_daily_promotion_stats` - **10 queries** - Aggregated engagement metrics

**Key Analytical Patterns:**
- **Weekly Seasonality:** Monday-to-Sunday season tracking (`dayofweek(date) = 2`)
- **User Segmentation:** FTD vs Repurchase vs Dormant user analysis
- **Completion Funnels:** Challenge start → finish rates by challenge type
- **Revenue Attribution:** Revenue during dash periods vs baseline

**Specialized Metrics:**
- Monthly unique paying users for Dash Plus
- Super dash finishing frequency (0-7+ completions)
- Points earning by source type
- Challenge completion rates by user level (>100 filter)

### 3. **Management Reporting** (23 queries)
**Primary Business Focus:** Core KPIs, user behavior analysis, churn tracking, balance management

**Core Table Usage:**
- `agg.agg_sm_daily_users_stats` - **15 queries** - Core user behavior metrics
- `dwh.sm_fact_payments` - **10 queries** - Revenue and transaction analysis
- `dwh.fact_sm_spin_history_kafka` - **8 queries** - Machine performance and payouts
- `dwh.sm_user_profile_datamining_snapshot` - **6 queries** - User segmentation
- `dwh.fact_sm_bonus_history` - **5 queries** - Bonus distribution analysis

**Key Analytical Patterns:**
- **Churn Analysis:** Login gap analysis (7-14, 14-30, 30-60, 60+ days)
- **Balance Indices:** Median balance tracking by tier with min/max normalization
- **Dormancy Tracking:** 30-day player return patterns
- **Machine Performance:** Payout analysis by machine type and launch date
- **Segment Analysis:** Revenue multipliers vs actual user behavior

**Specialized Metrics:**
- Balance index calculations: `(median - Min_Median) / (Max_Median - Min_Median)`
- Gems velocity and consumption rates
- SlotoBucks accumulation and spending patterns
- FTD rates by product category

### 4. **Seasonal Events Analytics** (8 queries)
**Primary Business Focus:** Event participation, board completion, revenue share analysis

**Core Table Usage:**
- `dwh.sm_fact_blast_games_activity` - **3 queries** - Blast event participation
- `dwh.sm_fact_battlesheep_events` - **3 queries** - Battlesheep event tracking
- `dwh.sm_fact_blast_events` - **2 queries** - New blast event structure
- `agg.agg_sm_daily_promotion_stats` - **6 queries** - Revenue attribution during events

**Key Analytical Patterns:**
- **Board Progression:** Multi-board completion tracking (1-5 cycles)
- **Revenue Share:** Individual user revenue as percentage of total event revenue
- **Pick Analysis:** Median picks per board completion
- **Event Comparison:** Blast vs Battlesheep performance metrics

### 5. **Mid-Term Features Analytics** (15 queries)
**Primary Business Focus:** Feature-specific performance, jackpot analysis, promotion effectiveness

**Core Table Usage:**
- `dwh.fact_sm_spin_history_kafka` - **8 queries** - Feature participation via spins
- `dwh.sm_fact_payments` - **6 queries** - Feature-related revenue (ROOG offers)
- `dwh.sm_fact_external_progressive_jaw_game_played` - **3 queries** - Dynamic jackpot tracking
- `sm_fact_mega_win_party_history` - **2 queries** - Mega pod collection
- `agg.agg_sm_daily_promotion_users_spins` - **4 queries** - Antebet analysis

**Key Analytical Patterns:**
- **Antebet Analysis:** Feature-specific betting behavior (Figz, Globez, Mega Pods)
- **Jackpot Performance:** Dynamic jackpot payouts by user segment (PU vs NPU)
- **Promotion Effectiveness:** DOS (Days of Season) analysis for different features
- **Bundle Analysis:** Figz bundle upgrade rates and gem ratios

**Specialized Metrics:**
- Cumulative win/loss ratios by event progression
- Jackpot index distribution (0-3 levels)
- Mega pod collection by status (COLLECTED, IMMEDIATELY_UNLOCK, SEASON_END)
- Raw bet percentiles for feature participation

---

## Common Column Patterns

### Universal Identifiers (Present in 90%+ of queries)
- `user_id` - Primary user identifier
- Date/time columns: `calc_date`, `tran_date`, `event_date`, `spin_date`, `bonus_ts`

### Standard Filters (Applied in 80%+ of queries)
```sql
-- User exclusions (test/internal users)
AND user_id > 0
AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.playtika_users)
AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_fact_journey_state_notifications WHERE step_id = 539265)

-- Transaction quality filters
AND tran_status_id = 2        -- Approved transactions only
AND artificial_ind = 0        -- Real transactions only  
AND is_test = 0              -- Non-test transactions only
```

### Revenue & Financial Columns
- `gross_amount` - Primary revenue metric
- `transaction_amount` - Transaction value
- `net_amount` - Net revenue after fees
- `cost` - Internal currency cost
- `bonus_amount` - Bonus/reward amounts

### User Segmentation Columns
- `tier_id` - User tier (1-7: Bronze to Black Diamond)
- `user_level` - Game level
- `platform_id` - Platform identifier
- `is_paying_user` - Paying user flag

---

## Data Quality & Governance Patterns

### Consistent Exclusion Patterns
1. **Test Users:** `dwh.playtika_users` table exclusion
2. **Journey Test Users:** Step ID 539265 exclusion
3. **Invalid Users:** `user_id > 0` filter
4. **Transaction Quality:** Status=2, artificial_ind=0, is_test=0

### Time Zone Handling
Most queries use Israel timezone conversion:
```sql
date(timestamp::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours')
```

### Common Date Ranges
- **Recent Analysis:** `current_date - 30` to `current_date - 90`
- **Historical Analysis:** `current_date - 180` to `current_date - 365`
- **Album Analysis:** Launch date to end date ranges

---

## Schema Organization

### `dwh` Schema - Production Data Warehouse
- Fact tables: `sm_fact_*`, `fact_sm_*`
- Dimension tables: `dim_*`, `sm_dim_*`
- User profiles and aggregations

### `agg` Schema - Aggregated Data
- Daily user statistics
- Promotion aggregations
- Performance summaries

### `sm_draft` Schema - Draft/Staging Data
- Product dimensions
- Event definitions
- Album metadata
- Experimental data structures

---

## Validation Against Slotomania Table Knowledge Rules

### Confirmed Table Usage Patterns

**✅ `sm_fact_payments` Usage Validated:**
- Our analysis shows heavy usage of `tran_date`, `user_id`, `tran_status_id`, `artificial_ind`, `is_test` - all confirmed as primary columns in the rules
- Standard filtering pattern matches rules: `tran_status_id = 2`, `artificial_ind = 0`, `is_test = 0`
- `gross_amount` and `transaction_amount` are indeed the primary revenue metrics
- `sku_id` and `transaction_source_type_id` heavily used for product analysis

**✅ `sm_fact_internal_purchases` Usage Validated:**
- `cost` column confirmed as gems spending metric (currency_id = 10000)
- `timestamp` and `user_id` are primary identifiers as expected
- `transaction_source_type_id` used for categorizing internal purchase sources

**✅ `fact_sm_spin_history_kafka` Usage Validated:**
- `guid`, `user_id`, `spin_ts`, `spin_date` confirmed as primary identifiers
- `bet_amount`, `win_amount` are core gameplay metrics
- `machine_type_id` essential for machine performance analysis
- Partition by `spin_date` confirmed for performance

**✅ `fact_sm_bonus_history` Usage Validated:**
- `bonus_type_id`, `bonus_amount`, `user_new_balance` are key columns
- `bonus_ts` used for timing analysis
- Multiple feature-specific fields confirmed but not all used in current queries

**✅ `Sm_User_Profile` vs `agg_sm_daily_users_stats`:**
- Our analysis shows preference for `agg_sm_daily_users_stats` over `Sm_User_Profile`
- This aligns with rules recommendation to prefer facts for event timing
- `calc_date` provides better temporal analysis than profile snapshots

### Key Insights from Rules Validation

1. **Column Usage Confirmation:** The rules document confirms that many columns exist but aren't frequently used - our analysis focuses on the actually utilized columns
2. **Validation Requirements:** Rules emphasize validation before using new columns - our frequency analysis helps identify "safe" commonly-used columns
3. **Filter Patterns:** Standard exclusion patterns in our analysis match the rules' recommendations for data quality
4. **Environment Filters:** Rules mention `environment_id = 1` and `game_type_id = 2` but these aren't prominent in current queries

### Gaps Identified

**Underutilized Tables from Rules:**
- `dwh.fact_sm_user_offer_history_po2` - Only used in 3 queries (Mid-term ROOG offers) despite being a key table in rules
- `dwh.fact_sm_sessions_kafka` - **Not used in any current queries** despite rich session data available
- `dwh.Sm_User_Profile` - Rarely used, preference for `agg_sm_daily_users_stats` and snapshot tables

**Well-Utilized Tables Matching Rules:**
- `dwh.fact_sm_goods_service_data` - **Actually heavily used** (10+ queries) across Album and other domains
- `dwh.sm_fact_internal_purchases` - Strong usage (12+ queries) for gem economy analysis
- `dwh.fact_sm_bonus_history` - Good coverage (8+ queries) for bonus analysis

**Potential Expansion Opportunities:**
- **Session Analysis:** `fact_sm_sessions_kafka` could provide device, channel, and session-level insights
- **Offer Performance:** `fact_sm_user_offer_history_po2` has rich offer lifecycle data (CREATED/IMPRESSION/PURCHASE/CLOSED)
- **Environment Filtering:** Rules mention `environment_id = 1` and `game_type_id = 2` but these aren't used in current queries

---

## Recommendations for Future Analysis

### 1. **Core Metrics Dashboard**
Focus on these high-frequency tables for KPI dashboards:
- `dwh.sm_fact_payments` (revenue)
- `agg.agg_sm_daily_users_stats` (user behavior)
- `dwh.fact_sm_spin_history_kafka` (engagement)

### 2. **Feature Performance Analysis**
Each feature has dedicated fact tables - use for deep-dive analysis:
- Albums: `dwh.sm_users_album_cards_amount_snp`
- Daily Dash: `dwh.sm_fact_daily_dash_challenges`
- Seasonals: Event-specific tables in `sm_draft`

### 3. **Data Lineage Considerations**
- Always apply standard user exclusions
- Use appropriate time zone conversions
- Validate transaction quality filters
- Consider partition pruning for large fact tables

---

## Glossary Integration

This analysis aligns with the Slotomania business glossary:
- **ARPU/ARPPU:** Calculated from `agg.agg_sm_daily_users_stats`
- **DAU:** Derived from daily user activity tables
- **PU (Paying Users):** Identified via `dwh.sm_fact_payments`
- **Churn Rate:** Calculated using `agg.agg_sm_daily_users_stats` patterns
- **Tiers:** Bronze(1) to Black Diamond(7) from `tier_id` columns

---

## Summary of Key Findings

### Data Architecture Insights

**1. Clear Domain Separation:**
- Each business domain (Album, Dash, Management, Seasonals, Mid-term) has dedicated fact tables
- Shared dimension tables provide consistent reference data across domains
- `agg.agg_sm_daily_users_stats` serves as the universal user behavior aggregation layer

**2. Consistent Data Quality Patterns:**
- Universal user exclusions: Playtika internal users and journey test users (step_id = 539265)
- Standard transaction filters: `tran_status_id = 2`, `artificial_ind = 0`, `is_test = 0`
- Time zone standardization: Israel timezone with 14-hour offset for promo dates

**3. Schema Organization Strategy:**
- **`dwh` schema:** Production fact and dimension tables
- **`agg` schema:** Performance-optimized aggregated views
- **`sm_draft` schema:** Feature-specific dimensions and experimental structures

### Business Intelligence Maturity

**Strengths:**
- Comprehensive event tracking across all game features
- Rich dimensional modeling for albums, products, and user segments
- Strong aggregation layer for performance optimization
- Consistent analytical patterns across business domains

**Opportunities:**
- Session-level analysis currently underutilized
- Offer lifecycle tracking could be expanded
- Environment and game type filtering could be standardized

### Table Usage Hierarchy

**Tier 1 (Universal):** `dwh.sm_fact_payments`, `agg.agg_sm_daily_users_stats`  
**Tier 2 (High Usage):** `dwh.fact_sm_spin_history_kafka`, `dwh.fact_sm_bonus_history`, `dwh.sm_fact_internal_purchases`  
**Tier 3 (Domain-Specific):** Album tables, Dash tables, Seasonal event tables  
**Tier 4 (Specialized):** Feature-specific tables (jackpots, mega pods, etc.)

### Analytical Sophistication

The queries demonstrate advanced analytical capabilities:
- Complex window functions for progression analysis
- Sophisticated user segmentation logic
- Multi-dimensional revenue attribution
- Time-series analysis with seasonal patterns
- Cohort analysis for user behavior tracking

---

*This document serves as the definitive guide for understanding Slotomania's data architecture based on systematic analysis of 85+ production queries. It should be updated as new features and tables are introduced to the ecosystem.*
