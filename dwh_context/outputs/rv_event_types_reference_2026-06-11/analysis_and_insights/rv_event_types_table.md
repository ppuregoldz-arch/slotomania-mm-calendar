# RV Client Events Reference Table

**Source**: `dwh.sm_fact_rv_client_events`
**Date Created**: June 11, 2026

## Complete Event Types Table

| Event Type | Description |
|------------|-------------|
| `AD_REWARDED` | User completed the ad and received reward (check transaction_id is not null for successful completion) |
| `AD_REWARD_FAILED` | User stopped or closed the ad in the middle before completion (did not complete the ad) |
| `AD_DISPLAYED` | Ad was successfully shown to the user on screen |
| `AD_SHOW_REQUESTED` | Request to show ad was made by the client |
| `AD_LOAD_SUCCEEDED` | Ad loaded successfully and is ready to display |
| `AD_OFFER_CLOSED_AUTOMATICALLY` | System automatically closed the ad (not user-initiated) |
| `ADS_RESTRICTED` | User is restricted from seeing ads due to system rules or policies |

## Event Flow & Validation

### Typical User Journey
```
AD_SHOW_REQUESTED → AD_LOAD_SUCCEEDED → AD_DISPLAYED → AD_REWARDED/AD_REWARD_FAILED
```

### Revenue Validation
- **Revenue events**: Only `AD_REWARDED` with `transaction_id IS NOT NULL` generate actual revenue
- **Success validation**: Always check `transaction_id IS NOT NULL` for `AD_REWARDED` events
- **Failed completions**: `AD_REWARD_FAILED` indicates user didn't complete the ad

### Key Table Columns
- `event_type` - Event type from table above
- `transaction_id` - Non-null for successful reward delivery
- `revenue` - Ad revenue generated (only for successful completions)
- `user_id` - User identifier
- `event_date` - Date of event (partitioned)
- `event_ts` - Timestamp of event
- `placement` - Ad placement location
- `placement_trigger` - What triggered the ad placement

## Business Context

This table tracks all rewarded video advertisement events in Slotomania, supporting revenue optimization, user experience monitoring, and A/B testing for the RV feature across NPU and DPU user segments.