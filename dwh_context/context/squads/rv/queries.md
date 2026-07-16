# RV - SQL Queries

**Note**: This file contains actual SQL queries provided by the user for RV analysis and investigations.

## RV Wheel Rewards Connection Pattern (May 2026)

### RV to Wheel Rewards Tracing
**Purpose**: Connect RV ads to wheel-based rewards using proper relational chain
**Use Case**: Hammers, coins, gems, power-ups from wheel of fortune mechanics

```sql
-- RV Wheel Connection Chain Template
select 
    rv.user_id,
    rv.event_type,
    rv.event_ts,
    coalesce(rewards.bonus_amount, 0) as reward_amount

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

/*goods service - actual rewards*/
left join (
    select user_id, bonus_amount, parent_reward_request_id, sku_id
    from dwh.fact_sm_goods_service_data
    where sku_id = [TARGET_SKU_ID]  -- 200173 for hammers, others for different rewards
      and event_date = current_date
) rewards on wheel.user_id = rewards.user_id 
    and wheel.game_guid = rewards.parent_reward_request_id

order by rv.event_ts;
```

## Cloud Gatekeeping - Coin Value Validation (May 2026)

### Cloud RV Rewards Validation
**Purpose**: Validate coin rewards for Cloud RV events match configuration  
**Data Source**: `sm.sm_str_video_ads_history` (Cloud uses different service than Offers)
**Key Difference**: Cloud rewards don't use `transaction_id` - validated via `FEATURE_REWARDED` events

**Important Notes**:
- Cloud uses `sm.sm_str_video_ads_history` table, NOT `dwh.sm_fact_rv_client_events`
- Filter by `event_type = 'FEATURE_REWARDED'` for reward validation
- Revenue aggregation: `max(revenue) over (partition by reward_id)`
- Date conversion: `business_ts` to promo_date with Jerusalem timezone (-14h offset)

## Query Inventory

### 1. RV Gems Offer Validation
**Purpose**: Validate gems offer amounts match configuration and bonus tracking
**Tables**: `dwh.sm_fact_rv_client_events`, `dwh.fact_sm_user_bonuses`, `dwh.sm_user_profile_datamining_snapshot`
**Validation**: Check bonus_amount = gems_base_coins for gems offers

```sql
/*values check - 26.02 - Gems Offer*/

select *
--user_id, count (*)

from (select
          a.*,
          j.platform_id,
          CASE
              WHEN j.platform_id = 0 THEN 'Web - Facebook'
              WHEN j.platform_id = 3 THEN 'Web - .Com/PRAS'
              WHEN j.platform_id = 1 THEN 'iOS'
              WHEN j.platform_id = 2 THEN 'Android'
              WHEN j.platform_id = 6 THEN 'Amazon'
              WHEN j.platform_id = 8 THEN 'Win8'
              WHEN j.platform_id = 9 THEN 'Win10'
              WHEN j.platform_id = 11 THEN 'PRAS App'
              ELSE 'Other' END                              as platform,
          case when bonus_amount = gems_base_coins then 'ok' else 'wrong' end as check_gems_amount

      /*rv events table*/
      from (select
                user_id,
                event_date,
                event_ts,
                placement,
                placement_trigger,
                event_type,
                feature_additional_data,
                revenue,
                convert_from(decode(replace(replace(replace(feature_additional_data, '\\', ''), '"', '|'), 'u0027', '~'), 'base64'),
                             'UTF8') as feature_add_data_decode
            from dwh.sm_fact_rv_client_events
            where 1 = 1
              and event_date >= '2026-02-26'
              and event_date <= '2026-02-26'
              and placement = 'Shiny'
              and event_type = 'IMPRESSION'
              and placement_trigger is not null
              and feature_additional_data ~ '"offer_type":"gems"'
      ) a
               /*sessions- platform*/
               left join (select user_id,
                                 session_date,
                                 platform_id
                          from dwh.fact_sm_user_sessions
                          where session_date = '2026-02-26'
               ) j on a.user_id = j.user_id and a.event_date = j.session_date

               /*bonuses tracking*/
               left join (select
                              user_id,
                              bonus_date,
                              bonus_ts,
                              bonus_amount,
                              case
                                  when bonus_type_id = 1 then 'coins'
                                  when bonus_type_id = 12 then 'slotobucks'
                                  when bonus_type_id = 32 then 'gems'
                                  when bonus_type_id = 178 then 'powerup'
                                  when bonus_type_id = 235 then 'picks'
                                  when bonus_type_id = 295 then 'cards'
                                  else 'other' end as bonus_type_name

                          from dwh.fact_sm_user_bonuses
                          where bonus_date = '2026-02-26'
                            and bonus_type_id = 32 --gems
                            and action_id = 'RV'
               ) z on a.user_id = z.user_id and a.event_date = z.bonus_date

               /*user profile*/
               left join (select
                              user_id,
                              gems_base_coins
                          from dwh.sm_user_profile_datamining_snapshot
                          where snapshot_date = '2026-02-26'
               ) r on a.user_id = r.user_id

) T

--where check_gems_amount = 'wrong' 
--group by 1
order by event_ts;
```

