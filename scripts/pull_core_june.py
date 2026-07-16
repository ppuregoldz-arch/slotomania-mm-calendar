#!/usr/bin/env python3
"""שלוף פריטי Core מיוני 2026 מבורד ה-MM calendar (הצלבה לניתוח wager)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monday_client import gql  # noqa: E402

BOARD = 18388590642
MONTH = "2026-06"
COLS = ["status", "date_mky27nx7", "long_text_mkxzgg1v"]

Q_FIRST = """
query ($board: [ID!], $cols: [String!]) {
  boards(ids: $board) {
    items_page(limit: 200) {
      cursor
      items { name column_values(ids: $cols) { id text } }
    }
  }
}
"""

Q_NEXT = """
query ($cursor: String!, $cols: [String!]) {
  next_items_page(cursor: $cursor, limit: 200) {
    cursor
    items { name column_values(ids: $cols) { id text } }
  }
}
"""


def cv(item, cid):
    for c in item["column_values"]:
        if c["id"] == cid:
            return c.get("text") or ""
    return ""


def main():
    data = gql(Q_FIRST, {"board": [BOARD], "cols": COLS})
    page = data["boards"][0]["items_page"]
    items = list(page["items"])
    cursor = page["cursor"]
    pages = 1
    while cursor:
        d = gql(Q_NEXT, {"cursor": cursor, "cols": COLS})
        page = d["next_items_page"]
        items.extend(page["items"])
        cursor = page["cursor"]
        pages += 1
    print(f"נשלפו {len(items)} פריטים ב-{pages} דפים\n")

    core = []
    for it in items:
        product = cv(it, "status")
        date = cv(it, "date_mky27nx7")
        if product.strip().lower() == "core" and date.startswith(MONTH):
            core.append((date, it["name"], cv(it, "long_text_mkxzgg1v")))

    core.sort()
    print(f"=== Core items ביוני 2026: {len(core)} ===")
    for date, name, desc in core:
        d = (desc or "").replace("\n", " ")[:110]
        print(f"{date}  {name}   | {d}")

    out = Path(__file__).resolve().parents[1] / "mm_calendar" / "data" / "core_june_2026.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write("date\tname\tdesc\n")
        for date, name, desc in core:
            f.write(f"{date}\t{name}\t{(desc or '').replace(chr(9),' ').replace(chr(10),' ')}\n")
    print(f"\nנשמר cache: {out}")


if __name__ == "__main__":
    main()
