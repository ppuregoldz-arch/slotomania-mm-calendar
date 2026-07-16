# X-Hunt System - General Engagement Mechanism

## System Overview

**X-Hunt** is a **flexible engagement framework** used across multiple features in Slotomania. It's not feature-specific but rather a **general progression/chase mechanism** that can be applied to different contexts (clans, individual events, seasonal activities, etc.).

## Core Architecture

### Primary Data Table
**`dwh.sm_fact_xhunt_progress_event`** - Universal X-Hunt progression tracking
- **`chase_id`**: Unique identifier for each hunt/chase instance
- **`user_id`**: Participant identifier  
- **`event_date`**: Progression timestamp
- **`current_steps`**: User's current progression level in the hunt
- **Flexible Design**: Can serve multiple feature types and contexts

### X-Hunt Types & Applications

#### 1. **Clan X-Hunt** (Example: Clan Chase)
- **User Base**: Clan members participating in group hunts
- **Progression**: Collective or individual advancement through steps
- **Data Source**: `dwh.sm_fact_xhunt_progress_event` + clan user filtering

#### 2. **Individual X-Hunt** (Seasonal Events, Personal Challenges)
- **User Base**: Individual players in timed events
- **Progression**: Personal advancement through challenge steps
- **Data Source**: `dwh.sm_fact_xhunt_progress_event` + event-specific filtering

#### 3. **Simulation X-Hunt** (What-If Analysis)
- **User Base**: Hypothetical user cohorts (e.g., "all clan users")
- **Progression**: Modeled progression for planning/forecasting
- **Data Source**: `dwh.sm_fact_xhunt_progress_event` + cohort simulation logic

## Standard Analysis Pattern

### Query Structure Template
```sql
-- Universal X-Hunt Analysis Pattern
SELECT 
    date AS promo_date,
    current_step_level,
    user_participation_metrics,
    revenue_impact_metrics,
    engagement_ratios
FROM (
    -- Date Range Setup
    date_dimension
    -- User Cohort Definition (varies by X-Hunt type)
    CROSS JOIN target_user_cohort  
    -- Revenue Impact (14-day rolling window)
    LEFT JOIN revenue_analysis
    -- DAU Context
    LEFT JOIN daily_active_users
    -- Paying User Context  
    LEFT JOIN paying_user_metrics
) base_analysis
```

### Core Metrics Framework
1. **Participation Rate**: `users / DAU` - engagement penetration
2. **Revenue Share**: `rs_14d` - spending impact of hunt participants
3. **PU Engagement**: `PUs_share` - paying user hunt participation
4. **Progression Tracking**: Step advancement over time
5. **User Cohort Analysis**: Hunt performance by user segment

## Business Intelligence Patterns

### Revenue Impact Measurement
- **14-Day Rolling Window**: Measures spending before/during hunts
- **Revenue Share Calculation**: `user_rev_14d / overall_rev_14d`
- **Attribution Logic**: Correlates hunt participation with spending behavior

### Engagement Analysis
- **Step Progression**: Tracks user advancement through hunt levels
- **Participation Rates**: Measures hunt adoption vs. total user base
- **Retention Impact**: How hunts affect daily active user patterns

### Cohort Flexibility
- **Clan-Based**: Filter for clan members (`dwh.sm_clan_user_profile`)
- **Event-Based**: Filter for event participants (event-specific tables)
- **Segment-Based**: Filter by user characteristics (tier, spending, etc.)

## Implementation Variations

### Clan X-Hunt Implementation
```sql
-- User Cohort: Clan members participating in specific chase
SELECT DISTINCT user_id
FROM dwh.sm_fact_xhunt_progress_event
WHERE chase_id = [specific_clan_chase_id]
  AND event_date >= [hunt_start_date]
```

### Simulation X-Hunt Implementation  
```sql
-- User Cohort: All clan users (simulation scenario)
SELECT DISTINCT user_id  
FROM dwh.sm_clan_user_profile
-- Simulates: "What if all clan users participated in X-Hunt?"
```

### Individual Event X-Hunt Implementation
```sql
-- User Cohort: Event-specific participants
SELECT DISTINCT user_id
FROM dwh.sm_fact_xhunt_progress_event  
WHERE chase_id = [individual_event_id]
  AND event_date BETWEEN [event_start] AND [event_end]
```

## Key Design Principles

### 1. **Universal Framework**
- Same table structure serves multiple feature contexts
- Flexible `chase_id` allows different hunt types
- Standard metrics enable cross-hunt comparisons

### 2. **Revenue Attribution** 
- Consistent 14-day rolling window approach
- Revenue impact measurement for all hunt types
- Spending behavior correlation analysis

### 3. **Engagement Measurement**
- Participation rates vs. total user base
- Progression tracking through steps
- User segment performance analysis

### 4. **Time-Bounded Events**
- Parameter-driven date ranges
- Typical analysis windows (17-20 days)
- Event lifecycle tracking

## Analysis Applications

### Performance Evaluation
- Which X-Hunt types drive highest engagement?
- Revenue impact comparison across hunt formats
- User segment performance in different hunt contexts

### Feature Planning
- Simulation modeling for new hunt concepts
- User cohort impact forecasting  
- Revenue projection for hunt events

### Cross-Feature Intelligence
- How do clan hunts perform vs. individual hunts?
- User behavior patterns across hunt types
- Optimal hunt frequency and duration

## Technical Integration

### Query Development Strategy
1. **Identify Hunt Type**: Clan, individual, simulation, etc.
2. **Define User Cohort**: Appropriate filtering for hunt context
3. **Apply Standard Metrics**: Revenue, engagement, progression patterns
4. **Use Common Framework**: Leverage established X-Hunt analysis structure

### Data Quality Considerations
- **Progress Gaps**: Handle missing step data with `last_value...ignore nulls`
- **Revenue Attribution**: 14-day window may include pre-hunt activity
- **User Filtering**: Focus on users with actual progression
- **Parameter Dependencies**: Require `chase_id` and date boundaries

## Business Value

X-Hunt system provides **unified engagement measurement** across diverse feature contexts while maintaining **analytical consistency** and **cross-feature comparability**. This enables strategic insights about which engagement mechanisms work best for different user segments and business objectives.