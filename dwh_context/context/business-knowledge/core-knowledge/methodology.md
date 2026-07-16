# Slotomania Product Usage Analysis - Methodology

**Last Updated:** 2024-01-15  
**Version:** 1.0  
**Analysis Type:** Descriptive Analytics with Time-series Comparison

---

## Analysis Approach Overview

### Primary Objective
Understand product usage pattern changes in Slotomania and quantify their impact on monetization metrics through time-based comparative analysis.

### Core Methodology
**Two-Query Aggregated Analysis** with temporal comparison framework:
1. **Product Usage Analysis:** User engagement and adoption patterns
2. **Revenue Metrics Analysis:** Monetization effectiveness and value trends

---

## Statistical Framework

### Time-series Comparison Design
- **Short-term Analysis:** Last 30 days (recent trends)
- **Long-term Analysis:** Last 90 days (extended patterns)
- **Comparison Method:** Cross-sectional analysis between time periods

### Sample Size Requirements
- **Usage Analysis:** Minimum 100 unique users per segment
- **Revenue Analysis:** Minimum 50 paying users per segment
- **Confidence Level:** 95% for all statistical inferences

### Segmentation Strategy
1. **Time-based:** 30-day vs 60-day vs 90-day periods
2. **User-based:** Tier levels (Bronze to Black Diamond)
3. **Experience-based:** Level buckets (Beginner to Expert)
4. **Product-based:** Category and individual product analysis

---

## Query 1: Product Usage Analysis Methodology

### Purpose
Identify changes in user engagement patterns and product adoption between recent and extended time periods.

### Key Metrics Framework
```
Engagement Depth = avg_session_duration × interactions_per_session
User Penetration = (product_users / total_dau) × 100
Usage Intensity = total_interactions / unique_users
Adoption Rate = unique_users_by_period / total_period_users
```

### Analysis Dimensions
1. **Temporal Dimension:** 30-day vs 90-day comparison
2. **Product Dimension:** Individual products and categories
3. **User Dimension:** Tier and level segmentation
4. **Behavioral Dimension:** Interaction types and patterns

### Statistical Measures
- **Central Tendency:** Mean, median for continuous variables
- **Distribution:** Percentiles for transaction analysis
- **Penetration:** Percentage calculations for adoption metrics
- **Frequency:** Count-based metrics for usage patterns

---

## Query 2: Revenue Metrics Analysis Methodology

### Purpose
Quantify revenue impact of usage pattern changes and assess value proposition trends.

### ARPPU Calculation Framework
```
ARPPU = Total Revenue (USD) / Unique Paying Users
Transaction Frequency = Total Transactions / Unique Paying Users
Average Transaction Size = Total Revenue / Total Transactions
```

### Value for Money (VFM) Analysis
```
VFM Ratio = Coins Purchased / USD Amount
VFM Trend = Current Period VFM / Historical Average VFM
VFM Improvement = (Recent VFM - Extended VFM) / Extended VFM × 100
```

### Revenue Segmentation
1. **User Tier Analysis:** Revenue by player tier
2. **Product Category Analysis:** Revenue by product type
3. **Payment Behavior Analysis:** First-time vs returning payers
4. **Promotion Impact Analysis:** Personal offers vs regular pricing

---

## Data Processing Methodology

### Data Quality Assurance
1. **Validation Filters:**
   - Active users only (`user_status = 'active'`)
   - Completed transactions only (`transaction_status = 'completed'`)
   - Positive amounts only (`usd_amount > 0`)
   - Recent data only (within 90-day window)

2. **Outlier Management:**
   - Statistical thresholds using percentile analysis
   - Business logic validation for reasonable values
   - Documentation of excluded data points

### Aggregation Strategy
- **No CTEs:** Using subqueries and window functions for compliance
- **Join Strategy:** Inner joins for core analysis, left joins for optional dimensions
- **Grouping Hierarchy:** Time period → Product → User segment
- **Ordering:** Prioritize by business impact (revenue, user volume)

---

## Temporal Analysis Framework

### Time Period Definition
```sql
CASE 
    WHEN event_date >= CURRENT_DATE - 30 THEN '30_day_recent'
    WHEN event_date >= CURRENT_DATE - 60 THEN '60_day_recent'
    WHEN event_date >= CURRENT_DATE - 90 THEN '90_day_extended'
    ELSE 'older'
END AS time_period
```

### Trend Analysis Approach
1. **Period-over-Period Comparison:** Direct metric comparison
2. **Rate of Change Calculation:** Percentage change between periods
3. **Statistical Significance:** Sample size validation
4. **Business Context:** Alignment with known business events

---

## Statistical Assumptions & Limitations

### Key Assumptions
1. **Data Completeness:** 90-day historical data is complete and accurate
2. **User Behavior Stability:** No major external factors affecting behavior
3. **Product Consistency:** Product definitions remain stable across time periods
4. **Currency Stability:** USD conversion rates are consistent

### Known Limitations
1. **Causation vs Correlation:** Analysis is descriptive, not causal
2. **External Factors:** Cannot control for marketing campaigns, seasonality
3. **Sample Bias:** Analysis limited to active users only
4. **Time Granularity:** Daily-level analysis, not intraday patterns

### Mitigation Strategies
- **Minimum Sample Sizes:** Ensure statistical reliability
- **Multiple Metrics:** Cross-validate findings across different measures
- **Business Context:** Validate findings against known business events
- **Documentation:** Clear documentation of limitations and assumptions

---

## Results Interpretation Framework

### Statistical Significance Testing
- **Sample Size Validation:** Ensure minimum thresholds are met
- **Percentage Change Thresholds:** 
  - Material change: >10% difference
  - Significant change: >20% difference
  - Major change: >50% difference

### Business Impact Assessment
1. **Revenue Impact:** Direct USD impact calculation
2. **User Engagement Impact:** User volume and frequency changes
3. **Product Performance Impact:** Product-specific adoption changes
4. **Strategic Implications:** Long-term trend identification

### Quality Control Measures
- **Cross-Metric Validation:** Ensure consistency across related metrics
- **Historical Context:** Compare against known benchmarks
- **Outlier Investigation:** Investigate and document unusual findings
- **Business Logic Validation:** Ensure results align with business understanding

---

## Reproducibility Standards

### Version Control
- **Query Versioning:** Date-stamped SQL files with version numbers
- **Documentation Versioning:** Tracked changes in methodology
- **Results Archiving:** Timestamped result sets for future reference

### Environment Specifications
- **Database:** Vertica 25.1.0 (playtika_dwh)
- **User Access:** Read-only analytical access
- **Dependencies:** Standard SQL functions only (no custom functions)

### Validation Checklist
- [ ] Sample sizes meet minimum requirements
- [ ] Data quality filters applied correctly
- [ ] Business logic validation completed
- [ ] Cross-metric consistency verified
- [ ] Results documented with context

---
