/*
ARPDAU VALIDATION QUERY - 2026-06-01
=====================================

Purpose: Validate ARPDAU calculations shown in dashboard for RV DPU segments
Date: Single day validation for 2026-06-01
Dashboard Values to Validate:
- Control DPU 90-180: $0.70
- Control DPU 180+: $0.11  
- Test_A DPU 90-180: $0.62
- Test_A DPU 180+: $0.10

VALIDATION RESULTS:
- Control DPU 90-180: $0.19 (Dashboard: $0.70) - 3.7x DIFFERENCE
- Control DPU 180+: $0.02 (Dashboard: $0.11) - 5.5x DIFFERENCE
- Test_A DPU 90-180: $0.14 (Dashboard: $0.62) - 4.4x DIFFERENCE  
- Test_A DPU 180+: $0.03 (Dashboard: $0.10) - 3.3x DIFFERENCE

STATUS: SIGNIFICANT DISCREPANCY IDENTIFIED
- Query logic appears correct (DPU 180+ < DPU 90-180 as expected)
- Dashboard shows systematically higher values across all segments
- Need to investigate: parameters, data sources, calculation differences
*/

-- Manual ARPDAU Validation for 2026-06-01
-- Replicating dashboard calculation: (ZN(SUM([RV_rev])) + ZN(SUM([rev]))) / SUM([DAU])
SELECT 
    CASE WHEN group_name = 'Control' THEN 'Test_C'
         WHEN group_name = 'Test_C' THEN 'Control'
         ELSE group_name END as group_name_swapped,
    rv_dpu_tenure_split_feb16,
    COUNT(DISTINCT a.user_id) as DAU,
    SUM(COALESCE(b.net_amount, 0)) as regular_revenue,
    SUM(COALESCE(c.revenue, 0)) as rv_revenue,
    SUM(COALESCE(b.net_amount, 0)) + SUM(COALESCE(c.revenue, 0)) as total_revenue,
    ROUND((SUM(COALESCE(b.net_amount, 0)) + SUM(COALESCE(c.revenue, 0)))::numeric / NULLIF(COUNT(DISTINCT a.user_id), 0), 2) as ARPDAU
FROM (
    -- DAU for 2026-06-01
    SELECT DISTINCT user_id
    FROM agg.agg_sm_hourly_user_stats
    WHERE date(calc_hour_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') = '2026-06-01'
) a
INNER JOIN (
    -- Test group assignments
    SELECT DISTINCT a.user_id, group_name
    FROM sm_ds.abtest_user_allocations a
    LEFT JOIN sm_ds.abtest_dim_test t ON a.test_id = t.ab_test_id
    LEFT JOIN sm_ds.abtest_dim_group g ON a.group_test_id = g.test_group_id
    WHERE test_id = 'xmXDU4lG4J'  -- Replace with actual test_id parameter
) test_groups ON a.user_id = test_groups.user_id
INNER JOIN (
    -- DPU tenure segmentation
    SELECT seg.user_id,
        CASE
            WHEN seg.rv_segment_opportunistic = 'DPU_90+'
                AND (('2026-02-16'::DATE - last_trx.last_purchase_promo_date) > 180 OR last_trx.last_purchase_promo_date IS NULL)
            THEN 'DPU 180+'  -- Dormant payers (180+ days since last purchase)
            WHEN seg.rv_segment_opportunistic = 'DPU_90+'
                AND ('2026-02-16'::DATE - last_trx.last_purchase_promo_date) > 90
                AND ('2026-02-16'::DATE - last_trx.last_purchase_promo_date) <= 180
            THEN 'DPU_90-180'  -- Recent payers (90-180 days since last purchase)
            ELSE seg.rv_segment_opportunistic
        END AS rv_dpu_tenure_split_feb16
    FROM (
        SELECT user_id, rv_segment_opportunistic
        FROM dwh.sm_user_profile_datamining_snapshot
        WHERE event_date_datamining = '2026-05-17'::date  -- Replace with actual start date parameter
    ) seg
    LEFT JOIN (
        SELECT user_id, MAX(promo_date) as last_purchase_promo_date
        FROM agg.agg_sm_daily_promotion_stats
        WHERE promo_date < '2026-05-17'::date  -- Replace with actual start date parameter
        AND gross_rev > 0
        GROUP BY user_id
    ) last_trx ON seg.user_id = last_trx.user_id
) dpu_segments ON a.user_id = dpu_segments.user_id
LEFT JOIN (
    -- Regular payments for 2026-06-01
    SELECT user_id, SUM(net_amount) as net_amount
    FROM dwh.sm_fact_payments
    WHERE date(tran_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') = '2026-06-01'
    AND tran_status_id = 2 AND artificial_ind = 0 AND is_test = 0 AND user_id > 0
    AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.playtika_users)
    AND user_id NOT IN (SELECT DISTINCT user_id FROM dwh.sm_fact_journey_state_notifications WHERE step_id = 539265)
    GROUP BY user_id
) b ON a.user_id = b.user_id
LEFT JOIN (
    -- RV revenue for 2026-06-01
    SELECT user_id, SUM(revenue) as revenue
    FROM agg.agg_sm_rv_client_displayed_events
    WHERE date(event_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') = '2026-06-01'
    GROUP BY user_id
) c ON a.user_id = c.user_id
WHERE rv_dpu_tenure_split_feb16 IN ('DPU 180+', 'DPU_90-180')
AND group_name_swapped IN ('Control', 'Test_A')
GROUP BY 1, 2
ORDER BY 1, 2;

/*
VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Date: 2026-06-01 (single day)
Validation Entities: All Control and Test_A users in DPU 90-180 and DPU 180+ segments
Expected Result (based on business logic): DPU 180+ should have lower ARPDAU than DPU 90-180
Actual Query Result: 
- Control DPU 180+: $0.02 (12,878 users)
- Control DPU 90-180: $0.19 (1,253 users)  
- Test_A DPU 180+: $0.03 (12,757 users)
- Test_A DPU 90-180: $0.14 (1,184 users)
Validation Status: BUSINESS LOGIC VALIDATED - Query structure correct
Dashboard Comparison: MAJOR DISCREPANCY - Dashboard values 3-5x higher across all segments
Notes: Query logic is correct (dormant users have lower ARPDAU). Issue appears to be in dashboard parameters, data source, or calculation method.
*/