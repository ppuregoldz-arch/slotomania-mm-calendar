/*
DPU 60-90 Gatekeeping Query 3a: Offers Coin Value Configuration Check
=====================================================================
Purpose: Validate coin rewards match configuration for DPU_60_90 users (OFFERS ONLY)
Data Source: dwh.sm_fact_rv_client_events + bonus tracking (transaction-based)
Expected: bonus_amount matches config calculation for offer-based rewards
Note: For Cloud rewards, use separate query 3b (different data source)
*/

select 
    a.user_id,
    a.event_date,
    a.event_ts,
    a.placement,
    a.placement_trigger,
    a.revenue,
    a.transaction_id,
    
    -- Platform information
    j.platform_id,
    case
        when j.platform_id = 0 then 'Web - Facebook'
        when j.platform_id = 3 then 'Web - .Com/PRAS'
        when j.platform_id = 1 then 'iOS'
        when j.platform_id = 2 then 'Android'
        when j.platform_id = 6 then 'Amazon'
        when j.platform_id = 8 then 'Win8'
        when j.platform_id = 9 then 'Win10'
        when j.platform_id = 11 then 'PRAS App'
        else 'Other'
    end as platform,
    
    -- User profile and segmentation
    up.email,
    up.country_name,
    b.rv_segment_opportunistic,
    b.rv_opportunistic_config_buckets,
    c.cz_price_cut_test,
    t.group_name as test_group,
    
    -- Bonus tracking
    bonus.sku_id,
    bonus.bonus_amount as actual_bonus_amount,
    bonus.bonus_type_name,
    
    -- Prestige and tier multipliers  
    pres.new_precious_level,
    mult.premium_multiplier,
    tier.tier_multiplier,
    
    -- Configuration-based coin calculation
    config.min_ecpm as config_min_ecpm,
    config.min_ad_rev as config_min_ad_rev,
    
    -- Expected coin calculation (simplified - needs actual config table)
    case 
        when bonus.sku_id = 1 then  -- Coins
            case
                when b.rv_opportunistic_config_buckets = 1000 and a.revenue >= 0.04 then 708750
                when b.rv_opportunistic_config_buckets = 2000 and a.revenue >= 0.08 then 1417500
                when b.rv_opportunistic_config_buckets = 3000 and a.revenue >= 0.15 then 3262500
                when b.rv_opportunistic_config_buckets = 4000 and a.revenue >= 0.20 then 4350000
                when b.rv_opportunistic_config_buckets = 5000 and a.revenue >= 0.30 then 6525000
                when b.rv_opportunistic_config_buckets = 6000 and a.revenue >= 0.40 then 8700000
                else null
            end
        when bonus.sku_id = 32 then -- Gems
            case
                when b.rv_opportunistic_config_buckets between 1000 and 6000 then 30  -- Standard gems amount for DPU_60_90
                else null
            end
        when bonus.sku_id = 200239 then 2  -- Power-ups (typically 2)
        when bonus.sku_id = 200150 then 2  -- Picks (typically 2)
        else null
    end as expected_bonus_amount,
    
    -- Validation results
    case 
        when bonus.bonus_amount is null then 'wrong'
        when bonus.sku_id = 1 and  -- Coins validation
             bonus.bonus_amount = (
                case
                    when b.rv_opportunistic_config_buckets = 1000 and a.revenue >= 0.04 then 708750
                    when b.rv_opportunistic_config_buckets = 2000 and a.revenue >= 0.08 then 1417500
                    when b.rv_opportunistic_config_buckets = 3000 and a.revenue >= 0.15 then 3262500
                    when b.rv_opportunistic_config_buckets = 4000 and a.revenue >= 0.20 then 4350000
                    when b.rv_opportunistic_config_buckets = 5000 and a.revenue >= 0.30 then 6525000
                    when b.rv_opportunistic_config_buckets = 6000 and a.revenue >= 0.40 then 8700000
                    else null
                end
             ) then 'ok'
        when bonus.sku_id = 32 and bonus.bonus_amount = 30 then 'ok'
        when bonus.sku_id = 200239 and bonus.bonus_amount = 2 then 'ok'
        when bonus.sku_id = 200150 and bonus.bonus_amount = 2 then 'ok'
        else 'wrong'
    end as bonus_validation,
    
    case 
        when b.rv_segment_opportunistic != 'DPU_60_90' then 'wrong'
        when t.group_name not in ('Test_A', 'Test_B', 'Control') then 'wrong'  
        when b.rv_opportunistic_config_buckets not between 1000 and 6000 then 'wrong'
        else 'ok'
    end as profile_validation

