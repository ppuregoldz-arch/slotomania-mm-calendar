# LBP - SQL Queries

**Note**: This file contains actual SQL queries provided by the user for LBP analysis and investigations.

## Query Inventory

### 1. LBP Weekly Performance Analysis
**Purpose**: Weekly LBP performance analysis by CZ range and PU status
**Tables**: `dwh.fact_sm_user_bonuses`, `dwh.fact_sm_user_transactions`, user segmentation
**Validation**: Analyze weekly conversion rates and revenue for LBP feature

```sql
select
    'LBP'                                           as product_name,
    a.week_start,
    a.cz_range,
    a.is_PU_30d,
    weekly_imp_events,
    weekly_imp_users,
    coalesce(weekly_trx, 0)                         as weekly_trx,
    coalesce(b.weekly_PUs, 0)                       as weekly_PUs,
    coalesce(b.weekly_gross_amount, 0)              as weekly_gross_amount,
    coalesce(b.weekly_net_amount, 0)                as weekly_net_amount,
    (coalesce(b.weekly_PUs, 0)) / weekly_imp_users  as weekly_cov_users,
    (coalesce(b.weekly_trx, 0)) / weekly_imp_events as weekly_cov_events

from (select
          date_trunc('week', bonus_date)::date                as week_start,
          coalesce(cz_range, '0-4.99')                        as cz_range,
          case when b.b_user_id is not null then 1 else 0 end as is_PU_30d,
          sum(case when bonus_type_id = 66 and face_multiplier = 140 then 1 else 0 end) as weekly_imp_events,
          count(distinct case
                             when bonus_type_id = 66 and face_multiplier = 140 then user_id
                             else null end)                   as weekly_imp_users,
          sum(case when bonus_type_id = 587 and face_multiplier = 140 then 1 else 0 end) as weekly_trx

      from dwh.fact_sm_user_bonuses a
               /*PUs in the last 30d*/
               left join (select distinct user_id as b_user_id
                          from dwh.fact_sm_user_transactions
                          where tran_date >= current_date - 30
                            and gross_amount > 0
               ) b on a.user_id = b.b_user_id
               /*user profile - cz*/
               left join (select
                              user_id,
                              case
                                  when coalesce(cz_price_cut_test, 0) = 0 then '0-4.99'
                                  when coalesce(cz_price_cut_test, 0) >= 5 and coalesce(cz_price_cut_test, 0) < 10 then '5-9.99'
                                  when coalesce(cz_price_cut_test, 0) >= 10 and coalesce(cz_price_cut_test, 0) < 20 then '10-19.99'
                                  when coalesce(cz_price_cut_test, 0) >= 20 then '20+'
                                  else '0-4.99' end as cz_range
                          from dwh.sm_user_profile_datamining_snapshot
                          where snapshot_date = current_date - 1
               ) profile on a.user_id = profile.user_id

      where 1 = 1
        and bonus_date >= '2025-01-13'
        and bonus_date < current_date
        and bonus_type_id in (66, 587) --impression, purchase
        and face_multiplier = 140 --LBP
      group by 1, 2, 3) a

         /*payments*/
         left join (select
                        date_trunc('week', tran_date)::date       as p_week_start,
                        coalesce(cz_range, '0-4.99')              as p_cz_range,
                        case when b.b_user_id is not null then 1 else 0 end as p_is_PU_30d,
                        count(distinct user_id)                   as weekly_PUs,
                        sum(gross_amount)                         as weekly_gross_amount,
                        sum(net_amount)                           as weekly_net_amount

                    from dwh.fact_sm_user_transactions a
                             /*PUs in the last 30d*/
                             left join (select distinct user_id as b_user_id
                                        from dwh.fact_sm_user_transactions
                                        where tran_date >= current_date - 30
                                          and gross_amount > 0
                             ) b on a.user_id = b.b_user_id
                             /*user profile - cz*/
                             left join (select
                                            user_id,
                                            case
                                                when coalesce(cz_price_cut_test, 0) = 0 then '0-4.99'
                                                when coalesce(cz_price_cut_test, 0) >= 5 and coalesce(cz_price_cut_test, 0) < 10 then '5-9.99'
                                                when coalesce(cz_price_cut_test, 0) >= 10 and coalesce(cz_price_cut_test, 0) < 20 then '10-19.99'
                                                when coalesce(cz_price_cut_test, 0) >= 20 then '20+'
                                                else '0-4.99' end as cz_range
                                        from dwh.sm_user_profile_datamining_snapshot
                                        where snapshot_date = current_date - 1
                             ) profile on a.user_id = profile.user_id

                    where 1 = 1
                      and tran_date >= '2025-01-13'
                      and tran_date < current_date
                      and product_name = 'LBP'
                      and gross_amount > 0
                    group by 1, 2, 3

         ) b on a.week_start = b.p_week_start
    and a.cz_range = b.p_cz_range
    and a.is_PU_30d = b.p_is_PU_30d;
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `business-context.md` - LBP business context