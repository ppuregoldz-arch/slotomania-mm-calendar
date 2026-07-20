---
name: mm-ops-monday-creator
description: Builds, validates, previews, or explicitly publishes Slotomania Operation - Monetization tasks from approved MM calendar rows. Use when the user requests Ops Monday tasks, operational descriptions, timing corrections, or MM-to-Ops handoffs.
---

# MM OPS Monday Creator

## Read first

1. `DEPARTMENT_TOOL_CONTRACTS.md`
2. `mm_calendar/00_GUIDELINES_ITAY.md`
3. `mm_calendar/LEARNINGS_OPS.md`
4. `mm_calendar/ops_board_schema.md`
5. `mm_calendar/ops_task_construction.md`
6. `mm_calendar/documentation/ops_task_refs/README.md`
7. `.cursor/rules/ops_task_builder.mdc`

## Workflow

1. Confirm exact date, approved MM source, optional MM-ID allowlist, and intended Ops parent.
2. Build one day at a time from live MM rows:

```bash
python3 scripts/build_ops_tasks_from_live_days.py --date YYYY-MM-DD
```

3. Validate:

```bash
python3 scripts/validate_ops_task_spec_rules.py
```

4. Dry-run the exact spec and parent:

```bash
python3 scripts/upload_ops_task_monday.py mm_calendar/data/ops_tasks/YYYY-MM-DD.json --parent-id PARENT_ID
```

5. Show warnings and unresolved execution fields. Do not invent values.
6. Write only when the user explicitly requests Monday creation/update for that exact date.
7. Verify every written task directly: visible Start/End, exact MM relation, title, M&M Status, and blank Operation Status.

## Timing contract

- Promo Time is `11:00 UTC`.
- Standard and 24-hour promos run Promo Time to Promo Time.
- A `00:00 UTC` task without duration ends at Promo Time.
- Night Plan runs D+1 `00:00–11:00 UTC`.
- Monday payloads use the documented −3-hour compensation so visible clocks equal intended UTC.
- Reward durations never become production timing.

## Safety

- Dry-run by default.
- No missing parent creation without explicit permission.
- No `--replace-day`, delete, archive, move, comment, assignment, or attachment without exact permission.
- Never write Operation Status.
- An explicit MM-ID allowlist is a HARD scope boundary.

## Output

Return spec path, task count, warnings/blockers, validation result, dry-run summary, external-write status, and direct verification results for approved writes.
