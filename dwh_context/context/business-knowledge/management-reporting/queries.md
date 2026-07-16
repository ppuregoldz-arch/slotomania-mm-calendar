# Management Report - SQL Queries

**Note**: This file contains actual SQL queries extracted from the Management report - New April 2025 (27).twbx for daily management reporting and executive oversight.

## Query Inventory

### 1. User Velocity Analysis by Tier
**Purpose**: Analyze user spending velocity (bet-win ratio) by tier for purchasers with balance tracking
**Tables**: `agg.agg_sm_daily_users_stats`, `dwh.playtika_users`, `dwh.sm_fact_coins_reset_migration`, `dwh.sm_fact_payments`
**Validation**: Track spending patterns and balance management across user tiers

```sql
select
        calc_date,
        first_session_tier,
        percentile_disc(0.50) within group (order by velocity asc)
        over (partition by calc_date, first_session_tier) as Velocity,
           percentile_disc(0.50) within group (order by balance_start_day asc)
        over (partition by calc_date, first_session_tier) as balance_start_day
    from
        (
        select
            calc_date,
            first_session_tier,
            user_id,
            (bet_coins - win_coins) / balance_start_day as velocity,
            balance_start_day
        from
            agg.agg_sm_daily_users_stats
        where
              first_session_tier >= 4
          and calc_date >= current_date() - 90
          and bet_coins > 0
          and balance_start_day > 1
          and user_id not in (
                             select distinct
                                 user_id
                             from
                                 dwh.playtika_users)
and user_id not in (select
          user_id
      from dwh.sm_fact_coins_reset_migration
      where 1 = 1
        and migrated = 'true'
and  user_id not in (select distinct user_id from dwh.playtika_users)
and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)

      group by 1
      having min(event_ts) >= '2025-08-18'
     )
          and user_id in (
                         select
                             user_id
                         from
                             dwh.sm_fact_payments
                         where
                               tran_date >= current_date - 90
                           and user_id > 0
                           and tran_status_id = 2
                           and artificial_ind = 0
                           and is_test = 0
                         group by 1
                         )
        ) a
    where
        first_session_tier is not null

    limit 1 over (partition by calc_date, first_session_tier order by 1 )
```

### 2. Slotobucks Balance Distribution by CZ Ranges
**Purpose**: Comprehensive analysis of Slotobucks balance distribution across different CZ (Customer Zone) ranges for purchasers
**Tables**: `agg.agg_sm_daily_users_stats`, `dwh.sm_fact_internal_purchase_balance_update_slotobucks`, `dwh.sm_user_profile_datamining_snapshot`, `dwh.sm_fact_payments`
**Validation**: Track balance patterns across different customer value segments

