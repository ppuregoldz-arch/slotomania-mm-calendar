# 1-Hour Power Booster Tracking Investigation

## Context
User requested to track the exact event of receiving 1-hour power boosters from purchases. They clarified that 1-hour power can come from various purchase types (not just gem purchases) and provided screenshots showing "1HR Power" as a bundle component in purchase confirmations.

## Screenshots Analysis
User provided 3 screenshots showing:

1. **Store Interface**: Shows "1HR Power" as a visible benefit in purchase bundle alongside coins, club points, status points
2. **Purchase Bundle Details**: Shows the bundle structure with "1HR Power Available for 7 days" as a distinct component  
3. **Purchase Confirmation**: Shows "1HR Power Available for 7 days" granted after successful purchase

## Key Discovery
The user identified two critical tables for tracking bundle components:
- `dwh.sm_fact_payments_bundle_details_slotobucks` - For Slotobucks purchases
- `dwh.sm_fact_payments_bundle_details` - For real money purchases

These tables should contain the actual bundle component information including 1-hour power benefits.

## Investigation Approach

### Phase 1: Bundle Table Analysis
- Explore structure of both bundle tables
- Identify how 1-hour power is recorded as bundle component
- Understand field mappings (component_name, component_type, etc.)

### Phase 2: Cross-Reference Analysis  
- Link bundle details to main payments table
- Correlate with bonus_history for actual power grants
- Validate timing between purchase and power activation

### Phase 3: User Transaction Validation
- User will provide specific transaction details from recent purchase
- Use transaction to validate our tracking methodology
- Confirm end-to-end flow from purchase → bundle → power grant

## Business Questions to Answer

1. **Direct Tracking**: Can we see "1HR Power" entries in bundle tables?
2. **Purchase Attribution**: Which specific products include 1-hour power benefits?
3. **Grant Mechanism**: How is the power actually applied to user accounts?
4. **Duration Tracking**: How do we track the 7-day availability period?
5. **Usage Analytics**: Can we measure power activation vs. availability?

## Expected Outcomes

1. **Complete tracking methodology** for 1-hour power booster events
2. **Product analysis** showing which purchases include power benefits  
3. **User journey mapping** from purchase → power grant → usage
4. **Performance metrics** for power booster adoption and effectiveness

## Technical Approach

- Focus on bundle tables as primary data source
- Cross-reference with bonus_history for validation
- Use transaction timing to correlate purchase → power events
- Validate methodology with user's actual transaction

## Next Steps

1. Run bundle table exploration queries once MCP server available
2. Get user transaction details for validation
3. Build comprehensive tracking dashboard
4. Document complete 1-hour power analytics methodology