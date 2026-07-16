# Holy Moley Analysis Queries

This folder contains SQL queries for analyzing the Holy Moley feature re-launch.

## Query Structure

### Analysis Categories
1. **Historical Performance** (`historical_*`): Queries analyzing past Holy Moley performance data
2. **Configuration Validation** (`config_*`): Queries validating feature settings, prize structures, and pick costs
3. **Blast Comparison** (`blast_comparison_*`): Queries comparing Holy Moley mechanics with current Blast feature
4. **User Behavior** (`user_behavior_*`): Queries analyzing player engagement patterns
5. **Revenue Analysis** (`revenue_*`): Queries focusing on monetization and revenue metrics

### Naming Convention
- `01_feature_discovery.sql` - Initial exploration of Holy Moley data availability
- `02_historical_performance.sql` - Historical metrics and performance analysis
- `03_blast_comparison.sql` - Feature comparison analysis
- `04_configuration_validation.sql` - Prize and cost structure validation
- `05_user_segmentation.sql` - Player behavior and segmentation analysis

## Expected Data Sources

### Primary Tables (to be validated)
- `dwh.sm_fact_promotions_*` - Promo-based feature events
- `dwh.sm_fact_picks_*` - Pick acquisition and usage
- `dwh.sm_fact_prizes_*` - Prize distribution and rewards
- `dwh.sm_fact_payments` - Purchase-based pick acquisitions
- `dwh.sm_user_profile_*` - User segmentation data

### Reference Tables
- Feature configuration tables
- Prize structure definitions
- Historical Blast data for comparison

## Analysis Framework

Each query follows the standard validation methodology:
- Manual validation with 1-3 specific entities
- Raw data verification before aggregation
- Business logic validation against known feature mechanics
- Documentation of assumptions and edge cases

---

*Query validation required for all analysis results*  
*Follow sql-standards and query-validation workspace rules*