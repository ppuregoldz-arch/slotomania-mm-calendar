# RV Opportunistic Min eCPM Table - Post-Change Results
**Date**: 2026-05-26  
**Purpose**: Document state after parameter changes and validate configuration

## Summary by Segment (After Changes)
| Segment | Row Count | Change |
|---------|-----------|---------|
| NPU | 9 | ✅ No change |
| DPU_90+ | 24 | ✅ No change |
| PUs_last_30D | 4 | ✅ Renamed (was PUs_last_90D) |
| DPU_60_90 | 6 | ✅ **NEW** |
| DPU_30_60 | 6 | ✅ **NEW** |
| **Total** | **49** | **+12 rows** |

## ✅ Changes Successfully Applied

### 1. Rename Completed ✅
- **OLD**: `PUs_last_90D` (4 rows)
- **NEW**: `PUs_last_30D` (4 rows)
- **Configuration**: Unchanged (same values, dates, CZ ranges)

### 2. New Segments Added ✅

#### DPU_60_90 Segment (6 rows)
- **Date Range**: 2026-05-27 to 2026-11-01
- **Segment Multiplier**: 1000
- **CZ Buckets & Values**:
  ```
  CZ 0.0:        parameter_value=1000,  min_ecpm=40,  min_ad_rev=0.04
  CZ 0.01-4.99:  parameter_value=2000,  min_ecpm=80,  min_ad_rev=0.08
  CZ 5.0-9.99:   parameter_value=3000,  min_ecpm=150, min_ad_rev=0.15
  CZ 10.0-14.99: parameter_value=4000,  min_ecpm=200, min_ad_rev=0.2
  CZ 15.0-24.99: parameter_value=5000,  min_ecpm=300, min_ad_rev=0.3
  CZ 25.0-50.0:  parameter_value=6000,  min_ecpm=400, min_ad_rev=0.4
  ```

#### DPU_30_60 Segment (6 rows)  
- **Date Range**: 2026-05-27 to 2026-11-01
- **Segment Multiplier**: 10000
- **CZ Buckets & Values**:
  ```
  CZ 0.0:        parameter_value=10000, min_ecpm=60,  min_ad_rev=0.06
  CZ 0.01-4.99:  parameter_value=20000, min_ecmp=120, min_ad_rev=0.12
  CZ 5.0-9.99:   parameter_value=30000, min_ecpm=225, min_ad_rev=0.225
  CZ 10.0-14.99: parameter_value=40000, min_ecpm=300, min_ad_rev=0.3
  CZ 15.0-24.99: parameter_value=50000, min_ecpm=400, min_ad_rev=0.4
  CZ 25.0-50.0:  parameter_value=60000, min_ecpm=500, min_ad_rev=0.5
  ```

## Configuration Validation

### ✅ Logical Parameter Value Progression
**DPU Segments by Recency** (Higher values = More restrictive = More recent purchasers):
- **DPU_30_60** (30-60 days): 10000-60000 (Most restrictive - Recent purchasers)
- **DPU_60_90** (60-90 days): 1000-6000 (Medium restrictive)  
- **DPU_90+** (90+ days): 10-60 (Least restrictive - Oldest purchasers)

### ✅ eCPM Value Progression Makes Sense
**Higher eCPMs for more recent purchasers**:
- **DPU_30_60**: 60-500 eCPM (Highest - Recent buyers)
- **DPU_60_90**: 40-400 eCPM (Medium)
- **DPU_90+**: 15-250 eCPM (Lowest - Old buyers)

### ✅ Ad Revenue Thresholds Align
**min_ad_rev follows same pattern**:
- **DPU_30_60**: $0.06-$0.50 (Highest thresholds)
- **DPU_60_90**: $0.04-$0.40 (Medium thresholds)  
- **DPU_90+**: $0.015-$0.25 (Lowest thresholds)

## Risk Assessment: ✅ LOW RISK

### Population Impact Analysis:
1. **NPU users**: No change ✅
2. **DPU_90+ users**: No change ✅  
3. **PUs_last_30D**: Same configuration, just renamed ✅
4. **New DPU_30_60 population**: Will get appropriate high thresholds ✅
5. **New DPU_60_90 population**: Will get moderate thresholds ✅

### Configuration Logic: ✅ CORRECT
- Values increase appropriately with CZ buckets
- Recent purchasers have higher thresholds (as intended)
- Segment multipliers are distinct and appropriate
- Date ranges are properly set for new segments