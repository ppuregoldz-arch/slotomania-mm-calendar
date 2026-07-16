/*
RV Hammers Investigation - Connection Chain Query
===============================================
Purpose: Connect RV AD_REWARDED events to hammers received from wheel of hammers
Business Question: How do RV ads lead to hammer rewards through wheel mechanics?

Connection Chain Discovery:
1. RV Event (transaction_id) → 
2. Bonus Journey (sku_id 200143) → 
3. Wheel Game (game_guid) → 
4. Goods/Hammers (sku_id 200173)

Validated with user 154000066502254:
- RV transaction: 58835720891 → Bonus: 58884637801 → Wheel: ad0cc0723c96749e8891bd30bbff629b → 7 hammers
*/

select 
    rv.user_id,
    rv.event_type,
    rv.event_ts,
    coalesce(hammers.bonus_amount, 0) as hammers_received

/*RV client events*/
from (
    select user_id, event_type, event_ts, transaction_id
    from dwh.sm_fact_rv_client_events
    where event_date = current_date
      and event_type = 'AD_REWARDED'
      and user_id not in (select distinct user_id from dwh.playtika_users)
) rv

/*bonus journey - wheel trigger (sku_id 200143)*/
left join (
    select user_id, skudata_tran_ticket, transaction_id
    from kafka.kds_sm_bonus_history_new
    where sku_id = 200143  -- Wheel journey trigger
      and bonus_date = current_date
) bonus on rv.user_id = bonus.user_id 
    and rv.transaction_id = bonus.skudata_tran_ticket

/*wheel game - generates game_guid*/
left join (
    select user_id, game_guid, source_reward_id
    from dwh.sm_external_progressive_jaw_game_played
    where event_date = current_date
) wheel on bonus.user_id = wheel.user_id 
    and bonus.transaction_id = wheel.source_reward_id

/*goods service - hammers (sku_id 200173)*/
left join (
    select 
        user_id, 
        bonus_amount, 
        parent_reward_request_id,
        goods.sku_id
    from dwh.fact_sm_goods_service_data goods
    where goods.sku_id = 200173  -- Hammers SKU
      and event_date = current_date
) hammers on wheel.user_id = hammers.user_id 
    and wheel.game_guid = hammers.parent_reward_request_id

order by rv.event_ts;