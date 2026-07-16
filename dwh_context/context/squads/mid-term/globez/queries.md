# Globez - SQL Queries

**Note**: This file contains actual SQL queries extracted from the New Mid-term dashboard.twbx for Globez analysis and investigations.

## Query Inventory

### 1. Collection Set Completion Analysis
**Purpose**: Analyze bundles required to finish Globez collection sets with percentile distribution
**Tables**: `dwh.sm_fact_lootbox_history_hero`, `dwh.fact_sm_goods_service_data`, `sm_draft.globez_dates`
**Validation**: Track bundle creation to collection completion patterns

```sql
select distinct
    season,
    completed_collection_set_name,
    bonus_rn,
    percentile_disc(0.25) within GROUP (ORDER BY bundels_to_finish_set ASC)
    over (partition BY season,completed_collection_set_name,bonus_rn) AS p25,
    percentile_disc(0.50) within GROUP (ORDER BY bundels_to_finish_set ASC)
    over (partition BY season,completed_collection_set_name,bonus_rn) AS Median,
    percentile_disc(0.75) within GROUP (ORDER BY bundels_to_finish_set ASC)
    over (partition BY season,completed_collection_set_name,bonus_rn) AS p75,
    percentile_disc(0.95) within GROUP (ORDER BY bundels_to_finish_set ASC)
    over (partition BY season,completed_collection_set_name,bonus_rn) AS p95
from (select
          a.season,
          box_user_id,
          completed_collection_set_name,
          bonus_rn,
          count(event_type) as bundels_to_finish_set
      from (select
                a.*,
                b.completed_collection_set_name,
                b.bonus_ts,
                dense_rank() over (partition by a.season,box_user_id,completed_collection_set_name order by bonus_ts) as bonus_rn
            from (select
                      season,
                      event_type,
                      event_ts,
                      box_user_id
                  from dwh.sm_fact_lootbox_history_hero a
                           join (select *
                                 from sm_draft.globez_dates
                                 ORDER BY start_promo_date desc
                                 limit 5
                                 ) f on date(a.event_ts::timestamp AT TIME ZONE 'UTC' at
                      time zone 'Asia/Jerusalem' -
                                interval '14 hours') between f.start_promo_date and f.end_promo_date - 1
                  where true
                    and event_date >= current_date - 60
--                     and box_user_id = 151325269863052
--                     and box_user_id = 154000075117194
                    and box_box_type = 'slotoheroes_globez'
                    and event_type = 'BOX_CREATED'
                  ) A
                     left join (select
                                    season,
                                    bonus_ts,
                                    user_id,
                                    completed_collection_set_name
                                from dwh.fact_sm_goods_service_data a
                                         join (select *
                                               from sm_draft.globez_dates
                                               ORDER BY start_promo_date desc
                                               limit 5
                                               ) f
                                              on date(a.bonus_ts::timestamp AT TIME ZONE 'UTC' at
                                                  time zone 'Asia/Jerusalem' -
                                                            interval '14 hours') between f.start_promo_date and f.end_promo_date - 1
                                where true
                                  and event_date >= current_date - 60
                                  and completed_collection_set_name is not null
                                  and sku_id = 142
--                                   and user_id = 151325269863052
--                                   and user_id = 154000075117194

                                ) b on a.season = b.season and a.box_user_id = b.user_id and a.event_ts <= b.bonus_ts
            ) A
      where completed_collection_set_name is not null
      and bonus_rn = 1
      group by 1, 2, 3, 4
      ) A
```

### 2. Globez Gems Upgrade Ratio Performance Analysis  
**Purpose**: Analyze gems upgrade ratios and payout performance by user gems usage patterns
**Tables**: `dwh.fact_sm_spin_history_kafka`, `agg.sm_agg_daily_promotion_users_spins`, `dwh.sm_fact_lootbox_history_hero`, `sm_draft.globez_dates`
**Validation**: Correlate gems usage with spinning behavior and payout patterns

