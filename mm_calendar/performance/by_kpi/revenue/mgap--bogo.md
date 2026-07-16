# MGAP — Bogo

- **Variant ID:** `mgap--bogo`
- **Family:** `mgap`
- **Default Main KPI:** `revenue`
- **Instances:** 13 rows across 13 dates (2026-04-01 to 2026-07-26)
- **Completed dates with daily outcomes:** 10

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 10 | $677,377 | $645,635 | $+31,741 | +4.9% | correlation | low |
| Paying users | 10 | 27,818 | 27,460 | +358 | +1.3% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 13/13 instance rows.
- Segments observed: unknown.
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

2026-04-01, 2026-04-10, 2026-04-26, 2026-05-08, 2026-05-17, 2026-05-24, 2026-05-31, 2026-06-02, 2026-06-21, 2026-07-01, 2026-07-14, 2026-07-20, 2026-07-26