```sql
select distinct
    calc_date,
    case
        when a.cz_deluxe_weekly_update >= 0 and a.cz_deluxe_weekly_update < 10 then '0-10'
        when a.cz_deluxe_weekly_update >= 10 and a.cz_deluxe_weekly_update < 50 then '10-50'
        when a.cz_deluxe_weekly_update >= 50 and a.cz_deluxe_weekly_update < 100 then '50-100'
        when a.cz_deluxe_weekly_update >= 100 and a.cz_deluxe_weekly_update < 300 then '100-300'
        when a.cz_deluxe_weekly_update >= 300 and a.cz_deluxe_weekly_update < 500 then '300-500'
        when a.cz_deluxe_weekly_update >= 500 then '500+'

        end                                                 as cz_ranges,
    percentile_cont(0.25) within group ( order by SB_users_new_balance )
    over (partition by calc_date,     case
        when a.cz_deluxe_weekly_update >= 0 and a.cz_deluxe_weekly_update < 10 then '0-10'
        when a.cz_deluxe_weekly_update >= 10 and a.cz_deluxe_weekly_update < 50 then '10-50'
        when a.cz_deluxe_weekly_update >= 50 and a.cz_deluxe_weekly_update < 100 then '50-100'
        when a.cz_deluxe_weekly_update >= 100 and a.cz_deluxe_weekly_update < 300 then '100-300'
        when a.cz_deluxe_weekly_update >= 300 and a.cz_deluxe_weekly_update < 500 then '300-500'
        when a.cz_deluxe_weekly_update >= 500 then '500+'

        end  )                                               as Percentile_25_end_day_balance_SB_users_CZ,
    percentile_cont(0.5) within group ( order by SB_users_new_balance )
    over (partition by calc_date, case
                                      when a.cz_deluxe_weekly_update >= 0 and a.cz_deluxe_weekly_update < 2 then '0-2'
                                      when a.cz_deluxe_weekly_update >= 2 and a.cz_deluxe_weekly_update < 3 then '2-3'
                                      when a.cz_deluxe_weekly_update >= 3 and a.cz_deluxe_weekly_update < 5 then '3-5'
                                      when a.cz_deluxe_weekly_update >= 5 and a.cz_deluxe_weekly_update < 7 then '5-7'
                                      when a.cz_deluxe_weekly_update >= 7 and a.cz_deluxe_weekly_update < 9 then '7-9'
                                      when a.cz_deluxe_weekly_update >= 9 and a.cz_deluxe_weekly_update < 12 then '9-12'
                                      when a.cz_deluxe_weekly_update >= 12 and a.cz_deluxe_weekly_update < 15
                                          then '12-15'
                                      when a.cz_deluxe_weekly_update >= 15 and a.cz_deluxe_weekly_update < 20
                                          then '15-20'
                                      when a.cz_deluxe_weekly_update >= 20 and a.cz_deluxe_weekly_update < 25
                                          then '20-25'
                                      when a.cz_deluxe_weekly_update >= 25 and a.cz_deluxe_weekly_update < 30
                                          then '25-30'
                                      when a.cz_deluxe_weekly_update >= 30 and a.cz_deluxe_weekly_update < 35
                                          then '30-35'
                                      when a.cz_deluxe_weekly_update >= 35 and a.cz_deluxe_weekly_update < 50
                                          then '35-50'
                                      when a.cz_deluxe_weekly_update >= 50 and a.cz_deluxe_weekly_update < 100
                                          then '50-100'
                                      when a.cz_deluxe_weekly_update >= 100 then '+100'
        end )                                               as Percentile_50_end_day_balance_SB_users_CZ,
    percentile_cont(0.75) within group ( order by SB_users_new_balance )
    over (partition by calc_date,     case
        when a.cz_deluxe_weekly_update >= 0 and a.cz_deluxe_weekly_update < 10 then '0-10'
        when a.cz_deluxe_weekly_update >= 10 and a.cz_deluxe_weekly_update < 50 then '10-50'
        when a.cz_deluxe_weekly_update >= 50 and a.cz_deluxe_weekly_update < 100 then '50-100'
        when a.cz_deluxe_weekly_update >= 100 and a.cz_deluxe_weekly_update < 300 then '100-300'
        when a.cz_deluxe_weekly_update >= 300 and a.cz_deluxe_weekly_update < 500 then '300-500'
        when a.cz_deluxe_weekly_update >= 500 then '500+'

        end )                                               as Percentile_75_end_day_balance_SB_users_CZ,
    percentile_cont(0.95) within group ( order by SB_users_new_balance )
    over (partition by calc_date, case
                                      when a.cz_deluxe_weekly_update >= 0 and a.cz_deluxe_weekly_update < 2 then '0-2'
                                      when a.cz_deluxe_weekly_update >= 2 and a.cz_deluxe_weekly_update < 3 then '2-3'
                                      when a.cz_deluxe_weekly_update >= 3 and a.cz_deluxe_weekly_update < 5 then '3-5'
                                      when a.cz_deluxe_weekly_update >= 5 and a.cz_deluxe_weekly_update < 7 then '5-7'
                                      when a.cz_deluxe_weekly_update >= 7 and a.cz_deluxe_weekly_update < 9 then '7-9'
                                      when a.cz_deluxe_weekly_update >= 9 and a.cz_deluxe_weekly_update < 12 then '9-12'
                                      when a.cz_deluxe_weekly_update >= 12 and a.cz_deluxe_weekly_update < 15
                                          then '12-15'
                                      when a.cz_deluxe_weekly_update >= 15 and a.cz_deluxe_weekly_update < 20
                                          then '15-20'
                                      when a.cz_deluxe_weekly_update >= 20 and a.cz_deluxe_weekly_update < 25
                                          then '20-25'
                                      when a.cz_deluxe_weekly_update >= 25 and a.cz_deluxe_weekly_update < 30
                                          then '25-30'
                                      when a.cz_deluxe_weekly_update >= 30 and a.cz_deluxe_weekly_update < 35
                                          then '30-35'
                                      when a.cz_deluxe_weekly_update >= 35 and a.cz_deluxe_weekly_update < 50
                                          then '35-50'
                                      when a.cz_deluxe_weekly_update >= 50 and a.cz_deluxe_weekly_update < 100
                                          then '50-100'
                                      when a.cz_deluxe_weekly_update >= 100 then '+100'
        end )                                               as Percentile_95_end_day_balance_SB_users_CZ,
    avg(SB_users_new_balance) over (partition by calc_date,     case
        when a.cz_deluxe_weekly_update >= 0 and a.cz_deluxe_weekly_update < 10 then '0-10'
        when a.cz_deluxe_weekly_update >= 10 and a.cz_deluxe_weekly_update < 50 then '10-50'
        when a.cz_deluxe_weekly_update >= 50 and a.cz_deluxe_weekly_update < 100 then '50-100'
        when a.cz_deluxe_weekly_update >= 100 and a.cz_deluxe_weekly_update < 300 then '100-300'
        when a.cz_deluxe_weekly_update >= 300 and a.cz_deluxe_weekly_update < 500 then '300-500'
        when a.cz_deluxe_weekly_update >= 500 then '500+'

        end  )                                               as avg_day_balance_SB_users_CZ,


    percentile_cont(0.25) within group ( order by SB_users_new_balance )
    over (partition by calc_date)                           as Percentile_25_end_day_balance_SB_users,
    percentile_cont(0.5) within group ( order by SB_users_new_balance )
    over (partition by calc_date)                           as Percentile_50_end_day_balance_SB_users,
    percentile_cont(0.75) within group ( order by SB_users_new_balance )
    over (partition by calc_date)                           as Percentile_75_end_day_balance_SB_users,
    percentile_cont(0.95) within group ( order by SB_users_new_balance )
    over (partition by calc_date)                           as Percentile_95_end_day_balance_SB_users,
    avg(SB_users_new_balance) over (partition by calc_date) as avg_day_balance_SB_users
from
    (
        select
            a.calc_date,
            a.user_id,
            a.cz_deluxe_weekly_update,
            coalesce(new_balance, 0) as SB_users_new_balance
        from
            agg.agg_sm_daily_users_stats                     a
                join
                     (
                         select
                             calc_date,
                             new_balance,
                             user_id
                         from
                             (
                                 select distinct
                                     date(
                                             timestamp) as                            calc_date,
                                     timestamp,
                                     user_id,
                                     new_balance,
                                     row_number(
                                         ) over (
                                         partition by user_id, date(
                                                 timestamp) order by timestamp desc ) rn
                                 from
                                     dwh.sm_fact_internal_purchase_balance_update_slotobucks a
                                 where
                                         date(
                                                 timestamp) >= '2024-01-01'
                                   and   1 = 1
                                         --and   user_id = 20283
                                   and   user_id not in (
                                                            select distinct
                                                                user_id
                                                            from
                                                                dwh.playtika_users
                                                        )
                                   and   user_id not in (
                                                            select distinct
                                                                user_id
                                                            from
                                                                dwh.sm_fact_journey_state_notifications
                                                            where
                                                                step_id = 539265
                                                        )
                             ) a
                         where
                             rn = 1
                     )                                       SB_balance
                on a.user_id = SB_balance.user_id and a.calc_date = SB_balance.calc_date
                join dwh.sm_user_profile_datamining_snapshot c
                on a.user_id = c.user_id and a.calc_date = c.event_date_datamining
        where
              a.calc_date >= '2024-01-01'
          and a.user_id
                  > 0
          and a.user_id in (
                               select distinct
                                   user_id
                               from
                                   dwh.sm_fact_payments
                               where
                                     user_id > 0
                                 and tran_status_id = 2
                                 and artificial_ind = 0
                                 and is_test = 0
                                 and tran_date >= '2024-01-01'
                           )
    ) A
```

