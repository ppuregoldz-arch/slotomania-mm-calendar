# RV - Queries & Gatekeeping Intelligence

## Summary
This file contains RV gatekeeping queries, validation patterns, and analytical intelligence for monitoring RV system compliance and performance.

## RV-Specific Gatekeeping Patterns
**Note**: For universal query best practices (data source selection, date logic, query optimization), see `context/business-knowledge/references/query-patterns.md`

### RV Event-Specific Considerations
- **AD_LOAD_SUCCEEDED**: `placement` and `placement_trigger` are NULL (assigned later when user creates trigger)
- **AD_DISPLAYED/AD_REWARDED**: Include placement data for validation
- **Revenue Validation**: Always filter `revenue > 0` for meaningful eCPM checks

### RV Data Sources by Placement Type
**Offers vs Cloud - Different Transaction Requirements**:
- **Offers**: Use `dwh.sm_fact_rv_client_events` with `transaction_id IS NOT NULL` (transaction-based completion)
- **Cloud**: Use `sm.sm_str_video_ads_history` with `event_type = 'FEATURE_REWARDED'` (different service, no transaction_id requirement)

**Cloud Gatekeeping Pattern**:
- **Data Source**: `sm.sm_str_video_ads_history` table
- **Event Type**: `'FEATURE_REWARDED'` for reward validation
- **Revenue Logic**: `max(revenue) over (partition by reward_id)` for proper revenue attribution
- **Date Logic**: `business_ts` converted to promo_date using Jerusalem timezone with 14-hour offset
- **Feature Filter**: `feature ilike '%cloud%'` for Cloud-specific events

### User Profile Table Limitations
**Important**: `dwh.sm_user_profile` has data quality issues for gatekeeping
- **Masked Data**: First name, last name, email are masked for privacy
- **Incomplete Coverage**: External QA accounts may not be fully updated in the table
- **Available Data**: Country information is reliable when present
- **Best Practice**: Use `dwh.playtika_users` exclusion list instead of relying on user profile for internal user detection

### RV Wheel Reward Connection Chain (May 2026)
**Purpose**: Connect RV ads to wheel-based rewards (hammers, coins, etc.)

**4-Table Connection Pattern**:
1. **RV Event** (`dwh.sm_fact_rv_client_events`) → `transaction_id`
2. **Bonus Journey** (`kafka.kds_sm_bonus_history_new`, sku_id 200143) → `transaction_id`  
3. **Wheel Game** (`dwh.sm_external_progressive_jaw_game_played`) → `game_guid`
4. **Actual Rewards** (`dwh.fact_sm_goods_service_data`) → `parent_reward_request_id`

**Key SKU IDs**:
- **200143**: Wheel journey trigger (links RV to wheel)
- **200173**: Hammers from wheel spin
- **Other wheel outcomes**: Coins, gems, power-ups (different sku_ids)

**Why NOT Timing/Session Connections**:
- **Multiple hammer sources**: RV wheel, purchases, daily rewards can all give hammers
- **Session overlap**: User might get wheel + purchase rewards in same session  
- **Processing delays**: Wheel spin happens seconds after RV event completes
- **Unreliable matching**: Could incorrectly link purchase hammers to RV events

**Validated Example**:
- User 154000066502254: RV transaction 58835720891 → Bonus 58884637801 → Wheel ad0cc0723c96749e8891bd30bbff629b → 7 hammers
- Timing would have failed: Wheel reward came 8+ seconds after RV event

### Focused Gatekeeping Principles
**Each RV gatekeeping query should validate one specific aspect**:
- **Coin Value**: Does actual bonus match expected calculation? (No configuration validation)
- **eCPM Threshold**: Does revenue meet minimum thresholds? (No coin validation)  
- **Load Events**: Are ads being loaded for target segment? (No revenue validation)
- **Placement Coverage**: Are all placements serving ads? (No detailed validation rules)

**Keep validation logic simple and direct**:
```sql
-- ✅ SIMPLE: Direct bucket-to-coins mapping
case
    when rv_opportunistic_config_buckets = 1000 then 708750
    when rv_opportunistic_config_buckets = 2000 then 1417500
    else null
end as config_base_coins

-- ❌ COMPLEX: Multiple threshold checks not requested
case
    when rv_opportunistic_config_buckets = 1000 and revenue >= 0.02 then 708750
    when rv_opportunistic_config_buckets = 1000 and revenue >= 0.01 then 354375
    -- ... additional logic not specifically requested
end
```

## Gatekeeping Query Categories

### 0. DPU 60-90 Launch Gatekeeping (May 2026)
**Purpose**: Validate new DPU_60_90 segment launch and configuration compliance

