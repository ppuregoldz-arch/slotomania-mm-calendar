# Local backup (Itay)

This folder is your **personal backup** of the team workspace.

| Role | Path |
|------|------|
| **Team canonical** | `/Volumes/studios/Slotomania/CRM2/MM Calendar/Cursor Work` |
| **Your local backup** | `/Users/itayg/Desktop/Cursor Work` |
| **OneDrive mirror** | `~/Library/CloudStorage/OneDrive-PlaytikaLtd/Documents/Cursor Work MM` |

## How to use

- **You** can keep working in **Desktop `Cursor Work`** anytime; treat it as a full copy, not a throwaway clone.
- **Teammates** should open the **studios** path (see `AGENTS.md`).
- After big team changes on studios, refresh your backup:

```bash
rsync -a --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
  "/Volumes/studios/Slotomania/CRM2/MM Calendar/Cursor Work/" \
  "/Users/itayg/Desktop/Cursor Work/"
```

- After **your** local work you want on the share, push the other way:

```bash
rsync -a --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
  "/Users/itayg/Desktop/Cursor Work/" \
  "/Volumes/studios/Slotomania/CRM2/MM Calendar/Cursor Work/"
```

Then append **`TEAM_WORKLOG.md`** so the team sees what changed.

**Do not** rely on only OneDrive for the full repo unless you sync the complete tree; the studio volume is the live team copy.

**Last synced:** 2026-07-16 (Desktop → studio / CRM share)
