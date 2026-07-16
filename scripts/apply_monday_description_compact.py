#!/usr/bin/env python3
"""Push compact Monday descriptions for a date range (live board 18388590642)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from monday_description_compact import compact_monday_description  # noqa: E402
from upload_mm_calendar_day_monday import set_columns  # noqa: E402

EXTREME_DAYS = {4, 11, 18, 25}  # August 2026 Extreme Stamp days


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--from", dest="from_iso", required=True, help="YYYY-MM-DD")
    p.add_argument("--to", dest="to_iso", required=True, help="YYYY-MM-DD")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d.isoformat()
        d += timedelta(days=1)


def main() -> None:
    args = parse_args()
    start = date.fromisoformat(args.from_iso)
    end = date.fromisoformat(args.to_iso)
    snap_path = REPO / "mm_calendar/data/monday_board_live_by_date.json"
    root = json.loads(snap_path.read_text())
    by_date = root["by_date"]

    updated = 0
    skipped = 0
    for iso in daterange(start, end):
        day_num = int(iso.split("-")[2])
        on_extreme = day_num in EXTREME_DAYS
        for it in by_date.get(iso, []):
            if it.get("product") == "Day":
                continue
            item_id = it["id"]
            name = it.get("name") or ""
            product = it.get("product") or ""
            pricing = it.get("pricing") or None
            old = (it.get("description") or "").strip()
            new = compact_monday_description(
                name=name,
                product=product,
                pricing=pricing,
                description=old,
                on_extreme=on_extreme,
            ).strip()
            if new == old:
                skipped += 1
                continue
            if args.dry_run:
                print(f"[dry-run] {iso} {item_id} {name[:50]}")
                print(f"  OLD ({len(old)}): {old[:100]}…" if len(old) > 100 else f"  OLD: {old}")
                print(f"  NEW ({len(new)}): {new[:100]}…" if len(new) > 100 else f"  NEW: {new}")
                updated += 1
                continue
            set_columns(item_id, {"long_text_mkxzgg1v": {"text": new}})
            print(f"updated {iso} {item_id} {name[:55]}")
            updated += 1

    print(f"done: {updated} changed, {skipped} unchanged")


if __name__ == "__main__":
    main()