**Key Validation Areas**:
- **Ad Load Events**: Verify `AD_LOAD_SUCCEEDED` events for DPU_60_90 users on launch day
- **Min eCPM Compliance**: Validate `AD_DISPLAYED` revenue meets $0.04-$0.40 thresholds
- **Coin Value Accuracy**: Verify `AD_REWARDED` bonus amounts match configuration (708,750-8,700,000 coins)
- **Placement Coverage**: Ensure ads serve across Offers, Cloud, and Shiny Show placements

**DPU 60-90 Configuration Context**:
- Parameter values: 1000-6000 (6 CZ buckets)
- Min eCPM range: $0.04-$0.40 based on CZ bucket
- Expected coin rewards: 708,750 to 8,700,000 coins based on bucket and revenue threshold
- Control group inclusion: 'Control' group now receives dynamic eCPM and bucket reduction logic

### 1. Offer Validation Queries
**Purpose**: Validate reward amounts and offer configuration compliance

**Key Patterns**:
- **Gems Offers**: Validate `bonus_amount = gems_base_coins` configuration
- **Power-up Offers**: Validate `bonus_amount = 2` for power-up rewards
- **Picks Offers**: Extract pick amounts from JSON and validate against config
- **Card Offers**: Validate card type and rarity specifications

**Core Validation Structure**:
```sql
/*Standard RV gatekeeping query pattern - Updated May 2026*/
SELECT 
    user_profile.*,
    test_groups.group_name,
    offer_config.*,
    bonus_validation.*,
    CASE WHEN actual_amount = config_amount THEN 'ok' ELSE 'wrong' END as validation_check
FROM (
    SELECT user_id, event_date, event_ts, placement, revenue,
           date(event_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '13 hours') as promo_date
    FROM dwh.sm_fact_rv_client_events 
    WHERE event_date = current_date AND event_type = 'AD_DISPLAYED'
) rv_events
LEFT JOIN dwh.sm_user_profile_datamining_snapshot user_profile 
    ON rv_events.user_id = user_profile.user_id 
    AND user_profile.event_date_datamining = current_date
LEFT JOIN sm_draft.RV_opportunistic_min_eCPM_per_segment config 
    ON user_profile.rv_opportunistic_config_buckets = config.parameter_value
    AND user_profile.cz_price_cut_test BETWEEN config.config_cz_from AND config.config_cz_to
    AND rv_events.promo_date >= config.config_promo_date_from 
    AND rv_events.promo_date < config.config_promo_date_to
LEFT JOIN test_groups ON user_allocation_match
```

### 2. Shiny Show Gatekeeping
**Purpose**: Validate Shiny Show placement triggers, floors, and daily caps

**Key Validations**:
- **Floor Trigger Rules**: MOLE (floors 6-12), Extra Pick (floor 10 only)
- **Daily Caps**: MOLE (2/day), Extra Pick (1/day)
- **Test Group Restriction**: Only Test_A and Test_B users
- **Maximum Floor**: No triggers above floor 12

**Floor Extraction Pattern**:
```sql
REGEXP_SUBSTR(feature_additional_data, '"level"\\s*:\\s*([0-9]+)', 1, 1, '', 1)::INT + 1 as Shiny_Show_floor
```

### 3. eCPM Threshold Validation  
**Purpose**: Validate revenue meets minimum eCPM requirements with dynamic adjustments

**Key Logic**:
- NPU users: Country tier-based thresholds with dynamic eCPM parameter
- DPU users: CZ bucket-based thresholds with bucket migration logic
- Revenue validation: `revenue >= min_threshold * dynamic_multiplier`

### 4. Platform & Client Validation
**Purpose**: Ensure proper platform detection and client type filtering

**Standard Filters**:
```sql
-- Client type filtering
client_type_id IN (2, 3, 7, 28, 29, 36, 227, 229, 319, 431, 432, 476)

-- Platform mapping validation
CASE 
    WHEN platform_id = 0 THEN 'Web - Facebook'
    WHEN platform_id = 3 THEN 'Web - .Com/PRAS'
    -- Additional platform mappings
END
```

## User-Provided Queries

### Gems Offer Validation (26.02)
*Query validates gems offer amounts match configuration based on user segment, CZ bucket, and revenue tiers*

### Power-up Offer Validation (05.03)  
*Query validates power-up offer amounts (typically 2 units) with comprehensive user profiling*

### Picks Offer Validation (09.03)
*Query validates pick amounts extracted from goods service JSON data*

### Card Type Validation (11.03)
*Query validates card type and rarity assignments for card-based RV offers*

### Coin Amount Validation (17.03)
*Query validates coin calculations including tier multipliers and prestige bonuses*

### DPU eCPM Reduction Validation (19.05)
*Query validates dynamic eCPM parameter effectiveness for DPU users*

### Shiny Show Daily Limits Gatekeeping
*Query validates daily impression caps are properly enforced after limits reached*