### 3. High Revenue User Analysis (Top 1% and Top 5%)
**Purpose**: Identify and analyze top revenue generating users by monthly cohorts
**Tables**: `agg.agg_sm_daily_users_stats`, `dwh.playtika_users`, `dwh.sm_fact_journey_state_notifications`
**Validation**: Track high-value user distribution and revenue concentration

```sql
select year_month,
          case when P95_rev <= rev then 1 else 0 end as is_top5,
          case when P99_rev <= rev then 1 else 0 end as is_top1,
          sum(rev)                                   as rev,
          count(distinct user_id) as PU
      from (select
                a.user_id,
                year_month,
                rev,
                percentile_disc(0.95) within GROUP (ORDER BY rev ASC) over (partition by year_month) AS P95_rev,
                  percentile_disc(0.99) within GROUP (ORDER BY rev ASC) over (partition by year_month) AS P99_rev
            from (select
                      user_id,
                      date_trunc('month', calc_date) year_month,
                      sum(daily_gross_rev) as           rev
                  from agg.agg_sm_daily_users_stats

                  where 1 = 1
                    and calc_date >= '2023-01-01'
                  and  user_id not in (select distinct user_id from dwh.playtika_users)
                  and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
                  group by 1, 2
                  having sum(daily_gross_rev) > 0
                 ) A
           ) A
      group by 1,2,3
```

