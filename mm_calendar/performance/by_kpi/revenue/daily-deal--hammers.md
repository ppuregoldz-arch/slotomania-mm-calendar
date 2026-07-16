# Daily Deal — Hammers

- **Variant ID:** `daily-deal--hammers`
- **Family:** `daily-deal`
- **Default Main KPI:** `revenue`
- **Instances:** 48 rows across 46 dates (2026-04-02 to 2026-07-30)
- **Completed dates with daily outcomes:** 32

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 32 | $665,760 | $646,223 | $+19,538 | +3.0% | correlation | low |
| Paying users | 32 | 28,046 | 27,542 | +504 | +1.8% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `revenue`
- **Result:** Nominal product proxy only; see source
- **Sample:** n=21
- **Source:** `promo_revenue_analysis.md`
- **Interpretation:** Sticky Bundle proxy ~$132.5K/day on solo days; not total DD lift.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Selective DWH validation

- **Window:** 2026-04-01–2026-07-05; n=38 distinct Smart Calendar start dates.
- **Revenue:** $646,142 vs $644,379 same-weekday baseline (+0.27%).
- **Paying users:** 27,576 vs 27,601 same-weekday baseline (-0.09%).
- **Evidence:** whole-day correlation; low confidence; not attributed lift.
- **Source:** `measurement/SELECTIVE_DWH_VALIDATION_2026-07-10.md`.

## Context and confounders

- Concurrent promotion present on 48/48 instance rows.
- Segments observed: dpu, finishers, unknown.
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

2026-04-02, 2026-04-04, 2026-04-06, 2026-04-10, 2026-04-15, 2026-04-16, 2026-04-19, 2026-04-25, 2026-04-28, 2026-05-01, 2026-05-03, 2026-05-04, 2026-05-06, 2026-05-08, 2026-05-12, 2026-05-13, 2026-05-16, 2026-05-17, 2026-05-22, 2026-05-25, 2026-05-27, 2026-05-29, 2026-06-01, 2026-06-02, 2026-06-11, 2026-06-12, 2026-06-19, 2026-06-23, 2026-06-25, 2026-06-26, 2026-07-04, 2026-07-05, 2026-07-06, 2026-07-09, 2026-07-11, 2026-07-13, 2026-07-14, 2026-07-16, 2026-07-21, 2026-07-23, 2026-07-24, 2026-07-26, 2026-07-27, 2026-07-28, 2026-07-29, 2026-07-30
