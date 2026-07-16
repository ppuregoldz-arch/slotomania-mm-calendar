# Daily Dash Max - SQL Queries

**Note**: This file contains actual SQL queries extracted from the Super Dash views.twbx for Daily Dash Max analysis and investigations.

## Query Inventory

### 1. Daily Dash Revenue Distribution Analysis
**Purpose**: Analyze revenue distribution patterns for Daily Dash Max across different tiers and time periods
**Tables**: `dwh.sm_fact_payments`, `sm_draft.SM_DIM_Products`
**Validation**: Track revenue patterns and tier-based performance metrics

```sql
select
    promo_date,
    tier_id,
    percentile_disc(0.50) within GROUP (ORDER BY net_amount ASC)
    over (partition BY promo_date, tier_id ) AS Median,
    percentile_disc(0.75) within GROUP (ORDER BY net_amount ASC)
    over (partition BY promo_date, tier_id ) AS p75,
    percentile_disc(0.95) within GROUP (ORDER BY net_amount ASC)
    over (partition BY promo_date, tier_id ) AS p95,
    percentile_disc(0.99) within GROUP (ORDER BY net_amount ASC)
    over (partition BY promo_date, tier_id ) AS p99
from (select
          date(tran_ts::timestamp AT TIME ZONE 'UTC' at
              time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
          tier_id,
          sum(net_amount)                                       as net_amount
      from dwh.sm_fact_payments a
               left join sm_draft.SM_DIM_Products b using (sku_id, transaction_source_type_id)
      where true
        and tran_status_id = 2
        and is_test = 0
        and user_id > 0
        and is_playtika_user = 0
        and artificial_ind = 0
        and tran_ts >= current_date - 60
        and (Product_Name = 'Daily Dash Plus'
          or sku_data ilike '{\"conditionTag\":\"J_No_Action\"}'
          or sku_data ilike '{\"conditionTag\":\"J_Roll_Dash_Max_Purchase\"}'
          or sku_data ilike '{J_Roll_ClanDashBundle_Purchase}'
          or sku_data ilike '{\"conditionTag\":\"J_Clan_Dash_bundle\"}')
      group by 1, 2, 3
      ) A
where tier_id > 0
limit 1 over(partition by promo_date,tier_id order by promo_date)
```

### 2. Super Dash Mission Completion Distribution Analysis
**Purpose**: Analyze mission completion patterns with percentile distribution by season, day, and user type
**Tables**: `dwh.sm_fact_super_dash`, `dwh.sm_fact_payments`, `sm_draft.SM_DIM_Products`
**Validation**: Track mission completion rates across Super Dash seasons with purchase behavior

