# Figz - SQL Queries

**Note**: This file contains actual SQL queries extracted from the New Mid-term dashboard.twbx for Figz analysis and investigations.

## Query Inventory

### 1. Comprehensive Figz & Globez Metrics Analysis
**Purpose**: Compare Figz and Globez feature performance across multiple KPIs including DAU, spinners, bundle purchasers
**Tables**: `agg.agg_sm_sessions_stats`, `agg.agg_sm_daily_promotion_stats`, `dwh.fact_sm_spin_history_kafka`, `dwh.sm_fact_internal_purchase_balance_update_hero_coins`, `dwh.fact_sm_goods_service_data`, `sm_draft.figz_dates`, `sm_draft.globez_dates`
**Validation**: Cross-feature comparison with unified metrics structure

```sql
SELECT *
FROM (WITH
          ------------------------------------------------------
          -- FIGZ DATES
          ------------------------------------------------------
          figz_dates AS (SELECT *
                         FROM sm_draft.figz_dates
                         ORDER BY date_from DESC
                         LIMIT 3
              ),

          ------------------------------------------------------
          -- FIGZ METRICS
          ------------------------------------------------------
          figz_dau AS (SELECT
                           f.event,
                           f.date_from,
                           COUNT(DISTINCT s.user_id) AS dau
                       FROM agg.agg_sm_sessions_stats s
                                JOIN figz_dates f
                                     ON s.session_creation_ts BETWEEN f.ts_from AND f.ts_to
                       GROUP BY 1, 2
              ),

          figz_spinners AS (SELECT
                                f.event,
                                COUNT(DISTINCT p.user_id) AS spinners
                            FROM agg.agg_sm_daily_promotion_stats p
                                     JOIN figz_dates f
                                          ON p.promo_date BETWEEN f.date_from AND f.date_to - 1
                            WHERE p.spins >> 0
                            GROUP BY 1
              ),

          figz_antebet AS (SELECT
                               f.event,
                               COUNT(DISTINCT sh.user_id) AS antebet_spinners
                           FROM dwh.fact_sm_spin_history_kafka sh
                                    JOIN figz_dates f
                                         ON sh.spin_ts BETWEEN f.ts_from AND f.ts_to
                           WHERE sh.antebet_amounts_slotoheroes >> 0
                           GROUP BY 1
              ),

          figz_purchasers AS (SELECT
                                  f.event,
                                  COUNT(DISTINCT hp.user_id) AS bundle_purchasers
                              FROM dwh.sm_fact_internal_purchase_balance_update_hero_coins hp
                                       JOIN figz_dates f
                                            ON hp.timestamp BETWEEN f.ts_from AND f.ts_to
                              where delta << 0
                              GROUP BY 1
              ),

          figz_finishers AS (SELECT
                                 f.event,
                                 COUNT(DISTINCT g.user_id) AS set_finishers
                             FROM dwh.fact_sm_goods_service_data g
                                      JOIN figz_dates f
                                           ON g.reward_ts BETWEEN f.ts_from AND f.ts_to
                             WHERE g.completed_collection_set_name IS NOT NULL
                               AND g.sku_id = 142
                             GROUP BY 1
              ),

          figz AS (SELECT
                       d.event,
                       'Figz' AS feature,
                       d.date_from,
                       d.dau,
                       s.spinners,
                       a.antebet_spinners,
                       p.bundle_purchasers,
                       f.set_finishers
                   FROM figz_dau d
                            JOIN figz_spinners s USING (event)
                            JOIN figz_antebet a USING (event)
                            JOIN figz_purchasers p USING (event)
                            JOIN figz_finishers f USING (event)
              ),

          ------------------------------------------------------
          -- GLOBEZ DATES
          ------------------------------------------------------
          globez_dates AS (SELECT *
                           FROM sm_draft.globez_dates
                           ORDER BY start_promo_date DESC
                           LIMIT 3
              ),

          ------------------------------------------------------
          -- GLOBEZ METRICS
          ------------------------------------------------------
          globez_dau AS (SELECT
                             g.season,
                             g.start_promo_date,
                             COUNT(DISTINCT s.user_id) AS dau
                         FROM agg.agg_sm_sessions_stats s
                                  JOIN globez_dates g
                                       ON DATE((s.session_creation_ts AT TIME ZONE 'UTC')
                                           AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours')
                                           BETWEEN g.start_promo_date AND g.end_promo_date - 1
                         GROUP BY 1, 2
              ),

          globez_spinners AS (SELECT
                                  g.season,
                                  COUNT(DISTINCT p.user_id) AS spinners
                              FROM agg.agg_sm_daily_promotion_stats p
                                       JOIN globez_dates g
                                            ON p.promo_date BETWEEN g.start_promo_date AND g.end_promo_date - 1
                              WHERE p.spins >> 0
                              GROUP BY 1
              ),

          globez_antebet AS (SELECT
                                 g.season,
                                 COUNT(DISTINCT sh.user_id) AS antebet_spinners
                             FROM dwh.fact_sm_spin_history_kafka sh
                                      JOIN globez_dates g
                                           ON DATE((sh.spin_ts AT TIME ZONE 'UTC')
                                               AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours')
                                               BETWEEN g.start_promo_date AND g.end_promo_date - 1
                             WHERE sh.antebet_amounts_slotoheroes >> 0
                             GROUP BY 1
              ),

          globez_purchasers AS (SELECT
                                    g.season,
                                    COUNT(DISTINCT hp.user_id) AS bundle_purchasers
                                FROM dwh.sm_fact_internal_purchase_balance_update_hero_coins hp
                                         JOIN globez_dates g
                                              ON DATE((hp.timestamp AT TIME ZONE 'UTC')
                                                  AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours')
                                                  BETWEEN g.start_promo_date AND g.end_promo_date - 1
                                where delta << 0

                                GROUP BY 1
              ),


          globez_finishers AS (SELECT
                                   g.season,
                                   COUNT(DISTINCT f.user_id) AS set_finishers
                               FROM dwh.fact_sm_goods_service_data f
                                        JOIN globez_dates g
                                             ON DATE((f.reward_ts AT TIME ZONE 'UTC')
                                                 AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours')
                                                 BETWEEN g.start_promo_date AND g.end_promo_date - 1
                               WHERE f.completed_collection_set_name IS NOT NULL
                                 AND f.sku_id = 142
                               GROUP BY 1
              ),

          globez AS (SELECT
                         d.season           AS event,
                         'Globez'           AS feature,
                         d.start_promo_date AS date_from,
                         d.dau,
                         s.spinners,
                         a.antebet_spinners,
                         p.bundle_purchasers,
                         f.set_finishers
                     FROM globez_dau d
                              JOIN globez_spinners s USING (season)
                              JOIN globez_antebet a USING (season)
                              JOIN globez_purchasers p USING (season)
                              JOIN globez_finishers f USING (season)
              )

      ------------------------------------------------------
      -- FINAL OUTPUT
      ------------------------------------------------------
      SELECT *
      FROM figz
      UNION ALL
      SELECT *
      FROM globez
      ) t
```

