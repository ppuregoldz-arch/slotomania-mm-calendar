#!/usr/bin/env python3
"""Restore Monday board columns on Aug 1–4 to pre–bulk-sync state using board activity_logs.

Uses the *first* sync-user change per (item, column)'s previous_value (API user 70910725).
Does not recreate deleted items (too risky for intentional dedupes). Column revert only.

Usage:
  python3 scripts/restore_monday_pre_sync.py --dry-run
  python3 scripts/restore_monday_pre_sync.py --apply
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from monday_client import gql  # noqa: E402

BOARD_ID = 18388590642
SYNC_USER = "70910725"
DAY_PREFIXES = tuple(f"2026-08-0{d} |" for d in range(1, 5))
SKIP_NAME_SUBSTR = (
    "dash pass - dash day",
    "winovate + mega pods",
)


def fetch_activity_logs(max_pages: int = 20) -> list[dict]:
    events: list[dict] = []
    for page in range(1, max_pages + 1):
        q = """
        query ($p: Int!) {
          boards(ids: [18388590642]) {
            activity_logs(limit: 500, page: $p) { event data user_id created_at }
          }
        }
        """
        logs = gql(q, {"p": page})["boards"][0]["activity_logs"]
        if not logs:
            break
        events.extend(logs)
        if len(logs) < 500:
            break
    return events


def parse_data(raw: str | dict) -> dict:
    return json.loads(raw) if isinstance(raw, str) else raw


def log_value_to_column_json(column_id: str, column_type: str, blob: dict | None) -> dict | None:
    if blob is None:
        return None
    if column_type == "long-text" or column_id == "long_text_mkxzgg1v":
        return {"text": blob.get("text") or ""}
    if column_type == "color":
        label = blob.get("label")
        if isinstance(label, dict):
            text = label.get("text")
        else:
            text = label
        if not text:
            return None
        return {"label": text}
    if column_type == "date" or column_id == "date_mky27nx7":
        d = blob.get("date") or blob.get("text")
        if d:
            return {"date": str(d)[:10]}
    if column_type == "timerange" or column_id.startswith("timerange"):
        fr, to = blob.get("from"), blob.get("to")
        if fr and to:
            return {"from": fr, "to": to}
    if column_type == "multiple-person" or column_id == "multiple_person_mky0jahx":
        ids = blob.get("personsAndTeams") or blob.get("ids_and_teams")
        if ids:
            return {"personsAndTeams": ids}
    return None


def build_revert_map(events: list[dict]) -> dict[tuple[int, str], dict]:
    """(pulse_id, column_id) -> API column value to restore."""
    sync_updates: list[dict] = []
    for e in events:
        if e["user_id"] != SYNC_USER or e["event"] != "update_column_value":
            continue
        d = parse_data(e["data"])
        name = d.get("pulse_name") or ""
        if not any(name.startswith(p) for p in DAY_PREFIXES):
            continue
        if any(s in name.lower() for s in SKIP_NAME_SUBSTR):
            continue
        if d.get("previous_value") is None:
            continue
        sync_updates.append((e["created_at"], d))

    sync_updates.sort(key=lambda x: x[0])
    revert: dict[tuple[int, str], dict] = {}
    meta: dict[tuple[int, str], tuple[str, str]] = {}
    for _ts, d in sync_updates:
        key = (int(d["pulse_id"]), d["column_id"])
        if key in revert:
            continue
        val = log_value_to_column_json(d["column_id"], d.get("column_type") or "", d["previous_value"])
        if val is None:
            continue
        revert[key] = val
        meta[key] = (d.get("pulse_name") or "", d.get("column_title") or d["column_id"])
    return revert, meta


def item_exists(item_id: str) -> bool:
    q = "query ($ids: [ID!]) { items(ids: $ids) { id } }"
    try:
        items = gql(q, {"ids": [str(item_id)]})["items"]
        return bool(items)
    except Exception:
        return False


def apply_revert(revert: dict[tuple[int, str], dict], meta: dict, *, dry_run: bool) -> None:
    q = """
    mutation ($board: ID!, $item: ID!, $vals: JSON!) {
      change_multiple_column_values(board_id: $board, item_id: $item, column_values: $vals) { id }
    }
    """
    by_item: dict[int, dict[str, dict]] = {}
    for (pid, col), val in revert.items():
        by_item.setdefault(pid, {})[col] = val

    applied = skipped = 0
    for pid, cols in sorted(by_item.items()):
        if not item_exists(str(pid)):
            skipped += 1
            print(f"SKIP missing item {pid}", flush=True)
            continue
        names = {meta.get((pid, c), ("", c))[0] for c in cols}
        label = next(iter(names)) if names else str(pid)
        if dry_run:
            print(f"DRY {pid} | {label[:60]} | cols: {list(cols.keys())}", flush=True)
            applied += 1
            continue
        try:
            gql(q, {"board": str(BOARD_ID), "item": str(pid), "vals": json.dumps(cols)})
        except RuntimeError as err:
            if "inactive" in str(err).lower():
                skipped += 1
                print(f"SKIP inactive {pid} | {label[:60]}", flush=True)
                continue
            raise
        print(f"OK {pid} | {label[:60]}", flush=True)
        applied += 1
        time.sleep(0.12)
    print(f"{'Would apply' if dry_run else 'Applied'} {applied} items; skipped missing {skipped}.", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write to Monday (default: dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="Print only")
    args = ap.parse_args()
    dry_run = not args.apply
    if args.dry_run:
        dry_run = True

    print("Fetching activity logs...", flush=True)
    events = fetch_activity_logs()
    revert, meta = build_revert_map(events)
    print(f"Revert targets: {len(revert)} column cells on Aug 1–4 (pre-sync previous_value).", flush=True)
    apply_revert(revert, meta, dry_run=dry_run)


if __name__ == "__main__":
    main()
