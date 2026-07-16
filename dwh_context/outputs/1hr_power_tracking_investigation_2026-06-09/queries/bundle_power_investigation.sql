/*
1-Hour Power Booster Tracking Investigation
==========================================
Date: 2026-06-09
Purpose: Track the actual events of receiving 1-hour power boosters from purchases
Context: User provided screenshots showing "1HR Power" benefit in purchase bundles
*/

-- Query 1: Explore bundle details structure for Slotobucks purchases
-- This table should contain information about purchase bundle components including 1HR Power
SELECT 
    user_id,
    transaction_id,
    bundle_component_id,
    bundle_component_name,
    component_type,
    component_value,
    component_quantity,
    transaction_date,
    insert_ts
FROM dwh.sm_fact_payments_bundle_details_slotobucks
WHERE transaction_date >= current_date - 7  -- Last week
    AND (bundle_component_name ILIKE '%power%' 
         OR bundle_component_name ILIKE '%hour%'
         OR component_type ILIKE '%power%')
ORDER BY transaction_date DESC, insert_ts DESC
LIMIT 100;

-- Query 2: Explore bundle details structure for real money purchases  
-- Similar structure but for regular purchases
SELECT 
    user_id,
    transaction_id,
    bundle_component_id,
    bundle_component_name,
    component_type,
    component_value,
    component_quantity,
    transaction_date,
    insert_ts
FROM dwh.sm_fact_payments_bundle_details
WHERE transaction_date >= current_date - 7  -- Last week
    AND (bundle_component_name ILIKE '%power%' 
         OR bundle_component_name ILIKE '%hour%'
         OR component_type ILIKE '%power%')
ORDER BY transaction_date DESC, insert_ts DESC
LIMIT 100;

-- Query 3: Get complete structure of bundle tables to understand fields
-- Slotobucks bundle structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'dwh' 
    AND table_name = 'sm_fact_payments_bundle_details_slotobucks'
ORDER BY ordinal_position;

-- Query 4: Real money bundle structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'dwh' 
    AND table_name = 'sm_fact_payments_bundle_details'
ORDER BY ordinal_position;

-- Query 5: Sample recent bundle transactions to understand data patterns
-- Recent Slotobucks bundles (any components)
SELECT *
FROM dwh.sm_fact_payments_bundle_details_slotobucks
WHERE transaction_date >= current_date - 3
ORDER BY transaction_date DESC, insert_ts DESC
LIMIT 20;

-- Query 6: Sample recent real money bundles 
SELECT *
FROM dwh.sm_fact_payments_bundle_details
WHERE transaction_date >= current_date - 3
ORDER BY transaction_date DESC, insert_ts DESC
LIMIT 20;

-- Query 7: Cross-reference with main payments table
-- Find purchases that include power benefits
SELECT 
    p.user_id,
    p.transaction_ticket,
    p.tran_date,
    p.tran_ts,
    p.net_amount,
    prod.Product_Name,
    bd.bundle_component_name,
    bd.component_type,
    bd.component_value,
    bd.component_quantity
FROM dwh.sm_fact_payments p
LEFT JOIN sm_draft.SM_DIM_Products prod 
    ON p.sku_id = prod.sku_id 
    AND p.transaction_source_type_id = prod.transaction_source_type_id
INNER JOIN dwh.sm_fact_payments_bundle_details bd
    ON p.transaction_ticket = bd.transaction_id
WHERE p.tran_status_id = 2
    AND p.tran_date >= current_date - 7
    AND (bd.bundle_component_name ILIKE '%power%' 
         OR bd.bundle_component_name ILIKE '%hour%')
ORDER BY p.tran_ts DESC;

-- Query 8: Correlate bundle power with bonus_history events
-- This should show the actual granting of 1-hour power
WITH power_purchases AS (
    SELECT 
        p.user_id,
        p.transaction_ticket,
        p.tran_ts,
        bd.bundle_component_name,
        bd.component_value
    FROM dwh.sm_fact_payments p
    INNER JOIN dwh.sm_fact_payments_bundle_details bd
        ON p.transaction_ticket = bd.transaction_id
    WHERE p.tran_status_id = 2
        AND p.tran_date >= current_date - 7
        AND bd.bundle_component_name ILIKE '%power%'
)
SELECT 
    pp.user_id,
    pp.transaction_ticket,
    pp.tran_ts,
    pp.bundle_component_name,
    bh.bonus_ts,
    bt.bonus_type_name,
    bh.bonus_amount,
    bh.source,
    -- Time difference between purchase and bonus grant
    DATEDIFF('second', pp.tran_ts, bh.bonus_ts) as seconds_after_purchase
FROM power_purchases pp
LEFT JOIN dwh.fact_sm_bonus_history bh 
    ON pp.user_id = bh.user_id
    AND bh.bonus_ts BETWEEN pp.tran_ts - INTERVAL '1 minute' AND pp.tran_ts + INTERVAL '5 minutes'
LEFT JOIN dwh.dim_sm_bonus_type bt 
    ON bh.bonus_type_id = bt.bonus_type_id
WHERE bt.bonus_type_name ILIKE '%power%' 
    OR bt.bonus_type_name ILIKE '%hour%'
    OR bt.bonus_type_name ILIKE '%turbo%'
ORDER BY pp.tran_ts DESC;

/*
VALIDATION DOCUMENTATION
========================
Validation Performed: No (pending user transaction details and MCP server availability)
Reason for No Validation: MCP Vertica server currently unavailable; awaiting user transaction details for targeted validation
Query Status: NOT FULLY VALIDATED
Risk Assessment: Medium risk - queries designed based on table structure assumptions; will validate once server available and user provides transaction details
*/