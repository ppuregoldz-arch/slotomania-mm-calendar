# Dice Deluxe - SQL Queries

**Note**: This file contains actual SQL queries provided by the user for Dice Deluxe analysis and investigations.

## Query Inventory

### 1. Dice Deluxe Conversion Analysis
**Purpose**: Weekly conversion analysis for Dice Deluxe by CZ range and PU status
**Tables**: `dwh.fact_sm_user_bonuses`, user segmentation
**Validation**: Analyze impression to purchase conversion rates

```sql
select
    'Dice'                                                                          as                   product_name,
    a.week_start,
    coalesce(cz_range, '0-4.99')                                                    as                   cz_range,
    case when b.b_user_id is not null then 1 else 0 end                             as                   is_PU_30d,
    sum(case when bonus_type_id = 66 and face_multiplier = 150 then 1 else 0 end)   as                   weekly_imp_events,
    count(distinct case
                       when bonus_type_id = 66 and face_multiplier = 150 then user_id
                       else null end)                                               as                   weekly_imp_users,
    count(distinct case when bonus_type_id = 587 and face_multiplier = 150 then user_id else null end) as weekly_PUs,
    sum(case when bonus_type_id = 587 and face_multiplier = 150 then 1 else 0 end) as weekly_trx

from (select
          date_trunc('week', bonus_date)::date                as week_start,
          coalesce(cz_range, '0-4.99')                        as cz_range,
          case when b.b_user_id is not null then 1 else 0 end as is_PU_30d,
          a.*
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
        and face_multiplier = 150 --dice deluxe
     ) a
         /*PUs in the last 30d*/
         left join (select distinct user_id as b_user_id
                    from dwh.fact_sm_user_transactions
                    where tran_date >= current_date - 30
                      and gross_amount > 0
         ) b on a.user_id = b.b_user_id

group by 1, 2, 3, 4;
```

### 2. Test Group & Price Validation
**Purpose**: Validate only Test users receive Dice Deluxe and price configuration is correct
**Tables**: `dwh.fact_sm_user_transactions`, `sm_ds.abtest_user_allocations`, config tables
**Validation**: Check Test group assignment and pricing accuracy

```sql
/*price check & only test receiving*/

select *,
       case when group_name = 'Test' then 'ok' else 'wrong' end                    as only_test_users_receiving_dice_deluxe,
       case when round(gross_amount) = round(config_price) then 'ok' else null end as price_check
/*payments*/
from (SELECT
          tran_ts,
          tran_date,
          user_id,
          gross_amount,
--           price,
          case
              when Product_Name = 'Payment Page' and payment_page_type_id = 30 then 'Payment Page'
              when Product_Name = 'Payment Page' and payment_page_type_id != 30 then 'ROOC'
              when Product_Name = 'Gems' and payment_page_type_id = 62 then 'Gems Payment Page'
              when Product_Name = 'Gems' and payment_page_type_id = 30 then 'Gems Payment Page'
              else Product_Name end as Product_Name_updated
      FROM dwh.fact_sm_user_transactions
      where 1 = 1
        and tran_date >= '2025-01-13'
        and tran_date < current_date
        and product_name = 'Dice Deluxe'
      order by tran_ts) A

         /*user profile - test groups*/
         left join (select
                        user_id,
                        group_name
                    from sm_ds.abtest_user_allocations
                    where test_id = 'dice_deluxe_test'
         ) t on a.user_id = t.user_id

         /*configuration*/
         left join (select
                        price as config_price
                    from sm_draft.dice_deluxe_config
         ) config on 1=1;
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `business-context.md` - Dice Deluxe business context