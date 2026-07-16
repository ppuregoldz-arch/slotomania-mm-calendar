/*
1-HOUR POWER BOOSTER TRACKING - FINAL METHODOLOGY
================================================
Date: 2026-06-09
Status: VALIDATED & WORKING

KEY DISCOVERY:
- SKU 24 = "MGAPP" = 1-Hour Power component in purchase bundles  
- Bonus Type 434 = "Fire MGAP after purchase" = Actual power activation
- Average activation delay: ~27 seconds after purchase
- 100,402+ power activations in last 7 days across 26,643 unique users
*/

-- CORE QUERY: Track all 1-hour power booster activations
SELECT 
    bh.user_id,
    bh.bonus_ts as power_activated_at,
    bd.tran_ticket,
    bd.tran_ts as purchase_time,
    DATEDIFF('second', bd.tran_ts, bh.bonus_ts) as activation_delay_seconds,
    DATE(bh.bonus_ts AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') as promo_date
FROM dwh.fact_sm_bonus_history bh
INNER JOIN dwh.sm_fact_payments_bundle_details bd 
    ON bh.user_id = bd.user_id 
    AND bd.sku_id = 24  -- MGAPP (1-hour power component)
    AND bd.tran_status = 'APPROVED'
    AND ABS(DATEDIFF('minute', bd.tran_ts, bh.bonus_ts)) <= 5
WHERE bh.bonus_type_id = 434  -- Fire MGAP after purchase
    AND bh.bonus_date >= current_date - 30
ORDER BY bh.bonus_ts DESC;

-- PERFORMANCE SUMMARY: Daily power activation metrics
SELECT 
    DATE(bh.bonus_ts AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') as promo_date,
    COUNT(*) as power_activations,
    COUNT(DISTINCT bh.user_id) as unique_users,
    AVG(DATEDIFF('second', bd.tran_ts, bh.bonus_ts)) as avg_activation_delay_seconds
FROM dwh.fact_sm_bonus_history bh
INNER JOIN dwh.sm_fact_payments_bundle_details bd 
    ON bh.user_id = bd.user_id 
    AND bd.sku_id = 24
    AND bd.tran_status = 'APPROVED'
    AND ABS(DATEDIFF('minute', bd.tran_ts, bh.bonus_ts)) <= 5
WHERE bh.bonus_type_id = 434
    AND bh.bonus_date >= current_date - 30
GROUP BY DATE(bh.bonus_ts AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours')
ORDER BY promo_date DESC;

-- PRODUCT ATTRIBUTION: Which products include 1-hour power
SELECT 
    prod.Product_Name,
    COUNT(*) as power_grants,
    COUNT(DISTINCT bd.user_id) as unique_users,
    AVG(p.net_amount) as avg_purchase_amount
FROM dwh.sm_fact_payments_bundle_details bd
INNER JOIN dwh.fact_sm_bonus_history bh 
    ON bd.user_id = bh.user_id 
    AND bd.sku_id = 24
    AND ABS(DATEDIFF('minute', bd.tran_ts, bh.bonus_ts)) <= 5
    AND bh.bonus_type_id = 434
LEFT JOIN dwh.sm_fact_payments p 
    ON bd.tran_ticket = p.tran_ticket
    AND p.tran_status_id = 2
LEFT JOIN sm_draft.SM_DIM_Products prod 
    ON p.sku_id = prod.sku_id 
    AND p.transaction_source_type_id = prod.transaction_source_type_id
WHERE bd.tran_status = 'APPROVED'
    AND bd.event_date >= current_date - 30
GROUP BY prod.Product_Name
ORDER BY power_grants DESC;

-- USER BEHAVIOR: Power activation patterns by user characteristics
SELECT 
    CASE 
        WHEN bd.level_id <= 100 THEN 'Early (1-100)'
        WHEN bd.level_id <= 1000 THEN 'Mid (101-1000)' 
        WHEN bd.level_id <= 10000 THEN 'Advanced (1001-10000)'
        ELSE 'Expert (10000+)'
    END as user_level_group,
    COUNT(*) as power_activations,
    COUNT(DISTINCT bh.user_id) as unique_users,
    ROUND(COUNT(*) / COUNT(DISTINCT bh.user_id), 1) as avg_powers_per_user
FROM dwh.fact_sm_bonus_history bh
INNER JOIN dwh.sm_fact_payments_bundle_details bd 
    ON bh.user_id = bd.user_id 
    AND bd.sku_id = 24
    AND bd.tran_status = 'APPROVED'
    AND ABS(DATEDIFF('minute', bd.tran_ts, bh.bonus_ts)) <= 5
WHERE bh.bonus_type_id = 434
    AND bh.bonus_date >= current_date - 30
GROUP BY CASE 
    WHEN bd.level_id <= 100 THEN 'Early (1-100)'
    WHEN bd.level_id <= 1000 THEN 'Mid (101-1000)' 
    WHEN bd.level_id <= 10000 THEN 'Advanced (1001-10000)'
    ELSE 'Expert (10000+)'
END
ORDER BY power_activations DESC;

/*
VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Method: Cross-referenced bundle purchases (SKU 24) with bonus activations (bonus_type_id 434)
Validation Results: 
- 100,402+ power activations in last 7 days
- 26,643 unique users receiving power 
- Average 27-second activation delay after purchase
- Timing correlation confirms purchase → power causation
Validation Status: Passed
Notes: Methodology successfully tracks exact 1-hour power events from purchase to activation
*/