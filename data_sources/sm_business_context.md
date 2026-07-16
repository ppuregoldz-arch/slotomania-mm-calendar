# Slotomania (SM) - Business Context

## Overview
Slotomania is Playtika's premier slot machine casino game, featuring a virtual currency economy, in-app purchases, and social gaming elements. This document provides comprehensive business context for data analysis.

## Game Mechanics

### Core Gameplay
- **Slot Machines**: Primary gameplay mechanic with various themed slot machines
- **Spins**: Players wager virtual coins (bets) to spin slot machines
- **Wins**: Players win virtual coins based on slot machine outcomes
- **Return-to-Player (RTP)**: Percentage of wagered coins returned as wins
- **Bonus Features**: Special features triggered during gameplay (free spins, multipliers, etc.)

### Machine-Level Analysis
**Purpose**: Analyze slot machine performance, RTP, and payout rates by machine type

**Key Concepts:**
- **Machine RTP**: Return-to-player rate calculated as `SUM(win_amount) / SUM(bet_amount)` by machine type
- **Machine Payouts**: Total win amounts by machine for performance comparison
- **Machine Launch Date**: Filter machines by launch date to focus on active machines only (`launch_date <= CURRENT_DATE`)
- **Test Machine Exclusions**: Exclude test machines (IDs: 13522, 13569, 13626) from production analysis
- **Reel Type Exclusions**: Exclude special reel types (`'dynamicJackpot'`, `'royalCommunalJackpot'`) for standard machine analysis

**Data Sources:**
- **Spin Data**: `dwh.fact_sm_spin_history_kafka` (individual spin events)
- **Machine Metadata**: `dwh.sm_fact_machines_characteristics_data` (machine names, launch dates)

**Analysis Use Cases:**
- Compare RTP across different machine types
- Identify top-performing machines by revenue and engagement
- Monitor machine performance over time
- Optimize machine mix and placement

**Critical Filters:**
- Active machines only: `launch_date <= CURRENT_DATE`
- Production machines only: Exclude test machine IDs
- Standard gameplay only: Exclude special reel types

### Game Progression
- **Levels**: Players progress through levels by playing and winning
- **VIP Tiers**: Players advance through VIP tiers based on engagement and spending
- **Achievements**: Various achievements and milestones unlock rewards
- **Social Features**: Friends, gifting, and social interactions

## Virtual Currency Economy

### Currency Types

#### Coins (Primary Currency)
- **Purpose**: Primary virtual currency for gameplay
- **Sources**: 
  - Real money purchases (IAP)
  - Slotobucks redemption
  - Bonus rewards
  - Gameplay wins
- **Sinks**: 
  - Slot machine bets
  - In-game purchases
  - Social gifting
- **Balance Tracking**: Tracked daily in `agg.agg_sm_daily_users_stats` (balance_start_day, balance_end_day)

#### Gems (Secondary Currency)
- **Purpose**: Premium currency for special features and purchases
- **Sources**: 
  - Real money purchases
  - Special promotions
  - Achievement rewards
- **Sinks**: 
  - Premium features
  - Special purchases
- **Balance Tracking**: Tracked in `agg.agg_sm_daily_users_stats` (gems_end_of_day_balance)

#### Slotobucks (Virtual Currency)
- **Purpose**: Virtual currency earned through gameplay and promotions
- **Redemption**: Can be redeemed for coins
- **Tracking**: Redemptions tracked in `dwh.sm_fact_virtual_payment_slotobucks`
- **Critical**: NEVER mix with real money revenue (different currency, different purpose)

#### Slotobucks Flow Analysis (IN/OUT)
**Purpose**: Track Slotobucks balance changes and flow patterns

**Key Concepts:**
- **Slotobucks IN**: Positive delta values in `dwh.sm_fact_internal_purchase_balance_update_slotobucks` indicate Slotobucks added to user accounts
- **Slotobucks OUT**: Negative delta values indicate Slotobucks redeemed or consumed
- **Event Type Categorization**: Different event types (e.g., 'manual-bonus-group') represent different sources of Slotobucks
- **Tier-Based Analysis**: Analyze Slotobucks flow by VIP tier (`decorated_tier_id`) to understand tier-based patterns
- **Initial Balance Exclusion**: Exclude `event_type = 'initialBalance'` for flow analysis (represents account initialization, not actual flow)

**Data Source:**
- **Balance Updates**: `dwh.sm_fact_internal_purchase_balance_update_slotobucks` (real-time balance update events)

**Analysis Patterns:**
- **Daily Flow**: `SUM(CASE WHEN delta > 0 THEN delta END)` for IN, `SUM(CASE WHEN delta < 0 THEN delta END)` for OUT
- **Event Type Breakdown**: Group by `event_type` to understand Slotobucks sources
- **Tier Analysis**: Analyze flow patterns by `decorated_tier_id` for tier-based insights

