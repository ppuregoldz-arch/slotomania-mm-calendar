# Golden Spin — Standard

- **Variant ID:** `golden-spin--standard`
- **Family:** `golden-spin`
- **Default Main KPI:** `revenue`
- **Instances:** 6 rows across 6 dates (2026-05-19 to 2026-07-30)
- **Completed dates with daily outcomes:** 4

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 4 | $569,042 | $620,536 | $-51,494 | -8.3% | correlation | low |
| Paying users | 4 | 23,311 | 25,530 | -2,220 | -8.7% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Selective DWH validation

- **Window:** 2026-04-01–2026-07-05; n=11 distinct Smart Calendar start dates.
- **Revenue:** $588,900 vs $621,998 same-weekday baseline (-5.32%).
- **Paying users:** 25,400 vs 25,932 same-weekday baseline (-2.05%).
- **Evidence:** whole-day correlation; low confidence; not attributed lift.
- **Source:** `measurement/SELECTIVE_DWH_VALIDATION_2026-07-10.md`.

## Context and confounders

- Concurrent promotion present on 6/6 instance rows.
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

2026-05-19, 2026-05-30, 2026-06-25, 2026-07-02, 2026-07-16, 2026-07-30