### 2. RV Segmentation Logic (UPDATED MAY 2026)
**Purpose**: Classify users into expanded RV opportunistic segments with granular DPU targeting
**Tables**: `dwh.sm_user_profile`, `stg.stg_smart_seg_sm_cz_price_cut_test`
**Segments**: NPU, PUs_last_30D, DPU_30_60, DPU_60_90, DPU_90+ (5 total)

```sql
select
    user_id,
    case
        when ltv = 0 and user_level >= 300 then 'NPU'
        when ltv > 0 and user_level > 100 and days_since_last_purchase <= 30 and coalesce(cz_price_cut_test, 0) <= 15
            then 'PUs_last_30D'
        when ltv > 0 and user_level > 100 and days_since_last_purchase >= 90 and coalesce(cz_price_cut_test, 0) <= 50
            then 'DPU_90+'
        when ltv > 0 and user_level > 100 and days_since_last_purchase >= 60 and coalesce(cz_price_cut_test, 0) <= 50
            then 'DPU_60_90'
        when ltv > 0 and user_level > 100 and days_since_last_purchase >= 30 and coalesce(cz_price_cut_test, 0) <= 50
            then 'DPU_30_60'
        else null end as rv_segment_opportunistic
from (select
          a.*,
          current_date - last_transaction_date as days_since_last_purchase,
          b.cz_price_cut_test
/*user profile - level, ltv*/
      from (select
                user_id,
                case when sum_net_amount < 0 then 0 else sum_net_amount end as ltv,
                user_level,
                last_transaction_ts::date as last_transaction_date
            from dwh.sm_user_profile
            where 1 = 1) a
/*last cz value*/
               left join (select *
                          from stg.stg_smart_seg_sm_cz_price_cut_test) b
                         on a.user_id = b.user_id
      where 1 = 1) A;
```

### 3. RV Bucket Assignment Logic (UPDATED MAY 2026)
**Purpose**: Assign users to expanded config buckets with new DPU segments
**Tables**: User profile tables, segmentation data, `sm_draft.RV_opportunistic_min_eCPM_per_segment`
**Segments**: NPU (country-based), DPU segments (CZ-based with expanded ranges)

```sql
select
    user_id,
    rv_segment_opportunistic,
    country_tier,
    cz_price_cut_test,
    case 
        when rv_segment_opportunistic = 'NPU' then
            case 
                when country_tier = 'US' then 1
                when country_tier = 'Tier_1' then 2
                else 3
            end
        when rv_segment_opportunistic = 'PUs_last_30D' then
            case 
                when coalesce(cz_price_cut_test, 0) = 0 then 100
                when cz_price_cut_test >= 0.01 and cz_price_cut_test <= 4.99 then 200
                when cz_price_cut_test >= 5 and cz_price_cut_test <= 9.99 then 300
                when cz_price_cut_test >= 10 and cz_price_cut_test <= 14.99 then 400
                else 100
            end
        when rv_segment_opportunistic = 'DPU_30_60' then
            case 
                when coalesce(cz_price_cut_test, 0) = 0 then 10000
                when cz_price_cut_test >= 0.01 and cz_price_cut_test <= 4.99 then 20000
                when cz_price_cut_test >= 5 and cz_price_cut_test <= 9.99 then 30000
                when cz_price_cut_test >= 10 and cz_price_cut_test <= 14.99 then 40000
                when cz_price_cut_test >= 15 and cz_price_cut_test <= 24.99 then 50000
                when cz_price_cut_test >= 25 then 60000
                else 10000
            end
        when rv_segment_opportunistic = 'DPU_60_90' then
            case 
                when coalesce(cz_price_cut_test, 0) = 0 then 1000
                when cz_price_cut_test >= 0.01 and cz_price_cut_test <= 4.99 then 2000
                when cz_price_cut_test >= 5 and cz_price_cut_test <= 9.99 then 3000
                when cz_price_cut_test >= 10 and cz_price_cut_test <= 14.99 then 4000
                when cz_price_cut_test >= 15 and cz_price_cut_test <= 24.99 then 5000
                when cz_price_cut_test >= 25 then 6000
                else 1000
            end
        when rv_segment_opportunistic = 'DPU_90+' then
            case 
                when coalesce(cz_price_cut_test, 0) = 0 then 10
                when cz_price_cut_test >= 0.01 and cz_price_cut_test <= 4.99 then 20
                when cz_price_cut_test >= 5 and cz_price_cut_test <= 9.99 then 30
                when cz_price_cut_test >= 10 and cz_price_cut_test <= 14.99 then 40
                when cz_price_cut_test >= 15 and cz_price_cut_test <= 24.99 then 50
                when cz_price_cut_test >= 25 then 60
                else 10
            end
        else null
    end as rv_opportunistic_config_buckets
from [segmentation_and_profile_tables];
```

