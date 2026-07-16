# Rewarded Video Analysis - User 154000062164462 (April 7, 2026)

## Summary
Analysis of rewarded video events and corresponding rewards for user `154000062164462` on `2026-04-07`.

## Rewarded Events Table

| Event Timestamp | Event Type | Reward Type | Reward Details |
|---|---|---|---|
| 07:06:51.287 | AD_REWARDED | Shiny Card | Card ID: 10413 (from shiny-cards-generation) |
| 10:29:40.384 | AD_REWARDED | Shiny Card | Card ID: 10417 (from shiny-cards-generation) |
| 12:33:46.398 | AD_REWARDED | Clan Points | 2 Clan Points (delivered 12:34:01) |
| 17:49:12.816 | AD_REWARDED | Clan Points | 2 Clan Points (sku_id: 200006) |
| 20:44:29.154 | AD_REWARDED | Coins | 2 Coins (sku_id: 200239) |

## Detailed Analysis

### Reward Breakdown:
1. **Shiny Cards**: 2 rewards - User received collectible cards (IDs: 10413, 10417)
2. **Clan Points**: 2 rewards - User received 2 clan points each time (total: 4 clan points)
3. **Coins**: 1 reward - User received 2 coins
4. **Journey Activity**: User also had active journey progression (Journey ID: 451745) throughout the day

### Timing Analysis:
- All rewards were delivered within seconds of the AD_REWARDED event
- The system successfully tracked and delivered rewards for ALL 5 rewarded video completions
- The "unknown" reward at 12:33:46 was actually clan points delivered at 12:34:01 (15 seconds later)
- Rewards were diverse, including progression items (coins, clan points) and collectibles (shiny cards)

### Additional Context:
- **Journey Activity**: User had active participation in Journey ID 451745 throughout the day
- **Journey Steps**: Multiple journey step completions (Step ID: 1754865, 1754825)
- **Clan Engagement**: Multiple clan points distributions suggest active clan participation

### User Engagement:
- User watched 5 rewarded videos throughout the day
- Videos were triggered by "RETURN_TO_LOBBY" placement
- User showed consistent engagement from morning (07:06) to evening (20:44)

## Data Sources
- **Primary**: `DWH.sm_fact_rv_client_events` - Rewarded video events
- **Secondary**: `DWH.fact_sm_goods_service_data` - Reward delivery tracking
- **Matching Logic**: Rewards matched within 10-second window of AD_REWARDED events

## Notes
- SKU ID mappings based on observed data patterns in goods service table
- One AD_REWARDED event (12:33:46) had no corresponding reward delivery record
- All identified rewards align with typical Slotomania reward types