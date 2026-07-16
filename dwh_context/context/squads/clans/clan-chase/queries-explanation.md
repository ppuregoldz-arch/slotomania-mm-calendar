# Clan Chase - Queries

**Note**: This file contains only queries provided by the user, not queries created during conversations.

## Dashboard Intelligence - Clans Dashboard EQ Analysis

### Clans Dashboard EQ Data Sources Identified
Based on Tableau dashboard analysis for competitive clan analytics:

#### Competition & Performance Metrics
- **Clan Participation Tracking**: Seasonal participation and eligibility analysis
- **Session-Based Analysis**: `dwh.fact_sm_sessions_kafka` integration for engagement tracking
- **Bonus Collection Metrics**: `dwh.fact_sm_bonus_history` and `dwh.dim_sm_bonus_type` integration
- **A/B Testing Framework**: `sm_draft.clan_ids_with_hashes_18_09_24` for test/control allocation

#### Technical Infrastructure Revealed
- **Primary Tables Identified**:
  - `dwh.sm_clan_user_profile` - Core clan membership data
  - `agg.agg_sm_daily_side_games_promotion_stats` - Daily clan activity aggregations
  - `dwh.fact_sm_sessions_kafka` - Session-level engagement tracking
  - `dwh.fact_sm_bonus_history` - Bonus collection and reward tracking
  - `dwh.fact_sm_goods_service_data` - Additional reward mechanism tracking

#### Business Logic Patterns Discovered
- **Seasonal Structure**: 7-day seasons (from_promo_date to to_promo_date + 6 days)
- **Eligibility Criteria**: `user_current_point >> 30` threshold for participation eligibility
- **Test Group Logic**: `case when a.is_test = 1 then 'Test' else 'Control' end`
- **User Exclusions**: Standard Playtika user and journey step 539265 filtering
- **Session Filtering**: `session_creation_ts >= '2024-09-16 11:00'` indicating test start date

#### Key Metrics Framework
- **clan_participants**: Total clan members participating
- **clan_eligible_participants**: Members meeting eligibility criteria (>30 points)
- **bonus_collected**: Active bonus collection during competition periods
- **season_counter**: Sequential season numbering for trend analysis

## Query Categories (Awaiting User-Provided Queries)

#### Competition Performance
- Clan participation and ranking analysis using `sm_clan_user_profile`
- Individual contribution tracking during events via session data
- Competition completion and progression metrics with bonus integration

#### Social Dynamics  
- Clan collaboration patterns during competitions
- Cross-clan interaction and rivalry analysis
- Leadership emergence through point contribution analysis

#### A/B Testing & Experimentation
- Test vs Control group performance comparison
- Clan-level A/B test impact analysis
- Feature rollout and competitive balance validation

#### Seasonal Analysis
- 7-day season performance tracking and comparison
- Seasonal progression and milestone achievement
- Cross-season retention and engagement evolution

#### Business Impact
- Competition-driven monetization through bonus systems
- Retention impact of competitive participation
- Premium feature adoption during competitive events

#### Technical Quality Assurance
- Eligibility threshold validation (30+ points)
- Session data integrity and timeline verification
- Bonus collection accuracy and distribution fairness

## Business Intelligence Framework

### Competition Architecture
1. **Seasonal Structure**: 7-day competitive cycles with clear start/end boundaries
2. **Eligibility System**: Point-based participation thresholds (30+ points)
3. **A/B Testing**: Structured test vs control clan allocation
4. **Multi-Table Integration**: Session, bonus, and clan data unified analysis

### Key Performance Indicators
- **Participation Rate**: Eligible clan members actively competing
- **Engagement Depth**: Session frequency and bonus collection during competitions  
- **Competitive Balance**: Test vs control performance parity
- **Retention Impact**: Competition participation effect on ongoing engagement

---
**Migration Note**: Actual competitive SQL queries will be added here when explicitly provided by the user. The above represents competitive framework intelligence extracted from Clans Dashboard EQ workbook analysis.