```sql
select
    season_start_date,
    promo_date,
    day,
    user_type,
    percentile_disc(0.50) within GROUP (ORDER BY running_total ASC)
    over (partition BY season_start_date,promo_date,day,user_type ) AS Median,
    percentile_disc(0.75) within GROUP (ORDER BY running_total ASC)
    over (partition BY season_start_date,promo_date,day,user_type ) AS p75,
    percentile_disc(0.95) within GROUP (ORDER BY running_total ASC)
    over (partition BY season_start_date,promo_date,day,user_type ) AS p95,
    percentile_disc(0.99) within GROUP (ORDER BY running_total ASC)
    over (partition BY season_start_date,promo_date,day,user_type) AS p99

from (select
          season_start_date,
          promo_date,
          day,
          a.user_id,
          case
              when p.user_id is null then 'NPU'
              when user_type = 1 then 'Dash Max PU'
              when user_type = 0 then 'PU'
              end                                                                            as user_type,
          mission_finished,
          sum(mission_finished) over (partition by season_start_date,a.user_id order by day) as running_total
      from (select
                season_start_date,
                date(event_ts::timestamp AT TIME ZONE 'UTC' at
                    time zone 'Asia/Jerusalem' - interval '14 hours')  as promo_date,
                datediff('day', season_start_date, date(event_ts::timestamp AT TIME ZONE 'UTC' at
                    time zone 'Asia/Jerusalem' - interval '14 hours')) as day,
                user_id,
                count(challenge_id)                                    as mission_finished

            from dwh.sm_fact_super_dash a
                     left join (select
                                    date                                   as season_start_date,
                                    date(date + interval ' 6 days')        as season_end_date,
                                    row_number() over (order by date desc) as season_counter
                                from dwh.dim_dates
                                where true
                                  and date >= current_date - 120
                                  and date <= current_date
                                  and dayofweek(date) = 2
                                ) b on date(event_ts::timestamp AT TIME ZONE 'UTC' at
                time zone 'Asia/Jerusalem' - interval '14 hours') between season_start_date and season_end_date
--       where event_ts >= '2025-05-05 11:00'
            where event_ts >= '2025-05-05 11:00'
              and status = 'FINISHED'
            group by 1, 2, 3, 4
            ) A
               left join (select
                              from_promo_date,
                              user_id,
                              max(case
                                      when Product_Name = 'Daily Dash Plus' then 1
                                      when sku_data ilike '{\"conditionTag\":\"J_No_Action\"}' then 1
                                      when sku_data ilike '{\"conditionTag\":\"J_Roll_Dash_Max_Purchase\"}' then 1
                                      when sku_data ilike '{J_Roll_ClanDashBundle_Purchase}' then 1
                                      when sku_data ilike '{\"conditionTag\":\"J_Clan_Dash_bundle\"}' then 1
                                      else 0
                                  end) as user_type
                          from dwh.sm_fact_payments a
                                   left join sm_draft.SM_DIM_Products b using (sku_id, transaction_source_type_id)
                                   left join (select
                                                  date                              as from_promo_date,
                                                  date(date + interval ' 6 days')   as to_promo_date,
                                                  row_number() over (order by date) as season_counter
                                              from dwh.dim_dates
                                              where date between current_date - 180 and current_date
                                                and date <= current_date
                                                and dayofweek(date) = 2
                                              order by season_counter desc
                                              ) c on date(tran_ts::timestamp AT TIME ZONE 'UTC' at
                              time zone 'Asia/Jerusalem' -
                                        interval '14 hours') between from_promo_date and to_promo_date
                          where true
                            and tran_date >= current_date - 120
                            and tran_status_id = 2
                            and is_test = 0
                            and user_id > 0
                            and is_playtika_user = 0
                            and artificial_ind = 0
                          group by 1, 2
                          ) p on a.season_start_date = p.from_promo_date and a.user_id = p.user_id
      ) A
limit 1 over(partition by season_start_date,promo_date,user_type,day order by season_start_date)
```

### 3. Daily Dash Mission Completion Distribution Analysis
**Purpose**: Alternative analysis using Daily Dash challenges table for mission completion patterns
**Tables**: `dwh.sm_fact_daily_dash_challenges`, `dwh.sm_fact_payments`, `sm_draft.SM_DIM_Products`
**Validation**: Compare mission completion using daily dash challenges vs super dash data

