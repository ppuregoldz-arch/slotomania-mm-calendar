# Core — Pyp

- **Variant ID:** `core--pyp`
- **Family:** `core`
- **Default Main KPI:** `wager`
- **Instances:** 12 rows across 12 dates (2026-04-14 to 2026-07-10)
- **Completed dates with daily outcomes:** 11

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 11 | $638,938 | $655,150 | $-16,212 | -2.5% | correlation | low |
| Paying users | 11 | 27,472 | 27,443 | +30 | +0.1% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `wager`
- **Result:** +3.0% vs documented baseline
- **Sample:** n=5
- **Source:** `core_wager_analysis.md`
- **Interpretation:** June all-user median wager uplift; day-level correlation.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Context and confounders

- Concurrent promotion present on 12/12 instance rows.
- Segments observed: finishers, unknown.
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

2026-04-14, 2026-04-22, 2026-04-25, 2026-04-30, 2026-05-02, 2026-05-10, 2026-05-30, 2026-06-05, 2026-06-10, 2026-06-15, 2026-06-20, 2026-07-10
