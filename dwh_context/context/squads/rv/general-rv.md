# General RV - Complete Context & Queries

**Squad**: Rewarded Video (RV)
**Scope**: All RV functionality including ad serving, revenue optimization, segmentation, and performance monitoring

## Overview
Rewarded Video (RV) is an advertising monetization project in Slotomania that allows eligible users to watch advertisements in exchange for in-game rewards. The goal is to generate advertising revenue while maintaining a positive player experience and providing meaningful rewards.

**Advertising Partner**: We work with **AppLovin**, which acts as a mediation platform between Slotomania and multiple advertising publishers and networks. AppLovin determines which advertisement to serve based on available demand, bidding results, user characteristics, geography, and other monetization factors.

**Experiment Status**: The RV project is currently running as an experiment with 80% exposure to the eligible population. Multiple configuration and logic changes have been introduced throughout the project lifecycle.

## Business Goals

### Primary Objectives
- **Advertising Revenue Generation**: Monetize non-paying and dormant users through video ad impressions
- **Player Retention**: Provide meaningful rewards to maintain engagement without direct purchases
- **User Experience Balance**: Generate revenue while preserving positive gameplay experience
- **Segment Optimization**: Maximize revenue efficiency across different user segments and geographies

### Strategic Approach
- **Targeted Exposure**: Focus on NPU and dormant DPU populations with minimal cannibalization risk
- **Dynamic Configuration**: Adaptive thresholds and rewards based on user behavior and market conditions
- **Revenue Optimization**: Balance ad fill rates with eCPM requirements for sustainable revenue growth
- **Experimental Framework**: Continuous testing and optimization of configuration parameters

## Key Performance Indicators

### Revenue Metrics
- **Daily/Weekly RV Revenue**: Total advertising revenue generated across all placements
- **eCPM Performance**: Effective cost per thousand impressions by segment and placement
- **Revenue per User**: RV revenue attribution by user segment and engagement level
- **Fill Rate Optimization**: Percentage of ad requests successfully filled with qualifying ads

### User Engagement Metrics
- **Ad Completion Rate**: Percentage of started ads that are completed for rewards
- **Daily Active RV Users**: Users engaging with RV features per day
- **Placement Performance**: Effectiveness of different ad placement types
- **Segment Participation**: RV usage rates across NPU and DPU populations

### Configuration Effectiveness
- **Threshold Compliance**: Performance of eCPM minimum requirements
- **Bucket Migration Success**: Effectiveness of dynamic DPU bucket adjustments
- **Geographic Performance**: Revenue and engagement differences across country tiers
- **Experiment Impact**: A/B test results on revenue and user experience metrics

---

## Main Tables Used

### 1. dwh.sm_fact_rv_client_events
**Purpose**: Client-side ad events tracking
**Key Columns**:
- `user_id` - Unique user identifier
- `event_date` - Date of the event (used for partitioning)
- `event_ts` - Timestamp of the event
- `event_type` - Type of event (see Event Types below)
- `ad_id` - Ad identifier
- `offer_id` - Offer identifier (links to PO2 table)
- `revenue` - Revenue generated from the ad
- `transaction_id` - Transaction identifier (null if reward failed)
- `user_local_ts` - User's local timestamp
- `placement` - Ad placement location
- `placement_trigger` - What triggered the ad placement
- `feature_additional_data` - JSON with additional context (floor info, etc.)

**Event Types**:
- `AD_REWARDED` - User completed the ad and received reward (check transaction_id is not null)
- `AD_REWARD_FAILED` - User stopped/closed the ad in the middle (did not complete)
- `AD_DISPLAYED` - Ad was shown to the user
- `AD_SHOW_REQUESTED` - Request to show ad was made
- `AD_LOAD_SUCCEEDED` - Ad loaded successfully
- `AD_OFFER_CLOSED_AUTOMATICALLY` - System closed the ad automatically
- `ADS_RESTRICTED` - User is restricted from seeing ads

