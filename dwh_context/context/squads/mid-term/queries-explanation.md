# Mid-term Squad - Technical Queries & Dashboard Intelligence

## Dashboard Intelligence

### New Mid-term Dashboard Analysis
Analysis of the New Mid-term dashboard reveals **22 custom SQL queries** and **19 business worksheets** providing comprehensive mid-term feature intelligence:

#### Advanced Mid-term Analytics (22 queries total)
- **Comprehensive Feature Coverage**: Figz, Globez, Winovate (Scapes), Mega Pods with detailed progression tracking
- **Sophisticated Payout Analysis**: Percentile-based payout analysis (P25/P50/P75/P90) across features and user segments
- **Gem Usage Intelligence**: Advanced gem spending attribution across all mid-term features
- **Cross-Feature Funnel Analysis**: "figz globez funnel" demonstrating multi-feature engagement paths
- **Personal Offer Integration**: Detailed PO performance and DOS (Days of Service) analysis per feature

#### Key Business Worksheets
1. **Ante Bet Analysis** - Betting behavior during mid-term features (daily trends, spin share)
2. **Bundle Economics** - "Bundles needed - 1st set" analyzing completion requirements
3. **PO Performance** - "Winovate PO DOS", personal offer effectiveness by feature
4. **Pod Management** - "Pods Per Promo" tracking Mega Pods distribution and collection
5. **Engagement Funnels** - "figz globez funnel" cross-feature participation analysis
6. **Payout Intelligence** - Feature-specific payout analysis with gem usage integration
7. **Progression Tracking** - "Winovate Progression DOS" monitoring renovation advancement
8. **Hammer Economics** - "hammers distribution", "hammers in and out" for Winovate
9. **Unengagement Analysis** - "Unengagment" identifying feature drop-off patterns
10. **Revenue Attribution** - "4th type set finishers" revenue progression analysis

### Combined Dashboard Intelligence (37+ data sources total)
From the original 15 Tableau data sources plus 22+ dashboard queries, comprehensive analytical frameworks include:

### Advanced Technical Architecture Insights

#### Core Mid-term Tables & Data Sources
- **`dwh.sm_fact_lootbox_history_hero`** - Figz bundle tracking (BOX_CREATED, BOX_UPGRADED events)
- **`sm_fact_mega_win_party_history`** - Mega Pods system with chest types and unlock methods (COLLECTED, IMMEDIATELY_UNLOCK, COLLECTED_SEASON_END_REWARD)
- **`dwh.sm_fact_scapes_events`** - Winovate (Scapes) renovation events with source_amount tracking
- **`dwh.sm_fact_internal_purchase_balance_update_hero_coins`** - Figz coins balance tracking (received vs used)
- **`agg.sm_agg_daily_promotion_users_spins`** - Mid-term feature spin activity with scapes_antebet_amount
- **`dwh.fact_sm_goods_service_data`** - Journey-based bonus distribution and source attribution
- **`sm_Draft.figz_dates`** - Figz feature date ranges (ts_from, ts_to)
- **`sm_draft.winovate_dates`** - Winovate season boundaries (start_promo_date, end_promo_date)

#### Advanced Business Logic Patterns
- **Season Management**: Comprehensive season tracking with start/end boundaries across all features
- **Multi-Feature Percentile Analysis**: Sophisticated P25/P50/P75/P90 payout analysis across user segments
- **Cross-Feature Funnel Tracking**: "figz globez funnel" revealing multi-feature engagement patterns
- **Gem Usage Attribution**: Advanced gem spending tracking with seasonal usage patterns
- **DOS Integration**: Days of Service analysis integrated with personal offer performance
- **Renovation Progression**: Room-based progression tracking (max_room) with recompletion mechanics
- **Ante-Bet Integration**: Micro-betting behavior analysis during mid-term features
- **Bundle-to-Completion Economics**: Sophisticated analysis of bundles required for set completion
- **Unengagement Detection**: Advanced metrics identifying users with high coin acquisition but zero usage

#### Advanced Analytical Frameworks

##### Collection & Progression Intelligence
- **Multi-Feature Funnel Analysis**: Cross-feature engagement patterns ("figz globez funnel")
- **Set Completion Economics**: Bundle-to-completion ratios and economic analysis
- **Renovation Progression**: Room-based advancement with recompletion tracking (Winovate)
- **Seasonal Engagement**: Season-day progression analysis with retention curves
- **Unengagement Detection**: Users with high resource acquisition but zero utilization

##### Sophisticated Monetization Intelligence
- **Gem Usage Seasonal Patterns**: Advanced gem spending attribution across features and seasons
- **Personal Offer DOS Analysis**: Days of Service impact on offer conversion and effectiveness
- **Percentile-Based Payout Analysis**: P25/P50/P75/P90 payout distribution across user segments
- **Bundle Economics**: Detailed analysis of bundles required for first set completion
- **Revenue Share Progression**: "4th type set finishers" revenue tracking by completion timeline
- **Cross-Feature Revenue Attribution**: Multi-feature spending patterns and revenue impact

##### Advanced Behavioral Analytics
- **Ante-Bet Integration**: Micro-betting behavior during mid-term features (bet share, spin share)
- **Gem Spending Ratios**: Sophisticated gem usage analysis with seasonal and feature attribution  
- **Hammer Economics**: "hammers in and out" flow analysis for Winovate renovation
- **Pod Collection Strategy**: Gem-opened vs time-based collection behavior analysis
- **Journey-Based Bonus Distribution**: Source attribution through goods service data integration

##### Cross-Feature Performance Metrics
- **Multi-Feature Participation**: Users engaging across Figz, Globez, Winovate simultaneously
- **Season Overlap Analytics**: Performance during concurrent mid-term feature periods
- **Feature-Specific Retention**: DOS analysis showing sustained engagement per feature
- **Revenue Synergy**: Cross-feature spending amplification and revenue attribution
- **Engagement Pipeline**: How mid-term feature participation drives other game area engagement

### Data Quality & Validation Patterns
- **Feature Date Validation**: Strict enforcement of feature availability periods
- **Event Type Consistency**: Standardized event categorization across features
- **Status Progression Logic**: Proper status flow validation (created → collected/unlocked)
- **Gem Economy Integration**: Accurate gem spending attribution to feature activities
- **Cross-Feature Attribution**: Proper assignment of revenue and engagement to originating features

## Query Templates & Patterns

*Note: This section contains dashboard intelligence only. User-provided queries will be added here as they are shared and approved for integration.*

### Placeholder for User-Provided Queries
```sql
-- User-approved Mid-term queries will be documented here
-- Following the established pattern of:
-- 1. Query title and business purpose
-- 2. Full query with comments
-- 3. Expected output description
-- 4. Usage context and validation notes
```

## Integration Points

### Cross-Squad Dependencies
- **Purchase Tools**: Feature-specific personal offers and gem monetization
- **Revenue Analytics**: Mid-term contribution to overall revenue streams
- **Daily Dash**: Mid-term objectives potentially integrated with daily challenges
- **Seasonal Features**: Coordination to prevent overwhelming players with concurrent content
- **Album System**: Mid-term rewards potentially including cards or album-related benefits