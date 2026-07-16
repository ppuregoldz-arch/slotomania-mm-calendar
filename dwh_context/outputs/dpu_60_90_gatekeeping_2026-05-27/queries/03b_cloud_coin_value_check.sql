/*
DPU 60-90 Gatekeeping Query 3b: Cloud Coin Value Configuration Check
====================================================================
Purpose: Validate coin rewards match configuration for DPU_60_90 users (CLOUD ONLY)
Data Source: sm.sm_str_video_ads_history (Cloud uses different service than Offers)
Expected: coins_amount matches config calculation based on revenue thresholds
Note: Cloud doesn't use transaction_id - validated via FEATURE_REWARDED events
*/

select 
    user_id,
    business_date,
    business_ts,
    promo_date,
    feature,
    revenue,
    coins_amount as actual_coins,
    rv_segment_opportunistic,
    rv_opportunistic_config_buckets,
    RV_opportunistic_dynamic_ecpm,
    cz_price_cut_test,
    group_name as test_group,
    
    -- Configuration values
    config_min_ad_rev,
    config_min_ecpm,
    config_base_coins,
    Tier_multiplier,
    premium_multiplier,
    
    -- Expected coin calculation
    config_base_coins * coalesce(Tier_multiplier, 1) * coalesce(premium_multiplier, 1) as expected_coins,
    
    -- Validations
    case 
        when revenue >= config_min_ad_rev * coalesce(RV_opportunistic_dynamic_ecpm, 1) then 'ok'
        else 'wrong'
    end as revenue_threshold_validation,
    
    case 
        when round(coins_amount) = round(config_base_coins * coalesce(Tier_multiplier, 1) * coalesce(premium_multiplier, 1)) then 'ok'
        else 'wrong'
    end as coins_amount_validation,
    
    case 
        when rv_segment_opportunistic = 'DPU_60_90' then 'ok'
        else 'wrong'
    end as segment_validation,
    
    case
        when group_name in ('Test_A', 'Test_B', 'Control') then 'ok'
        else 'wrong'
    end as test_group_validation

from (
    select 
        a.*,
        t.group_name,
        c.rv_segment_opportunistic,
        c.rv_opportunistic_config_buckets,
        c.RV_opportunistic_dynamic_ecpm,
        c.cz_price_cut_test,
        c.tier_id_user,
        d.new_precious_level,
        e.premium_multiplier,
        f.Tier_multiplier,
        config.config_min_ecpm,
        config.config_min_ad_rev,
        
        -- DPU 60-90 configuration base coins (based on CZ buckets 1000-6000)
        case
            when c.rv_opportunistic_config_buckets = 1000 and a.revenue >= 0.02 then 708750   -- CZ 0, min $0.02
            when c.rv_opportunistic_config_buckets = 2000 and a.revenue >= 0.04 then 1417500  -- CZ 0.01-4.99, min $0.04
            when c.rv_opportunistic_config_buckets = 3000 and a.revenue >= 0.075 then 3262500 -- CZ 5-9.99, min $0.075
            when c.rv_opportunistic_config_buckets = 4000 and a.revenue >= 0.10 then 4350000  -- CZ 10-14.99, min $0.10
            when c.rv_opportunistic_config_buckets = 5000 and a.revenue >= 0.15 then 6525000  -- CZ 15-24.99, min $0.15
            when c.rv_opportunistic_config_buckets = 6000 and a.revenue >= 0.20 then 8700000  -- CZ 25-50, min $0.20
            else null
        end as config_base_coins
        
    from (
        -- Cloud rewards data
        select 
            event_type,
            user_id,
            session_id,
            feature,
            business_date,
            business_ts,
            date(business_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
            reward_id,
            coins_reward_request_id,
            coins_amount,
            max(revenue) over (partition by reward_id) as revenue
        from sm.sm_str_video_ads_history
        where user_id not in (select distinct user_id from dwh.playtika_users)
          and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
          and business_date = current_date
          and feature ilike '%cloud%'
          and event_type = 'FEATURE_REWARDED'
          and coins_amount > 0
    ) a
    
    -- User segmentation (DPU_60_90 only)
    join (
        select user_id, rv_segment_opportunistic, rv_opportunistic_config_buckets, 
               RV_opportunistic_dynamic_ecpm, cz_price_cut_test, tier_id_user
        from dwh.sm_user_profile_datamining_snapshot
        where event_date_datamining = current_date
          and rv_segment_opportunistic = 'DPU_60_90'
    ) c on a.user_id = c.user_id
    
    -- Prestige level data
    left join (
        select user_id, new_precious_level, event_ts,
               coalesce(lead(event_ts) over (partition by user_id order by event_ts), current_timestamp) as lead_event_ts
        from dwh.sm_fact_precious_level_up
    ) d on a.user_id = d.user_id and a.business_ts between d.event_ts and d.lead_event_ts
    
    -- Prestige multipliers
    left join (
        select prestige_level, premium_multiplier
        from sm_draft.prestige_multipliers_03_12
    ) e on d.new_precious_level = e.prestige_level
    
    -- Tier multipliers
    left join (
        select tier_id, tier_multiplier
        from dwh.Dim_Coins_Value
        where platform = 'Web'
        group by 1, 2
    ) f on c.tier_id_user = f.tier_id
    
    -- Configuration thresholds using promo_date
    left join (
        select rv_segment, min_ecpm as config_min_ecpm, min_ad_rev as config_min_ad_rev, parameter_value,
               config_cz_from, config_cz_to, config_promo_date_from, config_promo_date_to
        from sm_draft.RV_opportunistic_min_eCPM_per_segment
        where rv_segment = 'DPU_60_90'
    ) config on c.rv_opportunistic_config_buckets = config.parameter_value
        and c.cz_price_cut_test between config.config_cz_from and config.config_cz_to
        and a.promo_date >= config.config_promo_date_from
        and a.promo_date < config.config_promo_date_to
    
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

) final_data

where config_base_coins is not null  -- Only include events with valid configuration

order by business_ts desc;