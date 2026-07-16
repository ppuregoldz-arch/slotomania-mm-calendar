# RV_opportunistic_dynamic_ecpm Parameter Definition

## Overview
**Purpose**: Dynamic eCPM multiplier for NPU users to optimize ad fill rates based on performance
**Output Values**: 0.7-1.0 (multiplier applied to minimum revenue thresholds)
**Scope**: NPU users only - DPU users always receive 1.0 (no reduction)

## Business Logic
The parameter provides additional eCPM threshold reduction for NPU users based on their recent ad revenue performance relative to minimum thresholds. This enables gradual threshold optimization while maintaining revenue floors.

### Optimization Logic
- **NPU-Specific**: Only applied to NPU segment users
- **Performance-Based**: Reduction based on recent revenue vs threshold achievement
- **Safety Floor**: Minimum 0.7 multiplier (maximum 30% reduction)
- **Test Group Scope**: Only active for Test_A, Test_B, Control groups

### Multiplier Calculation
| Performance Condition | Multiplier Value | Impact |
|---------------------|------------------|--------|
| **Meeting thresholds** | 1.0 | No reduction |
| **Moderate underperformance** | 0.9 | 10% threshold reduction |
| **Significant underperformance** | 0.8 | 20% threshold reduction |
| **Maximum underperformance** | 0.7 | 30% threshold reduction (floor) |

### Reset Conditions
The parameter resets to 1.0 (baseline) when:
- User changes bucket assignment
- User changes segment classification
- User achieves threshold for consecutive periods
- Configuration changes occur

## Parameter Query

```sql
select 
    user_id,
    case 
        -- Only NPU users get dynamic eCPM adjustment
        when rv_segment_opportunistic = 'NPU' 
             and group_name in ('Test_A', 'Test_B', 'Control') then
            
            -- Calculate performance ratio over last 2 days
            case 
                when avg_revenue_performance >= min_threshold then 1.0
                when avg_revenue_performance >= (min_threshold * 0.9) then 0.9
                when avg_revenue_performance >= (min_threshold * 0.8) then 0.8
                else 0.7  -- Minimum floor
            end
            
        -- DPU users and other groups always get 1.0 (no reduction)
        else 1.0
    end as RV_opportunistic_dynamic_ecpm,
    
    -- Performance calculation for NPU users
    case 
        when rv_segment_opportunistic = 'NPU' then
            (
                select avg(max_ad_revenue_per_day) 
                from dwh.sm_fact_rv_client_events 
                where user_id = profile.user_id 
                  and promo_date >= current_date - 2
                  and promo_date < current_date
            )
        else null
    end as avg_revenue_performance
    
from dwh.sm_user_profile_datamining_snapshot profile
left join sm_ds.abtest_user_allocations test using (user_id)
left join sm_draft.RV_opportunistic_min_eCPM_per_segment config
    on profile.rv_opportunistic_config_buckets = config.parameter_value
    and current_date - 1 >= config.config_promo_date_from
    and current_date - 1 < config.config_promo_date_to
where profile.snapshot_date = current_date - 1;
```

## Dependencies
- **Segmentation**: `rv_segment_opportunistic = 'NPU'` requirement
- **Test Groups**: `sm_ds.abtest_user_allocations` for optimization eligibility
- **Revenue Data**: `dwh.sm_fact_rv_client_events` for performance calculation
- **Configuration**: `sm_draft.RV_opportunistic_min_eCPM_per_segment` for threshold reference
- **Performance Window**: 2-day lookback for revenue analysis

## Current Configuration (May 2026)
- **Scope**: NPU users in Test_A, Test_B, Control groups only
- **Multiplier Range**: 0.7 to 1.0 (30% maximum reduction)
- **Performance Window**: 2-day rolling average
- **Update Frequency**: Daily calculation with performance lookback
- **Control Group**: Included as of May 2026 update

## Validation Points
- DPU users should always have 1.0 multiplier (no reduction)
- NPU users outside test groups should have 1.0 multiplier
- Multiplier values should be between 0.7 and 1.0 (inclusive)
- Performance calculations should use 2-day window consistently
- Reset conditions should trigger return to 1.0 baseline

## Business Impact
- **Revenue Protection**: 0.7 floor prevents excessive threshold reduction
- **Fill Rate Optimization**: Gradual reduction improves ad serving for underperforming users
- **Test Measurement**: Control group inclusion enables proper A/B testing
- **User Experience**: Maintains ad relevance while optimizing monetization