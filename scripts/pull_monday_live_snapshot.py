#!/usr/bin/env python3
"""Read-only full pull of MM calendar Monday board → monday_board_live_snapshot.json."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from monday_client import gql  # noqa: E402

BOARD_ID = 18388590642
OUT = REPO / "mm_calendar" / "data" / "monday_board_live_snapshot.json"
INDEX_OUT = REPO / "mm_calendar" / "data" / "monday_board_live_by_date.json"

COLS = [
    "status",
    "date_mky27nx7",
    "timerange_mkz3t5qy",
    "long_text_mkxzgg1v",
    "color_mky9aesm",
    "color_mky0czxd",
    "color_mkztqb24",
    "color_mm4kygty",
    "person",
    "multiple_person_mky0jahx",
    "color_mky2sdgt",
]

AUTHORITY = (
    "Itay 2026-07-12 — live Monday board is the updated schedule truth for agents; "
    "read-only snapshot; prefer this over august_2026_plan.json for what is scheduled on the board. "
    "Days 2026-08-01 … 2026-08-15 are committed — do not change via builder/upload without explicit approval."
)


def col_map(column_values: list) -> dict[str, str]:
    return {c["id"]: c.get("text") or "" for c in column_values}


def pull_all() -> list[dict]:
    items_raw: list = []
    cursor = None
    while True:
        q = """
        query ($board: [ID!], $cols: [String!], $cursor: String) {
          boards(ids: $board) {
            items_page(limit: 500, cursor: $cursor) {
              cursor
              items {
                id
                name
                group { id }
                column_values(ids: $cols) { id text }
              }
            }
          }
        }
        """
        page = gql(q, {"board": [BOARD_ID], "cols": COLS, "cursor": cursor})["boards"][0][
            "items_page"
        ]
        items_raw.extend(page["items"])
        cursor = page.get("cursor")
        if not cursor:
            break
    normalized = []
    for it in items_raw:
        c = col_map(it["column_values"])
        dt = (c.get("date_mky27nx7") or "").strip()
        iso = dt[:10] if len(dt) >= 10 else ""
        normalized.append(
            {
                "id": it["id"],
                "name": it["name"],
                "group_id": (it.get("group") or {}).get("id") or "",
                "product": c.get("status") or "",
                "date": iso,
                "timeline": c.get("timerange_mkz3t5qy") or "",
                "description": c.get("long_text_mkxzgg1v") or "",
                "pricing": c.get("color_mky9aesm") or "",
                "economy_status": c.get("color_mky0czxd") or "",
                "config_status": c.get("color_mkztqb24") or "",
                "creative_label": c.get("color_mm4kygty") or "",
                "mm_owner": c.get("person") or "",
                "economist": c.get("multiple_person_mky0jahx") or "",
                "ops_status": c.get("color_mky2sdgt") or "",
            }
        )
    normalized.sort(key=lambda x: (x["date"] or "9999", x["product"], x["name"].lower()))
    return normalized


def main() -> None:
    items = pull_all()
    pulled_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    meta = {
        "authority": AUTHORITY,
        "board_id": str(BOARD_ID),
        "board_url": f"https://playtika.monday.com/boards/{BOARD_ID}",
        "pulled_at_utc": pulled_at,
        "read_only": True,
        "item_count": len(items),
        "dated_items": sum(1 for r in items if r["date"]),
        "undated_items": sum(1 for r in items if not r["date"]),
        "august_2026_dated": sum(1 for r in items if r["date"].startswith("2026-08")),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"meta": meta, "items": items}, ensure_ascii=False, indent=2), encoding="utf-8")

    by_date: dict[str, list] = {}
    for row in items:
        key = row["date"] if row["date"] else "_no_date"
        by_date.setdefault(key, []).append(
            {
                "id": row["id"],
                "name": row["name"],
                "product": row["product"],
                "pricing": row["pricing"],
                "config_status": row["config_status"],
                "description": row["description"],
            }
        )
    INDEX_OUT.write_text(
        json.dumps(
            {
                "meta": {k: v for k, v in meta.items() if k != "authority"},
                "authority_note": meta["authority"],
                "by_date": by_date,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {len(items)} items → {OUT}")


if __name__ == "__main__":
    main()
