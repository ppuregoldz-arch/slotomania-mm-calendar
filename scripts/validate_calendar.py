#!/usr/bin/env python3
"""Validate July 2026 calendar (from canvas) against learned rules + Nivi guidelines.
Reports every violation. Re-run: python3 scripts/validate_calendar.py
"""
from __future__ import annotations

import re
from pathlib import Path

CANVAS = Path("/Users/itayg/.cursor/projects/Users-itayg-Desktop-Cursor-Work/canvases/july-2026-calendar.canvas.tsx")


def parse_days():
    tsx = CANVAS.read_text(encoding="utf-8")
    block = re.search(r"const DAYS: Day\[\] = \[(.*?)\n\];", tsx, re.S).group(1)
    days = []
    for m in re.finditer(r"\{\s*date:\s*(\d+),\s*dow:\s*\"(\w+)\"(.*?)\},?\s*$", block, re.M):
        date = int(m.group(1)); dow = m.group(2); rest = m.group(3)
        sale = "sale: true" in rest
        tagm = re.search(r'tag:\s*"(\w+)"', rest)
        tag = tagm.group(1) if tagm else ""
        itemsm = re.search(r'items:\s*\[(.*)\]', rest, re.S)
        items = re.findall(r'"([^"]*)"', itemsm.group(1)) if itemsm else []
        days.append({"date": date, "dow": dow, "sale": sale, "tag": tag, "items": items})
    return days


def st_season(d):
    if d <= 3: return "Battlesheep"
    if d <= 8: return "Blast"
    if d <= 13: return "Battlesheep"
    if d <= 18: return "Blast"
    if d <= 23: return "SNL"
    if d <= 28: return "Battlesheep"
    return "Blast"


def mt_season(d):
    if d <= 5: return "Quest"
    if d <= 10: return "Globez"
    if d <= 15: return "Figz"
    if d <= 20: return "Quest"
    if d <= 25: return "Globez"
    return "Figz"


def album_week(d):
    if d <= 13: return "old"      # weeks 8-9, Wilds allowed
    if d <= 19: return "wk1"      # Reg3/Shiny/Starter
    if d <= 26: return "wk2"      # up to Ace3 + Shiny Limited
    return "wk3"                  # up to Ace4 + Gold3


# Allowed card bank by album week (Nivi) — no Wild after Jul 14
BANK = {
    "old": {"reg", "ace", "gold", "wild", "shiny"},
    "wk1": {"reg", "shiny", "starter"},           # Reg3, Shiny, Starter (no ace/gold/wild)
    "wk2": {"reg", "ace", "shiny"},               # Reg3-4, Ace3, Shiny, Shiny Limited (no wild/gold)
    "wk3": {"reg", "ace", "gold", "shiny"},       # Reg3-4, Gold3, Ace3-4, Shiny (no wild)
}
SEASON_SKU = {
    "superboom": "Blast", "pab": "Blast", "pickaboom": "Blast",
    "parasheep": "Battlesheep", "airstrike": "Battlesheep",
    "multiwheel": "SNL", "shield": "SNL", "snl dice": "SNL",
}
VFM = ["mgap bogo", "mgap matched", "more-for-less", "more for less", "buy more", "coin sale", "extreme stamp", "price cut"]


