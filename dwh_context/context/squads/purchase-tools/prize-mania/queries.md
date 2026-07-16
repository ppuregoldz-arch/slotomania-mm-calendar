# Prize Mania - SQL Queries

**Note**: This file contains actual SQL queries provided by the user for Prize Mania analysis and investigations.

## Query Inventory

### 1. Price & SlotoBucks Amount Validation
**Purpose**: Validate Prize Mania pricing configuration and SlotoBucks bonus amounts
**Tables**: `kafka.src_sm_prize_mania`, `dwh.fact_sm_user_transactions`, `sm_draft.prize_mania_config`
**Validation**: Check config_price = gross_amount and gross_amount = bonus_amount

```sql
/*price check & SB amount check*/ 

select *,
       case when round(config_price) = round(gross_amount) then 'ok' else 'wrong' end as price_check,
       case when round(gross_amount) = round(bonus_amount) then 'ok' else 'wrong' end as SB_check
/*prize mania data*/
from (select
          user_id,
          event_ts,
          event_date,
          status,
          reward_id,
          mission_id,
          schedule_id,
          origin_transaction_id
      from kafka.src_sm_prize_mania
      where 1 = 1
--         and user_id = 154000066502254
        and event_ts >= '2026-03-24 11:00:00'
--         and status = 'FINISHED' -- collected
        and status = 'FINISHED_UNCOLLECTED' -- purchased without collecting prizes
      order by event_ts) A

         /*bonuses- kafka - SB*/
         left join (select
                        user_id,
                        bonus_date,
                        bonus_ts,
                        bonus_amount,
                        origin_transaction_id as t_origin_transaction_id
                    from kafka.src_sm_user_bonuses
                    where bonus_type_id = 12 --slotobucks
         ) bonus on a.origin_transaction_id = bonus.t_origin_transaction_id

         /*payments*/
         left join (select
                        origin_transaction_id,
                        tran_ts,
                        tran_date,
                        user_id,
                        gross_amount,
                        price
                    from dwh.fact_sm_user_transactions
                    where product_name = 'Prize Mania'
         ) payments on a.origin_transaction_id = payments.origin_transaction_id

         /*configuration*/
         left join (select
                        mission_id,
                        reward_id,
                        schedule_id,
                        price as config_price
                    from sm_draft.prize_mania_config
         ) config on a.mission_id = config.mission_id
             and a.reward_id = config.reward_id
             and a.schedule_id = config.schedule_id;
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence  
- `business-context.md` - Prize Mania business context