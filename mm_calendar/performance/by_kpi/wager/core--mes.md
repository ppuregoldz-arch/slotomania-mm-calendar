# Core — Mes

- **Variant ID:** `core--mes`
- **Family:** `core`
- **Default Main KPI:** `wager`
- **Instances:** 28 rows across 22 dates (2026-04-15 to 2026-07-24)
- **Completed dates with daily outcomes:** 15

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 15 | $631,411 | $628,174 | $+3,236 | +0.5% | correlation | low |
| Paying users | 15 | 28,060 | 28,027 | +33 | +0.1% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `wager`
- **Result:** -8.8% vs documented baseline
- **Sample:** n=3
- **Source:** `core_wager_analysis.md`
- **Interpretation:** June all-user median wager uplift; heavily timing-confounded.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Context and confounders

- Concurrent promotion present on 28/28 instance rows.
- Segments observed: black-diamond, finishers, unknown.
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

2026-04-15, 2026-04-20, 2026-04-28, 2026-05-05, 2026-05-07, 2026-05-17, 2026-05-22, 2026-05-31, 2026-06-08, 2026-06-12, 2026-06-18, 2026-06-21, 2026-06-29, 2026-06-30, 2026-07-02, 2026-07-07, 2026-07-09, 2026-07-11, 2026-07-13, 2026-07-18, 2026-07-21, 2026-07-24
