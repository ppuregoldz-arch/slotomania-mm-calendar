# Album Squad - Technical Queries & Dashboard Intelligence

## Dashboard Intelligence

### Funky Family Album 05-2026 Features Dashboard
Analysis of Features dashboard reveals **18 custom SQL queries** and **18 business worksheets** focused on:

#### Key Features Intelligence
- **Shiny Show Integration**: Major album feature with floor progression, gem monetization, and bomb failure mechanics
- **Shiny Card Collection**: Specialized shiny card progression tracked separately from regular cards
- **Wild Card Economy**: WoS (Wheel of Surprises) integration for wild card distribution
- **Ace Machine Integration**: Ace card stars feeding spin balance for additional gameplay layer
- **Cross-Feature Revenue**: Detailed gem spending attribution across album features

#### Business Worksheets (Features Focus)
1. **Floor reach shiny show** - Shiny Show progression tracking
2. **Gems revenue** - Album-driven gem monetization
3. **New Shiny cards** - Shiny card acquisition patterns
4. **Shiny CardsCurrent Progression** - Real-time shiny collection status
5. **Shiny Experience** - Overall shiny feature engagement
6. **Shiny Show Activations** - Entry and participation tracking
7. **WOS 2.0** - Wild card distribution via Wheel of Surprises
8. **ace machine spins balance/used** - Ace card ecosystem performance

### Funky Family Album 05-2026 Core Dashboard
Analysis of Core dashboard reveals **23 custom SQL queries** and **35 business worksheets** focused on:

#### Core Album Intelligence
- **Album Lifecycle Management**: Complete 70-day album season tracking with launch/end dates
- **Completion Thresholds**: 200+ cards = album completion, detailed finisher journey analysis
- **Revenue Progression**: Cost-to-completion tracking with finisher period segmentation
- **Missing Card Strategy**: Sophisticated missing card ratio analysis by segment and rarity
- **Cross-Album Benchmarking**: Multi-season comparison (last 3 albums: Funky Family #93, Royal #90)

#### Business Worksheets (Core Focus)
1. **# of Album Finishers & AVG Cost to Finish** - Completion economics by timeline
2. **% progression by set** - Set-level completion tracking
3. **Cards by Segment** - Segmented collection behavior analysis
4. **Cohort by Segment** - Player retention through collection journey
5. **Cost per Progression** - Revenue efficiency at each collection milestone
6. **Daily Wild Distribution** - Wild card economy health monitoring
7. **Finishers Revenue by Period** - Revenue patterns by completion timeframe
8. **Missing Ratio by Card** - Individual card scarcity and bottleneck analysis
9. **Revenue Snapshot Progression** - Real-time revenue tracking through collection
10. **Weekly Progression** - Weekly collection velocity and engagement patterns

### Combined Dashboard Intelligence (41 queries total)
Based on analysis of both Album dashboards, the following analytical frameworks have been identified:

### Key Technical Architecture Insights

#### Core Album Tables & Data Sources
- **`dwh.sm_fact_collectibles_cards`** - Primary card acquisition and ownership events
- **`dwh.sm_fact_shiny_show`** - Shiny Show minigame progression and outcomes
- **`dwh.sm_fact_shiny_challenge_progression`** - Specialized shiny collection tracking
- **`dwh.sm_fact_wos_game_state_history`** - Wheel of Surprises wild card distribution
- **`dwh.sm_fact_milestone_reward_history`** - Album enhancement challenge rewards
- **`sm_draft.ariel_dim_albums_info`** - Album metadata with launch/end dates and card ranges
- **Album completion tracking** - 200+ cards = album finisher status
- **Shiny card ranges** - Separate shiny_card_from/shiny_card_to boundaries

#### Business Logic Patterns
- **Album Seasons**: Exact 70-day cycles with precise launch_date/end_date tracking
- **Completion Thresholds**: 200+ cards for album completion, 10+ cards typical per set
- **Revenue Attribution**: Sophisticated pre/during/post completion spending analysis
- **Multi-Card Economy**: Regular, Gold, Shiny, Ace, Wild, and Fusion card integration
- **Set Structure**: Cards organized by set_num with rareness_id classifications
- **Finisher Segmentation**: P1-P6 periods from "Very Fast" (0-28d) to "Last Minute Rush" (71-84d)

#### Advanced Analytical Frameworks

##### Collection Progression Analysis
- **Days from Launch Tracking**: `datediff('day', launch_date, event_date)` standardization
- **Weekly Benchmarks**: Sophisticated weekly card collection benchmarks (week 1: 35 cards, week 11: 197 cards)
- **Completion Journey**: Running total revenue with finisher performance post-completion tracking  
- **Near-Miss Identification**: Missing card ratio analysis by segment and completion proximity
- **Cohort Retention**: Day-N retention analysis through collection lifecycle

##### Monetization Intelligence  
- **Cost-to-Finish Economics**: Revenue required per completion period (P1-P6 segmentation)
- **Gem Revenue Attribution**: Multi-source gem spending (Shiny Show, regular collection, wild cards)
- **Cross-Feature Revenue**: Album-driven spending in Shiny Show, WoS, and other features
- **Set Revenue Progression**: Revenue contribution analysis per card set completion
- **Finisher LTV Analysis**: Lifetime value comparison across completion timeframes

##### Shiny Show Integration
- **Floor Progression**: Shiny Show floor reach tracking with bomb failure mechanics
- **Gem Monetization**: EP (Extra Pick), bomb saves, and stock-up purchases
- **Shiny Card Tracking**: Separate progression system within album framework
- **Cross-System Revenue**: Shiny Show revenue attribution to album engagement

##### Wild Card & WoS Economy
- **WoS Distribution**: Wheel of Surprises wild card allocation by wheel type and tier
- **Wild Card Usage**: Strategic application tracking for fusion vs regular completion
- **Ace Machine Integration**: Ace card stars feeding spin balance economy
- **Multi-Source Wild Cards**: Daily Dash, WoS, gem purchases, challenge rewards

#### Advanced Performance Metrics Architecture
- **Multi-Album Benchmarking**: Cross-season performance (Albums 90, 93 comparison)
- **Segment-Based Analytics**: Revenue share percentile analysis (ALL, PU, PU_P95 segments)
- **Missing Card Intelligence**: Individual card bottleneck identification with rarity impact
- **Finisher Economics**: Average cost per completion period with ROI analysis
- **Cross-Feature Attribution**: Album engagement driving other feature participation and spending

### Data Quality & Validation Patterns
- **Album ID Consistency**: Latest album tracking with `max(album_id) over ()`
- **Tradability Flags**: `is_tradable` indicates card transfer restrictions
- **User Activity Validation**: Integration with daily paying user (`daily_pu`) status
- **Timezone Standardization**: Consistent IL timezone conversion across queries
- **Revenue Attribution**: Pre/during/post completion revenue tracking

## Query Templates & Patterns

*Note: This section contains dashboard intelligence only. User-provided queries will be added here as they are shared and approved for integration.*

### Placeholder for User-Provided Queries
```sql
-- User-approved Album queries will be documented here
-- Following the established pattern of:
-- 1. Query title and business purpose
-- 2. Full query with comments
-- 3. Expected output description
-- 4. Usage context and validation notes
```

## Integration Points

### Cross-Squad Dependencies
- **Daily Dash**: Wild cards as progression rewards
- **Purchase Tools**: Gem spending on card packs and wild cards
- **Seasonals**: Album-themed seasonal content integration
- **Revenue Analytics**: Album-driven monetization contribution tracking