### Shiny Show Floor & Test Group Validation
*Query validates floor-based triggers and test group restrictions for Shiny Show placements*

### Cloud Placement eCPM & Reward Validation
*Comprehensive validation of Cloud placement revenue thresholds and coin calculations*

## Dashboard Analytics Patterns

### Revenue Performance Tracking
- Daily/weekly revenue trends by segment and placement
- eCPM threshold compliance monitoring
- Revenue per user analysis across test groups

### User Behavior Analytics
- Ad completion rates by placement type
- Daily active RV user tracking
- Retention impact analysis by test group

### Configuration Monitoring  
- Bucket migration effectiveness tracking
- Dynamic eCPM parameter performance
- A/B testing impact measurement

### Gatekeeping Compliance
- Floor restriction adherence monitoring
- Daily cap enforcement validation
- Test group allocation accuracy

## Parameter Logic Implementation

### Core Segmentation Parameters

**UPDATED MAY 2026**: Comprehensive parameter documentation now available in `parameters/` folder.

#### rv_segment_opportunistic (CURRENT - May 2026)
**Purpose**: Expanded user classification with granular DPU targeting
**Segments**: NPU, PUs_last_30D, DPU_30_60, DPU_60_90, DPU_90+ (5 total)
```sql
CASE 
    WHEN ltv = 0 AND user_level >= 300 THEN 'NPU'
    WHEN ltv > 0 AND user_level > 100 AND days_since_last_purchase <= 30 THEN 'PUs_last_30D'
    WHEN ltv > 0 AND user_level > 100 AND days_since_last_purchase >= 90 THEN 'DPU_90+'  
    WHEN ltv > 0 AND user_level > 100 AND days_since_last_purchase >= 60 THEN 'DPU_60_90'
    WHEN ltv > 0 AND user_level > 100 AND days_since_last_purchase >= 30 THEN 'DPU_30_60'
END
```

#### rv_opportunistic_config_buckets (UPDATED - May 2026) 
**Purpose**: Dynamic bucket assignment with Control group inclusion
**Key Features**:
- Test_A/Test_B/Control users: Full optimization enabled (bucket reduction up to 2 levels)
- Other groups: Static bucket assignment (no dynamic changes)
- NPU users: Country-based buckets (US=1, Tier_1=2, Other=3)
- DPU users: CZ-based buckets with expanded ranges
- New segments: DPU_30_60 (10000-60000), DPU_60_90 (1000-6000)
- Historical performance analysis over last 2 days
- Maximum 2-bucket reduction per optimization cycle

#### RV_opportunistic_dynamic_ecpm (UPDATED - May 2026)
**Purpose**: Additional eCPM threshold reduction for NPU users only with Control group inclusion
**Key Features**:
- NPU-specific optimization (DPU users always get 1.0 multiplier)
- Test_A/Test_B/Control users: Dynamic reduction based on revenue ratio  
- Minimum floor: 0.7 (30% maximum reduction)
- Country-specific application (US, Tier_1, Other all use same 0.7 floor)
- Reset conditions: bucket changes, segment changes, recent threshold achievement

### Parameter Calculation Dependencies

#### Data Sources
- **User Profile**: LTV, level, last transaction date from `dwh.sm_user_profile`
- **CZ Values**: Current CZ from `stg.stg_smart_seg_sm_cz_price_cut_test`
- **Ad History**: Last 60 days performance from `dwh.sm_fact_rv_client_events`
- **Country Data**: Geographic targeting from sessions or user profile
- **A/B Testing**: Test group assignment from `sm_ds.abtest_user_allocations`

#### Configuration Tables
- **eCPM Thresholds**: `sm_draft.RV_opportunistic_min_eCPM_per_segment`
- **Bucket Definitions**: Linked to configuration via parameter_value
- **Date Ranges**: Configuration validity periods for threshold changes
- **Geographic Mapping**: Country group assignments (US/Tier_1/Other)

### Implementation Notes
- **Daily Updates**: Parameters recalculated daily based on latest data
- **Performance Window**: 2-day lookback for ad performance analysis  
- **Test Group Dependency**: Optimization features only active for Test_A/Test_B
- **Safety Limits**: Maximum reduction caps prevent excessive threshold lowering
- **Reset Mechanisms**: Multiple conditions trigger parameter resets to baseline

*Note: Parameter logic ensures systematic eCPM optimization while maintaining revenue targets and preventing over-reduction through comprehensive safety mechanisms and test group controls.*

## Related Documentation

For complete parameter documentation including configuration data, change history, and full SQL queries:
- **Current State**: `parameters/rv-parameters-overview.md`
- **Change History**: `parameters/rv-parameters-changes.md` 
- **SQL Repository**: `parameters/rv-parameters-queries.sql`