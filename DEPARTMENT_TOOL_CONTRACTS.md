# MM Department Tool Contracts

These contracts define the minimum information and safe output for a context-free Cursor. They route to canonical sources; they do not replace business rules.

## Shared contract

Every tool must:

1. Read `mm_calendar/00_GUIDELINES_ITAY.md`.
2. Follow `mm_calendar/BUILD_CALENDAR_ROUTER.md` and the named Skill.
3. State the exact input scope.
4. Never invent missing rules, values, rewards, segments, dates, sources, or IDs.
5. Return:
   - sources and authority used;
   - assumptions and unresolved information;
   - output or proposed changes;
   - validation performed and result;
   - external-write status.
6. Leave Monday, GitHub, DWH, and shared-drive systems unchanged unless the user explicitly authorizes the relevant mutation.

## `mm-calendar-planning`

**Required inputs**

- Target month and calendar type.
- Approved `mm_calendar/monthly_guidelines/YYYY-MM.md`.
- Known seasons, album phase, events, machine launches, and business goals.
- Exact requested scope: full month, week, or date.

**Output**

- Proposed plan or review.
- HARD-rule and reward/card-ledger validation.
- Conflicts, missing decisions, and explicit exceptions.
- Monday status: `not written` unless exact write scope was separately approved.

**Block**

- Missing month guidelines, reward bank, caps, or required business decision.
- Any request to overwrite live authority without explicit approval.

## `mm-calendar-forecast`

**Required inputs**

- Target dates and requested KPIs.
- Calendar rows or approved plan version.
- Baseline period and data freshness requirement.
- Segment/context when relevant.

**Output**

- Revenue: same-weekday baseline with documented uncertainty and at most one eligible family scenario.
- PU: baseline with documented uncertainty; no unsupported promo-specific adjustment.
- Gems and Coins/wager: directional evidence or `insufficient evidence` unless a separate validated analysis supports a numeric range.
- Source, baseline method, calculation date, confidence, validation, risks, and alternative.

**Block**

- Causal language without causal evidence.
- Numeric Gems/Coins range without a validated source.
- Forecast precision narrower than current documented backtest uncertainty.

## `mm-brief-maker`

**Required inputs**

- Exact promotion date and approved MM source rows.
- Theme/mechanic/prize information present in the source.
- Whether the request is dry-run or an explicitly approved Monday write.
- Explicit permission for any in-flight override or destructive rebuild.

**Output**

- Classified parent brief and required asset subitems.
- Exact embedded reference and CRM3 folder evidence where available.
- Dry-run summary or created/updated pulse IDs.
- Validation of scope, people mapping, status, and references.

**Block**

- Unsupported theme, asset, hook, pricing, or product scope.
- Nonblank in-flight MM status without explicit override.
- Rebuild/delete without exact approval.

## `mm-ops-monday-creator`

**Required inputs**

- Exact date and approved MM source.
- Optional MM-item allowlist.
- Exact Ops parent when the standard parent is not used.
- Whether the request is build/validate only or an explicitly approved Monday write.

**Output**

- Reviewed JSON spec under `mm_calendar/data/ops_tasks/`.
- Dry-run showing names, visible UTC windows, descriptions, statuses, and warnings.
- Validation result.
- For approved writes: created/updated IDs plus direct verification of visible clocks, blank Operation Status, and exact MM relations.

**Block**

- Missing day parent unless creation is explicitly approved.
- Unsupported execution values unless intentionally published with the correct blocker status.
- Replace/delete/archive without exact approval.
