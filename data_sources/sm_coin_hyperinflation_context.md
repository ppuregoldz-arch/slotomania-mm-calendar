# SM Coin Hyperinflation Context - CRITICAL REFERENCE

## Overview
**Slotomania (SM) operates with EXTREME hyperinflation in virtual currency (coins).** Coin amounts that would be errors in other games are **NORMAL and EXPECTED** in SM. This document provides the normal ranges to prevent false error flags.

## CRITICAL WARNING FOR AI MODELS

**DO NOT FLAG HIGH COIN AMOUNTS AS ERRORS**

SM coins are in hyperinflation. The following amounts are **NORMAL** and **EXPECTED**:
- **Trillions** (10^12) - Common for median values
- **Sextillions** (10^21) - Common for payment quantities
- **Septillions** (10^24) - Common for P95 percentiles
- **Undecillions** (10^32) - Common for maximum values

**These are NOT data quality issues - this is the normal state of SM's virtual economy.**

## Normal Coin Amount Ranges (Based on Recent Data - November 2025)

### Balance End Day (balance_end_day)

**Typical Ranges:**
- **P25 (25th percentile)**: ~5-6 billion coins (5-6 × 10^9)
- **Median (50th percentile)**: ~73-99 trillion coins (7.3-9.9 × 10^13)
- **P75 (75th percentile)**: ~2.4-4.6 sextillion coins (2.4-4.6 × 10^19)
- **P95 (95th percentile)**: ~7.8-10.2 septillion coins (7.8-10.2 × 10^24)
- **P99 (99th percentile)**: ~3.9-4.2 octillion coins (3.9-4.2 × 10^26)
- **Maximum**: ~4.6-9.5 undecillion coins (4.6-9.5 × 10^32)
- **Average**: ~1.1-1.7 octillion coins (1.1-1.7 × 10^28)

**Example Values (November 2025):**
- Median: 73,206,509,249,241 coins (~73 trillion)
- P95: 8,001,435,944,727,320,000,000,000 coins (~8 septillion)
- P99: 401,627,622,564,769,000,000,000,000 coins (~401 octillion)
- Max: 460,889,069,606,984,000,000,000,000,000,000 coins (~460 undecillion)

### Bet Coins (bet_coins)

**Typical Ranges:**
- **Median (50th percentile)**: ~100-173 trillion coins (1.0-1.7 × 10^14)
- **P95 (95th percentile)**: ~8.7-11.5 septillion coins (8.7-11.5 × 10^24)
- **P99 (99th percentile)**: ~4.4-5.8 octillion coins (4.4-5.8 × 10^26)
- **Maximum**: ~1.4-1.9 undecillion coins (1.4-1.9 × 10^32)
- **Average**: ~7.4-7.8 octillion coins (7.4-7.8 × 10^27)

**Example Values (November 2025):**
- Median: 148,047,969,600,000 coins (~148 trillion)
- P95: 11,542,720,000,000,000,000,000,000 coins (~11.5 septillion)
- P99: 580,128,000,000,000,000,000,000,000 coins (~580 octillion)
- Max: 142,956,979,200,000,000,000,000,000,000,000 coins (~142 undecillion)

### Win Coins (win_coins)

**Typical Ranges:**
- **Median (50th percentile)**: ~72-125 trillion coins (7.2-1.25 × 10^13)
- **P95 (95th percentile)**: ~5.8-8.3 septillion coins (5.8-8.3 × 10^24)
- **P99 (99th percentile)**: ~3.0-4.3 octillion coins (3.0-4.3 × 10^26)
- **Maximum**: ~1.0-1.9 undecillion coins (1.0-1.9 × 10^32)
- **Average**: ~7.0-7.5 octillion coins (7.0-7.5 × 10^27)

**Example Values (November 2025):**
- Median: 109,837,500,000,240 coins (~109 trillion)
- P95: 7,898,759,049,999,980,000,000,000 coins (~7.9 septillion)
- P99: 432,943,080,000,000,000,000,000,000 coins (~432 octillion)
- Max: 105,352,567,256,920,000,000,000,000,000,000 coins (~105 undecillion)

### Payment Quantity (payment_quantity from purchases)

**Typical Ranges:**
- **Median (50th percentile)**: ~7.6 sextillion coins (7.6 × 10^21)
- **P95 (95th percentile)**: ~30 septillion coins (3.0 × 10^25)
- **P99 (99th percentile)**: ~304 septillion coins (3.04 × 10^26)
- **Maximum**: ~1.9 octillion coins (1.9 × 10^28)
- **Average**: ~15.1 septillion coins (1.51 × 10^25)

**Example Values (November 2025):**
- Median: 7,668,353,665,315,050,000,000 coins (~7.7 sextillion)
- P95: 30,049,398,225,000,000,000,000,000 coins (~30 septillion)
- P99: 304,651,013,625,000,000,000,000,000 coins (~304 septillion)
- Max: 19,121,805,870,195,300,000,000,000,000 coins (~19 octillion)