def audit(days):
    """Run all rule checks on day list; return (violations, coverage) for CLI + build script."""
    V = []
    def flag(d, msg): V.append(f"  Day {d}: {msg}")

    hammer_week = {}
    mgap_week = {}
    shiny_week = {}
    ggs_week = {}
    rmfl_days = []      # Rolling More for Less — cooldown
    matched_sale = []
    def wk(d): return (d - 1) // 7

    for day in days:
        d = day["date"]; items = day["items"]; low = [i.lower() for i in items]
        st = st_season(d); alb = album_week(d)

        # 1. Sale Fri/Sat only
        if day["sale"] and day["dow"] not in ("Fri", "Sat"):
            flag(d, f"Sale on {day['dow']} (allowed Fri/Sat only)")

        # 2. Hammers one source/day (H = Hammers · h = hours)
        ham = [i for i in items if (re.search(r"[Hh]ammer", i) or re.search(r"\b\d+\s*H\b", i)) and "wheel" not in i.lower()]
        if len(ham) > 1:
            flag(d, f"More than one Hammers source ({len(ham)})")
        hammer_week[wk(d)] = hammer_week.get(wk(d), 0) + (1 if ham else 0)

        # 3. VFM <=1/day (except event)
        vfm = [i for i in low if any(k in i for k in VFM)]
        if len(vfm) > 1 and day["tag"] != "event":
            flag(d, f"More than one VFM: {vfm}")

        # 4. Clan Pack ban
        if any("clan pack" in i for i in low):
            flag(d, "Clan Pack (banned)")

        # 5. Monday no strong revenue promo
        if day["dow"] == "Mon" and any(any(k in i for k in ("mgap", "coin sale", "rolling", "prize mania")) for i in low):
            flag(d, "Strong revenue promo on Monday (Dash Day)")

        # 6. DD present
        dds = [i for i in low if i.startswith("dd") or "daily deal" in i]
        if not dds:
            flag(d, "Missing Daily Deal")

        # 7. DD once/multiple
        once_dd = [i for i in dds if re.search(r"wild|shiny limited", i)]
        if once_dd and len(dds) < 2:
            flag(d, f"DD once (Wild/Shiny Limited) without alternate DD multiple: {once_dd}")

        # 8. Card bank — no Wild after 14/7; Shiny Show variant excluded (feature not bank card)
        for i in low:
            if "wild" in i and alb != "old" and "shiny show" not in i:
                flag(d, f"Wild outside bank ({alb}, no Wild): '{i}'")
            if "ace" in i and alb == "wk1":
                # ace not in wk1 bank (unless 'ace spins' generic gameplay)
                if "ace spin" not in i and "ace heist" not in i:
                    flag(d, f"Ace in wk1 (Ace not in bank): '{i}'")

        # 9. Season SKU matches active Short-Term
        for i in low:
            for kw, season in SEASON_SKU.items():
                if kw in i and season != st:
                    # avoid false positives: dice booster/deluxe not snl dice
                    if kw == "snl dice" or kw in ("superboom", "pab", "parasheep", "airstrike", "multiwheel", "shield", "pickaboom"):
                        flag(d, f"Season SKU '{kw}' ({season}) on {st} day")

        # 10. SnL Dice multiples (>=2)
        for i in items:
            m = re.search(r"(\d+)?\s*SnL Dice", i)
            if m and (not m.group(1) or int(m.group(1)) < 2):
                flag(d, f"SnL Dice not in pair/triple (2/3): '{i}'")

        # 11. Extreme Stamp not on sale day (except event)
        if any("extreme stamp" in i for i in low) and day["sale"] and day["tag"] != "event":
            flag(d, "Extreme Stamp on Sale day")

        # 12. Extreme Stamp not with Wild card (offers; Shiny Show excluded; event = exception)
        if any("extreme stamp" in i for i in low) and any(("wild" in i and "shiny show" not in i) for i in low) and day["tag"] != "event":
            flag(d, "Extreme Stamp with Wild Card")

        # 13. ADS daily
        if not any(i.startswith("ads") for i in low):
            flag(d, "Missing ADS PO")

        # 14. Core daily
        if not any(any(k in i for k in ("core", "mes", "spin zone", "pyp", "win master", "ace heist", "spinner", "loot")) for i in low):
            flag(d, "Missing Core (coin sink)")

        # MGAP Matched not on sale day
        if any("matched" in i for i in low) and day["sale"]:
            flag(d, "MGAP Matched on Sale day (excluded)")
        # Rolling More for Less — collect dates (cooldown)
        if any(("more-for-less" in i or "more for less" in i or "buy more" in i) for i in low):
            rmfl_days.append(d)

        # tallies
        if any("mgap" in i for i in low): mgap_week[wk(d)] = mgap_week.get(wk(d), 0) + 1
        if any("shiny show" in i for i in low): shiny_week[wk(d)] = shiny_week.get(wk(d), 0) + 1
        if any("ggs" in i for i in low): ggs_week[wk(d)] = ggs_week.get(wk(d), 0) + 1

        # anchors
        if day["dow"] == "Thu" and not any("golden spin" in i for i in low):
            flag(d, "Thursday without Golden Spin")
        if day["dow"] == "Wed" and not any("piggy" in i for i in low):
            pass  # Piggy weekly, not every Wed necessarily
        if day["dow"] == "Mon" and day["tag"] != "dash" and not any("dash pass" in i for i in low):
            flag(d, "Monday without Dash Day")

    # weekly caps
    MGAP_PER_WEEK = 2

    def days_in_week_slice(w: int, last: int = 31) -> int:
        return sum(1 for d in range(1, last + 1) if (d - 1) // 7 == w)

    for w, c in mgap_week.items():
        if c > MGAP_PER_WEEK:
            V.append(f"  Week {w+1}: MGAP {c} (>{MGAP_PER_WEEK}/week)")
        elif days_in_week_slice(w) >= 4 and c < MGAP_PER_WEEK:
            V.append(f"  Week {w+1}: MGAP {c} (<{MGAP_PER_WEEK}/week)")
        elif days_in_week_slice(w) < 4 and c < 1:
            V.append(f"  Week {w+1}: MGAP {c} (partial week needs ≥1)")
    for w, c in hammer_week.items():
        if c > 4: V.append(f"  Week {w+1}: Hammers {c} days (>4/week)")
    for w, c in ggs_week.items():
        if c > 2: V.append(f"  Week {w+1}: x2 GGS {c} (>2/week)")
    for w, c in shiny_week.items():
        if c > 3: V.append(f"  Week {w+1}: Shiny Show {c} (>3/week)")
    for a, b in zip(rmfl_days, rmfl_days[1:]):
        if b - a < 10:
            V.append(f"  Rolling More for Less {a}→{b}: gap {b-a} days (<10, cooldown 1.5-2 wks)")

    coverage = {
        "shiny_week": dict(sorted(shiny_week.items())),
        "mgap_week": dict(sorted(mgap_week.items())),
        "hammer_week": dict(sorted(hammer_week.items())),
        "ggs_week": dict(sorted(ggs_week.items())),
    }
    return V, coverage


# Rules checked (dashboard transparency)
RULES_CHECKED = 18


def main():
    days = parse_days()
    V, coverage = audit(days)
    print(f"=== Validation: {len(days)} days ===")
    if not V:
        print("✅ No violations — calendar passes all checked rules.")
    else:
        print(f"❌ Found {len(V)} violations:")
        print("\n".join(V))
    # coverage summary
    print("\n=== Coverage summary ===")
    print(f"Shiny Show per week: {coverage['shiny_week']}")
    print(f"MGAP per week: {coverage['mgap_week']}")
    print(f"Hammers days per week: {coverage['hammer_week']}")


if __name__ == "__main__":
    main()
