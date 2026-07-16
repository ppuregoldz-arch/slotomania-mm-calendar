# SM Data Validation Checklist

## Validation Overview

**Analysis Name**: [Analysis Name]  
**Analyst**: [Analyst Name]  
**Date**: [Date]  
**Complexity Level**: 🟢🟡🔴⚫  
**Validation Confidence**: [High/Medium/Low]

**Business Context**: [Brief description of what this analysis is trying to achieve]

---

## Level 1: Raw Data Validation

### 1.1 Data Completeness
- [ ] **Record Count Validation**
  - [ ] Expected daily record counts verified
  - [ ] Missing dates identified and documented
  - [ ] Null value percentages calculated (<5% for critical fields)
  - [ ] Data freshness confirmed (last update within SLA)

- [ ] **Field Completeness**
  - [ ] Required fields present for all records
  - [ ] `daily_Net_revenue` completeness verified
  - [ ] User activity fields (spins, bet_coins, win_coins) complete
  - [ ] Balance fields (balance_start_day, balance_end_day) complete

### 1.2 Data Integrity
- [ ] **Data Type Validation**
  - [ ] Numeric fields contain valid numbers
  - [ ] Date fields in correct format (YYYY-MM-DD)
  - [ ] `calc_date` format validated
  - [ ] `tran_date` format validated

- [ ] **Constraint Validation**
  - [ ] Primary key uniqueness verified (user_id + calc_date)
  - [ ] Foreign key relationships valid
  - [ ] Business rule constraints enforced

### 1.3 Range Validation
- [ ] **Numeric Ranges**
  - [ ] Revenue amounts within business expectations
  - [ ] User counts reasonable (hundreds of thousands, not tens of thousands)
  - [ ] Balance values logical
  - [ ] Spin counts reasonable

- [ ] **Date Ranges**
  - [ ] Dates not in the future
  - [ ] Historical dates within reasonable range
  - [ ] Current date excluded for incomplete periods

---

## Level 2: Business Logic Validation

### 2.1 Revenue Calculation Validation
- [ ] **Revenue Calculations**
  - [ ] Daily Net revenue = sum of individual approved transactions
  - [ ] ARPU = total revenue / total users
  - [ ] ARPPU = total revenue / paying users
  - [ ] Revenue matches aggregated table

- [ ] **Status Filter Validation**
  - [ ] `tran_status_id = 2` filter applied (approved only)
  - [ ] `is_test = 0` filter applied
  - [ ] `artificial_ind = 0` filter applied
  - [ ] Revenue not inflated (matches aggregated table)

### 2.2 User Count Validation
- [ ] **DAU Calculation**
  - [ ] DAU = unique users per day
  - [ ] User counts in hundreds of thousands (not tens of thousands)
  - [ ] Two-step aggregation used for period comparisons

- [ ] **Paying User Calculation**
  - [ ] Paying users = users with `daily_Net_revenue > 0`
  - [ ] Paying users ≤ DAU
  - [ ] Conversion rate logical

### 2.3 Aggregation Methodology Validation
- [ ] **Two-Step Aggregation**
  - [ ] Step 1: Daily metrics calculated with `GROUP BY calc_date`
  - [ ] Step 2: Monthly averages calculated with `AVG(daily_metric)`
  - [ ] Results match simple daily queries
  - [ ] No single-step aggregation used

### 2.4 Currency Separation Validation
- [ ] **Real Money Revenue**
  - [ ] Real money revenue from `dwh.sm_fact_payments.net_amount`
  - [ ] Status filter applied (`tran_status_id = 2`)
  - [ ] Reported in USD

- [ ] **Virtual Currency**
  - [ ] Virtual currency from `dwh.sm_fact_virtual_payment_slotobucks.transaction_amount`
  - [ ] Status filter applied (`tran_status_id = 2`)
  - [ ] Reported separately (NOT added to real money)

---

## Level 3: Cross-Table Validation

### 3.1 Revenue Cross-Validation
- [ ] **Fact vs Aggregated Table**
  - [ ] Fact table revenue matches aggregated table
  - [ ] Difference < $100 or < 1%
  - [ ] Status filter verified in fact table

### 3.2 User Activity Cross-Validation
- [ ] **Activity Consistency**
  - [ ] Spins align with bet_coins
  - [ ] Balance changes align with activity
  - [ ] Session counts align with activity

### 3.3 Segment Cross-Validation
- [ ] **CZ Deluxe Segments**
  - [ ] Segment assignment accurate
  - [ ] Snapshot date alignment correct
  - [ ] Segment totals consistent

---

## Level 4: Statistical Validation

### 4.1 Distribution Analysis
- [ ] **Revenue Distribution**
  - [ ] Revenue distribution reasonable
  - [ ] Outliers identified and explained
  - [ ] Percentiles calculated correctly

- [ ] **User Distribution**
  - [ ] User count distribution reasonable
  - [ ] Segment distribution logical
  - [ ] Balance distribution healthy

### 4.2 Outlier Detection
- [ ] **Statistical Outliers**
  - [ ] Outliers identified (>2 standard deviations)
  - [ ] Outliers explained or excluded
  - [ ] Outlier impact assessed

---

## Level 5: Business Logic Validation

### 5.1 Business Rules
- [ ] **Revenue Rules**
  - [ ] Approved transactions only
  - [ ] Test transactions excluded
  - [ ] Artificial transactions excluded

- [ ] **Economy Rules**
  - [ ] Balance calculations logical
  - [ ] Consumption rates reasonable
  - [ ] Currency flow consistent

### 5.2 Edge Cases
- [ ] **Boundary Conditions**
  - [ ] Zero revenue days handled
  - [ ] Zero activity days handled
  - [ ] Missing data handled

---

## Level 6: Historical Validation

### 6.1 Benchmark Comparison
- [ ] **Historical Benchmarks**
  - [ ] Results compared to historical averages
  - [ ] Trends consistent with historical patterns
  - [ ] Anomalies explained

### 6.2 Trend Validation
- [ ] **Temporal Consistency**
  - [ ] Trends logical over time
  - [ ] Seasonal patterns consistent
  - [ ] Growth/decline patterns explained

---

## Validation Summary

### Validation Results
- **Level 1 (Raw Data)**: ✅ Pass / ❌ Fail
- **Level 2 (Business Logic)**: ✅ Pass / ❌ Fail
- **Level 3 (Cross-Table)**: ✅ Pass / ❌ Fail
- **Level 4 (Statistical)**: ✅ Pass / ❌ Fail
- **Level 5 (Business Rules)**: ✅ Pass / ❌ Fail
- **Level 6 (Historical)**: ✅ Pass / ❌ Fail

### Overall Validation Status
- **Status**: ✅ Validated / ❌ Issues Found
- **Confidence Level**: [High/Medium/Low]
- **Issues Identified**: [List any issues]
- **Recommendations**: [List recommendations]

### Validation Users
- **User 1**: [User ID] - [Validation Result]
- **User 2**: [User ID] - [Validation Result]
- **User 3**: [User ID] - [Validation Result]

This checklist ensures comprehensive validation of SM data analysis with proper attention to SM-specific data patterns and business rules.