### 2. Figz Internal Purchase Analysis with Test Groups
**Purpose**: Analyze Figz internal purchase patterns with A/B test group segmentation and platform breakdown
**Tables**: `dwh.sm_fact_internal_purchase_balance_update`, `sm_ds.abtest_user_allocations`, `dwh.sm_user_profile_datamining`, `sm_draft.figz_dates`, `dwh.dim_sku_type`
**Validation**: Track purchase behavior across test groups and user segments

```sql
SELECT
    event,
    date_from,
    date(timestamp::timestamp AT TIME ZONE 'UTC' at
    time zone 'Asia/Jerusalem' - interval '14 hours') as Promo_date,
    platform_id,
    decorated_tier_id AS tier_id,
    CASE
        WHEN (decorated_level=0
            OR  decorated_level IS NULL)
        THEN NULL
        WHEN (decorated_level BETWEEN 1 AND 100)
        THEN '1-100'
        WHEN (decorated_level BETWEEN 101 AND 500)
        THEN '101-500'
        WHEN (decorated_level BETWEEN 501 AND 1000)
        THEN '501-1000'
        WHEN (decorated_level BETWEEN 1001 AND 1500)
        THEN '1001-1500'
        WHEN (decorated_level BETWEEN 1501 AND 2000)
        THEN '1501-2000'
        WHEN (decorated_level BETWEEN 2001 AND 3000)
        THEN '2001-3000'
        WHEN (decorated_level BETWEEN 3001 AND 5000)
        THEN '3001-5000'
        ELSE '5000+'
    END level_group,
c.sku_id,
    event_type,
    case
		   when t.user_id is not null then group_name
		   else dm_test_group end        as t_groups,
    c.sku_name,
    e.transaction_source_type_name,
    ee.transaction_source_type_name AS transaction_source_type_name_internal_purchase,
    COUNT(*)                events_count,
    SUM(net_amount)         AS sum_net_amount,
    SUM(delta)              AS sum_Delta,
    COUNT(DISTINCT a.user_id) AS pu,
    SUM(cost)               AS sum_Cost
FROM
    dwh.sm_fact_internal_purchase_balance_update a
    left join (
					  select distinct
						  a.test_id,
						  t.ab_test_name,
						  a.user_id,
						  a.group_test_id,
						  a.allocation_request_id,
						  g.group_segment_id      as segment_id,
						  g.group_name,
						  g.allocation_percentage as group_size,
						  date(t.start_ts)        as start_date,
						  date(t.end_ts)          as end_date,
						  t.num_of_groups,
						  t.duration_in_days
					  from
						  sm_ds.abtest_user_allocations        a
							  left join sm_ds.abtest_dim_test  t
							  on a.test_id = t.ab_test_id
							  left join sm_ds.abtest_dim_group g
							  on a.group_test_id = g.test_group_id
					  where
						  test_id = <[Parameters].[Parameter 1 2]>) t
                on a.user_id = t.user_id
                 left join (
			  select distinct user_id,
			      -- in case smart allocation dosnt work - insert old allocation test groups case here:
case
   when test_id_6 in (0,1,3,4,6,7,8) then 'Control - Old Level-Ups mission config'/*segment_id 117231425*/
   when test_id_6 in (2,5,9) then 'Test - New Level-Ups mission config'/*segment_id 117231433*/
   end

 dm_test_group
			  from
				  dwh.sm_user_profile_datamining) dm
	on a.user_id = dm.user_id
join (select
	*
        from
	sm_draft.figz_dates order by date_from desc limit 4) season on timestamp between ts_from and ts_to
JOIN
    (
        SELECT
            purchase_id AS purchase_id,
            sku_id,
            transaction_source_type_id
        FROM
            dwh.sm_fact_internal_purchases) b
ON
    a.purchase_id=b.purchase_id
LEFT JOIN
    dwh.dim_sku_type c
ON
    b.sku_id=c.sku_id
LEFT JOIN
    dwh.sm_dim_transaction_source_type ee
ON
    b.transaction_source_type_id=ee.transaction_source_type_id
LEFT JOIN
    (
        SELECT
            tran_id,
            transaction_source_type_id,
            net_amount
        FROM
            dwh.sm_fact_payments
        WHERE
            tran_status_id=2
        AND is_test=0
        AND tran_date>=CURRENT_DATE-60
        AND sku_id=37) d
ON
    a.transaction_id=d.tran_id
LEFT JOIN
    dwh.sm_dim_transaction_source_type e
ON
    d.transaction_source_type_id=e.transaction_source_type_id
WHERE
    date(a.timestamp)>=CURRENT_DATE-60
    and a.currency_id=10000
GROUP BY
    1,2,3,4,5,6,7,8,9,10, 11, 12
```

