# Migration Manifest

**Policy:** `RAW_DATA_AND_MIGRATION_POLICY.md`  
**Rule:** Add a row before moving or archiving a file. Raw sources are never moved.

| ID | Original path | New/archive path | Class | Reason | Replacement | Source preserved | Link check | Status | Date | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| MIG-000 | — | — | — | Manifest initialized; no migration executed | — | yes | n/a | completed | 2026-07-10 | Placeholder documenting initialization only |
| MIG-001 | Existing performance analyses in `mm_calendar/*.md` | `mm_calendar/performance/by_kpi/` | routing | Add canonical per-variant synthesis without moving evidence | `performance/README.md` | yes | passed | completed | 2026-07-10 | Original analyses remain in place and are cited |
| MIG-002 | `prediction_model.md` | `prediction/PREDICTION_AND_OPTIMIZATION.md` | canonical | Replace unbacktested routing authority with post-backtest framework | `prediction/PREDICTION_AND_OPTIMIZATION.md` | yes | passed | completed | 2026-07-10 | Legacy model retained in place as historical source |
| MIG-003 | Scattered source/method notes | `measurement/` | canonical | Centralize inventory, identity, model, methodology, registers, and SOP | `measurement/README.md` | yes | passed | completed | 2026-07-10 | No original source moved |
| MIG-004 | `real_months.json` + Monday/DWH snapshots | `performance/instances/promo_instances.jsonl` | derived | Add normalized one-record-per-line instance index | `performance/instances/promo_instances.jsonl` | yes | passed | completed | 2026-07-10 | Inputs unchanged |
| MIG-005 | — | `_archive/README.md` | routing | Initialize protected archive policy without moving evidence | `measurement/RAW_DATA_AND_MIGRATION_POLICY.md` | yes | passed | completed | 2026-07-10 | No files archived in this run |

## Status definitions

- `planned`: approved entry; operation not executed.
- `blocked`: missing ownership, replacement, or link information.
- `completed`: operation and checks completed.
- `reverted`: operation reversed; original path restored.
