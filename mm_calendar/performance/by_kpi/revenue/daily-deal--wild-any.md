# Daily Deal — Wild Any

- **Variant ID:** `daily-deal--wild-any`
- **Family:** `daily-deal`
- **Default Main KPI:** `revenue`
- **Instances:** 12 rows across 11 dates (2026-05-03 to 2026-07-12)
- **Completed dates with daily outcomes:** 8

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 8 | $777,923 | $647,638 | $+130,285 | +20.1% | correlation | low |
| Paying users | 8 | 30,835 | 27,810 | +3,025 | +10.9% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 12/12 instance rows.
- Segments observed: dpu, finishers, unknown.
- Pricing observed: high, max, none.
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

2026-05-03, 2026-05-05, 2026-05-07, 2026-05-10, 2026-05-11, 2026-06-20, 2026-07-03, 2026-07-04, 2026-07-10, 2026-07-11, 2026-07-12
