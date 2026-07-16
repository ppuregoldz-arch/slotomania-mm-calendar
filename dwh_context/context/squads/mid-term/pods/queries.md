# Pods - SQL Queries

**Note**: This file contains actual SQL queries extracted from the New Mid-term dashboard.twbx for Pods analysis and investigations.

## Query Inventory

### 1. Pods Payout Analysis by Gems Usage
**Purpose**: Analyze payout percentiles and user behavior based on gems usage for pod opening
**Tables**: `dwh.sm_fact_mega_win_party_history`, `dwh.sm_fact_payments`, `dwh.fact_sm_bonus_history`, `dwh.fact_sm_spin_history_kafka`
**Validation**: Compare payout patterns between users who open pods with gems vs normal collection

```sql
select
    a.season,
    gems_opened_pods_share,
    pass_pu,
    percentile_disc(0.50) within
        GROUP (ORDER BY (bonus / ante_bet) ASC)
    over (partition by gems_opened_pods_share, pass_pu, a.season) AS                    P_50,
    avg(bonus / ante_bet) over (partition by gems_opened_pods_share, pass_pu, a.season) avg_payout,
    percentile_disc(0.25) within
        GROUP (ORDER BY (bonus / ante_bet) ASC)
    over (partition by gems_opened_pods_share, pass_pu, a.season) AS                    P_25,
    percentile_disc(0.75) within
        GROUP (ORDER BY (bonus / ante_bet) ASC)
    over (partition by gems_opened_pods_share, pass_pu, a.season) AS                    P_75,
    percentile_disc(0.95) within
        GROUP (ORDER BY (bonus / ante_bet) ASC)
    over (partition by gems_opened_pods_share, pass_pu, a.season) AS                    P_95,
    percentile_disc(0.99) within
        GROUP (ORDER BY (bonus / ante_bet) ASC)
    over (partition by gems_opened_pods_share, pass_pu, a.season) AS                    P_99,
    sum(bonus) over (partition by gems_opened_pods_share, pass_pu, a.season) /
    sum(ante_bet) over (partition by gems_opened_pods_share, pass_pu, a.season)         total_po,
    count(a.user_id) over (partition by gems_opened_pods_share, pass_pu, a.season)      users,
    count(case when coalesce(bonus, 0) = 0 then a.user_id end)
    over (partition by gems_opened_pods_share, pass_pu, a.season)                       users_with_no_payout
from (select
          a.user_id, pass_pu, a.season,
          case
              when opened_with_gems / rec < 0.25 then '0 - 0.25'
              when opened_with_gems / rec < 0.5 then '0.25 - 0.5'
              when opened_with_gems / rec < 0.75 then '0.5 - 0.75'
              when opened_with_gems / rec <= 1 then '0.75 - 1' end gems_opened_pods_share
      from (select
                a.user_id, case when c.user_id is not null then true else false end pass_pu,
                a.season,
                count(distinct a.chest_id)                                          rec,
                sum(activated)                                                      activated,
                sum(opened_with_gems)                                               opened_with_gems,
                sum(collected)                                                      collected
            from (select
                      user_id, chest_id,
                      timestampadd(day, 1, date_trunc('week', timestampadd(day, -1,
                                                                           date(timestamp::timestamp AT TIME ZONE
                                                                                'UTC' at
                                                                               time zone 'Asia/Jerusalem' -
                                                                                         interval '14 hours')))) as season
                  from dwh.sm_fact_mega_win_party_history
                  where status = 'RECEIVED'
                    and timestamp >= current_date - 30
                 )          A
                left join (select
                               user_id, chest_id, max(case when status = 'ACTIVATED' then 1 else 0 end) activated,
                               max(case when status = 'IMMEDIATELY_UNLOCK' then 1 else 0 end)           opened_with_gems,
                               max(case when status = 'COLLECTED' then 1 else 0 end)                    collected
                           from dwh.sm_fact_mega_win_party_history
                           group by 1, 2
                          ) B using (user_id, chest_id)
                left join (SELECT distinct
                               user_id,
                               timestampadd(day, 1, date_trunc('week', timestampadd(day, -1,
                                                                                    date(tran_ts::timestamp AT TIME ZONE
                                                                                         'UTC' at
                                                                                        time zone 'Asia/Jerusalem' -
                                                                                                  interval '14 hours')))) as season
                           from dwh.sm_fact_payments              a
                               left join sm_draft.SM_DIM_Products b
                                                 on a.sku_id = b.sku_id and
                                                    a.transaction_source_type_id = b.transaction_source_type_id
                           where 1 = 1
                             and tran_status_id = 2
                             and artificial_ind = 0
                             and is_test = 0
                             and user_id > 0
                             and Product_Name = 'Mega Pods Pass'
                             and tran_ts >= current_date - 30
                          ) C on a.user_id = c.user_id and a.season = c.season
            group by 1, 2, 3
           ) A
      --       where collected >= 3
      /*exclude abusers*/
      where a.user_id not in (select distinct user_id
                              from dwh.fact_sm_sessions_kafka
                              where session_creation_ts >= current_date - 30
                                  and
                                    client_type_id in
                                    (340, 341, 342, 346, 347, 348, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363,
                                     364, 365, 366, 368, 397, 398, 399, 401, 402, 403, 405, 406, 407, 413, 414, 415,
                                     420, 421, 422)
                                 or version = '6.26.6'
                             )
     )          A
    left join
              (select

                   a.user_id, a.season, coalesce(bar_bonus, 0) + coalesce(chest_bonus, 0) bonus
               from (select
                         user_id,
                         timestampadd(day, 1, date_trunc('week', timestampadd(day, -1,
                                                                              date(bonus_ts::timestamp AT TIME ZONE
                                                                                   'UTC' at
                                                                                  time zone 'Asia/Jerusalem' -
                                                                                            interval '14 hours')))) as season,
                         sum(bonus_amount)                                                                             bar_bonus
                     from dwh.fact_sm_bonus_history
                     where bonus_type_id = 390
                       and bonus_ts >= current_date - 30
                       and source = 'megaPodBar'
                     group by 1, 2
                    )          A
                   left join (select
                                  a.user_id,
                                  a.season,
                                  sum(bonus_amount) chest_bonus
                              from (select
                                        user_id, chest_id,
                                        timestampadd(day, 1, date_trunc('week', timestampadd(day, -1,
                                                                                             date(timestamp::timestamp AT TIME ZONE
                                                                                                  'UTC' at
                                                                                                 time zone
                                                                                                  'Asia/Jerusalem' -
                                                                                                  interval '14 hours')))) as season
                                    from dwh.sm_fact_mega_win_party_history
                                    where status = 'RECEIVED'
                                      and timestamp >= current_date - 30
                                   )          A
                                  left join (select
                                                 user_id, chest_id, sum(sku_data_amount) bonus_amount
                                             from dwh.sm_fact_mega_win_party_history
                                             where status = 'COLLECTED'
                                               and timestamp >= current_date - 30
                                             group by 1, 2
                                            ) B using (chest_id)
                              group by 1, 2
                             ) B using (user_id, season)
              ) B using (user_id, season)
    left join (select
                   user_id,
                   timestampadd(day, 1, date_trunc('week', timestampadd(day, -1,
                                                                        date(spin_ts::timestamp AT TIME ZONE
                                                                             'UTC' at
                                                                            time zone 'Asia/Jerusalem' -
                                                                                      interval '14 hours')))) as season,
                   sum(antebet_amounts_mega_pod)                                                                 ante_bet
               from dwh.fact_sm_spin_history_kafka a
               where spin_ts >= current_date - 30
               group by 1, 2
              ) C using (user_id, season)
limit 1 over (partition by gems_opened_pods_share, pass_pu, a.season order by gems_opened_pods_share)
```

