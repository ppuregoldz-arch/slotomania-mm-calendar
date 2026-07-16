# Daily Deal — Cards

- **Variant ID:** `daily-deal--cards`
- **Family:** `daily-deal`
- **Default Main KPI:** `revenue`
- **Instances:** 48 rows across 39 dates (2026-04-01 to 2026-07-30)
- **Completed dates with daily outcomes:** 31

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 31 | $671,361 | $642,127 | $+29,234 | +4.6% | correlation | low |
| Paying users | 31 | 27,583 | 26,879 | +704 | +2.6% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 48/48 instance rows.
- Segments observed: unknown.
- Pricing observed: high, max, medium, none.
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

2026-04-01, 2026-04-03, 2026-04-05, 2026-04-07, 2026-04-09, 2026-04-11, 2026-04-12, 2026-04-16, 2026-04-17, 2026-04-19, 2026-04-21, 2026-04-22, 2026-04-26, 2026-04-27, 2026-04-30, 2026-05-05, 2026-05-07, 2026-05-31, 2026-06-07, 2026-06-12, 2026-06-13, 2026-06-18, 2026-06-19, 2026-06-20, 2026-06-21, 2026-06-24, 2026-06-27, 2026-06-30, 2026-07-02, 2026-07-03, 2026-07-04, 2026-07-07, 2026-07-08, 2026-07-13, 2026-07-19, 2026-07-23, 2026-07-25, 2026-07-28, 2026-07-30
