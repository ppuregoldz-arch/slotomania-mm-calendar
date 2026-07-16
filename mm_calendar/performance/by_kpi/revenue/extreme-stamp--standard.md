# Extreme Stamp — Standard

- **Variant ID:** `extreme-stamp--standard`
- **Family:** `extreme-stamp`
- **Default Main KPI:** `revenue`
- **Instances:** 31 rows across 14 dates (2026-04-08 to 2026-07-28)
- **Completed dates with daily outcomes:** 12

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 12 | $724,045 | $633,858 | $+90,187 | +14.2% | correlation | low |
| Paying users | 12 | 27,074 | 26,081 | +993 | +3.8% | correlation | low |

## KPI-specific historical evidence

No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.

## Selective DWH validation

- **Window:** 2026-04-01–2026-07-05; n=23 distinct Smart Calendar start dates.
- **Revenue:** $673,185 vs $625,061 same-weekday baseline (+7.70%).
- **Paying users:** 26,574 vs 26,242 same-weekday baseline (+1.26%).
- **Evidence:** whole-day correlation; low confidence; not attributed lift.
- **Source:** `measurement/SELECTIVE_DWH_VALIDATION_2026-07-10.md`.

## Context and confounders

- Concurrent promotion present on 31/31 instance rows.
- Segments observed: unknown.
- Pricing observed: high, medium, none.
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

2026-04-08, 2026-04-14, 2026-04-28, 2026-05-05, 2026-05-13, 2026-05-28, 2026-06-03, 2026-06-13, 2026-06-19, 2026-06-20, 2026-06-23, 2026-07-04, 2026-07-07, 2026-07-28
