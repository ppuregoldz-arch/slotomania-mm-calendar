# Prize Mania - Queries

**Note**: This file contains only queries provided by the user, not queries created during conversations.

## Query Inventory

### 1. Price and SlotoBucks Amount Validation
**Purpose**: Validate Prize Mania pricing configuration and SlotoBucks bonus amounts  
**Category**: Gatekeeping / Configuration Validation  
**Business Rule**: Ensure pricing matches configuration and SlotoBucks amounts are correctly awarded

```sql
/*price check & SB amount check*/ 

select *,
       case when round(config_price) = round(gross_amount) then 'ok' else 'wrong' end as price_check,
       case when round(gross_amount) = round(bonus_amount) then 'ok' else 'wrong' end as SB_check
/*prize mania data*/
from (select
          user_id,
          event_ts,
          event_date,
          status,
          reward_id,
          mission_id,
          schedule_id,
          origin_transaction_id
      from kafka.src_sm_prize_mania
      where 1 = 1
--         and user_id = 154000066502254
        and event_ts >= '2026-03-24 11:00:00'
--         and status = 'FINISHED' -- collected
        and status = 'FINISHED_UNCOLLECTED' -- purchased without collecting prizes
      order by event_ts) A

         /*bonuses- kafka - SB*/
         join (select
                   user_id as b_user_id,
                   parent_reward_request_id,
                   a.sku_id,
                   sku_name,
                   bonus_amount,
                   tier_id
               from kafka.kds_sm_bonus_history_new a
                        left join dwh.dim_sku_type b
                                  on a.sku_id = b.sku_id
               where 1 = 1
                 --                       and user_id = 154000066502254
                 and a.sku_id = 200031
                 and event_date = current_date) B
              on a.user_id = b.b_user_id and a.reward_id = b.parent_reward_request_id


/*payments*/
         left join (SELECT
                        Product_Name,
                        gross_amount,
                        tran_id,
                        user_id
                    from dwh.sm_fact_all_payments a
                             left join sm_draft.SM_DIM_Products b
                                       on a.sku_id = b.sku_id and
                                          a.transaction_source_type_id = b.transaction_source_type_id
                    where 1 = 1
                      and tran_status_id = 2
                      and artificial_ind = 0
                      and is_test = 0
                      and user_id > 0
                      and tran_date = current_date) c
                   on a.user_id = c.user_id and a.origin_transaction_id = c.tran_id
/*datamining- cz*/
         left join (select
                        event_date_datamining,
                        user_id                        as d_user_id,
                        coalesce(cz_price_cut_test, 0) as cz_price_cut_test
                    from dwh.sm_user_profile_datamining_snapshot
                    where 1 = 1
                      and event_date_datamining >= current_date - 1) d
                   on a.user_id = d.d_user_id and a.event_date = d.event_date_datamining
/*pricing table*/
         left join (select
                        cz_from,
                        cz_to,
                        pricing_level,
                        price as config_price
                    from sm_draft.pricing_level_prices_base_coins_base_gems
                    where 1 = 1
                      and pricing_level = 'High') e
                   on d.cz_price_cut_test between e.cz_from and e.cz_to;
```

### 2. SKU Type Per Mission Validation
**Purpose**: Validate that each Prize Mania mission awards the correct SKU types  
**Category**: Gatekeeping / Mission Rewards Validation  
**Business Rules**: 
- Mission 1: Coins (0) or RDS (238)
- Mission 2: Dice (35) or RDS (238) 
- Mission 3: Gems (37) or Gems stamp (200179)
- Mission 4: Air strike/BattleSheep (200240) or RDS (238)
- Mission 5: Card (43)
- Mission 6: Coins (0), Gems (37), or SlotoBucks (200031)

