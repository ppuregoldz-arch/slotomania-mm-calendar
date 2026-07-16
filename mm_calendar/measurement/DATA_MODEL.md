# Promotion Data Model

**Version:** 1.0  
**Last updated:** July 2026  
**Canonical instance format:** UTF-8 JSON Lines at `performance/instances/promo_instances.jsonl`; one independently parseable JSON object per line.

## Required instance fields

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `schema_version` | string | yes | `1.0` |
| `instance_id` | string | yes | Globally unique ID from `PROMO_IDENTITY.md` |
| `logical_promo_group_id` | string/null | yes | Links segmented rows belonging to one logical treatment |
| `family_id` | enum | yes | Canonical family |
| `family_name` | string | yes | Human-readable family |
| `variant_id` | string | yes | Canonical `<family>--<variant>` |
| `variant_name` | string | yes | Human-readable variant |
| `promo_name` | string | yes | Exact source name |
| `start_date` | ISO date | yes | Occurrence start |
| `end_date` | ISO date | yes | Inclusive display end for the instance index |
| `duration_hours` | number/null | yes | Only when explicit or calculable from exact timestamps |
| `target_audience` | array[string] | yes | Empty when unknown |
| `segment` | enum | yes | `all`, known segment, or `unknown` |
| `day_type` | array[enum] | yes | Calendar context; at least `normal` if no explicit type |
| `placement` | enum | yes | `promo-time`, `night-plan`, `time-limited`, `multi-day`, or `unknown` |
| `pricing` | enum | yes | `low`, `medium`, `high`, `max`, `mixed`, `none`, `unknown` |
| `mechanic` | string/null | yes | Source-backed mechanic only |
| `rewards` | array[object] | yes | Empty when not extractable; no inferred rewards |
| `main_kpi` | KPI/null | yes | Inherited family default or documented override |
| `main_kpi_level` | enum | yes | `family-default`, `variant-override`, `instance-override`, `unassigned` |
| `main_kpi_override` | object/null | yes | `{reason, source}` when override is used |
| `secondary_kpis` | array[KPI] | yes | Documented secondary goals |
| `actual_results` | object | yes | KPI observations keyed by KPI |
| `baseline` | object/null | yes | Value/method/window/source |
| `lift_vs_baseline` | object/null | yes | Nominal and percentage lift with evidence label |
| `nominal_volume` | object | yes | Explicit counts/amounts only |
| `concurrent_promotions` | array[string] | yes | Family/variant IDs known live that day |
| `known_confounders` | array[enum] | yes | Explicit context flags |
| `result_confidence` | enum | yes | `high`, `medium`, `low`, `insufficient` |
| `evidence_type` | enum | yes | Causal-confidence ladder value |
| `validation_status` | enum | yes | Provenance/validation status |
| `what_worked` | array[string] | yes | Empty unless supported |
| `what_did_not_work` | array[string] | yes | Empty unless supported |
| `reuse_recommendation` | enum | yes | Evidence-bound recommendation |
| `best_timing` | array[string] | yes | Empty unless supported |
| `source_refs` | array[object] | yes | At least one traceable source |
| `calculation_date` | ISO date/null | yes | Required for calculated KPI values |
| `notes` | array[string] | yes | Non-numeric context |

## Numeric result object

Each `actual_results.<kpi>` object must contain:

```json
{
  "value": 762122,
  "unit": "usd_per_day",
  "scope": "whole_day",
  "attribution": "not_attributed",
  "source": "mm_calendar/data/wide_revenue_pu.json",
  "source_date": "2026-07-06",
  "calculation_date": null,
  "baseline_method": null,
  "validation_status": "dwh-snapshot",
  "confidence": "high",
  "evidence_type": "observed-result"
}
```

Rules:

- Whole-day results repeated on concurrent promo instances are observations, not promo-attributed results.
- A calculated value requires `calculation_date` and `baseline_method`.
- Null is preferable to an inferred number.
- Real-money revenue and virtual-currency amounts never share a unit or get added.

## Source reference object

