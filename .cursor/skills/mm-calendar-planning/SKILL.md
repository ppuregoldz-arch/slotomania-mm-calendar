---
name: mm-calendar-planning
description: Plans or reviews Slotomania MM calendar months, weeks, and days using approved month guidelines, HARD constraints, reward banks, and live-calendar authority. Use when the user asks to build, change, validate, or explain an MM calendar plan.
---

# MM Calendar Planning

## Read first

1. `DEPARTMENT_TOOL_CONTRACTS.md`
2. `mm_calendar/00_GUIDELINES_ITAY.md`
3. `mm_calendar/BUILD_CALENDAR_ROUTER.md`
4. `mm_calendar/LEARNINGS_MONTH.md`
5. `.cursor/rules/mm_calendar_builder.mdc`

Then read the target `mm_calendar/monthly_guidelines/YYYY-MM.md` and the domain documents selected by `mm_calendar/topics/README.md`.

## Workflow

1. Confirm target month, scope, calendar type, approved monthly guidelines, seasons/events, and business goal.
2. If a required cap, reward bank, allocation, or decision is missing, stop and ask. Never infer it.
3. Respect the authority order. For August 2026, preserve the documented live-Monday authority split.
4. Build in the canonical order from `mm_calendar/LEARNINGS_MONTH.md`.
5. Keep a reward/card ledger and record every explicit exception.
6. Validate before presenting.

For August 2026:

```bash
python3 scripts/build_august_2026_plan.py
python3 scripts/audit_august_2026_plan.py
python3 scripts/validate_season_skus.py
```

Do not use `scripts/validate_calendar.py` as August authority.

## Output

Return the requested plan/review, HARD-rule validation, unresolved decisions, sources, and Monday-write status.

## External-write policy

Planning is local by default. Never run a Monday upload unless the user explicitly approves exact dates. Never run a wide or destructive sync from a general planning request.
