# Promotion Measurement Methodology

**Version:** 1.0  
**Last updated:** July 2026

## Non-negotiable principles

1. Preserve raw sources.
2. Never infer a missing result or business rule.
3. Calculate daily metrics first, then aggregate across days.
4. Use complete days only; exclude today.
5. Match the comparison to weekday, audience, season/album phase, and placement where possible.
6. Report nominal result and percentage lift together.
7. Keep real money, coins, gems, and Slotobucks separate.
8. A whole-day outcome is not attributed to every concurrent promo.
9. Log missing, contradictory, non-reproducible, and low-confidence findings centrally.

## Causal-confidence ladder

| Label | Definition | Permitted wording |
|---|---|---|
| Observed result | Direct source value for a day, offer, or participant set | “Observed revenue was…” |
| Measured lift | Difference from a documented baseline | “Measured lift versus the selected baseline…” |
| Attributed lift | A model assigns incremental change after stated controls | “The controlled model attributes…” |
| Correlation | Promo presence and KPI move together without adequate isolation | “Associated with” / “correlated with” |
| Causal evidence | Randomized or credible quasi-experimental identification with validated controls | “Caused” only within the tested population/context |

If concurrent promos, holiday/event timing, album phase, LBP/Lotto peak, Dash Day, segment mix, pricing, placement, audience changes, or missing controls remain material, causal wording is prohibited.

## Baseline selection

### General baseline

- Primary: same weekday over the latest 20 complete eligible days before the instance.
- If fewer than 20 eligible days exist, use all available same-weekday observations and lower confidence.
- Exclude the evaluated day, incomplete days, test populations, and registered anomalous/holiday days unless the question is event-specific.
- For an event-specific comparison, use matched historical events and label the baseline separately.
- Never compare a lift to one adjacent day.

### Revenue

- Primary source: `agg.agg_sm_daily_users_stats.daily_Net_revenue`.
- Daily metric: sum net revenue by `calc_date`.
- Product cross-check: `dwh.sm_fact_payments` only with `tran_status_id=2`, `is_test=0`, and `artificial_ind=0`.
- Report USD/day, nominal USD delta, and percentage delta.
- Current historical reference: `smart_calendar_insights.md` documents a holiday-adjusted regime mean of $638,427 over its stated window. It is a historical reference, not a universal future baseline.

### Paying users

- Daily metric: distinct users with positive approved daily payment/revenue according to the selected canonical query.
- Report payer count, nominal payer delta, and percentage delta.
- Do not mix “payers for one product” with whole-day payers.
- Control or report DAU and audience-size changes.

### Wager

- Prefer total wager or wager per eligible user from DWH.
- If using Tableau median wager, retain its exact aggregation and population label.
- Report coin values in scientific notation when needed; hyperinflated magnitude is expected.
- Day-level all-user wager versus Core presence is correlation unless participant/nonparticipant controls exist.

### Gem usage

- Define whether the metric is Shiny mini-game usage, game-wide internal-purchase spend, or balance delta.
- Never combine gem usage with gem balance.
- Report exact unit and population.
- `shiny_show_performance.md` documents a historical Play-X baseline near 48.7M gems/day for its Apr–Jun source window; do not transplant it to another metric/window.

## Required two-step aggregation

```sql
WITH daily AS (
  SELECT
    calc_date,
    SUM(daily_Net_revenue) AS revenue,
    COUNT(DISTINCT CASE WHEN daily_Net_revenue > 0 THEN user_id END) AS paying_users
  FROM agg.agg_sm_daily_users_stats
  WHERE calc_date BETWEEN :start_date AND :end_date
    AND calc_date < CURRENT_DATE
  GROUP BY calc_date
)
SELECT
  AVG(revenue) AS avg_daily_revenue,
  AVG(paying_users) AS avg_daily_paying_users
FROM daily;
```

For promo-family analysis, first deduplicate the promo calendar to one `(date,family_id)` row, then join daily outcomes.

## Confounder handling

For every instance, record:

- all concurrent family/variant IDs;
- weekday and week/month position;
- holiday/event and machine launch;
- album open/end phase;
- Dash Day;
- LBP/Lotto peak;
- segment and audience population;
- pricing and exact duration/placement;
- source mismatch or missing control.

Methods, from strongest to weakest:

1. randomized/control experiment;
2. participant-level matched/control design;
3. controlled regression or difference-in-differences with pre-registered features;
4. same-weekday matched baseline;
5. raw comparison.

Method strength affects evidence label and confidence; it does not upgrade correlation to causality automatically.

## Holiday and anomaly register

Do not hard-code one undocumented list in multiple analyses. Maintain one approved exclusion list in the measurement pipeline with date, reason, scope, and approval.

Existing sources disagree: `smart_calendar_insights.md` describes eight excluded dates, while `calibrate_model.py` currently lists ten. Until reconciled, analyses must disclose the exact list used and the conflict remains registered.

## Confidence rubric

| Confidence | Minimum conditions |
|---|---|
| High | Reproducible source; adequate sample; matched/control design; consistent direction; material confounders controlled; provenance complete |
| Medium | Reproducible source and consistent direction, but limited sample or residual confounders |
| Low | Small sample, day-level correlation, proxy KPI, source mismatch, or important uncontrolled context |
| Insufficient | Missing baseline/result/provenance, contradictory direction without resolution, or sample too sparse for the requested claim |

Numeric sample thresholds are KPI/design-specific and must be calibrated by backtesting; no universal threshold is silently assumed.

## Validation status

- `source-only`: identity/context captured; KPI not reproduced.
- `existing-reproduced`: existing result independently recalculated from available source.
- `existing-unverified`: result documented but source unavailable or not rerun.
- `dwh-snapshot`: exact value from a dated local DWH snapshot.
- `dwh-validated`: selective query independently verified the result.
- `conflicting`: credible sources disagree.
- `missing`: required evidence unavailable.
- `not-applicable`: field does not apply.

## Selective Vertica validation

Run live queries only for:

- missing high-impact cells;
- registered conflicts;
- non-reproducible existing numbers;
- high-impact recommendations with insufficient provenance;
- backtesting inputs whose result would materially change the model.

For each query:

1. record query purpose, tables, filters, date range, execution date, and row count;
2. use source-specific HARD filters;
3. validate representative users when the metric is user-level;
4. cross-check revenue totals against `daily_Net_revenue`;
5. write results to derived files only;
6. update missing/conflict registers.

## Provenance contract

Every numeric result must store:

- source path/table;
- source pull date;
- calculation date;
- metric definition and unit;
- baseline value, method, and window when lift is reported;
- filters and population;
- evidence label;
- confidence;
- validation status;
- known confounders.

Without these fields, the number may be retained as historical text but cannot drive a confirmed learning or recommendation.

## Recommendation eligibility

A recommendation is eligible only when it includes expected KPI, expected direction/range, applicable segment/context, supporting instances, confidence, risks/confounders, and an alternative.

Low-confidence evidence may produce a clearly labeled experiment suggestion. Insufficient evidence may not produce a performance claim.
