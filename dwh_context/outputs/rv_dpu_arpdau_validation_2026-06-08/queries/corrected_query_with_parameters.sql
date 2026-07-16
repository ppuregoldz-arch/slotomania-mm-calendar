/*
CORRECTED QUERY WITH ACTUAL PARAMETER VALUES
=============================================

Original Parameters Replaced:
- <Parameters.start date> = '2026-05-17'
- <Parameters.end date> = '2026-06-08' 
- <Parameters.test id> = 'xmXDU4lG4J'

This query will pull data for the full date range and can be filtered 
to specific dates (like 2026-06-01) in the outer query or dashboard.
*/

select
    a.promo_date,
    case when group_name = 'Control' then 'Test_C'
     when group_name = 'Test_C' then 'Control'
         else group_name end as group_name,
    is_during_users,
    allocation_percentage,
    rv_segment_opportunistic_fixed,
    case
        when coalesce(cz_fixed, 0) < 3 then '0-2.99'
        when cz_fixed < 5 then '3-4.99'
        when cz_fixed < 10 then '5-9.99'
        when cz_fixed < 15 then '10-14.99'
        when cz_fixed < 20 then '15-19.99'
        when cz_fixed < 25 then '20-24.99'
        when cz_fixed < 30 then '25-29.99'
        when cz_fixed < 35 then '30-35.99'
        when cz_fixed < 40 then '35-39.99'
        when cz_fixed < 45 then '40-44.99'
        when cz_fixed < 50 then '45-49.99'
        when cz_fixed < 60 then '50-59.99'
        when cz_fixed < 70 then '60-69.99'
        when cz_fixed < 80 then '70-79.99'
        when cz_fixed < 90 then '80-89.99'
        when cz_fixed < 100 then '90-99.99'
        when cz_fixed < 130 then '100-129.99'
        when cz_fixed < 160 then '130-159.99'
        when cz_fixed < 200 then '160-199.99'
        when cz_fixed < 10000 then '200-9999.99'
        end as cz_range_fixed,
    coalesce(rv_dpu_tenure_split_feb16, 'DPU 180+') as rv_dpu_tenure_split_feb16,
    case when o.user_id is not null then 1 else 0 end as outliers_during,
    case when o2.user_id is not null then 1 else 0 end as outluers_before,
    count (distinct a.user_id) as DAU,
    sum(net_amount) as rev,
    sum (revenue) as RV_rev,
    count(distinct b.user_id) as PUs,
    count (distinct c.user_id) as RV_users,
    sum(tran_id) as trx
