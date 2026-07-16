#!/usr/bin/env python3
"""Daily / weekly / monthly sanity check for august_2026_plan.json."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_august_2026_plan import (  # noqa: E402
    DD_ON_PURCHASE_DAYS,
    POPUP_STORE_DAYS,
    PUZZLE_MES_TEST,
    ROLLING_BMFL_CYCLES,
    ROLLING_BMFL_PRICING,
    counts_toward_vfm_cap,
    count_gameplay_core_challenges,
    has_parallel_control_gameplay,
    is_popup_store_item,
    is_puzzle_mes_item,
    is_rolling_bmfl_name,
    normalize_offer_pricing,
    validate_rolling_item_stamps,
)

PLAN = ROOT / "mm_calendar" / "data" / "august_2026_plan.json"


def load_days() -> list[dict]:
    return json.loads(PLAN.read_text(encoding="utf-8"))["days"]


def audit_daily(days: list[dict]) -> list[str]:
    out: list[str] = []
    bogo_count = sum(
        1
        for day in days
        for i in day.get("items", [])
        if i.get("status") == "Daily deal" and "BOGO" in (i.get("name") or "")
    )
    if bogo_count != 2:
        out.append(f"DD BOGO: צפוי 2×/חודש, בפועל {bogo_count}")
    for day in days:
        d = int(day["date"])
        items = [i for i in day.get("items", []) if not i.get("backup")]
        names = [i.get("name") or "" for i in items]
        if sum(1 for n in names if re.search(r"coin sale", n, re.I)) > 1:
            out.append(f"{d}/8: יותר מ-Coin Sale אחד")
        if sum(1 for n in names if re.search(r"shiny show", n, re.I)) > 1:
            out.append(f"{d}/8: יותר מ-Shiny Show אחד")
        gp_n = count_gameplay_core_challenges(items)
        gp_cap = 2 if d in PUZZLE_MES_TEST else 1
        if gp_n > gp_cap:
            out.append(f"{d}/8: יותר מ-Core משחקי אחד ({gp_n})")
        if d in DD_ON_PURCHASE_DAYS and not any("(on purchase)" in n.lower() for n in names):
            out.append(f"{d}/8: חסר DD (on purchase)")
        if d in PUZZLE_MES_TEST and not any(is_puzzle_mes_item(i) for i in items):
            out.append(f"{d}/8: חסר שורת Puzzle M.E.S")
        if d in PUZZLE_MES_TEST and not has_parallel_control_gameplay(items):
            out.append(f"{d}/8: חסר Core לקונטרול (80%) ביום Puzzle")
        vfm_n = sum(1 for i in items if counts_toward_vfm_cap(i))
        popup_shell_vfm = d in POPUP_STORE_DAYS and any(
            is_popup_store_item(i) for i in day.get("items", [])
        )
        if vfm_n < 1 and d != 22 and not popup_shell_vfm:
            out.append(f"{d}/8: חסרה הצעה שנייה (VFM, לא Dash)")
        dd_p = sec_p = None
        for i in items:
            if i.get("status") == "Daily deal":
                dd_p = normalize_offer_pricing(i.get("pricing"))
            elif counts_toward_vfm_cap(i):
                sec_p = normalize_offer_pricing(i.get("pricing"))
        if dd_p and sec_p and dd_p == sec_p:
            out.append(f"{d}/8: DD והצעה שנייה באותו Pricing ({dd_p})")
        for i in items:
            nm = (i.get("name") or "").lower()
            if "popup store" in nm and d not in POPUP_STORE_DAYS:
                out.append(f"{d}/8: Popup Store מחוץ ל-12/19/26")
            if re.search(r"puzzle m\.e\.s", nm, re.I) and d not in PUZZLE_MES_TEST:
                out.append(f"{d}/8: Puzzle M.E.S מחוץ ל-18–24")
    shiny = sorted(
        int(day["date"])
        for day in days
        if any(re.search(r"shiny show", i.get("name") or "", re.I) for i in day["items"])
    )
    for a, b in zip(shiny, shiny[1:]):
        if b - a < 2:
            out.append(f"Shiny Show: מרווח {b - a} ימים בין {a} ו-{b}")
    return out


def audit_weekly(days: list[dict]) -> list[str]:
    out: list[str] = []
    mgap_by_w: dict[int, list[int]] = defaultdict(list)
    for day in days:
        d = int(day["date"])
        w = (d - 1) // 7
        if any("mgap" in (i.get("name") or "").lower() for i in day["items"]):
            mgap_by_w[w].append(d)
    for w, ds in sorted(mgap_by_w.items()):
        if len(ds) > 2:
            out.append(f"שבוע {w + 1}: {len(ds)} MGAP (ברזל 2): {ds}")
        elif len(ds) < 2 and w < 4:
            out.append(f"שבוע {w + 1}: רק {len(ds)} MGAP: {ds}")
    for w in range(6):
        ds = [d for d in range(1, 32) if (d - 1) // 7 == w]
        if len(ds) < 7:
            continue
        tiers: set[str] = set()
        for d in ds:
            day = next(x for x in days if int(x["date"]) == d)
            for i in day.get("items", []):
                t = normalize_offer_pricing(i.get("pricing"))
                if t:
                    tiers.add(t)
        if not {"Medium", "High", "Max"}.issubset(tiers):
            out.append(f"שבוע {w + 1}: Pricing חסר M/H/Max — בפועל {sorted(tiers)}")
    return out


def audit_monthly(days: list[dict]) -> list[str]:
    out: list[str] = []
    pm = [i.get("name") or "" for day in days for i in day["items"] if i.get("status") == "Prize Mania"]
    def _pm_reg_only(n: str) -> bool:
        low = n.lower()
        if "shiny limited" in low or "dice booster" in low:
            return False
        return "reg pack" in low

    reg_only = sum(1 for n in pm if _pm_reg_only(n))
    if pm and reg_only == len(pm):
        out.append(f"Prize Mania: כולם Reg-pack ({len(pm)})")
    popup_days = sorted(int(d["date"]) for d in days if any("popup store" in (i.get("name") or "").lower() for i in d["items"]))
    if popup_days != sorted(POPUP_STORE_DAYS):
        out.append(f"Popup Store ימים: {popup_days} (צפוי 12/19/26)")
    puzzle_days = sorted(
        int(d["date"])
        for d in days
        if any(re.search(r"puzzle m\.e\.s", i.get("name") or "", re.I) for i in d["items"])
    )
    if puzzle_days != sorted(PUZZLE_MES_TEST):
        out.append(f"Puzzle M.E.S ימים: {puzzle_days} (צפוי 18–24)")
    bmfl_bad: list[str] = []
    bxgy_count = 0
    for day in days:
        d = int(day["date"])
        for i in day.get("items", []):
            if i.get("status") != "Rolling offer":
                continue
            nm = i.get("name") or ""
            m = re.search(r"(\d+)\s*cycles?", nm, re.I)
            pr = normalize_offer_pricing(i.get("pricing"))
            if is_rolling_bmfl_name(nm):
                if not m or int(m.group(1)) != ROLLING_BMFL_CYCLES:
                    bmfl_bad.append(f"{d}:cycles")
                if pr != ROLLING_BMFL_PRICING:
                    bmfl_bad.append(f"{d}:bmfl-pricing")
            else:
                bxgy_count += 1
    if bmfl_bad:
        out.append(f"Rolling BMFL: {','.join(bmfl_bad)}")
    if bxgy_count < 1:
        out.append("Rolling Buy X Get Y: חסר בחודש")
    stamp_issues: list[str] = []
    for day in days:
        d = int(day["date"])
        for i in day.get("items", []):
            if i.get("status") != "Rolling offer":
                continue
            stamp_issues.extend(
                validate_rolling_item_stamps(d, i.get("name") or "", i.get("desc") or "")
            )
    if stamp_issues:
        out.append("Rolling stamps: " + "; ".join(stamp_issues[:8]))
    return out


def main() -> int:
    days = load_days()
    daily = audit_daily(days)
    weekly = audit_weekly(days)
    monthly = audit_monthly(days)
    print("# אודיט אוגוסט 2026\n")
    print("## יומי")
    print("OK" if not daily else "\n".join(f"- {x}" for x in daily))
    print("\n## שבועי")
    print("OK" if not weekly else "\n".join(f"- {x}" for x in weekly))
    print("\n## חודשי")
    print("OK" if not monthly else "\n".join(f"- {x}" for x in monthly))
    return 1 if daily or weekly or monthly else 0


if __name__ == "__main__":
    raise SystemExit(main())