from (
    -- RV events for completed ads
    select
        user_id,
        event_date,
        event_ts,
        placement,
        placement_trigger,
        revenue,
        transaction_id,
        session_id,
        date(event_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '13 hours') as promo_date
    from dwh.sm_fact_rv_client_events
    where 1 = 1
      and user_id not in (select distinct user_id from dwh.playtika_users)
      and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
      and event_type = 'AD_REWARDED'
      and event_date = current_date  -- Today only (run on launch day)
      and transaction_id is not null  -- Offers require completed transactions (not applicable for Cloud)
) a

-- User segmentation (DPU_60_90 only)
join (
    select
        user_id,
        rv_segment_opportunistic,
        rv_opportunistic_config_buckets
    from dwh.sm_user_profile_datamining_snapshot
    where event_date_datamining = current_date
      and rv_segment_opportunistic = 'DPU_60_90'
) b on a.user_id = b.user_id

-- CZ data from datamining table
left join (
    select user_id, cz_price_cut_test
    from dwh.sm_user_profile_datamining_snapshot
    where event_date_datamining = current_date
) c on a.user_id = c.user_id

-- Bonus tracking - what user actually received
left join (
    select
        user_id,
        bonus_ts,
        sku_id,
        bonus_amount,
        skudata_tran_ticket,
        case
            when bonus_type_id = 1 then 'coins'
            when bonus_type_id = 12 then 'slotobucks'  
            when bonus_type_id = 32 then 'gems'
            when bonus_type_id = 178 then 'powerup'
            when bonus_type_id = 235 then 'picks'
            when bonus_type_id = 295 then 'cards'
            else 'other'
        end as bonus_type_name
    from kafka.kds_sm_bonus_history_new
    where bonus_date = current_date
      and action_id = 'RV'
) bonus on a.user_id = bonus.user_id and a.transaction_id = bonus.skudata_tran_ticket

-- Platform information
left join (
    select user_id, session_id, platform_id 
    from dwh.fact_sm_sessions_kafka 
    where session_creation_date = current_date 
    group by 1, 2, 3
) j on a.user_id = j.user_id and a.session_id = j.session_id

-- User profile
left join (
    select user_id, email, country_name 
    from dwh.sm_user_profile
) up on a.user_id = up.user_id

-- Test group allocation  
left join (
    select distinct
        a.user_id as t_user_id,
        group_name
    from sm_ds.abtest_user_allocations a
    left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
    left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
    where test_id = 'xmXDU4lG4J'
) t on a.user_id = t.t_user_id

-- Prestige level (for multipliers)
left join (
    select
        user_id,
        old_precious_level,
        new_precious_level,
        event_ts,
        coalesce(lead(event_ts) over (partition by user_id order by event_ts), current_timestamp) as lead_event_ts
    from dwh.sm_fact_precious_level_up
) pres on a.user_id = pres.user_id and a.event_ts between pres.event_ts and pres.lead_event_ts

-- Prestige multipliers
left join (
    select * from sm_draft.prestige_multipliers_03_12
) mult on pres.new_precious_level = mult.prestige_level

-- Tier multipliers
left join (
    select tier_id, tier_multiplier 
    from dwh.Dim_Coins_Value 
    where platform = 'Web' 
    group by 1, 2
) tier on c.cz_price_cut_test = tier.tier_id  -- Simplified join

-- Configuration thresholds using promo_date
left join (
    select *
    from sm_draft.RV_opportunistic_min_eCPM_per_segment
    where rv_segment = 'DPU_60_90'
) config on b.rv_opportunistic_config_buckets = config.parameter_value
    and c.cz_price_cut_test between config.config_cz_from and config.config_cz_to
    and a.promo_date >= config.config_promo_date_from
    and a.promo_date < config.config_promo_date_to

order by a.event_ts desc;
