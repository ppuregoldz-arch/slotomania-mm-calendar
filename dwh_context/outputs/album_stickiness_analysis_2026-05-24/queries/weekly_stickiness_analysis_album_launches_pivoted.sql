/*
Weekly Stickiness Analysis - Pivoted Format (One Row Per Album)

Business Logic:
- Day 0 = Launch day (excluded from analysis)
- Week Before Launch = Days -7 to -1  
- Week After Launch = Days 1 to 7
- One row per album with before/after metrics in separate columns
- Includes change calculations for easy comparison

VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Status: Pivoted version of corrected stickiness query
Notes: Each album gets one row with before/after metrics in separate columns.
Corrected user exclusion filters applied as per workspace standards.
*/

select 
    launch_date,
    album_name,
    
    /*WAU metrics*/
    sum(case when period = 'Before' then wau else 0 end) as wau_before,
    sum(case when period = 'After' then wau else 0 end) as wau_after,
    sum(case when period = 'After' then wau else 0 end) - sum(case when period = 'Before' then wau else 0 end) as wau_change,
    
    /*Login Frequency metrics*/
    sum(case when period = 'Before' then login_frequency else 0 end) as login_frequency_before,
    sum(case when period = 'After' then login_frequency else 0 end) as login_frequency_after,
    sum(case when period = 'After' then login_frequency else 0 end) - sum(case when period = 'Before' then login_frequency else 0 end) as login_frequency_change,
    
    /*Stickiness metrics*/
    round(max(case when period = 'Before' then stickiness end), 3) as stickiness_before,
    round(max(case when period = 'After' then stickiness end), 3) as stickiness_after,
    round(max(case when period = 'After' then stickiness end) - max(case when period = 'Before' then stickiness end), 3) as stickiness_change
    
from (
    select 
        launch_date,
        album_name,
        period,
        count(distinct user_id) as wau, /*weekly active users*/
        count(distinct user_id || '|' || activity_date) as login_frequency, /*total user-day combinations*/
        round(
            count(distinct user_id || '|' || activity_date)::numeric / 
            nullif(count(distinct user_id), 0), 
            3
        ) as stickiness /*average active days per active user*/
    from (
        -- Before periods for all albums
        select 
            a.album_id,
            a.album_name,
            a.launch_date,
            'Before' as period,
            u.user_id,
            u.calc_date as activity_date
        from (
            select 
                album_id,
                album_name,
                launch_date
            from sm_draft.ariel_dim_albums_info
            where album_type <> 'Communal'
            order by launch_date desc
            limit 5
        ) a
        join agg.agg_sm_daily_users_stats u
            on u.calc_date between a.launch_date - interval '7 days' and a.launch_date - interval '1 day'
        where u.user_id > 0
          /*exclude playtika employees*/
          and u.user_id not in (select distinct user_id from dwh.playtika_users)
          /*exclude test users*/
          and u.user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
        
        union all
        
        -- After periods for all albums  
        select 
            a.album_id,
            a.album_name,
            a.launch_date,
            'After' as period,
            u.user_id,
            u.calc_date as activity_date
        from (
            select 
                album_id,
                album_name,
                launch_date
            from sm_draft.ariel_dim_albums_info
            where album_type <> 'Communal'
            order by launch_date desc
            limit 5
        ) a
        join agg.agg_sm_daily_users_stats u
            on u.calc_date between a.launch_date + interval '1 day' and a.launch_date + interval '7 days'
        where u.user_id > 0
          /*exclude playtika employees*/
          and u.user_id not in (select distinct user_id from dwh.playtika_users)
          /*exclude test users*/
          and u.user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
    ) user_activity_periods
    group by 1, 2, 3
) period_metrics
group by 1, 2
order by launch_date desc;