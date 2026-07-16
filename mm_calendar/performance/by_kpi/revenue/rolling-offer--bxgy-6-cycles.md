# Rolling Offer — Bxgy 6 Cycles

- **Variant ID:** `rolling-offer--bxgy-6-cycles`
- **Family:** `rolling-offer`
- **Default Main KPI:** `revenue`
- **Instances:** 11 rows across 11 dates (2026-04-27 to 2026-07-23)
- **Completed dates with daily outcomes:** 9

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 9 | $638,475 | $646,945 | $-8,469 | -1.3% | correlation | low |
| Paying users | 9 | 27,721 | 27,387 | +334 | +1.2% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 11/11 instance rows.
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

2026-04-27, 2026-05-12, 2026-05-31, 2026-06-05, 2026-06-09, 2026-06-12, 2026-06-19, 2026-06-27, 2026-07-01, 2026-07-17, 2026-07-23
