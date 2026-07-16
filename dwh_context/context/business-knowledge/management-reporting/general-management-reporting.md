# Management Reporting - Business Context

## Overview

The **Management Report** is a critical daily executive dashboard delivered to Slotomania leadership for strategic decision-making and operational oversight. This report consolidates key performance indicators across revenue, user engagement, and operational metrics into executive-ready insights.

## Report Characteristics

### **Delivery & Audience**
- **Frequency**: Daily delivery to management
- **Audience**: Executive leadership, product managers, business stakeholders
- **Format**: Tableau dashboard with supporting data tables
- **Time Window**: Typically covers last 30-90 days with daily granularity

### **Report Focus Areas**
1. **Financial Performance**: Revenue trends, monetization efficiency
2. **User Behavior**: Engagement patterns, spending velocity  
3. **Segmentation Analysis**: Customer value distribution, tier performance
4. **Operational Health**: Economy balance, payment system performance

## Key Business Concepts

### **Customer Zone (CZ) Segmentation**
- **Purpose**: Customer lifetime value classification system
- **Ranges**: 0-10, 10-50, 50-100, 100-300, 300-500, 500+
- **Business Use**: Targeted promotions, resource allocation, balance management
- **Data Source**: `dwh.sm_user_profile_datamining_snapshot.cz_deluxe_weekly_update`

### **User Velocity Analysis**  
- **Definition**: Rate of balance consumption relative to starting balance
- **Formula**: (Bet Coins - Win Coins) / Balance Start Day
- **Business Insight**: Higher velocity = more engaged/aggressive spending
- **Management Application**: Retention strategy, monetization optimization

### **Revenue Concentration Tracking**
- **Top 1% Users**: P99 revenue percentile identification
- **Top 5% Users**: P95 revenue percentile identification  
- **Risk Assessment**: Revenue dependency on high-value users
- **Strategic Planning**: VIP program development, churn prevention

### **Prestige Economy Integration**
- **Economy Scaling**: Prestige level affects coin value through multipliers
- **Validation Logic**: Actual payment value vs. prestige-adjusted configuration
- **Business Health**: Ensures pricing consistency with progression systems

## Management KPIs

### **Primary Revenue Metrics**
- **Daily Gross Revenue**: Total revenue across all payment methods
- **Revenue by Payment Type**: PP, ROOC, Gems, promotional offers
- **Revenue by User Tier**: 1-5, 6-15, 16-25, 25+ tier performance
- **ARPU/ARPPU**: Average revenue per user/paying user trends

### **User Engagement Metrics**
- **Spending Velocity**: Balance consumption rate by tier
- **Balance Distribution**: Slotobucks balance health by CZ segment
- **User Tier Progression**: Revenue generation across progression levels
- **Active User Quality**: Engagement depth beyond basic sessions

### **Operational Health Metrics**
- **Payment Page Efficiency**: Actual vs. configured coin delivery
- **Currency Economy Balance**: Slotobucks distribution and velocity
- **Segmentation Accuracy**: CZ range effectiveness for targeting
- **System Performance**: Payment processing and delivery accuracy

## Business Intelligence Architecture

### **Data Integration Points**
1. **User Behavior**: `agg.agg_sm_daily_users_stats` - Core engagement metrics
2. **Revenue Tracking**: `dwh.sm_fact_payments` - All monetary transactions  
3. **User Profiling**: `dwh.sm_user_profile_datamining_snapshot` - Segmentation data
4. **Currency Management**: Balance update tables - Economy tracking
5. **Progression Systems**: Prestige and tier tables - Economy scaling

### **Data Quality Standards**
- **User Exclusions**: Playtika users, test accounts, migration users
- **Transaction Filters**: Successful payments only, non-artificial transactions
- **Time Boundaries**: Consistent promo date calculations with timezone adjustments
- **Validation Requirements**: Cross-table reconciliation for accuracy

## Strategic Decision Support

### **Monetization Optimization**
- **Tier Gap Analysis**: Identify progression points with monetization drops
- **Payment Method Performance**: Optimize conversion flows based on efficiency data
- **Pricing Strategy**: Validate prestige economy pricing against user behavior

### **User Retention Strategy**  
- **High-Value User Risk**: Monitor revenue concentration for churn vulnerability
- **Velocity Trends**: Track spending pattern changes for engagement health
- **Segmentation Effectiveness**: Refine CZ ranges based on behavior patterns

### **Operational Excellence**
- **Economy Tuning**: Balance currency distribution with spending velocity
- **System Performance**: Ensure payment and delivery systems operate accurately  
- **Data Accuracy**: Maintain clean user base for reliable analytics

## Report Dependencies

### **Critical Data Sources**
- Daily user statistics aggregation tables
- Payment transaction system with product mapping
- User profile datamining with segmentation logic
- Balance update tracking for economy monitoring
- Prestige and tier configuration tables

### **Supporting Systems**
- Tableau dashboard infrastructure for visualization
- Data pipeline ensuring daily refresh and accuracy
- Configuration management for prestige economy parameters
- User segmentation algorithms for CZ calculations

## Success Metrics

The Management Report's effectiveness is measured by:
1. **Decision Impact**: Strategic decisions informed by report insights
2. **Trend Identification**: Early detection of performance changes
3. **Operational Efficiency**: Quick identification of system issues
4. **Revenue Optimization**: Monetization improvements based on analysis
5. **User Experience**: Balance between revenue and player satisfaction