### 2. dwh.sm_user_profile_datamining_snapshot
**Purpose**: User segmentation and RV configuration data
**Key RV Columns**:
- `user_id` - Unique user identifier
- `rv_opportunistic_config_buckets` - RV segmentation bucket
- `RV_opportunistic_dynamic_ecpm` - Dynamic eCPM threshold
- `cz_bucket` - Customer Zone bucket for segmentation
- `snapshot_date` - Date of the snapshot

### 3. sm_ds.abtest_user_allocations
**Purpose**: A/B test group assignments
**Key Columns**:
- `user_id` - User identifier
- `test_id` - A/B test identifier
- `group_name` - Test group assignment (Test_A, Test_B, Control, etc.)
- `allocation_date` - When user was allocated to test

### 4. dwh.sm_fact_payments
**Purpose**: Revenue validation and user payment behavior
**Key Columns**:
- `user_id` - User identifier
- `tran_date` - Transaction date
- `gross_amount` - Gross payment amount
- `net_amount` - Net payment amount
- `tran_status_id` - Transaction status (2 = successful)

### 5. Segmentation Parameter Tables
**Purpose**: Dynamic user segmentation and parameter calculation

#### stg.stg_smart_seg_sm_rv_segments
- `user_id` - User identifier
- `rv_segment_opportunistic` - Calculated segment (NPU/PUs_last_30D/DPU_30_60/DPU_60_90/DPU_90+)

#### stg.stg_smart_seg_sm_rv_opportunistic_config_buckets  
- `user_id` - User identifier
- `rv_opportunistic_config_buckets` - Dynamic bucket assignment with expanded ranges (1-60000)

#### stg.stg_smart_seg_sm_cz_price_cut_test
- `user_id` - User identifier
- `cz_price_cut_test` - Customer zone price value
- `RV_opportunistic_dynamic_ecpm` - Dynamic eCPM multiplier (NPU only, includes Control group)

### 6. Configuration & Supporting Tables (UPDATED MAY 2026)
#### sm_draft.RV_opportunistic_min_eCPM_per_segment
**Rows**: 49 (expanded from 37 in May 2026)
- `rv_segment` - Segment identifier (NPU/PUs_last_30D/DPU_30_60/DPU_60_90/DPU_90+/All)
- `country` - Country group (US/Tier_1/Other/All)
- `config_cz_from/config_cz_to` - CZ range for DPU buckets
- `min_ad_rev` - Minimum eCPM threshold ($)
- `parameter_value` - Bucket identifier (expanded ranges: 1-60000)
- `segment_multiplier` - Bucket reduction multiplier (1/10/100/1000/10000)
- `config_promo_date_from/to` - Configuration validity dates

#### dwh.fact_sm_sessions_kafka
- `user_id` - User identifier  
- `session_creation_date` - Session date
- `country` - User country for geo-targeting
- Used for country group assignment when datamining snapshot unavailable

## Target Population & Eligibility

The RV feature is **not available to the entire player base**. Current exposure is limited to two primary user segments:

### NPU (Non-Paying Users)
Users who have **never made a purchase**.

### DPU 90+ (Dormant Payers)  
Users who have made purchases in the past but have **not purchased for at least 90 days**.

**Key Segmentation Field**: `rv_segment_opportunistic` - primary field used throughout the project for user targeting.

### Detailed Segmentation Logic (UPDATED MAY 2026)

#### rv_segment_opportunistic Definition (Current)
```sql
CASE 
    WHEN ltv = 0 AND user_level >= 300 THEN 'NPU'
    WHEN ltv > 0 AND user_level > 100 AND days_since_last_purchase <= 30 
         AND COALESCE(cz_price_cut_test, 0) <= 15 THEN 'PUs_last_30D'
    WHEN ltv > 0 AND user_level > 100 AND days_since_last_purchase >= 90 
         AND COALESCE(cz_price_cut_test, 0) <= 50 THEN 'DPU_90+'  
    WHEN ltv > 0 AND user_level > 100 AND days_since_last_purchase >= 60 
         AND COALESCE(cz_price_cut_test, 0) <= 50 THEN 'DPU_60_90'
    WHEN ltv > 0 AND user_level > 100 AND days_since_last_purchase >= 30 
         AND COALESCE(cz_price_cut_test, 0) <= 50 THEN 'DPU_30_60'
    ELSE null 
END
```