### 3. Figz Revenue Analysis by Feature Finishers
**Purpose**: Compare revenue between Figz and Globez feature finishers vs general participants
**Tables**: `dwh.sm_fact_payments`, `dwh.fact_sm_goods_service_data`, `sm_draft.figz_dates`, `sm_draft.globez_dates`
**Validation**: Revenue impact analysis for collection set completion

```sql
select
    'Globez' as feature,
    events,
    promo_date,
    start_promo_date,
    datediff('dd', start_promo_date, promo_date),
    count(distinct PUser)                                     PUs,
    count(distinct finisher)                                  finishers,
    sum(gross_rev)                                         as total_gross_rev,
    sum(case when finisher is not null then gross_rev end) as finishers_rev
from (select *,
             A.season   as events,
             A.user_id as PUser,
             B.user_id as finisher
      from (select
                season,
                user_id,
                sum(gross_amount) as gross_rev
            from dwh.sm_fact_payments
                     join (select *
                           from sm_draft.globez_dates
                           order by start_promo_date desc
                           limit 3
                           ) b
                          on date(tran_ts::timestamp AT TIME ZONE 'UTC' at
                              time zone 'Asia/Jerusalem' - interval '14 hours') between start_promo_date and
                              end_promo_date-1
            where tran_status_id = 2
              and artificial_ind = 0
              and is_test = 0
              and user_id >> 0
            group by 1, 2
            ) A
               left join
           (select distinct *,
                            date(reward_ts::timestamp AT TIME ZONE 'UTC' at
                                time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date
            from (select distinct
                      season,
                      start_promo_date,
                      reward_ts,
                      user_id,
                      row_number() over (partition by season,a.user_id order by bonus_ts) rows
                  from dwh.fact_sm_goods_service_data a
                           join (select *
                           from sm_draft.globez_dates
                           order by start_promo_date desc
                           limit 3
                           ) b
                          on date(reward_ts::timestamp AT TIME ZONE 'UTC' at
                              time zone 'Asia/Jerusalem' - interval '14 hours') between start_promo_date and
                              end_promo_date-1

                  where 1 = 1
                    and completed_collection_set_name is not null
                    and sku_id = 142
                    and sku_data ilike '%4%'
--                   and user_id = 151326066440130
                  ) A2
            where rows = 1
            ) B
           on A.season = B.season and A.user_id = B.user_id
      ) A
group by 1, 2, 3, 4,5

union all


select
    'Figz' as feature,
	events,
    promo_date,
    date_from,
	datediff('dd', date_from, promo_date),
	count(distinct PUser)    PUs,
	count(distinct finisher) finishers,
    sum(gross_rev) as total_gross_rev,
    sum(case when finisher is not null then gross_rev end) as finishers_rev
from
	(
		select *,
			   A.event   as events,
			   A.user_id as PUser,
			   B.user_id as finisher
		from

			(
				select
					event,
					user_id,
					sum(gross_amount) as gross_rev
				from
					dwh.sm_fact_payments
						join (
							 select *
							 from
								 sm_draft.figz_dates
							 order by date_from desc
							 limit 3) b
						on tran_ts between ts_from and
							ts_to
				where
					  tran_status_id = 2
				  and artificial_ind = 0
				  and is_test = 0
				  and user_id >> 0
				group by 1, 2)    A
				left join
				(
					select distinct *,
							date(reward_ts::timestamp AT TIME ZONE 'UTC' at
								time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date
					from
						(
							select distinct
								event,
								date_from,
								reward_ts,
								user_id,
								row_number() over (partition by event,a.user_id order by bonus_ts) rows
							from
								dwh.fact_sm_goods_service_data a
									join (
										 select *
										 from
											 sm_draft.figz_dates
										 order by date_from desc
										 limit 3)          b
									on reward_ts between ts_from and
										ts_to

							where
								  1 = 1
							  and completed_collection_set_name is not null
							  and sku_id = 142
							  and sku_data ilike '%4%') A2
					where
						rows = 1) B
				on A.event = B.event and A.user_id = B.user_id) A
group by 1,2,3, 4
```

