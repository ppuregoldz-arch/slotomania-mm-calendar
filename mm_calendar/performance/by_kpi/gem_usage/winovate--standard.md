# Winovate — Standard

- **Variant ID:** `winovate--standard`
- **Family:** `winovate`
- **Default Main KPI:** `gem_usage`
- **Instances:** 15 rows across 15 dates (2026-04-06 to 2026-07-28)
- **Completed dates with daily outcomes:** 12

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 12 | $651,195 | $625,963 | $+25,232 | +4.0% | correlation | low |
| Paying users | 12 | 27,864 | 26,804 | +1,060 | +4.0% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 15/15 instance rows.
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

2026-04-06, 2026-04-14, 2026-04-30, 2026-05-08, 2026-05-12, 2026-05-16, 2026-05-24, 2026-06-09, 2026-06-16, 2026-06-21, 2026-06-25, 2026-07-03, 2026-07-08, 2026-07-11, 2026-07-28
