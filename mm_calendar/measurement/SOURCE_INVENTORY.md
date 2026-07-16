# MM Calendar Source Inventory and Source-of-Truth Hierarchy

**Inventory date:** July 10, 2026  
**Scope:** promotion and calendar planning, measurement, performance, prediction, Monday exports, CSV/JSON sources, and Vertica documentation. Other repository areas are included only when referenced by an in-scope source.  
**Freshness:** dates below are documented pull/calculation dates, not filesystem modification times.

## Reliability scale

| Level | Meaning |
|---|---|
| A | Authoritative system/source with reproducible extraction rules |
| B | Derived from authoritative sources with documented transformation |
| C | Human summary or analysis with method and limitations |
| D | Heuristic, inferred, stale, partial, or non-reproducible evidence |

Reliability does not imply causality. An exact daily total can be Level A while its attribution to one concurrent promo remains low confidence.

## Approved hierarchy by data type

| Data type | Approved order | Notes |
|---|---|---|
| What was operationally live | Smart Calendar DWH latest version per `promo_id`, live-at-snapshot; Monday board export; `real_months.json`; human reports | Smart Calendar requires cancellation filters and carryover window |
| Exact Monday copy, pricing, board row, description | Monday board item/export; generated Monday reference docs | Monday source ID retained |
| Promo family/variant identity | Source row + `PROMO_IDENTITY.md`; approved alias mapping; parser result | Unknown names remain `unclassified` |
| Daily net revenue and payers | `agg.agg_sm_daily_users_stats`; `wide_revenue_pu.json`; documented diary fallback | Revenue uses `daily_Net_revenue` |
| Product/offer revenue | Approved `sm_fact_payments` only with required filters + product mapping; existing CSV analysis | Never use unfiltered payment transactions |
| Wager/coin pressure | `agg.agg_sm_daily_users_stats`/approved DWH; Tableau wager export; `core_wager_analysis.md`; diary direction | Hyperinflated coin magnitude is normal |
| Gem usage | `sm_fact_internal_purchases`/approved DWH; Shiny/Gems CSV exports; existing analyses; diary | Keep gem usage separate from gem balance |
| Family/day promo flags | Smart Calendar DWH + `wide_promo_keys.json`; Monday classification cross-check | Deduplicate `(day,family)` |
| Core/gem-sink flags | Smart Calendar DWH + `sink_mechanic_keys.json`; Monday source text | Shiny/Winovate are gem sinks; Core is coin sink |
| Variant occurrence dates | Monday rows/source IDs; `monday_pull_last_3mo.json`; `variant_dates.json` as derived index | Existing variant parser has known fallback weaknesses |
| Month-specific planning rules | Live Itay instruction; `00_GUIDELINES_ITAY.md`; monthly guideline cap/card bank; constraints | Monthly ceilings remain HARD absent explicit exception |
| Measured promo lift | Reproducible DWH analysis; canonical variant doc; existing documented analysis | Preserve baseline and confounders |
| Prediction constants | Post-backtest calibration artifact; `model_calibration.json`; draft prediction guide | Prediction guide remains draft until backtesting |

## Primary structured sources

