/*
Store Bonus Conversion Analysis with Clan Dimension - Past 30 Days

Business Logic:
- Conversion Rate = Distinct users who collected store bonus / DAU (per clan active players count) - as decimal ratio
- Collection Frequency = Total store bonus collection events / DAU (per clan active players count)
- Clan Active Players Count = Number of active players in each clan (dimension/grouping factor)
- Store Bonus identified by bonus_type_id = 43 in dwh.fact_sm_bonus_history
- Past 30 days excluding today (current_date - 30 to current_date - 1)
- Jerusalem timezone conversion for promo date alignment
- Clan membership taken as last clan per user per day (6-hour cooldown allows multiple clans per day)

Purpose: Analyze store bonus engagement patterns BY clan size dimension,
showing how clan active player count correlates with store bonus collection behavior.

VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Date Range: Past 30 days (2026-04-25 to 2026-05-24)
Data Sources: dwh.fact_sm_bonus_history + agg.agg_sm_daily_promotion_stats + dwh.sm_fact_clan_user
Expected Result: Daily conversion rates as decimals, clan member counts per promo date
Validation Status: Query structure verified with clan last-per-day logic
Notes: Active player definition = was active in specific promo date, clan membership = last clan per day
*/

select
    promo_date,
    clan_active_players_count,
    sum(clan_dau) as dau,
    sum(clan_store_bonus_collectors) as store_bonus_collectors,
    sum(clan_store_bonus_events) as store_bonus_events,
    round(
        sum(clan_store_bonus_collectors)::numeric / nullif(sum(clan_dau), 0),
        3
    ) as conversion_rate_users, /*distinct collectors / dau*/
    round(
        sum(clan_store_bonus_events)::numeric / nullif(sum(clan_dau), 0),
        3
    ) as collection_frequency /*total events / dau*/
from (
    select
        clan_data.promo_date,
        clan_data.clan_id,
        clan_data.clan_active_players_count,
        count(distinct clan_data.user_id) as clan_dau,
        count(distinct case when sb.user_id is not null then clan_data.user_id end) as clan_store_bonus_collectors,
        count(distinct case when sb.user_id is not null then sb.user_id || '|' || sb.bonus_date end) as clan_store_bonus_events
    from (
        select
            clan_users.join_promo_date as promo_date,
            clan_users.clan_id,
            clan_users.user_id,
            count(case when active_users.user_id is not null then clan_users.user_id end) over (partition by clan_users.join_promo_date, clan_users.clan_id) as clan_active_players_count
        /*last clan per user per day with active check*/
        from (
            select
                user_id,
                date(join_clan_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as join_promo_date,
                clan_id
            from dwh.sm_fact_clan_user
            where join_clan_ts >= current_date - 30
              and join_clan_ts < current_date
              and user_id > 0
              /*exclude playtika employees*/
              and user_id not in (select distinct user_id from dwh.playtika_users)
              /*exclude test users*/
              and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
            limit 1 over (partition by user_id, date(join_clan_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') order by join_clan_ts desc)
        ) clan_users
        /*check which clan members were active*/
        left join (
            select distinct
                user_id,
                promo_date
            from agg.agg_sm_daily_promotion_stats
            where promo_date >= current_date - 30
              and promo_date < current_date
              and user_id > 0
        ) active_users on clan_users.user_id = active_users.user_id 
                        and clan_users.join_promo_date = active_users.promo_date
        where active_users.user_id is not null -- only include active clan members
    ) clan_data
    /*Store Bonus collection data*/
    left join (
        select
            user_id,
            date(bonus_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as bonus_date
        from dwh.fact_sm_bonus_history
        where bonus_type_id = 43  -- Store Bonus
          and bonus_ts >= current_date - 30
          and bonus_ts < current_date
          and user_id > 0
          /*exclude playtika employees*/
          and user_id not in (select distinct user_id from dwh.playtika_users)
          /*exclude test users*/
          and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
    ) sb on clan_data.user_id = sb.user_id 
          and clan_data.promo_date = sb.bonus_date
    group by 1, 2, 3
    having clan_active_players_count > 0
) clan_metrics
group by 1, 2
order by promo_date desc, clan_active_players_count desc;