## Validation Guidelines

### DO NOT Flag as Errors
- ✅ Coin amounts in trillions (10^12) - **NORMAL**
- ✅ Coin amounts in quadrillions (10^15) - **NORMAL**
- ✅ Coin amounts in sextillions (10^21) - **NORMAL**
- ✅ Coin amounts in septillions (10^24) - **NORMAL**
- ✅ Coin amounts in octillions (10^27) - **NORMAL**
- ✅ Coin amounts in undecillions (10^32) - **NORMAL for maximum values**

### DO Flag as Errors
- ❌ Negative coin amounts (unless explicitly documented as debt/negative balance)
- ❌ Zero coin amounts when activity exists (spins > 0 but balance = 0 may indicate data issue)
- ❌ Coin amounts that are orders of magnitude outside the normal ranges above
- ❌ Inconsistent relationships (e.g., win_coins > bet_coins by 1000x when no purchase occurred)

## Expected Relationships

### Balance Relationships
- **Balance End Day** should generally be positive (can be very large)
- **Balance Start Day** should generally be positive (can be very large)
- **Balance Change** = Balance End Day - Balance Start Day (can be positive or negative, can be very large)

### Bet/Win Relationships
- **Win Coins** can be larger than **Bet Coins** (players can win more than they bet)
- **Win Coins** can be smaller than **Bet Coins** (players can lose)
- Both can be in trillions, sextillions, or even higher ranges

### Payment Relationships
- **Payment Quantity** (coins purchased) can be in sextillions or higher
- **Payment Quantity** should align with **Balance Changes** when purchases occur
- Very large payment quantities are **NORMAL** in SM

## Business Context

### Why Hyperinflation Exists
- **Long-running game**: SM has been operating for many years
- **Virtual currency accumulation**: Coins accumulate over time without deflation mechanisms
- **Large user base**: Millions of players contributing to economy
- **High engagement**: Active players generate massive coin volumes
- **Game design**: SM's economy is designed to handle these large numbers

### Impact on Analysis
- **Percentile analysis**: Use percentiles rather than absolute values for comparisons
- **Ratio analysis**: Focus on ratios (e.g., win rate, consumption rate) rather than absolute amounts
- **Trend analysis**: Focus on relative changes rather than absolute values
- **Segmentation**: Compare segments using percentiles and ratios

## Data Quality Checks

### Valid Checks
- ✅ Check for negative balances (unless documented)
- ✅ Check for zero balances when activity exists (may indicate data issue)
- ✅ Check for logical relationships (win ≤ bet when no purchase, etc.)
- ✅ Check for missing data (NULL values)
- ✅ Check for data completeness

### Invalid Checks (DO NOT PERFORM)
- ❌ Flag high coin amounts as errors
- ❌ Flag amounts in trillions/sextillions/septillions as outliers
- ❌ Suggest data cleaning for large coin amounts
- ❌ Question data quality based on coin magnitude alone

## Example Validation Queries

### Valid: Check for Negative Balances
```sql
-- ✅ VALID: Check for negative balances (may indicate data issue)
SELECT 
    calc_date,
    COUNT(*) as negative_balance_count
FROM agg.agg_sm_daily_users_stats
WHERE calc_date >= CURRENT_DATE - 7
  AND balance_end_day < 0
GROUP BY calc_date;
```

### Valid: Check for Zero Balance with Activity
```sql
-- ✅ VALID: Check for zero balance when activity exists (may indicate data issue)
SELECT 
    calc_date,
    COUNT(*) as zero_balance_with_activity
FROM agg.agg_sm_daily_users_stats
WHERE calc_date >= CURRENT_DATE - 7
  AND balance_end_day = 0
  AND spins > 0
GROUP BY calc_date;
```

### Invalid: Flag High Coin Amounts
```sql
-- ❌ INVALID: DO NOT flag high coin amounts as errors
-- This query should NOT be used for validation
SELECT 
    calc_date,
    COUNT(*) as high_balance_count
FROM agg.agg_sm_daily_users_stats
WHERE calc_date >= CURRENT_DATE - 7
  AND balance_end_day > 1000000000  -- ❌ WRONG: 1 billion is actually LOW for SM
GROUP BY calc_date;
```

## Summary

**Key Message**: SM coin amounts are in extreme hyperinflation. Values in trillions, sextillions, septillions, and even undecillions are **NORMAL and EXPECTED**. Do not flag these as data quality issues or errors. Focus validation on logical relationships, missing data, and negative values, not on the magnitude of coin amounts.

**Last Updated**: November 2025  
**Data Source**: `agg.agg_sm_daily_users_stats`, `dwh.sm_fact_payments`  
**Validation Period**: Recent 7-30 days

