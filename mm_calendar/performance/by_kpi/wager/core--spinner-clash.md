# Core — Spinner Clash

- **Variant ID:** `core--spinner-clash`
- **Family:** `core`
- **Default Main KPI:** `wager`
- **Instances:** 8 rows across 8 dates (2026-04-16 to 2026-07-29)
- **Completed dates with daily outcomes:** 5

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 5 | $598,235 | $638,779 | $-40,543 | -6.3% | correlation | low |
| Paying users | 5 | 26,607 | 26,567 | +40 | +0.2% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Context and confounders

- Concurrent promotion present on 8/8 instance rows.
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

2026-04-16, 2026-05-09, 2026-05-27, 2026-06-11, 2026-06-28, 2026-07-06, 2026-07-13, 2026-07-29