### 2. Pods Antebet Analysis by Purchase Status
**Purpose**: Analyze antebet spending patterns across different game features for purchasers vs non-purchasers
**Tables**: `fact_sm_spin_history_kafka`, `agg_sm_daily_promotion_stats`
**Validation**: Track antebet distribution across Mega Pods, Scapes, Heroes, and Quest features

```sql
select
    spin_date,
    pu,
    percentile_cont(0.25) within group (order by antebet_perc) over (partition by spin_date,pu) antebet_p25,
    percentile_cont(0.50) within group (order by antebet_perc) over (partition by spin_date,pu) antebet_p50,
    percentile_cont(0.75) within group (order by antebet_perc) over (partition by spin_date,pu) antebet_p75,
    percentile_cont(0.25) within group (order by raw_mp) over (partition by spin_date,pu)       mp_p25,
    percentile_cont(0.50) within group (order by raw_mp) over (partition by spin_date,pu)       mp_p50,
    percentile_cont(0.75) within group (order by raw_mp) over (partition by spin_date,pu)       mp_p75,
    percentile_cont(0.25) within group (order by raw_scapes) over (partition by spin_date,pu)   scapes_p25,
    percentile_cont(0.50) within group (order by raw_scapes) over (partition by spin_date,pu)   scapes_p50,
    percentile_cont(0.75) within group (order by raw_scapes) over (partition by spin_date,pu)   scapes_p75,
    percentile_cont(0.25) within group (order by raw_heroes) over (partition by spin_date,pu)   heroes_p25,
    percentile_cont(0.50) within group (order by raw_heroes) over (partition by spin_date,pu)   heroes_p50,
    percentile_cont(0.75) within group (order by raw_heroes) over (partition by spin_date,pu)   heroes_p75,
    percentile_cont(0.25) within group (order by raw_quest) over (partition by spin_date,pu)   quest_p25,
    percentile_cont(0.50) within group (order by raw_quest) over (partition by spin_date,pu)   quest_p50,
    percentile_cont(0.75) within group (order by raw_quest) over (partition by spin_date,pu)   quest_p75
from (select
          spin_date,
          pu,
          coalesce(tot_antebet, 0) / total_bet as antebet_perc,
          coalesce(raw_mp, 0) / tot_raw        as raw_mp,
          coalesce(raw_scapes, 0) / tot_raw    as raw_scapes,
          coalesce(raw_heroes, 0) / tot_raw    as raw_heroes,
          coalesce(raw_quest, 0) / tot_raw     as raw_quest
      from (select
                spin_date,
                user_id,
                pu,
                sum(total_bet)                                total_bet,
                sum(antebet)                                  tot_antebet,
                sum(raw_bet)                                  tot_raw,
                sum(case when is_mp = 1 then raw_bet end)     raw_mp,
                sum(case when is_scapes = 1 then raw_bet end) raw_scapes,
                sum(case when is_heroes = 1 then raw_bet end) raw_heroes,
                sum(case when is_quest = 1 then raw_bet end) raw_quest,
                count(*)                                      spins
            from (select
                      a.user_Id,
                      case when b.user_id is not null then 1 else 0 end           as pu,
                      spin_date,
                      bet_amount - (coalesce(raw_bet_amount, bet_amount))            antebet,
                      bet_amount                                                  as total_bet,
                      coalesce(raw_bet_amount, bet_amount)                           raw_bet,
                      case when antebet_amounts_mega_pod > 0 then 1 else 0 end    as is_mp,
                      case when antebet_amounts_scapes > 0 then 1 else 0 end      as is_scapes,
                      case when antebet_amounts_slotoheroes > 0 then 1 else 0 end as is_heroes,
                      case when antebet_amounts_slotoquest > 0 then 1 else 0 end  as is_quest
                  from fact_sm_spin_history_kafka a
                           left join (select
                                          user_id
                                      from agg_sm_daily_promotion_stats
                                      where gross_rev > 0
                                        and promo_date >= current_date - 30
                                      group by 1
                                      ) b using (user_Id)
                  where bet_amount > 0
                    and spin_date >= current_date - 90
                  ) a
            group by 1, 2, 3
            ) a
      where spins >= 50
      ) a
limit 1 over (partition by spin_date,pu order by spin_date)
```