| Path/source | Purpose | Coverage | Freshness | Origin/owner | Reliability | Overlap/conflict |
|---|---|---|---|---|---|---|
| `dwh.sm_fact_smart_calendar_promotion_updates` | Operational promo timeline | Historical; queried by requested window | Live DWH | Smart Calendar/DWH | A | Versioned rows; must select latest and filter cancellations |
| `agg.agg_sm_daily_users_stats` | Daily revenue, PU, DAU, wager, balances | Historical daily | Live DWH | SM DWH | A | Daily attribution still confounded |
| `dwh.sm_fact_payments` | Approved transactions/product revenue | Historical transactions | Live DWH | SM DWH | A with required filters | 18–25× inflation if status/test filters omitted |
| `dwh.fact_sm_user_offer_history_po2` | Offer impression/purchase/state | Historical offer events | Live DWH | SM DWH | A | Offer-name identity normalization required |
| `dwh.sm_fact_internal_purchases` | Gem spend by source | Historical internal purchases | Live DWH | SM DWH | A | Requires currency and source mapping |
| `mm_calendar/data/monday_pull_last_3mo.json` | Read-only Monday rows with IDs/copy/pricing | 2026-04-08–2026-07-09; 972 rows | Pulled 2026-07-09 | Monday board 18388590642 | A snapshot | Partial April and July; overlaps `real_months` |
| `mm_calendar/data/_monday_raw_cache.json` | Raw Monday GraphQL cache | Board snapshot | Pull-time cache | Monday board | A raw snapshot | Do not edit or move |
| `mm_calendar/data/real_months.json` | Four-month day model with Monday content and selected outcomes | 2026-04-01–2026-07-31; 122 days; 1,180 item/season rows | Generated July 2026 | `pull_real_months.py` | B | Future July rows lack actual outcomes; contains fallback/heuristic fields |
| `mm_calendar/data/wide_revenue_pu.json` | Exact daily net revenue and payer count | 2025-11-01–2026-07-05; 246 days | Pulled 2026-07-06 | DWH refresh script | B/A snapshot | Primary local daily outcomes |
| `mm_calendar/data/wide_promo_keys.json` | DWH Smart Calendar family flags at 11:00 UTC | 2025-11-01–2026-07-05; 247 days | Pulled 2026-07-06 | DWH refresh script | B | Regex family classification |
| `mm_calendar/data/sink_mechanic_keys.json` | Coin/gem-sink day flags | 2026-04-01–2026-07-05; 96 days | Pulled 2026-07-06 | DWH refresh script | B | Regex classification; no participant-level attribution |
| `mm_calendar/data/pu_balance_raw.json` | Active-PU median coin/gem balance snapshots | From 2026-04 onward where available | Pulled July 2026 | DWH refresh script | B/A snapshot | Segment-specific; not daily payer count |
| `mm_calendar/data/variant_dates.json` | Existing variant/date/context index | Primarily 2026-05–2026-07; 23 variants, 226 occurrences | Generated July 2026 | Monday parser | B/D by row | MGAP unknown defaults to BOGO; dedup is date-only |
| `mm_calendar/data/model_calibration.json` | Current model coefficients and self-checks | Revenue 2026-04-09–07-05; PU 05-09–07-05; wide history used | Computed 2026-07-08 | `calibrate_model.py` | B | Uses priors for thin data; not final until independent backtest |
| `mm_calendar/data/august_2026_plan.json` | August draft plan | 2026-08 | Builder output July 2026 | Calendar builder | B plan | Not historical actuals |

**Pipeline health:** the July 10, 2026 daily automation failed at the Vertica refresh step. Local DWH snapshots currently end around July 3–5, were pulled July 4–6, and calibration was computed July 8. Treat newer dashboard/instance outcomes as unavailable until a successful refresh is documented.

## Canonical planning and rule documents

| Path/group | Purpose | Freshness | Origin/owner | Reliability | Notes |
|---|---|---|---|---|---|
| `00_GUIDELINES_ITAY.md` | Standing authority and evidence rules | July 2026 | Itay instructions | A policy | Overrides lower documentation |
| `monthly_guidelines/2026-07.md`, `2026-08.md` | Monthly caps, card bank, exclusions | Target month | Economy/Nivi | A policy for month | Never extrapolate to another month |
| `constraints.md`, `rules_cheatsheet.md` | Scheduling constraints | July 2026 | Planner knowledge base | B policy summary | Older conflicts defer upward |
| `PRIZE_PRIORITY_AND_MONTH_BUILD.md` | Prize/build workflow | July 2026 | Planner synthesis | B | Routing authority will be rewired |
| `lanes.md`, `offer_construction.md`, `rolling_offer.md` | Product anatomy and construction | July 2026 | Monday examples + Itay corrections | B | `rolling_offer.md` supersedes old BXGY builder helper |
| `recurring_events.md`, `day_planning_template.md`, `approval_process.md` | Anchors, day composition, approval timing | July 2026 | Planner synthesis | B/C | Validate against target-month guidelines |
| `album_cards.md`, `nivi_collector_album_prizes.md`, `core_mes_references.md`, `lotto_bonus.md`, `dice_promos.md` | Domain references | July 2026 | Economy/CRM/Monday synthesis | B/C | Card bank still comes from monthly guideline |
| `dpu_calendar.md` | DPU segment planning | July 2026 | Segment-specific synthesis | C | Do not generalize to all users |
| `art_inventory.md` | CRM art availability | July 2026 | CRM3 scan | B snapshot | Operational availability, not performance |