### 4. Payment Page Performance Analysis with Prestige Economy
**Purpose**: Comprehensive analysis of Payment Page performance including prestige multipliers and sale vs PP value
**Tables**: `dwh.sm_fact_payments`, `sm_draft.SM_DIM_Products`, `dwh.sm_user_profile_datamining_snapshot`, `dwh.sm_fact_precious_level_up`, `sm_draft.new_premium_multipliers_12_01`, `dwh.Dim_Coins_Value`, `sm_draft.base_coins_Control_18_09`
**Validation**: Track payment page efficiency with prestige economy calculations

```sql
select a.*,
             Config_Base_Coins * prestige_multiplier * tier_multiplier                      as config_PP_value_perstige_ecomony,
             payment_quantity / (Config_Base_Coins * prestige_multiplier * tier_multiplier) as ratio,
             round((payment_quantity - (Config_Base_Coins * prestige_multiplier * tier_multiplier)) /
                   (Config_Base_Coins * prestige_multiplier * tier_multiplier), 2)          as sale_VS_PP
/*PP purchases - excluding rolled back  & test - new prestige */
      from (SELECT
                date(tran_ts::timestamp AT TIME ZONE 'UTC' at
                    time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
                     case when Product_Name = 'Payment Page' and payment_page_type_id = 30 then 'Payment Page'
                     when Product_Name = 'Payment Page' and payment_page_type_id != 30 then 'ROOC'
                     when Product_Name = 'Gems' and payment_page_type_id = 62 then 'Gems Payemnt Page'
                     when Product_Name = 'Gems' and payment_page_type_id != 62 then 'ROOG'
                     else Product_Name end as Product_Name,
                user_id,
                gross_amount,
                payment_quantity,
                tran_ts,
                price,
                tier_id,
                level_id,
                tran_id,
                page_option_id
            from dwh.sm_fact_payments a
                     left join sm_draft.SM_DIM_Products b
                               on a.sku_id = b.sku_id and a.transaction_source_type_id = b.transaction_source_type_id
            where 1 = 1
              and tran_status_id = 2
              and artificial_ind = 0
              and is_test = 0
              and user_id > 0
              and payment_quantity > 0
              and tran_date >= current_date - 14
              --- excluding rolled back users
              and user_id not in (select distinct user_id from dwh.playtika_users)
              and user_id not in
                  (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)) A
/*CZ & BM - datamaining tbl*/
               left join (SELECT
                              event_date_datamining,
                              user_id,
                              DPU_Segment,
                              max(cz_price_cut_test) as cz_price_cut_test
                          from dwh.sm_user_profile_datamining_snapshot
                          where 1 = 1
                            and event_date_datamining >= current_date- 14
                          group by 1, 2, 3) x
                         on a.user_id = x.user_id and x.event_date_datamining = a.promo_date
/*prestige level*/
               left join (select
                              user_id,
                              old_precious_level,
                              new_precious_level,
                              event_ts,
                              event_source,
                              coalesce(lead(event_ts) over (partition by user_id order by event_ts),
                                       current_timestamp) as lead_event_ts
                          from dwh.sm_fact_precious_level_up
                          where 1 = 1) f
                         on a.user_id = f.user_id and tran_ts between event_ts and lead_event_ts
/*prestige level multipliers*/
               left join (select *,
                                 premium_multiplier as prestige_multiplier
                          from sm_draft.new_premium_multipliers_12_01) g
                         on f.new_precious_level = g.p_level
/*tier & level multipliers*/
               left join (select
                              tier_id,
                              max(tier_multiplier)  tier_multiplier
                          from dwh.Dim_Coins_Value
                          group by 1) cv
                         on a.tier_id = cv.tier_id
/*Config - PP*/
               left join (select
                              denom,
                              base_coins as Config_Base_Coins
                          FROM sm_draft.base_coins_Control_18_09) r
                         on round(price) = round(denom)
      where 1 = 1
        and cz_price_cut_test is not null
```