```sql
----- ============================================ Skus per mission check  ============================================

/*Skus type per mission*/
select *,
       case
           when mission_id = 1 and sku_id in (0, 238) then 'ok' --  Coins / RDS
           when mission_id = 2 and sku_id in (35, 238) then 'ok' --  Dice / RDS
           when mission_id = 3 and sku_id in (37, 200179) then 'ok' --  Gems / Gems stamp
           when mission_id = 4 and sku_id in (200240, 238) then 'ok' --  Air strike- battleSheep / RDS
           when mission_id = 5 and sku_id in (43) then 'ok' --  Card
           when mission_id = 6 and sku_id in (0, 37, 200031) then 'ok' --  Coins / Gems / SB
           else 'wrong' end as Skus_type_per_mission_check
/*prize mania data*/
from (select
          user_id,
          event_ts,
          status,
          reward_id,
          mission_id,
          schedule_id
      from kafka.src_sm_prize_mania
      where 1 = 1
--         and user_id = 154000066502254
        and event_ts >= '2026-03-24 11:00:00'
        and status = 'FINISHED' -- collected
      order by event_ts) A
/*bonuses- kafka*/
         join (select
                   user_id as b_user_id,
                   parent_reward_request_id,
                   a.sku_id,
                   sku_name,
                   bonus_amount
               from kafka.kds_sm_bonus_history_new a
                        left join dwh.dim_sku_type b
                                  on a.sku_id = b.sku_id
               where 1 = 1
--                       and user_id = 154000066502254
                 and event_date = current_date) B
              on a.user_id = b.b_user_id and a.reward_id = b.parent_reward_request_id;
```

### 3. MGAP Multiplier Validation
**Purpose**: Validate MGAP coin calculations are based on correct base amounts and multipliers  
**Category**: Gatekeeping / MGAP Integration  
**Business Rule**: MGAP coins = base_coins × prestige_multiplier × tier_multiplier × 1.3 × final_win_multiplier

```sql
/*MGAP check - is multiply the correct base coins*/
select
    a.MGAP_final_win_multiplier,
    b.tier_id,
    d.new_precious_level,
    b.source_product_name,
    c.MGAP_gross_amount,
    c.MGAP_payment_quantity,
    r.base_coins,
    e.prestige_multiplier,
    f.Tier_multiplier,
    r.base_coins * e.prestige_multiplier * f.Tier_multiplier * 1.3                                 as MGAP_base_coins_config,
    (r.base_coins * e.prestige_multiplier * f.Tier_multiplier * 1.3) * MGAP_final_win_multiplier   as config_MGAP_coins,
    MGAP_payment_quantity /
    ((r.base_coins * e.prestige_multiplier * f.Tier_multiplier * 1.3) * MGAP_final_win_multiplier) as ratio

/*MGAP tbl*/
from (select
          event_date,
          user_id,
          game_type           as MGAP_type,
          transaction_id,
          orig_transaction_id as MGAP_source_tran_id,
          max(win_multiplier) as MGAP_final_win_multiplier,
          max(event_ts)       as MGAP_event_ts
      from dwh.sm_fact_mgap_bonus_game_history
      where 1 = 1
        and event_ts >= '2026-03-24 11:00:00'
        and game_type = 'fire'
      group by 1, 2, 3, 4, 5) A
/*payments - prize mania only*/
         join (SELECT
                   user_id,
                   tran_id,
                   product_name as source_product_name,
                   tier_id
               from dwh.sm_fact_all_payments a
                        left join sm_draft.SM_DIM_Products b
                                  on a.sku_id = b.sku_id and a.transaction_source_type_id = b.transaction_source_type_id
               where 1 = 1
                 and tran_status_id = 2
                 and artificial_ind = 0
                 and is_test = 0
                 and user_id > 0
                 and Product_Name ilike '%mania%'
                 and tran_date >= current_date) b
              on a.user_id = b.user_id and a.MGAP_source_tran_id = b.tran_id
/*payments - MGAP*/
         left join (SELECT
                        user_id,
                        tran_id,
                        product_name,
                        payment_quantity as MGAP_payment_quantity,
                        gross_amount     as MGAP_gross_amount
                    from dwh.sm_fact_all_payments a
                             left join sm_draft.SM_DIM_Products b
                                       on a.sku_id = b.sku_id and
                                          a.transaction_source_type_id = b.transaction_source_type_id
                    where 1 = 1
                      and tran_status_id = 2
                      and artificial_ind = 0
                      and is_test = 0
                      and user_id > 0
                      and Product_Name ilike '%mgap%'
                      and tran_date = current_date) c
                   on a.user_id = c.user_id and a.transaction_id = c.tran_id
/*base coins*/
         left join (select *
                    from sm_draft.pricing_level_prices_base_coins_base_gems
                    where 1 = 1
                      and pricing_level = 'High') r
                   on round(MGAP_gross_amount) = round(r.price)
/*prestige level*/
         left join (select
                        user_id,
                        old_precious_level,
                        new_precious_level,
                        event_ts,
                        event_source,
                        coalesce(lead(event_ts) over (partition by user_id order by event_ts),
                                 current_timestamp) as lead_event_ts
                    from dwh.sm_fact_precious_level_up
                    where 1 = 1) d
                   on a.user_id = d.user_id and a.MGAP_event_ts between d.event_ts and d.lead_event_ts
/*prestige level multipliers*/
         left join (select *,
                           premium_multiplier as prestige_multiplier
                    from sm_draft.new_premium_multipliers_12_01) e
                   on d.new_precious_level = e.p_level
/*tier multiplier*/
         left join (select distinct
                        tier_id,
                        tier_multiplier
                    from dwh.Dim_Coins_Value) f
                   on b.tier_id = f.tier_id;
```

