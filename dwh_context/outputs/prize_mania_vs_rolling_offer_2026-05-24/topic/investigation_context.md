# Prize Mania vs Rolling Offer Analysis - Investigation Context

## Investigation Purpose

This analysis was requested to compare the performance of Prize Mania and Rolling Offer features over the past 30 days, providing insights into their relative revenue contribution, user engagement patterns, and transaction behaviors.

## Business Question

**Primary Question:** How do Prize Mania and Rolling Offer compare in terms of revenue generation, user engagement, and transaction patterns?

**Specific Requirements:**
- Prize Mania metrics per promo date
- Rolling Offer average metrics across the same time period  
- Metrics: Gross Revenue, Net Revenue, Purchasers (PUs), Transactions (TRX), Average Transaction Value

## Analysis Scope & Methodology

### Time Frame Definition
- **Analysis Period**: Past 30 days (excluding today: 2026-04-26 to 2026-05-23)
- **Prize Mania Active Period**: Determined dynamically from event data (3 active dates found)
- **Rolling Offer Period**: Same date range for fair comparison

### Feature Identification Logic
- **Prize Mania**: `Product_Name ilike '%mania%'` from payment transactions
- **Rolling Offer**: `Product_Name = 'Rolling Offer'` from payment transactions
- **Data Source**: `dwh.sm_fact_payments` joined with `sm_draft.SM_DIM_Products`

### User Exclusions Applied
- Standard exclusions for clean analysis:
  - Playtika employees (`dwh.playtika_users`)  
  - Test users (`dwh.sm_fact_journey_state_notifications where step_id = 539265`)
  - Invalid transactions (`tran_status_id = 2`, `artificial_ind = 0`, `is_test = 0`)

## Key Findings Summary

### Prize Mania Performance
- **3 Active Days**: May 3, May 21, May 22, 2026
- **Total Revenue**: $242,880 across active days
- **Peak Performance**: May 22 with $130,772 revenue
- **Strong Daily Engagement**: ~11,500 purchasers per active day

### Rolling Offer Performance  
- **Consistent Operation**: All 28 days in period
- **Total Revenue**: $1,246,653 (5.1x larger than Prize Mania)
- **Steady Daily Average**: $44,523/day 
- **Broader Reach**: 31,150 total purchasers

### Transaction Behavior
- **Similar Transaction Values**: $8.71 (RO) vs $9.37 (PM)
- **Different Volume Patterns**: RO consistent daily, PM concentrated bursts
- **User Engagement Quality**: Both maintain healthy spend per transaction

## Business Context & Implications

### Feature Positioning
- **Prize Mania**: Event-driven monetization with high-intensity periods
- **Rolling Offer**: Baseline monetization infrastructure with consistent availability
- **Complementary Roles**: Peak acceleration vs. steady foundation

### Strategic Value
- Prize Mania generates **revenue spikes** during marketing campaigns
- Rolling Offer provides **predictable daily revenue** for business planning
- Combined approach maximizes both **event excitement** and **ongoing monetization**

## Analysis Limitations & Assumptions

### Data Assumptions
- Product name patterns accurately identify feature usage
- Jerusalem timezone conversion correctly reflects promo dates
- Standard user exclusions provide clean user base for comparison

### Temporal Considerations
- Prize Mania's limited activity (3/28 days) reflects intended event-based design
- Rolling Offer's daily availability enables different user engagement patterns
- Comparison captures intended operational differences between features

## Technical Implementation Notes

### Query Structure
- Union of Prize Mania (grouped by date) and Rolling Offer (aggregated) metrics
- Consistent user filtering and timezone handling across both features
- Standard payment validation filters applied uniformly

### Data Quality Validation
- Manual calculation verification: Prize Mania totals match expected aggregations
- User exclusion counts verified against standard patterns
- Transaction value ranges consistent with feature expectations

## Next Steps & Follow-up Opportunities

1. **Extended Time Analysis**: Quarterly comparison to capture seasonal patterns
2. **User Overlap Study**: Analyze cross-feature usage among the same users
3. **Revenue Attribution**: Track combined impact on overall monetization metrics
4. **Feature Optimization**: Evaluate Prize Mania frequency and Rolling Offer positioning

---

**Analysis Completed**: May 24, 2026  
**Data Coverage**: April 26 - May 23, 2026 (28 days)  
**Primary Analyst**: Slotomania Analytics Specialist