```sql
select
    season_start_date,
    promo_date,
    day,
    user_type,
    percentile_disc(0.50) within GROUP (ORDER BY running_total ASC)
    over (partition BY season_start_date,promo_date,day,user_type ) AS Median,
    percentile_disc(0.75) within GROUP (ORDER BY running_total ASC)
    over (partition BY season_start_date,promo_date,day,user_type ) AS p75,
    percentile_disc(0.95) within GROUP (ORDER BY running_total ASC)
    over (partition BY season_start_date,promo_date,day,user_type ) AS p95,
    percentile_disc(0.99) within GROUP (ORDER BY running_total ASC)
    over (partition BY season_start_date,promo_date,day,user_type) AS p99

from (select
          season_start_date,
          promo_date,
          day,
          a.user_id,
          case
              when p.user_id is null then 'NPU'
              when user_type = 1 then 'Dash Max PU'
              when user_type = 0 then 'PU'
              end                                                                            as user_type,
          mission_finished,
          sum(mission_finished) over (partition by season_start_date,a.user_id order by day) as running_total
      from (select
                season_start_date,
                date(event_ts::timestamp AT TIME ZONE 'UTC' at
                    time zone 'Asia/Jerusalem' - interval '14 hours')  as promo_date,
                datediff('day', season_start_date, date(event_ts::timestamp AT TIME ZONE 'UTC' at
                    time zone 'Asia/Jerusalem' - interval '14 hours')) as day,
                user_id,
                count(challenge_id)                                    as mission_finished

            from dwh.sm_fact_daily_dash_challenges a
                     left join (select
                                    date                                   as season_start_date,
                                    date(date + interval ' 6 days')        as season_end_date,
                                    row_number() over (order by date desc) as season_counter
                                from dwh.dim_dates
                                where true
                                  and date >= current_date - 120
                                  and date <= current_date
                                  and dayofweek(date) = 2
                                ) b on date(event_ts::timestamp AT TIME ZONE 'UTC' at
                time zone 'Asia/Jerusalem' - interval '14 hours') between season_start_date and season_end_date
--       where event_ts >= '2025-05-05 11:00'
            where event_ts >= '2025-05-05 11:00'
              and status = 'finished'
            group by 1, 2, 3, 4
            ) A
               left join (select
                              from_promo_date,
                              user_id,
                              max(case
                                      when Product_Name = 'Daily Dash Plus' then 1
                                      when sku_data ilike '{\"conditionTag\":\"J_No_Action\"}' then 1
                                      when sku_data ilike '{\"conditionTag\":\"J_Roll_Dash_Max_Purchase\"}' then 1
                                      when sku_data ilike '{J_Roll_ClanDashBundle_Purchase}' then 1
                                      when sku_data ilike '{\"conditionTag\":\"J_Clan_Dash_bundle\"}' then 1
                                      else 0
                                  end) as user_type
                          from dwh.sm_fact_payments a
                                   left join sm_draft.SM_DIM_Products b using (sku_id, transaction_source_type_id)
                                   left join (select
                                                  date                              as from_promo_date,
                                                  date(date + interval ' 6 days')   as to_promo_date,
                                                  row_number() over (order by date) as season_counter
                                              from dwh.dim_dates
                                              where date between current_date - 180 and current_date
                                                and date <= current_date
                                                and dayofweek(date) = 2
                                              order by season_counter desc
                                              ) c on date(tran_ts::timestamp AT TIME ZONE 'UTC' at
                              time zone 'Asia/Jerusalem' -
                                        interval '14 hours') between from_promo_date and to_promo_date
                          where true
                            and tran_date >= current_date - 120
                            and tran_status_id = 2
                            and is_test = 0
                            and user_id > 0
                            and is_playtika_user = 0
                            and artificial_ind = 0
                          group by 1, 2
                          ) p on a.season_start_date = p.from_promo_date and a.user_id = p.user_id
      ) A
limit 1 over(partition by season_start_date,promo_date,user_type,day order by season_start_date)
```

### 4. Super Dash Mission Completion by Tier Analysis
**Purpose**: Analyze mission completion patterns by user tier for Super Dash feature
**Tables**: `dwh.sm_fact_super_dash`
**Validation**: Track performance differences across different user tiers

