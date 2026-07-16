# Happy Hour / Jumbo — Standard

- **Variant ID:** `happy-hour--standard`
- **Family:** `happy-hour`
- **Default Main KPI:** `revenue`
- **Instances:** 17 rows across 14 dates (2026-04-04 to 2026-07-25)
- **Completed dates with daily outcomes:** 12

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 12 | $731,227 | $667,735 | $+63,492 | +9.5% | correlation | low |
| Paying users | 12 | 27,769 | 26,931 | +838 | +3.1% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 17/17 instance rows.
- Segments observed: unknown.
- Pricing observed: none.
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

2026-04-04, 2026-05-05, 2026-05-22, 2026-05-23, 2026-05-27, 2026-05-31, 2026-06-05, 2026-06-06, 2026-06-19, 2026-06-20, 2026-06-21, 2026-07-04, 2026-07-19, 2026-07-25
