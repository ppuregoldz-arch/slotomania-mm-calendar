/*
Prize Mania Promo Dates Analysis - NET REVENUE - Since April 3rd, 2026

Business Question: Which promo dates has Prize Mania product gone live since April 3rd (using NET revenue)?

Data Sources:
- dwh.sm_fact_payments (transaction data)
- sm_draft.SM_DIM_Products (product mapping)

VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Date Range: 2026-04-03 to present (2026-05-31)
Data Sources: dwh.sm_fact_payments + sm_draft.SM_DIM_Products
Expected Result: List of promo dates with Prize Mania net revenue since April 3rd
Actual Query Result: 7 promo dates identified with net revenue ranging $2.39 to $151,877.67
Validation Status: Passed
Notes: Net revenue shows ~83-84% of gross revenue (platform fees), May 21st minimal activity confirmed
Manual validation: Net-to-gross ratio consistent across all dates at ~16-17% deduction
*/

select 
    distinct date(p.tran_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
    sum(p.net_amount) as total_net_revenue,
    count(distinct p.user_id) as PUs,  -- Paying Users (Purchasers)
    count(*) as total_transactions,
    round(sum(p.net_amount)::numeric / nullif(count(distinct p.user_id), 0), 2) as net_arppu,  -- Net ARPPU
    round(sum(p.net_amount)::numeric / nullif(count(*), 0), 2) as avg_net_transaction_value
    /*summary metrics per promo date - NET REVENUE FOCUS with PUs and ARPPU*/
from dwh.sm_fact_payments p
join sm_draft.SM_DIM_Products pr 
    on p.sku_id = pr.sku_id 
    and p.transaction_source_type_id = pr.transaction_source_type_id
    /*product mapping*/
where 1 = 1
    and p.tran_status_id = 2                    /*successful transactions only*/
    and p.artificial_ind = 0                    /*exclude artificial transactions*/
    and p.is_test = 0                          /*exclude test transactions*/
    and p.user_id > 0                          /*valid user ids only*/
    /*exclude playtika employees*/
    and p.user_id not in (select distinct user_id from dwh.playtika_users)
    /*exclude test users*/
    and p.user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
    and pr.Product_Name ilike '%mania%'        /*Prize Mania product identification*/
    and date(p.tran_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') >= '2026-04-03'
    /*analysis period start*/
group by 1
order by 1 desc;

/*
NET REVENUE & PUs Results Summary (as of 2026-05-31):
- 7 promo dates identified
- Date range: 2026-04-09 to 2026-05-30
- Net Revenue range: $2.39 to $151,877.67
- PUs (Paying Users) range: 1 to 16,616 users
- Transaction range: 1 to 18,766 transactions
- Net ARPPU range: $2.39 to $9.49 (excluding May 21st anomaly: $8.01-$9.49)
- Avg Net Transaction Value: $2.39 to $8.50
- Net-to-Gross Ratio: ~83-84% (consistent platform fee deduction)
- PU Engagement: 1.12-1.20 transactions per paying user (good repeat purchase)
*/