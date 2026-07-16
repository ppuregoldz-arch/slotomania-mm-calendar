# SM Unified Metrics Dictionary

**Note**: All SQL formulas in this document use Vertica-compatible syntax. For detailed Vertica SQL syntax guidelines, see `documentation/sm_vertica_sql_compatibility.md`.

## Overview
This comprehensive metrics dictionary provides complete definitions, formulas, business logic, and usage guidelines for all SM metrics used in daily reports and analysis.

## Core Revenue Metrics

### Primary Revenue KPIs

| Metric | Definition | Formula | Business Logic | Validation Notes |
|--------|------------|---------|----------------|------------------|
| **Daily Net Revenue** | Approved revenue after fees | `SUM(daily_Net_revenue)` | Primary revenue metric for reporting | Use agg.agg_sm_daily_users_stats (AUTHORITATIVE) |
| **Daily Gross Revenue** | Revenue before adjustments | `SUM(daily_gross_rev)` | Revenue before fees and adjustments | Cross-check with fact table |
| **ARPU** | Average Revenue Per User | `SUM(daily_Net_revenue) / COUNT(DISTINCT user_id)` | Revenue efficiency per active user | Benchmark against industry standards |
| **ARPPU** | Average Revenue Per Paying User | `SUM(daily_Net_revenue) / COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END)` | Revenue per monetized user | Key conversion quality metric |
| **Average Transaction Value** | Average purchase amount | `SUM(daily_Net_revenue) / SUM(daily_payments)` | Purchase behavior indicator | Monitor for pricing optimization |

### Revenue Sources

| Revenue Source | Table | Filter | Description | Business Importance |
|----------------|-------|--------|-------------|-------------------|
| **Real Money Revenue** | `dwh.sm_fact_payments` | `tran_status_id = 2` | Actual USD purchases | Primary monetization (Financial KPI) |
| **Slotobucks Redemption** | `dwh.sm_fact_virtual_payment_slotobucks` | `tran_status_id = 2` | Virtual currency redemption | Currency injection analysis (NOT USD) |

**CRITICAL**: Never mix real money revenue with virtual currency redemption (different currencies, different purposes)

### Revenue by Product Group

| Product Group | Source | Business Logic | Strategic Value | Analysis Focus |
|---------------|--------|----------------|----------------|----------------|
| **Product Groups** | `sm_draft.SM_DIM_Products` | Grouped by product type | Product performance analysis | Revenue optimization |
| **SKU Performance** | `dwh.dim_sku_types` | Individual SKU analysis | Product-level insights | Pricing optimization |

## User Engagement Metrics

### Activity KPIs

| Metric | Definition | Formula | Business Logic | Usage |
|--------|------------|---------|----------------|--------|
| **DAU** | Daily Active Users | `COUNT(DISTINCT user_id)` | Core engagement metric | Daily operational tracking |
| **Spins per User** | Average spins per active user | `AVG(spins)` | Game engagement depth | Game design insights |
| **Sessions per User** | Average sessions per active user | `AVG(daily_sessions_amount)` | Session engagement quality | User experience optimization |
| **Spins per Session** | Average spins per session | `SUM(spins) / SUM(daily_sessions_amount)` | Session quality indicator | Engagement optimization |

### SM-Specific Gaming Behavior

| Metric | Definition | Formula | Business Logic | Key Insights |
|--------|------------|---------|----------------|--------------|
| **Bet Coins** | Total coins wagered | `SUM(bet_coins)` | Wagering activity | Economy health indicator |
| **Win Coins** | Total coins won | `SUM(win_coins)` | Winning activity | RTP analysis |
| **Net Wagering** | Net coins wagered (bet - win) | `SUM(bet_coins) - SUM(win_coins)` | Net consumption | Economy balance |
| **Win Rate** | Percentage of bets won | `SUM(win_coins) / SUM(bet_coins) * 100` | Return-to-player rate | Game balance analysis |

### Session Quality Metrics

