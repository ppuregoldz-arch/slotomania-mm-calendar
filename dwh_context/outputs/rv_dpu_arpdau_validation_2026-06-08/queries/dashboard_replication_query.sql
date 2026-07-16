/*
DASHBOARD REPLICATION QUERY - Manual ARPDAU Calculation
=======================================================

Purpose: Replicate dashboard results by replacing parameters with actual values
Target Date: 2026-06-01 (promo_date)
Parameters Used:
- test_id = 'xmXDU4lG4J'
- start_date = '2026-05-17' (Parameter 1)
- end_date = '2026-06-08' (Parameter 2)

Goal: Calculate ARPDAU per segment matching dashboard values
*/

SELECT
    '2026-06-01' as analysis_date,
    CASE WHEN group_name = 'Control' THEN 'Test_C'
         WHEN group_name = 'Test_C' THEN 'Control'
         ELSE group_name END as group_name,
    is_during_users,
    COALESCE(rv_dpu_tenure_split_feb16, 'DPU 180+') as rv_dpu_tenure_split_feb16,
    COUNT(DISTINCT a.user_id) as DAU,
    SUM(COALESCE(net_amount, 0)) as rev,
    SUM(COALESCE(revenue, 0)) as RV_rev,
    -- Manual ARPDAU calculation matching dashboard formula
    ROUND((COALESCE(SUM(revenue), 0) + COALESCE(SUM(net_amount), 0))::numeric / 
          NULLIF(COUNT(DISTINCT a.user_id), 0), 2) as ARPDAU
    
