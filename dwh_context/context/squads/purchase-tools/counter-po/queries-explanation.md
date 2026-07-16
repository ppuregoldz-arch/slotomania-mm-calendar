# Counter PO - Queries

**Note**: This file contains only queries provided by the user, not queries created during conversations.

## Query Inventory

### 1. Groups Per User Analysis
**Purpose**: Validate that users are not exposed to multiple Counter PO groups simultaneously  
**Category**: Gatekeeping / Exposure Control  
**Business Rule**: Each user should typically see only one Counter PO group to maintain controlled scarcity

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

### 2. Configuration Validation Check
**Purpose**: Validate Counter PO pricing, coins, and test group configuration consistency  
**Category**: Gatekeeping / Configuration Validation  
**Business Rule**: Ensure pricing matches configuration, test groups are correct, and coin calculations are accurate

```sql
/*configuration check*/
select *,
       case when group_name = 'Test_A' then 'ok' else 'wrong' end              as test_groups_check,
       case when round(config_price) = round(price) then 'ok' else 'wrong' end as price_check,
       case when config_coins = payment_quantity then 'ok' else 'wrong' end    as coins_check,
       payment_quantity / config_coins                                         as coins_ratio
from (select
          a.*,
          t.group_name,
          b.cz_price_cut_test,
          c.config_price,
          config_base_coins,
          d.Tier_multiplier,
          f.prestige_multiplier,
          config_base_coins * Tier_multiplier * prestige_multiplier * 2 as config_coins
/*payments*/
      from (SELECT
                Product_Name,
                gross_amount,
                price,
                tran_id,
                user_id,
                tran_date,
                tran_ts,
                tier_id,
--                 (payment_quantity / 2.5) *2 as payment_quantity
                payment_quantity
            from dwh.sm_fact_payments a

                     left join sm_draft.SM_DIM_Products b
                               on a.sku_id = b.sku_id and
                                  a.transaction_source_type_id = b.transaction_source_type_id
            where 1 = 1
              and tran_status_id = 2
              and artificial_ind = 0
              and is_test = 0
              and user_id > 0
              and Product_Name ilike '%counter%'
--               and user_id=154000066502254
--               and tran_ts >= '2026-05-20 11:00:00'
              and tran_date >= current_date) a
               /*datamining- cz*/
               left join (select
                              event_date_datamining,
                              user_id                        as b_user_id,
                              coalesce(cz_price_cut_test, 0) as cz_price_cut_test
                          from dwh.sm_user_profile_datamining_snapshot
                          where 1 = 1
                            and event_date_datamining >= current_date) b
                         on a.user_id = b.b_user_id and a.tran_date = b.event_date_datamining
/*pricing table*/
               left join (select
                              cz_from,
                              cz_to,
                              pricing_level,
                              price      as config_price,
                              base_coins as config_base_coins
                          from sm_draft.pricing_level_prices_base_coins_base_gems
                          where 1 = 1
                            and pricing_level = 'High') c
                         on b.cz_price_cut_test between c.cz_from and c.cz_to
/*tier multiplier*/
               left join (select distinct
                              tier_id,
                              tier_multiplier
                          from dwh.Dim_Coins_Value) d
                         on a.tier_id = d.tier_id
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
                          where 1 = 1) e
                         on a.user_id = e.user_id and a.tran_ts between e.event_ts and e.lead_event_ts
/*prestige level multipliers*/
               left join (select *,
                                 premium_multiplier as prestige_multiplier
                          from sm_draft.new_premium_multipliers_12_01) f
                         on e.new_precious_level = f.p_level
/*test groups*/
               left join (select distinct
                              a.user_id as t_user_id,
                              group_name,
                              allocation_percentage
                          from sm_ds.abtest_user_allocations a
                                   left join sm_ds.abtest_dim_test t on a.test_id = t.ab_test_id
                                   left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                          where test_id = 'i58UEhWuzT') t
                         on a.user_id = t.t_user_id) A;
```

### 3. Group Size and User Distribution Validation
**Purpose**: Monitor Counter PO group lifecycle and validate group size constraints  
**Category**: Gatekeeping / Group Management  
**Business Rules**: Max 10,000 users per group, max 1,205 groups, proper group closure triggers

```sql
/*num of users per group (up to 10,000) & num of groups (up to 1205)*/
SELECT
    a.offer_group_id,
    a.event_details,
    a.group_size,
    min_event_ts_per_group,
    coalesce(b.distinct_users, 0)                                               AS distinct_users,
    case when coalesce(b.distinct_users, 0) <= 10000 THEN 'ok' ELSE 'wrong' END AS max_users_per_group,
    case
        when a.event_details = 'Full' and coalesce(b.distinct_users, 0) = 10000 THEN 'ok'
        when a.event_details = 'Sold_out' and coalesce(b.distinct_users, 0) < 10000 and
             coalesce(b.distinct_users, 0) >= 100 THEN 'ok'
        ELSE 'wrong'
        END                                                                     AS user_per_group_check,
    count(a.offer_group_id) over ()                                             as num_of_groups
/*groups table*/
FROM (SELECT
          template_id,
          h.offer_group_id,
          max(event_details) AS event_details,
          max(h.group_size)  AS group_size,
          min(event_ts)      as min_event_ts_per_group
      FROM dwh.sm_str_offer_group_history AS h
      WHERE 1 = 1
        and template_id = 227705 --- update
--         AND h.offer_group_id IS NOT NULL
      GROUP BY 1, 2) AS a
         /*po2*/
         LEFT JOIN (SELECT
                        x.template_id,
                        x.offer_group_id,
                        count(DISTINCT x.user_id) AS distinct_users
                    FROM (SELECT
                              po.user_id,
                              po.offer_group_id,
                              template_id,
                              offer_status_ts,
                              offer_name
                          FROM dwh.fact_sm_user_offer_history_po2 AS po
                          WHERE 1 = 1
                            and po.offer_status_ts::DATE >= current_date
                            and template_id = 227705
--                             and offer_status_ts = current_date
--                             and offer_status_ts >= '2026-05-13 12:30:00'
                            AND po.offer_group_id IS NOT NULL
                            AND po.user_id > 0) AS x
                    GROUP BY 1,
                             2) AS b
                   ON a.template_id = b.template_id
                       AND a.offer_group_id = b.offer_group_id;
```

## Key Gatekeeping Validations

### **Test Configuration**
- **Template ID**: 227705
- **Test ID**: 'i58UEhWuzT'  
- **Expected Group**: 'Test_A' only
- **Pricing Level**: 'High'

### **Business Rules Monitored**
1. **Single Group Exposure**: Users should see only one Counter PO group
2. **Group Size Limits**: Maximum 10,000 users per group
3. **Group Count Limits**: Maximum 1,205 total groups
4. **Configuration Consistency**: Prices and coins match expected calculations
5. **Proper Group Closure**: Groups close correctly via 'Full' (10K users) or 'Sold_out' (counter reached zero)

### **Key Tables Used**
- `dwh.fact_sm_user_offer_history_po2` - User offer impressions and group assignments
- `dwh.sm_str_offer_group_history` - Group lifecycle events and closure reasons
- `dwh.sm_fact_payments` - Counter PO purchase transactions
- `sm_ds.abtest_user_allocations` - A/B test group assignments
- `dwh.sm_user_profile_datamining_snapshot` - User CZ segmentation
- `sm_draft.pricing_level_prices_base_coins_base_gems` - Pricing configuration

---
**Source**: User-provided Counter PO gatekeeping queries for feature validation and monitoring.