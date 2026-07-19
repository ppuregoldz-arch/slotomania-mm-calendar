# Local backup (Itay)

This folder is your **personal backup** of the team workspace.

| Role | Path |
|------|------|
| **Team canonical** | `/Volumes/studios/Slotomania/CRM3/MM Calendar/Cursor Work` |
| **Your local backup** | `/Users/itayg/Desktop/Cursor Work` |
| **OneDrive mirror** | `~/Library/CloudStorage/OneDrive-PlaytikaLtd/Documents/Cursor Work MM` |

## How to use

- **You** can keep working in **Desktop `Cursor Work`** anytime; treat it as a full copy, not a throwaway clone.
- **Teammates** should open the **studios** path (see `AGENTS.md`).
- After big team changes on studios, refresh your backup:

```bash
rsync -a --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
  "/Volumes/studios/Slotomania/CRM3/MM Calendar/Cursor Work/" \
  "/Users/itayg/Desktop/Cursor Work/"
```

- After **your** local work you want on the share, push the other way:

```bash
rsync -a --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
  "/Users/itayg/Desktop/Cursor Work/" \
  "/Volumes/studios/Slotomania/CRM3/MM Calendar/Cursor Work/"
```

Then append **`TEAM_WORKLOG.md`** so the team sees what changed.

**Do not** rely on only OneDrive for the full repo unless you sync the complete tree; the studio volume is the live team copy.

**Last synced:** 2026-07-19 (Desktop → CRM3 studio share)

## August 2026 — MM Calendar month backup (Monday)

Full month from live board (read-only):

```bash
cd "/Users/itayg/Desktop/Cursor Work"
python3 scripts/pull_monday_live_snapshot.py
python3 scripts/backup_august_mm_calendar_local.py
```

Output:

| Path | Contents |
|------|----------|
| `mm_calendar/backups/august_2026/latest/` | Symlink to newest run |
| `monday_august_by_date.json` | All days 1–31 (Product, name, description, pricing) |
| `monday_august_items_full.json` | Full Monday columns per row |
| `august_2026_from_monday.md` | Human-readable month |
| `august_2026_plan.json`, `2026-08_calendar.md`, `2026-08.md` | Builder + examples + economy (reference) |

**Authority:** scheduled rows = Monday snapshot; plan JSON may differ on some days.
