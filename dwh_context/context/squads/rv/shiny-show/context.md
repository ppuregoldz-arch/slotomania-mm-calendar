# Shiny Show - Technical Context

**Feature**: Shiny Show placement within Rewarded Video (RV) feature
**Purpose**: Specialized ad placement that appears during specific game moments with strict gatekeeping rules

## How Shiny Show Works

### Placement Specifications

#### Trigger Types & Floor Requirements
- **MOLE (bomb_pick)**: Can trigger on floors 6-12
- **Extra Pick (wait_buy_extra_pick)**: Can trigger ONLY on floor 10
- **Maximum Floor Limit**: Floor 12 (no triggers beyond this)

#### Daily Caps
- **MOLE triggers**: Up to 2 per day
- **Extra Pick triggers**: Up to 1 per day

#### User Targeting
- **Current Status**: Live only for internal Playtika users
- **Test Groups**: Test_A and Test_B only (Test ID: xmXDU4lG4J)

### eCPM Thresholds by Segment & Floor

#### NPU Segments (Buckets 1, 2, 3)
- **Floors ≤8**: Use config_min_ecpm
- **Floors 9-10**: 
  - Bucket 1 (US): 30
  - Bucket 2 (Tier 1): 15 
  - Bucket 3 (Other): 10
- **Floors 11-12**:
  - Bucket 1 (US): 50
  - Bucket 2 (Tier 1): 25
  - Bucket 3 (Other): 15

#### DPU Segments (Buckets 10, 20, 30, 40, 50, 60)
- **Floors ≤7**: Use config_min_ecpm
- **Floor 8**: 
  - Bucket 10 (CZ=0): 30
  - Bucket 20 (CZ=0.01-4.99): 40
  - Bucket 30+ (CZ≥5): 125-250
- **Floors 9-10**:
  - Bucket 10: 30
  - Bucket 20: 60
  - Bucket 30+: 150-300
- **Floor 11**:
  - Bucket 10: 50
  - Bucket 20: 80
  - Bucket 30+: 200-400
- **Floor 12**:
  - Bucket 10: 55
  - Bucket 20: 100
  - Bucket 30+: 250-500

## Key Tables & Fields

### Primary Event Table
- `dwh.sm_fact_rv_client_events`
- Key fields: `placement`, `placement_trigger`, `feature_additional_data`, `revenue`, `event_type`
- Floor extraction: `REGEXP_SUBSTR(feature_additional_data, '"level"\s*:\s*([0-9]+)', 1, 1, '', 1)::INT + 1`

### Segmentation
- `dwh.sm_user_profile_datamining_snapshot`
- Key fields: `rv_opportunistic_config_buckets`, `RV_opportunistic_dynamic_ecpm`

### A/B Testing
- `sm_ds.abtest_user_allocations` (Test ID: 'xmXDU4lG4J')

## Common Issues to Watch For

- Extra Pick triggers firing outside floor 10
- MOLE triggers outside floors 6-12
- Daily caps being exceeded 
- Ads served below eCPM thresholds
- Non-test group users receiving ads
- Config mismatches after updates