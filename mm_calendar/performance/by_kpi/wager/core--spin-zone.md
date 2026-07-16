# Core — Spin Zone

- **Variant ID:** `core--spin-zone`
- **Family:** `core`
- **Default Main KPI:** `wager`
- **Instances:** 34 rows across 30 dates (2026-04-03 to 2026-07-31)
- **Completed dates with daily outcomes:** 26

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 26 | $646,021 | $644,739 | $+1,282 | +0.2% | correlation | low |
| Paying users | 26 | 28,444 | 28,827 | -383 | -1.3% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `wager`
- **Result:** +4.1% vs documented baseline
- **Sample:** n=5
- **Source:** `core_wager_analysis.md`
- **Interpretation:** June all-user median wager uplift; day-level correlation.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Context and confounders

- Concurrent promotion present on 34/34 instance rows.
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

2026-04-03, 2026-04-08, 2026-04-11, 2026-04-12, 2026-04-17, 2026-04-20, 2026-04-23, 2026-04-24, 2026-04-27, 2026-05-01, 2026-05-03, 2026-05-04, 2026-05-11, 2026-05-14, 2026-05-15, 2026-05-18, 2026-05-21, 2026-05-28, 2026-06-03, 2026-06-06, 2026-06-14, 2026-06-15, 2026-06-16, 2026-06-21, 2026-06-22, 2026-07-02, 2026-07-06, 2026-07-08, 2026-07-17, 2026-07-31