**Use Cases:**
- Monitor Slotobucks injection and redemption rates
- Understand Slotobucks sources and usage patterns
- Optimize Slotobucks campaigns and promotions
- Analyze tier-based Slotobucks behavior

### Economy Balance

#### Coin Flow
```
Coin Injection:
  - Real Money Purchases → Coins
  - Slotobucks Redemption → Coins
  - Bonus Rewards → Coins
  - Gameplay Wins → Coins

Coin Consumption:
  - Slot Machine Bets → Coins Wagered
  - In-Game Purchases → Coins Spent
  - Social Gifting → Coins Given

Net Flow = Injection - Consumption
```

#### Balance Health Metrics
- **Balance Distribution**: Percentiles of user balances (25th, 50th, 75th, 95th)
- **Balance Velocity**: Rate of balance change over time
- **Consumption Rate**: Ratio of coins wagered to coins injected
- **Balance Index**: Balance relative to wagering activity

### Economy Analysis

#### Consumption Analysis
**Purpose**: Measure how quickly users consume injected currency relative to currency injection

**Key Metrics:**
- **Total Consumption Rate**: `(bet_coins - win_coins) / (payment_quantity + bonus_amount)`
  - Measures overall consumption relative to total currency injection (payments + bonuses)
  - Higher rate indicates faster currency consumption
- **Payment Consumption Rate**: `(bet_coins - win_coins) / payment_quantity`
  - Measures consumption relative to real money purchases only
  - Useful for understanding spending behavior of paying users
- **Bonus Consumption Rate**: `(bet_coins - win_coins) / bonus_amount`
  - Measures consumption relative to bonus currency injection only
  - Useful for understanding bonus effectiveness and user engagement

**Calculation Components:**
- **Net Consumption**: `bet_coins - win_coins` (coins wagered minus coins won)
- **Total Injection**: `payment_quantity + bonus_amount` (coins from purchases + coins from bonuses)
- **Payment Injection**: `payment_quantity` from `dwh.sm_fact_payments` (approved transactions only)
- **Bonus Injection**: `bonus_amount` from `dwh.fact_sm_bonus_history` (non-transaction bonuses only)

**Data Sources:**
- **Consumption**: `agg.agg_sm_daily_users_stats` (bet_coins, win_coins)
- **Payment Injection**: `dwh.sm_fact_payments` (payment_quantity, with `tran_status_id = 2`)
- **Bonus Injection**: `dwh.fact_sm_bonus_history` (bonus_amount, where `transaction_id IS NULL`)

**Analysis Use Cases:**
- Monitor economy health and currency velocity
- Optimize currency injection strategies
- Understand user spending patterns
- Balance economy to prevent inflation or deflation

**Best Practices:**
- Calculate consumption rates at daily level, then aggregate for period analysis
- Consider country-based exclusions when appropriate (document rationale)
- Cross-validate consumption calculations with balance changes

#### Velocity Analysis
- **Coin Velocity**: Rate of coin turnover (bets relative to balance)
- **Balance Velocity**: Rate of balance change
- **Purpose**: Understand economy health and user engagement

## Revenue Model

### In-App Purchases (IAP)
- **Real Money Revenue**: Actual USD from player purchases
- **Products**: Various coin packages, gem packages, special offers
- **Platforms**: iOS, Android, Web
- **Tracking**: `dwh.sm_fact_payments` (with status filter) and `agg.agg_sm_daily_users_stats`

### Product Groups
- **Product Categorization**: Products grouped by type, value, and purpose
- **Value-for-Money**: Analysis of product value relative to price
- **Product Performance**: Revenue and conversion by product group
- **Tracking**: `sm_draft.SM_DIM_Products` for product mapping

### Revenue Metrics
- **Daily Net Revenue**: Approved revenue after fees (`daily_Net_revenue`)
- **Gross Revenue**: Revenue before adjustments (`daily_gross_rev`)
- **ARPU**: Average Revenue Per User
- **ARPPU**: Average Revenue Per Paying User
- **Conversion Rate**: Percentage of users who make purchases
- **FTD Rate**: First-Time Deposit rate

## Player Segments

### CZ Deluxe Segments
**Purpose**: Engagement-based segmentation using CZ deluxe weekly update metric

**Segments:**
- **0-5**: Low engagement players
- **5-10**: Low-medium engagement players
- **10-20**: Medium engagement players
- **20-40**: Medium-high engagement players
- **40-60**: High engagement players
- **60-80**: Very high engagement players
- **80-100**: Extremely high engagement players
- **+100**: Maximum engagement players

