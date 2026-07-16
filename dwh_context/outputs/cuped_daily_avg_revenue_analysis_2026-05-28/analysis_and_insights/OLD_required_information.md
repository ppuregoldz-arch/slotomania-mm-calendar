# Required Information - CUPED Daily Avg Revenue Analysis

## Test Configuration

**Test ID:** ahhcuJnMV1

**Date Ranges:**
- **Start Date (Promo Date):** May 20, 2024
- **End Date (Promo Date):** May 26, 2024 (inclusive)
- **Pre-experiment Period:** 14 days (May 6, 2024 - May 19, 2024)
- **Experiment Period:** 7 days (May 20, 2024 - May 26, 2024)

## Population Definition

**Target Population:** "During" users only
- **Definition:** Users who were active during the test period (May 20-26, 2024 promo dates)
- **Criteria:** Must have activity/engagement during the experiment period
- **Exclusions:** Users who were only assigned to test but not active during test period

## CUPED Methodology Requirements

**Pre-experiment Covariate Period:** 14 days before test start
- **Purpose:** Establish baseline revenue patterns for variance reduction
- **Period:** May 6-19, 2024 (14 days)
- **Metric:** Daily average revenue per user during pre-period

**Experiment Period Analysis:** 7 days during test
- **Purpose:** Measure treatment effect on daily average revenue
- **Period:** May 20-26, 2024 (7 days)
- **Metric:** Daily average revenue per user during experiment period

## Key Analysis Components

1. **Population Identification:** Extract users active during May 20-26, 2024
2. **Pre-period Revenue:** Calculate baseline daily avg revenue (May 6-19)
3. **Experiment Revenue:** Calculate treatment daily avg revenue (May 20-26)
4. **CUPED Adjustment:** Apply variance reduction using pre-period covariate
5. **Treatment Effect:** Measure adjusted difference between control and treatment groups

## Expected Deliverables

- SQL queries for data extraction and CUPED calculations
- Analysis of treatment effect with variance reduction
- Comparison of CUPED vs. non-CUPED results
- Statistical significance testing of adjusted treatment effect