### 4. Figz Gems Usage Performance Analysis
**Purpose**: Analyze gems upgrade ratios and payout performance by user type and gems usage patterns
**Tables**: `dwh.fact_sm_spin_history_kafka`, `agg.sm_agg_daily_promotion_users_spins`, `dwh.sm_fact_lootbox_history_hero`, `sm_draft.figz_dates`
**Validation**: Correlate gems usage with spinning behavior and payout patterns

```sql
select
    a.event,
    a.date_from,
    a.datediff,
    type,
    gems_ratio,
    count(a.user_id) over (partition by a.event,a.datediff,type)                       per_type_users,
    avg(cum_bonus / cum_ante_bet) over (partition by a.event,a.datediff,type)          per_type_avg_po,
    median(cum_bonus / cum_ante_bet) over (partition by a.event,a.datediff,type)       per_type_med_po,

    count(a.user_id) over (partition by a.event,a.datediff,gems_ratio)                 per_gems_users,
    avg(cum_bonus / cum_ante_bet) over (partition by a.event,a.datediff,gems_ratio)    per_gems_avg_po,
    median(cum_bonus / cum_ante_bet) over (partition by a.event,a.datediff,gems_ratio) per_gems_med_po,



    count(a.user_id) over (partition by a.event,a.datediff,gems_ratio,type)                 per_gems_users_all_dim,
    median(cum_bonus / cum_ante_bet) over (partition by a.event,a.datediff,gems_ratio,type) per_gems_med_po_all_dim,
    percentile_disc(0.75) within GROUP (ORDER BY cum_bonus / cum_ante_bet ASC) over (partition by a.event,a.datediff,gems_ratio,type) AS per_gems_p75_po,
    percentile_disc(0.90) within GROUP (ORDER BY cum_bonus / cum_ante_bet ASC) over (partition by a.event,a.datediff,gems_ratio,type) AS per_gems_p90_po,
    percentile_disc(0.95) within GROUP (ORDER BY cum_bonus / cum_ante_bet ASC) over (partition by a.event,a.datediff,gems_ratio,type) AS per_gems_p95_po

from (select
          dates_users.user_id,
          dates_users.event,
          dates_users.date_from,
          gems_ratio,
          datediff('day', dates_users.date_from, dates_users.date)                             datediff,
          type,
          sum(coalesce(ante_bet_amount, 0))
          over (partition by dates_users.user_id, dates_users.event order by dates_users.date) cum_ante_bet,
          sum(coalesce(bonus_amount, 0))
          over (partition by dates_users.user_id, dates_users.event order by dates_users.date) cum_bonus
      from (select
                date,
                b.event,
                b.date_from,
                user_id
            from (select * from dwh.dim_dates where date between current_date - 60 and current_date) a
                     join sm_draft.figz_dates b on date between date_from and date_to-1
                     join (select distinct
                               user_id,
                               event,
                               date_from
                           from dwh.fact_sm_spin_history_kafka
                                    join sm_draft.figz_dates on spin_ts between ts_from and ts_to
                           where ts_from >= current_date - 60
                             and machine_type_id in (13522, 13569)
                           ) users using (date_From)
            ) dates_users
               left join (select
                              user_id,
                              event,
                              date_from,
                              date(spin_ts::timestamp AT TIME ZONE 'UTC' at
                                  time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
                              sum(win_amount)                                          bonus_amount
                          from dwh.fact_sm_spin_history_kafka
                                   join sm_draft.figz_dates on spin_ts between ts_from and ts_to
                          where ts_from >= current_date - 60
                            and machine_type_id in (13522, 13569)
                          group by 1, 2, 3, 4
                          ) A on dates_users.user_id = a.user_id and dates_users.date = a.promo_date
               left join (select
                              user_id,
                              event,
                              date_from,
                              start_promo_date                 promo_date,
                              sum(antebet_amounts_slotoheroes) ante_bet_amount
                          from agg.sm_agg_daily_promotion_users_spins
                                   join sm_draft.figz_dates b on start_promo_date between b.date_from and b.date_to
                          where ts_from >= current_date - 60
                            and slotoheros_antebet_spins_amount >> 0
                          group by 1, 2, 3, 4
                          ) B on dates_users.user_id = b.user_id and dates_users.date = b.promo_date
               left join (select
                              event,
                              user_id,
                              bundles_upgraded,
                              bundles_purchased,
                              case
                                  when bundles_upgraded / bundles_purchased = 0 then 0
                                  when bundles_upgraded / bundles_purchased <= 0.25 then 0.25
                                  when bundles_upgraded / bundles_purchased <= 0.5 then 0.50
                                  when bundles_upgraded / bundles_purchased <= 0.75 then 0.75
                                  when bundles_upgraded / bundles_purchased <= 0.99 then 0.99
                                  when bundles_upgraded = bundles_purchased then 1 end gems_ratio,
                              case
                                  when lion = 1 and gorilla = 1 then 'both'
                                  when lion = 1 then 'lion'
                                  when gorilla = 1 then 'gorilla' end                  type
                          from (select
                                    event,
                                    box_user_id                                                             user_id,
                                    max(case when box_box_type = 'slotoheroes_silverlion' then 1 end)       lion,
                                    max(case when box_box_type = 'slotoheroes_gorilla' then 1 end)          gorilla,
                                    count(distinct box_guid)                                                bundles_purchased,
                                    count(distinct case when event_type = 'BOX_UPGRADED' then box_guid end) bundles_upgraded
                                from dwh.sm_fact_lootbox_history_hero
                                         join sm_Draft.figz_dates on event_ts between ts_from and ts_to
                                where 1 = 1
                                  and event_type in ('BOX_CREATED', 'BOX_UPGRADED')
                                  and event_source_type = 'internal-purchase'
                                  and box_box_type in ('slotoheroes_silverlion',
                                                       'slotoheroes_gorilla')
                                  and ts_from >= current_date - 60
                                group by 1, 2
                                ) A
                          ) C on a.user_id = c.user_id and a.event = c.event
      ) A
where cum_ante_bet >> 0
limit 1 over (partition by a.event,a.datediff,gems_ratio, type  order by a.event,a.datediff)
```

