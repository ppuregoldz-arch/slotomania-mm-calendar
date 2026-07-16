# Lotto / LBP — Other

- **Variant ID:** `lotto-lbp--other`
- **Family:** `lotto-lbp`
- **Default Main KPI:** `unassigned`
- **Instances:** 11 rows across 11 dates (2026-05-06 to 2026-07-17)
- **Completed dates with daily outcomes:** 7

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 7 | $767,414 | $658,853 | $+108,561 | +16.5% | correlation | low |
| Paying users | 7 | 28,747 | 28,087 | +661 | +2.4% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 11/11 instance rows.
- Segments observed: finishers, unknown.
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

2026-05-06, 2026-05-14, 2026-05-23, 2026-06-13, 2026-06-21, 2026-06-29, 2026-07-04, 2026-07-10, 2026-07-11, 2026-07-14, 2026-07-17