/*hourly - agg to user & day*/
FROM (
    SELECT
        DATE(calc_hour_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') as promo_date,
        user_id
    FROM agg.agg_sm_hourly_user_stats
    WHERE DATE(calc_hour_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') = '2026-06-01'::date
    GROUP BY 1,2
) a

/*test groups*/
LEFT JOIN (
    SELECT DISTINCT
        a.user_id as t_user_id,
        group_name,
        allocation_percentage,
        CASE WHEN during_users.user_id IS NOT NULL THEN true ELSE false END is_during_users
    FROM sm_ds.abtest_user_allocations a
    LEFT JOIN sm_ds.abtest_dim_test t ON a.test_id = t.ab_test_id
    LEFT JOIN sm_ds.abtest_dim_group g ON a.group_test_id = g.test_group_id
    LEFT JOIN (
        SELECT DISTINCT user_id
        FROM dwh.fact_sm_sessions_kafka
        WHERE DATE(session_creation_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') >= '2026-05-17'::date
    ) during_users ON a.user_id = during_users.user_id
    WHERE test_id = 'xmXDU4lG4J'
) t ON a.user_id = t.t_user_id

/*payments & CZ - FIXED TO SINGLE DAY*/
LEFT JOIN (
    SELECT
        a.user_id,
        DATE(tran_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') promo_date,
        COUNT(DISTINCT tran_id) as tran_id,
        SUM(net_amount) as net_amount
    FROM dwh.sm_fact_payments a
    WHERE 1 = 1
        AND tran_status_id = 2
        AND artificial_ind = 0
        AND a.user_id NOT IN (SELECT DISTINCT user_id FROM dwh.playtika_users)
        AND a.user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_fact_journey_state_notifications WHERE step_id = 539265)
        AND is_test = 0
        AND a.user_id > 0
        -- CORRECTED: Single day filter instead of wide range
        AND DATE(tran_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') = '2026-06-01'::date
    GROUP BY 1,2
) b ON a.user_id = b.user_id AND a.promo_date = b.promo_date

/*rv main KPIs - FIXED TO SINGLE DAY*/
LEFT JOIN (
    SELECT 
        user_id,
        DATE(event_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') as promo_date,
        SUM(revenue) as revenue
    FROM agg.agg_sm_rv_client_displayed_events
    WHERE DATE(event_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') = '2026-06-01'::date
    GROUP BY 1,2
) c ON a.user_id = c.user_id AND a.promo_date = c.promo_date

/*RV segment - DPU tenure split*/
LEFT JOIN (
    SELECT
        user_id as dpu_tenure_feb16_user_id,
        CASE
            WHEN rv_segment_opportunistic = 'DPU_90+'
                AND (('2026-02-16'::DATE - last_purchase_promo_date) > 180 OR last_purchase_promo_date IS NULL)
            THEN 'DPU 180+'
            WHEN rv_segment_opportunistic = 'DPU_90+'
                AND ('2026-02-16'::DATE - last_purchase_promo_date) > 90
                AND ('2026-02-16'::DATE - last_purchase_promo_date) <= 180
            THEN 'DPU_90-180'
            ELSE rv_segment_opportunistic
        END AS rv_dpu_tenure_split_feb16
    FROM (
        SELECT
            user_id,
            rv_segment_opportunistic
        FROM dwh.sm_user_profile_datamining_snapshot
        WHERE event_date_datamining = '2026-05-17'::date
    ) AS seg
    LEFT JOIN (
        SELECT
            user_id as last_trx_user_id,
            MAX(promo_date) as last_purchase_promo_date
        FROM agg.agg_sm_daily_promotion_stats
        WHERE promo_date < '2026-05-17'::date
            AND gross_rev > 0
        GROUP BY 1
    ) AS last_trx ON seg.user_id = last_trx.last_trx_user_id
) AS dpu_tenure_feb16 ON a.user_id = dpu_tenure_feb16.dpu_tenure_feb16_user_id

WHERE 1=1
    AND t.t_user_id IS NOT NULL  -- Only users in test
    AND COALESCE(rv_dpu_tenure_split_feb16, 'DPU 180+') IN ('DPU 180+', 'DPU_90-180')
    AND CASE WHEN group_name = 'Control' THEN 'Test_C' 
             WHEN group_name = 'Test_C' THEN 'Control' 
             ELSE group_name END IN ('Control', 'Test_A')

GROUP BY 1,2,3,4
ORDER BY 2,4;

-- Additional validation query to check if filtering on is_during_users matters
SELECT
    'WITH during_users filter' as filter_type,
    CASE WHEN group_name = 'Control' THEN 'Test_C'
         WHEN group_name = 'Test_C' THEN 'Control'
         ELSE group_name END as group_name,
    COALESCE(rv_dpu_tenure_split_feb16, 'DPU 180+') as rv_dpu_tenure_split_feb16,
    COUNT(DISTINCT a.user_id) as DAU,
    ROUND(SUM(COALESCE(net_amount, 0)), 1) as rev,
    ROUND(SUM(COALESCE(revenue, 0)), 1) as RV_rev,
    ROUND((COALESCE(SUM(revenue), 0) + COALESCE(SUM(net_amount), 0))::numeric / 
          NULLIF(COUNT(DISTINCT a.user_id), 0), 2) as ARPDAU
FROM (
    SELECT
        DATE(calc_hour_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') as promo_date,
        user_id
    FROM agg.agg_sm_hourly_user_stats
    WHERE DATE(calc_hour_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') = '2026-06-01'::date
    GROUP BY 1,2
) a
LEFT JOIN (
    SELECT DISTINCT
        a.user_id as t_user_id,
        group_name,
        CASE WHEN during_users.user_id IS NOT NULL THEN true ELSE false END is_during_users
    FROM sm_ds.abtest_user_allocations a
    LEFT JOIN sm_ds.abtest_dim_test t ON a.test_id = t.ab_test_id
    LEFT JOIN sm_ds.abtest_dim_group g ON a.group_test_id = g.test_group_id
    LEFT JOIN (
        SELECT DISTINCT user_id
        FROM dwh.fact_sm_sessions_kafka
        WHERE DATE(session_creation_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') >= '2026-05-17'::date
    ) during_users ON a.user_id = during_users.user_id
    WHERE test_id = 'xmXDU4lG4J'
) t ON a.user_id = t.t_user_id
LEFT JOIN (
    SELECT
        a.user_id,
        DATE(tran_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') promo_date,
        SUM(net_amount) as net_amount
    FROM dwh.sm_fact_payments a
    WHERE tran_status_id = 2 AND artificial_ind = 0 AND is_test = 0 AND a.user_id > 0
        AND a.user_id NOT IN (SELECT DISTINCT user_id FROM dwh.playtika_users)
        AND a.user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_fact_journey_state_notifications WHERE step_id = 539265)
        AND DATE(tran_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') = '2026-06-01'::date
    GROUP BY 1,2
) b ON a.user_id = b.user_id AND a.promo_date = b.promo_date
LEFT JOIN (
    SELECT user_id,
        DATE(event_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') as promo_date,
        SUM(revenue) as revenue
    FROM agg.agg_sm_rv_client_displayed_events
    WHERE DATE(event_ts::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') = '2026-06-01'::date
    GROUP BY 1,2
) c ON a.user_id = c.user_id AND a.promo_date = c.promo_date
LEFT JOIN (
    SELECT
        user_id as dpu_tenure_feb16_user_id,
        CASE
            WHEN rv_segment_opportunistic = 'DPU_90+'
                AND (('2026-02-16'::DATE - last_purchase_promo_date) > 180 OR last_purchase_promo_date IS NULL)
            THEN 'DPU 180+'
            WHEN rv_segment_opportunistic = 'DPU_90+'
                AND ('2026-02-16'::DATE - last_purchase_promo_date) > 90
                AND ('2026-02-16'::DATE - last_purchase_promo_date) <= 180
            THEN 'DPU_90-180'
            ELSE rv_segment_opportunistic
        END AS rv_dpu_tenure_split_feb16
    FROM (
        SELECT user_id, rv_segment_opportunistic
        FROM dwh.sm_user_profile_datamining_snapshot
        WHERE event_date_datamining = '2026-05-17'::date
    ) AS seg
    LEFT JOIN (
        SELECT user_id as last_trx_user_id, MAX(promo_date) as last_purchase_promo_date
        FROM agg.agg_sm_daily_promotion_stats
        WHERE promo_date < '2026-05-17'::date AND gross_rev > 0
        GROUP BY 1
    ) AS last_trx ON seg.user_id = last_trx.last_trx_user_id
) AS dpu_tenure_feb16 ON a.user_id = dpu_tenure_feb16.dpu_tenure_feb16_user_id
WHERE t.t_user_id IS NOT NULL
    AND t.is_during_users = TRUE  -- FILTER ON DURING USERS ONLY
    AND COALESCE(rv_dpu_tenure_split_feb16, 'DPU 180+') IN ('DPU 180+', 'DPU_90-180')
    AND CASE WHEN group_name = 'Control' THEN 'Test_C' 
             WHEN group_name = 'Test_C' THEN 'Control' 
             ELSE group_name END IN ('Control', 'Test_A')
GROUP BY 1,2,3
ORDER BY 2,3;

/*
EXPECTED RESULTS TO MATCH DASHBOARD:
====================================
Control DPU 90-180: DAU ~2,025, rev ~1,409.7, RV_rev ~0, ARPDAU ~0.70
Control DPU 180+: DAU ~14,373, rev ~1,638.9, RV_rev ~0, ARPDAU ~0.11
Test_A DPU 90-180: DAU ~2,042, rev ~1,252.1, RV_rev ~21.1, ARPDAU ~0.62
Test_A DPU 180+: DAU ~14,209, rev ~1,303.9, RV_rev ~181.3, ARPDAU ~0.10
*/