### 4. Coins Reward Validation
**Purpose**: Validate coin amounts awarded for different missions  
**Category**: Gatekeeping / Reward Calculation  
**Business Rules**: Mission 1 = 30% of base coins, Mission 6 = 100% of base coins

```sql
/*values check - Coins*/
select *,
       case when config_coins_per_mission = bonus_amount then 'ok' else 'wrong' end as coins_check,
       bonus_amount / config_coins_per_mission                                      as ratio
from (select
          a.*,
          b.bonus_amount,
          c.gross_amount,
          d.new_precious_level,
          e.premium_multiplier,
          b.tier_id,
          f.Tier_multiplier,
          r.base_coins,
          r.base_coins * Tier_multiplier * prestige_multiplier                    as price_coins_config,
          case
              when mission_id = 1 then (r.base_coins * Tier_multiplier * prestige_multiplier) * 0.3
              when mission_id = 6
                  then (r.base_coins * Tier_multiplier * prestige_multiplier) end as config_coins_per_mission
/*prize mania data*/
      from (select
                user_id,
                event_ts,
                status,
                reward_id,
                mission_id,
                schedule_id,
                origin_transaction_id
            from kafka.src_sm_prize_mania
            where 1 = 1
              and event_ts >= '2026-03-24 11:00:00'
              and status = 'FINISHED' -- collected
            order by event_ts) A
/*bonuses- kafka - Coins Only*/
               join (select
                         user_id as b_user_id,
                         parent_reward_request_id,
                         a.sku_id,
                         sku_name,
                         bonus_amount,
                         tier_id
                     from kafka.kds_sm_bonus_history_new a
                              left join dwh.dim_sku_type b
                                        on a.sku_id = b.sku_id
                     where 1 = 1
                       and a.sku_id = 0
                       and event_date = current_date) B
                    on a.user_id = b.b_user_id and a.reward_id = b.parent_reward_request_id
/*payments tbl*/
               left join (SELECT
                              user_id,
                              product_name,
                              gross_amount,
                              tran_id
--              price
                          from dwh.sm_fact_all_payments a
                                   left join sm_draft.SM_DIM_Products b
                                             on a.sku_id = b.sku_id and
                                                a.transaction_source_type_id = b.transaction_source_type_id
                          where 1 = 1
                            and tran_status_id = 2
                            and artificial_ind = 0
                            and is_test = 0
                            and user_id > 0
                            and tran_date = current_date) c
                         on a.user_id = c.user_id and a.origin_transaction_id = c.tran_id
/*prestige level*/
               left join (select
                              user_id,
                              old_precious_level,
                              new_precious_level,
                              event_ts,
                              event_source,
                              coalesce(lead(event_ts) over (partition by user_id order by event_ts),
                                       current_timestamp) as lead_event_ts
                          from dwh.sm_fact_precious_level_up
                          where 1 = 1) d
                         on a.user_id = d.user_id and a.event_ts between d.event_ts and d.lead_event_ts
/*prestige level multipliers*/
               left join (select *,
                                 premium_multiplier as prestige_multiplier
                          from sm_draft.new_premium_multipliers_12_01) e
                         on d.new_precious_level = e.p_level
/*tier multiplier*/
               left join (select distinct
                              tier_id,
                              tier_multiplier
                          from dwh.Dim_Coins_Value) f
                         on b.tier_id = f.tier_id
/*base coins*/
               left join (select *
                          from sm_draft.pricing_level_prices_base_coins_base_gems
                          where 1 = 1
                            and pricing_level = 'High') r
                         on round(gross_amount) = round(r.price)) A;
```

### 5. Gems Reward Validation
**Purpose**: Validate gem amounts awarded (50% of base gems configuration)  
**Category**: Gatekeeping / Reward Calculation  
**Business Rule**: Gems rewards = base_gems × 0.5

