#!/usr/bin/env python3
"""Local backup of full August 2026 from live MM Calendar (Monday board 18388590642)."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SNAP = REPO / "mm_calendar" / "data" / "monday_board_live_snapshot.json"
INDEX = REPO / "mm_calendar" / "data" / "monday_board_live_by_date.json"
YEAR, MONTH = 2026, 8
PREFIX = f"{YEAR}-{MONTH:02d}"


def august_dates() -> list[str]:
    return [f"{PREFIX}-{d:02d}" for d in range(1, 32)]


def backup_dir() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = REPO / "mm_calendar" / "backups" / f"august_{YEAR}"
    d = root / stamp
    d.mkdir(parents=True, exist_ok=True)
    latest = root / "latest"
    if latest.is_symlink() or latest.exists():
        if latest.is_symlink():
            latest.unlink()
        elif latest.is_dir():
            shutil.rmtree(latest)
    latest.symlink_to(d.name, target_is_directory=True)
    return d


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_calendar_md(by_date: dict, out: Path) -> None:
    lines = [
        f"# MM Calendar — August {YEAR} (Monday backup)",
        "",
        f"**Generated (UTC):** {datetime.now(timezone.utc).replace(microsecond=0).isoformat()}",
        "**Source:** Monday board `18388590642` — live snapshot.",
        "",
    ]
    for ds in august_dates():
        rows = by_date.get(ds, [])
        if not rows:
            lines.append(f"## {ds}\n\n_(no rows)_\n")
            continue
        lines.append(f"## {ds}\n")
        for r in sorted(rows, key=lambda x: (x.get("product") or "", x.get("name") or "")):
            if (r.get("product") or "") == "Day":
                continue
            pr = r.get("pricing") or ""
            prs = f" · **{pr}**" if pr else ""
            cfg = r.get("config_status") or ""
            cfgs = f" · _{cfg}_" if cfg else ""
            lines.append(f"- **{r.get('product', '?')}** — {r.get('name', '')}{prs}{cfgs}")
            desc = (r.get("description") or "").strip()
            if desc:
                first = desc.split("\n")[0][:200]
                lines.append(f"  - {first}")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SNAP.is_file() or not INDEX.is_file():
        raise SystemExit("Run pull_monday_live_snapshot.py first.")

    snap = load_json(SNAP)
    idx = load_json(INDEX)
    by_date = idx.get("by_date") or {}

    out = backup_dir()
    dates = august_dates()
    aug_by_date = {d: by_date.get(d, []) for d in dates}
    aug_items = [it for it in snap.get("items", []) if (it.get("date") or "").startswith(PREFIX)]

    meta = {
        "backup_type": "august_mm_calendar_monday",
        "month": f"{YEAR}-{MONTH:02d}",
        "board_id": snap.get("meta", {}).get("board_id") or "18388590642",
        "pulled_at_utc": snap.get("meta", {}).get("pulled_at_utc"),
        "backup_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "days_with_rows": sum(1 for d in dates if aug_by_date.get(d)),
        "promo_rows": sum(
            len([r for r in aug_by_date.get(d, []) if r.get("product") != "Day"]) for d in dates
        ),
        "full_item_rows": len(aug_items),
    }

    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "monday_august_by_date.json").write_text(
        json.dumps({"meta": meta, "by_date": aug_by_date}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "monday_august_items_full.json").write_text(
        json.dumps({"meta": meta, "items": aug_items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_calendar_md(aug_by_date, out / "august_2026_from_monday.md")

    copies = [
        REPO / "mm_calendar" / "data" / "august_2026_plan.json",
        REPO / "mm_calendar" / "examples" / "2026-08_calendar.md",
        REPO / "mm_calendar" / "monthly_guidelines" / "2026-08.md",
    ]
    for src in copies:
        if src.is_file():
            shutil.copy2(src, out / src.name)

    readme = out / "README.md"
    readme.write_text(
        f"""# August {YEAR} — local MM Calendar backup

- **Monday (authority for scheduled rows):** `monday_august_by_date.json`, `monday_august_items_full.json`
- **Human read:** `august_2026_from_monday.md`
- **Reference (builder / not always = board):** `august_2026_plan.json`, `2026-08_calendar.md`
- **Economy guidelines:** `2026-08.md`

**Latest symlink:** `mm_calendar/backups/august_{YEAR}/latest` → this folder.

Re-run:
```bash
python3 scripts/pull_monday_live_snapshot.py
python3 scripts/backup_august_mm_calendar_local.py
```
""",
        encoding="utf-8",
    )
    print(f"Backup → {out}")
    print(f"  days: {meta['days_with_rows']}/31, promos: {meta['promo_rows']}, items: {meta['full_item_rows']}")
    print(f"  latest → mm_calendar/backups/august_{YEAR}/latest")


if __name__ == "__main__":
    main()
