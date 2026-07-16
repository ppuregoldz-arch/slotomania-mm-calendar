/*
DPU 60-90 Gatekeeping Query 4: Placement Coverage Check
======================================================
Purpose: Simple check - are DPU_60_90 users receiving ads from all placements?
Expected: >0 events for Offers, Cloud, and Shiny Show placements
*/

-- Simple placement coverage check
select
    case 
        when placement ilike '%shiny%' or placement_trigger in ('bomb_pick', 'wait_buy_extra_pick') then 'Shiny Show'
        when placement_trigger in ('RETURN_TO_LOBBY', 'RUN_OUT_OF_COINS') then 'Offers'  
        when placement_trigger in ('floating-cloud-lobby', 'floating-cloud-slot') then 'Cloud'
        else 'Other'
    end as placement_category,
    count(distinct user_id) as unique_users,
    count(*) as total_events,
    case when count(*) > 0 then 'ok' else 'wrong' end as validation_status
    
from dwh.sm_fact_rv_client_events a
join (
    select user_id 
    from dwh.sm_user_profile_datamining_snapshot
    where event_date_datamining = current_date
      and rv_segment_opportunistic = 'DPU_60_90'
) b on a.user_id = b.user_id

where a.event_date = current_date
  and a.event_type = 'AD_IMPRESSION'
  and a.user_id not in (select distinct user_id from dwh.playtika_users)
  
group by 1
order by 1;