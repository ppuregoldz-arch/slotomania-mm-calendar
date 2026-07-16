# Winovate - SQL Queries

**Note**: This file contains actual SQL queries extracted from the New Mid-term dashboard.twbx for Winovate analysis and investigations.

## Query Inventory

### 1. Winovate Tokens Flow Analysis
**Purpose**: Track tokens earned vs tokens spent in Winovate renovation system
**Tables**: `dwh.sm_fact_scapes_events`, `sm_draft.winovate_dates`  
**Validation**: Monitor token economy balance and daily flow patterns

```sql
select 
    tokens_in.start_promo_date as season,
    tokens_in.promo_date,
    total_tokens_in,
    total_tokens_out
from (select
          start_promo_date,
          date(event_ts::timestamp AT TIME ZONE 'UTC' at
              time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
          sum(source_amount) * -1 as total_tokens_in
      from dwh.sm_fact_scapes_events a
               join (select *,
                            row_number() over (order by start_promo_date desc) index
                     from sm_draft.winovate_dates) b
                    on date(event_ts::timestamp AT TIME ZONE 'UTC' at
                        time zone 'Asia/Jerusalem' - interval '14 hours') 
                        between b.start_promo_date and b.end_promo_date - 1 
                        and index <= 10
      where true
        and event_type = 'IncreaseTokens'
        and event_ts >= '2025-12-01 12:00'
      group by 1, 2
      ) tokens_in
         left join (select
                        start_promo_date,
                        date(event_ts::timestamp AT TIME ZONE 'UTC' at
                            time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
                        sum(mission_price) as total_tokens_out
                    from dwh.sm_fact_scapes_events a
                             join (select *,
                                          row_number() over (order by start_promo_date desc) index
                                   from sm_draft.winovate_dates) b
                                  on date(event_ts::timestamp AT TIME ZONE 'UTC' at
                                      time zone 'Asia/Jerusalem' - interval '14 hours') 
                                      between b.start_promo_date and b.end_promo_date - 1 
                                      and index <= 10
                    where true
                      and event_type = 'CompleteMission'
                      and event_ts >= '2025-12-01 12:00'
                    group by 1, 2
                    ) tokens_out 
                   on tokens_in.start_promo_date = tokens_out.start_promo_date 
                   and tokens_in.promo_date = tokens_out.promo_date;
```

### 2. Winovate Performance by Room & Recompletion
**Purpose**: Analyze user performance metrics by max room reached and recompletion status
**Tables**: `agg.sm_agg_daily_promotion_users_spins`, `dwh.sm_fact_scapes_events`, `sm_draft.winovate_dates`
**Validation**: Track payout ratios and user distribution across room levels

```sql
select
    a.season,
    season_date,
    max_room,
    recompletion,
    upgrade_range,
    MEDIAN(user_po) over (partition by upgrade_range,a.season,max_room,recompletion) median_po,
    COUNT(a.user_id) over (partition by upgrade_range,a.season,max_room,recompletion) user_count
from (select
          a.user_id,
          a.season,
          a.start_promo_date as season_date,
          max_room,
          case when recompletion > 1 then 1 else 0 end as recompletion,
          SUM(scapes_ante) ante,
          SUM(coalesce(wins, 0)) wins,
          SUM(coalesce(wins, 0)) / SUM(scapes_ante) user_po
      from (SELECT
                user_id,
                season,
                b.start_promo_date,
                end_promo_date,
                sum(scapes_antebet_amount) scapes_ante
            From agg.sm_agg_daily_promotion_users_spins A
                     JOIN sm_draft.winovate_dates b
                          on A.start_promo_date between b.start_promo_date and end_promo_date - 1
            where scapes_antebet_amount > 0
              and a.start_promo_date >= current_date - 90
            group by 1, 2, 3, 4
            ) a
               JOIN (SELECT
                         user_id,
                         season,
                         max(coalesce(max_room_unlocked, 0)) as max_room,
                         count(distinct season_id) as recompletion,
                         sum(coalesce(wins, 0)) as wins
                     FROM dwh.sm_fact_scapes_events A
                              JOIN sm_draft.winovate_dates b
                                   on date(event_ts::timestamp AT TIME ZONE 'UTC' at
                                       time zone 'Asia/Jerusalem' -
                                             interval '14 hours') between b.start_promo_date and b.end_promo_date - 1
                     where event_ts >= current_date - 90
                     group by 1, 2
                     ) B USING (user_id, season)
      group by 1, 2, 3, 4, 5
      ) a
where ante > 0;
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `business-context.md` - Winovate business context
