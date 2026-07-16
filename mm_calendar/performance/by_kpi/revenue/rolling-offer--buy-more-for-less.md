# Rolling Offer — Buy More For Less

- **Variant ID:** `rolling-offer--buy-more-for-less`
- **Family:** `rolling-offer`
- **Default Main KPI:** `revenue`
- **Instances:** 12 rows across 12 dates (2026-04-02 to 2026-07-28)
- **Completed dates with daily outcomes:** 10

## Measured daily context

The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.

| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue | 10 | $652,564 | $636,663 | $+15,901 | +2.5% | correlation | low |
| Paying users | 10 | 27,346 | 27,494 | -149 | -0.5% | correlation | low |

## KPI-specific historical evidence

- **KPI:** `revenue`
- **Result:** Nominal product proxy only; see source
- **Sample:** n=4
- **Source:** `promo_revenue_analysis.md`
- **Interpretation:** Product revenue proxy ~$131.7K/day on solo days; not lift.
- **Evidence label:** correlation
- **Confidence:** low unless the source explicitly documents stronger controls.

## Context and confounders

- Concurrent promotion present on 12/12 instance rows.
- Segments observed: unknown.
- Pricing observed: high, none.
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

2026-04-02, 2026-04-15, 2026-05-02, 2026-05-10, 2026-05-19, 2026-05-23, 2026-06-01, 2026-06-17, 2026-06-30, 2026-07-05, 2026-07-13, 2026-07-28