```sql
select
    season_start_date,
    tier_id,
    percentile_disc(0.50) within GROUP (ORDER BY mission_finished ASC)
    over (partition BY season_start_date, tier_id) AS Median,
    percentile_disc(0.75) within GROUP (ORDER BY mission_finished ASC)
    over (partition BY season_start_date, tier_id) AS p75,
    percentile_disc(0.95) within GROUP (ORDER BY mission_finished ASC)
    over (partition BY season_start_date, tier_id) AS p95,
    percentile_disc(0.99) within GROUP (ORDER BY mission_finished ASC)
    over (partition BY season_start_date, tier_id) AS p99
from (select
          season_start_date,
          user_id,
          tier_id,
          count(challenge_id) as mission_finished
      from dwh.sm_fact_super_dash a
               left join (select
                              date                                   as season_start_date,
                              date(date + interval ' 6 days')        as season_end_date,
                              row_number() over (order by date desc) as season_counter
                          from dwh.dim_dates
                          where true
                            and date >= current_date - 120
                            and date <= current_date
                            and dayofweek(date) = 2
                          ) b on date(event_ts::timestamp AT TIME ZONE 'UTC' at
          time zone 'Asia/Jerusalem' - interval '14 hours') between season_start_date and season_end_date
      where event_ts >= '2025-05-05 11:00'
        and status = 'FINISHED'
      group by 1, 2, 3
      ) A
where tier_id > 0
limit 1 over ( partition by season_start_date,tier_id order by season_start_date)
```

### 5. Daily Dash User Engagement Analysis
**Purpose**: Track user engagement patterns including started vs finishing users with running totals
**Tables**: `dwh.sm_fact_daily_dash_points_history`, `dwh.sm_fact_payments`, `sm_draft.SM_DIM_Products`
**Validation**: Monitor user acquisition and retention patterns by purchase behavior