### 4. Dynamic eCPM Parameter Calculation (UPDATED MAY 2026)
**Purpose**: Calculate dynamic eCPM multiplier for NPU users with Control group inclusion
**Tables**: Performance tracking tables, user profile, A/B test allocations
**Test Groups**: Test_A, Test_B, Control (expanded from original Test_A/Test_B only)

```sql
select
    user_id,
    rv_segment_opportunistic,
    test_group,
    max_ad_revenue_per_day,
    min_ad_rev,
    case 
        when rv_segment_opportunistic = 'NPU' 
        and test_group in ('Test_A', 'Test_B', 'Control')
        and max_ad_revenue_per_day > 0 
        and min_ad_rev > 0 then
            greatest(0.7, max_ad_revenue_per_day / min_ad_rev)
        else 1.0
    end as RV_opportunistic_dynamic_ecpm

from (
    select 
        user_id,
        rv_segment_opportunistic,
        test_group,
        max_ad_revenue_per_day,
        min_ad_rev
    from [performance_and_test_tables]
    where calculation_date >= current_date - 2
) performance_data;
```

---

### 3. Comprehensive RV Gatekeeping - Gems Offer Validation
**Purpose**: Comprehensive validation for RV gems offers with full business context
**Tables**: `dwh.sm_fact_rv_client_events`, `kafka.kds_sm_bonus_history_new`, `dwh.fact_sm_user_offer_history_po2`, `dwh.sm_user_profile_datamining_snapshot`, `sm_ds.abtest_user_allocations`
**Test ID**: xmXDU4lG4J
**Validation**: Platform mapping, gems amount verification, RV segment validation

