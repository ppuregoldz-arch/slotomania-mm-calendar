# Payment Offer — Standard

- **Variant ID:** `payment-offer--standard`
- **Family:** `payment-offer`
- **Default Main KPI:** `revenue`
- **Instances:** 11 rows across 7 dates (2026-04-01 to 2026-07-23)
- **Completed dates with daily outcomes:** 6

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 6 | $745,567 | $672,413 | $+73,154 | +10.9% | correlation | low |
| Paying users | 6 | 28,684 | 27,061 | +1,623 | +6.0% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 11/11 instance rows.
- Segments observed: dpu, mixed, unknown.
- Pricing observed: low, none.
- Holiday set used for the local DOW comparison: 2026-04-04, 2026-05-05, 2026-05-25, 2026-07-04.
- The holiday-list conflict remains registered; changing it may change the comparison.

## Reuse recommendation

**Insufficient evidence for a confirmed recommendation.** Use only with the family rules and current monthly constraints; consult the prediction framework for eligibility.

## Provenance

- `mm_calendar/data/monday_pull_last_3mo.json`
- `mm_calendar/data/real_months.json`
- `mm_calendar/data/wide_revenue_pu.json`
- Calculation date: 2026-07-10
- Baseline method: mean daily outcome for the same weekday in Apr 1–Jul 5, excluding the four dates listed above.

## Instance dates

2026-04-01, 2026-05-09, 2026-06-12, 2026-06-19, 2026-06-21, 2026-07-04, 2026-07-23