**Eligibility Criteria**:
- **NPU**: LTV = 0 (never purchased) + Level 300+ 
- **PUs_last_30D**: LTV > 0 + Level 100+ + Last purchase within 30 days + CZ ≤ 15 (renamed from PUs_last_90D)
- **DPU_30_60**: LTV > 0 + Level 100+ + Last purchase 30-60 days ago + CZ ≤ 50 (NEW)
- **DPU_60_90**: LTV > 0 + Level 100+ + Last purchase 60-90 days ago + CZ ≤ 50 (NEW)
- **DPU_90+**: LTV > 0 + Level 100+ + Last purchase > 90 days ago + CZ ≤ 50

**Population Expansion**: Added granular targeting for DPU 30-90 day users who were previously classified as 'PU' and not receiving ads.

**Parameter Documentation**: Complete segmentation details available in `parameters/` folder.

## Configuration Logic

The RV system uses **different configuration approaches** for each user segment:

### NPU Configuration (Country Tier Based)
NPU users are configured by **Country Tier** with three country-tier segments:

- **Bucket 1**: US users (highest eCPM thresholds)
- **Bucket 2**: Tier 1 countries 
- **Bucket 3**: Other countries (lowest thresholds)

Each country tier determines:
- Minimum revenue (minimum eCPM) required before an advertisement can be shown
- Reward granted to the user based on the revenue generated by that advertisement

### DPU Configuration (CZ Bucket Based)
DPU users are configured using **CZ buckets** controlled by: `rv_opportunistic_config_buckets`

- **Bucket 10**: CZ = 0 (no historical spend)
- **Bucket 20**: CZ = 0.01-4.99 (low spenders)
- **Bucket 30+**: CZ ≥ 5 (higher spenders, buckets 30-60)

Configuration determines:
- Minimum eCPM threshold
- Reward value  
- Eligibility for advertisement exposure

## Dynamic Bucket & eCPM Optimization

### rv_opportunistic_config_buckets Logic
**Adaptive Bucket System**: Users can be moved to lower buckets (reduced eCPM thresholds) based on performance history.

#### Bucket Assignment Logic
```sql
CASE 
    -- Non-test groups: Keep current bucket
    WHEN COALESCE(group_name, 'NA') NOT IN ('Test_A', 'Test_B') THEN last_value_parameter_value
    
    -- Changed segment/CZ: Keep current bucket  
    WHEN group_name IN ('Test_A', 'Test_B') AND parameter_value != last_value_parameter_value THEN last_value_parameter_value
    
    -- New user or segment change: Keep current bucket
    WHEN group_name IN ('Test_A', 'Test_B') AND (previous_parameter_value IS NULL OR parameter_value != previous_parameter_value) THEN last_value_parameter_value
    
    -- Met threshold in last 2 days: Keep current bucket
    WHEN group_name IN ('Test_A', 'Test_B') AND COALESCE(is_above_min_threshold_last_2_days, 1) > 0 THEN last_value_parameter_value
    
    -- At lowest bucket: Keep current bucket
    WHEN group_name IN ('Test_A', 'Test_B') AND previous_bucket_min_rev IS NULL THEN last_value_parameter_value
    
    -- Can afford previous bucket: Reduce by 1 bucket
    WHEN group_name IN ('Test_A', 'Test_B') AND max_ad_revenue_per_day >= previous_bucket_min_rev THEN parameter_value - 1 * segment_multiplier
    
    -- Near lowest bucket: Reduce by 1 bucket (safety)
    WHEN group_name IN ('Test_A', 'Test_B') AND (parameter_value - 2 * segment_multiplier <= 0) THEN parameter_value - 1 * segment_multiplier
    
    -- Can handle 2-bucket reduction: Reduce by 2 buckets (maximum)
    WHEN group_name IN ('Test_A', 'Test_B') AND (parameter_value - 2 * segment_multiplier > 0) THEN parameter_value - 2 * segment_multiplier
    
    ELSE last_value_parameter_value
END
```

#### Country-Based NPU Bucket Mapping
- **Bucket 1**: US users (highest thresholds)
- **Bucket 2**: Tier 1 countries (AU, CA, GB, DE)
- **Bucket 3**: Other countries (lowest thresholds)

