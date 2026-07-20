---
name: mm-calendar-forecast
description: Forecasts or evaluates Slotomania MM calendar Revenue, paying users, Gems usage, and Coins/wager with documented baselines, evidence limits, confidence, and validation. Use when the user requests calendar forecasts, expected KPI impact, performance scenarios, or optimization.
---

# MM Calendar Forecast

## Read first

1. `DEPARTMENT_TOOL_CONTRACTS.md`
2. `mm_calendar/00_GUIDELINES_ITAY.md`
3. `mm_calendar/measurement/SOURCE_INVENTORY.md`
4. `mm_calendar/measurement/MEASUREMENT_METHODOLOGY.md`
5. `mm_calendar/prediction/PREDICTION_AND_OPTIMIZATION.md`
6. `mm_calendar/prediction/BACKTEST_RESULTS.md`
7. `mm_calendar/topics/10_data_performance/README.md`

For DWH work, also follow `.cursor/rules/data_assistant_unified.mdc` and the validation rules it references.

## Workflow

1. Confirm dates, KPIs, calendar version, segment/context, and required freshness.
2. Use the source hierarchy in `SOURCE_INVENTORY.md`.
3. Exclude incomplete current-day data.
4. Use a same-weekday trailing baseline with at least 20 complete eligible days when available.
5. Apply no more than one eligible family scenario; never sum concurrent promo effects.
6. Validate the source, baseline, calculations, and known confounders.
7. Return `insufficient evidence` instead of inventing precision.

## Current forecast limits

- Revenue may use the documented calibrated scenario method and uncertainty.
- PU uses the documented baseline uncertainty; no family currently supports a reliable promo-specific adjustment.
- Gems and Coins/wager are directional unless a separate validated analysis supports a numeric range.
- Never describe the model as causal or high confidence.

Useful checks:

```bash
python3 scripts/backtest_promo_prediction.py
python3 scripts/scorer.py
python3 scripts/validate_promo_knowledge_base.py
```

Refresh DWH snapshots only when the user requests fresh data or freshness is necessary and access is available.

## Output

Include source, baseline method, calculation date, expected direction/range, segment/context, supporting instances, confidence/evidence, validation status, risks/confounders, and an alternative.

## External-write policy

Forecasting is read-only for Monday. Never alter the calendar, knowledge base, or model calibration unless the user explicitly asks for that change.
