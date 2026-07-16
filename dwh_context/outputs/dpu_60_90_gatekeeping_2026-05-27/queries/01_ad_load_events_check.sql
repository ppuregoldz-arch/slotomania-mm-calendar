/*
DPU 60-90 Gatekeeping Query 1: Ad Load Events Check
===================================================
Purpose: Validate DPU_60_90 users are receiving ad load events on launch day
Date: 2026-05-27 Launch

EXECUTION: Run ON LAUNCH DAY (2026-05-27) only
Expected: >0 AD_LOAD_SUCCEEDED events for DPU_60_90 users

Note: placement/placement_trigger will be NULL for load events 
(placement assigned later when user creates trigger)
*/

-- Check ad load events by date for DPU_60_90 users
select
    event_date,
    count(distinct user_id) as unique_users,
    count(*) as total_events,
    case when count(*) > 0 then 'ok' else 'wrong' end as validation_status
    
from (
    select 
        user_id,
        event_date,
        event_ts,
        event_type
    from dwh.sm_fact_rv_client_events
    where 1 = 1
      and user_id not in (select distinct user_id from dwh.playtika_users)
      and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
      and event_type = 'AD_LOAD_SUCCEEDED'
      and event_date = current_date  -- Today only (tomorrow will be checked when it becomes today)
      and user_id in (
          -- DPU_60_90 users from latest snapshot
          select user_id 
          from dwh.sm_user_profile_datamining_snapshot 
          where event_date_datamining = current_date
            and rv_segment_opportunistic = 'DPU_60_90'
      )
) events

group by 1
order by event_date;
