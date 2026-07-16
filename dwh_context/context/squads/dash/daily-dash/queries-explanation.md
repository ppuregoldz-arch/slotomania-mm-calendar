# Daily Dash Squad - Queries

**Note**: This file contains only queries provided by the user, not queries created during conversations.

## Dashboard Intelligence & Wiki Analysis

### Daily Dash Dashboard Data Sources Identified (121 sources)
From New Daily Dash Dashboard analysis, key analytical frameworks:

#### Core Performance Metrics
- **Daily Dash Finishing Rate**: Completion rate analysis and user progression tracking
- **User Share & Revenue Share**: Revenue attribution and user segment performance
- **Revenue & PU by Segment**: Monetization analysis across different user segments
- **Daily Dash Monthly Unique PU**: Monthly paying user acquisition and retention
- **Repurchase Dash**: Repeat purchase behavior and subscription retention analysis

#### Progression & Engagement Analytics
- **Daily User Progression**: Individual user progression through daily challenges
- **Each Day and Max Progression**: Daily progression limits and peak performance
- **Completion PU**: Paying user completion rates and conversion analysis
- **Dash Finishers**: Challenge completion and daily dash finishing behavior
- **Mission Percentiles**: Challenge difficulty distribution and completion percentiles

#### Premium Feature Analysis
- **Super Dashes**: Premium challenge completion and engagement metrics
- **Super Dashes Finished**: Premium subscription utilization and success rates
- **Number of Super Dashes Finishing**: Premium feature adoption and completion
- **Coins Amount for Dash**: Currency economy and reward distribution analysis

#### Cross-Feature Integration
- **SKUs from Daily Dash**: Product integration and monetization tracking
- **Swap Shop**: Cross-feature economy and exchange mechanisms
- **Rewarded per Source Points**: Multi-source reward attribution analysis
- **Dash Points Current Amount**: Point economy and balance management

### Super Dash Views Intelligence (16 sources)
Specialized analytics for premium Daily Dash features:

#### Percentile Analysis Framework
- **SD Daily Percentiles**: Super Dash user performance distribution
- **Daily Running Total SD/DD Percentiles**: Cumulative performance tracking
- **Bar Finishers**: Progression bar completion analysis
- **Percentiles SD**: Super Dash difficulty and completion distribution

### Challenge Rules Framework (Wiki Analysis)

#### Rule System Architecture
- **Rule ID Range**: 159010000-159010129+ for different challenge categories
- **JSON Configuration**: `jstrue{target, conditions}` dynamic parameter system
- **Asset Integration**: Challenge UI assets and localization key mapping
- **BI Parameter Mapping**: Challenge metrics linked to specific BI tracking parameters

#### Challenge Categories Documented

##### Core Gameplay (159010000-159010003)
- **Level Up**: `levelUp 2` - Level progression challenges
- **Bet Coins**: `bet 1000` - Wagering-based objectives with spin limits
- **Win Coins**: `win 10000` - Winning-based challenges with machine targeting
- **Spin Count**: `spin 1000` - Spin frequency and engagement challenges

##### Bonus & Reward Collection (159010004-159010009)
- **Bonus Collection**: Various bonus types including Store Bonus (bonus_type 43)
- **SlotoCards**: Card collection by type, rarity, and star rating
- **Club Points**: `collectClubPoints 1000` - Social currency challenges
- **Card Stars**: `collectCardsStars 10` - Card progression and quality metrics

##### Cross-Feature Integration (159010050+)
- **Clan Points**: `clanPoints 10` - Social feature integration challenges
- **Gems Usage**: `get 6 gems` / `use 7 gems` - Premium currency challenges
- **Super Dash**: `timeChallenges 5 feature super-dash` - Premium feature challenges
- **Mega Pods**: Various pod type challenges (Common, Rare, Epic, Legendary, Xtreme)

##### Seasonal & Feature-Specific (159010070+)
- **Blast Games**: Pick usage, board completion, jackpot mechanics
- **Battle Sheep**: Wolf ships, parasheep usage, airstrikes, board completion
- **SlotoQuest**: Mission completion, booster usage, machine interaction
- **Snakes & Ladders**: Dice usage, board progression, tile movement

### Technical Implementation Patterns