#### CZ-Based DPU Bucket Mapping  
- **Bucket 10**: CZ = 0 (no spend history)
- **Bucket 20**: CZ = 0.01-4.99 (low spenders)
- **Buckets 30+**: CZ ≥ 5 (incrementally higher buckets for higher spenders)

### RV_opportunistic_dynamic_ecmp Logic (NPU Only)
**Purpose**: Further reduce eCPM thresholds for NPU users who consistently fail to meet requirements.

#### Dynamic eCPM Calculation
```sql
CASE
    -- Non-test groups: No reduction (1.0 multiplier)
    WHEN COALESCE(group_name, 'NA') NOT IN ('Test_A', 'Test_B') THEN 1
    
    -- Non-NPU users: No reduction
    WHEN COALESCE(rv_segment_opportunistic, 'NA') != 'NPU' THEN 1
    
    -- Bucket changed: Reset to no reduction  
    WHEN config_buckets != parameter_value THEN 1
    
    -- Segment changed between ad events: Reset to no reduction
    WHEN parameter_value != lag_parameter_value THEN 1
    
    -- Met threshold recently: No reduction needed
    WHEN COALESCE(is_above_threshold_days, 1) >= 1 THEN 1
    
    -- Revenue meets or exceeds threshold: No reduction
    WHEN ratio >= 1 THEN 1
    
    -- Country-specific minimum reductions (30% floor):
    WHEN country_group = 'US' AND ratio >= 0.7 THEN ratio
    WHEN country_group = 'US' AND ratio < 0.7 THEN 0.7
    WHEN country_group = 'Tier_1' AND ratio >= 0.7 THEN ratio  
    WHEN country_group = 'Tier_1' AND ratio < 0.7 THEN 0.7
    WHEN country_group = 'Other' AND ratio >= 0.7 THEN ratio
    WHEN country_group = 'Other' AND ratio < 0.7 THEN 0.7
    
    ELSE 1
END
```

#### Key Parameters
- **Ratio Calculation**: `max_ad_revenue_per_day / min_ad_rev`
- **Minimum Reduction Floor**: 0.7 (30% reduction maximum)
- **Analysis Window**: Last 2 days of ad events
- **Reset Conditions**: Bucket changes, segment changes, threshold achievement

## Advertisement Placements

The project currently includes **three primary advertisement placements**:

### 1. Offers Placement
Offer-based advertisements triggered through several entry points:
- **Back To Lobby**
- **ROOC** (Return On Other Coin)
- **ROOG** (Return On Other Gem)

Each trigger can expose the user to an RV opportunity under the relevant configuration and eligibility rules.

### 2. Cloud Placement
**Automatic Appearance**: The Cloud placement appears automatically when an eligible advertisement is available.

**Locations**: Can appear in one of two locations depending on user's current position:
- **Lobby**
- **Slot Machine**

**Purpose**: Serves as a proactive exposure mechanism rather than requiring user navigation to a dedicated offer.

### 3. Shiny Show Placement
Contains two primary advertisement triggers:

#### BOOMB / Mole Trigger
Advertisement becomes available when the user encounters a **Mole event (BOOMB)**.

#### Shiny Floor Trigger  
Advertisement becomes available when the user reaches a **Shiny Floor** and is offered an additional pick opportunity.

*See shiny-show/ folder for detailed gatekeeping queries, trigger logic, limitations, daily caps, and eligibility behavior.*

## Experiment Groups

Current experiment contains **three groups**:
- **Test_A**
- **Test_B**  
- **Control** / **Test_C**

**Migration in Progress**: The existing "Control" group is being renamed to **Test_C** to avoid confusion and better reflect current experiment structure.

**Test Group Impact on Parameter Logic (UPDATED MAY 2026)**:
- **Test_A, Test_B & Control**: Full dynamic bucket and eCPM optimization enabled
- **Other groups**: Dynamic optimization **disabled** (users keep current bucket assignments)  
- **Non-allocated users**: Treated same as non-test groups (no dynamic changes)

**Control Group Integration**: As of May 2026, Control group participates in all parameter optimization alongside Test_A and Test_B.