### 5. Figz Simplified Gems Performance Analysis
**Purpose**: Simplified analysis of gems upgrade performance without user type segmentation
**Tables**: Same as above but focused on gems ratio performance
**Validation**: Cleaner gems usage analysis without lion/gorilla type complexity

```sql
select
    a.event,
    a.date_from,
    a.datediff,
    gems_ratio,

    count(a.user_id) over (partition by a.event,a.datediff,gems_ratio)                 per_gems_users,
    median(cum_bonus / cum_ante_bet) over (partition by a.event,a.datediff,gems_ratio) per_gems_med_po,
    percentile_disc(0.75) within GROUP (ORDER BY cum_bonus / cum_ante_bet ASC) over (partition by a.event,a.datediff,gems_ratio) AS per_gems_p75_po,
    percentile_disc(0.90) within GROUP (ORDER BY cum_bonus / cum_ante_bet ASC) over (partition by a.event,a.datediff,gems_ratio) AS per_gems_p90_po,
    percentile_disc(0.95) within GROUP (ORDER BY cum_bonus / cum_ante_bet ASC) over (partition by a.event,a.datediff,gems_ratio) AS per_gems_p95_po

from (select
          dates_users.user_id,
          dates_users.event,
          dates_users.date_from,
          gems_ratio,
          datediff('day', dates_users.date_from, dates_users.date)                             datediff,
--           type,
          sum(coalesce(ante_bet_amount, 0))
          over (partition by dates_users.user_id, dates_users.event order by dates_users.date) cum_ante_bet,
          sum(coalesce(bonus_amount, 0))
          over (partition by dates_users.user_id, dates_users.event order by dates_users.date) cum_bonus
      from (select
                date,
                b.event,
                b.date_from,
                user_id
            from (select * from dwh.dim_dates where date between current_date - 60 and current_date) a
                     join sm_draft.figz_dates b on date between date_from and date_to-1
                     join (select distinct
                               user_id,
                               event,
                               date_from
                           from dwh.fact_sm_spin_history_kafka
                                    join sm_draft.figz_dates on spin_ts between ts_from and ts_to
                           where ts_from >= current_date - 60
                             and machine_type_id in (13522, 13569)
                           ) users using (date_From)
            ) dates_users
               left join (select
                              user_id,
                              event,
                              date_from,
                              date(spin_ts::timestamp AT TIME ZONE 'UTC' at
                                  time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
                              sum(win_amount)                                          bonus_amount
                          from dwh.fact_sm_spin_history_kafka
                                   join sm_draft.figz_dates on spin_ts between ts_from and ts_to
                          where ts_from >= current_date - 60
                            and machine_type_id in (13522, 13569)
                          group by 1, 2, 3, 4
                          ) A on dates_users.user_id = a.user_id and dates_users.date = a.promo_date
               left join (select
                              user_id,
                              event,
                              date_from,
                              start_promo_date                 promo_date,
                              sum(antebet_amounts_slotoheroes) ante_bet_amount
                          from agg.sm_agg_daily_promotion_users_spins
                                   join sm_draft.figz_dates b on start_promo_date between b.date_from and b.date_to-1
                          where ts_from >= current_date - 60
                            and slotoheros_antebet_spins_amount >> 0
                          group by 1, 2, 3, 4
                          ) B on dates_users.user_id = b.user_id and dates_users.date = b.promo_date
               left join (select
                              event,
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
                                    event,
                                    box_user_id                                                             user_id,
                                    max(case when box_box_type = 'slotoheroes_silverlion' then 1 end)       lion,
                                    max(case when box_box_type = 'slotoheroes_gorilla' then 1 end)          gorilla,
                                    count(distinct box_guid)                                                bundles_purchased,
                                    count(distinct case when event_type = 'BOX_UPGRADED' then box_guid end) bundles_upgraded
                                from dwh.sm_fact_lootbox_history_hero
                                         join sm_Draft.figz_dates on event_ts between ts_from and ts_to
                                where 1 = 1
                                  and event_type in ('BOX_CREATED', 'BOX_UPGRADED')
                                  and event_source_type = 'internal-purchase'
                                  and box_box_type in ('slotoheroes_silverlion',
                                                       'slotoheroes_gorilla')
                                  and ts_from >= current_date - 60
                                group by 1, 2
                                ) A
                          ) C on a.user_id = c.user_id and a.event = c.event
      ) A
where cum_ante_bet >> 0
limit 1 over (partition by a.event,a.datediff,gems_ratio  order by a.event,a.datediff)
```