```sql
select
    aa.season_counter,
    aa.season_start_date,
    aa.user_type,
    aa.day,
    users,
    sum(users_started) over (partition by aa.season_start_date,aa.user_type order by aa.day) as running_sum_users_started,
    users_started,
    sum(users) over (partition by aa.season_start_date,aa.user_type order by aa.day) as running_sum_users
from (select
          a.season_counter,
          season_start_date,
          case
              when p.user_id is null then 'NPU'
              when user_type = 1 then 'Dash Max PU'
              when user_type = 0 then 'PU'
              end                                                as user_type,
          datediff('day', season_start_date, date(min_event_ts)) as day,
          count(distinct a.user_id)                              as users_started
      from (select
                season_counter,
                from_promo_date                                              as season_start_date,
                user_id,
                min(date(event_ts::timestamp AT TIME ZONE 'UTC' at
                    time zone 'Asia/Jerusalem' - interval '14 hours'))::date as min_event_ts
            from dwh.sm_fact_daily_dash_points_history a
                     left join (select
                                    date                              as from_promo_date,
                                    date(date + interval ' 6 days')   as to_promo_date,
                                    row_number() over (order by date) as season_counter
                                from dwh.dim_dates
                                where date between current_date - 180 and current_date
                                  and date <= current_date
                                  and dayofweek(date) = 2
                                order by season_counter desc
                                ) b on date(event_ts::timestamp AT TIME ZONE 'UTC' at
                time zone 'Asia/Jerusalem' - interval '14 hours') between from_promo_date and to_promo_date
            where true
              and user_id not in (select distinct user_id from dwh.playtika_users)
              and user_id not in
                  (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
              and event_date >= current_date - 120
            group by 1, 2, 3
            ) A
               left join
           (select
                season_counter,
                user_id,
                max(case
                        when Product_Name = 'Daily Dash Plus' then 1
                        when sku_data ilike '{\"conditionTag\":\"J_No_Action\"}' then 1
                        when sku_data ilike '{\"conditionTag\":\"J_Roll_Dash_Max_Purchase\"}' then 1
                        when sku_data ilike '{J_Roll_ClanDashBundle_Purchase}' then 1
                        when sku_data ilike '{\"conditionTag\":\"J_Clan_Dash_bundle\"}' then 1
                        else 0
                    end) as user_type
            from dwh.sm_fact_payments a
                     left join sm_draft.SM_DIM_Products b using (sku_id, transaction_source_type_id)
                     left join (select
                                    date                              as from_promo_date,
                                    date(date + interval ' 6 days')   as to_promo_date,
                                    row_number() over (order by date) as season_counter
                                from dwh.dim_dates
                                where date between current_date - 180 and current_date
                                  and date <= current_date
                                  and dayofweek(date) = 2
                                order by season_counter desc
                                ) c on date(tran_ts::timestamp AT TIME ZONE 'UTC' at
                time zone 'Asia/Jerusalem' - interval '14 hours') between from_promo_date and to_promo_date
            where true
              and tran_date >= current_date - 120
              and tran_status_id = 2
              and is_test = 0
              and user_id > 0
              and is_playtika_user = 0
              and artificial_ind = 0
            group by 1, 2
            ) p using (season_counter, user_id)
      group by 1, 2, 3, 4
      ) AA
         left join (select
                        aa.season_counter,
                        season_start_date,
                        user_type,
                        day,
                        users,
                        sum(users) over (partition by season_start_date,user_type order by day) as running_sum_users
                    from (select
                              a.season_counter,
                              season_start_date,
                              case
                                  when p.user_id is null then 'NPU'
                                  when user_type = 1 then 'Dash Max PU'
                                  when user_type = 0 then 'PU'
                                  end                                                as user_type,
                              datediff('day', season_start_date, date(min_event_ts)) as day,
                              count(distinct a.user_id)                              as users
                          from (select
                                    season_counter,
                                    from_promo_date                                              as season_start_date,
                                    user_id,
                                    min(date(event_ts::timestamp AT TIME ZONE 'UTC' at
                                        time zone 'Asia/Jerusalem' - interval '14 hours'))::date as min_event_ts
                                from dwh.sm_fact_daily_dash_points_history a
                                         left join (select
                                                        date                              as from_promo_date,
                                                        date(date + interval ' 6 days')   as to_promo_date,
                                                        row_number() over (order by date) as season_counter
                                                    from dwh.dim_dates
                                                    where date between current_date - 180 and current_date
                                                      and date <= current_date
                                                      and dayofweek(date) = 2
                                                    order by season_counter desc
                                                    ) b on date(event_ts::timestamp AT TIME ZONE 'UTC' at
                                    time zone 'Asia/Jerusalem' -
                                              interval '14 hours') between from_promo_date and to_promo_date
                                where true
                                  and user_id not in (select distinct user_id from dwh.playtika_users)
                                  and user_id not in
                                      (select distinct
                                           user_id
                                       from dwh.sm_fact_journey_state_notifications
                                       where step_id = 539265
                                       )
                                  and event_date >= current_date - 120
                                  and current_points >= 1200
                                group by 1, 2, 3
                                ) A
                                   left join
                               (select
                                    season_counter,
                                    user_id,
                                    max(case
                                            when Product_Name = 'Daily Dash Plus' then 1
                                            when sku_data ilike '{\"conditionTag\":\"J_No_Action\"}' then 1
                                            when sku_data ilike '{\"conditionTag\":\"J_Roll_Dash_Max_Purchase\"}' then 1
                                            when sku_data ilike '{J_Roll_ClanDashBundle_Purchase}' then 1
                                            when sku_data ilike '{\"conditionTag\":\"J_Clan_Dash_bundle\"}' then 1
                                            else 0
                                        end) as user_type
                                from dwh.sm_fact_payments a
                                         left join sm_draft.SM_DIM_Products b using (sku_id, transaction_source_type_id)
                                         left join (select
                                                        date                              as from_promo_date,
                                                        date(date + interval ' 6 days')   as to_promo_date,
                                                        row_number() over (order by date) as season_counter
                                                    from dwh.dim_dates
                                                    where date between current_date - 180 and current_date
                                                      and date <= current_date
                                                      and dayofweek(date) = 2
                                                    order by season_counter desc
                                                    ) c on date(tran_ts::timestamp AT TIME ZONE 'UTC' at
                                    time zone 'Asia/Jerusalem' -
                                              interval '14 hours') between from_promo_date and to_promo_date
                                where true
                                  and tran_date >= current_date - 120
                                  and tran_status_id = 2
                                  and is_test = 0
                                  and user_id > 0
                                  and is_playtika_user = 0
                                  and artificial_ind = 0
                                group by 1, 2
                                ) p using (season_counter, user_id)
                          group by 1, 2, 3, 4
                          ) AA
                    ) bb on aa.season_counter = bb.season_counter and aa.season_start_date = bb.season_start_date and aa.user_type = bb.user_type and aa.day = bb.day
```

