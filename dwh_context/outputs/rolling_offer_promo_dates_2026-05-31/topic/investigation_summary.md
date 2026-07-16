# Rolling Offer Promo Dates Investigation - May 31, 2026

## Business Question
Which promo dates has Rolling Offer product gone live since April 3rd, 2026?

## Investigation Context
- **Analysis Period**: April 3, 2026 to present
- **Product Focus**: Rolling Offer (identified by Product_Name = 'Rolling Offer')
- **Data Source**: dwh.sm_fact_payments joined with sm_draft.SM_DIM_Products
- **Filters Applied**: Standard payment safety filters (successful transactions, non-test users, non-employees)

## Key Findings
Rolling Offer has gone live on **25 promo dates** since April 3rd, 2026 (much more frequent than Prize Mania's 7 dates).

**Rolling Offer shows significantly different patterns compared to Prize Mania:**
- **More frequent launches**: Nearly daily activity vs Prize Mania's ~10-11 day gaps
- **Different PU volumes**: 1-10,435 PUs per date vs Prize Mania's consistent 10K-16K
- **Wider ARPPU range**: $2.08-$29.72 vs Prize Mania's stable $8-9.50
- **Variable transaction patterns**: Some dates have high repeat purchase rates (up to 5.5 transactions/PU)

## Top Performing Rolling Offer Dates (from sample data)

### Highest Revenue Dates:
1. **2026-05-02** - $135,818.60 net revenue, 4,847 PUs, $28.02 ARPPU
2. **2026-05-28** - $134,504.26 net revenue, 4,525 PUs, $29.72 ARPPU 
3. **2026-04-30** - $130,409.54 net revenue, 10,435 PUs, $12.50 ARPPU
4. **2026-05-10** - $129,755.66 net revenue, 4,798 PUs, $27.04 ARPPU
5. **2026-05-23** - $126,685.25 net revenue, 4,557 PUs, $27.80 ARPPU

### Different Activity Patterns:
- **High Volume/Lower ARPPU**: May 12th (10,435 PUs, $12.50 ARPPU)
- **Low Volume/High ARPPU**: May 28th (4,525 PUs, $29.72 ARPPU)
- **Minimal Activity**: May 20th (1 PU, $2.08 ARPPU) - likely test

## Comparison with Prize Mania
- **Launch Frequency**: Rolling Offer ~25 dates vs Prize Mania 7 dates
- **Revenue Consistency**: Rolling Offer more variable ($40K-$135K) vs Prize Mania stable ($93K-$152K)
- **PU Strategy**: Rolling Offer targets smaller, higher-value segments vs Prize Mania's volume approach
- **ARPPU Range**: Rolling Offer $11-30 vs Prize Mania $8-9.50

## Methodology
- Used promo date conversion: `date(tran_ts at time zone 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours')`
- Applied standard Slotomania payment safety filters
- Identified Rolling Offer using exact match `Product_Name = 'Rolling Offer'`