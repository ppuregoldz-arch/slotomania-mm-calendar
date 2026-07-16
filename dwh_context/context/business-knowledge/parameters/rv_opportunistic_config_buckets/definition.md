# rv_opportunistic_config_buckets Parameter Definition

## Overview
**Purpose**: Dynamic bucket assignment and reduction logic for RV configuration table joins
**Output Values**: 1-60000 (parameter values linking to configuration thresholds)
**Scope**: Links user segments to specific configuration rules with dynamic optimization

## Business Logic
The parameter assigns users to configuration buckets based on their segment, CZ value, and country, with dynamic reduction logic for test groups to optimize ad fill and revenue performance.

### Bucket Assignment Logic

#### NPU Users (Country-Based)
| Country Tier | Parameter Value | Logic |
|--------------|----------------|--------|
| **US** | 1 | Premium country, highest thresholds |
| **Tier_1** | 2 | High-value countries |
| **Other** | 3 | Remaining countries |

#### DPU Users (CZ-Based with Ranges)

**PUs_last_30D (Recent Purchasers)**:
| CZ Range | Parameter Value |
|----------|----------------|
| 0.0 | 100 |
| 0.01-4.99 | 200 |
| 5.0-9.99 | 300 |
| 10.0-14.99 | 400 |

**DPU_30_60 (High Protection)**:
| CZ Range | Parameter Value |
|----------|----------------|
| 0.0 | 10000 |
| 0.01-4.99 | 20000 |
| 5.0-9.99 | 30000 |
| 10.0-14.99 | 40000 |
| 15.0-24.99 | 50000 |
| 25.0-50.0 | 60000 |

**DPU_60_90 (Medium Protection)**:
| CZ Range | Parameter Value |
|----------|----------------|
| 0.0 | 1000 |
| 0.01-4.99 | 2000 |
| 5.0-9.99 | 3000 |
| 10.0-14.99 | 4000 |
| 15.0-24.99 | 5000 |
| 25.0-50.0 | 6000 |

**DPU_90+ (Lower Protection)**:
| CZ Range | Parameter Value |
|----------|----------------|
| 0.0 | 10 |
| 0.01-4.99 | 20 |
| 5.0-9.99 | 30 |
| 10.0-14.99 | 40 |
| 15.0-24.99 | 50 |
| 25.0-50.0 | 60 |

### Dynamic Reduction Logic
- **Test Groups Only**: Test_A, Test_B, Control get dynamic optimization
- **Performance-Based**: Bucket reduction based on revenue vs thresholds
- **Maximum Reduction**: Up to 2 bucket levels per optimization cycle
- **Safety Mechanism**: Prevents excessive threshold lowering

## Parameter Query

```sql
select 
    user_id,
    case 
        -- NPU users: country-based buckets
        when rv_segment_opportunistic = 'NPU' then
            case 
                when country_tier = 'US' then 1
                when country_tier = 'Tier_1' then 2
                when country_tier = 'Other' then 3
                else null
            end
        
        -- PUs_last_30D: CZ-based buckets (100s range)
        when rv_segment_opportunistic = 'PUs_last_30D' then
            case 
                when cz_price_cut_test = 0 then 100
                when cz_price_cut_test between 0.01 and 4.99 then 200
                when cz_price_cut_test between 5.0 and 9.99 then 300
                when cz_price_cut_test between 10.0 and 14.99 then 400
                else null
            end
            
        -- DPU_30_60: CZ-based buckets (10000s range)
        when rv_segment_opportunistic = 'DPU_30_60' then
            case 
                when cz_price_cut_test = 0 then 10000
                when cz_price_cut_test between 0.01 and 4.99 then 20000
                when cz_price_cut_test between 5.0 and 9.99 then 30000
                when cz_price_cut_test between 10.0 and 14.99 then 40000
                when cz_price_cut_test between 15.0 and 24.99 then 50000
                when cz_price_cut_test between 25.0 and 50.0 then 60000
                else null
            end
            
        -- DPU_60_90: CZ-based buckets (1000s range)
        when rv_segment_opportunistic = 'DPU_60_90' then
            case 
                when cz_price_cut_test = 0 then 1000
                when cz_price_cut_test between 0.01 and 4.99 then 2000
                when cz_price_cut_test between 5.0 and 9.99 then 3000
                when cz_price_cut_test between 10.0 and 14.99 then 4000
                when cz_price_cut_test between 15.0 and 24.99 then 5000
                when cz_price_cut_test between 25.0 and 50.0 then 6000
                else null
            end
            
        -- DPU_90+: CZ-based buckets (10s range)  
        when rv_segment_opportunistic = 'DPU_90+' then
            case 
                when cz_price_cut_test = 0 then 10
                when cz_price_cut_test between 0.01 and 4.99 then 20
                when cz_price_cut_test between 5.0 and 9.99 then 30
                when cz_price_cut_test between 10.0 and 14.99 then 40
                when cz_price_cut_test between 15.0 and 24.99 then 50
                when cz_price_cut_test between 25.0 and 50.0 then 60
                else null
            end
        else null
    end as rv_opportunistic_config_buckets,
    
    -- Apply dynamic reduction for test groups only
    case 
        when group_name in ('Test_A', 'Test_B', 'Control') then
            -- Apply bucket reduction logic based on performance
            -- (Complex reduction logic based on revenue performance)
        else rv_opportunistic_config_buckets -- Static for other groups
    end as final_bucket_value
    
from dwh.sm_user_profile_datamining_snapshot
left join sm_ds.abtest_user_allocations using (user_id)
where snapshot_date = current_date - 1;
```

## Dependencies
- **Segmentation**: `rv_segment_opportunistic` parameter output
- **CZ Data**: `cz_price_cut_test` from user profile snapshot  
- **Country Mapping**: Country tier classification (US/Tier_1/Other)
- **Test Groups**: `sm_ds.abtest_user_allocations` for optimization eligibility
- **Configuration Table**: `sm_draft.RV_opportunistic_min_eCPM_per_segment` for threshold lookup

## Current Configuration (May 2026)
- **Parameter Range**: 1-60000 (expanded ranges for new segments)
- **Test Group Optimization**: Active for Test_A, Test_B, Control
- **Bucket Reduction**: Maximum 2-level decrease per cycle
- **Update Frequency**: Daily via datamining snapshot with performance lookback

## Validation Points
- Parameter values should align with configuration table parameter_value column
- Test group users should have dynamic buckets, others static
- CZ ranges should not overlap or have gaps
- Bucket reduction should respect maximum decrease limits