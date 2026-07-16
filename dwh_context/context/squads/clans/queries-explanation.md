# Clans Squad - Queries

**Note**: This file contains only queries provided by the user, not queries created during conversations.

## Dashboard Analysis - Data Source Intelligence

### Clan Go Dashboard Data Sources Identified
Based on Tableau dashboard analysis, the following analytical frameworks have been identified:

#### Core Clan Go Metrics
- **CLAN GO+BUNDLE+DASH MAX**: Cross-feature integration analysis combining Clan Go, Bundle offers, and Dash Max
- **clan go funnel**: Conversion funnel analysis from clan discovery to active participation
- **clan go mission completion**: Mission-specific completion rates and progression tracking
- **clan go completion**: Overall completion metrics and success rates
- **clan go data**: Core clan go performance and engagement data

#### Performance & Progression Analytics
- **milestone rev share progression till current date**: Revenue attribution and milestone tracking
- **clan feature payout**: Reward distribution and payout analysis
- **clan trophy progression**: Achievement and trophy progression tracking
- **Clan Rank by day**: Daily ranking performance and movement analysis
- **rank status**: Current ranking status and tier distribution

#### Engagement & Funnel Analysis
- **clan go funnel** (multiple variants): Different funnel analysis perspectives
- **bar bonuses**: Clan Go bar progression and bonus mechanics
- **cards_sources**: Card acquisition within clan context
- **mass**: Mass engagement and participation metrics
- **CLAN GO PACKING**: Feature packaging and bundle analysis

#### Technical Infrastructure
- **Vertica Database**: playtika_dwh schema
- **Server**: Verticalb.va2 (primary), verticalb.va2 (secondary)
- **Extract Files**: 24 federated extract files for optimized dashboard performance

## Query Categories (Awaiting User-Provided Queries)

#### Social Engagement Analytics
- Clan participation and activity tracking
- Social interaction metrics and patterns  
- Chat engagement and communication analysis

#### Collaborative Performance
- Communal challenge completion rates
- Clan point earning and distribution
- Chest reward participation metrics

#### Retention & Monetization  
- Clan membership impact on user retention
- Social pressure and collaborative purchasing
- Cross-feature engagement enhancement

#### Clan Go Specific Analytics
- Mission completion and progression funnel
- Trophy and milestone achievement tracking
- Revenue attribution and monetization impact
- Cross-feature integration (Bundle, Dash Max)
- Ranking and competitive performance metrics

#### Trading & Economy
- Inter-clan asset exchange analysis
- Trading volume and pattern tracking
- Economic impact of clan trading system

## Business Intelligence Framework Revealed

### Key Analytical Areas Confirmed
1. **Funnel Analysis**: Multiple clan go funnel perspectives indicating sophisticated conversion tracking
2. **Cross-Feature Integration**: Bundle and Dash Max integration showing ecosystem approach
3. **Revenue Attribution**: Milestone revenue sharing and payout analysis
4. **Competitive Elements**: Ranking, trophy progression, and daily competitive tracking
5. **Mission System**: Completion tracking indicating structured objective framework
6. **Performance Optimization**: Extract-based architecture for real-time dashboard performance

### Technical Architecture
- **Primary Database**: Vertica (playtika_dwh)
- **Dashboard Performance**: 24 federated extracts for optimized query performance
- **Real-Time Capability**: Daily ranking and progression tracking
- **Cross-Schema Integration**: Multiple data source federation

## Core Clan Data Tables

### Clan Creation & Metadata
- **`dwh.sm_clan_profile`** - Primary clan information with accurate creation timestamps
  - `clan_creation_ts` - Exact clan creation time (active data: 1.46M clans, 2019-present)
  - `clan_name`, `clan_type` (PUBLIC/PRIVATE), `admin_user_id` (creator)
  - `members_count`, `member_capacity`, `clan_rank` - Current status
  - **Use for**: Clan creation analysis, clan lifecycle tracking, current clan metrics

### Current Clan Membership
- **`dwh.sm_clan_user_profile`** - Current clan membership snapshot
  - One record per user currently in a clan
  - `join_clan_ts`, `clan_role`, `source_of_join` (Invite/List/etc.)
  - **Use for**: Current membership analysis, clan size calculations

### Historical Clan Activity
- **`dwh.sm_fact_clan_user`** - Historical clan join/leave events
  - All clan membership movements over time
  - Multiple entries per user for clan switching
  - **Use for**: Clan movement patterns, retention within clans, historical analysis

---
**Migration Note**: Actual SQL queries will be added here when explicitly provided by the user. The above represents dashboard architecture intelligence extracted from Tableau workbook analysis.