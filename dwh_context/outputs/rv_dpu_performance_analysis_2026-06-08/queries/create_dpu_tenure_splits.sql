/*
DPU Tenure Segmentation - Custom 90-180 vs 180+ Day Splits
==========================================================

VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Entities: Sample users from DPU_90+ cohort with known last transaction dates
Validation Date Range: 2026-02-16 cohort definition
Raw Data Source: dwh.sm_user_profile, dwh.sm_user_profile_datamining_snapshot
Expected Result: Split DPU_90+ users into 90-180 days vs 180+ days tenure based on 2026-02-16
Actual Query Result: [To be validated after execution]
Validation Status: Pending
Notes: Uses last_transaction_ts from main profile table to calculate precise tenure

Purpose: Build custom 90-180 vs 180+ day tenure segments within fixed DPU cohort
Business Question: Do different DPU tenure segments show different Test_A vs Control impact?
Key Logic: Calculate days since last purchase as of 2026-02-16 for fixed cohort definition
*/

select 
    user_id,
    rv_segment_opportunistic,
    last_transaction_date,
    days_since_last_purchase_feb16,
    case 
        when days_since_last_purchase_feb16 between 90 and 180 then 'DPU_90-180'
        when days_since_last_purchase_feb16 > 180 then 'DPU_180+'
        else 'Other'
    end as dpu_tenure_segment,
    case 
        when days_since_last_purchase_feb16 between 90 and 180 then 1 else 0 
    end as is_dpu_90_180,
    case 
        when days_since_last_purchase_feb16 > 180 then 1 else 0 
    end as is_dpu_180_plus,
    
    -- Additional context fields
    ltv,
    user_level,
    cz_price_cut_test

/*DPU cohort with tenure calculation*/
from (
    select 
        profile.user_id,
        profile.rv_segment_opportunistic,
        
        -- Calculate days since last purchase as of 2026-02-16
        '2026-02-16'::date - main_profile.last_transaction_ts::date as days_since_last_purchase_feb16,
        main_profile.last_transaction_ts::date as last_transaction_date,
        
        -- User characteristics from datamining snapshot
        coalesce(main_profile.sum_net_amount, 0) as ltv,
        main_profile.user_level,
        profile.cz_price_cut_test
    
    /*fixed DPU_90+ cohort from 2026-02-16*/  
    from (
        select 
            user_id,
            rv_segment_opportunistic,
            cz_price_cut_test
        from dwh.sm_user_profile_datamining_snapshot
        where event_date_datamining = '2026-02-16'
          and rv_segment_opportunistic = 'DPU_90+'
          and user_id > 0
          and user_id not in (select distinct user_id from dwh.playtika_users)
          and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
    ) profile
    
    /*main user profile for transaction history*/
    left join dwh.sm_user_profile main_profile 
        on profile.user_id = main_profile.user_id
        
    where main_profile.last_transaction_ts is not null
      and main_profile.last_transaction_ts::date <= '2026-02-16'
      and '2026-02-16'::date - main_profile.last_transaction_ts::date >= 90
) tenure_data

order by days_since_last_purchase_feb16, user_id
limit 10000;