### 3. Pods Collection Status Analysis
**Purpose**: Analyze how pods are collected - through normal completion, gems unlock, or season end
**Tables**: `sm_fact_mega_win_party_history`
**Validation**: Track collection method distribution and timing patterns

```sql
select
    date(timestamp::timestamp AT TIME ZONE 'UTC' at
        time zone 'Asia/Jerusalem' - interval '14 hours') as                  promo_date,
    chest_type,
    case when end_season=1 then 'COLLECTED_SEASON_END_REWARD' when gem_opened=1 then 'IMMEDIATELY_UNLOCK'  else 'COLLECTED' end status,
    count(*) pods
from (select chest_id,
             chest_type,
             max(case when status='IMMEDIATELY_UNLOCK' then 1 else 0 end) gem_opened,
             max(case when status='COLLECTED_SEASON_END_REWARD' then 1 else 0 end) end_season,
             min(timestamp) timestamp
      from sm_fact_mega_win_party_history
      where timestamp >= current_date - 60
        and status in ('COLLECTED', 'COLLECTED_SEASON_END_REWARD', 'IMMEDIATELY_UNLOCK')
      group by 1, 2
     ) a
group by grouping sets ((1,3), (1,2,3))
```

### 4. Pods Payout Analysis with Iraq Special Tracking
**Purpose**: Detailed payout analysis by day in season with special Iraq user tracking
**Tables**: `agg.sm_agg_daily_promotion_users_spins`, `dwh.fact_sm_spin_history_kafka`, `dwh.fact_sm_bonus_history`, `dwh.sm_user_profile`
**Validation**: Track payout patterns across season progression with regional focus