```sql
/*values check - Gems*/
select
    a.*,
    b.bonus_amount,
    c.gross_amount,
    d.base_gems                                                                                 as config_gems_amount_offers,
    case when bonus_amount = (d.base_gems * 0.5) then 'ok' else 'wrong' end                     as gems_check,
    bonus_amount / (base_gems * 0.5)                                                            as ratio,
    case when (bonus_amount / (base_gems * 0.5)) between 0.9 and 1.1 then 'ok' else 'wrong' end as ratio_check

/*prize mania data*/
from (select
          user_id,
          event_ts,
          status,
          reward_id,
          mission_id,
          schedule_id,
          origin_transaction_id
      from kafka.src_sm_prize_mania
      where 1 = 1
        and event_ts >= '2026-03-24 11:00:00'
        and status = 'FINISHED' -- collected
      order by event_ts) A
/*bonuses- kafka - Coins Only*/
         join (select
                   user_id as b_user_id,
                   parent_reward_request_id,
                   a.sku_id,
                   sku_name,
                   bonus_amount,
                   tier_id
               from kafka.kds_sm_bonus_history_new a
                        left join dwh.dim_sku_type b
                                  on a.sku_id = b.sku_id
               where 1 = 1
--                       and user_id = 154000066502254
                 and a.sku_id = 37
                 and event_date = current_date) B
              on a.user_id = b.b_user_id and a.reward_id = b.parent_reward_request_id
/*payments tbl*/
         left join (SELECT
                        user_id,
                        product_name,
                        gross_amount,
                        tran_id
--              price
                    from dwh.sm_fact_all_payments a
                             left join sm_draft.SM_DIM_Products b
                                       on a.sku_id = b.sku_id and
                                          a.transaction_source_type_id = b.transaction_source_type_id
                    where 1 = 1
                      and tran_status_id = 2
                      and artificial_ind = 0
                      and is_test = 0
                      and user_id > 0
                      and tran_date >= current_date) c
                   on a.user_id = c.user_id and a.origin_transaction_id = c.tran_id
/*base coins & pricing*/
         left join (select *
                    from sm_draft.pricing_level_prices_base_coins_base_gems
                    where 1 = 1
                      and pricing_level = 'High') d
                   on round(c.gross_amount) = round(d.price);
```

### 6. Card Type Validation
**Purpose**: Validate collectible card rewards are correct type and rarity  
**Category**: Gatekeeping / Card Rewards  
**Business Rule**: Cards should be type 1 (gold) and rarity 4 (stars)

```sql
/*values check - cards type*/
select *,
       case when card_type = 1 and rareness = 4 then 'ok' else 'wrong' end as card_type_check
from (select
          user_id,
          event_ts,
          status,
          reward_id,
          mission_id,
          schedule_id
      from kafka.src_sm_prize_mania
      where 1 = 1
--         and user_id = 154000066502254
        and event_ts >= '2026-03-24 11:00:00'
        and status = 'FINISHED' -- collected
      order by event_ts) A
/*bonuses- kafka*/
         join (select
                   user_id as b_user_id,
                   parent_reward_request_id,
                   a.sku_id,
                   sku_name,
                   bonus_amount,
                   reward_request_id
               from kafka.kds_sm_bonus_history_new a
                        left join dwh.dim_sku_type b
                                  on a.sku_id = b.sku_id
               where 1 = 1
                 and a.sku_id = 43
--                       and user_id = 154000066502254
                 and event_date = current_date) B
              on a.user_id = b.b_user_id and a.reward_id = b.parent_reward_request_id
/*collectibles table- card type & stars*/
         left join (select
                        a.*,
                        trigger_type_name
                    from (select
                              event_date,
                              created_ts,
                              card_type, -- Type: 0 regular , 1 gold , 2 ace
                              rareness,  -- stars
                              user_id,
                              trigger_type_id,
                              request_id
                          from dwh.sm_fact_collectibles_cards
                          where event_date >= current_date) A
                             left join (select *
                                        from dwh.sm_dim_collectibles_triggers
                                        where 1 = 1) b
                                       on a.trigger_type_id = b.trigger_type_id) c
                   on a.user_id = c.user_id and b.reward_request_id = c.request_id;
```

### 7. Air Strike Validation
**Purpose**: Validate Air Strike rewards (BattleSheep power-up)  
**Category**: Gatekeeping / Power-up Rewards  
**Business Rule**: Air Strike rewards should be exactly 1 unit

