# Ops task learnings

**Last updated:** July 2026  
**Purpose:** Start-here index for confirmed Operation - Monetization handoff rules. Detailed construction and board contracts remain canonical.

## Authority and reading order

1. A live instruction from Itay overrides every document.
2. Read [ops_task_construction.md](ops_task_construction.md) for task eligibility, composition, timing, and status rules.
3. Read [ops_board_schema.md](ops_board_schema.md) for board IDs, columns, relations, and safe write behavior.
4. Use [documentation/ops_task_refs/README.md](documentation/ops_task_refs/README.md) only for recent historical execution evidence.
5. Agent workflow is enforced by [ops_task_builder.mdc](../.cursor/rules/ops_task_builder.mdc).

## Confirmed learnings

- **Source and placement:** Build only from an approved MM day and only when Itay asks. Production tasks are subitems under the exact `YYYY-MM-DD` parent on board `2109172490`.
- **MM relation:** Every Ops subitem must relate to its exact source MM item through `board_relation_mkzvrve9`; verify through `BoardRelationValue.linked_items`.
- **Name authority:** MM Name wins over a conflicting Description.
- **No invention:** Never infer prizes, segments, pricing, triggers, IDs, owners, files, or links. Unsupported execution data remains `TBD - owner required`.
- **Lean composer:** Description contains only fields Ops must execute:
  - standard offers: Segment, Prizes, Pricing;
  - other promos: Segment, optional Trigger, Prize;
  - use product-specific schemas only where documented.
- **No duplicated metadata:** Keep dates/times in Start/End columns and Once/Multiple in its dedicated column. Do not repeat them in Description.
- **Promo Time:** `11:00 UTC`. Standard and 24-hour promos run Promo Time to Promo Time.
- **Midnight:** A `00:00 UTC` task with no explicit duration ends at Promo Time. Night Plan runs D+1 `00:00–11:00 UTC`.
- **Monday clock rendering:** Monday displays API timestamps at UTC+3, so apply the −3-hour payload compensation to every task, including Night Plan (`21:00` previous day → visible `00:00`; `08:00` → visible `11:00`).
- **MES timing:** Durations inside milestone prizes are reward durations, not production timing. MES stays Promo Time to Promo Time unless MM explicitly gives a production clock or says time-limited.
- **Lotto peak + LBP:** Calendar parent D creates two separate Night Plan tasks. Both run on D+1 from `00:00` to `11:00 UTC`.
- **LBP timing:** LBP is the overnight Promo Time window, not an arbitrary two-hour period after 12:00 UTC.
- **X2 Extreme Stamp:** When an explicit MM row exists, create a separate task with Segment plus `don't forget UI`. Pairing details belong in the related offer task.
- **Extreme-only scope:** When Itay provides an explicit MM-ID allowlist for an Extreme day, build/write only those rows. Do not pull unrelated same-day tasks into the handoff.
- **Extreme-day identity:** RYD remains RYD; do not silently replace it with Rolling. Canceled / On Hold MM rows do not become active Ops tasks.
- **RLAP / Stash Booster:** Segment + eligible-offer Trigger + segmented Prize lines; no Pricing. Use only approved MM rewards and triggers.
- **X2 GGS:** Calendar amplifier by default; no Ops task unless explicitly requested.
- **Statuses:** Never write Operation Status. Use the most specific M&M blocker; use `Waiting for MM Approval` only when the handoff is complete and config/MCP is ready or not required.
- **Safety:** Dry-run first; one day at a time; add/update only by default. `--replace-day` is destructive and requires explicit approval for that exact parent; `--parent-id` is required when Itay means a nonstandard dated parent. Never move, archive, comment, attach, relate, or assign beyond explicit scope.
- **Validation:** Run `scripts/validate_ops_task_spec_rules.py` after changing generated specs.
- **Historical refs:** `documentation/ops_task_refs/` preserves historical voice. Current field order comes from `ops_task_construction.md` and the composer, not old examples that embed dates or dependency prose.

## Maintenance rule

`TEAM_WORKLOG.md` is a handoff log, not a canonical rule source. Confirmed Ops learnings must be encoded in `ops_task_construction.md` / `ops_board_schema.md` / `ops_task_builder.mdc` and summarized here.
