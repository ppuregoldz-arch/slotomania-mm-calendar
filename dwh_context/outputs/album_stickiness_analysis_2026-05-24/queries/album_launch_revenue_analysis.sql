/*
Album Launch Revenue Analysis - Weekly Revenue Patterns Around Album Launches

Business Logic:
- Analyze average daily gross revenue 1 week before vs 1 week after album launch
- Reference point: Album launch date = Day 0 (excluded from analysis)
- Week Before: Days -7 to -1 (7 days, launch day excluded)
- Week After: Days +1 to +7 (7 days, launch day excluded)
- Revenue source: agg.agg_sm_daily_users_stats.daily_gross_rev
- Analysis covers the past 5 album launches (most recent first)

Purpose: Identify revenue patterns and potential album launch impact on player spending behavior.
*/

select
    album_name,
    launch_date,
    round(avg(case when period = 'Before' then daily_gross_rev end), 2) as avg_daily_revenue_before,
    round(avg(case when period = 'After' then daily_gross_rev end), 2) as avg_daily_revenue_after,
    round(
        avg(case when period = 'After' then daily_gross_rev end) / nullif(avg(case when period = 'Before' then daily_gross_rev end), 0) - 1,
        3
    ) as revenue_change_ratio /*after vs before - 0.1 means 10% increase*/
from (
    select
        a.album_name,
        a.launch_date,
        u.calc_date,
        case 
            when u.calc_date between a.launch_date - interval '7 days' and a.launch_date - interval '1 day' then 'Before'
            when u.calc_date between a.launch_date + interval '1 day' and a.launch_date + interval '7 days' then 'After'
        end as period,
        u.daily_gross_rev
    /*album launch dates - last 5 albums*/
    from (
        select
            album_name,
            launch_date
        from sm_draft.ariel_dim_albums_info
        where album_type <> 'Communal'
        order by launch_date desc
        limit 5
    ) a
    /*daily revenue data*/
    join (
        select
            calc_date,
            sum(daily_gross_rev) as daily_gross_rev
        from agg.agg_sm_daily_users_stats
        where user_id > 0
          /*exclude playtika employees*/
          and user_id not in (select distinct user_id from dwh.playtika_users)
          /*exclude test users*/
          and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
        group by 1
    ) u on u.calc_date between a.launch_date - interval '7 days' and a.launch_date + interval '7 days'
       and u.calc_date <> a.launch_date  -- exclude launch day itself
) revenue_periods
where period is not null  -- only include before/after periods
group by 1, 2
order by launch_date desc;

/*
VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Entities: To be validated with specific album launch dates
Validation Date Range: 7 days before/after each album launch (excluding launch day)
Raw Data Source: agg.agg_sm_daily_users_stats - daily_gross_rev aggregated by calc_date
Expected Result: Each album should show average daily revenue for 7-day periods before and after launch
Actual Query Result: [To be validated after execution]
Validation Status: [To be completed]
Notes: Revenue change ratio shows proportional increase/decrease (0.1 = 10% increase, -0.1 = 10% decrease)
*/