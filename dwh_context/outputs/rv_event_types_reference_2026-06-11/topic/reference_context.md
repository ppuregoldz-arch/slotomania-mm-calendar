# RV Event Types Reference - Topic Context

**Business Purpose**: Create a comprehensive reference table of all event types in the RV client events table with clear explanations for each event.

**Why Created**: User requested a table of events from `dwh.sm_fact_rv_client_events` with one-sentence explanations for each event type.

**Scope**: Complete documentation of all 7 event types in the RV client events table, including their business meanings and validation requirements.

## Key Findings

### Complete Event Type Coverage
- Identified 7 distinct event types in the RV client events table
- Each event represents a specific stage in the rewarded video user journey
- Events cover the full flow from ad request through completion/failure

### Revenue Event Identification  
- Only `AD_REWARDED` events with non-null `transaction_id` generate actual revenue
- Failed or incomplete events (`AD_REWARD_FAILED`) indicate user abandoned the ad

### Event Flow Understanding
- Events follow logical progression: Request → Load → Display → Complete/Fail
- System can automatically close ads (`AD_OFFER_CLOSED_AUTOMATICALLY`)
- User restrictions are tracked (`ADS_RESTRICTED`)

## Reference Value

This reference table serves as:
- **Quick lookup** for analysts working with RV data
- **Validation guide** for ensuring correct event filtering in queries
- **Business context** for understanding user ad journey stages
- **Documentation standard** for RV event analysis

## Usage Applications

- Filter revenue queries to `AD_REWARDED` + `transaction_id IS NOT NULL`
- Analyze ad completion rates using `AD_DISPLAYED` vs `AD_REWARDED`
- Track user restrictions with `ADS_RESTRICTED` events  
- Monitor system behavior with automatic closure events