**Usage:**
- Analyze behavior patterns by engagement level
- Optimize monetization strategies by segment
- Identify retention opportunities
- Track segment migration over time

**Source**: `dwh.sm_user_profile_datamining_snapshot.cz_deluxe_weekly_update`

#### CZ Deluxe Segment Analysis with Recent Payer Flag
**Purpose**: Dual segmentation combining engagement level (CZ deluxe) with recent payment activity

**Key Concepts:**
- **Recent Payer Flag**: User made a payment in the last 14 days (`tran_date BETWEEN calc_date - 14 AND calc_date`)
  - Flag = 1: User is a recent payer (made payment in last 14 days)
  - Flag = 0: User is not a recent payer (no payment in last 14 days)
- **Dual Segmentation**: Analyze behavior by both CZ deluxe segment AND recent payer status
- **CZ Segment Binning**: Standard segments (0-5, 5-10, 10-20, 20-40, 40-60, 60-80, 80-100, +100)
- **Percentile Analysis**: Calculate median, P75, P95 by segment for key metrics (bets, balances, spins, wins)

**Analysis Pattern:**
- Segment users by CZ deluxe value (0-5, 5-10, etc.)
- Flag users as recent payers (payment in last 14 days)
- Analyze metrics (bets, balances, spins, wins, revenue) by both dimensions
- Use percentile analysis (median, P75, P95) for distribution insights

**Data Sources:**
- **CZ Segments**: `dwh.sm_user_profile_datamining_snapshot.cz_deluxe_weekly_update`
- **Recent Payer Flag**: `dwh.sm_fact_payments` (check for payments in last 14 days)
- **User Metrics**: `agg.agg_sm_daily_users_stats` (bets, balances, spins, wins, revenue)

**Use Cases:**
- Compare behavior between recent payers and non-payers within same CZ segment
- Identify monetization opportunities in high-engagement non-payers
- Understand payment patterns by engagement level
- Optimize targeting strategies for different segment combinations

### VIP Tiers
**Purpose**: Progression-based segmentation using VIP tier system

**Tiers:**
- **Tier 1-3**: Lower tiers (newer or less engaged players)
- **Tier 4+**: Higher tiers (more engaged, higher value players)

**Usage:**
- Analyze monetization by tier
- Track tier progression
- Optimize tier-based rewards and offers
- Understand tier-based behavior patterns

**Source**: `dwh.sm_user_profile_datamining_snapshot.tier_id` or `dwh.Dim_Coins_Value.tier_id`

### Paying vs Non-Paying Users
**Purpose**: Monetization segmentation

**Segments:**
- **Paying Users**: Users with `daily_Net_revenue > 0`
- **Non-Paying Users**: Users with `daily_Net_revenue = 0`

**Usage:**
- Analyze conversion rates
- Compare engagement patterns
- Optimize monetization strategies
- Track payer acquisition and retention

**Source**: `agg.agg_sm_daily_users_stats.is_paying_user` or `daily_Net_revenue > 0`

### Level-Based Segments
**Purpose**: Progression-based segmentation

**Segments:**
- **New Players**: Low levels (1-10)
- **Mid-Level Players**: Medium levels (11-50)
- **Advanced Players**: High levels (51-100)
- **Expert Players**: Very high levels (100+)

**Usage:**
- Analyze progression patterns
- Optimize level-based rewards
- Track progression rates
- Understand level-based monetization

**Source**: `agg.agg_sm_daily_users_stats` level fields or `dwh.sm_user_profile_datamining_snapshot.level_id`

## Key Business Metrics

### Revenue Metrics
- **Daily Net Revenue**: Approved revenue per day
- **Gross Revenue**: Revenue before adjustments
- **ARPU**: Average Revenue Per User
- **ARPPU**: Average Revenue Per Paying User
- **Conversion Rate**: Percentage of users who purchase
- **FTD Rate**: First-Time Deposit rate
- **Revenue by Product Group**: Revenue breakdown by product category
- **Value-for-Money**: Product value relative to price

### User Metrics
- **DAU**: Daily Active Users
- **MAU**: Monthly Active Users
- **Retention**: Day 1, 7, 30 retention rates
- **Churn Rate**: Percentage of users who stop playing
- **Reactivation Rate**: Percentage of dormant users who return
- **Dormant Players**: Users inactive for 30+ days

### Engagement Metrics
- **Spins per User**: Average spins per active user
- **Sessions per User**: Average sessions per active user
- **Session Duration**: Average time per session
- **Bet Amount**: Average bet per spin
- **Win Rate**: Percentage of spins that result in wins
- **Balance Distribution**: Percentiles of user balances

