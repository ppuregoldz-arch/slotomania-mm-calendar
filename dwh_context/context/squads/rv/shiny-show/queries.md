# Shiny Show - SQL Queries

**Note**: This file contains actual SQL queries provided by the user for Shiny Show analysis and investigations.

## Query Inventory

### 1. Shiny Show Floor & Trigger Validation
**Purpose**: Validate Shiny Show placement triggers fire on correct floors and respect daily caps
**Tables**: `dwh.sm_fact_rv_client_events`, `sm_ds.abtest_user_allocations`
**Validation**: Check MOLE (floors 6-12, 2/day) and Extra Pick (floor 10 only, 1/day) rules

```sql
select 
    user_id,
    event_date,
    event_ts,
    placement,
    placement_trigger,
    event_type,
    REGEXP_SUBSTR(feature_additional_data, '"level"\\s*:\\s*([0-9]+)', 1, 1, '', 1)::INT + 1 as Shiny_Show_floor,
    case 
        when placement_trigger = 'bomb_pick' and 
             (REGEXP_SUBSTR(feature_additional_data, '"level"\\s*:\\s*([0-9]+)', 1, 1, '', 1)::INT + 1) between 6 and 12 
        then 'ok'
        when placement_trigger = 'wait_buy_extra_pick' and 
             (REGEXP_SUBSTR(feature_additional_data, '"level"\\s*:\\s*([0-9]+)', 1, 1, '', 1)::INT + 1) = 10 
        then 'ok'
        else 'wrong'
    end as floor_trigger_validation,
    
    test_group,
    case when test_group in ('Test_A', 'Test_B') then 'ok' else 'wrong' end as test_group_validation,
    
    revenue,
    min_ecpm_threshold,
    dynamic_ecpm,
    case when revenue >= (min_ecpm_threshold / 1000.0) * dynamic_ecpm then 'ok' else 'wrong' end as ecpm_validation

from (
    select
        user_id,
        event_date,
        event_ts,
        placement,
        placement_trigger,
        event_type,
        feature_additional_data,
        revenue
    from dwh.sm_fact_rv_client_events
    where 1 = 1
      and event_date >= current_date - 7
      and placement = 'Shiny'
      and event_type = 'IMPRESSION'
      and placement_trigger in ('bomb_pick', 'wait_buy_extra_pick')
) events

left join (
    select 
        user_id,
        group_name as test_group
    from sm_ds.abtest_user_allocations 
    where test_id = 'xmXDU4lG4J'
) tests on events.user_id = tests.user_id

left join (
    select 
        user_id,
        rv_opportunistic_config_buckets,
        RV_opportunistic_dynamic_ecpm as dynamic_ecmp,
        case 
            when rv_opportunistic_config_buckets in (1, 2, 3) then config_min_ecpm
            when rv_opportunistic_config_buckets = 10 then 30  -- NPU/DPU floor-specific thresholds
            when rv_opportunistic_config_buckets = 20 then 40
            -- Add other bucket thresholds as needed
            else config_min_ecpm
        end as min_ecpm_threshold
    from dwh.sm_user_profile_datamining_snapshot
    where snapshot_date = current_date - 1
) profile on events.user_id = profile.user_id

order by event_ts;
```

### 2. Daily Cap Enforcement Check
**Purpose**: Validate daily caps are enforced (2 MOLE + 1 Extra Pick per day)
**Tables**: `dwh.sm_fact_rv_client_events`
**Validation**: Count daily triggers per user and flag violations

```sql
select 
    user_id,
    event_date,
    sum(case when placement_trigger = 'bomb_pick' then 1 else 0 end) as daily_mole_triggers,
    sum(case when placement_trigger = 'wait_buy_extra_pick' then 1 else 0 end) as daily_extra_pick_triggers,
    case 
        when sum(case when placement_trigger = 'bomb_pick' then 1 else 0 end) > 2 then 'VIOLATION: MOLE cap exceeded'
        when sum(case when placement_trigger = 'wait_buy_extra_pick' then 1 else 0 end) > 1 then 'VIOLATION: Extra Pick cap exceeded'  
        else 'ok'
    end as daily_cap_validation

from dwh.sm_fact_rv_client_events
where 1 = 1
  and event_date >= current_date - 7
  and placement = 'Shiny'
  and event_type = 'IMPRESSION'
  and placement_trigger in ('bomb_pick', 'wait_buy_extra_pick')

group by 1, 2
having sum(case when placement_trigger = 'bomb_pick' then 1 else 0 end) > 2
    or sum(case when placement_trigger = 'wait_buy_extra_pick' then 1 else 0 end) > 1

order by event_date, user_id;
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `business-context.md` - Shiny Show business context