**Documentation Impact**:
- Some dashboards, queries, and documentation may still reference "Control"
- Other assets may already reference "Test_C"  
- Both naming conventions represent the same experiment group until migration is fully completed
- Parameter logic specifically checks for Test_A/Test_B to enable optimization features

## Parameter Calculation Workflow

### Daily Parameter Update Process
1. **Segment Classification**: Calculate `rv_segment_opportunistic` based on LTV, level, and purchase history
2. **Country Assignment**: Determine country group from sessions or user profile (US/Tier_1/Other)  
3. **Base Bucket Assignment**: Map NPU to country buckets (1-3), DPU to CZ buckets (10-60)
4. **Historical Performance Analysis**: Review last 2 days of ad events for threshold achievement
5. **Dynamic Bucket Adjustment**: Apply bucket reduction logic for Test_A/Test_B users
6. **eCPM Parameter Calculation**: Calculate dynamic eCPM multiplier for NPU users
7. **Configuration Matching**: Join with min eCPM config tables for final thresholds

### Key Dependencies
- **LTV Calculation**: From `dwh.sm_user_profile.sum_net_amount`
- **Purchase History**: `days_since_last_purchase = current_date - last_transaction_date`
- **Ad Performance History**: Last 60 days from `dwh.sm_fact_rv_client_events`
- **A/B Test Assignment**: Test group allocation from `sm_ds.abtest_user_allocations`

## Standard Filters & Patterns

### User Exclusions
```sql
-- Always exclude test users
user_id not in (select distinct user_id from dwh.playtika_users)

-- Exclude journey step users  
user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
```

### Date Ranges
- **Recent Analysis**: Last 7-30 days
- **Trend Analysis**: Last 60-90 days
- **Historical Comparison**: Year-over-year periods
- **A/B Test Periods**: Test-specific date ranges

### Revenue Validation
```sql
-- Only successful RV completions
event_type = 'AD_REWARDED' 
and transaction_id is not null
and revenue > 0
```

## Gatekeeping & Validation Logic

### Core Gatekeeping Principles
**Test Group Validation**: Only users in Test_A and Test_B groups should receive advertisements
**Floor Restrictions**: Shiny Show placements have strict floor-based eligibility rules
**Daily Caps**: Users have placement-specific daily impression limits
**eCPM Compliance**: Revenue must meet dynamic minimum thresholds based on user segment

### Shiny Show Gatekeeping Rules

#### Floor-Based Trigger Validation
```sql
-- MOLE/BOOMB Trigger: Floors 6-12 only
placement_trigger = 'bomb_pick' AND floor IN (6,7,8,9,10,11,12)

-- Extra Pick Trigger: Floor 10 only  
placement_trigger = 'wait_buy_extra_pick' AND floor = 10

-- Maximum Floor Limit: Floor 12 (no triggers beyond)
floor <= 12
```

#### Daily Caps Implementation
- **MOLE triggers**: Maximum 2 impressions per user per day
- **Extra Pick triggers**: Maximum 1 impression per user per day
- **Cap Validation**: System should prevent impressions after daily limits reached

#### Floor Extraction Logic
```sql
-- Extract Shiny Show floor from feature_additional_data JSON
REGEXP_SUBSTR(feature_additional_data, '"level"\s*:\s*([0-9]+)', 1, 1, '', 1)::INT + 1 as Shiny_Show_floor
```

### Offer Placement Validation

#### Template ID Mapping
- **221769**: NPU - Back to Lobby
- **221921**: NPU - ROOC
- **221777**: DPU - Back to Lobby  
- **222145**: DPU - ROOC
- **221169**: Internal offers

#### Reward Amount Validation
**Gems Offers** (SKU_ID = 37):
```sql
-- Validate gem reward matches configuration
bonus_amount = config_gems_amount
```

**Power-up Offers** (SKU_ID = 200239):
```sql
-- Validate power-up amount (typically 2)
bonus_amount = 2
```

**Picks Offers** (SKU_ID = 200150):
```sql
-- Extract pick amount from goods service data
REGEXP_SUBSTR(sku_data, '"pickAmount":([0-9]+)', 1, 1, '', 1)::INT as picks_amount
-- Validate pick amount matches configuration (typically 2)
picks_amount = 2
```