## Historical Monday reference collection

`mm_calendar/documentation/monday_refs/` is a read-only derived collection from board `18388590642`, generated by `scripts/pull_monday_feature_refs.py`. Its source snapshot is `data/monday_pull_last_3mo.json`.

Included files:

- `sm_monday_ref_{blast,battlesheep,snl,daily_deal,prize_mania,rolling_offer,ads_po,core,time_limited_promotions,winovate,mega_pods,golden_spin,lotto_bonus_l_b_p,buy_all,reveal_your_deal,album}.md`
- `sm_monday_rewards_skus.md`
- `sm_monday_ref_unclassified.md`
- collection `README.md`

Coverage is the pull window, not a complete product history. Reliability is B for exact exported text and C for keyword classification. These files are examples, not scheduling law.

## Performance and measurement analyses

| Path | KPI/purpose | Coverage | Freshness | Reliability | Known limitation/conflict |
|---|---|---|---|---|---|
| `smart_calendar_insights.md` | Revenue/PU family ranking | 2025-11-01–2026-07-02, 242 days | July 2026 v2.1 | B/C | Day-level correlation; holiday exclusions differ from calibration list |
| `relationships_deep.md` | DOW/month/crowd/interaction patterns | Nov 2025–Jul 2026 | July 2026 | C | Observational |
| `deep_research_insights.md` | Apr–Jul promo findings | Apr–Jul 2026 | July 2026 | C | Mixed source cuts; preserve confounders |
| `promo_revenue_analysis.md` | Product revenue by variant | May–Jun 2026 | June 2026 | C | Small n; Sticky Bundle proxy for DD; conflicts with clean family results |
| `performance_benchmarks.md` | Feature revenue ranking | Existing CSV window | 2026 | C | Feature-level, not isolated promo lift |
| `shiny_show_performance.md` | Shiny gem usage by variant | Apr–Jun 2026 | June 2026 | C | Small n; event/album confounding; removed Clan Pack still appears historically |
| `boosted_gemback_impact.md` | Gem/revenue halo | June 2026, n=5 Gemback days | July 2026 | C | Correlation and sale/event confounding |
| `core_wager_analysis.md` | Core mechanic wager | June 2026 | July 2026 | C/D | Day-level all-user wager; n=1–6; no participant control |
| `daily_mm_reports.md` | Operational evening observations | Apr–Jun 2026 | July 2026 synthesis | C/D | Human notes; some estimated/fallback outcomes |
| `learnings.md`, `top_promos.md`, `patterns_derived.md`, `deep_study_may_june.md` | Operational/pattern summaries | Mainly Apr–Jul 2026 | July 2026 | C | Derived summaries; lower authority than canonical evidence |

## Prediction artifacts

| Path | Purpose | Status | Reliability |
|---|---|---|---|
| `prediction_model.md` | Existing v5 heuristic | Superseded as final authority; retained source | C |
| `data/model_calibration.json` | Generated coefficients/self-check | Input to new draft and backtest | B |
| `scripts/calibrate_model.py` | Calibration implementation | Reproducible derived pipeline | B |
| `scripts/scorer.py` | Existing score logic | Supporting tool | C until reconciled |
| `scripts/build_calendar_html.py` | Dashboard prediction consumer | Downstream dependency | B implementation |

No existing prediction artifact is considered validated by the new framework until the historical backtest and post-backtest revision are complete.

## Relevant scripts and outputs

