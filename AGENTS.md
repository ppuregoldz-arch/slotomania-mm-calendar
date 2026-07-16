# Cursor agents — MM Calendar / Slotomania monetization

**Canonical workspace (team):**  
`/Volumes/studios/Slotomania/CRM2/MM Calendar/Cursor Work`

Open this folder in **Cursor → File → Open Folder** (not a single file). Agents read rules from `.cursor/rules/` automatically when relevant.

---

## What this repo is

1. **MM Calendar (`mm_calendar/`)** — Knowledge base + **August 2026** draft calendar for Slotomania monetization (Monday board “MM calendar”, lanes, caps, offer construction).
2. **Builders (`scripts/`)** — Python pipelines: generate plan JSON, validate, dashboard HTML, optional Monday sync, revenue calibration.
3. **SM data assistant** — Optional Vertica/DWH analysis via MCP (see `.cursor/mcp.json`); separate from calendar building unless the task asks for data pulls.

**Start reading for calendar work:** `mm_calendar/00_GUIDELINES_ITAY.md` → `mm_calendar/BUILD_CALENDAR_ROUTER.md` → `mm_calendar/topics/README.md` (pick domain) → target `mm_calendar/monthly_guidelines/YYYY-MM.md` → `mm_calendar/rules_cheatsheet.md` → `mm_calendar/PRIZE_PRIORITY_AND_MONTH_BUILD.md`.

For measurement/performance/prediction work, route through `mm_calendar/measurement/`, `mm_calendar/performance/`, and `mm_calendar/prediction/`. Raw sources are immutable; low-confidence evidence is not a confirmed learning.

**Builder rule (encoding):** `.cursor/rules/mm_calendar_builder.mdc`

---

## August 2026 — source of truth

| Artifact | Path |
|----------|------|
| Plan JSON | `mm_calendar/data/august_2026_plan.json` |
| Human calendar | `mm_calendar/examples/2026-08_calendar.md` |
| Dashboard (local) | `mm_calendar/public/index.html` |
| Standalone HTML | `MM_Calendar_Dashboard.html` (repo root, if present) |
| Main builder | `scripts/build_august_2026_plan.py` |

After **any** plan change, run validation before you consider the task done.

---

## Standard commands (from repo root)

```bash
cd "/Volumes/studios/Slotomania/CRM2/MM Calendar/Cursor Work"

# Regenerate August plan + markdown
python3 scripts/build_august_2026_plan.py

# Audit (daily / weekly / monthly checks)
python3 scripts/audit_august_2026_plan.py

# Refresh revenue lifts used for tie-breaks (optional, needs DWH/MCP data)
python3 scripts/calibrate_model.py
python3 scripts/build_august_2026_plan.py   # again after calibrate

# Dashboard + OneDrive standalone HTML (if configured on your machine)
python3 scripts/build_calendar_html.py

# Push to Monday (only when explicitly requested; needs credentials)
python3 scripts/upload_mm_calendar_day_monday.py --all
python3 scripts/upload_mm_calendar_day_monday.py --day 17
```

`build_august_2026_plan.py` must exit **0**. If validation fails, fix the builder or the plan logic — do not hand-edit JSON to “paper over” failures unless the user explicitly asks for a one-off exception documented in the worklog.

---

## Product rules agents must respect (August builder)

- **Rolling — Buy More for Less (BMFL):** MFL anchor days only; **3 cycles**, **High** pricing only.
- **Rolling — Buy X Get Y:** Other rolling slots; pricing from `assign_offer_pricing` (M/H/Max); cycle variants (1/2/5/6).
- **RDS / GGS per cycle:** max **4 RDS** (1 + 3 on stamp steps), max **2 GGS** (1 + 1); validated in `validate_rolling_item_stamps`.
- **Every day:** at least one **VFM second offer** (RYD / Rolling / Buy All / Decoy / Prize Mania). **Clan-Dash / Dash Pass do not count.** Mondays get a light second offer (RYD or Buy All), except MFL Mondays where Rolling is the VFM offer.
- **DD pricing ≠ second-offer pricing** on the same day (when both are priced).
- **Monday upload mapping:** `scripts/upload_mm_calendar_day_monday.py` — only rows that appear in `build_rows()` matter for the board; test with a single day before `--all`.
- **Lotto peak + LBP:** upload leaves **Config Status empty** (no LiveOps config task; promo is the row name + rotation per `lotto_bonus.md`).
- **LBP timing:** **00:00 UTC → 11:00 UTC (Promo Time)** on the calendar day — not 2h post 12:00 UTC (see `promo_duration_note` in builder).

Season SKU alignment: `scripts/validate_season_skus.py` (imported from the August builder validation).

---

## MCP & secrets

- MCP config: `.cursor/mcp.json`
- Monday / API env: `.cursor/monday.env` (local; **never commit** tokens; do not paste secrets into chat or worklog).
- If MCP DB is unavailable, say so in the worklog and use existing JSON snapshots under `mm_calendar/data/`.

---

## Mandatory handoff — `TEAM_WORKLOG.md`

**After every agent session that changes files or runbooks**, append an entry to:

**`TEAM_WORKLOG.md`** (repo root)

Use this template:

```markdown
### YYYY-MM-DD — <your name> — <short title>
- **Goal:** …
- **Done:** …
- **Files:** …
- **Commands run:** `build_august_2026_plan.py` ✓/✗, `audit_…` ✓/✗, Monday sync ✓/✗/n/a
- **Notes for next agent:** …
```

Do not delete others’ entries. Newest at the **top** of the file.

---

## What not to do

- Do not force-push or change git config unless the user asks.
- Do not run full Monday `--all` or wide `--from/--to` sync without explicit approval **and** a defined day list. Sync **overwrites** matched rows and **deletes** orphans — it will undo manual Monday edits. Default: builder + JSON only.
- Do not treat SM coin amounts in trillions+ as data errors (hyperinflation is normal in SM DWH rules).
- Do not edit files under `.cursor/plans/` unless assigned.

---

## Alternate access

- **OneDrive:** `Documents/Cursor Work MM` (sync copy; studio path above is preferred for the team).
- **Share link:** use the folder your lead shared in Teams/SharePoint; map to the same tree as the studio volume when mounted.

---

## Questions

Calendar semantics → `mm_calendar/learnings.md`, `mm_calendar/lanes.md`, `mm_calendar/offer_construction.md`.  
Monday column contract → `mm_calendar/board_schema.md`.