/*hourly - agg to user & day*/
from (
    select
        date(calc_hour_ts::timestamp AT TIME ZONE 'UTC' at
            time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
        user_id
    from agg.agg_sm_hourly_user_stats
    where 1=1
        -- REPLACED: <Parameters.start date>::timestamp-14 with actual value
        and date(calc_hour_ts::timestamp AT TIME ZONE 'UTC' at
            time zone 'Asia/Jerusalem' - interval '14 hours') >= '2026-05-17'::timestamp - interval '14 days'
    group by 1,2
) a
/*test groups*/
left join (
    select distinct
        a.user_id as t_user_id,
        group_name,
        allocation_percentage,
        case when during_users.user_id is not null then true else false end is_during_users
    from sm_ds.abtest_user_allocations a
    left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
    left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
    left join (
        select distinct user_id
        from dwh.fact_sm_sessions_kafka
        where date(session_creation_ts::timestamp AT TIME ZONE 'UTC' at
            time zone 'Asia/Jerusalem' - interval '14 hours') >= '2026-05-17'::timestamp
    ) during_users on a.user_id = during_users.user_id
    -- REPLACED: <Parameters.test id> with actual value
    where test_id = 'xmXDU4lG4J'
) t on a.user_id = t.t_user_id
/*payments & CZ*/
left join (
    SELECT
        a.user_id,
        date(tran_ts::timestamp AT TIME ZONE 'UTC' at
            time zone 'Asia/Jerusalem' - interval '14 hours') promo_date,
        count (distinct tran_id) as tran_id,
        sum (net_amount) as net_amount
    from dwh.sm_fact_payments a
    where 1 = 1
        and tran_status_id = 2
        and artificial_ind = 0
        and a.user_id not in (select distinct user_id from dwh.playtika_users)
        and a.user_id not in (
            select distinct user_id 
            from dwh.sm_fact_journey_state_notifications 
            where step_id = 539265
        )
        and is_test = 0
        and a.user_id > 0
        -- REPLACED: Parameter date range with actual values
        AND date(tran_ts::timestamp AT TIME ZONE 'UTC' at
            time zone 'Asia/Jerusalem' - interval '14 hours')
        between date('2026-05-17'::timestamp) - interval '14 days' 
            and date('2026-06-08'::timestamp) + interval '14 days'
    group by 1,2
) b on a.user_id = b.user_id and a.promo_date = b.promo_date
/*rv main KPIs*/
left join (
    select 
        user_id,
        date(event_ts::timestamp AT TIME ZONE 'UTC' at
            time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
        sum (revenue) as revenue
    from agg.agg_sm_rv_client_displayed_events
    where 1=1
        -- REPLACED: <Parameters.start date> with actual value
        and date(event_ts::timestamp AT TIME ZONE 'UTC' at
            time zone 'Asia/Jerusalem' - interval '14 hours') >= 
            date('2026-05-17'::timestamp) - interval '14 days'
    group by 1,2
) c on a.user_id = c.user_id and a.promo_date = c.promo_date
/*RV segment*/
left join (
    select
        user_id,
        cz_price_cut_test,
        case
            when coalesce(cz_price_cut_test, 0) < 3 then '0-2.99'
            when cz_price_cut_test < 5 then '3-4.99'
            when cz_price_cut_test < 10 then '5-9.99'
            when cz_price_cut_test < 15 then '10-14.99'
            when cz_price_cut_test < 20 then '15-19.99'
            when cz_price_cut_test < 25 then '20-24.99'
            when cz_price_cut_test < 30 then '25-29.99'
            when cz_price_cut_test < 35 then '30-35.99'
            when cz_price_cut_test < 40 then '35-39.99'
            when cz_price_cut_test < 45 then '40-44.99'
            when cz_price_cut_test < 50 then '45-49.99'
            when cz_price_cut_test < 60 then '50-59.99'
            when cz_price_cut_test < 70 then '60-69.99'
            when cz_price_cut_test < 80 then '70-79.99'
            when cz_price_cut_test < 90 then '80-89.99'
            when cz_price_cut_test < 100 then '90-99.99'
            when cz_price_cut_test < 130 then '100-129.99'
            when cz_price_cut_test < 160 then '130-159.99'
            when cz_price_cut_test < 200 then '160-199.99'
            when cz_price_cut_test < 10000 then '200-9999.99'
        end as cz_range,
        event_date_datamining,
        snapshot_insert_ts,
        case
            when rv_segment_opportunistic is null then rv_opportunistic_segment
            else rv_segment_opportunistic 
        end as rv_segment_opportunistic,
        -- REPLACED: <Parameters.start date> with actual value
        max(case
            when event_date_datamining = '2026-05-17'::date then (
                case
                    when rv_segment_opportunistic is null then rv_opportunistic_segment
                    else rv_segment_opportunistic 
                end
            )
            else null 
        end) over (partition by user_id) as rv_segment_opportunistic_fixed,
        -- REPLACED: <Parameters.start date> with actual value
        max(case
            when event_date_datamining = '2026-05-17'::date then cz_price_cut_test
            else null 
        end) over (partition by user_id) as cz_fixed
    from dwh.sm_user_profile_datamining_snapshot
    where date(snapshot_insert_ts::timestamp AT TIME ZONE 'UTC' at
        time zone 'Asia/Jerusalem' - interval '14 hours') >= 
        date('2026-05-17') - 30
) dms on a.user_id = dms.user_id and a.promo_date = dms.event_date_datamining
/*outliers*/
left join (
    select user_id
    from (
        SELECT
            z.*,
            case
                when lg > P75 then (lg - P75) / daily_STDDEV
                else 0 
            end as 'how_far_from_P25_P75'
        FROM (
            select
                a.user_id,
                log(gross_rev) as lg,
                gross_rev,
                percentile_cont(0.75) within group (order by (log(gross_rev)) asc) over () as P75,
                stddev(log(gross_rev)) over () as daily_stddev
            from (
                select 
                    a.user_id, 
                    sum(gross_rev) gross_rev
                from agg.agg_sm_daily_promotion_stats a
                left join dwh.sm_user_profile_datamining_snapshot b
                    on a.user_id = b.user_id and promo_date = date(snapshot_insert_ts)
                -- REPLACED: Parameter date range with actual values
                where promo_date between date('2026-05-17'::timestamp) and date('2026-06-08'::timestamp)
                    and gross_rev > 0
                    and gross_rev is not null
                    and promo_date <= current_date
                    and a.user_id not in (
                        select distinct user_id
                        from dwh.playtika_users
                        where environment_id = 12
                    )
                group by 1
            ) a
        ) z
    ) a
    where abs(how_far_from_P25_P75) >= 3
) o on a.user_id = o.user_id
left join (
    select user_id
    from (
        SELECT
            z.*,
            case
                when lg > P75 then (lg - P75) / daily_STDDEV
                else 0 
            end as 'how_far_from_P25_P75'
        FROM (
            select
                a.user_id,
                log(gross_rev) as lg,
                gross_rev,
                percentile_cont(0.75) within group (order by (log(gross_rev)) asc) over () as P75,
                stddev(log(gross_rev)) over () as daily_stddev
            from (
                select 
                    a.user_id, 
                    sum(gross_rev) gross_rev
                from agg.agg_sm_daily_promotion_stats a
                left join dwh.sm_user_profile_datamining_snapshot b
                    on a.user_id = b.user_id and promo_date = date(snapshot_insert_ts)
                -- REPLACED: Parameter date range with actual values for "before" period
                where promo_date between date('2026-05-17'::timestamp) - interval '14 days' 
                    and date('2026-05-17'::timestamp) - interval '1 day'
                    and gross_rev > 0
                    and gross_rev is not null
                    and promo_date <= current_date
                    and a.user_id not in (
                        select distinct user_id
                        from dwh.playtika_users
                        where environment_id = 12
                    )
                group by 1
            ) a
        ) z
    ) a
    where abs(how_far_from_P25_P75) >= 3
) o2 on a.user_id = o2.user_id
/*rv segment - 90-180 VS 180+*/
LEFT JOIN (
    SELECT
        user_id as dpu_tenure_feb16_user_id,
        CASE
            WHEN rv_segment_opportunistic = 'DPU_90+'
                AND (('2026-02-16'::DATE - last_purchase_promo_date) > 180 or last_purchase_promo_date is null)
            THEN 'DPU 180+'
            WHEN rv_segment_opportunistic = 'DPU_90+'
                AND ('2026-02-16'::DATE - last_purchase_promo_date) > 90
                AND ('2026-02-16'::DATE - last_purchase_promo_date) <= 180
            THEN 'DPU_90-180'
            ELSE rv_segment_opportunistic
        END AS rv_dpu_tenure_split_feb16,*
    FROM (
        SELECT
            user_id,
            rv_segment_opportunistic
        FROM dwh.sm_user_profile_datamining_snapshot
        -- REPLACED: <Parameters.start date> with actual value
        WHERE event_date_datamining = '2026-05-17'::date
    ) AS seg
    LEFT JOIN (
        select
            user_id as last_trx_user_id,
            max(promo_date) as last_purchase_promo_date
        from agg.agg_sm_daily_promotion_stats
        where 1 = 1
            -- REPLACED: <Parameters.start date> with actual value
            and promo_date < '2026-05-17'::date
            and gross_rev > 0
        group by 1
    ) AS last_trx ON seg.user_id = last_trx.last_trx_user_id
) AS dpu_tenure_feb16 ON a.user_id = dpu_tenure_feb16.dpu_tenure_feb16_user_id
where 1=1
group by 1,2,3,4,5,6,7,8,9;

/*
PARAMETER REPLACEMENT SUMMARY:
==============================
- <Parameters.start date> → '2026-05-17'
- <Parameters.end date> → '2026-06-08'
- <Parameters.test id> → 'xmXDU4lG4J'

DATE RANGES USED:
=================
- Hourly user stats: >= '2026-05-03' (start date - 14 days)
- Test groups: >= '2026-05-17' (start date)
- Payments: '2026-05-03' to '2026-06-22' (start date ± 14 days, end date + 14 days)
- RV events: >= '2026-05-03' (start date - 14 days)
- User profile snapshot: >= '2026-04-17' (start date - 30 days)
- Outliers during: '2026-05-17' to '2026-06-08' (start to end date)
- Outliers before: '2026-05-03' to '2026-05-16' (start date - 14 days to start date - 1)
- DPU segments: event_date = '2026-05-17', last purchase < '2026-05-17'

TO FILTER FOR 2026-06-01 ANALYSIS:
==================================
Add this WHERE clause to the outer query:
WHERE promo_date = '2026-06-01'::date

OR use this in your dashboard filters.
*/