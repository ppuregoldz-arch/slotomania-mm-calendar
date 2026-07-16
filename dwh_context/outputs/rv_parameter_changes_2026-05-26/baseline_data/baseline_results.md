# RV Opportunistic Min eCPM Table - Baseline Results
**Date**: 2026-05-26  
**Purpose**: Document current state before parameter changes

## Summary by Segment
| Segment | Row Count |
|---------|-----------|
| DPU_90+ | 24 |
| NPU | 9 |
| PUs_last_90D | 4 |
| **Total** | **37** |

## Current Segment Structure

### 1. NPU Segment (9 rows)
- **Countries**: US, Tier_1, Other
- **CZ Range**: 0.0 to 9999999999.0 (all CZ values)
- **Parameter Values**: 1 (US), 2 (Tier_1), 3 (Other)
- **Segment Multiplier**: 1
- **Date Ranges**: 2026-02-16 to 2026-07-01 (3 time periods)

### 2. PUs_last_90D Segment (4 rows) - **TO BE RENAMED**
- **Country**: All
- **CZ Ranges**: 0.0-0.0, 0.01-4.99, 5.0-9.99, 10.0-14.99
- **Parameter Values**: 100, 200, 300, 400
- **Segment Multiplier**: 100
- **Date Range**: 2026-02-16 to 2026-07-01 (single period)

### 3. DPU_90+ Segment (24 rows)
- **Country**: All
- **CZ Ranges**: 0.0-0.0, 0.01-4.99, 5.0-9.99, 10.0-14.99, 15.0-24.99, 25.0-49.99
- **Parameter Values**: 10, 20, 30, 40, 50, 60
- **Segment Multiplier**: 10
- **Date Ranges**: Multiple periods from 2026-02-16 to 2026-11-01

## Expected Changes
1. **Rename**: `PUs_last_90D` → `PUs_last_30D`
2. **Add**: `DPU_30_60` segment (new bucket for DPU 30-60 days)
3. **Add**: `DPU_60_90` segment (new bucket for DPU 60-90 days)

## Baseline Data Details

### NPU Segment Details
```
US: parameter_value=1, min_ad_rev: 0.025/0.015/0.015 (by date)
Tier_1: parameter_value=2, min_ad_rev: 0.025/0.015/0.01 (by date)  
Other: parameter_value=3, min_ad_rev: 0.025/0.015/0.007 (by date)
```

### PUs_last_90D Details (Current - To Be Changed)
```
CZ 0.0: parameter_value=100, min_ad_rev=0.13
CZ 0.01-4.99: parameter_value=200, min_ad_rev=0.2
CZ 5.0-9.99: parameter_value=300, min_ad_rev=0.3
CZ 10.0-14.99: parameter_value=400, min_ad_rev=0.5
```

### DPU_90+ Details
```
6 CZ buckets × 4 time periods = 24 rows
CZ ranges: 0.0, 0.01-4.99, 5.0-9.99, 10.0-14.99, 15.0-24.99, 25.0-49.99
Parameter values: 10, 20, 30, 40, 50, 60
Time periods: 2026-02-16→02-24, 02-24→03-16, 03-16→05-19, 05-19→11-01
```