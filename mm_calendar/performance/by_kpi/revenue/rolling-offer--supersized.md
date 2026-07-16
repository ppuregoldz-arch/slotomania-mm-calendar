# Rolling Offer — Supersized

- **Variant ID:** `rolling-offer--supersized`
- **Family:** `rolling-offer`
- **Default Main KPI:** `revenue`
- **Instances:** 9 rows across 9 dates (2026-04-04 to 2026-06-30)
- **Completed dates with daily outcomes:** 9

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 9 | $648,419 | $648,202 | $+217 | +0.0% | correlation | low |
| Paying users | 9 | 25,939 | 26,294 | -356 | -1.4% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `revenue`
- **Result:** Nominal product proxy only; see source
- **Sample:** n=2
- **Source:** `promo_revenue_analysis.md`
- **Interpretation:** Product revenue proxy ~$73.7K/day on solo days; not lift.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Context and confounders

- Concurrent promotion present on 9/9 instance rows.
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

2026-04-04, 2026-04-17, 2026-04-21, 2026-04-30, 2026-05-15, 2026-05-24, 2026-06-06, 2026-06-12, 2026-06-30
