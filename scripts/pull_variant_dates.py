#!/usr/bin/env python3
"""שולף לכל וריאנט אופר את תאריכי הריצה מהבורד + הקשר יומי (האם היה סייל / MGAP באותו יום).
פלט: mm_calendar/data/variant_dates.json  ={ variantKey: [ {d, sale, mgap}, ... ] }
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monday_client import gql  # noqa: E402

BOARD = 18388590642
MONTHS = ("2026-05", "2026-06", "2026-07")
COLS = ["status", "date_mky27nx7", "timerange_mkz3t5qy"]
OUT = Path(__file__).resolve().parents[1] / "mm_calendar" / "data" / "variant_dates.json"

Q_FIRST = 'query($b:[ID!],$c:[String!]){boards(ids:$b){items_page(limit:200){cursor items{name column_values(ids:$c){id text}}}}}'
Q_NEXT = 'query($cur:String!,$c:[String!]){next_items_page(cursor:$cur,limit:200){cursor items{name column_values(ids:$c){id text}}}}'


def cv(it, cid):
    for c in it["column_values"]:
        if c["id"] == cid:
            return c.get("text") or ""
    return ""


def variant_of(product: str, name: str):
    p = product.strip().lower()
    n = name.lower()
    if "cancel" in n:
        return None
    if p == "mgap":
        if "bigger" in n: return "MGAP Bigger Multipliers"
        if "wild symbol" in n: return "MGAP Wild Symbols"
        if "bogo" in n or "buy one" in n or "buy 1" in n: return "MGAP BOGO"
        if "match" in n: return "MGAP Matched"
        return "MGAP BOGO"
    if p == "daily deal":
        if "clan pack" in n: return "DD Clan Pack"
        if "wild supreme" in n: return "DD Wild Supreme"
        if "hammer" in n: return "DD Hammers"
        if "superboom" in n or "super boom" in n: return "DD Superboom"
        if "sb wheel" in n or "100% sb" in n: return "DD SB Wheel"
        if "wild any" in n: return "DD Wild Any"
        if "parasheep" in n or "air strike" in n or re.search(r"\bas\b", n): return "DD Parasheep"
        return None
    if p == "rolling offer":
        if "more for less" in n or "more-for-less" in n or "buy more" in n: return "Rolling Buy More for Less"
        if "supersize" in n: return "Rolling Supersized"
        return "Rolling Offer"
    if p == "buy all":
        if "decoy" in n or "bonanza" in n: return "Bonanza"
        if "wild" in n: return "Buy All Wild"
        if "coin" in n: return "Buy All Coins"
        return None
    if p == "ryd":
        if "wild gold" in n: return "RYD Wild Gold"
        if "100%" in n: return "RYD 100% SB"
        if "150%" in n or "155%" in n: return "RYD 150% SB"
        return None
    if p == "gems":
        if "gemback" in n: return "Boosted Gemback"
        if "ggs" in n or "gold gem" in n: return "x2 GGS"
        if "sale" in n or "%" in n: return "Gems Sale"
        return None
    return None


def days_of(item):
    tl = cv(item, "timerange_mkz3t5qy")
    dt = cv(item, "date_mky27nx7")
    m = re.findall(r"\d{4}-\d{2}-\d{2}", tl)
    if len(m) == 2:
        a, b = date.fromisoformat(m[0]), date.fromisoformat(m[1])
        out = []
        cur = a
        while cur <= b and (cur - a).days < 60:
            out.append(cur.isoformat()); cur += timedelta(days=1)
        return out
    if re.match(r"\d{4}-\d{2}-\d{2}", dt):
        return [dt[:10]]
    return []


def main():
    data = gql(Q_FIRST, {"b": [BOARD], "c": COLS})
    page = data["boards"][0]["items_page"]
    items = list(page["items"])
    cur = page["cursor"]
    while cur:
        d = gql(Q_NEXT, {"cur": cur, "c": COLS})
        page = d["next_items_page"]
        items.extend(page["items"])
        cur = page["cursor"]

    in_range = lambda d: any(d.startswith(m) for m in MONTHS)
    # per-day context
    day_sale, day_mgap = {}, {}
    for it in items:
        product = cv(it, "status").strip()
        n = it["name"].lower()
        for d in days_of(it):
            if not in_range(d):
                continue
            if product == "Offers & coin sale" or "coin sale" in n:
                day_sale[d] = True
            if product == "MGAP" and "cancel" not in n:
                t = "Bigger" if "bigger" in n else ("BOGO" if "bogo" in n else ("Matched" if "match" in n else ("Wild" if "wild" in n else "MGAP")))
                day_mgap[d] = t

    variant_dates = {}
    for it in items:
        product = cv(it, "status").strip()
        v = variant_of(product, it["name"])
        if not v:
            continue
        for d in days_of(it):
            if not in_range(d):
                continue
            variant_dates.setdefault(v, {})[d] = True

    out = {}
    for v, days in variant_dates.items():
        rows = []
        for d in sorted(days):
            rows.append({"d": d, "sale": bool(day_sale.get(d)), "mgap": day_mgap.get(d, "")})
        out[v] = rows

    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"נכתב: {OUT}  ({len(out)} variants)")
    for v, rows in sorted(out.items()):
        print(f"  {v}: {len(rows)} dates")


if __name__ == "__main__":
    main()