#### Challenge Validation Logic
```json
// Example challenge configuration
{
  "target": 1000,
  "conditions": {
    "machines": [7, 275],
    "spinLimit": 20,
    "anteBetFeature": "MEGA_POD"
  }
}
```

#### BI Parameter Integration
- **Mission Parameters**: `simple_avg_levels`, `sq_wager`, `simple_median_spins`
- **Prize Parameters**: Corresponding reward tracking metrics
- **Relifer Parameters**: Relief/seasonal feature specific tracking
- **Validation Rules**: Challenge eligibility and completion criteria

### Core Table Identified
- **Primary Table**: `dwh.sm_fact_daily_dash_challenges`
- **Key Fields**: user_id, event_ts, status ('finished'), rule_id, challenge_data
- **Status Values**: 'finished' indicates completed challenges
- **Rule Integration**: rule_id maps to challenge type and configuration

### Example Query Pattern (from Documentation)
```sql
-- How many users finished N daily-dash challenges yesterday, by N?
SELECT challenges_finish, promo_date, COUNT(DISTINCT user_id) AS users
FROM (
  SELECT user_id,
         DATE( CASE
                 WHEN DATEDIFF('hh', event_ts AT TIME ZONE 'Asia/Jerusalem', event_ts AT TIME ZONE 'UTC') = 2
                 THEN event_ts - INTERVAL '12 hour' ELSE event_ts - INTERVAL '11 hour' END
         ) AS promo_date,
         COUNT(*) AS challenges_finish
  FROM dwh.sm_fact_daily_dash_challenges
  WHERE status = 'finished' AND event_ts >= CURRENT_DATE - 30
  GROUP BY 1,2
) a
GROUP BY 1,2;
```

## Query Categories (Awaiting User-Provided Queries)

### Core Engagement Analytics
- Daily challenge completion rates and patterns
- Challenge type effectiveness and optimization
- User progression through daily and weekly bars
- Cross-challenge completion correlation analysis

### Retention & Behavioral Analysis
- Daily Dash participation impact on user retention
- Challenge streak analysis and lifetime value correlation
- Session frequency patterns around challenge reset timing
- Drop-off analysis by challenge difficulty and type

### Premium Feature Performance
- Super Dash gem spending and skip behavior analysis
- Daily Dash Max subscription conversion and retention tracking
- Premium vs free user engagement and progression comparison
- Revenue attribution and cross-feature monetization impact

### Technical Quality Assurance
- Challenge reset timing validation and completion accuracy
- Promo date alignment verification for daily boundaries
- Reward distribution and progression bar integrity checks
- Cross-platform completion sync and consistency validation

### Cross-Feature Integration
- Daily Dash challenge impact on other feature engagement
- Wild Card distribution through Dash Max and album integration
- VIP platform bonus points and enhanced reward tracking
- Clan challenge integration and social progression analysis

### Seasonal & Temporal Analysis
- Bi-weekly progression cycle analysis and optimization
- Seasonal challenge performance and content effectiveness
- Day-of-week and time-of-day completion pattern analysis
- Holiday and special event impact on daily challenge engagement

## Business Intelligence Framework

### Challenge Architecture
1. **Daily Structure**: 4 challenges reset at 14:00 IL with immediate completion tracking
2. **Progression System**: Dual-layer progression (daily + bi-weekly) with graduated rewards
3. **Premium Integration**: Gem-based skips and subscription model for enhanced experience
4. **Cross-Feature Connectivity**: Challenges drive engagement across multiple game systems

### Key Performance Indicators
- **Completion Rate**: Daily and per-challenge completion percentage
- **Retention Impact**: Users with dash engagement vs without
- **Monetization Efficiency**: Revenue per dash user and conversion rates
- **Content Performance**: Individual challenge effectiveness and optimization needs

### Technical Implementation
- **Promo Date Alignment**: Challenge reset synchronized with game's canonical day boundary
- **Status Tracking**: Real-time completion monitoring with 'finished' status validation
- **Cross-Platform Consistency**: Challenge progress sync across all player platforms
- **Performance Optimization**: Efficient completion tracking for real-time user feedback

---
**Migration Note**: Actual Daily Dash SQL queries will be added here when explicitly provided by the user. The above represents technical framework and business logic patterns extracted from onboarding documentation and system analysis.