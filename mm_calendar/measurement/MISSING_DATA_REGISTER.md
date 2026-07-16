# Missing Data Register

**Last updated:** July 10, 2026  
**Rule:** Unknown values remain null/empty. This register tracks evidence gaps; it does not authorize inference.

| ID | Affected scope | Missing information | Sources checked | Impact | Required action | Status |
|---|---|---|---|---|---|---|
| MD-001 | April 1–7 and July 10–31 promo rows | Stable Monday source IDs are outside `monday_pull_last_3mo.json` window | Monday pull; `real_months.json` | Fallback hashed instance IDs; lower identity provenance | Refresh a dated Monday export covering full Apr–Jul window | open |
| MD-002 | July 6–31 instances | Exact daily revenue/PU after DWH snapshot end | `wide_revenue_pu.json` | No complete observed outcomes for future/incomplete days | Refresh DWH after each complete day; never fill future values | open |
| MD-003 | Many instances | Explicit target audience/segment absent from source copy | Monday pull; `real_months.json` | Segment-level performance unavailable | Pull Smart Calendar `population_id` or authoritative audience mapping selectively | open |
| MD-004 | Many instances | Exact timestamps/duration absent | Monday date/timeline fields | Placement and duration controls incomplete | Preserve `unknown`; enrich from Smart Calendar only when needed | open |
| MD-005 | Core variants outside June | Comparable wager source unavailable | `core_wager_analysis.md`; referenced Tableau export | Cannot stabilize family/variant wager lift | Import immutable wager exports or query canonical DWH metric | open |
| MD-006 | Shiny variants outside source window | Comparable gem-usage source unavailable | `shiny_show_performance.md`; Shiny CSV references | Variant gem-usage coverage limited | Import immutable Shiny exports or query gem-spend source | open |
| MD-007 | Happy Hour/Jumbo variants | Halo measurement not run | `boosted_gemback_impact.md` | No validated expected range | Run dedicated halo analysis before recommendation claim | open |
| MD-008 | Core causal claims | Participant/nonparticipant treatment flag unavailable | `core_wager_analysis.md`; DWH docs | Day-level correlation cannot support causality | Identify participation source and run controlled user-level validation | open |
| MD-009 | External CSV sources | Canonical repository paths and pull metadata unavailable for several CSV/TSV inputs | Analysis docs and scripts | Existing numbers are not fully reproducible on another machine | Add immutable copies or documented source URIs/checksums | open |
| MD-010 | Unclassified/other variants | Source name lacks an approved repeatable treatment mapping | Monday/real-month rows | Variant-level aggregation may be too broad | Review names; approve mapping or retain `other/unclassified` | open |
| MD-011 | Variant-level revenue attribution | Exact product/offer outcome absent for most instances | Daily totals; existing small-window CSV analysis | Whole-day revenue cannot be assigned to one promo | Selectively query approved payment/offer sources | open |
| MD-012 | Album/LBP/Dash confounder timing | Exact daily phase/peak control not uniformly encoded | Monday descriptions; planning docs | Confidence downgraded | Add authoritative phase/peak calendar source | open |
| MD-013 | Daily DWH/dashboard refresh | July 10 automation failed at Vertica step; local snapshots end around July 3–5 and calibration is dated July 8 | Daily update log; snapshot metadata | Latest outcomes and model evidence are stale | Restore Vertica connectivity, run the approved refresh pipeline, and retain dated snapshot metadata | open |

## Closure rule

A row closes only when the missing value is populated from a traceable source, or when the field is confirmed not applicable. “Estimated” does not close a missing source.
