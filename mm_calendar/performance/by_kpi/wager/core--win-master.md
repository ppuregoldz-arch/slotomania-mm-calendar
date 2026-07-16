# Core — Win Master

- **Variant ID:** `core--win-master`
- **Family:** `core`
- **Default Main KPI:** `wager`
- **Instances:** 14 rows across 13 dates (2026-04-04 to 2026-07-30)
- **Completed dates with daily outcomes:** 10

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 10 | $685,983 | $645,235 | $+40,748 | +6.3% | correlation | low |
| Paying users | 10 | 28,729 | 27,835 | +894 | +3.2% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `wager`
- **Result:** -6.7% vs documented baseline
- **Sample:** n=4
- **Source:** `core_wager_analysis.md`
- **Interpretation:** June all-user median wager uplift; day-level correlation.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Context and confounders

- Concurrent promotion present on 14/14 instance rows.
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

2026-04-04, 2026-04-09, 2026-05-03, 2026-05-29, 2026-06-04, 2026-06-08, 2026-06-17, 2026-06-21, 2026-07-01, 2026-07-05, 2026-07-20, 2026-07-22, 2026-07-30
