# Daily Deal — Clan Pack

- **Variant ID:** `daily-deal--clan-pack`
- **Family:** `daily-deal`
- **Default Main KPI:** `revenue`
- **Instances:** 3 rows across 3 dates (2026-05-20 to 2026-06-07)
- **Completed dates with daily outcomes:** 3

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 3 | $609,110 | $632,076 | $-22,967 | -3.6% | correlation | low |
| Paying users | 3 | 25,344 | 26,906 | -1,562 | -5.8% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 3/3 instance rows.
- Segments observed: unknown.
- Pricing observed: high, medium.
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

2026-05-20, 2026-05-28, 2026-06-07