```sql
/*values check - 26.02 - Gems Offer - COMPREHENSIVE GATEKEEPING*/

select *
from (select
          a.*,
          j.platform_id,
          CASE
              WHEN j.platform_id = 0 THEN 'Web - Facebook'
              WHEN j.platform_id = 3 THEN 'Web - .Com/PRAS'
              WHEN j.platform_id = 1 THEN 'iOS'
              WHEN j.platform_id = 2 THEN 'Android'
              WHEN j.platform_id = 6 THEN 'Amazon'
              WHEN j.platform_id = 8 THEN 'Win8'
              WHEN j.platform_id = 9 THEN 'Win10'
              WHEN j.platform_id = 11 THEN 'PRAS App'
              ELSE 'Other'
              END                                                             AS platform,
          h.email,
          h.country_name,
          t.group_name,
          i.offer_name,
          i.opperation_template_id_name,
          b.sku_id,
          b.bonus_amount,
          c.rv_segment_opportunistic,
          c.rv_segment_to_join_config_tbl,
          c.cz_price_cut_test,
          d.new_precious_level,
          e.premium_multiplier,
          f.Tier_multiplier,
          g.gems_base_coins,
          case when bonus_amount = gems_base_coins then 'ok' else 'wrong' end as Gems_amount_check
      from (select
                user_id,
                ad_id,
                event_type,
                event_date,
                event_ts,
                transaction_id,
                user_level,
                revenue,
                placement_trigger,
                offer_id,
                session_id
            from dwh.sm_fact_rv_client_events
            where 1 = 1
              and client_type_id in (2, 3, 7, 28, 29, 36, 227, 229, 319, 431, 432, 476)
              and event_ts >= '2026-02-24 13:10:00'
              and event_type = 'AD_REWARDED') a
               join (select
                         user_id,
                         bonus_ts,
                         sku_id,
                         bonus_amount,
                         event_type,
                         skudata_tran_ticket
                     from kafka.kds_sm_bonus_history_new
                     where 1 = 1
                       and sku_id = 37
                       and bonus_date >= current_date - 1) b
                    on a.user_id = b.user_id and a.transaction_id = b.skudata_tran_ticket
               left join (select
                              user_id,
                              offer_name,
                              offer_status_ts,
                              offer_id,
                              template_id,
                              case
                                  when template_id = 221769 then 'NPU- back to lobby'
                                  when template_id = 221921 then 'NPU- ROOC'
                                  when template_id = 221777 then 'DPU- back to lobby'
                                  when template_id = 222145 then 'DPU- ROOC'
                                  when template_id = 221169 then 'internals' end as opperation_template_id_name
                          from dwh.fact_sm_user_offer_history_po2
                          where 1 = 1
                            and offer_status_ts >= current_date - 1
                            and offer_name ilike '%ad%'
                            and offer_status_id = 'IMPRESSION') i
                         on a.user_id = i.user_id and a.offer_id = i.offer_id
               left join (select
                              event_date_datamining,
                              user_id,
                              rv_segment_opportunistic,
                              case
                                  when rv_segment_opportunistic ilike '%DPU%' then 'DPU'
                                  when rv_segment_opportunistic ilike '%NPU%' then 'NPU'
                                  when rv_segment_opportunistic ilike '%PU%' then 'PU'
                                  else rv_segment_opportunistic end as rv_segment_to_join_config_tbl,
                              coalesce(cz_price_cut_test, 0)        as cz_price_cut_test,
                              tier_id_user
                          from dwh.sm_user_profile_datamining_snapshot
                          where 1 = 1
                            and event_date_datamining >= current_date) c
                         on a.user_id = c.user_id and a.event_date = c.event_date_datamining
               left join (select
                              user_id,
                              old_precious_level,
                              new_precious_level,
                              event_ts,
                              coalesce(lead(event_ts) over (partition by user_id order by event_ts),
                                       current_timestamp) as lead_event_ts
                          from dwh.sm_fact_precious_level_up) d
                         on a.user_id = d.user_id and a.event_ts between d.event_ts and lead_event_ts
               left join (select * from sm_draft.prestige_multipliers_03_12) e
                         on d.new_precious_level = e.prestige_level
               left join (select tier_id, tier_multiplier from dwh.Dim_Coins_Value where platform = 'Web' group by 1, 2) f
                         on c.tier_id_user = f.tier_id
               left join (select * from sm_draft.RV_gems_config_26_02) g
                         on c.rv_segment_to_join_config_tbl = g.rv_segment
                             and c.cz_price_cut_test between g.config_cz_from and g.config_cz_to
                             and a.revenue between g.ad_rev_from and g.ad_rev_to
               left join (select distinct
                              a.user_id as t_user_id,
                              group_name
                          from sm_ds.abtest_user_allocations a
                                   left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
                                   left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                          where test_id = 'xmXDU4lG4J') t
                         on a.user_id = t.t_user_id
               left join (select user_id, email, country_name from dwh.sm_user_profile) h
                         on a.user_id = h.user_id
               left join (select user_id, session_id, platform_id from dwh.fact_sm_sessions_kafka 
                          where session_creation_date >= current_date - 1 group by 1, 2, 3) j
                         on a.user_id = j.user_id and a.session_id = j.session_id) A
```

### 4. Shiny Show Floor & Daily Limits Validation
**Purpose**: Validate Shiny Show trigger floor constraints and daily impression limits
**Tables**: `dwh.sm_fact_rv_client_events`, `sm_ds.abtest_user_allocations`
**Test ID**: xmXDU4lG4J
**Gatekeeping**: Bomb_pick floors 6-12, Extra_pick floor 10 only, max floors 12, daily limits

