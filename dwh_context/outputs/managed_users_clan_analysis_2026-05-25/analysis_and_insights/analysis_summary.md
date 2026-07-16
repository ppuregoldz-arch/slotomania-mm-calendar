# Managed Users Clan Analysis - Key Findings

**Analysis Date**: 2026-05-25  
**Query Validation**: ✅ Passed  
**Data Sources**: VIP Account Managers, User Profiles, Daily Activity Stats, Clan Membership

## Executive Summary

Analysis of managed VIP users (tier 5+) reveals clan membership patterns and identifies users in potentially problematic clans requiring attention.

## Key Findings

### User Population
- **Target Population**: Managed users with account managers, tier 5+, active within 4 days
- **Sample Results**: Users managed by Nitzan Shaked, Robert Ursea, Nikita Sinha confirmed in dataset
- **Activity Filter**: Successfully limited to recently active high-value users

### Clan Membership Patterns
- **Mixed Membership**: Both clan members and solo players identified in managed user base
- **Clan Sizes**: Range from 9-14 members in sample clans
- **Engagement Variation**: Clear distinction between healthy and weak clans

### Weak Clan Identification
- **Threshold Applied**: 3+ users inactive for 10+ days classifies clan as "weak"
- **Results**: Multiple managed users identified in weak clans
- **Example**: User 559 in healthy clan (9 members) vs. Users 174, 250 in weak clans (10+ members)

## Business Implications

### For VIP Management
- **Intervention Opportunities**: Managed users in weak clans may need engagement support
- **Account Manager Insights**: Distribution shows which managers have users in problematic clans
- **Retention Risk**: Users in weak clans may have higher churn risk due to reduced social engagement

### For Clan Strategy
- **Size vs. Health**: Larger clans not necessarily healthier (10+ member clans showing weakness)
- **Activity Patterns**: Clear indicators available for clan health assessment
- **Managed User Impact**: VIP users may be carrying inactive clans

## Recommendations

### Immediate Actions
1. **Account Manager Review**: Share weak clan lists with respective account managers
2. **Clan Health Monitoring**: Implement regular tracking of managed user clan health
3. **Engagement Initiatives**: Consider clan-focused retention programs for VIP users

### Strategic Considerations
1. **Clan Assignment Strategy**: Evaluate if managed users should be guided toward healthier clans
2. **VIP Clan Programs**: Develop exclusive clan features for high-tier managed users
3. **Cross-Functional Collaboration**: Align VIP management with clan engagement teams

## Data Quality Notes

- **Validation Confirmed**: Manual verification of sample users shows accurate results
- **Current State**: Analysis reflects current clan membership, not historical patterns
- **Activity Reliability**: Using aggregated daily stats provides consistent activity measurement
- **Binary Simplicity**: Clear 1/0 flags enable straightforward business decision-making

## Technical Implementation Success

- **Query Performance**: Efficient execution with proper indexing on date fields
- **Data Accuracy**: Cross-validated user examples confirm logic correctness
- **Scalability**: Structure supports regular refresh for ongoing monitoring
- **Business Usability**: Output format ready for dashboard integration or executive reporting