| Script group | Outputs/use | Reliability note |
|---|---|---|
| `pull_real_months.py`, `pull_monday_feature_refs.py`, `pull_variant_dates.py` | Monday-derived JSON/docs | Reproducible; parser classifications need canonical identity validation |
| `refresh_dwh_snapshots.py` | Four local DWH caches | Reproducible; currently rewrites cache paths by design, so preserve dated copies during knowledge refresh |
| `calibrate_model.py`, `corr_analysis.py`, `deep_research.py` | Model/relationship analyses | Derived observational analysis |
| `promo_revenue_join.py`, `gemback_impact.py`, `shiny_gem_analysis.py`, `wager_core_analysis.py` | KPI-specific analysis | Depends on external CSV/Tableau exports and documented windows |
| `build_august_2026_plan.py`, `audit_august_2026_plan.py`, `validate_calendar.py` | Plan generation/validation | Plan rules, not historical outcome evidence |
| `build_calendar_html.py` | Dashboard generation and consumer | Must remain compatible with existing plan/model formats |
| `upload_mm_calendar_day_monday.py` and Monday client scripts | External board writes | Out of scope unless explicitly approved |

## External CSV/TSV sources referenced by in-scope analyses

| Source | Referenced by | Coverage/status | Reliability |
|---|---|---|---|
| `Revenue By Product.csv` | promo revenue and Gemback analyses | May–Jun 2026 documented; local path not canonical | B raw export if present |
| `Shiny Experience.csv`, `Shiny Experience (1).csv` | Shiny analysis | Apr–Jun 2026 | B raw exports if present |
| `Gems Consumption.csv` | Gemback/prediction | June 2026 documented | B raw export if present |
| `Daily Wager (W_O Migrated Users).csv` | Core wager analysis | 2026-06-04–06-30 documented | B raw export if present |
| `core_june_2026.tsv` | Core/Monday join | June 2026 | B derived export; path availability requires check |

These referenced raw exports are not all stored under `mm_calendar/`; absence or machine-local paths are registered as missing provenance/dependency issues.

## Vertica documentation and referenced DWH outputs

- `dwh_reference.md` is the calendar-facing table/query guide.
- `smart_calendar.md` defines version selection, live-at-snapshot logic, cancellation filters, and month carryover.
- `.cursor/mcp.json` configures local connectivity and is not an analytical source; credentials must never be copied into documentation.
- `dwh_context/` is included only for analyses explicitly referenced by calendar sources. Relevant known collections include Rolling Offer dates/averages, Prize Mania versus Rolling, Hammers investigations, and tracking investigations. These remain historical evidence and are not automatically canonical.

## Confirmed overlaps and conflicts

1. `real_months.json`, Monday references, and `monday_pull_last_3mo.json` overlap; the raw pull preserves row identity, while `real_months` adds derived day fields.
2. Monday board and Smart Calendar can disagree because one is planning copy and the other operational live truth. Preserve both and register mismatches.
3. `promo_revenue_analysis.md` calls MGAP Bigger strongest on a two-month product-revenue cut; `smart_calendar_insights.md` finds near-neutral clean day-level family lift after holiday removal. They answer different questions and must not be merged.
4. Extreme Stamp has strong raw/conditional readings but near-neutral clean standalone family lift.
5. Golden Spin is consistently negative but has only 10 recent family days.
6. DD Hammers is a stable product-revenue proxy in one source but can be confounded in day-level outcomes.
7. Clan Pack appears in historical analyses but is prohibited for future planning.
8. Holiday exclusion lists are inconsistent: one document says eight dates while current calibration code includes ten.
9. Existing `variant_dates.json` defaults unclassified MGAP rows to BOGO and should not be treated as canonical identity.
10. `real_months.json` reports 63 Smart Calendar/Monday mismatches, 27 Monday-only days, and 5 Smart-only days across the 122-day Apr–Jul calendar. Monday describes planning/copy; Smart Calendar describes operational live-at-snapshot state.
11. `validate_calendar.py` and part of the dashboard audit still read a July canvas, while the August source of truth is the builder-generated August JSON plus its dedicated audit.
12. The current August human audit reports MGAP week/count/spacing violations; this reorganization did not alter the plan or Monday.

All unresolved items must appear in `UNRESOLVED_CONFLICTS.md`; unavailable evidence must appear in `MISSING_DATA_REGISTER.md`.