```json
{
  "source_type": "monday-export",
  "path_or_table": "mm_calendar/data/monday_pull_last_3mo.json",
  "source_id": "11458112000",
  "pulled_at": "2026-07-09",
  "fields_used": ["name", "product", "date", "timeline", "description", "pricing"]
}
```

## Controlled vocabularies

### Main and secondary KPI

- `revenue`
- `paying_users`
- `wager`
- `gem_usage`

### Family IDs

- `daily-deal`
- `rolling-offer`
- `mgap`
- `buy-all`
- `decoy-bonanza`
- `ryd`
- `coin-sale`
- `prize-mania`
- `counter-po`
- `payment-offer`
- `gems-sale`
- `boosted-gemback`
- `ggs`
- `extreme-stamp`
- `happy-hour`
- `golden-spin`
- `core`
- `clan-dash`
- `shiny-show`
- `winovate`
- `short-term-season`
- `mid-term-season`
- `album`
- `lotto-lbp`
- `ads`
- `event`
- `slotobucks`
- `other`
- `unclassified`

### Segment

- `all`
- `dpu`
- `npu`
- `dormant`
- `pu`
- `ic`
- `black-diamond`
- `finishers`
- `tier-6-7`
- `mixed`
- `unknown`

### Day type

- `normal`
- `sale`
- `dash-day`
- `event`
- `holiday`
- `album-open`
- `album-end`
- `machine-launch`
- `lbp-peak`
- `lotto-peak`
- `month-start`
- `month-end`

### Known confounder

- `concurrent-promotions`
- `holiday-event`
- `album-timing`
- `lbp-lotto-peak`
- `dash-day`
- `segment-mix`
- `weekday-placement`
- `pricing`
- `duration-window`
- `audience-size`
- `missing-control`
- `small-sample`
- `source-mismatch`
- `future-or-incomplete-day`

### Evidence type

- `observed-result`
- `measured-lift`
- `attributed-lift`
- `correlation`
- `causal-evidence`
- `insufficient-evidence`

### Validation status

- `source-only`
- `existing-reproduced`
- `existing-unverified`
- `dwh-snapshot`
- `dwh-validated`
- `conflicting`
- `missing`
- `not-applicable`

### Reuse recommendation

- `prefer`
- `eligible`
- `conditional`
- `avoid`
- `historical-only`
- `insufficient-evidence`
- `not-applicable`

## Main KPI inheritance map

This map is a default, not a constraint on every variant.

| Family | Default Main KPI | Notes |
|---|---|---|
| Daily Deal | `revenue` | A breadth-focused variant may override to `paying_users` |
| Rolling, MGAP, Buy All, Decoy/Bonanza, RYD, Coin Sale, Counter PO, payment offers | `revenue` | Preserve pricing/segment context |
| Prize Mania | `paying_users` | Revenue-focused purchase treatment may override |
| Clan-Dash | `paying_users` | Not a VFM second offer |
| Core | `wager` | Includes Spin Zone/PYP/MES/coin-sink Custom Pod |
| Shiny Show, Winovate | `gem_usage` | Gem sinks, not Core |
| Gems Sale | `revenue` | Gem-balance/usage may be secondary |
| Boosted Gemback | `gem_usage` | Revenue halo is secondary; no direct SKU revenue claim |
| GGS | `gem_usage` | Revenue may be secondary |
| Extreme Stamp, Happy Hour | `revenue` | Toppers/amplifiers; attribution usually low |
| Season, Album, event, ADS | null | Assign only with explicit source objective |

Every variant/instance override must store a reason and source. Do not force variants with different intended player actions to share a family KPI.

## Validation requirements

The JSONL validator must enforce:

1. every line parses independently;
2. required fields exist;
3. dates and IDs are valid;
4. all controlled values are allowed;
5. `instance_id` is unique;
6. `variant_id` starts with `family_id + "--"`;
7. at least one `source_ref` exists;
8. every numeric KPI result has source, scope, unit, confidence, evidence type, and validation status;
9. overrides have reason and source;
10. no null/unknown value is replaced by a guessed value.
