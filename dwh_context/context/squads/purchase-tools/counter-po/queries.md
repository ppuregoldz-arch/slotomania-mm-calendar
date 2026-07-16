# Counter PO - SQL Queries

**Note**: This file contains actual SQL queries provided by the user for Counter PO analysis and investigations.

## Query Inventory

### 1. Groups Per User Analysis
**Purpose**: Analyze number of offer groups per user for Counter PO gatekeeping
**Tables**: `dwh.fact_sm_user_offer_history_po2`
**Validation**: Count groups distribution for template 227705

```sql
/*number of groups per user*/

select
    b_offer_group_id as     groups_per_user,
    count(distinct user_id) distinct_users
from (SELECT
          user_id,
          count(distinct offer_group_id) as b_offer_group_id

      FROM dwh.fact_sm_user_offer_history_po2 a
      where 1 = 1
--         and offer_status_ts >= '2026-05-13 11:00:00'
        and offer_status_ts::date >= current_date - 7
        and template_id = 227705
        and offer_group_id is not null
        and offer_status_id = 'IMPRESSION'
      group by 1) A
group by 1;
```

### 2. Configuration Check & Test Group Validation
**Purpose**: Validate Counter PO configuration and test group assignments
**Tables**: `dwh.fact_sm_user_offer_history_po2`, user profiles, A/B test allocation
**Validation**: Check Test_A assignment, price configuration, and purchase matching

```sql
/*configuration check*/
select *,
       case when group_name = 'Test_A' then 'ok' else 'wrong' end              as test_groups_check,
       case when round(config_price) = round(price) then 'ok' else 'wrong' end as price_check,
       case when round(gross_amount) = round(config_price) then 'ok' else 'wrong' end as gross_amount_check
/*counter po data*/
from (select
          user_id,
          offer_status_ts,
          offer_status_ts::date as offer_date,
          offer_status_id,
          offer_group_id,
          template_id,
          mission_id,
          reward_id,
          schedule_id,
          origin_transaction_id
      from dwh.fact_sm_user_offer_history_po2 a
      where 1 = 1
--         and user_id = 154000066502254
        and offer_status_ts >= '2026-05-13 11:00:00'
        and template_id = 227705
        and offer_group_id is not null
        and offer_status_id = 'IMPRESSION'
      order by offer_status_ts) A

         /*user profile - test groups*/
         left join (select
                        user_id,
                        group_name
                    from sm_ds.abtest_user_allocations
                    where test_id = 'xmXDU4lG4J'
         ) t on a.user_id = t.user_id

         /*configuration*/
         left join (select
                        mission_id,
                        reward_id,
                        schedule_id,
                        price as config_price
                    from sm_draft.counter_po_po2_config
         ) config on a.mission_id = config.mission_id
             and a.reward_id = config.reward_id
             and a.schedule_id = config.schedule_id

         /*payments*/
         left join (select
                        origin_transaction_id,
                        tran_ts,
                        tran_date,
                        user_id,
                        gross_amount,
                        price
                    from dwh.fact_sm_user_transactions
                    where product_name = 'Counter PO'
         ) payments on a.origin_transaction_id = payments.origin_transaction_id;
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `business-context.md` - Counter PO business context