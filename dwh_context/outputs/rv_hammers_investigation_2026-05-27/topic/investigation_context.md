# RV Hammers Investigation - May 27, 2026

## Investigation Purpose
Understand how RV (Rewarded Video) ad rewards connect to hammer rewards from the "wheel of hammers" feature.

## Business Context
User watched an RV ad with "back to lobby" trigger at ~12:45 Israel time and received a wheel of hammers spin, resulting in 7 hammers. Need to trace the data connection between the ad event and the hammer reward.

## Key Discovery - Proper Connection Chain
Found the correct 4-table connection chain for RV wheel rewards:

1. **RV Event** → `transaction_id`
2. **Bonus Journey** (sku_id 200143) → `transaction_id` 
3. **Wheel Game** → `game_guid`
4. **Hammers/Goods** (sku_id 200173) → `parent_reward_request_id`

## Validation Case
- **User ID**: 154000066502254
- **RV Event**: 09:48:50 UTC (12:48 Israel time)
- **Transaction Chain**: 58835720891 → 58884637801 → ad0cc0723c96749e8891bd30bbff629b → 7 hammers
- **Result**: Successfully traced RV ad to exact hammer amount received

## Investigation Value
This establishes the proper methodology for connecting RV events to wheel-based rewards, distinguishing them from other hammer sources (purchases, etc.) through the game mechanics flow rather than timing or session assumptions.

## Tables Involved
- `dwh.sm_fact_rv_client_events` - RV ad events
- `kafka.kds_sm_bonus_history_new` - Bonus journey tracking
- `dwh.sm_external_progressive_jaw_game_played` - Wheel game mechanics
- `dwh.fact_sm_goods_service_data` - Actual goods/hammers received