| Metric | Definition | Formula | Business Logic | Optimization Focus |
|--------|------------|---------|----------------|-------------------|
| **Session Frequency** | Sessions per user per day | `AVG(daily_sessions_amount)` | User engagement frequency | Retention optimization |
| **Spin Frequency** | Spins per user per day | `AVG(spins)` | User engagement intensity | Engagement optimization |
| **Median Bet** | Median bet amount | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY actual_median_bet)` | Typical wagering behavior | Game balance optimization |

## Virtual Economy Metrics

### Coins Economy

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Coin Injection** | Total coins injected | `SUM(payment_quantity) + SUM(bonus_amount)` | Economy health indicator | Balance monitoring |
| **Coin Consumption** | Total coins wagered | `SUM(bet_coins)` | Spending behavior | Sink optimization |
| **Balance Start** | Average starting balance | `AVG(balance_start_day)` | Economy balance | Inflation control |
| **Balance End** | Average ending balance | `AVG(balance_end_day)` | Economy balance | Balance health |
| **Balance Change** | Net balance change | `AVG(balance_end_day - balance_start_day)` | Economy flow | Balance management |

### Gems Economy

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Gems Balance** | Average user gems | `AVG(gems_end_of_day_balance)` | Premium economy | Value perception |
| **Gems Distribution** | Percentiles of gems balance | `PERCENTILE_CONT(0.25/0.5/0.75/0.95) WITHIN GROUP (ORDER BY gems_end_of_day_balance)` | Premium currency distribution | Economy health |

### Economy Health Metrics

| Metric | Definition | Formula | Business Logic | Optimization Focus |
|--------|------------|---------|----------------|-------------------|
| **Consumption Rate** | Consumption to injection ratio | `(bet_coins - win_coins) / (payment_quantity + bonus_amount)` | Economy sustainability | Balance maintenance |
| **Payment Consumption** | Consumption from payments | `(bet_coins - win_coins) / payment_quantity` | Payment efficiency | Monetization quality |
| **Bonus Consumption** | Consumption from bonuses | `(bet_coins - win_coins) / bonus_amount` | Bonus effectiveness | Bonus optimization |
| **Balance Index** | Balance relative to wagering | `balance_end_day / bet_coins` | Economy balance indicator | Balance health |

### Balance Distribution Metrics

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Balance Percentile 25** | 25th percentile balance | `PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY balance_end_day)` | Lower quartile balance | Economy health |
| **Balance Percentile 50** | Median balance | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance_end_day)` | Median balance | Typical user balance |
| **Balance Percentile 75** | 75th percentile balance | `PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY balance_end_day)` | Upper quartile balance | High-value user balance |
| **Balance Percentile 95** | 95th percentile balance | `PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY balance_end_day)` | Top 5% balance | Whale user balance |

## Monetization Conversion Metrics

### Conversion KPIs

| Metric | Definition | Formula | Business Logic | Strategic Importance |
|--------|------------|---------|----------------|---------------------|
| **Paying Users (PU)** | Users who made purchases | `COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END)` | Daily monetization reach | Conversion funnel health |
| **PU/DAU** | Conversion rate | `Paying_Users / DAU` | Monetization efficiency | Key performance indicator |
| **FTD** | First Time Depositors | `COUNT(DISTINCT CASE WHEN is_ftd_platform = 1 THEN user_id END)` | New monetization acquisition | Growth measurement |
| **Transactions per Payer** | Purchase frequency | `SUM(daily_payments) / Paying_Users` | User monetization depth | Retention indicator |

### SM-Specific Conversion Funnel

| Metric | Definition | Formula | Business Logic | Optimization Focus |
|--------|------------|---------|----------------|-------------------|
| **DAU to Spinner** | Engagement rate | `Spinners / DAU` | Core game engagement | Game design optimization |
| **Spinner to Payer** | Game to monetization | `PU / Spinners` | Monetization efficiency | Conversion optimization |
| **Payer Retention** | Paying user retention | `Retained_Payers / Total_Payers` | Monetization retention | Revenue optimization |

## User Segmentation Metrics

### CZ Deluxe Segments

