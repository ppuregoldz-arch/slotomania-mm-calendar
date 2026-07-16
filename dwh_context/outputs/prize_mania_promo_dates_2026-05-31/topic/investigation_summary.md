# Prize Mania Promo Dates Investigation - May 31, 2026

## Business Question
Which promo dates has Prize Mania product gone live since April 3rd, 2026?

## Investigation Context
- **Analysis Period**: April 3, 2026 to present
- **Product Focus**: Prize Mania products (identified by Product_Name ilike '%mania%')
- **Data Source**: dwh.sm_fact_payments joined with sm_draft.SM_DIM_Products
- **Filters Applied**: Standard payment safety filters (successful transactions, non-test users, non-employees)

## Key Findings
Prize Mania went live on **7 promo dates** since April 3rd, 2026:

1. **2026-05-30** (Most Recent) - $118,772.47 revenue, 10,676 purchasers
2. **2026-05-22** - $130,756.79 revenue, 11,495 purchasers  
3. **2026-05-21** - $3.41 revenue, 1 purchaser (likely test/minimal activity)
4. **2026-05-03** - $112,109.07 revenue, 11,657 purchasers
5. **2026-04-22** - $132,123.57 revenue, 12,506 purchasers
6. **2026-04-13** - $138,061.82 revenue, 13,306 purchasers
7. **2026-04-09** - $180,176.27 revenue, 16,616 purchasers (highest performing)

## Performance Insights
- **Highest Revenue Date**: April 9th ($180,176.27)
- **Most Recent Activity**: May 30th ($118,772.47) 
- **Anomaly**: May 21st shows minimal activity ($3.41) suggesting possible test or limited rollout
- **Average Performance**: Most dates generate $110K-$180K in revenue with 10K-16K purchasers

## Methodology
- Used promo date conversion: `date(tran_ts at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours')`
- Applied standard Slotomania payment safety filters
- Identified Prize Mania products using `Product_Name ilike '%mania%'` pattern