**Card Offers** (SKU_ID = 43):
```sql
-- Validate card type and rarity
card_type = 0 AND rareness = 3  -- Standard validation for specific card types
```

### eCPM Threshold Validation

#### Dynamic eCPM Calculation
```sql
-- NPU/DPU users with dynamic eCPM parameter
revenue >= (config_min_ad_rev / 1000.0) * COALESCE(RV_opportunistic_dynamic_ecpm, 1)
```

#### Config-Based Coin Rewards
**NPU Segments** (Country Tier Based):
```sql
-- Example NPU USA (Bucket 1) coin calculations based on revenue tiers
CASE 
  WHEN rv_opportunistic_config_buckets = 1 AND revenue >= 500/1000.0 THEN 7087500
  WHEN rv_opportunistic_config_buckets = 1 AND revenue >= 250/1000.0 THEN 4725000
  WHEN rv_opportunistic_config_buckets = 1 AND revenue >= 130/1000.0 THEN 1771875
  -- Additional tiers based on configuration
END
```

**DPU Segments** (CZ Bucket Based):
```sql  
-- Example DPU coin calculations
CASE
  WHEN rv_opportunistic_config_buckets = 10 AND revenue >= 20/1000.0 THEN 708750   -- CZ 0
  WHEN rv_opportunistic_config_buckets = 20 AND revenue >= 40/1000.0 THEN 1417500  -- CZ 0.01-4.99
  WHEN rv_opportunistic_config_buckets = 30 AND revenue >= 75/1000.0 THEN 3262500  -- CZ 5-9.99
  -- Additional buckets 40, 50, 60 with higher thresholds
END
```

#### Coin Amount Validation
```sql
-- Final coin calculation with multipliers
config_coins_calc = config_base_coins * tier_multiplier * premium_multiplier

-- Validation ratio
coins_ratio = actual_bonus_amount / config_coins_calc
-- Expected: coins_ratio should equal 1.0 for correct implementation
```

### Platform Integration

#### Client Type Filtering
```sql
-- Standard client types for RV events
client_type_id IN (2, 3, 7, 28, 29, 36, 227, 229, 319, 431, 432, 476)
```

#### Platform Mapping
```sql
CASE 
  WHEN platform_id = 0 THEN 'Web - Facebook'
  WHEN platform_id = 3 THEN 'Web - .Com/PRAS'  
  WHEN platform_id = 1 THEN 'iOS'
  WHEN platform_id = 2 THEN 'Android'
  WHEN platform_id = 6 THEN 'Amazon'
  WHEN platform_id = 8 THEN 'Win8'
  WHEN platform_id = 9 THEN 'Win10'
  WHEN platform_id = 11 THEN 'PRAS App'
  ELSE 'Other'
END
```

## Common Analysis Patterns

### Revenue Analysis
- Daily/weekly revenue trends
- Revenue per user segments
- eCPM threshold performance
- Revenue impact of configuration changes

### User Behavior Analysis  
- Ad completion rates by segment
- Daily active RV users
- User journey through RV flow
- Retention impact of RV usage

### A/B Testing Analysis
- Test group performance comparison
- Statistical significance testing
- Revenue impact assessment
- User experience metrics

### Performance Monitoring
- Fill rates by placement type
- Load time and technical metrics
- Error rates and failure analysis
- Configuration compliance monitoring

---

## Technical Notes

### Performance Optimization
- Always partition by event_date when possible
- Use user_id indexes for efficient joins
- Filter early in subqueries for large datasets
- Avoid cross-joins between large fact tables

### Data Quality Considerations
- Revenue can be null for failed completions
- Transaction_id correlates with successful completions
- Event timestamps may differ between client and server
- JSON parsing in feature_additional_data requires careful handling

## Dashboard Intelligence & Analytics

### Key Performance Dashboards
Based on RV test dashboard analysis (213 data sources, 79 worksheets):

**Core KPI Monitoring**:
- ALL main KPIs - minimal for analysis
- ALL main KPIs including coverage rates
- Cumulative total conversion rate tracking
- Config buckets monitoring

