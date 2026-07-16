# CZ Analysis - Context

**Purpose**: Customer Zone (CZ) analysis framework - understanding user spending behavior, segmentation, and pricing strategies.

## Overview

CZ (Customer Zone) analysis focuses on user segmentation based on historical spending patterns and lifetime value. This is a critical dimension for understanding user behavior, pricing optimization, and revenue forecasting.

## Key CZ Concepts

### CZ Buckets
- **CZ = 0**: Users with no historical spend
- **CZ = 0.01-4.99**: Low-value spenders 
- **CZ = 5-24.99**: Mid-value spenders
- **CZ = 25-99.99**: High-value spenders
- **CZ = 100-499.99**: Very high-value spenders  
- **CZ = 500+**: Premium spenders

### CZ Applications
- **User Segmentation**: Different CZ ranges receive different experiences
- **Pricing Strategy**: Offers and pricing tiers based on CZ level
- **Revenue Forecasting**: CZ patterns predict future spending
- **Feature Targeting**: Features rolled out by CZ segments first
- **A/B Testing**: CZ-based test group allocation

## Key Tables & Fields

### Primary CZ Data Source
- `dwh.sm_user_profile_datamining_snapshot`
- Key field: `cz_price_cut_test` - The main CZ value field
- Refresh: Daily snapshots

### Common CZ Segmentation Logic
```sql
case 
    when coalesce(cz_price_cut_test, 0) = 0 then '0'
    when cz_price_cut_test < 5 then '0.01-4.99'
    when cz_price_cut_test < 25 then '5-24.99'
    when cz_price_cut_test < 100 then '25-99.99'
    when cz_price_cut_test < 500 then '100-499.99'
    else '500+' 
end as cz_range
```

## Business Context

### Analysis Focus Areas
- **CZ Distribution**: How users are distributed across CZ ranges
- **CZ Migration**: How users move between CZ segments over time
- **CZ Performance**: Revenue and engagement by CZ segment
- **CZ Targeting**: Effectiveness of CZ-based campaigns and features

### Success Metrics
- **CZ Progression**: Users moving to higher CZ ranges
- **CZ Retention**: Maintaining spend levels within CZ segments
- **CZ ARPU**: Average Revenue Per User by CZ range
- **CZ Conversion**: Converting CZ=0 users to paying users

---
*This context provides the foundation for CZ-related analysis and query development.*