| Segment | Definition | Business Logic | Strategic Value |
|---------|------------|----------------|----------------|
| **CZ 0-5** | Low engagement | `cz_deluxe_weekly_update BETWEEN 0 AND 5` | Low-value user base |
| **CZ 5-10** | Low-medium engagement | `cz_deluxe_weekly_update BETWEEN 5 AND 10` | Emerging engagement |
| **CZ 10-20** | Medium engagement | `cz_deluxe_weekly_update BETWEEN 10 AND 20` | Moderate engagement |
| **CZ 20-40** | Medium-high engagement | `cz_deluxe_weekly_update BETWEEN 20 AND 40` | High engagement |
| **CZ 40-60** | High engagement | `cz_deluxe_weekly_update BETWEEN 40 AND 60` | Very high engagement |
| **CZ 60-80** | Very high engagement | `cz_deluxe_weekly_update BETWEEN 60 AND 80` | Premium engagement |
| **CZ 80-100** | Extremely high engagement | `cz_deluxe_weekly_update BETWEEN 80 AND 100` | Maximum engagement |
| **CZ +100** | Maximum engagement | `cz_deluxe_weekly_update > 100` | Elite engagement |

**Source**: `dwh.sm_user_profile_datamining_snapshot.cz_deluxe_weekly_update`

### VIP Tiers

| Tier Range | Definition | Business Logic | Strategic Value |
|------------|------------|----------------|----------------|
| **Tier 1-3** | Lower tiers | `tier_id BETWEEN 1 AND 3` | Newer or less engaged players |
| **Tier 4+** | Higher tiers | `tier_id >= 4` | More engaged, higher value players |

**Source**: `dwh.sm_user_profile_datamining_snapshot.tier_id` or `dwh.Dim_Coins_Value.tier_id`

### Paying Status Segments

| Segment | Definition | Business Logic | Strategic Value |
|---------|------------|----------------|----------------|
| **Paying Users** | Users with purchases | `daily_Net_revenue > 0` | Monetized user base |
| **Non-Paying Users** | Users without purchases | `daily_Net_revenue = 0` | Free-to-play base |

### Level-Based Segments

| Level Range | Definition | Business Logic | Strategic Value |
|-------------|------------|----------------|----------------|
| **New Players** | Low levels | `level_id BETWEEN 1 AND 10` | Onboarding optimization |
| **Mid-Level** | Medium levels | `level_id BETWEEN 11 AND 50` | Engagement optimization |
| **Advanced** | High levels | `level_id BETWEEN 51 AND 100` | Retention optimization |
| **Expert** | Very high levels | `level_id > 100` | Community leadership |

## Churn & Retention Metrics

### Churn Analysis

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Churn Rate** | Percentage of users who stop playing | `Churned_Users / Total_Users` | User retention health | Retention optimization |
| **Days from Last Login** | Time since last activity | `DATEDIFF('day', last_login_date, date)` | Churn risk indicator | Retention campaigns |
| **Dormant Players** | Users inactive 30+ days | `COUNT(DISTINCT CASE WHEN days_inactive >= 30 THEN user_id END)` | Churn measurement | Reactivation campaigns |

### Retention Metrics

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Day 1 Retention** | Users active on day 1 | `Day_1_Active / Day_0_Users` | Onboarding effectiveness | User experience optimization |
| **Day 7 Retention** | Users active on day 7 | `Day_7_Active / Day_0_Users` | Short-term retention | Engagement optimization |
| **Day 30 Retention** | Users active on day 30 | `Day_30_Active / Day_0_Users` | Long-term retention | Retention optimization |
| **Reactivation Rate** | Dormant users who return | `Reactivated_Users / Dormant_Users` | Re-engagement success | Reactivation campaigns |

## Product Performance Metrics

### Product Analysis

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Revenue by Product** | Revenue per product group | `SUM(net_amount) GROUP BY product_group` | Product performance | Product optimization |
| **Transactions by Product** | Transaction count per product | `COUNT(*) GROUP BY product_group` | Product popularity | Product development |
| **Value-for-Money Actual** | Actual coins per dollar | `payment_quantity / gross_amount` | Product value perception | Pricing optimization |
| **Value-for-Money Dimension** | Expected coins per dollar | `dim_coins_value / gross_amount` | Product value benchmark | Value optimization |
| **Percent Sale** | Discount percentage | `(value_for_money_actual / value_for_money_dim) - 1` | Promotion effectiveness | Pricing strategy |

