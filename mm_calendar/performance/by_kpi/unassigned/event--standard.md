# Event — Standard

- **Variant ID:** `event--standard`
- **Family:** `event`
- **Default Main KPI:** `unassigned`
- **Instances:** 81 rows across 52 dates (2026-04-01 to 2026-07-30)
- **Completed dates with daily outcomes:** 41

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 41 | $680,844 | $648,093 | $+32,752 | +5.1% | correlation | low |
| Paying users | 41 | 28,054 | 27,109 | +945 | +3.5% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 81/81 instance rows.
- Segments observed: black-diamond, dpu, finishers, ic, mixed, npu, unknown.
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

2026-04-01, 2026-04-02, 2026-04-03, 2026-04-04, 2026-04-05, 2026-04-10, 2026-04-11, 2026-04-17, 2026-04-22, 2026-04-24, 2026-04-28, 2026-05-02, 2026-05-04, 2026-05-05, 2026-05-06, 2026-05-07, 2026-05-08, 2026-05-09, 2026-05-10, 2026-05-11, 2026-05-12, 2026-05-13, 2026-05-22, 2026-06-01, 2026-06-03, 2026-06-04, 2026-06-10, 2026-06-11, 2026-06-12, 2026-06-16, 2026-06-17, 2026-06-19, 2026-06-25, 2026-06-26, 2026-06-27, 2026-06-28, 2026-07-01, 2026-07-02, 2026-07-03, 2026-07-04, 2026-07-05, 2026-07-07, 2026-07-08, 2026-07-09, 2026-07-11, 2026-07-14, 2026-07-16, 2026-07-18, 2026-07-21, 2026-07-24, 2026-07-26, 2026-07-30
