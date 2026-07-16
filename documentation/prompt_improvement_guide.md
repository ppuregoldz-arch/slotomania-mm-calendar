# Prompt Improvement Guide (SM)

## Rubric (1-5)
- **Clarity**: Is the request specific and unambiguous?
- **Scope**: Are metrics, timeframe, and segments clearly defined?
- **Complexity**: Is the request appropriately scoped?
- **Actionability**: Will results drive business decisions?

## Improve Prompts

### Specify Metrics
- Revenue: Daily Net Revenue, ARPU, ARPPU, Gross Revenue
- User: DAU, Paying Users, FTDs, Churn Rate
- Engagement: Spins, Sessions, Bet Coins, Win Coins
- Economy: Balance, Consumption Rate, Velocity
- Product: Revenue by Product Group, Value-for-Money

### Define Timeframe
- Specific dates: "2025-01-01 to 2025-01-31"
- Relative periods: "Last 30 days", "Current month", "Q1 2025"
- Granularity: Daily, weekly, monthly
- **CRITICAL**: Exclude current date for incomplete periods

### Define Segments
- CZ Deluxe: 0-5, 5-10, 10-20, 20-40, 40-60, 60-80, 80-100, +100
- VIP Tiers: Tier 1-3, Tier 4+
- Paying Status: Paying Users, Non-Paying Users
- Platform: iOS, Android, Web
- Product Groups: By product category

### State Business Objective
- Decision: "to inform pricing strategy"
- Use-case: "to optimize monetization campaigns"
- Analysis: "to identify retention opportunities"
- Monitoring: "to track daily performance"

## Structure
"Analyze [metric] by [segment] for [timeframe] to [business objective]."

## Examples

### Revenue Analysis
- ✅ **Good**: "Analyze daily Net revenue by CZ deluxe segment (0-5, 5-10, 10-20, etc.) for the last 30 days to identify monetization opportunities and inform pricing strategy decisions."
- ❌ **Poor**: "Show me revenue data"

### User Engagement
- ✅ **Good**: "Compare spin frequency and session duration between paying and non-paying users for Q1 2025 to optimize engagement strategies and identify conversion opportunities."
- ❌ **Poor**: "Compare user behavior"

### Economy Analysis
- ✅ **Good**: "Analyze coin consumption rates by CZ deluxe segment for the last 30 days to optimize economy balance and inform currency injection strategies."
- ❌ **Poor**: "Analyze consumption"

### Product Performance
- ✅ **Good**: "Analyze revenue by product group for the last month, including value-for-money metrics, to inform product development priorities and pricing optimization."
- ❌ **Poor**: "Show product data"

### Churn Analysis
- ✅ **Good**: "Analyze churn rates by CZ deluxe segment for the last 90 days, including days from last login breakdown, to inform retention campaigns and identify at-risk user segments."
- ❌ **Poor**: "Analyze churn"

## SM-Specific Considerations

### Revenue Analysis Prompts
- **Always specify**: Real money revenue vs virtual currency redemption (separate metrics)
- **Always specify**: Use daily Net revenue (approved revenue)
- **Always specify**: Product group breakdown if needed

### User Engagement Prompts
- **Always specify**: CZ deluxe segments or VIP tiers for segmentation
- **Always specify**: Paying vs non-paying users if relevant
- **Always specify**: Timeframe with date exclusion for incomplete periods

### Economy Analysis Prompts
- **Always specify**: Balance distribution percentiles (25th, 50th, 75th, 95th)
- **Always specify**: Consumption rate calculation method
- **Always specify**: Currency type (coins, gems, slotobucks)

### Product Analysis Prompts
- **Always specify**: Product group vs SKU level analysis
- **Always specify**: Value-for-money metrics if needed
- **Always specify**: Real money vs virtual currency products

## Documentation
Record prompt quality and improvements in `prompt_documentation/`.

## Common Issues

### Missing Timeframe
- ❌ "Analyze revenue by segment"
- ✅ "Analyze daily Net revenue by CZ deluxe segment for the last 30 days"

### Missing Segments
- ❌ "Compare user behavior"
- ✅ "Compare spin frequency and session duration between CZ deluxe segments 20-40 and 40-60 for Q1 2025"

### Missing Business Objective
- ❌ "Show me product data"
- ✅ "Analyze revenue by product group for the last month to inform product development priorities"

### Currency Confusion
- ❌ "Show total revenue including slotobucks"
- ✅ "Show real money revenue (USD) and slotobucks redemption (virtual currency) separately by product group"

### Aggregation Issues
- ❌ "Show average DAU for January"
- ✅ "Show average daily DAU for January 2025 using two-step aggregation methodology"

This guide ensures clear, actionable prompts for SM data analysis with proper specification of metrics, timeframes, segments, and business objectives.

