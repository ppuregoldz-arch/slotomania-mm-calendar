#!/usr/bin/env python3
"""משוך את כל פריטי יוני 2026 מהבורד ובנה קונטקסט יומי (סייל/אירוע/MGAP/Gems/סופ"ש + מכניקות Core)
לצורך ניתוח קורלציה מול wager. פלט: mm_calendar/data/june_context_2026.tsv
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monday_client import gql  # noqa: E402

BOARD = 18388590642
MONTH = "2026-06"
COLS = ["status", "date_mky27nx7"]

Q_FIRST = """
query ($board: [ID!], $cols: [String!]) {
  boards(ids: $board) {
    items_page(limit: 200) { cursor items { name column_values(ids: $cols) { id text } } }
  }
}
"""
Q_NEXT = """
query ($cursor: String!, $cols: [String!]) {
  next_items_page(cursor: $cursor, limit: 200) { cursor items { name column_values(ids: $cols) { id text } } }
}
"""


def cv(item, cid):
    for c in item["column_values"]:
        if c["id"] == cid:
            return c.get("text") or ""
    return ""


def core_mech(name: str) -> str | None:
    n = name.lower()
    if "cancel" in n:
        return None
    if "spin zone" in n:
        return "Spin Zone"
    if "win master" in n:
        return "Win Master"
    if "pyp" in n or "pick your path" in n:
        return "PYP"
    if "loot" in n:
        return "Ace/Card Loot"
    if "spinner clash" in n:
        return "Spinner Clash"
    if "custom pod" in n:
        return "Custom Pod"
    if "jackpot" in n:
        return "Jackpots MES"
    if "mega winner" in n:
        return "Mega Winner"
    if "dash" in n and ("complete" in n or "finish" in n or "super dash" in n):
        return "Dash Challenge"
    if "m.e.s" in n or "mes" in n or "wild supreme" in n:
        return "MES themed/cards"
    return None


def main():
    data = gql(Q_FIRST, {"board": [BOARD], "cols": COLS})
    page = data["boards"][0]["items_page"]
    items = list(page["items"])
    cursor = page["cursor"]
    while cursor:
        d = gql(Q_NEXT, {"cursor": cursor, "cols": COLS})
        page = d["next_items_page"]
        items.extend(page["items"])
        cursor = page["cursor"]
    print(f"נשלפו {len(items)} פריטים")

    # פרומואי קוינס בלבד (הדשבורד = wager בקוינס). ג'מס לא רלוונטי.
    COIN_FLAGS = ["coin_sale", "mgap", "rolling", "buy_all", "ryd", "decoy",
                  "prize_mania", "extreme_stamp", "custom_pod", "counter_po", "dd"]
    days: dict[str, dict] = {}
    for it in items:
        date = cv(it, "date_mky27nx7")
        if not date.startswith(MONTH):
            continue
        product = cv(it, "status").strip()
        name = it["name"]
        n = name.lower()
        rec = days.setdefault(date, {f: 0 for f in COIN_FLAGS} | {"event": 0, "weekend": 0, "cores": set(), "n_items": 0})
        rec["n_items"] += 1
        if product == "Offers & coin sale" or "coin sale" in n:
            rec["coin_sale"] = 1
        if product == "MGAP" or "mgap" in n:
            rec["mgap"] = 1
        if product == "Rolling offer" or "rolling" in n:
            rec["rolling"] = 1
        if product == "Buy all" or "buy all" in n:
            rec["buy_all"] = 1
        if product == "RYD" or n.startswith("ryd"):
            rec["ryd"] = 1
        if "decoy" in n or "bonanza" in n:
            rec["decoy"] = 1
        if product == "Prize Mania" or "prize mania" in n:
            rec["prize_mania"] = 1
        if product == "Extreme stamp" or "extreme stamp" in n:
            rec["extreme_stamp"] = 1
        if "custom pod" in n:
            rec["custom_pod"] = 1
        if product == "Counter PO" or "counter po" in n:
            rec["counter_po"] = 1
        if product == "Daily deal" or n.startswith("dd"):
            rec["dd"] = 1
        if product == "Event" or any(k in n for k in ("4th of july", "world cup", "father", "woofing", "cinco", "red carpet")):
            rec["event"] = 1
        m = core_mech(name)
        if m and product == "Core":
            rec["cores"].add(m)

    out = Path(__file__).resolve().parents[1] / "mm_calendar" / "data" / "june_context_2026.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    hdr = ["date", "dow", "weekend"] + COIN_FLAGS + ["event", "n_items", "cores"]
    with out.open("w", encoding="utf-8") as f:
        f.write("\t".join(hdr) + "\n")
        for date in sorted(days):
            y, mo, d = map(int, date.split("-"))
            dow = dt.date(y, mo, d).strftime("%a")
            wknd = 1 if dow in ("Fri", "Sat", "Sun") else 0
            r = days[date]
            vals = [date, dow, str(wknd)] + [str(r[f]) for f in COIN_FLAGS] + [str(r["event"]), str(r["n_items"]), "|".join(sorted(r["cores"]))]
            f.write("\t".join(vals) + "\n")
    print(f"נשמר: {out}")
    for date in sorted(days):
        r = days[date]
        on = [f for f in COIN_FLAGS if r[f]]
        print(f"{date} coin_promos={on} cores={sorted(r['cores'])}")


if __name__ == "__main__":
    main()
