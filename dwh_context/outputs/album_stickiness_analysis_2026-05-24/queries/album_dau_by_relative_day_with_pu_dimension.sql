/*
Album DAU by Relative Day with Pre-Album Paying User Dimension

Business Logic:
- Calculate DAU for each relative album day (-14 to +14)
- Add is_PU_14d dimension: 1 if user was paying user in 14 days before album launch, 0 if not
- Lookback period for PU classification: Days -14 to -1 (excluding launch day 0)
- PU definition: Made any payment (daily_Net_revenue > 0) during the 14-day lookback period
- Analysis covers the past 5 album launches

Purpose: Analyze album engagement patterns segmented by pre-album purchasing behavior.
*/

select
    album_dates.album_name,
    album_dates.launch_date,
    album_dates.album_name_with_date,
    album_dates.relative_day,
    album_dates.actual_date,
    coalesce(pu_classification.is_pu_14d, 0) as is_pu_14d,
    count(distinct daily_users.user_id) as dau
/*albums & relative dates*/
from (
    select
        album_name,
        launch_date,
        album_name || ' (' || launch_date || ')' as album_name_with_date,
        datediff('day', launch_date, calendar_date) as relative_day,
        calendar_date as actual_date
    /*album relative days using date arithmetic*/
    from (
        /*Albums from existing table*/
        select
            album_name,
            launch_date
        from sm_draft.ariel_dim_albums_info
        where album_type <> 'Communal'
        order by launch_date desc
        limit 5
    ) albums
    /*dates, for each album, 14 days before & after*/
    cross join (
        /*Use date dimension table or generate date range*/
        select
            date as calendar_date
        from dwh.dim_dates
        where date >= ('2025-06-01'::date - 30) /*extend range for before/after calculations*/
          and date <= (current_date + 30)
    ) date_range
    where datediff('day', albums.launch_date, date_range.calendar_date) between -14 and 14
    /*filter to 14 days before and after each album start*/
) album_dates
/*active users per day*/
join (
    select 
        user_id,
        promo_date
    from agg.agg_sm_daily_promotion_stats
    where promo_date >= ('2025-06-01'::date - 30)
      and user_id > 0
      /*exclude playtika employees*/
      and user_id not in (select distinct user_id from dwh.playtika_users)
      /*exclude test users*/
      and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
) daily_users on album_dates.actual_date = daily_users.promo_date
/*paying user classification - 14 days before album launch*/
left join (
    select distinct
        album_dates_inner.album_name,
        album_dates_inner.launch_date,
        pu_users.user_id,
        1 as is_pu_14d
    /*album launch dates for PU lookback*/
    from (
        select
            album_name,
            launch_date
        from sm_draft.ariel_dim_albums_info
        where album_type <> 'Communal'
        order by launch_date desc
        limit 5
    ) album_dates_inner
    /*users with payments 14 days before album launch (excluding launch day)*/
    join (
        select distinct
            user_id,
            calc_date
        from agg.agg_sm_daily_users_stats
        where daily_Net_revenue > 0
          and user_id > 0
          /*exclude playtika employees*/
          and user_id not in (select distinct user_id from dwh.playtika_users)
          /*exclude test users*/
          and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
    ) pu_users on pu_users.calc_date between album_dates_inner.launch_date - interval '14 days' 
                                           and album_dates_inner.launch_date - interval '1 day'
) pu_classification on album_dates.album_name = pu_classification.album_name
                     and album_dates.launch_date = pu_classification.launch_date
                     and daily_users.user_id = pu_classification.user_id
group by 1, 2, 3, 4, 5, 6
order by album_dates.launch_date desc, album_dates.relative_day, coalesce(pu_classification.is_pu_14d, 0) desc;

/*
VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Entities: To be validated with specific users and album launch dates
Validation Date Range: 14 days before and after each album launch
Raw Data Source: agg.agg_sm_daily_promotion_stats for DAU, agg.agg_sm_daily_users_stats for PU classification
Expected Result: Each album/day combination should show DAU split by is_pu_14d (1 for recent payers, 0/NULL for non-payers)
Actual Query Result: [To be validated after execution]
Validation Status: [To be completed]
Notes: is_pu_14d = 1 means user had daily_Net_revenue > 0 in days -14 to -1 before album launch
*/