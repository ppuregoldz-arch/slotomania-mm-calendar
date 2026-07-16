# Slotomania Parameters & Configuration Systems

Core parameters, thresholds, and configuration systems used across all Slotomania features for user segmentation, offer targeting, gatekeeping, and business logic implementation.

## RV (Rewarded Video) Parameters

### Core RV Parameters System

The RV parameter system consists of three interconnected parameters that work together for user segmentation and threshold management:

#### 1. `rv_segment_opportunistic`
**Purpose**: User segmentation based on payment behavior and recency
**Output Values**: NPU, PUs_last_30D, DPU_30_60, DPU_60_90, DPU_90+

**Segmentation Logic**:
| Segment | Criteria | Business Purpose |
|---------|----------|------------------|
| **NPU** | LTV=0, Level≥300 | Non-paying users, country-based targeting |
| **PUs_last_30D** | LTV>0, Level>100, ≤30 days since purchase | Active recent purchasers |
| **DPU_30_60** | LTV>0, Level>100, 30-60 days since purchase | Recent purchasers |
| **DPU_60_90** | LTV>0, Level>100, 60-90 days since purchase | Moderate purchasers |
| **DPU_90+** | LTV>0, Level>100, ≥90 days since purchase | Dormant purchasers |

#### 2. `rv_opportunistic_config_buckets`
**Purpose**: Bucket assignment and dynamic reduction logic
**Output Values**: 1-60000 (parameter values for configuration table joins)

**Bucket Ranges by Segment**:
- **NPU**: 1-3 (country-based: US=1, Tier_1=2, Other=3)
- **PUs_last_30D**: 100-400 (4 CZ buckets)
- **DPU_30_60**: 10000-60000 (6 CZ buckets)
- **DPU_60_90**: 1000-6000 (6 CZ buckets) 
- **DPU_90+**: 10-60 (6 CZ buckets × 4 time periods)

#### 3. `RV_opportunistic_dynamic_ecpm`
**Purpose**: Dynamic eCPM multiplier for NPU users only
**Output Values**: 0.7-1.0 (multiplier applied to minimum thresholds)
**Scope**: NPU users only (DPU users always get 1.0)

### RV Configuration Tables

#### `sm_draft.RV_opportunistic_min_eCPM_per_segment`
**Rows**: 49 (as of May 2026)
**Structure**: Segment × CZ Bucket × Time Period × Country
**Purpose**: Defines minimum eCPM and ad revenue thresholds per user segment

**Key Fields**:
- `parameter_value`: Links to `rv_opportunistic_config_buckets`
- `min_ad_rev`: Minimum revenue threshold ($USD)
- `min_ecpm`: Minimum eCPM requirement
- `config_promo_date_from/to`: Configuration validity period
- `config_cz_from/to`: CZ range for bucket application
- `country`: Geographic targeting (US/Tier_1/Other/All)

**Current Threshold Ranges**:
- **NPU**: $0.01-$0.25 (varies by country and time)
- **PUs_last_30D**: $0.13-$0.50 (4 CZ buckets)
- **DPU_30_60**: $0.06-$0.50 (highest thresholds)
- **DPU_60_90**: $0.04-$0.40 (medium thresholds)
- **DPU_90+**: $0.015-$0.25 (lowest thresholds)

### RV Integration Flow
1. **Segmentation**: User classified by purchase behavior → segment
2. **Bucket Assignment**: Segment + CZ + Country → parameter value
3. **Configuration Lookup**: parameter_value + date + CZ → thresholds
4. **Dynamic Adjustment**: NPU users get eCPM multiplier (0.7-1.0)
5. **Threshold Application**: Final values used for ad serving decisions

## Purchase Tools Parameters

### Template ID System
**Purpose**: Unique identifier system for offer configurations across all features
**Scope**: RV, Purchase Tools, Seasonals, Albums - any feature with offers

**Structure**: Each Template ID represents:
- Specific offer type + targeting segment
- Specific configuration (price, rewards, mechanics)  
- Specific promo date period
- Provided by Ops team only after offer goes live

**Examples**:
- `template_id = 221777` (RV offers)
- `template_id = 227705` (Counter PO)
- `template_id = 226225` (various Purchase Tools)

**Usage**: Essential for gatekeeping queries and offer validation

### Purchase Tools Configuration Tables

#### Prize Mania: `sm_draft.prize_mania_config`
**Purpose**: Price and SlotoBucks bonus configuration
**Key Fields**:
- `mission_id`, `reward_id`, `schedule_id`: Offer identification
- `price`: Configuration price for validation
- Links to transaction validation via gross_amount matching

#### Counter PO: `sm_draft.counter_po_po2_config`  
**Purpose**: Counter PO pricing and reward configuration
**Key Fields**:
- `mission_id`, `reward_id`, `schedule_id`: Offer identification
- `price`: Configuration price for validation
- Used for Test_A group validation and purchase matching

#### Dice Deluxe: `sm_draft.dice_deluxe_config`
**Purpose**: Dice Deluxe pricing configuration
**Key Fields**:
- `price`: Configuration price for Test group validation
- Used to validate only Test users receive offers at correct prices

## User Segmentation Parameters

### CZ (Customer Zone) Buckets
**Purpose**: User value segmentation for targeting and thresholds
**Source Table**: `dwh.sm_user_profile_datamining_snapshot.cz_price_cut_test`
**Ranges**: 0.0 to 50.0+ (continuous scale)

