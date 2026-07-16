# Daily Deal — Sb Wheel

- **Variant ID:** `daily-deal--sb-wheel`
- **Family:** `daily-deal`
- **Default Main KPI:** `revenue`
- **Instances:** 14 rows across 13 dates (2026-04-04 to 2026-07-12)
- **Completed dates with daily outcomes:** 11

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 11 | $714,379 | $645,627 | $+68,753 | +10.6% | correlation | low |
| Paying users | 11 | 28,983 | 27,172 | +1,811 | +6.7% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 14/14 instance rows.
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

2026-04-04, 2026-04-13, 2026-05-02, 2026-05-05, 2026-05-26, 2026-06-03, 2026-06-09, 2026-06-12, 2026-06-20, 2026-06-21, 2026-07-03, 2026-07-07, 2026-07-12
