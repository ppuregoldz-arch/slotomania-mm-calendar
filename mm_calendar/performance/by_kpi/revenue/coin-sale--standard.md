# Coin Sale — Standard

- **Variant ID:** `coin-sale--standard`
- **Family:** `coin-sale`
- **Default Main KPI:** `revenue`
- **Instances:** 11 rows across 9 dates (2026-04-04 to 2026-07-25)
- **Completed dates with daily outcomes:** 6

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 6 | $794,767 | $667,307 | $+127,460 | +19.1% | correlation | low |
| Paying users | 6 | 29,089 | 26,344 | +2,745 | +10.4% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 11/11 instance rows.
- Segments observed: mixed, unknown.
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

2026-04-04, 2026-05-05, 2026-05-22, 2026-06-05, 2026-06-20, 2026-07-03, 2026-07-18, 2026-07-24, 2026-07-25
