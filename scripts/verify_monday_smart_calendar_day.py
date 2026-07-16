#!/usr/bin/env python3
"""Compare Monday MM calendar promos for one day vs Smart Calendar (DWH starts-today view).

Usage:
  python3 scripts/verify_monday_smart_calendar_day.py 2026-08-01

Checks:
  - Every Monday promo (except Product=Day) has a matching SC row (fuzzy name match)
  - Monday Description text appears in SC promo_desc (comment), normalized whitespace
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from monday_client import gql  # noqa: E402
from refresh_dwh_snapshots import engine_from_config, rows  # noqa: E402

BOARD_ID = 18388590642


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def monday_promos(iso: str) -> list[dict]:
    cursor = None
    out: list[dict] = []
    while True:
        q = """
        query ($cursor: String) {
          boards(ids: [18388590642]) {
            items_page(limit: 500, cursor: $cursor) {
              cursor
              items {
                id name
                column_values(ids: ["date_mky27nx7", "status", "color_mkyfye85", "long_text_mkxzgg1v"]) {
                  id text
                }
              }
            }
          }
        }
        """
        page = gql(q, {"cursor": cursor})["boards"][0]["items_page"]
        for it in page["items"]:
            cols = {c["id"]: c.get("text") for c in it["column_values"]}
            if cols.get("date_mky27nx7") != iso:
                continue
            if cols.get("status") == "Day":
                continue
            short = it["name"]
            if "|" in short:
                short = short.split("|", 1)[1].strip()
            out.append(
                {
                    "id": it["id"],
                    "name": it["name"],
                    "short": short,
                    "add_sc": cols.get("color_mkyfye85") or "",
                    "desc": cols.get("long_text_mkxzgg1v") or "",
                }
            )
        cursor = page.get("cursor")
        if not cursor:
            break
    return sorted(out, key=lambda x: x["name"])


def smart_starts_today(iso: str) -> list[dict]:
    engine, text = engine_from_config()
    conn = engine.connect()
    try:
        q = """
        SELECT promo_name, promo_desc, status
        FROM (
          SELECT promo_name, promo_desc, status,
                 ROW_NUMBER() OVER (PARTITION BY promo_id ORDER BY update_ts DESC, insert_id DESC) rn
          FROM dwh.sm_fact_smart_calendar_promotion_updates
          WHERE start_date::date = :day
            AND status NOT ILIKE '%cancel%'
            AND promo_name NOT ILIKE '%cancel%'
            AND promo_name NOT ILIKE '%Operation - Daily View%'
        ) t
        WHERE rn = 1
        ORDER BY promo_name
        """
        return [dict(r) for r in rows(conn, text, q, {"day": iso})]
    finally:
        conn.close()


def match_monday_to_sc(monday: dict, sc_rows: list[dict]) -> dict | None:
    mnorm = norm(monday["short"])
    for sc in sc_rows:
        pn = norm(sc["promo_name"])
        if mnorm in pn or pn in mnorm:
            return sc
        # token overlap for DD / RYD style names
        mt = set(re.findall(r"[a-z0-9*]+", mnorm))
        pt = set(re.findall(r"[a-z0-9*]+", pn))
        if len(mt & pt) >= max(3, min(len(mt), len(pt)) // 2):
            return sc
    return None


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: verify_monday_smart_calendar_day.py YYYY-MM-DD")
    iso = sys.argv[1]
    mon = monday_promos(iso)
    sc = smart_starts_today(iso)

    print(f"=== {iso} — Monday promos: {len(mon)} | Smart Calendar (starts today): {len(sc)} ===\n")

    missing_add = [m for m in mon if m["add_sc"] != "Add"]
    if missing_add:
        print("Monday — missing Add to smart calendar:")
        for m in missing_add:
            print(f"  - {m['name']} (status={m['add_sc']!r})")
        print()

    unmatched = []
    comment_issues = []
    for m in mon:
        hit = match_monday_to_sc(m, sc)
        if not hit:
            unmatched.append(m)
            continue
        if m["desc"]:
            nd, np = norm(m["desc"]), norm(hit.get("promo_desc") or "")
            if nd not in np and np not in nd:
                # allow if first 40 chars of desc appear
                head = nd[: min(40, len(nd))]
                if head and head not in np:
                    comment_issues.append((m, hit))

    if unmatched:
        print("Not found in Smart Calendar (starts today):")
        for m in unmatched:
            print(f"  - {m['name']}")
        print()

    if comment_issues:
        print("Description not reflected in SC promo_desc (comment):")
        for m, hit in comment_issues:
            print(f"  - Monday: {m['name'][:70]}")
            print(f"    SC: {hit['promo_name']}")
            print(f"    desc preview: {m['desc'][:80]!r}")
            print(f"    promo_desc: {(hit.get('promo_desc') or '')[:80]!r}")
        print()

    if sc and not mon:
        print("Smart Calendar only (no Monday promos?):")
        for r in sc:
            print(f"  - {r['promo_name']}")

    if not missing_add and not unmatched and not comment_issues:
        print("OK — all Monday promos have Add; SC coverage and comments look aligned.")
    elif not missing_add and unmatched:
        print("Monday Add column is complete; Smart Calendar still missing rows (automation lag or not run yet).")

    sys.exit(1 if missing_add or unmatched or comment_issues else 0)


if __name__ == "__main__":
    main()
