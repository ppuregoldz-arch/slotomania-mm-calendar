#!/usr/bin/env python3
"""Audit Monday board card usage vs Nivi Aug 2026 weekly banks (date range).

ADS PO prizes do not count toward the weekly card bank (economy rule).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_august_2026_plan import (  # noqa: E402
    CARD_BUDGETS,
    CARD_VALUE_SCORE,
    card_week,
    collector_album_phase,
)

COUNT_PRODUCTS = frozenset(
    {
        "Daily deal",
        "RYD",
        "Buy all",
        "Rolling offer",
        "Prize Mania",
        "Counter PO",
        "Core",
        "Album",
        "Clan-Dash",
        "Offers & coin sale",
    }
)

EXCLUDE_NAME = re.compile(
    r"short term|mid term|quest season|globez|figz|winovate|mega pods|"
    r"mgap|wild symbol|album —|album - phase|blast -|snl -|battlesheep",
    re.I,
)

CARD_RE = re.compile(
    r"(?:(\d)\s*[*★]\s*(Reg|Gold|Ace)(?:\s+card)?|"
    r"(Shiny Limited|Shiny Card)|"
    r"(Wild(?:\s+(?:Ord(?:inary)?|Gold|Ace|Any|Supreme))?))",
    re.I,
)

ACE_RE = re.compile(r"(\d)\s*★\s*Ace", re.I)
GOLD_RE = re.compile(r"(\d)\s*★\s*Gold", re.I)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--from", dest="from_iso", default="2026-08-01")
    p.add_argument("--to", dest="to_iso", default="2026-08-15")
    p.add_argument("--json", action="store_true", help="Print machine-readable summary")
    return p.parse_args()


def card_keys_in_text(text: str) -> list[str]:
    keys: list[str] = []
    for m in CARD_RE.finditer(text or ""):
        if m.group(1) and m.group(2):
            kind = m.group(2).title()
            if kind == "Reg":
                kind = "Reg"
            keys.append(f"{kind}_{m.group(1)}")
        elif m.group(3):
            keys.append(m.group(3).title())
        elif m.group(4):
            w = (m.group(4) or "Wild").strip()
            if re.search(r"gold", w, re.I):
                keys.append("Wild Gold")
            elif re.search(r"ord", w, re.I):
                keys.append("Wild Ord")
            else:
                keys.append("Wild Ord")
    return keys


def should_count_row(product: str, name: str) -> bool:
    if product not in COUNT_PRODUCTS:
        return False
    if EXCLUDE_NAME.search(name or ""):
        return False
    if product == "Core":
        return is_core_gameplay(product, name) or bool(
            re.search(r"spinner clash", name or "", re.I)
        )
    if product == "Album":
        return bool(re.search(r"shiny show", name or "", re.I))
    if product == "Offers & coin sale":
        return "piggy" in (name or "").lower() or "decoy" in (name or "").lower()
    if product == "Clan-Dash":
        return "shiny card" in (name or "").lower() or "time limited prize" in (name or "").lower()
    return True


def is_purchase_row(product: str, name: str) -> bool:
    if product in ("Daily deal", "RYD", "Buy all", "Rolling offer", "Prize Mania", "Counter PO"):
        return True
    nl = name.lower()
    return "piggy" in nl or "decoy" in nl or "buy all" in nl or "mystery buy all" in nl


def is_core_gameplay(product: str, name: str) -> bool:
    if product != "Core":
        return False
    nl = name.lower()
    if any(x in nl for x in ("shiny show", "status boost", "betty", "custom pod", "dash pass", "album")):
        return False
    return bool(re.search(r"win master|ace heist|pyp|spin zone|spinner clash|spin zone", nl, re.I))


def primary_card_keys(product: str, name: str, desc: str) -> list[str]:
    """One primary bank slot per offer where possible."""
    blob = f"{name}\n{desc}"
    nl = name.lower()
    if product == "Daily deal":
        keys = card_keys_in_text(name + "\n" + (desc or ""))
        return keys[:1] if keys else []
    if product == "RYD" or nl.startswith("ryd"):
        keys = card_keys_in_text(name)
        return keys[:1] if keys else card_keys_in_text(desc)[:1]
    if "decoy" in nl:
        m = re.search(r"d3:\s*([^+|]+)", name, re.I)
        if m:
            keys = card_keys_in_text(m.group(1))
            if keys:
                return keys[:1]
        for line in (desc or "").splitlines():
            if line.lower().startswith("d3"):
                keys = card_keys_in_text(line)
                if keys:
                    return keys[-1:]  # hook last in d3 line
        return card_keys_in_text(blob)[:1]
    if "buy all" in nl or "mystery buy all" in nl:
        return card_keys_in_text(desc or name)
    if "prize mania" in nl:
        return card_keys_in_text(name)[:1]
    if product == "Rolling offer" or "rolling offer" in nl:
        keys = card_keys_in_text(desc or name)
        return keys[:1] if keys else []
    if product == "ADS" or nl.startswith("ads po"):
        return []  # ADS — not counted toward Nivi card bank
    if "piggy" in nl:
        return card_keys_in_text(name)[:1]
    if "spinner clash" in nl:
        return card_keys_in_text(desc or name)
    return card_keys_in_text(blob)


def audit_range(from_iso: str, to_iso: str) -> dict:
    by = json.loads(
        (ROOT / "mm_calendar/data/monday_board_live_by_date.json").read_text()
    )["by_date"]

    violations: list[dict] = []
    usages: list[dict] = []
    used_by_week: dict[int, Counter] = defaultdict(Counter)

    d_start = int(from_iso.split("-")[2])
    d_end = int(to_iso.split("-")[2])

    for day in range(d_start, d_end + 1):
        iso = f"2026-08-{day:02d}"
        cw = card_week(day)
        phase = collector_album_phase(day)
        day_slots: list[tuple[str, str, str, str]] = []

        for it in by.get(iso, []):
            if it.get("product") == "Day":
                continue
            name = it.get("name") or ""
            product = it.get("product") or ""
            if not should_count_row(product, name):
                continue
            desc = it.get("description") or ""
            blob = f"{name}\n{desc}"
            keys = primary_card_keys(product, name, desc)
            if not keys:
                continue
            purchase = is_purchase_row(product, name)
            core = is_core_gameplay(product, name) or "spinner clash" in name.lower()
            for k in keys:
                # 1★/2★ on top — not in Nivi bank table
                if re.match(r"Reg_[12]$", k):
                    continue
                day_slots.append((it["id"], product, name, k))
                usages.append(
                    {
                        "date": iso,
                        "day": day,
                        "card_week": cw,
                        "album_phase": phase,
                        "id": it["id"],
                        "product": product,
                        "name": name,
                        "card": k,
                        "purchase": purchase,
                        "core": core,
                    }
                )
                if purchase and k.startswith("Ace_"):
                    violations.append(
                        {
                            "rule": "no_ace_in_purchase",
                            "date": iso,
                            "name": name,
                            "card": k,
                            "detail": "אוגוסט: לא מוכרים Ace ב-DD/RYD/Buy All/Decoy/…",
                        }
                    )
                if core and (k.startswith("Gold_") or k == "Wild Gold"):
                    violations.append(
                        {
                            "rule": "no_gold_in_core",
                            "date": iso,
                            "name": name,
                            "card": k,
                            "detail": "Core משחקי — לא Gold",
                        }
                    )

            if purchase:
                wild_n = sum(1 for k in keys if k.startswith("Wild"))
                if wild_n > 1:
                    violations.append(
                        {
                            "rule": "wild_per_source",
                            "date": iso,
                            "name": name,
                            "detail": f"{wild_n} Wild באותה הצעה",
                        }
                    )

        # DD once+multiple pair: same card type → one bank slot
        from collections import Counter as _Counter

        dd_by_card = _Counter(k for _, p, _, k in day_slots if p == "Daily deal")
        if dd_by_card:
            for card, cnt in dd_by_card.items():
                if cnt > 1:
                    extras = cnt - 1
                    for _ in range(extras):
                        for i in range(len(day_slots) - 1, -1, -1):
                            if day_slots[i][1] == "Daily deal" and day_slots[i][3] == card:
                                day_slots.pop(i)
                                break

        for _id, _p, _n, k in day_slots:
            used_by_week[cw][k] += 1

        # Card type allowed in bank this week?
        for _id, _p, _n, k in day_slots:
            if k not in CARD_BUDGETS.get(cw, {}) and not k.startswith("Wild"):
                violations.append(
                    {
                        "rule": "card_not_in_bank",
                        "date": iso,
                        "name": _n,
                        "card": k,
                        "detail": f"סוג {k} לא בבנק שבוע {cw} (1–9/10–16/…)",
                    }
                )

    over_cap: list[dict] = []
    under_notes: list[dict] = []
    for cw in sorted(set(card_week(d) for d in range(d_start, d_end + 1))):
        budget = CARD_BUDGETS.get(cw, {})
        used = used_by_week[cw]
        for key, cap in budget.items():
            u = used.get(key, 0)
            if u > cap:
                over_cap.append({"card_week": cw, "card": key, "used": u, "cap": cap})
        for key, cap in budget.items():
            u = used.get(key, 0)
            if u < cap and cw == 1 and d_end >= 9:
                pass  # full week 1 — report unused
            elif u < cap and cw == 2 and d_end >= 16:
                pass

    # Week 1 full check if range includes 1-9
    w1_unused = []
    if d_start <= 1 and d_end >= 9:
        for key, cap in CARD_BUDGETS[1].items():
            u = used_by_week[1].get(key, 0)
            if u != cap:
                w1_unused.append({"card": key, "used": u, "budget": cap, "delta": u - cap})

    # Partial week 2 if 10-15 only
    w2_partial = []
    if d_end >= 10:
        for key, cap in CARD_BUDGETS[2].items():
            u = used_by_week[2].get(key, 0)
            w2_partial.append({"card": key, "used": u, "budget": cap, "remaining": cap - u})

    return {
        "range": f"{from_iso}..{to_iso}",
        "usages": usages,
        "used_by_week": {str(k): dict(v) for k, v in used_by_week.items()},
        "violations": violations,
        "over_cap": over_cap,
        "week1_bank_delta": w1_unused,
        "week2_progress": w2_partial,
        "budgets": {str(k): v for k, v in CARD_BUDGETS.items()},
    }


def main() -> None:
    args = parse_args()
    rep = audit_range(args.from_iso, args.to_iso)
    if args.json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        return

    print(f"=== בדיקת קלפים Monday {rep['range']} vs גיידליין Nivi ===\n")

    if rep["violations"]:
        print("❌ חריגות HARD")
        for v in rep["violations"]:
            print(f"  · {v['date']} [{v['rule']}] {v.get('card','')} — {v['name'][:55]}")
            print(f"    {v['detail']}")
    else:
        print("✅ אין חריגות Ace ברכישה / Gold ב-Core / Wild כפול בהצעה\n")

    if rep["over_cap"]:
        print("❌ חריגה מתקרת שבוע (מאגר)")
        for o in rep["over_cap"]:
            print(f"  · שבוע קלפים {o['card_week']}: {o['card']} = {o['used']} > {o['cap']}")
    else:
        print("✅ אין חריגה ממכסת שבוע במאגר (לפי מה שספירה על Monday)\n")

    print("--- שבוע קלפים 1 (1–9/8) — שימוש vs תקרה ---")
    used1 = rep["used_by_week"].get("1", {})
    for key, cap in CARD_BUDGETS[1].items():
        u = used1.get(key, 0)
        flag = "✓" if u == cap else ("!" if u > cap else "↓")
        print(f"  {flag} {key:14} {u}/{cap}")

    if int(args.to_iso.split("-")[2]) >= 10:
        print("\n--- שבוע קלפים 2 (10–16/8) — התקדמות עד", args.to_iso, "---")
        used2 = rep["used_by_week"].get("2", {})
        for key, cap in CARD_BUDGETS[2].items():
            u = used2.get(key, 0)
            print(f"  · {key:14} {u} used (תקרה שבוע {cap}, נשאר ~{max(0, cap - u)})")

    print("\n--- פירוט לפי יום (קלפים שזוהו) ---")
    by_day: dict[str, list[str]] = defaultdict(list)
    for u in rep["usages"]:
        by_day[u["date"]].append(f"{u['card']} ({u['product'][:8]})")
    for iso in sorted(by_day):
        print(f"  {iso}: {', '.join(by_day[iso])}")

    sys.exit(1 if rep["violations"] or rep["over_cap"] else 0)


if __name__ == "__main__":
    main()
