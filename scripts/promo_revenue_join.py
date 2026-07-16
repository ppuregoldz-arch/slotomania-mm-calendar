#!/usr/bin/env python3
"""Join daily Revenue-By-Product CSV with Monday calendar promos by date,
classify promos into types per lane, and rank types by average daily revenue.

Inputs:
  - Revenue By Product.csv (UTF-16), daily revenue per feature/product.
  - /tmp/board_items.json (cached Monday board items; see scripts comment).

Output: prints per-lane ranking of promo types by avg daily revenue.
Attribution is correlational (a day's feature revenue is attributed to the
promo type(s) live that day in that lane); "solo" days = only one type live.
"""
from __future__ import annotations
import csv, io, json, re
from collections import defaultdict
from datetime import date, timedelta

CSV_PATH = "/Users/itayg/Downloads/Revenue By Product.csv"
BOARD_CACHE = "/tmp/board_items.json"

# CSV product -> board lane (Product label)
PRODUCT_TO_LANE = {
    "MGAPP": "MGAP",
    "Reveal Your Deal": "RYD",
    "Rolling Offer": "Rolling offer",
    "Buy All": "Buy all",
    "Gems": "Gems",
    "Sticky Bundle PP": "Daily deal",
    "Clan Dash Bundle": "Clan-Dash",
    "Prize Mania": "Prize Mania",
}

# Per-lane promo-type classifiers: ordered (label, regex). First match wins.
CLASSIFIERS = {
    "MGAP": [
        ("Bigger Multipliers", r"bigger multiplier"),
        ("Wild Symbols", r"wild symbol"),
        ("BOGO", r"bogo"),
        ("Matched", r"match"),
        ("Night Plan", r"night plan"),
    ],
    "RYD": [
        ("Wild Gold", r"wild gold"),
        ("200%+ SB", r"200%|250%|300%"),
        ("150-155% SB", r"15[05]%"),
        ("100% SB", r"100% ?sb|100%"),
        ("Globez/coins", r"globez|coins"),
        ("Night Plan", r"night plan"),
    ],
    "Rolling offer": [
        ("Buy More for Less", r"buy more for less|more for less"),
        ("Supersized", r"supersize"),
        ("With bar / cycles", r"bar|cycle|denom"),
        ("Less is more", r"less is more"),
    ],
    "Buy all": [
        ("Decoy Bonanza", r"decoy"),
        ("Bonanza", r"bonanza"),
        ("Wild", r"wild"),
        ("Coins", r"coin"),
    ],
    "Gems": [
        ("Boosted Gemback", r"gemback"),
        ("GGS", r"ggs"),
        ("Gem Machine", r"gem machine|machine"),
        ("Gems Sale", r"sale|%"),
    ],
    "Daily deal": [
        ("Wild Supreme", r"wild supreme"),
        ("Wild Gold", r"wild gold"),
        ("Wild Any", r"wild any"),
        ("Wild Ordinary", r"wild ordinary"),
        ("Hammers", r"hammer"),
        ("SB Wheel", r"sb wheel|100% ?sb"),
        ("Parasheep/AS", r"parasheep|parashee|\bas\b|air strike"),
        ("Superboom", r"superboom|super boom"),
        ("Clan Pack", r"clan pack"),
        ("Shiny", r"shiny"),
    ],
}


def load_csv_daily():
    raw = open(CSV_PATH, "rb").read()
    for enc in ("utf-16", "utf-16-le", "utf-8-sig"):
        try:
            txt = raw.decode(enc); break
        except Exception:
            continue
    rows = list(csv.reader(io.StringIO(txt), delimiter="\t"))
    header = rows[3]  # row with M/D/YYYY dates, starting col index 2
    dates = []
    for cell in header[2:]:
        cell = cell.strip()
        m = re.match(r"(\d+)/(\d+)/(\d+)", cell)
        dates.append(date(int(m.group(3)), int(m.group(1)), int(m.group(2))).isoformat() if m else None)
    prod_daily = {}
    for r in rows[4:]:
        if len(r) < 3:
            continue
        name = (r[1] or r[0]).strip()
        if not name or name.lower() in ("total", "product"):
            continue
        dd = {}
        for i, cell in enumerate(r[2:]):
            if i >= len(dates) or not dates[i]:
                continue
            cell = cell.replace(",", "").strip()
            if cell:
                try:
                    dd[dates[i]] = float(cell)
                except ValueError:
                    pass
        if dd:
            prod_daily[name] = dd
    return prod_daily


def board_days_by_lane():
    """Return lane -> {iso_day: [promo_name,...]} expanding timelines to days."""
    items = json.load(open(BOARD_CACHE))
    lane_days = defaultdict(lambda: defaultdict(list))
    for it in items:
        lane = it["lane"]
        if not lane:
            continue
        days = []
        tl = it["timeline"]
        dt = it["date"]
        m = re.findall(r"\d{4}-\d{2}-\d{2}", tl)
        if len(m) == 2:
            a = date.fromisoformat(m[0]); b = date.fromisoformat(m[1])
            cur = a
            while cur <= b:
                days.append(cur.isoformat()); cur += timedelta(days=1)
        elif re.match(r"\d{4}-\d{2}-\d{2}", dt):
            days.append(dt[:10])
        for d in days:
            lane_days[lane][d].append(it["name"])
    return lane_days


def classify(lane, name):
    name_l = name.lower()
    for label, rgx in CLASSIFIERS.get(lane, []):
        if re.search(rgx, name_l):
            return label
    return "(other)"


def main():
    prod_daily = load_csv_daily()
    lane_days = board_days_by_lane()
    for product, lane in PRODUCT_TO_LANE.items():
        if product not in prod_daily or lane not in CLASSIFIERS:
            continue
        daily = prod_daily[product]
        # Build per-type revenue lists (solo = only one classified type that day)
        type_rev_all = defaultdict(list)
        type_rev_solo = defaultdict(list)
        for day, rev in daily.items():
            names = lane_days.get(lane, {}).get(day, [])
            types = set(classify(lane, n) for n in names if "cancel" not in n.lower())
            types.discard("(other)")
            for t in types:
                type_rev_all[t].append(rev)
            if len(types) == 1:
                type_rev_solo[list(types)[0]].append(rev)
        print(f"\n=== {lane}  (CSV product: {product}) ===")
        print(f"{'promo type':22s} {'solo days':>9s} {'avg(solo)':>11s} {'all days':>8s} {'avg(all)':>11s}")
        rows = []
        for t in set(list(type_rev_all) + list(type_rev_solo)):
            solo = type_rev_solo.get(t, [])
            alld = type_rev_all.get(t, [])
            avg_solo = sum(solo) / len(solo) if solo else 0
            avg_all = sum(alld) / len(alld) if alld else 0
            rows.append((avg_solo or avg_all, t, len(solo), avg_solo, len(alld), avg_all))
        for _, t, ns, asolo, na, aall in sorted(rows, reverse=True):
            print(f"{t:22s} {ns:9d} {asolo:11,.0f} {na:8d} {aall:11,.0f}")


if __name__ == "__main__":
    main()
