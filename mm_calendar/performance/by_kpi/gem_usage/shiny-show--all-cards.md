# Shiny Show — All Cards

- **Variant ID:** `shiny-show--all-cards`
- **Family:** `shiny-show`
- **Default Main KPI:** `gem_usage`
- **Instances:** 7 rows across 7 dates (2026-04-01 to 2026-07-07)
- **Completed dates with daily outcomes:** 6

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 6 | $686,725 | $643,948 | $+42,777 | +6.6% | correlation | low |
| Paying users | 6 | 27,862 | 28,180 | -317 | -1.1% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `gem_usage`
- **Result:** +54.0% vs documented baseline
- **Sample:** n=5
- **Source:** `shiny_show_performance.md`
- **Interpretation:** Shiny mini-game usage versus Play-X baseline.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Context and confounders

- Concurrent promotion present on 7/7 instance rows.
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

2026-04-01, 2026-04-15, 2026-04-23, 2026-05-29, 2026-06-01, 2026-06-07, 2026-07-07
