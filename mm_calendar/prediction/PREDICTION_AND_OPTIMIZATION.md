# Prediction and Optimization Framework — Post-Backtest v1

**Status:** Post-backtest, limited calibration  
**Backtest:** `BACKTEST_RESULTS.md` and `backtest_results.json`  
**Last revised:** July 10, 2026

This document was drafted from the prior v5 model, backtested with rolling-origin historical data, and revised from observed errors. It is not a causal model.

## What changed after backtesting

The tested additive family model produced:

- Revenue: 92 test days, MAPE 8.0%, MAE $50K, +$13.5K bias, direction accuracy 41.6%, empirical range coverage 72.8%.
- Paying users: 92 test days, MAPE 7.6%, MAE 2,003, +1,478 bias, direction accuracy 24.4%, range coverage 65.2%.
- Wager, gem usage, and segment performance: insufficient comparable evidence.

Therefore:

1. Do not add every concurrent promo delta to a point forecast.
2. Use a same-weekday baseline as the central forecast.
3. Use promo effects as bounded scenarios only when out-of-sample family evidence is eligible.
4. Do not issue promo-specific PU, wager, gem-usage, or segment ranges from this model.
5. Do not describe the model as high-confidence or causal.

## Forecast method

### Central estimate

```text
central_revenue =
  trailing_same_weekday_revenue
  + documented_audience_adjustment
  + explicit_event_or_machine_scenario
  + at_most_one_eligible_family_scenario
```

- `trailing_same_weekday_revenue`: at least 20 latest complete eligible days where available.
- `documented_audience_adjustment`: only when recent DAU/PU measurements support it.
- `event_or_machine_scenario`: kept separate from ordinary promo lift.
- Never sum correlated family effects merely because they coexist.

### Empirical uncertainty

- Revenue: use at least **±$75K** around the central estimate for ordinary non-holiday days. This is the observed 80th-percentile absolute backtest error; actual tested coverage was only 72.8%.
- Paying users: use at least **±3,200 PU**. Tested coverage was 65.2%.
- Flag holiday/event forecasts separately; the backtest excluded flagship holidays and does not calibrate those peaks.

Do not present a narrower range without a newer documented backtest.

## Eligible revenue family scenarios

Eligibility rule derived from the current backtest: at least 8 out-of-sample test dates and at least 60% direction accuracy. This is a minimum evidence gate, not high confidence.

| Family | Test n | Direction accuracy | Scenario adjustment | Confidence | Interpretation |
|---|---:|---:|---:|---|---|
| Custom Pod | 10 | 70.0% | +$25K central scenario | medium | Average actual DOW residual was +$50K, but the forecast effect was deliberately shrunk |
| Coin Sale | 8 | 62.5% | +$15K central scenario | low/medium | Positive direction, limited sample |
| Rolling More-for-Less | 13 | 69.2% | +$12K central scenario | medium | Small positive residual, more stable than broad Rolling |

Each adjustment still inherits the ±$75K day-level uncertainty and is a correlation, not attributed causal lift.

All other family coefficients are excluded from performance-based point adjustments until a new backtest passes the gate. They may still be scheduled because of product obligations, monthly rules, economy needs, or explicit Itay instruction.

## KPI-specific limits

### Paying users

No family passed a reliable PU direction gate in this backtest. Forecast PU from the trailing same-weekday baseline with ±3,200 uncertainty. Promo-specific PU claims require separate evidence.

### Wager

`core_wager_analysis.md` provides directional June correlations. Spin Zone and PYP are better-supported than other Core variants, but no cross-window backtest exists. Return **insufficient evidence** for a numeric expected wager range.

### Gem usage

`shiny_show_performance.md` and `boosted_gemback_impact.md` provide limited-window directional evidence. They support test prioritization, not a calibrated future range. Return **insufficient evidence** for a numeric expected gem-usage range outside the documented source context.

### Segment performance

The daily snapshot lacks canonical segment outcomes. Return **insufficient evidence** for segment-specific lift unless a selective query or experiment supplies the segment result.

## What moves players by intended action

These are evidence-labeled planning signals, not universal causal claims.

| Intended action | Better-supported options | Evidence status |
|---|---|---|
| Purchase/revenue | Custom Pod, Coin Sale, Rolling BMFL | Passed limited revenue direction gate |
| Broad payer participation | No family passed current PU gate | Insufficient evidence for numeric promo adjustment |
| Machine play/coin wager | Spin Zone, PYP | Directional June correlation only |
| Gem spend | Shiny Joker/All Cards treatments | Directional Apr–Jun Shiny usage correlation |
| Gem-economy halo | Boosted Gemback | Small-sample correlated halo; sale/event confounded |

Historical Clan Pack results are historical-only because current policy prohibits the reward.

## Recommendation eligibility

Every recommendation must include:

1. expected KPI;
2. expected direction and range;
3. applicable segment and calendar context;
4. supporting historical instance IDs/dates;
5. evidence label and confidence;
6. risks and confounders;
7. an alternative recommendation.

### May recommend as performance-supported

- The KPI has an eligible backtested family scenario or a separately validated KPI-specific result.
- Context is materially comparable.
- Required provenance exists.
- No open conflict would reverse the decision.
- The recommendation does not break current policy/caps.

### May recommend only as an experiment

- Evidence is low confidence but directionally useful.
- The expected range is explicitly “not calibrated” or uses the broad empirical day-level range.
- A measurement plan/control is included.

### Must return insufficient evidence

- No comparable baseline or numeric result.
- Requested KPI, segment, or variant was not backtested/validated.
- Material source conflict remains unresolved.
- Fewer than 8 out-of-sample family dates or direction accuracy below 60% for a performance-based revenue scenario.
- The requested precision is narrower than observed backtest error.
- Causal wording is requested without causal evidence.

## Optimization procedure

1. Validate HARD calendar rules and monthly caps first.
2. Identify the day's intended player action and Main KPI.
3. Calculate the DOW baseline and uncertainty.
4. Check whether one eligible family scenario fits the day and avoids cannibalization.
5. Check balance needs: Core for coin pressure; Shiny/Winovate for gem pressure.
6. Cite supporting instances and conflicts.
7. Provide one alternative with lower evidence or lower operational cost.
8. If evidence is insufficient, recommend a controlled test rather than a claimed winner.

## Required recommendation format

```text
Recommendation:
Expected KPI:
Expected direction and range:
Segment/context:
Supporting instances:
Evidence/confidence:
Risks/confounders:
Alternative:
```

## Known failure cases

- Additive stacking double-counts correlated concurrent promos.
- Holiday/event peaks are outside the calibrated ordinary-day range.
- Pricing, duration, album phase, LBP peak, and audience changes are incompletely encoded.
- Whole-day outcomes do not isolate one promo.
- PU direction forecasting is not currently reliable.
- Wager, gem usage, and segment ranges are not backtested.

Re-run `scripts/backtest_promo_prediction.py` after each monthly refresh and revise this document only from documented out-of-sample errors.
