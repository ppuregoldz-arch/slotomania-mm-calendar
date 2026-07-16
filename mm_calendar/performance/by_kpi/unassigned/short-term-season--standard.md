# Short-Term Season — Standard

- **Variant ID:** `short-term-season--standard`
- **Family:** `short-term-season`
- **Default Main KPI:** `unassigned`
- **Instances:** 44 rows across 37 dates (2026-04-01 to 2026-07-28)
- **Completed dates with daily outcomes:** 27

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 27 | $679,523 | $643,032 | $+36,491 | +5.7% | correlation | low |
| Paying users | 27 | 28,252 | 27,965 | +288 | +1.0% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 44/44 instance rows.
- Segments observed: dpu, finishers, unknown.
- Pricing observed: high, none.
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

2026-04-01, 2026-04-02, 2026-04-06, 2026-04-11, 2026-04-17, 2026-04-21, 2026-04-26, 2026-05-01, 2026-05-06, 2026-05-08, 2026-05-11, 2026-05-14, 2026-05-18, 2026-05-23, 2026-05-28, 2026-06-01, 2026-06-04, 2026-06-10, 2026-06-13, 2026-06-16, 2026-06-22, 2026-06-23, 2026-06-24, 2026-06-26, 2026-07-01, 2026-07-03, 2026-07-05, 2026-07-06, 2026-07-10, 2026-07-11, 2026-07-13, 2026-07-17, 2026-07-21, 2026-07-23, 2026-07-25, 2026-07-26, 2026-07-28