**Common CZ Bucket Ranges**:
- **Low CZ**: 0.0-4.99 (low-value users)
- **Mid CZ**: 5.0-14.99 (medium-value users)  
- **High CZ**: 15.0-50.0+ (high-value users)

### Level Requirements
**Purpose**: Feature access and progression gates
**Business Rule**: Higher levels unlock features and better offers

**Common Level Thresholds**:
- **Feature Access**: Minimum level requirements for feature participation
- **Machine Unlocks**: New slot machines at specific levels
- **Offer Eligibility**: Level gates for premium offers and rewards

### Geographic Parameters
**Purpose**: Country-based segmentation for RV and offer targeting

**Country Tiers**:
- **US**: Premium tier (highest thresholds, parameter_value = 1)
- **Tier_1**: High-value countries (medium thresholds, parameter_value = 2)  
- **Other**: Remaining countries (lower thresholds, parameter_value = 3)
- **All**: Global configuration (applies to all countries)

## Clan Parameters System

### Central Clan Parameter Table
**Primary Table**: `dwh.sm_clans_datamining`
**Architecture**: Comprehensive datamining table similar to `sm_user_profile_datamining_snapshot` but for clans
**Parameter Storage**: 35+ clan dash parameters as individual columns with `clan_dash_daily_*` naming pattern

### Clan Parameter Architecture
- **Granularity**: Clan-level (not user-level)
- **User Access**: Via clan membership join patterns  
- **Update Frequency**: Daily snapshots with `event_date`
- **Scope**: All clan dash features and mechanics

### Related Configuration Tables
- **Parameter Storage**: `dwh.stg_smart_seg_sm_clan_dash_parameter*` tables
- **Feature-Specific**: Individual tables per feature (get_smash_chips, royal_jackpot, etc.)
- **User Membership**: `dwh.sm_clan_user_profile` for user-clan relationships

## Threshold & Configuration Patterns

### Revenue Thresholds
**Purpose**: Minimum revenue requirements for ad display and offer eligibility

**Validation Pattern**:
```sql
-- Standard threshold validation across all features
case when actual_revenue >= min_threshold * multiplier then 'ok' else 'wrong' end
```

**Common Threshold Types**:
- **Min eCPM**: Minimum effective cost per mille for ad revenue
- **Min Ad Rev**: Minimum ad revenue per impression ($USD)
- **Gross Amount**: Transaction amount validation against configuration
- **Bonus Amount**: Reward amount validation against expected values

### Configuration Validation Patterns

#### Price Configuration Validation
```sql
case when round(config_price) = round(gross_amount) then 'ok' else 'wrong' end
```

#### Bonus Amount Validation  
```sql
case when round(expected_bonus) = round(actual_bonus) then 'ok' else 'wrong' end
```

#### Test Group Validation
```sql
case when group_name in ('Test_A', 'Test_B') then 'ok' else 'wrong' end
```

### Date-Based Configuration
**Purpose**: Time-bounded configuration rules and parameter changes

**Key Patterns**:
- **Promo Date Logic**: Use event `promo_date` for configuration joins
- **Validity Periods**: `config_promo_date_from/to` for active configurations
- **Change Management**: Historical configurations preserved for analysis

## Business Rules & Safety Mechanisms

### RV Parameter Safety Rules
- **Maximum Reduction**: 2-bucket decrease maximum per optimization cycle
- **eCPM Floor**: 0.7 multiplier minimum (30% max reduction)
- **Test Group Scope**: Optimization only active for Test_A/Test_B/Control
- **Reset Conditions**: Bucket changes, segment changes, threshold achievement

### Offer System Rules
- **Template ID Lifecycle**: IDs only valid during promo periods
- **Test Group Targeting**: Offers restricted to specific test groups
- **Configuration Validation**: All transactions must match configuration prices
- **Reward Validation**: Bonus amounts must match configured expectations

### User Eligibility Rules
- **Level Requirements**: Minimum levels for feature access
- **Segment Targeting**: Appropriate segments for each offer type
- **Geographic Restrictions**: Country-based offer and threshold targeting
- **Timing Rules**: Promo date-based eligibility and configuration application

## Parameter Documentation Sources

### Primary Documentation
- **RV Parameters**: `context/squads/rv/parameters/`
  - `rv-parameters-overview.md`: Current system architecture
  - `rv-parameters-changes.md`: Change history and validation
- **Query Patterns**: `context/business-knowledge/references/query-patterns.md`
- **Business Context**: `context/business-knowledge/core-knowledge/business-context.md`

### Configuration Table References
- **RV**: `sm_draft.RV_opportunistic_min_eCPM_per_segment`
- **Purchase Tools**: Various `sm_draft.*_config` tables
- **User Data**: `dwh.sm_user_profile_datamining_snapshot`
- **Test Groups**: `sm_ds.abtest_user_allocations`

### Query Validation Requirements
All parameter-based queries must include:
1. **Configuration Joins**: Proper linking via parameter values and date ranges
2. **Threshold Validation**: Revenue/amount validation against configuration
3. **Test Group Validation**: Proper test group filtering and validation
4. **Date Logic**: Use event promo_date, not execution date
5. **Documentation**: Clear parameter logic explanation in query comments

---

**Note**: Parameters and thresholds change frequently based on business needs and test results. Always validate current configuration values against live tables before implementing queries or analyses.