```sql
select
    a.season,
    a.start_promo_date,
    a.datediff,
    gems_ratio,

    count(a.user_id) over (partition by a.season,a.datediff,gems_ratio)                 per_gems_users,
    median(cum_bonus / cum_ante_bet) over (partition by a.season,a.datediff,gems_ratio) per_gems_med,
    avg(cum_bonus / cum_ante_bet) over (partition by a.season,a.datediff,gems_ratio)    per_gems_avg_po,

    percentile_disc(0.75) within GROUP (ORDER BY cum_bonus / cum_ante_bet ASC)
    over (partition by a.season,a.datediff,gems_ratio) AS                               per_gems_p75_po,
    percentile_disc(0.90) within GROUP (ORDER BY cum_bonus / cum_ante_bet ASC)
    over (partition by a.season,a.datediff,gems_ratio) AS                               per_gems_p90_po,
    percentile_disc(0.95) within GROUP (ORDER BY cum_bonus / cum_ante_bet ASC)
    over (partition by a.season,a.datediff,gems_ratio) AS                               per_gems_p95_po

from (select
          dates_users.user_id,
          dates_users.season,
          dates_users.start_promo_date,
          gems_ratio,
          datediff('day', dates_users.start_promo_date, dates_users.date)                       datediff,
          sum(coalesce(ante_bet_amount, 0))
          over (partition by dates_users.user_id, dates_users.season order by dates_users.date) cum_ante_bet,
          sum(coalesce(bonus_amount, 0))
          over (partition by dates_users.user_id, dates_users.season order by dates_users.date) cum_bonus
      from (select
                date,
                b.season,
                b.start_promo_date,
                user_id
            from (select * from dwh.dim_dates where date between current_date - 60 and current_date) a
                     join sm_draft.globez_dates b on date between start_promo_date and end_promo_date - 1
                     join (select distinct
                               user_id,
                               season,
                               start_promo_date
                           from dwh.fact_sm_spin_history_kafka
                                    join sm_draft.globez_dates b on date(spin_ts::timestamp AT TIME ZONE 'UTC' at
                               time zone 'Asia/Jerusalem' -
                                         interval '14 hours') between start_promo_date and end_promo_date - 1
                           where start_promo_date >= current_date - 60
                             and machine_type_id in (13626)
                           ) users using (start_promo_date)
            ) dates_users
               left join (select
                              user_id,
                              season,
                              start_promo_date,
                              date(spin_ts::timestamp AT TIME ZONE 'UTC' at
                                  time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
                              sum(win_amount)                                          bonus_amount
                          from dwh.fact_sm_spin_history_kafka
                                   join sm_draft.globez_dates b on date(spin_ts::timestamp AT TIME ZONE 'UTC' at
                              time zone 'Asia/Jerusalem' -
                                        interval '14 hours') between start_promo_date and end_promo_date - 1
                          where start_promo_date >= current_date - 60
                            and machine_type_id in (13626)
                          group by 1, 2, 3, 4
                          ) A on dates_users.user_id = a.user_id and dates_users.date = a.promo_date
               left join (select
                              user_id,
                              season,
                              b.start_promo_date,
                              a.start_promo_date               promo_date,
                              sum(antebet_amounts_slotoheroes) ante_bet_amount
                          from agg.sm_agg_daily_promotion_users_spins a
                                   join sm_draft.globez_dates b
                                        on a.start_promo_date between b.start_promo_date and end_promo_date - 1
                          where b.start_promo_date >= current_date - 60
                            and slotoheros_antebet_spins_amount >> 0
                          group by 1, 2, 3, 4
                          ) B on dates_users.user_id = b.user_id and dates_users.date = b.promo_date
               left join (select
                              season,
                              user_id,
                              bundles_upgraded,
                              bundles_purchased,
                              case
                                  when bundles_upgraded / bundles_purchased = 0 then 0
                                  when bundles_upgraded / bundles_purchased <= 0.25 then 0.25
                                  when bundles_upgraded / bundles_purchased <= 0.5 then 0.50
                                  when bundles_upgraded / bundles_purchased <= 0.75 then 0.75
                                  when bundles_upgraded / bundles_purchased <= 0.99 then 0.99
                                  when bundles_upgraded = bundles_purchased then 1 end gems_ratio
                          from (select
                                    season,
                                    box_user_id                                                             user_id,
                                    count(distinct box_guid)                                                bundles_purchased,
                                    count(distinct case when event_type = 'BOX_UPGRADED' then box_guid end) bundles_upgraded
                                from dwh.sm_fact_lootbox_history_hero
                                         join sm_Draft.globez_dates b on date(event_ts::timestamp AT TIME ZONE 'UTC' at
                                    time zone 'Asia/Jerusalem' -
                                              interval '14 hours') between b.start_promo_date and b.end_promo_date - 1
                                where 1 = 1
                                  and event_type in ('BOX_CREATED', 'BOX_UPGRADED')
                                  and event_source_type = 'payment'
                                  and box_box_type in ('slotoheroes_globez')

                                  and start_promo_date >= current_date - 60
                                group by 1, 2
                                ) A
                          ) C on a.user_id = c.user_id and a.season = c.season
      ) A
where cum_ante_bet >> 0
limit 1 over (partition by a.season,a.datediff,gems_ratio order by a.season,a.datediff)
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `general-mid-term.md` - Complete Mid-term business context