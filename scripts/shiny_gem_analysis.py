#!/usr/bin/env python3
"""Rank Shiny Show promo variants by daily gem usage (the Shiny Show KPI).

Input: Shiny Experience.csv (tab-delimited). One day spans several sparse rows;
gem usage (last col) and promo_name appear on the day's rows.
"""
from __future__ import annotations
import csv, io, re
from collections import defaultdict

CSV_PATHS = [
    "/Users/itayg/Downloads/Shiny Experience.csv",
    "/Users/itayg/Downloads/Shiny Experience (1).csv",
]

# promo variant classifiers (first match wins)
VARIANTS = [
    ("Wild Guaranteed", r"wild guaranteed"),
    ("Joker - Different Prizes", r"joker.*different|different prizes.*joker"),
    ("All Cards - Joker", r"all cards.*joker|joker.*all cards"),
    ("Different Prizes", r"different prizes"),
    ("All Cards", r"all cards"),
    ("Crazy with Aces", r"crazy with aces"),
    ("Clan Pack Guaranteed", r"clan pack"),
    ("Land on 4 moles", r"4 mole"),
    ("Find the Flower/Betty", r"find the flower|find betty"),
    ("JP Symbol", r"jp symbol"),
    ("SnL dice", r"snl dice"),
    ("Growing Shiny Show", r"growing shiny"),
    ("For Every 2 Dashes", r"every 2 dashes"),
    ("Finish Sticker", r"finish shiny show sticker"),
    ("Play X (baseline)", r"^play x shiny show$|^play x shiny show,"),
]


def classify(promo: str) -> str:
    p = promo.lower().strip()
    if not p:
        return "(no promo / baseline day)"
    for label, rgx in VARIANTS:
        if re.search(rgx, p):
            return label
    return "(other)"


def _decode(path):
    raw = open(path, "rb").read()
    for enc in ("utf-16", "utf-16-le", "utf-8-sig", "utf-8"):
        try:
            cand = raw.decode(enc)
            if "\x00" not in cand:
                return cand
        except Exception:
            continue
    return raw.decode("utf-8", errors="replace").replace("\x00", "")


def main():
    # dedup days across files by (album_id, gem_value) since the same day
    # has a unique gem number even when date strings differ (EN vs HE).
    day_gem = {}   # (album, date) -> gem
    day_promo = {}  # (album, date) -> promo
    seen_gem = set()  # (album, gem) to dedup overlapping days across files
    promo_idx = 11
    for path in CSV_PATHS:
        rows = list(csv.reader(io.StringIO(_decode(path)), delimiter="\t"))
        header = rows[0]
        gem_idx = len(header) - 1
        for r in rows[1:]:
            if len(r) <= gem_idx:
                continue
            key = (r[0], r[2])
            g = r[gem_idx].replace(",", "").strip()
            if g and re.fullmatch(r"\d+", g):
                dedup = (r[0], int(g))
                if dedup in seen_gem:
                    key = None
                else:
                    seen_gem.add(dedup)
                    day_gem.setdefault(key, int(g))
            if key and len(r) > promo_idx and r[promo_idx].strip():
                day_promo.setdefault(key, r[promo_idx].strip())

    # aggregate by variant
    var_vals = defaultdict(list)
    for key, gem in day_gem.items():
        promo = day_promo.get(key, "")
        var_vals[classify(promo)].append(gem)

    baseline = var_vals.get("Play X (baseline)", []) + var_vals.get("(no promo / baseline day)", [])
    base_avg = sum(baseline) / len(baseline) if baseline else 0

    print(f"Baseline (Play X / no promo) avg gem usage: {base_avg:,.0f}  (n={len(baseline)})\n")
    print(f"{'Shiny Show variant':28s} {'days':>4s} {'avg gem usage':>15s} {'vs baseline':>12s}")
    rowsout = []
    for v, vals in var_vals.items():
        avg = sum(vals) / len(vals)
        lift = (avg / base_avg - 1) * 100 if base_avg else 0
        rowsout.append((avg, v, len(vals), lift))
    for avg, v, n, lift in sorted(rowsout, reverse=True):
        print(f"{v:28s} {n:4d} {avg:15,.0f} {lift:+11.0f}%")


if __name__ == "__main__":
    main()
