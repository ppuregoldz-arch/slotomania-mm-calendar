# RV Parameters Overview

## System Architecture

The RV (Rewarded Video) parameter system controls ad delivery and revenue optimization through three interconnected parameters that work together to segment users and apply appropriate thresholds.

## Core Parameters

### 1. `rv_segment_opportunistic`
**Purpose**: User segmentation based on payment behavior and recency
**Output**: Segment classification (NPU, PUs_last_30D, DPU_30_60, DPU_60_90, DPU_90+)

### 2. `rv_opportunistic_config_buckets` 
**Purpose**: Bucket assignment and dynamic bucket reduction logic
**Output**: Parameter value (bucket ID) for configuration table joins

### 3. `RV_opportunistic_dynamic_ecpm`
**Purpose**: Dynamic eCPM multiplier based on user performance
**Output**: Multiplier value (0.7 to 1.0) applied to minimum ad revenue thresholds

## Current Segmentation Logic (May 2026)

### Segment Definitions
| Segment | Criteria | Purpose |
|---------|----------|---------|
| **NPU** | LTV=0, Level≥300 | Non-paying users, country-based buckets |
| **PUs_last_30D** | LTV>0, Level>100, ≤30 days since purchase | Active recent purchasers, premium treatment |
| **DPU_30_60** | LTV>0, Level>100, 30-60 days since purchase | Recent purchasers, high thresholds |
| **DPU_60_90** | LTV>0, Level>100, 60-90 days since purchase | Moderate purchasers, medium thresholds |
| **DPU_90+** | LTV>0, Level>100, ≥90 days since purchase | Old purchasers, lower thresholds |

### Monetization Strategy
**Revenue Protection Gradient**: More recent purchasers get higher thresholds to protect revenue potential.

- **PUs_last_30D**: Premium parameters (100-400)
- **DPU_30_60**: Highest thresholds (10000-60000) 
- **DPU_60_90**: Medium thresholds (1000-6000)
- **DPU_90+**: Lower thresholds (10-60)

## Configuration Tables

### `sm_draft.RV_opportunistic_min_eCPM_per_segment`
**Rows**: 49 (as of May 2026)
**Structure**: Segment × CZ Bucket × Time Period × Country
**Purpose**: Defines minimum eCPM and ad revenue thresholds per user type

### Current Configuration Summary
| Segment | CZ Buckets | Countries | Time Periods | Total Rows |
|---------|------------|-----------|--------------|------------|
| NPU | 1 | 3 (US/Tier_1/Other) | 3 | 9 |
| PUs_last_30D | 4 | 1 (All) | 1 | 4 |
| DPU_30_60 | 6 | 1 (All) | 1 | 6 |
| DPU_60_90 | 6 | 1 (All) | 1 | 6 |
| DPU_90+ | 6 | 1 (All) | 4 | 24 |

## Parameter Integration Flow

1. **Segmentation**: User classified into segment based on purchase behavior
2. **Bucket Assignment**: User assigned parameter value based on segment + CZ + country
3. **Dynamic Adjustment**: eCPM multiplier applied based on performance (NPU only)
4. **Threshold Application**: Final thresholds used for ad delivery decisions

## Test Group Coverage

**Included Groups**: Test_A, Test_B, Control
**Excluded Groups**: All other groups get default values (no dynamic adjustments)

**Control Group Integration**: As of May 2026, Control group participates in all parameter logic alongside test groups.

## Business Rules

### NPU Users
- **Segmentation**: Country-based (US/Tier_1/Other)
- **Dynamic eCPM**: Performance-based reduction (0.7-1.0 multiplier)
- **Bucket Reduction**: Based on revenue performance vs thresholds

### DPU Users  
- **Segmentation**: Purchase recency-based
- **Static eCPM**: No dynamic adjustments
- **Bucket Reduction**: Applied uniformly across test groups

### Key Thresholds
- **Minimum eCPM Reduction**: 30% (floor of 0.7)
- **Performance Measurement**: max_ad_revenue_per_day vs min_ad_rev
- **Bucket Reduction**: 1-2 bucket decrease maximum per cycle

## Data Sources

### Primary Tables
- `dwh.sm_user_profile`: User LTV, level, transaction history
- `stg.stg_smart_seg_sm_cz_price_cut_test`: CZ values
- `dwh.sm_fact_rv_client_events`: Ad revenue performance
- `sm_ds.abtest_user_allocations`: Test group assignments
- `sm_draft.RV_opportunistic_min_eCPM_per_segment`: Configuration thresholds

### Key Joins
- User segmentation: user_id + profile data
- Configuration: segment + CZ range + country + date range
- Performance: user_id + event date + revenue data