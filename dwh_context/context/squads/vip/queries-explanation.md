# VIP Squad - Queries & Dashboard Intelligence

## Summary
This file contains dashboard intelligence and analytical patterns for the VIP squad, focusing on premium player programs, Inner Circle performance, and high-value player retention analytics.

## Key Analytical Areas

### Inner Circle Analytics
- **VIP Enrollment Tracking**: Platinum tier progression and Inner Circle adoption rates
- **Platform Usage**: .com vs VIP app usage patterns among VIP players
- **Benefit Utilization**: Which Inner Circle perks drive the most engagement
- **Safety Net Analysis**: Weekly loss compensation patterns and player behavior impact

### Account Management Analytics
- **Managed User Identification**: Tracking VIP users with dedicated account managers
- **Account Manager Performance**: Analysis of managed user engagement and retention
- **Management Impact**: Measuring effectiveness of personalized account management

### Cross-Program Performance
- **Playtika Rewards**: Cross-game engagement and reward redemption patterns
- **Reel Owners**: Machine ownership program participation and retention
- **Sloto Club**: Premium membership utilization and satisfaction metrics
- **Tier Progression**: Movement between VIP tiers and retention rates

### Revenue and Retention Impact
- **VIP Spending Patterns**: Purchase behavior differences between VIP and standard players
- **Retention Analysis**: VIP program impact on long-term player retention
- **Feature Premium Performance**: Enhanced feature usage and conversion rates
- **Safety Net ROI**: Cost vs. retention benefit of loss compensation program

### Exclusive Feature Analytics
- **Sneak Peek Engagement**: Early machine access utilization and feedback
- **Exclusive Gamemania**: VIP-only machine performance and rotation effectiveness
- **Enhanced Bonus Performance**: Impact of percentage boosts on player satisfaction
- **Black Diamond Analytics**: Highest tier player behavior and program effectiveness

## Data Sources & Tables

### Account Manager Assignments
**Table**: `dwh.sm_dim_vip_account_managers`
- **Purpose**: Tracks VIP users assigned to dedicated account managers
- **Key Fields**:
  - `user_id`: Player identifier
  - `account_manager`: Assigned account manager name
- **Business Logic**: 
  - **Managed Users Filter**: `WHERE account_manager IS NOT NULL`
  - **Usage**: Identifies high-value VIP users with dedicated management support

**Common Pattern**:
```sql
-- Identify managed users
SELECT user_id, account_manager
FROM dwh.sm_dim_vip_account_managers
WHERE account_manager IS NOT NULL
```

## User-Provided Queries

*This section is reserved for user-provided SQL queries and analysis scripts. Only user-approved queries should be stored here.*

## Dashboard Intelligence Patterns

### VIP Performance Reports
- Daily/weekly VIP tier distribution and movement
- Inner Circle benefit utilization tracking
- Platform-specific VIP engagement (web vs mobile VIP apps)
- Safety Net distribution and player response analysis

### Premium Feature Analytics
- Enhanced bonus calculation accuracy and impact
- Exclusive content engagement measurement
- Cross-game Playtika Rewards integration effectiveness
- VIP program ROI and lifetime value analysis

### Comparative Analysis
- VIP vs standard player behavior comparisons
- Tier-based performance segmentation
- Platform preference analysis among VIP segments
- Feature enhancement effectiveness measurement

*Note: Specific dashboard extracts and query intelligence should be added here as they are identified and approved by the user.*