### 5. Real Money vs. Slotobucks Revenue Analysis
**Purpose**: Compare revenue from real money purchases vs. virtual currency (Slotobucks) spending
**Tables**: `dwh.sm_fact_payments`, `dwh.sm_fact_virtual_payment_slotobucks`, `sm_draft.SM_DIM_Products`
**Validation**: Track dual-currency economy health and revenue mix

```sql
select
    tran_date,
    product_name,
    'real money'      as currency,
    sum(gross_amount) as gross
from
    dwh.sm_fact_payments                   a
        left join sm_draft.SM_DIM_Products b
        on a.sku_id = b.sku_id and a.transaction_source_type_id = b.transaction_source_type_id
where
      user_id > 0
  and tran_status_id = 2
  and artificial_ind = 0
  and is_test = 0
  and tran_date >= current_date - 30
group by 1, 2
union
select
    tran_date,
    product_name,
    'Bucks'           as currency,
    sum(gross_amount) as gross
from
    dwh.sm_fact_virtual_payment_slotobucks a
        left join sm_draft.SM_DIM_Products b
        on a.sku_id = b.sku_id and a.transaction_source_type_id = b.transaction_source_type_id
where
      user_id > 0
  and tran_status_id = 2
  and artificial_ind = 0
  and is_test = 0
  and tran_date >= current_date - 30
group by 1, 2
```

### 6. User Churn Analysis by Login Recency
**Purpose**: Analyze user churn patterns based on login recency for retention insights
**Tables**: `agg.agg_sm_daily_users_stats`, `dwh.dim_dates`
**Validation**: Track engagement dropoff patterns and identify at-risk user segments

```sql
select
    case
        when days_from_login <= 7 then '1 week last_login'
        when days_from_login <= 14 then '2 weeks last_login'
        when days_from_login <= 21 then '3 weeks last login'
        when days_from_login >= 21 then 'more than 3 weeks' end as login_days,
    did_churn,
    date,
    is_pu,
    count(distinct user_id)                                        users
from
    (
        select
            date,
            user_id,
            did_churn,
            is_pu,
            last_login_date,
            datediff('dd', last_login_date, date) days_from_login
        from
            (
                select
                    did_churn,
                    date,
                    is_pu,
                    a.user_id,
                    max(calc_date) last_login_date
                from
                    (
                        select
                            a.user_id,
                            date,
                            is_pu,
                            case when b.calc_date is not null then 'STAY' else 'CHURN' end as did_churn
                        from
                            (
                                select
                                    a.date,
                                    b.user_id,
                                    is_pu
                                from
                                    (
                                        select distinct
                                            date
                                        from
                                            dwh.dim_dates
                                        where
                                            date between current_date - 180 and current_date - 1
                                    )                a
                                        cross join (
                                                       select distinct
                                                           user_id,
                                                           max(case when daily_Net_revenue > 0 then 1 else 0 end) is_pu
                                                       from
                                                           agg.agg_sm_daily_users_stats
                                                       where
                                                             calc_date >= current_date - 364
                                                       group by 1

                                                   ) b
                            )              a
                                left join(
                                             select *
                                             from
                                                 agg.agg_sm_daily_users_stats
                                             where
                                                   calc_date >= current_date - 364
                                         ) b
                                on a.user_id = b.user_id and a.date = b.calc_date
                    )              a
                        left join(
                                     select
                                         user_id,
                                         calc_date
                                     from
                                         agg.agg_sm_daily_users_stats
                                     where
                                         calc_date > current_date - 364
                                 ) c
                        on a.user_id = c.user_id and c.calc_date < date
                group by 1, 2, 3, 4
            ) a
    ) b
group by 1,2,3,4
```

