# Seasonals Squad - Technical Queries & Dashboard Intelligence

## Dashboard Intelligence

### United Seasonal Dashboard Analysis
Analysis of the United Seasonal dashboard reveals **52 business worksheets** and comprehensive seasonal intelligence covering multiple features:

#### Advanced Seasonal Analytics (18+ queries)
- **Multi-Seasonal Coverage**: Blast, Battle Sheep, Diggin Doggy with unified analytical framework
- **Token Balance Analysis**: Sophisticated token progression tracking with completion thresholds  
- **Revenue Share Segmentation**: Advanced revenue share analysis by token balance and completion status
- **Pick Economy Intelligence**: Comprehensive picks-in vs picks-out flow analysis
- **Gem Usage Attribution**: Detailed gem spending patterns across seasonal features

#### Key Business Worksheets (United Dashboard - 52 total)
1. **Token Balance Analytics** - "Balances each season", token balance extra analysis
2. **Revenue Performance** - "seasonal PUs segments", "v4$ Table", seasonal revenue attribution
3. **Engagement Analysis** - "Participation engagement", "season KPIs", completion tracking
4. **Pick Economy** - "median picks per board", pick distribution and efficiency analysis
5. **Monetization Intelligence** - "Gem Usage KPI", "Net KPI", gem spending effectiveness
6. **Cross-Feature Analysis** - "with/wo product daily", seasonal vs core product performance
7. **Hourly Analytics** - "Hourly Direct", "Hourly Direct CZ", time-based engagement patterns

### Snakes and Ladders Dashboard Analysis  
Analysis of the Snakes and Ladders dashboard reveals **16 custom SQL queries** and **20 business worksheets** with specialized board game mechanics:

#### Board Game Intelligence (16 queries)
- **Board Progression Tracking**: Detailed board_id, cycle_number progression analysis
- **Dice Roll Economy**: Dice roll acquisition, usage, and purchase patterns  
- **Multi-Board System**: 5-board progression with final prize achievement tracking
- **Booster Analytics**: Multi-Wheel and Persistent Shield gem monetization analysis

#### Snakes & Ladders Business Worksheets (20 total)
1. **Board Progression** - "Revshare Board progression", "Revshare Cycle progression"
2. **Participation Analytics** - "Participation engagement", "PUs KPI", player engagement depth
3. **Reward Analysis** - "Question Mark Distribution", reward type and distribution tracking
4. **Monetization Performance** - "Gem Usage KPI", booster purchase analysis
5. **Balance Analytics** - "Balances each season", dice roll economy health

### Combined Dashboard Intelligence (74+ worksheets total)
From the original 8 Tableau data sources plus 52 United dashboard worksheets plus 20 Snakes & Ladders worksheets, comprehensive analytical frameworks include:

### Advanced Technical Architecture Insights

#### Core Seasonal Tables & Data Sources
- **`dwh.sm_fact_blast_games_activity`** - Blast board progression with board_run_id and sub_blast_event_id
- **`dwh.sm_fact_battlesheep_events`** - Battle Sheep board mechanics with board_number and sub_event_id
- **`dwh.sm_fact_snl_rewards`** - Snakes & Ladders reward distribution with board_id and cycle_number
- **`sm_draft.battlesheep_events`** - Battle Sheep event configuration with challenge_start_ts/end_ts
- **`sm_draft.Maor_Blast_Events`** - Blast event configuration and timing
- **Event-Based Architecture**: Comprehensive event logging with event_type categorization across all features
- **Token Balance Systems**: Advanced token_balance_extra tracking with completion threshold analysis

#### Advanced Business Logic Patterns
- **Multi-Board Progression**: Sophisticated board-based advancement (Blast: board_run_id, Battle Sheep: board_number, SNL: 5-board system)
- **Token Economy Intelligence**: token_balance_extra with completion thresholds (50, 105, 210+ for cycle progression)
- **Revenue Share Segmentation**: Advanced revenue share analysis by token balance and completion achievement
- **Cross-Seasonal Analytics**: Unified analytical framework supporting Blast, Battle Sheep, Diggin Doggy, SNL
- **Booster Integration**: Multi-Wheel and Persistent Shield gem monetization with usage tracking
- **Dice Roll Economy**: SNL-specific dice roll acquisition through bet-based bar filling and purchase options
- **Board Game Mechanics**: Snake/ladder effects, green bonus cards, auto-roll functionality with 3-second activation

