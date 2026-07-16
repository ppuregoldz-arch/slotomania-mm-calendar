# DPU 60-90 Gatekeeping - Launch Validation

**Date**: 2026-05-27  
**Purpose**: Comprehensive gatekeeping for DPU_60_90 segment launch  
**Scope**: Validate ads serving, eCPM thresholds, coin values, and placement rules

## Background

DPU 60-90 day users were previously classified as 'PU' and not receiving ads. As of 2026-05-27, they will be targeted with the new `DPU_60_90` segment with parameter values 1000-6000 and eCPM thresholds $0.04-$0.40.

## Key Validation Requirements

### 1. **Ad Serving Timeline**
- **Today (2026-05-26)**: DPU_60_90 users should have 0 ad events
- **Tomorrow (2026-05-27)**: DPU_60_90 users should receive ads across all placements

### 2. **eCPM Thresholds**  
- Revenue must meet minimum thresholds: $0.04-$0.40 based on CZ buckets
- Parameter values: 1000, 2000, 3000, 4000, 5000, 6000
- Dynamic eCPM multiplier should apply (NPU only, but validate DPU gets 1.0)

### 3. **Coin Value Configuration**
- Bonus amounts must match configuration calculations
- Expected ranges: 708,750 - 8,700,000 coins based on bucket and revenue
- Gems: ~30 for DPU_60_90 users
- Powerups/Picks: 2 units standard

### 4. **Placement-Specific Rules**
- **Shiny Show**: Floor restrictions (MOLE 6-12, Extra Pick floor 10)
- **Offers**: Correct template IDs (221777 DPU Back to Lobby, 222145 DPU ROOC)
- **Cloud**: General availability validation

## Expected Population

Based on diagnostic data:
- **DPU_60_90 users**: ~22,787 users in segment
- **Test groups**: Should be Test_A, Test_B, Control only
- **Parameter range**: 1000-6000 (not 100-400 fallback)

## Risk Areas

### Configuration Issues
- **Date mismatch**: Config starts 2026-05-27, ensure parameter calculation aligns
- **Fallback behavior**: Users getting wrong parameter values if join fails
- **Test group exclusion**: Non-test users should not receive optimization

### Revenue Validation  
- **Threshold compliance**: All revenue must meet min eCPM requirements
- **CZ bucket matching**: Correct thresholds based on user CZ values
- **Dynamic multiplier**: Should be 1.0 for DPU users (not NPU reduction logic)

### Placement Compliance
- **Shiny Show floors**: Strict floor requirements must be enforced
- **Template IDs**: DPU users should get DPU-specific offer templates
- **Daily caps**: Shiny Show daily limits must be respected

## Success Criteria

### ✅ **PASS Conditions:**
1. **Zero ad events today** for DPU_60_90 users
2. **Ad events tomorrow** for DPU_60_90 users across all placements  
3. **100% eCPM compliance** - all revenue >= thresholds
4. **Bonus amount accuracy** - matches configuration calculations
5. **Placement rule compliance** - floors, templates, test groups correct

### ❌ **FAIL Conditions:**
- Any ad events today for DPU_60_90 users
- No ad events tomorrow for DPU_60_90 users  
- Revenue below eCPM thresholds
- Incorrect bonus amounts vs configuration
- Wrong template IDs or floor violations
- Non-test users receiving ads

## Query Execution Plan

### Pre-Launch (Today)
1. **Query 1**: Confirm 0 ad load events for DPU_60_90
2. **Population check**: Validate ~22k users in DPU_60_90 segment
3. **Config validation**: Verify parameter table ready for tomorrow

### Post-Launch (Tomorrow)  
1. **Query 1**: Confirm ad load events across all placements
2. **Query 2**: eCPM threshold compliance validation
3. **Query 3**: Coin value configuration accuracy
4. **Query 4**: Placement-specific rule compliance

### Monitoring Schedule
- **Hour 1**: Initial validation after launch
- **Hour 6**: Mid-day validation
- **EOD**: Full day validation and summary

## Escalation Plan

### Issues Found
- **Config mismatch**: Coordinate with data engineering for parameter fixes
- **Revenue violations**: Review eCPM configuration and AppLovin settings
- **Placement errors**: Validate game client logic and placement triggers

### Success Confirmation
- **Document results**: Population size, compliance rates, revenue performance  
- **Update context**: Add validation results to RV parameter documentation
- **Prepare DPU_30_60**: Use learnings for next segment launch