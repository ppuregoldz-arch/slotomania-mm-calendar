# MGAP — Bigger

- **Variant ID:** `mgap--bigger`
- **Family:** `mgap`
- **Default Main KPI:** `revenue`
- **Instances:** 9 rows across 8 dates (2026-05-05 to 2026-07-19)
- **Completed dates with daily outcomes:** 7

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 7 | $710,938 | $658,611 | $+52,327 | +7.9% | correlation | low |
| Paying users | 7 | 27,341 | 26,172 | +1,169 | +4.5% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `revenue`
- **Result:** Nominal product proxy only; see source
- **Sample:** n=3
- **Source:** `promo_revenue_analysis.md`
- **Interpretation:** Product revenue proxy ~$235.4K/day; conflicts with clean standalone family lift.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Selective DWH validation

- **Window:** 2026-04-01–2026-07-05; n=12 distinct Smart Calendar start dates.
- **Revenue:** $684,444 vs $659,252 same-weekday baseline (+3.82%).
- **Paying users:** 28,281 vs 27,790 same-weekday baseline (+1.77%).
- **Evidence:** whole-day correlation; low confidence; not attributed lift.
- **Source:** `measurement/SELECTIVE_DWH_VALIDATION_2026-07-10.md`.

## Context and confounders

- Concurrent promotion present on 9/9 instance rows.
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

2026-05-05, 2026-05-21, 2026-05-22, 2026-06-06, 2026-06-12, 2026-06-20, 2026-07-03, 2026-07-19
