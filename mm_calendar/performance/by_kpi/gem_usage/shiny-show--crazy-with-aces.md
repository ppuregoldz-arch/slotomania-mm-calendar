# Shiny Show — Crazy With Aces

- **Variant ID:** `shiny-show--crazy-with-aces`
- **Family:** `shiny-show`
- **Default Main KPI:** `gem_usage`
- **Instances:** 5 rows across 5 dates (2026-04-06 to 2026-06-24)
- **Completed dates with daily outcomes:** 5

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 5 | $626,539 | $653,025 | $-26,486 | -4.1% | correlation | low |
| Paying users | 5 | 28,561 | 28,095 | +465 | +1.7% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `gem_usage`
- **Result:** -2.0% vs documented baseline
- **Sample:** n=5
- **Source:** `shiny_show_performance.md`
- **Interpretation:** Shiny mini-game usage versus Play-X baseline.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Context and confounders

- Concurrent promotion present on 5/5 instance rows.
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

2026-04-06, 2026-04-11, 2026-05-07, 2026-06-05, 2026-06-24