### Economy Metrics
- **Coin Velocity**: Rate of coin turnover
- **Balance Velocity**: Rate of balance change
- **Consumption Rate**: Ratio of consumption to injection
- **Balance Index**: Balance relative to wagering
- **Bonus Consumption**: Rate of bonus coin consumption
- **Gems Balance**: Distribution of gems balances

### Product Metrics
- **Revenue by Product**: Revenue by product group/SKU
- **Transaction Count**: Number of transactions by product
- **Conversion by Product**: Conversion rate by product
- **Value-for-Money**: Product value analysis
- **Product Performance**: Revenue and conversion trends

## Business Objectives

### Revenue Optimization
- **Increase ARPU**: Improve average revenue per user
- **Increase Conversion**: Convert more free users to paying users
- **Optimize Product Mix**: Improve product performance and value
- **Maximize LTV**: Increase long-term user value

### User Engagement
- **Increase DAU**: Grow daily active users
- **Improve Retention**: Reduce churn and improve retention rates
- **Increase Session Frequency**: More sessions per user
- **Enhance Session Quality**: Better engagement per session

### Economy Health
- **Balance Economy**: Maintain healthy balance distribution
- **Optimize Consumption**: Balance coin injection and consumption
- **Monitor RTP**: Track return-to-player rates
- **Manage Currency Flow**: Ensure sustainable economy

### Product Performance
- **Optimize Product Mix**: Improve product offerings
- **Enhance Value-for-Money**: Better product value propositions
- **Track Product Trends**: Monitor product performance over time
- **Optimize Pricing**: Improve pricing strategies

## Analysis Use Cases

### Daily Revenue Analysis
- **Purpose**: Monitor daily revenue performance
- **Metrics**: Daily Net Revenue, ARPU, ARPPU, Conversion Rate
- **Segments**: By CZ deluxe segment, VIP tier, platform
- **Use Case**: Daily business monitoring and trend analysis

### User Behavior Analysis
- **Purpose**: Understand user engagement patterns
- **Metrics**: Spins, sessions, bet amounts, win rates
- **Segments**: By CZ deluxe segment, paying status, level
- **Use Case**: Engagement optimization and retention strategies

### Consumption Analysis
- **Purpose**: Monitor economy health and currency flow
- **Metrics**: Consumption rates, balance distribution, velocity
- **Segments**: By user segment, product group
- **Use Case**: Economy balance and currency injection optimization

### Churn Analysis
- **Purpose**: Identify and prevent user churn
- **Metrics**: Churn rates, retention rates, reactivation rates
- **Segments**: By engagement level, paying status, level
- **Use Case**: Retention campaigns and churn prevention

### Product Performance Analysis
- **Purpose**: Optimize product offerings and pricing
- **Metrics**: Revenue by product, conversion rates, value-for-money
- **Segments**: By product group, SKU, user segment
- **Use Case**: Product development and pricing optimization

### Balance Analysis
- **Purpose**: Monitor economy balance and health
- **Metrics**: Balance distribution, balance index, balance velocity
- **Segments**: By user segment, engagement level
- **Use Case**: Economy balance management and currency injection

### Bonus Analysis
- **Purpose**: Optimize bonus campaigns and rewards
- **Metrics**: Bonus consumption, bonus effectiveness, bonus impact
- **Segments**: By bonus type, user segment
- **Use Case**: Bonus campaign optimization and effectiveness

## Business Rules

### Revenue Rules
1. **Approved Transactions Only**: Only count `tran_status_id = 2` transactions
2. **Aggregated Table Authority**: Use `agg.agg_sm_daily_users_stats` for revenue totals
3. **Currency Separation**: Never mix real money revenue with virtual currency redemption
4. **Cross-Validation**: Always verify fact table results against aggregated table

### Economy Rules
1. **Balance Tracking**: Track balance changes daily (start vs end of day)
2. **Consumption Calculation**: `(bet_coins - win_coins) / (injection_amount)`
3. **Velocity Tracking**: Monitor balance and coin velocity over time
4. **Balance Health**: Maintain healthy balance distribution across segments

### Segmentation Rules
1. **CZ Deluxe Segments**: Use snapshot table for current segments
2. **VIP Tiers**: Use tier_id from snapshot or dimension tables
3. **Paying Status**: Use `daily_Net_revenue > 0` for current day status
4. **Level Progression**: Use level_id from snapshot or daily stats

### Analysis Rules
1. **Two-Step Aggregation**: Always use two-step aggregation for period comparisons
2. **Date Exclusion**: Exclude current date for incomplete period analysis
3. **Test User Exclusion**: Exclude test users and test countries
4. **Data Quality Flags**: Document data quality limitations in analysis

This business context provides the foundation for understanding SM business logic and conducting meaningful data analysis.

