# Management Report - Business Intelligence & Query Patterns

**Purpose**: Document the business logic, KPIs, and analytical patterns used in daily management reporting for executive oversight and decision-making.

## Management Report Overview

The Management Report is a **daily executive dashboard** sent to leadership, focusing on:
- **Financial Performance**: Revenue, user monetization, payment method efficiency
- **User Engagement**: Retention, spending velocity, balance management  
- **Segmentation Analysis**: CZ (Customer Zone) ranges, tier analysis, high-value user tracking
- **Operational KPIs**: Payment page performance, prestige economy impact

## Key Business Intelligence Patterns

### 1. **User Velocity Analysis**
- **Concept**: Velocity = (Bet Coins - Win Coins) / Starting Balance 
- **Business Purpose**: Measure how quickly users spend through their balance
- **Key Insight**: Higher velocity indicates more engaged/aggressive spending behavior
- **Management Use**: Track spending intensity across tiers for retention and monetization optimization

### 2. **CZ (Customer Zone) Segmentation**
- **CZ Ranges**: 0-10, 10-50, 50-100, 100-300, 300-500, 500+
- **Business Logic**: CZ represents customer lifetime value/spending potential
- **Slotobucks Analysis**: Balance distribution shows liquidity management by value segment
- **Management Use**: Resource allocation, targeted promotions, balance economy health

### 3. **High-Value User Identification**
- **Top 1% Users**: P99 percentile by monthly revenue
- **Top 5% Users**: P95 percentile by monthly revenue  
- **Business Purpose**: VIP identification and revenue concentration analysis
- **Management Use**: Understanding revenue dependence on whale users

### 4. **Prestige Economy Validation**
- **Formula**: Config Value = Base Coins × Prestige Multiplier × Tier Multiplier
- **Sale vs PP Ratio**: (Payment Quantity - Config Value) / Config Value
- **Business Purpose**: Validate pricing against prestige-enhanced economy
- **Management Use**: Ensure pricing consistency with progression systems

## Core Management KPIs

### **Financial Metrics**
1. **Daily Revenue**: Gross revenue by payment method (PP, ROOC, Gems, etc.)
2. **ARPU/ARPPU**: Average revenue per user/paying user
3. **Revenue Concentration**: % revenue from top 1%/5% users
4. **Payment Method Mix**: Revenue distribution across purchase types

### **User Metrics** 
1. **Spending Velocity**: Rate of balance consumption by tier
2. **Balance Health**: Slotobucks distribution across CZ segments
3. **Tier Progression**: Revenue generation by user tier groups
4. **User Lifecycle**: New vs. returning purchaser analysis

### **Operational Metrics**
1. **Payment Page Efficiency**: Actual vs. configured coin values
2. **Prestige Impact**: Multiplier effectiveness on pricing
3. **CZ Effectiveness**: Segmentation accuracy for targeting
4. **Economy Balance**: Currency distribution and velocity

## Data Quality & Filters

### **Standard Exclusions**
- **Playtika Users**: `user_id not in (select distinct user_id from dwh.playtika_users)`
- **Test Users**: `artificial_ind = 0` and `is_test = 0`
- **Journey Notifications**: `step_id = 539265` exclusion for clean user base
- **Migration Users**: Coins reset migration exclusions for accurate balance tracking

### **Key Table Relationships**
- **User Stats**: `agg.agg_sm_daily_users_stats` - Core daily user behavior
- **Payments**: `dwh.sm_fact_payments` + `sm_draft.SM_DIM_Products` - Revenue tracking  
- **Datamining**: `dwh.sm_user_profile_datamining_snapshot` - CZ and segmentation
- **Balance Tracking**: `dwh.sm_fact_internal_purchase_balance_update_slotobucks` - Currency management
- **Prestige**: `dwh.sm_fact_precious_level_up` + multiplier tables - Economy scaling

## Dashboard Intelligence Insights

### **Revenue Concentration Analysis**
- Tracks what % of total revenue comes from top spending users
- Identifies revenue risk if high-value users churn
- Guides VIP program and retention strategies

### **Balance Economy Health**
- Monitors Slotobucks distribution to prevent inflation/deflation
- Tracks velocity to ensure healthy spending patterns
- Validates currency sink/source balance

### **Tier-Based Performance**
- Revenue generation efficiency by user progression level
- Identifies tier gaps where monetization drops
- Guides progression pacing and reward optimization

### **Payment Method Optimization**
- Compares performance across different purchase flows
- Validates prestige economy pricing accuracy
- Identifies opportunities for conversion improvement

## Management Decision Support

This dashboard enables executive decisions on:
1. **Monetization Strategy**: Based on velocity and tier analysis
2. **User Retention**: Using high-value user concentration data
3. **Economy Tuning**: Via balance distribution and velocity metrics
4. **Pricing Optimization**: Through payment page performance analysis
5. **Segmentation Refinement**: Using CZ effectiveness measurements

## Query Validation Patterns

### **Revenue Validation**
- Cross-reference payment table with product dimensions
- Validate prestige calculations against configuration tables
- Ensure tier multipliers align with progression data

### **User Segmentation Validation**
- Verify CZ ranges produce meaningful user distributions
- Check tier groupings capture progression accurately  
- Validate exclusion filters remove test/internal users

### **Balance Economy Validation**
- Reconcile balance updates with payment transactions
- Check velocity calculations for mathematical accuracy
- Verify percentile distributions make business sense