### Product Performance by Segment

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Revenue by CZ Segment** | Revenue per CZ deluxe segment | `SUM(revenue) GROUP BY cz_segment` | Segment monetization | Segment optimization |
| **Revenue by VIP Tier** | Revenue per VIP tier | `SUM(revenue) GROUP BY tier_id` | Tier monetization | Tier optimization |
| **Conversion by Product** | Conversion rate per product | `Paying_Users / Total_Users GROUP BY product_group` | Product conversion | Product development |

## Bonus & Promotion Metrics

### Bonus Analysis

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Bonus Amount** | Total bonus coins | `SUM(bonus_amount)` | Bonus distribution | Bonus optimization |
| **Bonus Consumption** | Bonus coins consumed | `(bet_coins - win_coins) / bonus_amount` | Bonus effectiveness | Bonus campaigns |
| **Transaction-Linked Bonuses** | Bonuses from purchases | `SUM(bonus_amount) WHERE transaction_id IS NOT NULL` | Purchase bonuses | Monetization optimization |
| **Standalone Bonuses** | Non-purchase bonuses | `SUM(bonus_amount) WHERE transaction_id IS NULL` | Engagement bonuses | Retention optimization |

### Bonus Performance

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Bonus per User** | Average bonus per user | `AVG(daily_bonus_coins)` | Bonus distribution | Bonus strategy |
| **Bonus Impact** | Impact on engagement | `Correlation(bonus_amount, spins)` | Bonus effectiveness | Bonus optimization |

## Statistical Distribution Metrics

### Percentile Metrics

| Metric | Definition | Formula | Business Logic | Strategic Value |
|--------|------------|---------|----------------|----------------|
| **Median Wager** | 50th percentile bet | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY bet_coins)` | Typical wagering | Game balance |
| **Wager Percentile 75** | 75th percentile bet | `PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY bet_coins)` | High-value wagering | Whale analysis |
| **Wager Percentile 95** | 95th percentile bet | `PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY bet_coins)` | Top 5% wagering | Elite user analysis |
| **Spins Percentile 75** | 75th percentile spins | `PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY spins)` | High engagement | Engagement analysis |
| **Spins Percentile 95** | 95th percentile spins | `PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY spins)` | Top 5% engagement | Power user analysis |

## Platform Metrics

### Platform Performance

| Platform | Business Logic | Strategic Value | Analysis Focus |
|----------|----------------|----------------|----------------|
| **iOS** | `platform_id = iOS` | High-value users, premium experience | ARPU optimization, premium features |
| **Android** | `platform_id = Android` | Mass market, volume-driven | User acquisition, engagement optimization |
| **Web** | `platform_id = Web` | Desktop experience, different behavior | Cross-platform strategy, user journey |

## Calculation Notes

### Two-Step Aggregation (MANDATORY)
All period comparisons MUST use two-step aggregation:
1. **Step 1**: Calculate daily metrics with `GROUP BY calc_date`
2. **Step 2**: Average daily metrics for period comparisons

### Revenue Validation (MANDATORY)
- **Primary Source**: `agg.agg_sm_daily_users_stats.daily_Net_revenue`
- **Secondary Source**: `dwh.sm_fact_payments` with `tran_status_id = 2` filter
- **Cross-Validation**: Always verify fact table matches aggregated table

### Currency Separation (MANDATORY)
- **Real Money Revenue**: USD from `dwh.sm_fact_payments.net_amount`
- **Virtual Currency**: Virtual currency from `dwh.sm_fact_virtual_payment_slotobucks.transaction_amount`
- **NEVER ADD**: These are different currencies with different purposes

This metrics dictionary provides the foundation for consistent, accurate SM data analysis with proper understanding of all metrics and their business context.

