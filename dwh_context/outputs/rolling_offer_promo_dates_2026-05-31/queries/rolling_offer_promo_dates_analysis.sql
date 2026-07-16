/*
Rolling Offer Promo Dates Analysis - Since April 3rd, 2026

Business Question: Which promo dates has Rolling Offer gone live since April 3rd?

Data Sources:
- dwh.sm_fact_payments (transaction data)
- sm_draft.SM_DIM_Products (product mapping)

VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Date Range: 2026-04-03 to present (2026-05-31)
Data Sources: dwh.sm_fact_payments + sm_draft.SM_DIM_Products
Expected Result: List of promo dates with Rolling Offer activity since April 3rd
Actual Query Result: 25 promo dates identified (much higher frequency than Prize Mania's 7)
Validation Status: Passed
Notes: Rolling Offer shows daily/near-daily activity with variable PU volumes and ARPPUs
Manual validation: Revenue ranges $40K-$136K, PUs range 1K-10K, ARPPU $11-30
*/

select 
    distinct date(p.tran_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
    sum(p.net_amount) as total_net_revenue,
    count(distinct p.user_id) as PUs,  -- Paying Users (Purchasers)
    count(*) as total_transactions,
    round(sum(p.net_amount)::numeric / nullif(count(distinct p.user_id), 0), 2) as net_arppu,  -- Net ARPPU
    round(sum(p.net_amount)::numeric / nullif(count(*), 0), 2) as avg_net_transaction_value,
    round(count(*)::numeric / nullif(count(distinct p.user_id), 0), 2) as transactions_per_pu
    /*summary metrics per promo date - Rolling Offer analysis*/
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
    and pr.Product_Name = 'Rolling Offer'      /*Rolling Offer exact match*/
    and date(p.tran_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') >= '2026-04-03'
    /*analysis period start*/
group by 1
order by 1 desc;

/*
Rolling Offer Results Summary (as of 2026-05-31):
- 25 promo dates identified (vs Prize Mania's 7)
- Date range: 2026-04-03 to 2026-05-28
- Net Revenue range: ~$2 to $135,819 (excluding anomalies: $40K-$136K)
- PUs range: 1 to 10,435 users (much more variable than Prize Mania)
- Net ARPPU range: $11.32 to $29.72 (excluding anomalies)
- Transaction behavior: 2.0-5.5 transactions per PU (higher repeat rates)
- Strategy: High-frequency launches with segmented PU volumes and premium ARPPUs

Comparison to Prize Mania:
- Launch frequency: ~3.5x more frequent (25 vs 7 dates)
- Revenue strategy: More variable, higher ARPPUs
- PU strategy: Smaller segments but higher monetization
- Transaction behavior: More repeat purchases per PU
*/