```sql
/*values check - Air_strike*/
select *,
       case when bonus_amount = 1 then 'ok' else 'wrong' end as Air_strike_check
/*prize mania data*/
from (select
          user_id,
          event_ts,
          status,
          reward_id,
          mission_id,
          schedule_id
      from kafka.src_sm_prize_mania
      where 1 = 1
--         and user_id = 154000066502254
        and event_ts >= '2026-03-24 11:00:00'
        and status = 'FINISHED' -- collected
      order by event_ts) A
/*bonuses- kafka*/
         join (select
                   user_id as b_user_id,
                   parent_reward_request_id,
                   a.sku_id,
                   sku_name,
                   bonus_amount
               from kafka.kds_sm_bonus_history_new a
                        left join dwh.dim_sku_type b
                                  on a.sku_id = b.sku_id
               where 1 = 1
                 and a.sku_id = 200240
                 and event_date = current_date) B
              on a.user_id = b.b_user_id and a.reward_id = b.parent_reward_request_id;
```

### 8. Stamp Amount Validation
**Purpose**: Validate correct stamp amounts awarded per mission  
**Category**: Gatekeeping / Stamp Card Integration  
**Business Rules**: 
- Mission 1 RDS: 2 stamps
- Mission 2 RDS: 1 stamp  
- Mission 3 Gems stamp: 1 stamp
- Mission 4 RDS: 1 stamp

```sql
/*value check - Stamps amount received*/
select
    stamps_amount_check,
    count(distinct user_id) as users,
    count(*)                as events
from (select *,
             case
                 when mission_id = 1 and sku_id = 238 and stamps_amount = 2 then 'ok' -- RDS
                 when mission_id = 2 and sku_id = 238 and stamps_amount = 1 then 'ok' -- RDS
                 when mission_id = 3 and sku_id = 200179 and stamps_amount = 1 then 'ok' -- Gems
                 when mission_id = 4 and sku_id = 238 and stamps_amount = 1 then 'ok' -- rds
                 else 'wrong' end as stamps_amount_check
/*prize mania data*/
      from (select
                user_id,
                event_ts,
                status,
                reward_id,
                mission_id,
                schedule_id,
                origin_transaction_id
            from kafka.src_sm_prize_mania
            where 1 = 1
--               and user_id = 151325322934991
              and event_ts >= '2026-03-24 17:15:00'
              and status = 'FINISHED' -- collected
            order by event_ts) A
/*bonuses- kafka - stamps*/
               join (select
                         user_id as b_user_id,
                         parent_reward_request_id,
                         reward_request_id,
                         a.sku_id,
                         sku_name,
                         bonus_amount,
                         tier_id
                     from kafka.kds_sm_bonus_history_new a
                              left join dwh.dim_sku_type b
                                        on a.sku_id = b.sku_id
                     where 1 = 1
--                        and user_id = 154000026368610
--                        and user_id = 151325322934991
                       and a.sku_id in (238, 200179)
                       and event_date = current_date) B
                    on a.user_id = b.b_user_id and a.reward_id = b.parent_reward_request_id
/*stamp tbl - stamp amount*/
               join (select
                         user_id  as c_user_id,
                         source_id,
                         current_stamp_type,
                         count(*) as stamps_amount
                     from dwh.sm_fact_stamp_card
                     where 1 = 1
                     group by 1, 2, 3) c
                    on a.user_id = c.c_user_id and b.reward_request_id = c.source_id) A
group by 1;
```

### 9. Mission Goal Target Validation
**Purpose**: Validate mission goal targets match player spinner bucket segments  
**Category**: Gatekeeping / Difficulty Scaling  
**Business Rules**: Goal targets scale by spinner bucket (Low/Med/High) and mission progression

