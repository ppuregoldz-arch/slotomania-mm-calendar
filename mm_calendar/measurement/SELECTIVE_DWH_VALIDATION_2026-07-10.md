# Selective Vertica Validation — July 10, 2026

## Scope

Validated four registered high-impact/conflicting variants only:

- DD Hammers
- Extreme Stamp
- Golden Spin
- MGAP Bigger

## Sources and method

- Promo dates: `dwh.sm_fact_smart_calendar_promotion_updates`
  - latest row per `promo_id` by `update_ts DESC, insert_id DESC`;
  - cancelled names/statuses and `Operation - Daily View` excluded;
  - distinct start date per classified variant.
- Outcomes: `agg.agg_sm_daily_users_stats`
  - `SUM(daily_Net_revenue)`;
  - distinct users with `daily_Net_revenue > 0`;
  - `user_id > 0`;
  - daily aggregation first.
- Window: 2026-04-01 through 2026-07-05.
- Same-weekday baseline within the same window.
- Excluded dates: 2026-04-04, 2026-05-05, 2026-05-25, 2026-07-04.

The first connection attempt closed at the Vertica load balancer; the unchanged retry succeeded.

## Results

| Variant | n dates | Avg daily revenue | DOW baseline | Revenue difference | Avg PU | DOW PU baseline | PU difference |
|---|---:|---:|---:|---:|---:|---:|---:|
| DD Hammers | 38 | $646,142 | $644,379 | +0.27% | 27,576 | 27,601 | −0.09% |
| Extreme Stamp | 23 | $673,185 | $625,061 | +7.70% | 26,574 | 26,242 | +1.26% |
| Golden Spin | 11 | $588,900 | $621,998 | −5.32% | 25,400 | 25,932 | −2.05% |
| MGAP Bigger | 12 | $684,444 | $659,252 | +3.82% | 28,281 | 27,790 | +1.77% |

## Interpretation

- These are **measured whole-day correlations**, not attributed or causal lift.
- DD Hammers is approximately neutral on whole-day revenue/PU in this date-start cut; this does not contradict the separate product-revenue proxy.
- Golden Spin remains negative in direction, consistent with the wider historical analysis, but still has a thin recent sample.
- Extreme Stamp and MGAP Bigger are positive in this Apr–Jul cut. Wider-window holiday-adjusted sources report lower standalone values. Event placement and concurrent promos remain unresolved confounders.
- The validation does not resolve product-level revenue because approved offer/product attribution was not queried in this pass.

## Validation status

- Daily revenue and PU values: `dwh-validated`.
- Variant attribution: `correlation`, low confidence.
- CF-001 through CF-005 remain open where their conflict concerns scope, baseline window, holiday list, or product versus whole-day attribution.
