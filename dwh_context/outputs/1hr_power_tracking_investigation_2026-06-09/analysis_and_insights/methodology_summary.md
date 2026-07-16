# 1-Hour Power Booster Tracking Methodology

## Executive Summary

Based on user screenshots and investigation, we can definitively track 1-hour power booster events through the **bundle tables** that record individual purchase components. The user has identified the exact tables where this data is stored.

## Key Discovery: Bundle Tables Solution

### Primary Data Sources
1. **`dwh.sm_fact_payments_bundle_details`** - Real money purchase bundles
2. **`dwh.sm_fact_payments_bundle_details_slotobucks`** - Slotobucks purchase bundles

These tables contain individual components of purchase bundles, including the "1HR Power" benefit shown in user screenshots.

## Tracking Methodology

### Step 1: Direct Bundle Component Tracking
```sql
-- Track 1-hour power grants directly from bundle components
SELECT 
    user_id,
    transaction_id,
    bundle_component_name,
    component_type,
    component_value,
    transaction_date
FROM dwh.sm_fact_payments_bundle_details
WHERE bundle_component_name ILIKE '%power%' 
    OR bundle_component_name ILIKE '%hour%'
```

### Step 2: Purchase Attribution Analysis
```sql
-- Which products include 1-hour power benefits
SELECT 
    prod.Product_Name,
    COUNT(DISTINCT p.user_id) as purchasers,
    SUM(p.net_amount) as total_revenue
FROM dwh.sm_fact_payments p
INNER JOIN dwh.sm_fact_payments_bundle_details bd
    ON p.transaction_ticket = bd.transaction_id
LEFT JOIN sm_draft.SM_DIM_Products prod 
    ON p.sku_id = prod.sku_id
WHERE bd.bundle_component_name ILIKE '%power%'
    AND p.tran_status_id = 2
```

### Step 3: Cross-Validation with Bonus History
```sql
-- Correlate bundle power with actual bonus grants
SELECT 
    bd.user_id,
    bd.transaction_id,
    bd.bundle_component_name,
    bh.bonus_ts,
    bt.bonus_type_name
FROM dwh.sm_fact_payments_bundle_details bd
LEFT JOIN dwh.fact_sm_bonus_history bh 
    ON bd.user_id = bh.user_id
LEFT JOIN dwh.dim_sm_bonus_type bt 
    ON bh.bonus_type_id = bt.bonus_type_id
WHERE bd.bundle_component_name ILIKE '%power%'
    AND bt.bonus_type_name ILIKE '%power%'
```

## Analytics Capabilities

### 1. Power Booster Adoption Metrics
- **Grant Rate**: % of eligible purchases that include power
- **User Penetration**: % of users receiving power benefits
- **Revenue Attribution**: Revenue from power-enabled purchases

### 2. Product Performance Analysis  
- **Power Product Identification**: Which SKUs include power benefits
- **Bundle Value Analysis**: Impact of power on purchase conversion
- **Price Point Optimization**: Power inclusion across price tiers

### 3. Usage & Engagement Tracking
- **Activation Rate**: % of granted power that gets used
- **Collection Pattern Changes**: Special Bonus frequency during power periods
- **Retention Impact**: User behavior changes with power availability

## Implementation Advantages

### Direct Tracking Benefits
- **Exact Grant Moments**: Precise timestamps of power receipt
- **Purchase Attribution**: Direct link to originating transaction  
- **Bundle Context**: Full understanding of what was purchased together
- **No Inference Required**: Direct data vs. behavioral pattern analysis

### Cross-Platform Coverage
- **Real Money Purchases**: Standard payment flow power grants
- **Slotobucks Purchases**: Alternative currency power grants
- **Complete Attribution**: All power sources in single methodology

## Validation Approach

### User Transaction Method
1. **User provides transaction details** from recent power purchase
2. **Query bundle tables** for that specific transaction
3. **Verify power component** appears correctly
4. **Cross-check bonus_history** for corresponding power grant
5. **Validate timing and attribution**

### Data Quality Checks
- **Bundle completeness**: All power purchases show bundle components
- **Timing validation**: Power grants occur near purchase time
- **Cross-table consistency**: Bundle data matches bonus_history events

## Next Steps

1. **Execute queries** once MCP server available
2. **Validate with user transaction** to confirm methodology  
3. **Build comprehensive dashboard** for ongoing power analytics
4. **Document complete tracking framework** for future analyses

## Expected Business Impact

- **Product Optimization**: Identify most effective power-enabled products
- **Revenue Growth**: Optimize power inclusion strategies
- **User Experience**: Improve power benefit communication and usage
- **Feature Development**: Data-driven power system enhancements