#### Analytical Frameworks

##### Pick Economy Intelligence
- **Pick Flow Analysis**: "picks_in_-_picks_out" revealing player pick acquisition vs usage patterns
- **Pick Source Attribution**: Earned vs purchased pick distribution and effectiveness
- **Board Progression**: Median picks per board completion providing difficulty calibration data
- **Pick Economy Balance**: System health monitoring through pick flow metrics

##### Monetization Intelligence
- **Seasonal Revenue Attribution**: Direct seasonal product purchases vs total revenue comparison
- **Gem Usage Patterns**: Battle Sheep and other seasonal gem spending with net gem analysis
- **Revenue Share by Completion**: Completion status impact on revenue contribution
- **Paying User Segmentation**: Seasonal-specific vs total paying user analysis

##### Feature Performance Analytics
- **Battle Sheep Focus**: Detailed Battle Sheep analytics indicating it as primary seasonal reference
- **Event Count Tracking**: Seasonal engagement depth through event participation counting
- **Completion Analysis**: Revenue share analysis based on seasonal completion achievement
- **V4 Dollar Integration**: Seasonal contribution to overall V4 dollar performance metrics

#### Key Performance Metrics Architecture
- **Pick Economy Health**: Pick acquisition vs usage balance monitoring
- **Seasonal Revenue Contribution**: Direct seasonal spending vs overall revenue impact
- **Completion-Based Segmentation**: Player performance analysis by seasonal achievement levels
- **Cross-Seasonal Analytics**: Framework for analyzing multiple seasonal features simultaneously

### Data Quality & Validation Patterns
- **Event Type Consistency**: Standardized event categorization across seasonal features
- **Revenue Product Classification**: Clear seasonal product group definition and attribution
- **Pick Flow Validation**: Balance monitoring between pick generation and consumption
- **CZ Range Integration**: Consistent player segmentation across seasonal analytics
- **Gem Economy Tracking**: Accurate gem spending and earning attribution within seasonals

## Query Templates & Patterns

*Note: This section contains dashboard intelligence only. User-provided queries will be added here as they are shared and approved for integration.*

### Placeholder for User-Provided Queries
```sql
-- User-approved Seasonal queries will be documented here
-- Following the established pattern of:
-- 1. Query title and business purpose
-- 2. Full query with comments
-- 3. Expected output description
-- 4. Usage context and validation notes
```

## Integration Points

### Cross-Squad Dependencies
- **Album System**: Seasonal themes aligned with album cycles and card rewards
- **Purchase Tools**: Seasonal-specific personal offers and extra pick monetization
- **Revenue Analytics**: Seasonal contribution to overall revenue streams and gem economy
- **Daily Dash**: Coordination to prevent overwhelming players with concurrent short-term content
- **Mid-term Features**: Seasonal scheduling to complement rather than compete with mid-term features

## Seasonal Analytics Framework

### Pick-Based Analysis Patterns
- **Pick Economy Balance**: Monitoring pick generation vs consumption across all seasonal features
- **Source Effectiveness**: Comparing earned vs purchased pick conversion and player satisfaction
- **Board Difficulty Calibration**: Using median picks per board data to optimize seasonal challenge levels
- **Cross-Seasonal Pick Comparison**: Analyzing pick requirements and usage across different seasonal themes

### Revenue Attribution Framework
- **Direct Seasonal Revenue**: Purchases specifically attributed to seasonal product groups
- **Indirect Revenue Impact**: Cross-feature spending influenced by seasonal engagement
- **Gem Economy Contribution**: Net gem impact from seasonal features (spending vs earning)
- **Completion Revenue Correlation**: Revenue patterns based on seasonal progression and completion achievement