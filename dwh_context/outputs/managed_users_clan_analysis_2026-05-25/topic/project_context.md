# Managed Users Clan Analysis - Project Context

**Date**: 2026-05-25  
**Analyst**: Slotomania Analytics Specialist

## Why This Analysis Was Created

User requested a comprehensive analysis of managed VIP users and their clan characteristics to understand:
- The distribution of high-tier managed users across clans
- Which account managers are responsible for users in problematic ("weak") clans
- The relationship between VIP management and clan engagement patterns

## Business Question Being Answered

**Primary Question**: What is the clan membership status and clan health situation for our managed VIP users (tier 5+)?

**Secondary Questions**:
- How many managed users are in clans vs. solo players?
- Which clans containing managed users have engagement problems?
- Are there patterns in weak clan membership by account manager?

## Context That Led to This Analysis

This appears to be part of a broader VIP management review, likely to:
1. Identify managed users who might benefit from clan engagement initiatives
2. Flag account managers who have users in underperforming clans
3. Understand if clan membership impacts VIP user retention/engagement

## Key Assumptions Made

- **Managed User Definition**: Users with non-null account managers in `dwh.sm_dim_vip_account_managers`
- **Tier Threshold**: Tier 5+ represents high-value VIP users worth analyzing
- **Activity Definition**: Recent activity = active within past 4 days
- **Weak Clan Threshold**: 3+ inactive users (10+ days) indicates clan health problems
- **Current State Analysis**: Using current clan membership, not historical

## Important Decisions Made

1. **Activity Tracking**: Used `agg.agg_sm_daily_users_stats` for reliable activity data
2. **Tier Filtering**: Applied tier filter using `tier_id >= 5` from user profile snapshot
3. **Binary Flags**: Delivered simple 1/0 flags for easy business use
4. **Clan Size Inclusion**: Included total clan members for context analysis
5. **Weak Clan Logic**: Conservative approach (3+ inactive) to avoid false positives

## Results Interpretation

- Query successfully identified managed users with clan analysis
- Mixed results show both healthy and weak clan participation
- Account managers like Nitzan Shaked managing users across various clan health levels
- Results enable targeted interventions for users in weak clans

## Next Steps Identified

Based on results, potential follow-up analyses:
1. Correlation between weak clan membership and VIP user spending patterns
2. Account manager performance metrics including clan health of managed users
3. Clan intervention recommendations for managed users in weak clans
4. Historical trending of clan health for managed user portfolio