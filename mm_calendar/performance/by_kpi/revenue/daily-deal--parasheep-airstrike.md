# Daily Deal — Parasheep Airstrike

- **Variant ID:** `daily-deal--parasheep-airstrike`
- **Family:** `daily-deal`
- **Default Main KPI:** `revenue`
- **Instances:** 10 rows across 10 dates (2026-04-29 to 2026-07-22)
- **Completed dates with daily outcomes:** 7

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 7 | $611,885 | $644,803 | $-32,918 | -5.1% | correlation | low |
| Paying users | 7 | 28,979 | 30,362 | -1,382 | -4.6% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 10/10 instance rows.
- Segments observed: unknown.
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

2026-04-29, 2026-05-18, 2026-05-31, 2026-06-06, 2026-06-08, 2026-06-22, 2026-07-02, 2026-07-14, 2026-07-17, 2026-07-22
