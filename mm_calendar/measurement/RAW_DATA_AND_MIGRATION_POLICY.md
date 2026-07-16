# Raw Data Protection and Migration Policy

**Last updated:** July 2026

## Immutable raw sources

The following are raw or source snapshots and must never be deleted, edited in place, or overwritten by a migration:

- Monday exports and caches under `mm_calendar/data/`, including `monday_pull_last_3mo.json` and `_monday_raw_cache.json`;
- DWH snapshots under `mm_calendar/data/`, including `wide_revenue_pu.json`, `wide_promo_keys.json`, `sink_mechanic_keys.json`, and `pu_balance_raw.json`;
- source CSV/TSV exports used by analysis scripts;
- historical Monday reference exports under `mm_calendar/documentation/monday_refs/`;
- historical DWH analysis outputs under `dwh_context/outputs/`;
- original human reports and historical summaries used as evidence.

Refresh scripts may create a new dated snapshot or update a documented cache only as part of their normal source-refresh contract. A folder migration must not use that exception.

## Derived files

Generated datasets, normalized indexes, canonical variant documents, registers, coverage reports, and prediction artifacts are derived. They may be regenerated, but each result must preserve source references and calculation metadata.

## Migration rules

1. Inventory a file before moving or archiving it.
2. Add a manifest row before the file operation.
3. Never move a raw source. Add routing links to it in its original location.
4. Archive only a superseded derived summary.
5. Preserve history: archive instead of delete.
6. Record the replacement canonical document, or state `none`.
7. Verify all inbound internal links before and after a move.
8. Mark a manifest row `completed` only after path and link checks pass.
9. If ownership, replacement, or raw/derived status is unclear, set status `blocked` and register the issue.

## Migration manifest

Canonical manifest: `measurement/MIGRATION_MANIFEST.md`.

Required fields:

- manifest ID;
- original path;
- new/archive path;
- classification (`raw`, `derived`, `canonical`, `routing`);
- reason;
- replacement file;
- source preserved (`yes/no`);
- link check;
- status (`planned`, `blocked`, `completed`, `reverted`);
- execution date;
- notes.

## Prohibited actions

- deleting a source after synthesis;
- overwriting source evidence with normalized data;
- replacing an original number without retaining its baseline and provenance;
- moving a file before its manifest entry exists;
- hiding a conflict by choosing one result without registering the competing result.
