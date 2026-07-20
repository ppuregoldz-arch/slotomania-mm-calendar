# MM Department Cursor Tools

**Purpose:** Give every department member the same trained workflows while using their own Cursor as the interface.

## First-time setup

1. Clone `https://github.com/ppuregoldz-arch/slotomania-mm-calendar`.
2. Open the repository folder in Cursor. Do not open a single file.
3. Keep the repository on a feature branch; never work directly on `main`.
4. Request the local-only files from the platform owner when needed:
   - `.cursor/mcp.json` for DWH access;
   - `.cursor/monday.env` for Monday access;
   - `.cursor/github.env` only for approved repository automation.
5. Never commit credentials. The live files above are gitignored.
6. Run `python3 scripts/validate_department_tooling.py`.

## The four tools

Ask Cursor to use the exact skill name:

- **`mm-calendar-planning`** — construct or review a monthly MM calendar.
- **`mm-calendar-forecast`** — forecast Revenue / PU and assess Gems / Coins evidence.
- **`mm-brief-maker`** — create Monetization-Art brief previews or approved Monday briefs.
- **`mm-ops-monday-creator`** — build, validate, preview, or explicitly publish Ops tasks.

Examples:

```text
Use mm-calendar-planning to review August 2026 day 17. Do not write Monday.
```

```text
Use mm-calendar-forecast for August 17. Show sources, baseline, confidence, and validation.
```

```text
Use mm-brief-maker for 2026-08-17. Dry-run only.
```

```text
Use mm-ops-monday-creator for 2026-08-17. Build and validate; do not publish.
```

## Safety model

- Skills are thin workflow entry points. Canonical business rules remain in `mm_calendar/` and `.cursor/rules/`.
- A live instruction from Itay overrides repository documents.
- Missing business rules or numbers are never inferred.
- Planning and forecasting do not write Monday.
- Brief and Ops workflows are dry-run by default.
- Monday writes require an explicit date scope and explicit approval.
- Destructive rebuild, replace, delete, archive, or wide synchronization requires separate explicit approval.
- Every tool returns its sources, assumptions, warnings, validation status, and external-write status.

## Improve the tools safely

1. Submit a **Tool improvement** GitHub Issue with the current output, expected output, evidence, and affected tool.
2. Contributors create a branch and Pull Request; they never edit `main` directly.
3. Canonical rule or script changes require owner review and passing smoke checks.
4. Do not duplicate business rules inside a Skill. Update the canonical source and keep the Skill as a pointer/workflow.
5. Confirmed changes must update `TEAM_WORKLOG.md`.

See `DEPARTMENT_TOOL_CONTRACTS.md` and `CONTRIBUTING.md`.
