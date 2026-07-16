# Shiny Show - Business Context

**Feature**: Shiny Show RV placement
**Stakeholders**: RV Team, Product, Data Science
**Status**: Live for internal users only

## Business Goals

### Primary Objectives
- Increase RV revenue through strategic placement timing
- Maintain user experience by respecting daily caps
- Ensure proper targeting and segmentation compliance

### Key Performance Indicators (KPIs)
- **Revenue per placement**: Revenue ≥ (min_ecpm_threshold / 1000) * dynamic_ecpm
- **Daily cap compliance**: ≤2 MOLE triggers, ≤1 Extra Pick per user per day
- **Floor targeting accuracy**: 100% compliance with floor requirements
- **Test group accuracy**: Only Test_A and Test_B users receive ads

## Gatekeeping & Validation Rules

### Standard Validations
1. **Test Group Verification**: Only Test_A and Test_B users should receive ads
2. **Floor Validation**: Triggers fire only on correct floors per type
3. **Daily Cap Enforcement**: Respect 2 MOLE + 1 Extra Pick daily limits
4. **eCPM Threshold Compliance**: Revenue meets minimum thresholds
5. **Internal User Restriction**: Currently live only for Playtika internal users
6. **Configuration Alignment**: Behavior matches latest config updates

### Investigation Workflow
When investigating issues:
1. **User Profile Check**: Verify test group assignment and segment
2. **Event Analysis**: Review all Shiny placement impressions and timing 
3. **Floor & Trigger Validation**: Confirm correct floor-trigger combinations
4. **Cap Compliance**: Check daily limits aren't exceeded
5. **eCPM Analysis**: Validate revenue meets thresholds
6. **Configuration Cross-check**: Ensure latest config is applied

## Success Metrics
- **Quality**: Zero violations of business rules
- **Performance**: Revenue targets met per segment
- **Compliance**: 100% adherence to test group restrictions
- **User Experience**: Daily caps respected consistently

## Risk Areas
- Accidental expansion beyond internal users
- Configuration drift causing rule violations
- eCPM threshold miscalculations
- Daily cap overflow during high-activity periods