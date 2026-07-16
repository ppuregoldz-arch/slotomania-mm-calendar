# rv_segment_opportunistic Parameter Definition

## Overview
**Purpose**: User segmentation based on payment behavior and recency for RV (Rewarded Video) targeting
**Output Values**: NPU, PUs_last_30D, DPU_30_60, DPU_60_90, DPU_90+
**Scope**: Core segmentation logic for all RV parameter calculations

## Business Logic
The parameter classifies users into segments based on their payment history and time since last purchase to enable targeted ad serving with appropriate revenue thresholds.

### Segmentation Criteria
| Segment | Criteria | Business Purpose |
|---------|----------|------------------|
| **NPU** | LTV=0, Level≥300 | Non-paying users eligible for RV |
| **PUs_last_30D** | LTV>0, Level>100, ≤30 days since purchase | Active recent purchasers |
| **DPU_30_60** | LTV>0, Level>100, 30-60 days since purchase | Recent dormant purchasers |
| **DPU_60_90** | LTV>0, Level>100, 60-90 days since purchase | Moderate dormant purchasers |
| **DPU_90+** | LTV>0, Level>100, ≥90 days since purchase | Long-dormant purchasers |

### Monetization Strategy
- **Revenue Protection Gradient**: More recent purchasers receive higher thresholds to protect revenue potential
- **Engagement Recovery**: Dormant purchasers targeted with progressively lower thresholds based on recency
- **NPU Optimization**: Non-payers receive country-based targeting with dynamic optimization

## Parameter Query

```sql
select 
    user_id,
    case 
        when ltv = 0 and level >= 300 then 'NPU'
        when ltv > 0 and level > 100 and days_since_last_purchase <= 30 then 'PUs_last_30D'
        when ltv > 0 and level > 100 and days_since_last_purchase between 31 and 60 then 'DPU_30_60'
        when ltv > 0 and level > 100 and days_since_last_purchase between 61 and 90 then 'DPU_60_90'
        when ltv > 0 and level > 100 and days_since_last_purchase > 90 then 'DPU_90+'
        else null
    end as rv_segment_opportunistic
from dwh.sm_user_profile_datamining_snapshot
where snapshot_date = current_date - 1;
```

## Dependencies
- **User Profile Data**: `dwh.sm_user_profile_datamining_snapshot`
- **LTV Calculation**: Total lifetime value in USD
- **Level Progression**: User level from game progression
- **Transaction History**: Last purchase date calculation
- **Downstream Parameters**: Feeds into `rv_opportunistic_config_buckets` calculation

## Current Configuration (May 2026)
- **Active Segments**: 5 segments (expanded from 3 in May 2026)
- **Level Threshold**: 300 for NPU, 100 for DPU segments
- **Date Calculation**: Based on most recent purchase transaction
- **Update Frequency**: Daily via datamining snapshot

## Validation Points
- Segment distribution should align with user base composition
- No users should have null segments if meeting basic criteria
- Segment transitions should follow expected patterns over time
- Cross-validation with transaction history for recency accuracy