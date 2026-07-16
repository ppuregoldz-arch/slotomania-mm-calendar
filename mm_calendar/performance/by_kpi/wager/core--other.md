# Core — Other

- **Variant ID:** `core--other`
- **Family:** `core`
- **Default Main KPI:** `wager`
- **Instances:** 42 rows across 34 dates (2026-04-01 to 2026-07-29)
- **Completed dates with daily outcomes:** 26

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 26 | $628,993 | $625,309 | $+3,684 | +0.6% | correlation | low |
| Paying users | 26 | 27,177 | 26,908 | +268 | +1.0% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 42/42 instance rows.
- Segments observed: finishers, ic, unknown.
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

2026-04-01, 2026-04-05, 2026-04-06, 2026-04-07, 2026-04-09, 2026-04-10, 2026-04-11, 2026-04-15, 2026-04-19, 2026-04-21, 2026-04-23, 2026-04-26, 2026-04-28, 2026-04-29, 2026-04-30, 2026-05-07, 2026-05-14, 2026-05-16, 2026-05-20, 2026-05-26, 2026-05-27, 2026-05-28, 2026-06-01, 2026-06-02, 2026-06-07, 2026-06-23, 2026-07-07, 2026-07-09, 2026-07-11, 2026-07-14, 2026-07-15, 2026-07-23, 2026-07-28, 2026-07-29