```sql
/*Checking that Only test groups receive ads & checking Shiny Floors - per trigger (Mole - 6-12, extra pick - 10 only, MAX FLOOR- 12) */

select *,
       case
           when placement_trigger = 'bomb_pick' and Shiny_Show_floor in (6, 7, 8, 9, 10, 11, 12) then 'ok'
           when placement_trigger = 'wait_buy_extra_pick' and Shiny_Show_floor = 10 then 'ok'
           else 'wrong' end                                                    as floor_per_trigger_check,
       case when Shiny_Show_floor > 12 then 'wrong' else 'ok' end              as floor_limit_check,
       case when group_name in ('Test_A', 'Test_B') then 'ok' else 'wrong' end as test_groups_check
from (select
          user_id,
          event_ts,
          event_date,
          ad_id,
          revenue,
          event_type,
          placement,
          placement_trigger,
          feature_additional_data,
          REGEXP_SUBSTR(feature_additional_data, '\"level\"\\s*:\\s*([0-9]+)', 1, 1, '', 1)::INT + 1 as Shiny_Show_floor
      from dwh.sm_fact_rv_client_events
      where 1 = 1
        and user_id not in (select distinct user_id from dwh.playtika_users)
        and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
        and placement ilike '%shiny%'
        and event_type = 'AD_IMPRESSION'
        and event_ts >= '2026-04-16 11:00:00') A
         left join (select distinct
                        a.user_id as t_user_id,
                        group_name
                    from sm_ds.abtest_user_allocations a
                             left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
                             left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                    where test_id = 'xmXDU4lG4J') t
                   on a.user_id = t.t_user_id
```

### 5. Dynamic eCPM Threshold Validation
**Purpose**: Validate DPU users meet dynamic eCPM thresholds based on segments and parameters
**Tables**: `dwh.sm_fact_rv_client_events`, `dwh.sm_user_profile_datamining_snapshot`, `sm_draft.RV_opportunistic_min_eCPM_per_segment`
**Test ID**: xmXDU4lG4J
**Gatekeeping**: Revenue >= min_ad_rev * RV_opportunistic_dynamic_ecpm

```sql
/*DPUs- eCPM reduce 19.05 Promo date- all events and not just per user*/ 

select
    a.*,
    b.*,
    g.*,
    group_name,
    h.previous_min_ad_rev_DPU,
    up.country_name,
    RV_opportunistic_dynamic_ecpm,
    min_ad_rev * coalesce(RV_opportunistic_dynamic_ecpm, 1) AS min_ad_rev_with_param,
    case
        when revenue >= min_ad_rev * coalesce(RV_opportunistic_dynamic_ecpm, 1) then 'ok'
        else 'wrong' end as min_eCPM_check,
    revenue / (min_ad_rev * coalesce(RV_opportunistic_dynamic_ecpm, 1)) as ratio
from (select
          user_id,
          date(event_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '13 hours') as promo_date,
          event_date,
          placement_trigger,
          revenue
      from dwh.sm_fact_rv_client_events
      where 1 = 1
        and user_id not in (select distinct user_id from dwh.playtika_users)
        and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
        and event_ts >= '2026-05-19 15:30:00'
        and event_type = 'AD_DISPLAYED') a
         left join (select
                        a.user_id as t_user_id,
                        group_name
                    from sm_ds.abtest_user_allocations a
                             left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
                             left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                    where test_id = 'xmXDU4lG4J') t
                   on a.user_id = t.t_user_id
         left join (select
                        event_date_datamining,
                        user_id,
                        rv_segment_opportunistic,
                        coalesce(cz_price_cut_test, 0) as cz_price_cut_test,
                        rv_opportunistic_config_buckets,
                        RV_opportunistic_dynamic_ecpm
                    from dwh.sm_user_profile_datamining_snapshot
                    where event_date_datamining = current_date - 1) b
                   on a.user_id = b.user_id
         left join (select * from sm_draft.RV_opportunistic_min_eCPM_per_segment) g
                   on b.rv_opportunistic_config_buckets = g.parameter_value
                       and a.promo_date >= g.config_promo_date_from
                       and a.promo_date < g.config_promo_date_to
         left join (select
                        parameter_value,
                        min_ad_rev as previous_min_ad_rev_DPU
                    from sm_draft.RV_opportunistic_min_eCPM_per_segment
                    where config_promo_date_to = '2026-05-19'::date) h
                   on b.rv_opportunistic_config_buckets = h.parameter_value
         left join (select user_id as up_user_id, country_name from dwh.sm_user_profile) up
                   on a.user_id = up.up_user_id
```

---

---

## Parameter Documentation (Updated May 2026)

**IMPORTANT**: Complete parameter documentation now available in dedicated `parameters/` folder:

### Core Parameter Files
- **`parameters/rv-parameters-overview.md`** - Current system architecture and configuration
- **`parameters/rv-parameters-changes.md`** - Change history and validation data  
- **`parameters/rv-parameters-queries.sql`** - Full SQL repository with version control

### Legacy Reference Files  
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `general-rv.md` - Complete RV business context

**Note**: For complete parameter queries including full joins, complex logic, and production versions, refer to `parameters/rv-parameters-queries.sql`. The queries above show simplified logic patterns.