**User Behavior Analysis**:
- Daily retention by test group
- Daily retention in purchase behavior
- Funnel analysis (events and users)
- Balance/consumption/wager trend analysis

**Revenue & Performance Tracking**:
- Daily average retention changes
- Daily balance/consumption trends  
- Displayed events by ad unit
- Average daily velocity metrics

**A/B Testing Analytics**:
- Test group performance comparison
- Statistical significance monitoring
- User allocation and behavior analysis

### Configuration Tables & References
**Core Config Tables**:
- `sm_draft.RV_opportunistic_config` - Main RV configuration
- `sm_draft.RV_gems_config_26_02` - Gems offer configuration
- `sm_draft.RV_coins_config_24_02` - Coins offer configuration  
- `sm_draft.RV_opportunistic_min_eCPM_per_segment` - eCPM thresholds
- `sm_draft.prestige_multipliers_03_12` - Prestige level multipliers

**Supporting Tables**:
- `dwh.Dim_Coins_Value` - Tier multipliers by platform
- `dwh.dim_sku_type` - SKU definitions and mappings
- `kafka.kds_sm_bonus_history_new` - Real-time bonus tracking
- `dwh.fact_sm_goods_service_data` - Goods and rewards data

### Integration Points
- **AppLovin Mediation**: Primary advertising partner for ad serving and revenue optimization
- **Shiny Show**: Specialized placement with BOOMB/Mole and Shiny Floor triggers (see shiny-show/ folder)
- **Payment Systems**: Revenue validation against payment tables for DPU dormancy calculations
- **A/B Testing**: Experiment management with Test_A, Test_B, and Control/Test_C groups
- **User Segmentation**: NPU/DPU classification with country tier and CZ bucket targeting
- **Dynamic Optimization**: Adaptive bucket movement and eCPM threshold adjustments
- **Configuration Management**: Separate config logic for NPU (country-based) vs DPU (CZ bucket-based)
- **Real-time Validation**: Gatekeeping queries for offer validation and compliance monitoring

---

## Risk Areas & Considerations

### Revenue Optimization Risks
- **Threshold Sensitivity**: eCPM requirements that are too high may reduce fill rates and total revenue
- **User Experience Impact**: Excessive ad frequency or poor rewards may negatively affect player satisfaction
- **Market Volatility**: Changes in ad market conditions affecting revenue predictability
- **Configuration Complexity**: Multiple segment-specific configurations requiring careful management

### Technical Implementation Risks  
- **AppLovin Integration**: Dependency on third-party mediation platform for ad serving
- **Dynamic Logic Accuracy**: Proper execution of bucket migration and threshold adjustments
- **Data Accuracy**: Reliable tracking of user segments, completion rates, and revenue attribution
- **Experiment Integrity**: Maintaining proper A/B test allocation and measurement accuracy

### Business Strategy Risks
- **Cannibalization Prevention**: Ensuring RV doesn't reduce direct purchase behavior
- **Segment Definition Accuracy**: Proper NPU/DPU classification and eligibility determination
- **Long-term Sustainability**: Balancing short-term revenue gains with player lifetime value
- **Competitive Positioning**: RV feature effectiveness compared to alternative monetization approaches

---
---

## Parameter Documentation (Updated May 2026)

**Complete parameter system documentation** now available in dedicated `parameters/` folder:

### Parameter Files
- **`parameters/rv-parameters-overview.md`** - Current system architecture and segment configuration
- **`parameters/rv-parameters-changes.md`** - May 2026 changes, validation data, and change history  
- **`parameters/rv-parameters-queries.sql`** - Complete SQL repository with old and new versions

### Key Updates
- **Expanded Segmentation**: 3 → 5 segments with granular DPU targeting
- **Configuration Growth**: 37 → 49 config table rows
- **Control Group Integration**: Full parameter participation
- **Population Expansion**: DPU 30-90 day users now targeted

---

*This file serves as the comprehensive business and technical reference for all RV-related analysis. The RV project includes complex segmentation logic, dynamic optimization features, and multiple advertisement placements requiring careful configuration management and performance monitoring. For current parameter details, see dedicated `parameters/` folder documentation.*