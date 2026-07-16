# Managed Users Clan Analysis

**Date**: 2026-05-25  
**Purpose**: Extract managed VIP users with clan membership analysis and weak clan identification

## Business Requirements

User requested a query to analyze managed users with the following specifications:

### User Filters:
- **Managed users only**: Users with assigned account managers (from `dwh.sm_dim_vip_account_managers`)
- **Tier 5+ users**: High-tier players only (`tier_id >= 5`)
- **Recently active**: Users active within the past 4 days (using `agg.agg_sm_daily_users_stats`)

### Output Columns:
1. `user_id` - Player identifier
2. `account_manager` - Assigned account manager name
3. `is_clan_member` - Binary flag (1/0) indicating clan membership
4. `num_of_clan_members` - Total clan size including the user
5. `is_weak_clan` - Binary flag (1/0) indicating if clan is "weak"

### Business Logic:
- **Weak clan definition**: Clans with 3 or more users who haven't been active in the past 10+ days
- **Clan membership**: Based on current status in `dwh.sm_clan_user_profile`
- **Activity tracking**: Using daily stats for recent activity validation

## Query Implementation

The query uses a nested structure:

1. **Base set**: Managed users (tier 5+) active in past 4 days
2. **Clan membership**: Left join with current clan profile
3. **Clan size**: Aggregated count of clan members
4. **Weak clan identification**: Complex subquery identifying clans with 3+ inactive users

## Sample Results

Query executed successfully and returns managed users with clan analysis. Example output shows users like:
- User 174 (Nitzan Shaked): clan member in weak clan of 10 members
- User 559 (Nitzan Shaked): clan member in healthy clan of 9 members

## Data Sources

- `dwh.sm_dim_vip_account_managers` - Account manager assignments
- `dwh.sm_user_profile_snapshot` - User tier information
- `agg.agg_sm_daily_users_stats` - User activity tracking
- `dwh.sm_clan_user_profile` - Current clan memberships

## Validation

Query successfully validated with test users showing correct:
- Account manager mapping
- Clan membership status
- Clan size calculations  
- Weak clan identification logic