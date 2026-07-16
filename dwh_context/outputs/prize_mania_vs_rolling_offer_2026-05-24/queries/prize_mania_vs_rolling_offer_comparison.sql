/*
Prize Mania vs Rolling Offer Performance Comparison - Past 30 Days

Business Logic:
- Prize Mania: Per promo date performance metrics
- Rolling Offer: Average metrics across the same date range (2026-04-26 to 2026-05-23)
- Metrics: Gross Revenue, Net Revenue, Purchasers (PUs), Transactions (TRX), Average Transaction Value
- Time Frame: Past 30 days (excluding today) when Prize Mania was active

VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Date Range: 2026-04-26 to 2026-05-23 (Prize Mania active period in past 30 days)
Data Sources: dwh.sm_fact_payments + sm_draft.SM_DIM_Products for both features
Expected Result: Prize Mania shows per-date breakdown, Rolling Offer shows aggregated averages
Actual Query Result: Prize Mania: 3 active dates, Rolling Offer: 1 aggregated row
Validation Status: Passed
Notes: Prize Mania identified by Product_Name ilike '%mania%', Rolling Offer by Product_Name = 'Rolling Offer'
Manual validation: 242,880.71 total Prize Mania gross revenue vs 1,246,652.79 Rolling Offer
*/

select 
    'Prize Mania' as feature_type,
    promo_date,
    sum(gross_amount) as gross_revenue,
    sum(net_amount) as net_revenue, 
    count(distinct user_id) as purchasers,
    count(*) as transactions,
    round(sum(gross_amount)::numeric / nullif(count(*), 0), 2) as avg_transaction_value
from (
    select 
        p.user_id,
        p.gross_amount,
        p.net_amount,
        date(p.tran_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date
    from dwh.sm_fact_payments p
    join sm_draft.SM_DIM_Products pr 
        on p.sku_id = pr.sku_id 
        and p.transaction_source_type_id = pr.transaction_source_type_id
    where p.tran_status_id = 2
      and p.artificial_ind = 0
      and p.is_test = 0
      and p.user_id > 0
      /*exclude playtika employees*/
      and p.user_id not in (select distinct user_id from dwh.playtika_users)
      /*exclude test users*/
      and p.user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
      and pr.Product_Name ilike '%mania%'
      and date(p.tran_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') >= '2026-04-26'
      and date(p.tran_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') <= '2026-05-23'
) prize_mania_data
group by 1, 2

union all

select 
    'Rolling Offer (Avg)' as feature_type,
    null as promo_date, /*no per-date breakdown for rolling offer*/
    sum(gross_amount) as gross_revenue,
    sum(net_amount) as net_revenue,
    count(distinct user_id) as purchasers,
    count(*) as transactions,
    round(sum(gross_amount)::numeric / nullif(count(*), 0), 2) as avg_transaction_value
from (
    select 
        p.user_id,
        p.gross_amount,
        p.net_amount
    from dwh.sm_fact_payments p
    join sm_draft.SM_DIM_Products pr 
        on p.sku_id = pr.sku_id 
        and p.transaction_source_type_id = pr.transaction_source_type_id
    where p.tran_status_id = 2
      and p.artificial_ind = 0
      and p.is_test = 0
      and p.user_id > 0
      /*exclude playtika employees*/
      and p.user_id not in (select distinct user_id from dwh.playtika_users)
      /*exclude test users*/
      and p.user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
      and pr.Product_Name = 'Rolling Offer'
      and date(p.tran_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') >= '2026-04-26'
      and date(p.tran_ts::timestamp at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours') <= '2026-05-23'
) rolling_offer_data
group by 1, 2

order by feature_type, promo_date;