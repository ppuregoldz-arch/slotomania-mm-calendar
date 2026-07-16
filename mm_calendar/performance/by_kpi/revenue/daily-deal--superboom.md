# Daily Deal — Superboom

- **Variant ID:** `daily-deal--superboom`
- **Family:** `daily-deal`
- **Default Main KPI:** `revenue`
- **Instances:** 6 rows across 6 dates (2026-04-04 to 2026-07-20)
- **Completed dates with daily outcomes:** 4

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 4 | $724,238 | $656,071 | $+68,168 | +10.4% | correlation | low |
| Paying users | 4 | 30,938 | 29,771 | +1,167 | +3.9% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 6/6 instance rows.
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

2026-04-04, 2026-04-05, 2026-05-24, 2026-06-29, 2026-07-18, 2026-07-20
