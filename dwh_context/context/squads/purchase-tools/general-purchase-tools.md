# General Purchase Tools - Complete Context

**Squad**: Purchase Tools
**Scope**: All Purchase Tools functionality including monetization features, virtual currencies, offers, and purchase optimization

## Overview
Purchase Tools encompass all monetization-related features in Slotomania, focusing on converting users to paying customers and maximizing revenue through various purchase mechanisms, virtual currencies, and dynamic offers.

---

## Main Tables Used

### 1. dwh.sm_fact_payments
**Purpose**: Real money payment transactions
**Key Columns**:
- `user_id` - User identifier
- `tran_date` - Transaction date
- `tran_status_id` - Transaction status (2 = successful)
- `gross_amount` - Gross payment amount
- `net_amount` - Net payment amount
- `product_id` - Product purchased
- `platform` - Payment platform
- `artificial_ind` - Artificial transaction indicator
- `is_test` - Test transaction indicator

### 2. dwh.sm_fact_internal_purchase_balance_update_slotobucks
**Purpose**: SlotoBucks virtual currency transactions
**Key Columns**:
- `user_id` - User identifier
- `timestamp` - Transaction timestamp
- `delta` - SlotoBucks change amount
- `new_balance` - New SlotoBucks balance
- `reason` - Transaction reason/source
- `transaction_id` - Unique transaction identifier

### 3. dwh.sm_fact_internal_purchase_balance_update_gems
**Purpose**: Gems virtual currency transactions
**Key Columns**:
- `user_id` - User identifier
- `timestamp` - Transaction timestamp
- `delta` - Gems change amount
- `new_balance` - New Gems balance
- `reason` - Transaction reason/source
- `source` - Gems source (purchase, reward, etc.)

### 4. agg.agg_sm_daily_users_stats
**Purpose**: Daily user aggregated metrics including revenue
**Key Purchase-Related Columns**:
- `user_id` - User identifier
- `calc_date` - Calculation date
- `daily_Net_revenue` - Daily net revenue (TRUSTED SOURCE)
- `balance_end_day` - End of day balance
- `daily_sessions` - Daily sessions count

### 5. dwh.sm_user_profile_datamining_snapshot
**Purpose**: User segmentation and configuration
**Key Purchase-Related Columns**:
- `user_id` - User identifier
- `cz_price_cut_test` - Customer Zone value (spending history)
- `purchase_config_buckets` - Purchase configuration segments
- `snapshot_date` - Snapshot date

## Purchase Tools Features

### MGAP (Main Monetization Tool)
- Primary purchase optimization feature
- Dynamic pricing and offers
- User segmentation for purchase targeting

### LBP (Purchase Optimization)
- Purchase funnel optimization
- Conversion rate improvement
- User experience optimization

### AVIATOR 
- Purchase tool feature
- Advanced purchase mechanics

### SlotoBucks System
- Primary virtual currency
- Earned through gameplay and purchases
- Used for slot machine spins

### Gems System  
- Premium virtual currency
- Primarily purchased with real money
- Used for premium features and shortcuts

### Offers System
- **Rolling Offers**: Dynamic, rotating purchase offers
- **Sticky Bundle**: Persistent purchase packages
- **Reveal Your Deal**: Personalized deal discovery

### Prize Mania
- Prize and reward distribution system
- Gamified prize mechanics
- User engagement through rewards

### Config Buckets
- User segmentation for purchase features
- A/B testing configurations
- Dynamic feature enablement

## Standard Filters & Patterns

### Payment Filters
```sql
-- Only successful real money payments
tran_status_id = 2 
and artificial_ind = 0 
and is_test = 0

-- Exclude test users
user_id not in (select distinct user_id from dwh.playtika_users)

-- Exclude journey step users  
user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
```

### Revenue Authority
```sql
-- ALWAYS use agg table for revenue
daily_Net_revenue from agg.agg_sm_daily_users_stats
-- This is the ONLY trusted revenue source
```

### CZ Segmentation for Purchase Analysis
```sql
-- Standard CZ buckets for purchase behavior
case 
    when coalesce(cz_price_cut_test, 0) = 0 then '0'
    when cz_price_cut_test < 5 then '0.01-4.99'
    when cz_price_cut_test < 25 then '5-24.99'
    when cz_price_cut_test < 100 then '25-99.99'
    when cz_price_cut_test < 500 then '100-499.99'
    else '500+' 
end as cz_range
```

## Common Analysis Patterns

### Purchase Conversion Analysis
- First-time buyer conversion rates
- Purchase funnel drop-off analysis
- Feature-specific conversion metrics
- Segmented conversion by user type

### Revenue Analysis
- Daily/weekly/monthly revenue trends
- Revenue per user by segments
- Product performance analysis
- Pricing optimization impact

### Virtual Currency Analysis
- SlotoBucks flow and velocity
- Gems purchase and usage patterns
- Currency balance distributions
- Cross-currency conversion analysis

### Offer Performance Analysis
- Offer impression and conversion rates
- Dynamic pricing effectiveness
- User response to different offer types
- Seasonal and temporal offer patterns

### User Segmentation
- Purchase behavior segmentation
- CZ-based analysis
- First-time vs returning buyers
- High-value user identification

## Business Logic

### Purchase Flow Validation
- Verify transaction completion
- Check payment gateway responses
- Validate product delivery
- Monitor refund and chargeback rates

### Virtual Currency Integrity
- Balance consistency checks
- Transaction audit trails
- Currency exchange validations
- Anti-fraud monitoring

### Configuration Management
- A/B test group assignments
- Feature flag compliance
- Dynamic configuration updates
- Rollback procedures

## Key Performance Indicators

### Revenue KPIs
- **ARPU**: Average Revenue Per User
- **ARPPU**: Average Revenue Per Paying User
- **Conversion Rate**: % of users making purchases
- **LTV**: Lifetime Value projections

### Engagement KPIs
- **Purchase Frequency**: How often users buy
- **Time to First Purchase**: User journey to conversion
- **Retention**: Purchase impact on user retention
- **Feature Adoption**: Usage rates of purchase tools

### Product KPIs
- **Product Mix**: Distribution of product sales
- **Pricing Elasticity**: Price sensitivity analysis
- **Offer Performance**: Success rates of different offers
- **Currency Velocity**: Virtual currency usage patterns

---

## Technical Notes

### Performance Optimization
- Always use agg tables for revenue calculations
- Filter by date ranges to optimize query performance
- Use proper indexes on user_id and date fields
- Avoid cross-joins between large transaction tables

### Data Quality Considerations
- Revenue authority: Only trust agg.agg_sm_daily_users_stats
- Transaction status validation is critical
- Test user exclusion is mandatory
- Balance consistency requires careful handling

### Integration Points
- **Payment Gateways**: External payment processing validation
- **Virtual Currencies**: Cross-system balance management
- **User Segmentation**: Dynamic bucket assignments
- **A/B Testing**: Configuration and performance tracking

---
*This file serves as the comprehensive reference for all Purchase Tools-related analysis and context. Specialized sub-features have dedicated folders with additional detail.*