### 7. DAU and Active Purchaser Tracking
**Purpose**: Daily Active Users (DAU) and active purchaser monitoring for engagement health
**Tables**: `agg.agg_sm_daily_users_stats`, `dwh.playtika_users`, `dwh.sm_fact_journey_state_notifications`
**Validation**: Core engagement metrics with clean user base for management reporting

```sql
select calc_date,
       count(distinct user_id) as DAU,
       count(distinct case when is_pu=1 then a.user_id else null end) as active_PUs
from (select
          a.user_id,
          a.calc_date,
          daily_gross_rev,
          max(case when b.user_id is null then 0 else 1 end) as is_pu

      from (select
                user_id,
                calc_date,
                daily_gross_rev

            from agg.agg_sm_daily_users_stats
            where 1=1
              and calc_date between current_date - 121 and current_date - 1
            and  user_id not in (select distinct user_id from dwh.playtika_users)
            and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
           ) A
               left join (select
                              user_id,
                              calc_date
                          from agg.agg_sm_daily_users_stats
                          where 1=1
                            and daily_gross_rev > 0
                            and calc_date between current_date - 140 and current_date - 1
                          and  user_id not in (select distinct user_id from dwh.playtika_users)
                          and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)


                         ) b on a.user_id = b.user_id and b.calc_date between a.calc_date - 14 and a.calc_date

      group by 1, 2, 3
     ) A
group by 1
```

### 8. Bonus Distribution Analysis with Iraq Tracking
**Purpose**: Track bonus distribution patterns with special focus on Iraq users and purchase-related bonuses
**Tables**: `dwh.fact_sm_bonus_history`, `dwh.dim_sm_bonus_type`, `dwh.sm_user_profile`, `dwh.sm_fact_payments`
**Validation**: Monitor bonus economy health and regional user behavior patterns

```sql
select
    a.bonus_type_id,
    b.bonus_type_name,
    case when c.country_name ilike '%iraq%' then 1 else 0 end is_iraq,
    case when transaction_id is not null then 1 else 0 end as is_purcashe,
    date(bonus_ts)                                            calc_date,
    sum(bonus_amount)                                         bonus_amounts,
    count(distinct a.user_id)                                   users
from
    dwh.fact_sm_bonus_history           a
        left join dwh.dim_sm_bonus_type b
        on a.bonus_type_id = b.bonus_type_id
        left join dwh.sm_user_profile c
        on a.user_id=c.user_id

where
      bonus_ts >= current_date - 180
  and a.user_id not in (
                         select distinct
                             user_id
                         from
                             dwh.sm_fact_journey_state_notifications
                         where
                             step_id = 539265
                     )
  AND a.user_id in (
                     select distinct
                         user_id
                     from
                         dwh.sm_fact_payments
                     where
                           user_id > 0
                       and tran_status_id = 2
                       and artificial_ind = 0
                       and is_test = 0
                       and tran_date >= current_date - 180
                 )
and a.user_id not in (154000075169724,154000075167752,154000075217673,154000075170768,154000075168702,
                    154000075171722,154000075166703,154000075163749,154000075219659,154000075213698,
                    154000075173657,154000075167753,154000075164719,154000075168709,154000075171727,
                    154000075217672,154000075164718,154000075158947,154000075162758,154000075164723,
                    154000075218640,154000075169727,154000075220595,154000075210880,154000075212758,
                    154000075216646,154000075162763,154000075164723
) --Iraq players, excluded due to cheat in Winovate
and a.user_id not in (2786798) --exclude due to stamps

      and a.user_id not in (select
          user_id
      from dwh.sm_fact_coins_reset_migration
      where 1 = 1
          and migrated = 'true'
and  user_id not in (select distinct user_id from dwh.playtika_users)
and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)

      group by 1
      having min(event_ts) >= '2025-08-18')


group by 1, 2, 3, 4, 5
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence for management reporting
- Core business knowledge files for understanding executive KPIs and reporting structure