### 6. Figz Spin Performance Analysis with Featured Machines
**Purpose**: Analyze Figz spin activity including featured machine usage and antebet patterns 
**Tables**: `dwh.fact_sm_spin_history_kafka`, `sm_draft.figz_dates`, `agg.sm_agg_daily_promotion_users_spins`
**Validation**: Track spin patterns on featured vs regular machines by event period

```sql
select
    'Figz' as feature,
    event,
    date_from,
    datediff('dd', date_from, promo_date) days_from_start,
    count(distinct user_id) total_spinners,
    count(distinct case when count_anteBet_spins > 0 then user_id end) total_anteBet_spinners,
    sum(count_anteBet_spins) anteBet_spins,
    sum(count_spins) total_spins,
    sum(case when is_featured_machine = 'true' then count_spins else 0 end) total_spins_featured_machines,
    sum(total_bet_amount_with_anteBet) anteBet_bet_amount,
    sum(total_bet_amount) total_bets,
    sum(case when is_featured_machine = 'true' then total_bet_amount else 0 end) total_bet_featured_machines
from (select
          event,
          date_from,
          sp.user_id,
          date(spin_ts::timestamp AT TIME ZONE 'UTC' at
              time zone 'Asia/Jerusalem' - interval '14 hours') promo_date,
          case
              when machine_type_id in
                   (select distinct
                        machine_type_id
                    from agg.sm_agg_daily_promotion_users_spins
                    where antebet_amounts_slotoheroes >> 0
                    ) then 'true'
              else 'false' end is_featured_machine,
          count(*) count_spins,
          count(distinct case when antebet_amounts_slotoheroes >> 0 then guid end) count_anteBet_spins,
          sum(bet_amount) total_bet_amount,
          sum(case when antebet_amounts_slotoheroes >> 0 then bet_amount else 0 end) total_bet_amount_with_anteBet
      from (select *
            from dwh.fact_sm_spin_history_kafka
            ) sp
               join (select *
                     from sm_draft.figz_dates
                     order by date_from desc
                     limit 3
                     ) e
                    on spin_ts between ts_from and ts_to and date(spin_ts) >= current_date - 60

      group by 1, 2, 3, 4, 5
      ) q2
group by 1, 2, 3,4
```

### 7. Figz Engagement Analysis - Participant vs Unengaged Users
**Purpose**: Analyze Figz feature engagement metrics identifying unengaged users with high coin balances
**Tables**: `dwh.sm_fact_internal_purchase_balance_update_hero_coins`, `sm_draft.figz_dates`
**Validation**: Identify users who received significant coins but didn't engage with spending

```sql
select
	event,
        ts_from, 
	count(distinct case when figz_coins_recived >= 3000 and figz_coins_used = 0 then user_id end)
		unengaged_users,
        count(distinct case when figz_coins_recived > 0 then user_id end) all_partcipants
from
	(
		select
			event,
                        ts_from, 
			user_id,
			coalesce(sum(case when delta > 0 then delta end), 0)        figz_coins_recived,
			coalesce(sum(case when delta < 0 then delta * (-1) end), 0) figz_coins_used
		from
			dwh.sm_fact_internal_purchase_balance_update_hero_coins a
				join sm_draft.figz_dates                            b
				on a.timestamp between ts_from and ts_to
		group by 1, 2, 3) A
group by 1, 2
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `general-mid-term.md` - Complete Mid-term business context