```sql
select
    week,
    day_in_season,
    is_iq,
--     gems_ratio,
    percentile_cont(0.25) within group (order by wins / antebet)
    over (partition by week, day_in_season,is_iq) payout_q1,
    percentile_cont(0.50) within group (order by wins / antebet)
    over (partition by week, day_in_season,is_iq) payout_q2,
    percentile_cont(0.75) within group (order by wins / antebet)
    over (partition by week, day_in_season,is_iq) payout_q3,
    percentile_cont(0.99) within group (order by wins / antebet)
    over (partition by week, day_in_season,is_iq) payout_q4,
avg(wins / antebet)  over (partition by week, day_in_season,is_iq) as avg_po
from (select
          b.user_id,
          case when u.user_id is not null then 1 else 0 end as               is_iq,
--           gems_ratio,
          b.week,
          a.date,
          datediff('day', b.week, a.date)                                    day_in_season,
          sum(antebet) over (partition by b.user_id, b.week order by a.date) antebet,
          sum(wins) over (partition by b.user_id, b.week order by a.date)    wins
      from dwh.dim_dates a
               join
           (select
                user_id,
--                              timestampadd(day, 1, date_trunc('week', timestampadd(day,-1, start_promo_date))) week, -- if startd date is Tuesday
                date_trunc('week', start_promo_date) week, -- if monday
                min(start_promo_Date)                min_date
            from agg.sm_agg_daily_promotion_users_spins
            where start_promo_date >= current_date - 60
              and mega_pod_antebet_amount > 0
         --     and user_id = 250
            group by 1, 2
            ) b on a.date >= current_date - 60 and a.date >= min_date and a.date < b.week + 7
               and a.date <= current_date
               left join
           (select
                user_id,
                date(spin_ts::timestamp AT TIME ZONE 'UTC' at
                    time zone 'Asia/Jerusalem' - interval '14 hours')                start_promo_date,
                sum(antebet_amounts_mega_pod) antebet
            from dwh.fact_sm_spin_history_kafka
            where spin_ts >= current_date - 60
              and antebet_amounts_mega_pod > 0
        --    and user_id = 250
            group by 1, 2
            ) c on b.user_id = c.user_id and a.date = c.start_promo_date
               left join (select
                              user_id,
                              date(bonus_ts::timestamp AT TIME ZONE 'UTC' at
                                  time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
                              sum(bonus_amount)                                        wins
                          from dwh.fact_sm_bonus_history
                          where bonus_type_id = 390
                            and bonus_ts >= current_date - 60
                          -- and user_id = 250
                          group by 1, 2
                          ) d on b.user_id = d.user_id and a.date = d.promo_date
               left join (select *
                          from dwh.sm_user_profile
                          where country_name ilike '%iraq%'
                          ) u on b.user_id = u.user_id
      ) a
where true
  and wins > 0
limit 1 over (partition by week, day_in_season,is_iq order by week)
```

### 5. Pods Purchase Analysis
**Purpose**: Track Pods-related purchases including Pass purchases by season and pricing
**Tables**: `dwh.sm_fact_payments`, `sm_draft.SM_DIM_Products`
**Validation**: Monitor purchase patterns and revenue from Pods-related products

```sql
SELECT
    season_start_date,
    date(tran_ts::timestamp AT TIME ZONE 'UTC' at
        time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
    Product_Name,
price,
    count(distinct user_id) as users,
    sum(net_amount) as net_amount
from dwh.sm_fact_payments a
         left join sm_draft.SM_DIM_Products b
                   on a.sku_id = b.sku_id and a.transaction_source_type_id = b.transaction_source_type_id
left join (select date                                   as season_start_date,
        date(date + interval ' 6 days')        as season_end_date,
        row_number() over (order by date desc) as season_counter
 from dwh.dim_dates
 where true
   and date >= current_date - 120
   and date <= current_date
   and dayofweek(date) = 2
 ) season on date(tran_ts::timestamp AT TIME ZONE 'UTC' at
        time zone 'Asia/Jerusalem' - interval '14 hours') between season_start_date and season_end_date
where 1 = 1
  and tran_status_id = 2
  and artificial_ind = 0
  and is_test = 0
  and user_id > 0
  and tran_ts >= current_date - 60
and Product_Name ilike '%pods%'
group by 1,2,3,4
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `general-mid-term.md` - Complete Mid-term business context