```sql
/*with last value parameter value*/ 
select
    demand_check,
    count(*)                as events,
    count(distinct user_id) as distinct_users
from (select *,
             case
                 when mission_id = 1 and goal_target = 1 then 'ok'
                 when spinners_bucket = 'Low' and mission_id = 2 and goal_target = 10 then 'ok'
                 when spinners_bucket = 'Low' and mission_id = 3 and goal_target = 20 then 'ok'
                 when spinners_bucket = 'Low' and mission_id = 4 and goal_target = 40 then 'ok'
                 when spinners_bucket = 'Low' and mission_id = 5 and goal_target = 70 then 'ok'
                 when spinners_bucket = 'Low' and mission_id = 6 and goal_target = 100 then 'ok'
                 when spinners_bucket = 'Med' and mission_id = 2 and goal_target = 20 then 'ok'
                 when spinners_bucket = 'Med' and mission_id = 3 and goal_target = 40 then 'ok'
                 when spinners_bucket = 'Med' and mission_id = 4 and goal_target = 70 then 'ok'
                 when spinners_bucket = 'Med' and mission_id = 5 and goal_target = 100 then 'ok'
                 when spinners_bucket = 'Med' and mission_id = 6 and goal_target = 140 then 'ok'
                 when spinners_bucket = 'High' and mission_id = 2 and goal_target = 30 then 'ok'
                 when spinners_bucket = 'High' and mission_id = 3 and goal_target = 50 then 'ok'
                 when spinners_bucket = 'High' and mission_id = 4 and goal_target = 100 then 'ok'
                 when spinners_bucket = 'High' and mission_id = 5 and goal_target = 150 then 'ok'
                 when spinners_bucket = 'High' and mission_id = 6 and goal_target = 200 then 'ok'
                 else 'wrong' end as demand_check
/*prize mania data*/
      from (select
                user_id,
                event_ts,
                event_date,
                status,
                mission_id,
                schedule_id,
                goal_target
            from kafka.src_sm_prize_mania
            where 1 = 1
--         and user_id = 154000066502254
              and event_ts >= '2026-03-24 11:00:00'
              and status = 'STARTED'
            order by event_ts) a
/* datamining-spins bucket*/
               left join (select
                              event_date_datamining,
                              user_id                               as b_user_id,
                              simple_median_spins,
                              LAST_VALUE(simple_median_spins IGNORE NULLS)
                              OVER (
                                  PARTITION BY user_id
                                  ORDER BY event_date_datamining
                                  )                                 as last_value_sms,
--                         coalesce(simple_median_spins, 0)                                 as simple_median_spins,
                              case
                                  when LAST_VALUE(simple_median_spins IGNORE NULLS)
                                       OVER (
                                           PARTITION BY user_id
                                           ORDER BY event_date_datamining
                                           ) < 200 then 'Low'
                                  when LAST_VALUE(simple_median_spins IGNORE NULLS)
                                       OVER (
                                           PARTITION BY user_id
                                           ORDER BY event_date_datamining
                                           ) < 500 then 'Med'
                                  when LAST_VALUE(simple_median_spins IGNORE NULLS)
                                       OVER (
                                           PARTITION BY user_id
                                           ORDER BY event_date_datamining
                                           ) >= 500 then 'High' end as spinners_bucket
                          from dwh.sm_user_profile_datamining_snapshot
                          where 1 = 1
--                       and user_id=151325281593732
                            and event_date_datamining >= current_date - 180
--                           limit 1 over (partition by user_id order by event_date_datamining desc)
                          ) b
                         on a.user_id = b.b_user_id and a.event_date = b.event_date_datamining
/*user profile*/
               left join (select
                              user_id as c_user_id,
                              country_name
                          from dwh.sm_user_profile) c
                         on a.user_id = c.c_user_id
      where 1 = 1
--         and simple_median_spins is not null
      ) A
group by 1;
```

## Key Gatekeeping Validations

### **Mission Structure**
- **Mission 1**: Purchase completion (goal_target = 1)
- **Missions 2-6**: Gameplay objectives scaled by spinner bucket (Low < 200, Med 200-499, High ≥500)

### **Reward Types & Business Rules**
1. **Coins**: Mission 1 (30% of base), Mission 6 (100% of base)
2. **Gems**: 50% of base gems configuration  
3. **Cards**: Type 1 (gold), Rarity 4 (4 stars)
4. **Air Strike**: Exactly 1 unit
5. **Stamps**: RDS (1-2 stamps), Gems stamp (1 stamp)
6. **SlotoBucks**: Equal to gross payment amount
7. **MGAP Integration**: Fire MGAP with 1.3x base multiplier

### **Key Tables Used**
- `kafka.src_sm_prize_mania` - Prize Mania events and mission data
- `kafka.kds_sm_bonus_history_new` - Reward distribution events
- `dwh.sm_fact_all_payments` - Purchase transactions
- `dwh.sm_fact_mgap_bonus_game_history` - MGAP integration
- `dwh.sm_fact_collectibles_cards` - Card reward details
- `dwh.sm_fact_stamp_card` - Stamp card progression
- `dwh.sm_user_profile_datamining_snapshot` - User segmentation (CZ, spinner buckets)

---
**Source**: User-provided Prize Mania gatekeeping queries for comprehensive feature validation and reward accuracy monitoring.