# X-Hunt Business Context

**Squad**: Clans  
**Feature Type**: Engagement/Chase System  
**Status**: Active  

## Feature Overview

X-Hunt appears to be a **clan-based chase/progression system** where users advance through steps in time-limited events. Based on the available query evidence, it's an engagement feature that tracks user progression and measures both participation and revenue impact.

## Key Business Metrics

### Progression Tracking
- **Current Step**: User's progress level in the chase (`filled_current_steps`)
- **User Share**: Percentage of total DAU participating in X-Hunt
- **PU Share**: Percentage of paying users involved in X-Hunt chases

### Revenue Analysis
- **14-Day Rolling Revenue Share** (`rs_14d`): Individual user's revenue contribution vs. total
- **Chase Impact on Spending**: Measures how X-Hunt participation affects user spending patterns
- **Paying User Engagement**: Tracks which paying users are active in chases

## Data Sources & Tables

### Primary Event Table
- **`dwh.sm_fact_xhunt_progress_event`**: Core X-Hunt progression tracking
  - `chase_id`: Unique identifier for each chase event
  - `user_id`: Participant identifier
  - `event_date`: Progression timestamp
  - `current_steps`: User's current progression level

### Supporting Data
- **`agg.agg_sm_daily_promotion_stats`**: Revenue and activity metrics
- **`dwh.dim_dates`**: Date dimension for time series analysis

## Business Logic Insights

### Chase Participation
- Users enter chases through `dwh.sm_fact_xhunt_progress_event`
- Progression tracked by `current_steps` advancement
- Analysis typically covers 20-day periods (`date < start_date + 20`)

### Revenue Attribution
- **14-day rolling window**: Measures spending impact before/during chases
- **Revenue share calculation**: `user_rev_14d / overall_rev_14d`
- **Paying user identification**: Users with `user_rev_14d > 0`

### Key Performance Indicators
1. **Participation Rate**: `users / DAU` - what % of daily users join chases
2. **Revenue Concentration**: `PUs_share` - paying user participation vs. total PUs
3. **Chase Progression**: Step-by-step advancement tracking
4. **Engagement Duration**: 20-day analysis window suggests chase length

## Engagement Strategy

X-Hunt appears designed to:
- **Drive Daily Engagement**: Users return to progress through chase steps
- **Encourage Spending**: Revenue tracking suggests monetization component
- **Clan Coordination**: Located in clans context suggests group participation
- **Time-Limited Events**: Parameter-based start dates indicate scheduled chases

## Analysis Patterns

### Common Query Structure
1. **Date Range Setup**: 20-day analysis window
2. **User Cohort**: Chase participants from progress events
3. **Revenue Overlay**: 14-day rolling spending analysis
4. **Progression Tracking**: Step-by-step advancement
5. **Share Calculations**: Participation vs. total user base

### Key Metrics Relationships
- Higher current steps → increased engagement
- Chase participants → revenue impact measurement
- Daily progression → retention indicators
- PU participation → monetization success

## Business Questions Answered

- Which users are progressing through X-Hunt chases?
- How does chase participation affect spending behavior?
- What percentage of DAU/PUs participate in chases?
- How do users advance through chase steps over time?
- What's the revenue impact of X-Hunt events?

## Related Features

Based on clan squad context:
- **Clan Chase**: Separate clan-based chase system
- **Daily Dash**: Individual progression system
- **Seasonal Events**: Time-limited engagement features

## Data Quality Notes

- **Progression Gaps**: `last_value...ignore nulls` handles missing step data
- **Revenue Attribution**: 14-day window may include pre-chase spending
- **User Filtering**: Query focuses on users with actual progression (`filled_current_steps is not null`)
- **Parameter Dependency**: Requires `chase_id` and start date for analysis