### 6. Daily Dash Plus Revenue Analysis
**Purpose**: Track Daily Dash Plus product revenue patterns across seasons
**Tables**: `dwh.sm_fact_payments`, `sm_draft.SM_DIM_Products`
**Validation**: Monitor Daily Dash Plus purchase behavior and revenue generation

```sql
select
    season_start_date,
    date(tran_ts::timestamp AT TIME ZONE 'UTC' at
        time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
    platform_id,
    decorated_tier_id,
    count(distinct user_id) users,
    sum(net_amount) revenue
from dwh.sm_fact_payments a
         left join sm_draft.SM_DIM_Products b using (sku_id, transaction_source_type_id)
         left join (select
                        date                                   as season_start_date,
                        date(date + interval ' 6 days')        as season_end_date,
                        row_number() over (order by date desc) as season_counter
                    from dwh.dim_dates
                    where true
                      and date >= current_date - 120
                      and date <= current_date
                      and dayofweek(date) = 2
                    ) c on date(tran_ts::timestamp AT TIME ZONE 'UTC' at
        time zone 'Asia/Jerusalem' - interval '14 hours') between season_start_date and season_end_date
where true
  and tran_status_id = 2
  and is_test = 0
  and user_id > 0
  and is_playtika_user = 0
  and artificial_ind = 0
  and tran_ts >= current_date - 60
  and Product_Name = 'Daily Dash Plus'
group by 1, 2, 3, 4
```

### 7. Daily Dash User Points Progression Analysis
**Purpose**: Analyze user point accumulation patterns with tier and platform breakdowns
**Tables**: `dwh.sm_fact_daily_dash_points_history`
**Validation**: Track point progression patterns across different user segments

```sql
select
    season_counter,
    case
        when tier_id <= 0 or tier_id is null then 'No tier'
        else tier_id::varchar
        end                                            as tier_group,
    case
        when platform_id <= 0 or platform_id is null then 'No Platform'
        else platform_id::varchar
        end                                            as platform_group,
    percentile_disc(0.50) within GROUP (ORDER BY max_points ASC)
    over (partition BY season_counter,tier_group,platform_group) AS Median,
    percentile_disc(0.75) within GROUP (ORDER BY max_points ASC)
    over (partition BY season_counter,tier_group,platform_group) AS p75,
    percentile_disc(0.95) within GROUP (ORDER BY max_points ASC)
    over (partition BY season_counter,tier_group,platform_group) AS p95,
    percentile_disc(0.99) within GROUP (ORDER BY max_points ASC)
    over (partition BY season_counter,tier_group,platform_group) AS p99
from (select
          season_counter,
          user_id,
          tier_id,
          platform_id,
          max(current_points) as max_points
      from dwh.sm_fact_daily_dash_points_history a
               left join (select
                              date                              as from_promo_date,
                              date(date + interval ' 6 days')   as to_promo_date,
                              row_number() over (order by date) as season_counter
                          from dwh.dim_dates
                          where date between current_date - 180 and current_date
                            and date <= current_date
                            and dayofweek(date) = 2
                          order by season_counter desc
                          ) b on date(event_ts::timestamp AT TIME ZONE 'UTC' at
          time zone 'Asia/Jerusalem' - interval '14 hours') between from_promo_date and to_promo_date
      where true
        and event_date >= current_date - 120
        and user_id not in (select distinct user_id from dwh.playtika_users)
        and user_id not in
            (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
      group by 1, 2, 3, 4
      ) A
limit 1 over(partition by season_counter,tier_group,platform_group order by season_counter)
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `general-daily-dash.md` - Complete Daily Dash business context