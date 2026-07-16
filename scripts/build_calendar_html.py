#!/usr/bin/env python3
"""Build unified HTML dashboard: calendar, offers, Core coin sink, gem usage, revenue — tabbed UI.
Output: mm_calendar/data/mm_dashboard.html
"""
from __future__ import annotations

import json
import re
import shutil
import statistics as st
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))
import validate_calendar as vcal  # noqa: E402
from mm_calendar.purchase_drivers import ensure_month_open_biggest_denom, ensure_all_months  # noqa: E402
CANVAS = Path("/Users/itayg/.cursor/projects/Users-itayg-Desktop-Cursor-Work/canvases/july-2026-calendar.canvas.tsx")
OUT = ROOT / "mm_calendar" / "data" / "mm_dashboard.html"
CSS_FILE = ROOT / "mm_calendar" / "assets" / "dashboard.css"
PUBLIC_DIR = ROOT / "mm_calendar" / "public"
PUBLIC_INDEX = PUBLIC_DIR / "index.html"
PUBLIC_CSS = PUBLIC_DIR / "assets" / "dashboard.css"
SHELL_FILE = ROOT / "mm_calendar" / "assets" / "dashboard_shell.html"
APP_JS_FILE = ROOT / "mm_calendar" / "assets" / "dashboard_app.js"
REAL_MONTHS_FILE = ROOT / "mm_calendar" / "data" / "real_months.json"
AUGUST_PLAN_FILE = ROOT / "mm_calendar" / "data" / "august_2026_plan.json"
CALIBRATION_FILE = ROOT / "mm_calendar" / "data" / "model_calibration.json"
from monday_live_dashboard import (  # noqa: E402
    load_monday_by_date,
    merge_august_plan_days,
    write_authority_artifacts,
)


def extract_days() -> str:
    tsx = CANVAS.read_text(encoding="utf-8")
    m = re.search(r"const DAYS: Day\[\] = (\[[\s\S]*?\n\]);", tsx)
    if not m:
        raise SystemExit("DAYS array not found in canvas")
    return m.group(1)


def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_calibration() -> dict:
    if not CALIBRATION_FILE.is_file():
        return {}
    try:
        return json.loads(CALIBRATION_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_real_months() -> dict:
    if not REAL_MONTHS_FILE.is_file():
        return {}
    try:
        return json.loads(REAL_MONTHS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def normalize_august_plan_day(day: dict) -> dict:
    """Map august_2026_plan.json day → real_months.json shape for the dashboard."""

    def infer_item_pricing(it: dict) -> str:
        pr = it.get("pricing")
        if pr is not None and str(pr).strip():
            return str(pr).strip()
        name = it.get("name") or ""
        desc = it.get("desc") or ""
        m = re.search(r"Pricing:\s*(High|Max|Medium|Mid|Low)", desc, re.I)
        if m:
            v = m.group(1)
            return "Medium" if v.lower() == "mid" else v.title()
        m = re.search(r"\|\s*(H|M|L)\s*Pric(?:e|ing)", name, re.I)
        if m:
            return {"H": "High", "M": "Medium", "L": "Low"}[m.group(1).upper()]
        return ""

    out: dict = {
        "date": day["date"],
        "iso": day["iso"],
        "dow": day["dow"],
        "hasAnchor": False,
        "seasons": [
            {
                "name": s.get("name", ""),
                "status": s.get("status", ""),
                "desc": s.get("desc", "") or "",
                "isFirst": bool(s.get("isFirst", False)),
            }
            for s in day.get("seasons", [])
        ],
        "items": [],
        "sale": bool(day.get("sale")),
        "tag": day.get("tag"),
        "banner": day.get("banner"),
        "isPast": False,
        "draftSource": "august_2026_plan",
        "planNotes": (day.get("notes") or "").strip(),
    }
    for it in day.get("items", []):
        out["items"].append(
            {
                "name": it.get("name", ""),
                "status": it.get("status", ""),
                "pricing": infer_item_pricing(it),
                "desc": it.get("desc", "") or "",
                "backup": bool(it.get("backup")),
            }
        )
    for it in out["items"]:
        st_lower = (it.get("status") or "").lower()
        if st_lower == "event":
            out["hasAnchor"] = True
            break
    ensure_month_open_biggest_denom(out)
    return out


def load_months_for_dashboard() -> tuple[dict, list[str]]:
    """Monday-backed months plus local draft plans (never uploaded to Monday)."""
    months = load_real_months()
    draft_keys: list[str] = []
    if not AUGUST_PLAN_FILE.is_file():
        return months, draft_keys
    try:
        plan = json.loads(AUGUST_PLAN_FILE.read_text(encoding="utf-8"))
        by_date = load_monday_by_date()
        merged_plan_days = merge_august_plan_days(plan.get("days", []), by_date)
        write_authority_artifacts(plan.get("days", []), by_date)
        days: list[dict] = []
        for d in merged_plan_days:
            if d.get("mondayAuthority"):
                ensure_month_open_biggest_denom(d)
                days.append(d)
            else:
                days.append(normalize_august_plan_day(d))
        if days:
            months["2026-08"] = days
            draft_keys.append("2026-08")
    except Exception as exc:
        print(f"Warning: could not merge August plan: {exc}")
    ensure_all_months(months)
    return months, draft_keys


def patch_calibration_for_draft_months(cal: dict, draft_months: list[str]) -> dict:
    if not draft_months:
        return cal
    import copy

    cal = copy.deepcopy(cal)
    meta = cal.setdefault("meta", {})
    existing = list(meta.get("draft_calendar_months") or [])
    for key in draft_months:
        if key not in existing:
            existing.append(key)
    meta["draft_calendar_months"] = existing
    rev = cal.setdefault("revenue", {})
    pu = cal.setdefault("pu", {})
    rev_crowd = rev.setdefault("crowd_adj_by_month", {})
    pu_crowd = pu.setdefault("crowd_adj_by_month", {})
    if "2026-08" in draft_months:
        july_rev = rev_crowd.get("2026-07", -3.3)
        rev_crowd.setdefault("2026-08", round(float(july_rev) - 2.0, 1))
        july_pu = pu_crowd.get("2026-07", 0.0)
        pu_crowd.setdefault("2026-08", round(float(july_pu), 1))
        meta["monday_authority_2026_08"] = {
            "from": "2026-08-01",
            "to": "2026-08-15",
            "read_only": True,
            "forecast_items_from": "monday_board_live_by_date.json",
            "note": "Days 1–15 revenue/PU forecasts use Monday board promos; do not overwrite without Itay approval.",
        }
    return cal


PROMO_LABEL = {
    "customPod": "Custom Pod", "coinSale": "Coin Sale", "decoyBonanza": "Decoy/Bonanza",
    "mgapBogo": "MGAP BOGO", "mgapMatched": "MGAP Matched", "mgapWildSymbols": "MGAP Wild Symbols",
    "mgapBigger": "MGAP Bigger", "gemback": "Boosted Gemback", "rollingMoreForLess": "Rolling More-for-Less",
    "rolling": "Rolling (other)", "prizeMania": "Prize Mania", "priceCut": "Price Cut", "buyAll": "Buy All",
    "goldenSpin": "Golden Spin", "counterPo": "Counter PO", "snl": "SNL", "happyHour": "Happy Hour",
    "extremeStamp": "Extreme Stamp", "fortuneDip": "Fortune Dip",
}
# Coin/gem SINK mechanics (gameplay features that CONSUME currency) — distinct from
# PROMO_LABEL above, which is purchase/injection offers (Coin Sale, Buy All, MGAP...). Core
# and Gems tabs are about what drains the economy, not what sells it, so they use this set.
COIN_SINK_LABEL = {
    "pyp": "PYP", "mesTokens": "M.E.S Tokens/Steps", "spinnerClash": "Spinner Clash",
    "aceCardLoot": "Ace/Card Loot", "customPod": "Custom Pod", "clanPoints": "Clan points/badges",
    "dashChallenge": "Dash Challenge", "machine": "Gameplay machine", "winMaster": "Win Master",
    "spinZone": "Spin Zone", "jackpot": "Jackpot (MES)", "megaWinner": "Mega Winner"
}
GEM_SINK_LABEL = {
    "shortTerm": "Short Term", "midTerm": "Mid Term", "album": "Album", "shinyShow": "Shiny Show"
}
SINK_LABEL = {**COIN_SINK_LABEL, **GEM_SINK_LABEL}


# ===== Performance data =====
LANE_COLOR = {"MGAP": "#ec4899", "Rolling": "#4f9cff", "Daily Deal": "#22c55e",
              "Gems": "#eab308", "Buy All": "#06b6d4", "RYD": "#a855f7"}
# (display, query-for-descFor, lane, solo_days, $/day)
REVENUE = [
    ("MGAP Bigger Multipliers", "MGAP Bigger Multipliers", "MGAP", 3, 235387),
    ("MGAP BOGO", "MGAP BOGO", "MGAP", 7, 190992),
    ("MGAP Matched", "MGAP Matched", "MGAP", 5, 183760),
    ("MGAP Wild Symbols", "MGAP Wild Symbols", "MGAP", 2, 178453),
    ("DD Clan Pack ⛔", "DD Clan Pack", "Daily Deal", 4, 151389),
    ("DD Superboom", "DD Superboom", "Daily Deal", 2, 132904),
    ("DD Hammers ⭐", "DD Hammers", "Daily Deal", 21, 132528),
    ("Rolling Buy More for Less ⭐", "Rolling Buy More for Less", "Rolling", 4, 131689),
    ("DD Wild Supreme", "DD Wild Supreme", "Daily Deal", 2, 129187),
    ("DD SB Wheel", "DD SB Wheel", "Daily Deal", 4, 127011),
    ("DD Wild Any", "DD Wild Any", "Daily Deal", 7, 106075),
    ("DD Parasheep/AS", "DD Parasheep", "Daily Deal", 8, 104774),
    ("Rolling bar/cycles", "Rolling Offer", "Rolling", 2, 104080),
    ("Rolling Supersized", "Rolling Supersized", "Rolling", 2, 73745),
    ("RYD 100% SB", "RYD 100% SB", "RYD", 2, 71672),
    ("Buy All Coins", "Buy All Coins", "Buy All", 2, 70232),
    ("Buy All Decoy Bonanza", "Bonanza", "Buy All", 1, 56650),
    ("Buy All Wild", "Buy All Wild", "Buy All", 4, 55461),
    ("RYD Wild Gold", "RYD Wild Gold", "RYD", 1, 36368),
    ("Gems Boosted Gemback", "Boosted Gemback", "Gems", 2, 42848),
    ("RYD 150% SB", "RYD 150% SB", "RYD", 6, 31750),
    ("Gems GGS", "x2 GGS", "Gems", 5, 34111),
    ("Gems Sale", "Gems Sale", "Gems", 5, 32918),
]

# DD-level prizes ($/day) — strongest prize types
PRIZES = [
    ("Clan Pack ⛔", 4, 151389, "Removed — reference only"),
    ("Superboom", 2, 132904, "Strong (small n)"),
    ("Hammers ⭐", 21, 132528, "Anchor — stable over 21 days"),
    ("Wild Supreme", 2, 129187, "Strong (small n)"),
    ("SB Wheel", 4, 127011, "Stable"),
    ("Wild Any", 7, 106075, "Weak (−20%)"),
    ("Parasheep / AS", 8, 104774, "Weak (−21%)"),
]

# (variant, days, gem_usage_M, Lift%) — baseline 48.7M
GEMS = [
    ("Joker - Different Prizes ⭐", 4, 92.3, 89), ("Wild Guaranteed", 1, 83.6, 71),
    ("All Cards - Joker", 5, 76.6, 57), ("All Cards", 5, 75.1, 54),
    ("Find the Flower / Betty", 1, 69.3, 42), ("Growing Shiny Show", 2, 68.3, 40),
    ("JP Symbol", 2, 67.9, 39), ("Clan Pack Guaranteed ⛔", 3, 67.4, 38),
    ("Different Prizes", 7, 67.1, 38), ("SnL dice", 1, 62.7, 29),
    ("For Every 2 Dashes", 2, 57.0, 17), ("Crazy with Aces ⚠️", 5, 47.9, -2),
    ("Finish Sticker ⚠️", 1, 44.6, -8),
]




def _econ_dow_chart(base_dow: dict, unit: str = "%") -> str:
    dows = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    vals = [base_dow.get(d, 0) for d in dows]
    mx = max(abs(v) for v in vals) or 1
    bars = '<div class="wc-chart"><div class="wc-mid"></div>'
    for d, v in zip(dows, vals):
        h = abs(v) / mx * 100
        pos = v >= 0
        bars += (f'<div class="wc-col" title="{d}: {v:+.1f}{unit}"><div class="wc-wrap">'
                 f'<div class="wc-bar" style="height:{h/2:.1f}%;background:{"#22c55e" if pos else "#ef4444"};{"bottom:50%" if pos else "top:50%"}"></div></div>'
                 f'<div class="wc-v {"g" if pos else "r"}">{v:+.0f}{unit}</div><div class="wc-d">{d}</div></div>')
    return bars + "</div>"


def _econ_promo_table(promo_delta: dict, n_dow_total: int, label_map: dict = None, col_label: str = "Sink mechanic") -> str:
    labels = label_map or PROMO_LABEL
    rows = sorted(promo_delta.items(), key=lambda kv: -abs(kv[1]["value"]))
    mx = max((abs(v["value"]) for _, v in rows), default=1) or 1
    trs = ""
    for key, v in rows:
        val = v["value"]
        pos = val >= 0
        col = "#22c55e" if pos else "#ef4444"
        w = abs(val) / mx * 46
        fill = f'<div class="fill {"pos" if pos else "neg"}" style="width:{w:.1f}%;background:{col}"></div>'
        basis_lbl = {"data": "n=" + str(v["n"]), "blended": "n=" + str(v["n"]) + " (thin)", "no-data": "no data yet"}.get(v["basis"], "—")
        trs += (f'<tr><td class="nm">{_esc(labels.get(key, key))}</td><td class="num">{v["n"]}</td>'
                f'<td class="num {"g" if pos else "r"}">{val:+.2f}pp</td>'
                f'<td class="track"><div class="cbar">{fill}</div></td><td class="num">{basis_lbl}</td></tr>')
    return (f'<table class="rank"><thead><tr><th>{col_label}</th><th class="num">Days seen</th>'
            f'<th class="num">Δ vs DOW baseline</th><th class="track">Size</th><th class="num">Confidence</th></tr></thead>'
            f'<tbody>{trs}</tbody></table>')


def _core_mechanic(name: str, status: str) -> str:
    s = (name or "").lower()
    st = (status or "").lower()
    if "pyp" in s or "pick your path" in s:
        return "PYP"
    if "mes" in s or "m.e.s" in s or "mega event store" in s:
        return "M.E.S"
    if "spinner clash" in s:
        return "Spinner Clash"
    if "spin zone" in s:
        return "Spin Zone"
    if "win master" in s:
        return "Win Master"
    if "ace" in s and "loot" in s:
        return "Ace Loot"
    if "card" in s and "loot" in s:
        return "Card Loot"
    if "custom pod" in s or "pod" in s:
        return "Custom Pod"
    if "jackpot" in s:
        return "Jackpot"
    if "mega winner" in s:
        return "Mega Winner"
    if "machine" in s:
        return "Gameplay machine"
    if st == "clan-dash" or "clan" in s or "dash" in s:
        return "Clan/Dash"
    if st == "core":
        return "Core challenge"
    return ""


def _core_prize_bucket(name: str) -> str:
    s = (name or "").lower()
    if "wild supreme" in s:
        return "Wild Supreme"
    if "wild any" in s:
        return "Wild Any"
    if "wild gold" in s or "wild god" in s:
        return "Wild Gold"
    if "shiny" in s:
        return "Shiny / album card"
    if "5*" in s or "5 star" in s or "5-star" in s:
        return "5-star Ace/Card"
    if "4*" in s or "4 star" in s or "4-star" in s:
        return "4-star Ace/Card"
    if "ace" in s:
        return "Ace card"
    if "card" in s or "pack" in s or "sticker" in s:
        return "Card/pack"
    if "dice" in s:
        return "Dice"
    if "hammer" in s:
        return "Hammers"
    if "jackpot" in s:
        return "Jackpot"
    if "token" in s or "step" in s:
        return "Tokens/steps"
    if "superboom" in s or "super boom" in s:
        return "Superboom"
    if "sb" in s or "slotobucks" in s:
        return "SlotoBucks"
    return "Other / unclear"


def _core_content_table() -> str:
    months = load_real_months()
    rows = {}
    for days in months.values():
        for day in days:
            iso = day.get("iso")
            for item in day.get("items", []):
                if item.get("backup"):
                    continue
                name = item.get("name", "")
                status = item.get("status", "")
                mech = _core_mechanic(name, status)
                if not mech:
                    continue
                prize = _core_prize_bucket(name)
                key = (mech, prize)
                rows.setdefault(key, {"items": 0, "days": set(), "examples": []})
                rows[key]["items"] += 1
                if iso:
                    rows[key]["days"].add(iso)
                if len(rows[key]["examples"]) < 2:
                    rows[key]["examples"].append(name)
    ordered = sorted(rows.items(), key=lambda kv: (-len(kv[1]["days"]), -kv[1]["items"], kv[0][0], kv[0][1]))[:18]
    if not ordered:
        return '<div class="warn">No Core content rows found in real_months.json.</div>'
    trs = ""
    for (mech, prize), v in ordered:
        examples = " / ".join(v["examples"])
        trs += (f'<tr><td class="nm">{_esc(mech)}</td><td>{_esc(prize)}</td>'
                f'<td class="num">{len(v["days"])}</td><td class="num">{v["items"]}</td>'
                f'<td class="nm">{_esc(examples)}</td></tr>')
    return (f'<table class="rank"><thead><tr><th>Mechanic</th><th>Reward/content bucket</th>'
            f'<th class="num">Days</th><th class="num">Items</th><th>Examples from board</th></tr></thead>'
            f'<tbody>{trs}</tbody></table>')


def _offer_family_py(name: str, status: str) -> str:
    s = (name or "").lower()
    st = (status or "").lower()
    if st == "daily deal" or s.startswith("dd") or "daily deal" in s:
        return "Daily Deal"
    if "mgap" in s or st == "mgap":
        if "bogo" in s:
            return "MGAP BOGO"
        if "matched" in s:
            return "MGAP Matched"
        if "bigger" in s:
            return "MGAP Bigger"
        if "wild symbol" in s:
            return "MGAP Wild Symbols"
        return "MGAP"
    if "buy all" in s or st == "buy all":
        return "Buy All"
    if "rolling" in s or st == "rolling offer":
        return "Rolling More-for-Less" if re.search(r"more.?for.?less|buy.?more", s) else "Rolling"
    if "decoy" in s or "bonanza" in s:
        return "Decoy/Bonanza"
    if "ryd" in s or st == "ryd":
        return "RYD"
    if "prize mania" in s or st == "prize mania":
        return "Prize Mania"
    if re.search(r"coins? sale", s):
        return "Coin Sale"
    if "gemback" in s:
        return "Boosted Gemback"
    if "ggs" in s or "gold gem stamp" in s:
        return "x2 GGS"
    if "gems sale" in s or "gem sale" in s:
        return "Gems Sale"
    if "counter po" in s or "limited po" in s:
        return "Counter PO"
    return ""


def _revenue_content_bucket(name: str) -> str:
    s = (name or "").lower()
    buckets = []
    if "hammer" in s:
        buckets.append("Hammers")
    if "superboom" in s or "super boom" in s:
        buckets.append("Superboom")
    if "wild supreme" in s:
        buckets.append("Wild Supreme")
    elif "wild any" in s:
        buckets.append("Wild Any")
    elif "wild gold" in s:
        buckets.append("Wild Gold")
    elif "wild" in s:
        buckets.append("Wild")
    if "shiny" in s:
        buckets.append("Shiny/album card")
    if "ace" in s:
        buckets.append("Ace card")
    elif "card" in s or "pack" in s or "sticker" in s:
        buckets.append("Card/pack")
    if "dice" in s:
        buckets.append("Dice")
    if "sb" in s or "slotobucks" in s:
        buckets.append("SlotoBucks")
    if "ggs" in s:
        buckets.append("GGS")
    if "rds" in s:
        buckets.append("RDS")
    if "picks" in s or "pick" in s:
        buckets.append("Picks")
    if "airstrike" in s or " as" in s:
        buckets.append("Airstrikes")
    return " + ".join(dict.fromkeys(buckets)) or "Base currency / unclear prize"


def _revenue_content_table() -> str:
    months = load_real_months()
    rows = {}
    for days in months.values():
        for day in days:
            rev = day.get("actualRev")
            if rev is None:
                continue
            iso = day.get("iso")
            for item in day.get("items", []):
                if item.get("backup"):
                    continue
                fam = _offer_family_py(item.get("name", ""), item.get("status", ""))
                if not fam:
                    continue
                bucket = _revenue_content_bucket(item.get("name", ""))
                key = (fam, bucket)
                rows.setdefault(key, {"days": set(), "revs": [], "examples": []})
                if iso not in rows[key]["days"]:
                    rows[key]["days"].add(iso)
                    rows[key]["revs"].append(rev)
                if len(rows[key]["examples"]) < 2:
                    rows[key]["examples"].append(item.get("name", ""))
    ordered = sorted(rows.items(), key=lambda kv: (-st.mean(kv[1]["revs"]), -len(kv[1]["days"])))[:18]
    trs = ""
    mx = max((st.mean(v["revs"]) for _, v in ordered), default=1) or 1
    for (fam, bucket), v in ordered:
        avg_rev = st.mean(v["revs"])
        w = avg_rev / mx * 100
        examples = " / ".join(v["examples"])
        trs += (f'<tr><td class="nm">{_esc(fam)}</td><td>{_esc(bucket)}</td>'
                f'<td class="num">{len(v["days"])}</td><td class="num g">${avg_rev/1000:.0f}K</td>'
                f'<td class="track"><div class="hbar"><div class="fill" style="width:{w:.1f}%;background:#4f9cff"></div></div></td>'
                f'<td class="nm">{_esc(examples)}</td></tr>')
    return (f'<div class="card"><div class="note">Promo + visible prize/content from real board items, ranked by average same-day DWH revenue. This is for reproducibility/context, not isolated causality; use with the v11 joint-regression table above.</div>'
            f'<table class="rank"><thead><tr><th>Promo family</th><th>Visible prize/content</th><th class="num">Days</th><th class="num">Avg rev/day</th><th class="track">Strength</th><th>Examples</th></tr></thead><tbody>{trs}</tbody></table></div>')


def render_core_perf() -> str:
    cal = load_calibration()
    econ = cal.get("economy") or {}
    if not econ or not econ.get("n_coin_days"):
        return '<div class="warn">No PU coin-balance data available for this panel — run scripts/calibrate_model.py after pulling PU balance data.</div>'
    base_dow = econ.get("coin_pct_base_dow", {})
    n_dow = econ.get("coin_pct_n_dow", {})
    promo_delta = econ.get("coin_pct_promo_delta", {})
    n_days = econ.get("n_coin_days", 0)
    cv_full = econ.get("coin_cv_full_pp")
    cv_dow = econ.get("coin_cv_dow_only_pp")
    dow_sorted = sorted(base_dow.items(), key=lambda kv: kv[1])
    lo_d, lo_v = dow_sorted[0]
    hi_d, hi_v = dow_sorted[-1]
    return (f'<div class="sec-title">🪙 Core — coin sink mechanics vs. Active PU coin velocity</div>'
            f'<div class="banner-note">Median <b>Active PU</b> balance-segment coin balance, <b>today\'s close vs yesterday\'s close</b>, pulled from <code>agg.agg_sm_daily_user_currency_balance</code> with <code>pu_segment=\'Active PU\'</code> and non-Playtika users — {n_days} real days (Apr 1 – Jul 2 2026). '
            f'<b>Why this source:</b> it matches the Velocity / Balance / Index / Consumption Tableau reference more closely than <code>daily_payments&gt;0</code>. Daily payers are useful for PU forecasting, but they bias balance movement toward purchase injection; Active PU is the more stable economy-health segment. '
            f'<b>What\'s tested against it:</b> coin-<i>sink</i> gameplay mechanics — PYP, M.E.S, Spinner Clash, Ace/Card Loot, Custom Pod, Clan Dash/points, gameplay machines, Win Master, Spin Zone, Jackpot, Mega Winner — pulled from the same DWH source and classified separately from the purchase/injection offers (Coin Sale, Buy All, MGAP) that drive the Revenue tab. Sink mechanics are what should plausibly move this metric; purchase offers inject coins rather than drain them, so they were the wrong regressor and have been removed from this tab.</div>'
            f'<div class="kpis"><div class="kpi"><div class="v g">{hi_v:+.0f}%</div><div class="l">{hi_d} — biggest PU balance growth</div></div>'
            f'<div class="kpi"><div class="v r">{lo_v:+.0f}%</div><div class="l">{lo_d} — smallest (more/newer payers dilute the median)</div></div>'
            f'<div class="kpi"><div class="v">{n_days}</div><div class="l">Real days behind this chart</div></div></div>'
            f'<div class="card"><div class="note">Day-of-week baseline — this is the strongest, best-supported signal in the data (see CV note below).</div>{_econ_dow_chart(base_dow)}</div>'
            f'<div class="card"><div class="note">Coin-sink mechanic effect on top of the DOW baseline (joint regression across Core sink mechanics, cross-validated — see <code>scripts/calibrate_model.py</code>). Values are small by design.</div>{_econ_promo_table(promo_delta, n_days, COIN_SINK_LABEL, "Coin sink mechanic")}</div>'
            f'<div class="card"><div class="note">Core content granularity from the real board: mechanics split by visible prize/content bucket. This is for planning visibility, not causal ranking — reward wording is parsed from item names, so unclear names stay marked as unclear instead of being guessed.</div>{_core_content_table()}</div>'
            f'<div class="warn">⚠️ <b>Honest finding:</b> 5-fold cross-validation shows sink-mechanic composition adds almost nothing beyond the DOW baseline for this metric — held-out error is <b>{cv_full:.1f}pp</b> with sink terms vs <b>{cv_dow:.1f}pp</b> DOW-only (basically identical). '
            f'The day-to-day variation in PU coin balance growth is mostly <b>not explained by which sink mechanics ran</b> — likely driven more by which specific payers converted that day (new vs. whale) than by the gameplay mix. Treat the deltas above as decoration, not a planning lever; the DOW pattern (Monday low, Fri/Wed high) is the real, useable signal.</div>')


def render_core_reco() -> str:
    cal = load_calibration()
    econ = cal.get("economy") or {}
    base_dow = econ.get("coin_pct_base_dow", {})
    if not base_dow:
        return ""
    dow_sorted = sorted(base_dow.items(), key=lambda kv: kv[1])
    lo_d, lo_v = dow_sorted[0]
    hi_d, hi_v = dow_sorted[-1]
    return ('<div class="card" style="border-color:#eab308">'
            '<div class="sec-sub">🎯 Recommendations — Core (coin sink)</div>'
            '<div class="grid2">'
            f'<div class="ins"><h4 style="color:#4f9cff">What the data actually supports</h4><p><b>{hi_d}</b> sees the largest PU coin-balance growth ({hi_v:+.0f}%) and <b>{lo_d}</b> the smallest ({lo_v:+.0f}%) — a day-of-week pattern, not a sink-mechanic-driven one. If coin-sink pressure is a planning goal, weight it by day of week rather than by which sink mechanic is scheduled.</p></div>'
            '<div class="ins"><h4 style="color:#ef4444">What the data does NOT support (yet)</h4><p>Cross-validation shows no reliable per-mechanic effect on PU coin balance beyond the DOW baseline with the current ~93-day sample — resist the temptation to pick a "best" sink mechanic from this data; it would be overfitting noise. Revisit once more days accumulate.</p></div>'
            '</div><div class="note">Based on real Active PU balance-segment coin data pulled from DWH (Apr–Jul 2026), tested against coin-sink gameplay mechanics (not purchase offers), cross-validated.</div></div>')


def render_gems_perf() -> str:
    cal = load_calibration()
    econ = cal.get("economy") or {}
    if not econ or not econ.get("n_gem_days"):
        return '<div class="warn">No PU gem-balance data available for this panel — run scripts/calibrate_model.py after pulling PU balance data.</div>'
    base_dow = econ.get("gem_pct_base_dow", {})
    promo_delta = econ.get("gem_pct_promo_delta", {})
    n_days = econ.get("n_gem_days", 0)
    cv_full = econ.get("gem_cv_full_pp")
    cv_dow = econ.get("gem_cv_dow_only_pp")
    dow_sorted = sorted(base_dow.items(), key=lambda kv: kv[1])
    lo_d, lo_v = dow_sorted[0]
    hi_d, hi_v = dow_sorted[-1]
    old_gems_rows = sorted(GEMS, key=lambda r: r[3], reverse=True)
    old_trs = "".join(
        f'<tr><td class="nm">{_esc(name)}</td><td class="num">{n}</td><td class="num">{usage:.1f}M</td>'
        f'<td class="num {"g" if lift >= 0 else "r"}">{lift:+d}%</td></tr>'
        for name, n, usage, lift in old_gems_rows
    )
    return (f'<div class="sec-title">💎 Gems — gem sink mechanics vs. Active PU gem velocity</div>'
            f'<div class="banner-note">Median <b>Active PU</b> balance-segment gem balance, <b>today\'s close vs yesterday\'s close</b>, pulled from <code>agg.agg_sm_daily_user_currency_balance</code> with <code>pu_segment=\'Active PU\'</code> and non-Playtika users — {n_days} real days (Apr 1 – Jul 2 2026). This follows the Velocity / Balance / Index / Consumption Tableau reference more closely than daily-payer-only balance movement. '
            f'<b>What\'s tested against it:</b> the gem-relevant planning surfaces only — <b>Short Term</b>, <b>Mid Term</b>, <b>Album</b>, and <b>Shiny Show</b>. Core coin mechanics and purchase/injection tools (Boosted Gemback, x2 GGS, Gems Sale) are deliberately excluded here because they are not the gem-sink taxonomy for monthly planning.</div>'
            f'<div class="kpis"><div class="kpi"><div class="v g">{hi_v:+.0f}%</div><div class="l">{hi_d} — biggest PU gem balance growth</div></div>'
            f'<div class="kpi"><div class="v r">{lo_v:+.0f}%</div><div class="l">{lo_d} — smallest growth</div></div>'
            f'<div class="kpi"><div class="v">{n_days}</div><div class="l">Real days behind this chart</div></div></div>'
            f'<div class="card"><div class="note">Day-of-week baseline for PU gem balance growth.</div>{_econ_dow_chart(base_dow)}</div>'
            f'<div class="card"><div class="note">Gem-sink planning-surface effect on top of the DOW baseline (Short Term / Mid Term / Album / Shiny Show only).</div>{_econ_promo_table(promo_delta, n_days, GEM_SINK_LABEL, "Gem sink")}</div>'
            f'<div class="warn">⚠️ <b>Honest finding:</b> cross-validated held-out error is <b>{cv_full:.1f}pp</b> with sink terms vs <b>{cv_dow:.1f}pp</b> DOW-only — sink-mechanic composition adds ~nothing measurable yet. The DOW pattern (Friday highest) is the real signal.</div>'
            f'<details class="card"><summary>Legacy Shiny Show variant ranking (pre-existing, small-sample, kept for reference — not yet cross-validated against PU balance)</summary>'
            f'<table class="rank" style="margin-top:10px"><thead><tr><th>Variant</th><th class="num">Days</th><th class="num">Gem usage</th><th class="num">Lift</th></tr></thead><tbody>{old_trs}</tbody></table>'
            f'<div class="note" style="margin-top:8px">This table predates the live PU balance pull and used a different, indirect gem-usage metric (not PU-segment, not balance-based) — kept only as historical reference, not as a validated ranking.</div></details>')


def render_gems_reco() -> str:
    cal = load_calibration()
    econ = cal.get("economy") or {}
    base_dow = econ.get("gem_pct_base_dow", {})
    if not base_dow:
        return ""
    dow_sorted = sorted(base_dow.items(), key=lambda kv: kv[1])
    lo_d, lo_v = dow_sorted[0]
    hi_d, hi_v = dow_sorted[-1]
    return ('<div class="card" style="border-color:#eab308">'
            '<div class="sec-sub">🎯 Recommendations — Gem Usage</div>'
            '<div class="grid2">'
            f'<div class="ins"><h4 style="color:#4f9cff">What the data actually supports</h4><p><b>{hi_d}</b> shows the strongest Active PU gem-balance growth ({hi_v:+.0f}%), <b>{lo_d}</b> the weakest ({lo_v:+.0f}%). Use the DOW rhythm as the primary planning guardrail, then layer Short/Mid/Album/Shiny according to content needs.</p></div>'
            '<div class="ins"><h4 style="color:#ef4444">What the data does NOT support (yet)</h4><p>The model should not rank unrelated Core mechanics in the Gems tab. With the current sample, Short Term / Mid Term / Album / Shiny Show effects remain small versus DOW, so treat the table as directional rather than causal.</p></div>'
            '</div><div class="note">Based on real Active PU gem balance data pulled from DWH (Apr–Jul 2026), cross-validated against the corrected gem taxonomy.</div></div>')


def render_revenue_perf() -> str:
    rows = sorted(REVENUE, key=lambda r: r[4], reverse=True)
    mx = max(r[4] for r in rows)
    trs = ""
    for disp, query, lane, n, val in rows:
        col = LANE_COLOR[lane]
        w = val / mx * 100
        trs += (f'<tr class="click" data-promo="{_esc(query)}"><td class="nm"><span class="dot" style="background:{col}"></span>{_esc(disp)}</td>'
                f'<td class="num" style="color:{col}">{lane}</td><td class="num">{n}</td><td class="num g">${val:,}</td>'
                f'<td class="track"><div class="hbar"><div class="fill" style="width:{w:.1f}%;background:{col}"></div></div></td></tr>')
    legend = "".join(f'<span><i class="dot" style="background:{c};display:inline-block;width:10px;height:10px;border-radius:3px"></i>{l}</span>' for l, c in LANE_COLOR.items())
    # prize ranking
    pr = sorted(PRIZES, key=lambda r: r[2], reverse=True)
    pmx = max(r[2] for r in pr)
    ptr = ""
    for name, n, val, note in pr:
        weak = "weak" in note.lower()
        col = "#ef4444" if weak else ("#22c55e" if "Anchor" in note or "Stable" in note else "#4f9cff")
        w = val / pmx * 100
        ptr += (f'<tr><td class="nm">{_esc(name)}</td><td class="num">{n}</td><td class="num g">${val:,}</td>'
                f'<td class="num" style="color:{col}">{_esc(note)}</td><td class="track"><div class="hbar"><div class="fill" style="width:{w:.1f}%;background:{col}"></div></div></td></tr>')
    return (f'<details class="cal-fc-card"><summary>Legacy: May–Jun promo/prize ranking (historical reference, not primary)</summary>'
            f'<div class="sec-title">💰 Legacy Revenue — Promo ranking by revenue/day</div>'
            f'<div class="kpis"><div class="kpi"><div class="v" style="color:#ec4899">$235K</div><div class="l">MGAP Bigger Multipliers</div></div>'
            f'<div class="kpi"><div class="v" style="color:#22c55e">$133K</div><div class="l">DD Hammers (n=21)</div></div>'
            f'<div class="kpi"><div class="v" style="color:#4f9cff">$132K</div><div class="l">Rolling BMFL</div></div>'
            f'<div class="kpi"><div class="v">May–Jun</div><div class="l">Legacy short sample</div></div></div>'
            f'<div class="card"><div class="note">Click a promo for offer contents (prizes by denom). Color = lane · ⭐ winner · ⛔ removed.</div>'
            f'<table class="rank"><thead><tr><th>Promo</th><th class="num">Lane</th><th class="num">Days</th><th class="num">$/day</th><th class="track">Strength</th></tr></thead><tbody>{trs}</tbody></table>'
            f'<div class="legend" style="margin-top:12px">{legend}</div></div>'
            f'<div class="sec-title">🏆 Prize ranking — strongest DD prizes</div>'
            f'<div class="card"><div class="note">Avg DD revenue/day by central prize. Shows which prizes drive revenue.</div>'
            f'<table class="rank"><thead><tr><th>Prize</th><th class="num">Days</th><th class="num">$/day</th><th>Assessment</th><th class="track">Strength</th></tr></thead><tbody>{ptr}</tbody></table></div>'
            f'<div class="grid2"><div class="ins"><h4 style="color:#22c55e">Strong prizes</h4><p><b>Hammers</b> anchor (n=21, ~$133K), <b>Superboom / Wild Supreme / SB Wheel</b> strong (~$127–133K).</p></div>'
            f'<div class="ins"><h4 style="color:#ef4444">Weak prizes</h4><p><b>Wild Any</b> (~$106K) and <b>Parasheep/AS</b> (~$105K) — ~20% below Hammers. Reduce.</p></div></div>'
            f'<div class="warn">⚠️ Legacy reference only: short sample (May–Jun), partial DD attribution (Sticky Bundle proxy), correlation not causation. Use the v11 live-calibrated table above as the primary planning source.</div></details>')


# ===== Smart Calendar × Revenue v2 — wide sample + holiday-adjusted (Nov 2025–Jul 2026, 242 days) =====
# (family, live_days, avg_daily_rev_on_live_days) — CLEAN (holiday-excluded, deduplicated), baseline = $638,427/day
# Methodology: see smart_calendar_insights.md §1 — raw (holiday-included) numbers for MGAP Bigger/Extreme Stamp were
# ~2x inflated by Black Friday/New Year/Valentine's/Cinco de Mayo confound; these are the corrected, clean values.
SC_BASELINE = 638427
SC_BASELINE_RAW = 650136  # all 242 days incl. holidays
SC_VALUE = [
    ("Custom Pod", 25, 695256), ("Coin Sale", 18, 665359), ("MGAP BOGO", 42, 660099),
    ("Decoy/Bonanza", 33, 660005), ("Rolling (other)", 94, 655812), ("Boosted Gemback", 51, 645825),
    ("Rolling More-for-Less", 31, 645657), ("MGAP (other)", 45, 644288), ("Prize Mania", 10, 643903),
    ("MGAP Bigger", 22, 641439), ("x2 GGS", 48, 639408), ("Clan Dash", 208, 638202),
    ("Extreme Stamp", 34, 637069), ("RYD", 133, 636033), ("Piggy", 24, 635643),
    ("Price Cut", 19, 633495), ("Happy Hour", 47, 632708), ("MGAP Matched", 20, 630150),
    ("MGAP Wild Symbols", 32, 620691), ("Buy All", 74, 620179), ("Golden Spin", 10, 586225),
]
# Raw (holiday-included) values for the two most confounded families — shown to illustrate the confound itself
SC_HOLIDAY_CONFOUND = [("MGAP Bigger", 731902, 641439), ("Extreme Stamp", 687414, 637069), ("Coin Sale", 730814, 665359), ("Custom Pod", 745869, 695256)]

# DAU/PU normalization (clean days, dedup) — see smart_calendar_insights.md §4
REGIME_DAU = 433_900
REGIME_PAY = 28_629
PLAN_DAU = 407_000  # Jul 2026 planning anchor (21d trail)
PLAN_PAY = 27_800
PLAN_REV = 615_000  # trailing daily net rev
CROWD_ADJ_K = -12  # additive $K vs regime baked into DOW-era mix
# (family, n, clean_Lift_%, dow_resid_$, pu_Lift_%, arpu_Lift_%)
SC_ENG_NORM = [
    ("Custom Pod", 25, 8.9, 37, 1.8, 5.5),
    ("Coin Sale", 18, 4.2, 17, 1.6, 1.6),
    ("MGAP BOGO", 42, 3.4, 15, 1.0, 1.8),
    ("Decoy/Bonanza", 32, 3.4, 19, 0.8, 2.5),
    ("Rolling (other)", 91, 2.6, 17, 0.5, 2.0),
    ("Boosted Gemback", 51, 1.2, 12, 0.2, 1.5),
    ("Golden Spin", 10, -8.2, -38, -4.6, -2.3),
    ("Buy All", 75, -2.9, -13, -0.2, -3.0),
]


def _promo_bonus_table(promo_bonus: dict, unit: str, digits: int = 1) -> str:
    rows = sorted(promo_bonus.items(), key=lambda kv: -kv[1]["value"])
    mx = max((abs(v["value"]) for _, v in rows), default=1) or 1
    trs = ""
    for key, v in rows:
        val = v["value"]
        pos = val >= 0
        col = "#22c55e" if pos else "#ef4444"
        w = abs(val) / mx * 46
        fill = f'<div class="fill {"pos" if pos else "neg"}" style="width:{w:.1f}%;background:{col}"></div>'
        basis_lbl = {"data": f'n={v["n"]}', "blended": f'n={v["n"]} (blended w/ prior)', "prior": "prior only, n=0"}.get(v["basis"], "—")
        trs += (f'<tr><td class="nm">{_esc(PROMO_LABEL.get(key, key))}</td><td class="num">{v["n"]}</td>'
                f'<td class="num {"g" if pos else "r"}">{val:+.{digits}f}{unit}</td>'
                f'<td class="track"><div class="cbar">{fill}</div></td><td class="num">{basis_lbl}</td></tr>')
    return (f'<table class="rank"><thead><tr><th>Promo family</th><th class="num">Days seen (real)</th>'
            f'<th class="num">Δ vs DOW+crowd baseline</th><th class="track">Size</th><th class="num">Confidence</th></tr></thead>'
            f'<tbody>{trs}</tbody></table>')


def _product_knowledge_table() -> str:
    kb = (load_calibration().get("product_knowledge") or {})
    families = kb.get("families") or []
    top_pairs = kb.get("top_pairs") or []
    weak_pairs = kb.get("weak_pairs") or []
    date_range = kb.get("date_range") or ["?", "?"]
    n_days = kb.get("n_clean_days", "?")

    def fam_label(key: str) -> str:
        return PROMO_LABEL.get(key, key)

    fam_rows = ""
    for r in families[:12]:
        col = "#22c55e" if r["avg_residual_k"] >= 15 else ("#ef4444" if r["avg_residual_k"] <= -10 else "#4f9cff")
        fam_rows += (f'<tr><td class="nm">{_esc(fam_label(r["key"]))}</td><td class="num">{r["n"]}</td>'
                     f'<td class="num g">${r["avg_rev_k"]:.0f}K</td><td class="num" style="color:{col}">{r["avg_residual_k"]:+.1f}K</td>'
                     f'<td class="num">{r["avg_pu"]/1000:.1f}K</td></tr>')

    def pair_rows(rows: list[dict]) -> str:
        out = ""
        for r in rows:
            names = " + ".join(fam_label(k) for k in r["keys"])
            col = "#22c55e" if r["avg_residual_k"] >= 15 else ("#ef4444" if r["avg_residual_k"] <= -10 else "#4f9cff")
            out += (f'<tr><td class="nm">{_esc(names)}</td><td class="num">{r["n"]}</td>'
                    f'<td class="num g">${r["avg_rev_k"]:.0f}K</td><td class="num" style="color:{col}">{r["avg_residual_k"]:+.1f}K</td>'
                    f'<td class="num">{r["synergy_k"]:+.1f}K</td></tr>')
        return out

    return (
        f'<div class="sec-title">🧠 Jan+ product knowledge — promos and combinations</div>'
        f'<div class="banner-note">Broad product-learning layer from <b>{date_range[0]} → {date_range[1]}</b> ({n_days} clean exact-DWH days, holidays excluded). '
        f'This is used to understand product behavior and combinations; the daily forecast still uses the shorter CV-winning windows above so it does not overfit old regimes.</div>'
        f'<div class="grid2">'
        f'<div class="card"><div class="sec-sub">Promo families — broad Jan+ read</div>'
        f'<table class="rank"><thead><tr><th>Family</th><th class="num">Days</th><th class="num">Avg rev</th><th class="num">vs DOW+month</th><th class="num">Avg PU</th></tr></thead><tbody>{fam_rows}</tbody></table></div>'
        f'<div class="card"><div class="sec-sub">Strong combinations — directional</div>'
        f'<table class="rank"><thead><tr><th>Combination</th><th class="num">Days</th><th class="num">Avg rev</th><th class="num">vs baseline</th><th class="num">Combo edge</th></tr></thead><tbody>{pair_rows(top_pairs[:8])}</tbody></table></div>'
        f'</div>'
        f'<details class="card"><summary>Risky / weak combinations to avoid or use only intentionally</summary>'
        f'<table class="rank" style="margin-top:10px"><thead><tr><th>Combination</th><th class="num">Days</th><th class="num">Avg rev</th><th class="num">vs baseline</th><th class="num">Combo edge</th></tr></thead><tbody>{pair_rows(weak_pairs[:8])}</tbody></table>'
        f'<div class="note" style="margin-top:8px">Combo edge = pair residual minus the average residual of the two families separately. It is an interaction signal, not proof of causality, because daily plans still include multiple overlapping levers.</div></details>'
    )


def render_sc_value() -> str:
    cal = load_calibration()
    rev_cal = cal.get("revenue") or {}
    pu_cal = cal.get("pu") or {}
    meta = cal.get("meta") or {}
    live_section = ""
    if rev_cal.get("promo_bonus"):
        cv_err = meta.get("self_check_mean_abs_pct_error")
        n_rev = meta.get("n_revenue_days", "?")
        n_pu = meta.get("n_pu_days", "?")
        rev_window = meta.get("revenue_window_days", "?")
        pu_window = meta.get("pu_window_days", "?")
        pu_cv = meta.get("pu_self_check_mean_abs_pct_error")
        live_section = (
            f'<div class="sec-title">🔄 Live-calibrated promo value (v11, cross-validated forecast)</div>'
            f'<div class="banner-note">This <b>replaces</b> the static table below as the primary promo-value reference. Computed fresh every pipeline run by <code>scripts/calibrate_model.py</code> from <b>{n_rev} real revenue days</b> (trailing {rev_window}d) and <b>{n_pu} real PU days</b> (trailing {pu_window}d), pulled directly from <code>dwh.sm_fact_smart_calendar_promotion_updates</code> × <code>agg.agg_sm_daily_users_stats</code> (not just the Monday-board window) — a joint (multivariate) regression across all promo types at once, cross-validated (revenue held-out accuracy ±{cv_err}%, PU ±{pu_cv}%). '
            f'The broader Jan+ knowledge base below is for product learning and combinations; this forecast table intentionally keeps the CV-winning shorter windows.</div>'
            f'<div class="card"><div class="note">Revenue Δ vs that day\'s DOW+crowd baseline ($K/day).</div>{_promo_bonus_table(rev_cal["promo_bonus"], "K", 1)}</div>'
            + (f'<div class="card"><div class="note">Payer (PU) count Δ vs that day\'s DOW+crowd baseline (%).</div>{_promo_bonus_table(pu_cal["promo_bonus"], "%", 2)}</div>' if pu_cal.get("promo_bonus") else "")
            + '<div class="warn">⚠️ Most promos now have 10-40+ real days behind them (was 0-24) — check the "Days seen" column per promo. A couple of newer/rarer types (Fortune Dip, SNL) are still thin and lean on documented literature priors.</div>'
        )
    rows = sorted(SC_VALUE, key=lambda r: r[2], reverse=True)
    mx = max(abs(r[2] - SC_BASELINE) for r in rows)
    trs = ""
    for fam, n, val in rows:
        Lift = (val - SC_BASELINE) / SC_BASELINE * 100
        col = "#22c55e" if Lift >= 3 else ("#4f9cff" if Lift >= 0 else "#ef4444")
        w = abs(val - SC_BASELINE) / mx * 100
        sign = "+" if Lift >= 0 else ""
        trs += (f'<tr><td class="nm">{_esc(fam)}</td><td class="num">{n}</td><td class="num g">${val:,}</td>'
                f'<td class="num" style="color:{col}">{sign}{Lift:.1f}%</td>'
                f'<td class="track"><div class="hbar"><div class="fill" style="width:{w:.1f}%;background:{col}"></div></div></td></tr>')
    conf_tr = ""
    for fam, raw, clean in SC_HOLIDAY_CONFOUND:
        raw_Lift = (raw / SC_BASELINE_RAW - 1) * 100
        clean_Lift = (clean / SC_BASELINE - 1) * 100
        conf_tr += (f'<tr><td class="nm">{_esc(fam)}</td><td class="num">${raw:,} ({raw_Lift:+.1f}%)</td>'
                    f'<td class="num g">${clean:,} ({clean_Lift:+.1f}%)</td></tr>')
    return (live_section
            + '<details class="cal-fc-card"><summary>Legacy: Smart Calendar × Revenue v2.1 — Nov 2025–Jul 2026 242-day snapshot (historical reference, not auto-updating)</summary>'
            + f'<div class="sec-title">🧭 Smart Calendar × Revenue v2.1 — Wide sample + holiday-clean + DAU/PU</div>'
            f'<div class="kpis"><div class="kpi"><div class="v">$638K</div><div class="l">Holiday-clean baseline (234 days)</div></div>'
            f'<div class="kpi"><div class="v">{PLAN_DAU/1000:.0f}K</div><div class="l">DAU anchor (trail) vs {REGIME_DAU/1000:.0f}K in window</div></div>'
            f'<div class="kpi"><div class="v">{PLAN_PAY/1000:.1f}K</div><div class="l">PU anchor vs {REGIME_PAY/1000:.1f}K · ARPU ↑ partially offsets</div></div>'
            f'<div class="kpi"><div class="v" style="color:#22c55e">+8.9%</div><div class="l">Custom Pod — also +PU + ARPU (§4)</div></div></div>'
            f'<div class="card"><div class="note">Source of truth: <b>dwh.sm_fact_smart_calendar_promotion_updates</b> (latest version/promo · live-at-snapshot · dedup · <b>excluding 8 holiday days</b>: Black Friday/NY/Valentine\'s/Cinco de Mayo/4.4/St.Patrick\'s). '
            f'Per promo family: clean daily revenue vs $638K baseline. Details: <code>mm_calendar/smart_calendar_insights.md</code>.</div>'
            f'<table class="rank"><thead><tr><th>Promo family</th><th class="num">Live days</th><th class="num">Rev/day (clean)</th><th class="num">vs baseline</th><th class="track">Strength</th></tr></thead><tbody>{trs}</tbody></table></div>'
            f'<div class="sec-title">👥 DAU / PU normalization — DOW-matched residual</div>'
            f'<div class="card"><div class="note">Removes weekday bias; <b>ΔPU</b> = change in payers vs same-weekday avg · <b>ΔARPU</b> = % change in rev/DAU. This legacy section is historical context only; v11 forecast values above are recomputed daily. Details: <code>smart_calendar_insights.md</code> §4.</div>'
            f'<table class="rank"><thead><tr><th>Family</th><th class="num">n</th><th class="num">Clean lift</th><th class="num">Residual $</th><th class="num">ΔPU</th><th class="num">ΔARPU</th></tr></thead><tbody>'
            + "".join(
                f'<tr><td class="nm">{_esc(f)}</td><td class="num">{n}</td><td class="num">{cl:+.1f}%</td>'
                f'<td class="num g">{dr:+.0f}K</td><td class="num">{pu:+.1f}%</td><td class="num">{ar:+.1f}%</td></tr>'
                for f, n, cl, dr, pu, ar in SC_ENG_NORM
            )
            + '</tbody></table></div>'
            f'<div class="sec-title">⚠️ Holiday confound — raw vs clean</div>'
            f'<div class="card"><div class="note">Promos that looked much stronger before holiday cleaning — mostly Black Friday / NY / Valentine\'s, not the promo itself.</div>'
            f'<table class="rank"><thead><tr><th>Family</th><th class="num">raw (with holidays)</th><th class="num">clean (no holidays)</th></tr></thead><tbody>{conf_tr}</tbody></table></div>'
            f'<div class="grid2"><div class="ins"><h4 style="color:#22c55e">True standalone winners</h4><p><b>Custom Pod</b> and <b>Coin Sale</b> — strong after holidays and on <b>+PU/+ARPU</b> (not just ARPPU on a smaller base). '
            f'<b>MGAP BOGO (+3.4%)</b> strongest MGAP variant.</p></div>'
            f'<div class="ins"><h4 style="color:#4f9cff">Audience + forecast</h4><p>DAU/PU down ~1–3%/month in the broad historical window; v11 now handles this via rolling DWH windows and current-month trend extrapolation. '
            f'<b>Golden Spin</b> weak on $ and PU (−4.6%). Extreme Stamp/MGAP Bigger — event toppers, not weekday anchors.</p></div></div>'
            f'<div class="warn">⚠️ Day-level correlation: multiple families live together. After holiday-clean + dedup, range is modest (±3–9%) — more realistic than raw estimates.</div>'
            + '</details>')


# ===== Deep relationships (data-grounded, Apr1–Jul2 2026) =====
DOW_DATA = [  # (day, rev, payers, arppu, note, color) — v2: 242 days (Nov 2025–Jul 2026), holidays included
    ("Sun", 641096, 29111, 22.0, "Stable", "#4f9cff"),
    ("Mon", 645891, 35919, 18.0, "Payer peak · breadth (Dash/Monday)", "#22c55e"),
    ("Tue", 599581, 26969, 22.2, "Weakest", "#ef4444"),
    ("Wed", 641823, 27969, 22.9, "Piggy", "#4f9cff"),
    ("Thu", 622640, 25952, 24.0, "Weak (Golden Spin often here)", "#ef4444"),
    ("Fri", 692534, 27715, 25.0, "Ramp to weekend", "#4f9cff"),
    ("Sat", 709507, 28015, 25.3, "Revenue peak · real depth/sale (Custom Pod/Coin Sale)", "#22c55e"),
]
WOM_DATA = [  # (label, rev, conv, note) — v2: 242 days
    ("Week 1 (1–7)", 671329, 6.78, "Strongest — but gap more modest vs v1"),
    ("Week 2 (8–14)", 654068, 6.63, "Strong"),
    ("Week 3 (15–21)", 632181, 6.55, "Monthly trough (−6% vs week 1, not −11%)"),
    ("Week 4 (22–28)", 641257, 6.57, "Recovery"),
    ("Week 5 (29+, partial)", 653273, 6.75, "End of month"),
]
CONN_DATA = [  # (segment, users, pct_dau, conv, rev, pct_rev)
    ("Daily", 321003, 79, 7.8, 680915, 90),
    ("Bi-daily", 33270, 8, 5.7, 42027, 5.5),
    ("Twice a week", 18746, 5, 5.7, 21432, 2.8),
    ("New / unclassified", 26214, 6, 2.7, 9509, 1.2),
    ("Weekly", 5885, 1, 5.8, 6387, 0.8),
    ("Occasional", 1825, 1, 6.1, 1853, 0.2),
]


# v2 (holiday-adjusted): Custom Pod/Coin Sale/MGAP BOGO are the genuine standalone winners.
# Extreme Stamp/MGAP Bigger were downgraded here — their apparent strength was mostly a holiday confound
# (see smart_calendar_insights.md §1); they're still valid as *toppers on real event days* (handled by day.tag=="event"),
# just no longer counted as a standalone "depth anchor" for an ordinary Saturday.
DEPTH_PROMOS = ["coin sale", "custom pod", "mgap bogo"]
TROUGH_WEEK_IDX0 = 2  # Week 3 (days 15–21) = empirical trough (relationships_deep.md)


def compute_calendar_audit():
    """Run validate_calendar on live canvas + measure fit to DWH day-of-week / week-of-month patterns."""
    days = vcal.parse_days()
    violations, coverage = vcal.audit(days)

    def wk(d):
        return (d - 1) // 7

    sat_hits, mon_ok, tue_hits, thu_hits = [], 0, [], []
    week_depth = {}
    for d in days:
        low = [i.lower() for i in d["items"]]
        hit = [k for k in DEPTH_PROMOS if any(k in i for i in low)]
        w = wk(d["date"])
        week_depth.setdefault(w, [0, 0])
        week_depth[w][1] += 1
        if hit:
            week_depth[w][0] += 1
        if d["dow"] == "Sat":
            sat_hits.append((d["date"], hit))
        elif d["dow"] == "Mon":
            if not hit and any("dash" in i or "monday max" in i for i in low):
                mon_ok += 1
        elif d["dow"] == "Tue":
            tue_hits.append((d["date"], hit))
        elif d["dow"] == "Thu":
            thu_hits.append((d["date"], hit))

    sat_total = len(sat_hits)
    sat_anchored = sum(1 for _, h in sat_hits if h)
    sat_gap = [d for d, h in sat_hits if not h]
    mon_total = sum(1 for d in days if d["dow"] == "Mon")
    week_rows = []
    for w in sorted(week_depth):
        n_depth, n_days = week_depth[w]
        week_rows.append((w + 1, n_depth, n_days))
    trough_ggs = coverage["ggs_week"].get(TROUGH_WEEK_IDX0, 0)
    return {
        "n_days": len(days),
        "violations": violations,
        "rules_checked": vcal.RULES_CHECKED,
        "sat_total": sat_total, "sat_anchored": sat_anchored, "sat_gap": sat_gap,
        "mon_total": mon_total, "mon_ok": mon_ok,
        "tue_hits": tue_hits, "thu_hits": thu_hits,
        "week_rows": week_rows, "trough_ggs": trough_ggs,
    }


def render_calendar_audit() -> str:
    a = compute_calendar_audit()
    v_ok = not a["violations"]
    v_col = "#22c55e" if v_ok else "#ef4444"
    v_txt = "0 violations ✅" if v_ok else f"{len(a['violations'])} violations ⚠️"
    sat_col = "#22c55e" if a["sat_anchored"] == a["sat_total"] else "#eab308"
    mon_col = "#22c55e" if a["mon_ok"] == a["mon_total"] else "#ef4444"
    week_tr = ""
    trough_w = 3  # Week 3 = historical trough per relationships_deep.md
    for w, nd, ntot in a["week_rows"]:
        mark = " ⬅ historical trough — strengthen" if w == trough_w else ""
        col = "#eab308" if w == trough_w else "#4f9cff"
        week_tr += (f'<tr><td class="nm">Week {w}{mark}</td><td class="num">{nd}/{ntot}</td>'
                    f'<td class="track"><div class="hbar"><div class="fill" style="width:{nd/ntot*100:.0f}%;background:{col}"></div></div></td></tr>')
    sat_line = (f'<b>All {a["sat_total"]} Saturdays</b> have a real depth anchor (Coin Sale / Custom Pod / MGAP BOGO) ✅ — matches Sat = empirical revenue peak ($710K). '
                f'(Fixed: day 11 Custom Pod X1300; day 4 MGAP Bigger → BOGO.)') if a["sat_anchored"] == a["sat_total"] else (
                f'<b>Saturday {", ".join(str(d) for d in a["sat_gap"])}</b> missing real depth — Sat is empirical peak ($710K); prefer Coin Sale / Custom Pod / MGAP BOGO (not Extreme Stamp/Bigger — conditional toppers, see smart_calendar_insights.md §1).')
    week3_line = (f'<b>Week 3 (15–21 Aug)</b> is the historical trough ($632K/day, −6% vs week 1); reinforced with {a["trough_ggs"]} x2 GGS days (day 17) plus normal depth density.')
    return (
        f'<div class="sec-title">✅ Validation + data-pattern fit — August 2026 (242-day wide sample, holiday-clean)</div>'
        f'<div class="kpis">'
        f'<div class="kpi"><div class="v" style="color:{v_col}">{v_txt}</div><div class="l">{a["rules_checked"]} HARD rules checked · {a["n_days"]} Days (validate_calendar.py)</div></div>'
        f'<div class="kpi"><div class="v" style="color:{sat_col}">{a["sat_anchored"]}/{a["sat_total"]}</div><div class="l">Saturdays with real depth anchor (Coin Sale/Custom Pod/MGAP BOGO)</div></div>'
        f'<div class="kpi"><div class="v" style="color:{mon_col}">{a["mon_ok"]}/{a["mon_total"]}</div><div class="l">Mondays = pure breadth (Dash, no MGAP/Sale) — matches DWH</div></div>'
        f'<div class="kpi"><div class="v">242 Days</div><div class="l">Source: Smart Calendar × live revenue, 8 holidays excluded (baseline $638K)</div></div>'
        f'</div>'
        f'<div class="grid2">'
        f'<div class="card"><div class="sec-sub">🗓️ Depth days per week (vs week 3 = historical trough)</div>'
        f'<table class="rank"><thead><tr><th>Week</th><th class="num">Depth days</th><th class="track"></th></tr></thead><tbody>{week_tr}</tbody></table></div>'
        f'<div class="ins"><h4 style="color:#eab308">🎯 Audit status (updated)</h4>'
        f'<p>1. {sat_line}</p>'
        f'<p>2. {week3_line}</p>'
        f'<p>3. <b>Mondays</b> ({a["mon_ok"]}/{a["mon_total"]}) stay 100% breadth (Dash only, no MGAP/Sale) — matches DWH (Mon = payer peak, lower ARPPU).</p></div>'
        f'</div>'
        f'<div class="note">Audit source: <code>validate_calendar.py</code> (canvas-sensitive — re-runs every build) + <code>relationships_deep.md</code> (dow/week-of-month from DWH).</div>')


DOM_LABEL = {"b1": "Days 1-2 (month-open)", "b2": "Days 3-7 (week 1)", "b3": "Days 8-14 (week 2)",
             "b4": "Days 15-21 (week 3)", "b5": "Days 22-28 (week 4)", "b6": "Month-end"}


def render_planning_insights() -> str:
    cal = load_calibration()
    rev = cal.get("revenue") or {}
    pu = cal.get("pu") or {}
    econ = cal.get("economy") or {}
    meta = cal.get("meta") or {}
    if not rev.get("day_of_month_curve"):
        return ""

    dom = rev["day_of_month_curve"]
    dom_rows = "".join(
        f'<tr><td class="nm">{DOM_LABEL.get(k, k)}</td><td class="num">{v["n"]}</td>'
        f'<td class="num {"g" if v["value"] >= 0 else "r"}">{v["value"]:+.0f}K</td></tr>'
        for k, v in dom.items()
    )
    best_dom = max(dom.items(), key=lambda kv: kv[1]["value"])
    worst_dom = min(dom.items(), key=lambda kv: kv[1]["value"])

    rev_dow = rev.get("base_dow", {})
    pu_dow = pu.get("base_dow", {})
    weak_rev_days = sorted(rev_dow.items(), key=lambda kv: kv[1])[:2]
    strong_rev_days = sorted(rev_dow.items(), key=lambda kv: -kv[1])[:2]

    trend_rev = list((rev.get("crowd_trend_per_day") or {}).values())
    trend_rev = trend_rev[0] if trend_rev else None
    trend_pu = list((pu.get("crowd_trend_per_day") or {}).values())
    trend_pu = trend_pu[0] if trend_pu else None
    cur_month = meta.get("current_month", "current month")

    trend_line = ""
    if trend_rev is not None:
        rev_dir = "declining" if trend_rev < 0 else "rising"
        pu_dir = "declining" if (trend_pu or 0) < 0 else "rising (recent short-term signal)"
        trend_line = (
            f'<p><b>Base is moving, not flat:</b> the trailing-real-days trend for {cur_month} shows revenue {rev_dir} '
            f'~${abs(trend_rev):.2f}K/day and PU {pu_dir} ~{abs(trend_pu or 0):.0f}/day. '
            f'These are short (~21-day) extrapolations, not the full documented multi-month decline — treat the PU uptick cautiously; it can reverse. '
            f'Either way, <b>flat monthly targets understate the shape of the month</b> — plan day-by-day, not off a single monthly average.</p>'
        )

    return (
        f'<div class="sec-title">🗓️ Monthly planning — what the data actually says</div>'
        f'<div class="banner-note">Computed fresh from {meta.get("n_revenue_days","?")} real revenue days (trailing {meta.get("revenue_window_days","?")}-day revenue window, currently {" → ".join(meta.get("revenue_date_range") or meta.get("date_range") or ["?","?"])}) every pipeline run — see <code>scripts/calibrate_model.py</code>\'s <code>compute_day_of_month_curve</code> and DOW baselines. This directly replaces guesswork about "week 1 is strong" / "week 3 is the trough" with a measured, cross-validated shape.</div>'
        f'<div class="grid2">'
        f'<div class="card"><div class="sec-sub">Day-of-month revenue curve (Δ vs DOW+crowd baseline)</div>'
        f'<table class="rank"><thead><tr><th>Period</th><th class="num">Real days</th><th class="num">Δ vs baseline</th></tr></thead><tbody>{dom_rows}</tbody></table></div>'
        f'<div class="ins"><h4 style="color:#eab308">🎯 The month has one real peak, not two</h4>'
        f'<p><b>{DOM_LABEL.get(best_dom[0])}</b> is the only period meaningfully above baseline (<b>{best_dom[1]["value"]:+.0f}K</b>). '
        f'Every other period of the month runs flat-to-negative, including <b>{DOM_LABEL.get(worst_dom[0])}</b> at <b>{worst_dom[1]["value"]:+.0f}K</b> — the real trough. '
        f'This contradicts the older assumption that week 1 is a second strong period: the data now shows it running <i>below</i> baseline once month-open is separated out. '
        f'<b>Planning implication:</b> if a headline promo is being held back for "week 1 momentum," the data says that momentum isn\'t there — consider whether it would do more good reinforcing month-open (already the peak, compounding a strong start) or countering the month-end dip (where every $ has to fight a structural −{abs(worst_dom[1]["value"]):.0f}K headwind).</p></div>'
        f'</div>'
        f'<div class="grid2">'
        f'<div class="ins"><h4 style="color:#4f9cff">Day-of-week isn\'t just a revenue pattern</h4>'
        f'<p><b>{strong_rev_days[0][0]}/{strong_rev_days[1][0]}</b> are the strongest revenue days (${strong_rev_days[0][1]:.0f}K/${strong_rev_days[1][1]:.0f}K); '
        f'<b>{weak_rev_days[0][0]}/{weak_rev_days[1][0]}</b> the weakest (${weak_rev_days[0][1]:.0f}K/${weak_rev_days[1][1]:.0f}K). '
        f'<b>Monday</b> has by far the most payers ({pu_dow.get("Mon",0):,.0f} PU) but the <i>lowest</i> PU coin-balance growth ({econ.get("coin_pct_base_dow",{}).get("Mon",0):+.0f}% vs {econ.get("coin_pct_base_dow",{}).get("Fri",0):+.0f}% on Friday) — consistent with Monday\'s payer mix skewing toward smaller/newer converters (Dash Day breadth), not depth. Don\'t schedule your biggest single-ticket offer expecting Monday\'s ARPU to match Saturday\'s.</p></div>'
        f'<div class="ins"><h4 style="color:#a855f7">Trend, not just level</h4>{trend_line}</div>'
        f'</div>'
    )


def render_growth_vs_economy_insights() -> str:
    cal = load_calibration()
    rev = cal.get("revenue") or {}
    pu = cal.get("pu") or {}
    econ = cal.get("economy") or {}
    rev_b = rev.get("promo_bonus") or {}
    pu_b = pu.get("promo_bonus") or {}
    coin_b = econ.get("coin_pct_promo_delta") or {}
    gem_b = econ.get("gem_pct_promo_delta") or {}
    if not (rev_b and coin_b):
        return ""
    dual_keys = sorted(set(rev_b) & set(coin_b), key=lambda k: -rev_b[k]["value"])  # e.g. customPod: both an offer AND a sink mechanic
    top_offers = sorted(rev_b.items(), key=lambda kv: -kv[1]["value"])[:4]
    bot_offers = sorted(rev_b.items(), key=lambda kv: kv[1]["value"])[:2]
    top_sinks = sorted(coin_b.items(), key=lambda kv: -kv[1]["value"])[:3]
    dual_rows = "".join(
        f'<tr><td class="nm">{_esc(SINK_LABEL.get(k, PROMO_LABEL.get(k, k)))}</td>'
        f'<td class="num {"g" if rev_b[k]["value"]>=0 else "r"}">{rev_b[k]["value"]:+.1f}K</td>'
        f'<td class="num {"g" if pu_b.get(k,{}).get("value",0)>=0 else "r"}">{pu_b.get(k,{}).get("value",0):+.2f}%</td>'
        f'<td class="num {"g" if coin_b[k]["value"]>=0 else "r"}">{coin_b[k]["value"]:+.2f}pp</td>'
        f'<td class="num {"g" if gem_b.get(k,{}).get("value",0)>=0 else "r"}">{gem_b.get(k,{}).get("value",0):+.2f}pp</td></tr>'
        for k in dual_keys
    )
    return (
        f'<div class="sec-title">⚖️ Can PU / Revenue grow without hurting the economy?</div>'
        f'<div class="banner-note"><b>Important correction:</b> revenue/PU-driving <i>offers</i> (Coin Sale, MGAP, Rolling, Buy All — purchase/injection mechanics) and coin/gem-<i>sink</i> mechanics (PYP, Dash, Shiny Show — gameplay features that consume currency) are classified from largely <b>different, non-overlapping promo vocabularies</b> — see the Core/Gems tabs for why offers were the wrong regressor there. '
        f'That means there usually isn\'t a direct "this exact promo\'s revenue lift vs. its own economy cost" comparison to make — they\'re different levers. <b>{"Custom Pod is the one exception" if dual_keys else "No promo currently appears in both taxonomies"}</b>: it\'s structured as a coin-sink tool that\'s also sold as a purchase, so it\'s the one lever with a real dual-signal reading.</div>'
        + (f'<div class="card"><table class="rank"><thead><tr><th>Dual-purpose lever</th><th class="num">Revenue Δ</th><th class="num">PU Δ</th><th class="num">PU coin bal. Δ</th><th class="num">PU gem bal. Δ</th></tr></thead><tbody>{dual_rows}</tbody></table></div>' if dual_keys else "")
        + f'<div class="grid2">'
        f'<div class="ins"><h4 style="color:#22c55e">Revenue/PU side: what\'s actually driving growth</h4>'
        f'<p>Top offers by revenue lift: ' + ", ".join(f'<b>{_esc(PROMO_LABEL.get(k,k))}</b> ({v["value"]:+.1f}K)' for k, v in top_offers) + '. '
        f'Weakest: ' + ", ".join(f'<b>{_esc(PROMO_LABEL.get(k,k))}</b> ({v["value"]:+.1f}K)' for k, v in bot_offers) + '.</p></div>'
        f'<div class="ins"><h4 style="color:#a855f7">Economy side: what plausibly drains coins</h4>'
        f'<p>Top coin-sink mechanics by (small, mostly-noise) coin-velocity delta: ' + ", ".join(f'<b>{_esc(SINK_LABEL.get(k,k))}</b> ({v["value"]:+.2f}pp, n={v["n"]})' for k, v in top_sinks) + '. '
        f'Per the Core tab\'s cross-validation, none of these reliably beat day-of-week yet — treat as directional, not a lever to pull.</p></div>'
        f'</div>'
        + (f'<div class="ins" style="margin-top:12px"><h4 style="color:#4f9cff">The one dual-purpose lever</h4>'
           f'<p><b>Custom Pod</b> is both the strongest revenue offer ({rev_b.get("customPod",{}).get("value",0):+.1f}K) and one of the few sink mechanics with a flat-to-negative coin-balance reading ({coin_b.get("customPod",{}).get("value",0):+.2f}pp) — consistent with how it\'s structured (a coin sink that\'s sold, not a coin-injection tool). That\'s the closest thing to a "grows revenue without inflating balances" signal in the data, though with the same small-sample caveat as everything else in the economy model.</p></div>' if "customPod" in dual_keys else "")
        + f'<div class="ins" style="margin-top:12px"><h4 style="color:#eab308">The honest overall answer</h4>'
        f'<p>Because revenue-driving offers and coin/gem-sink mechanics are largely separate scheduling decisions, <b>growing revenue/PU via offer selection doesn\'t mechanically require changing which sink mechanics run</b> — the two are planned somewhat independently already. Combined with the Core/Gems finding that sink-mechanic choice barely moves the PU balance metric beyond day-of-week anyway, the defensible conclusion is: <b>there\'s no visible near-term economy cost to optimizing the offer mix for revenue/PU</b> — not because a clean trade-off was found and avoided, but because the data doesn\'t show promo-level decisions on either side moving the economy metric much at all. Re-check this if payment or spend velocity ever shows real strain.</p></div>'
    )


def _backtest_sink_hits(day: dict, keys: list[str]) -> list[str]:
    statuses = {s.get("status") for s in day.get("seasons", [])}
    names = [it.get("name", "") for it in day.get("items", []) if not it.get("backup")]
    hits = []
    for key in keys:
        if key == "shortTerm" and "Short Term" in statuses:
            hits.append(key)
        elif key == "midTerm" and "Mid Term" in statuses:
            hits.append(key)
        elif key == "album" and "Album" in statuses:
            hits.append(key)
        elif key == "shinyShow" and any("shiny" in n.lower() for n in names):
            hits.append(key)
        elif key in COIN_SINK_LABEL and any(_core_mechanic(n, "") == key for n in names):
            hits.append(key)
    return hits


def _economy_backtest_rows() -> dict:
    months = load_real_months()
    econ = (load_calibration().get("economy") or {})
    coin_bonus = econ.get("coin_pct_promo_delta") or {}
    gem_bonus = econ.get("gem_pct_promo_delta") or {}
    out = {"coin": [], "gem": []}
    for month_key in ("2026-04", "2026-05", "2026-06"):
        for day in months.get(month_key, []):
            dow = day.get("dow")
            if day.get("coinSource") == "active_pu_balance_dwh" and day.get("coinMagnitude") is not None:
                pred = (econ.get("coin_pct_base_dow") or {}).get(dow)
                if pred is not None:
                    hits = _backtest_sink_hits(day, list(coin_bonus))
                    pred += sum((coin_bonus.get(k) or {}).get("value", 0) for k in hits)
                    out["coin"].append({"iso": day["iso"], "dow": dow, "pred": pred, "actual": day["coinMagnitude"], "hits": hits})
            if day.get("gemSource") == "active_pu_balance_dwh" and day.get("gemMagnitude") is not None:
                pred = (econ.get("gem_pct_base_dow") or {}).get(dow)
                if pred is not None:
                    hits = _backtest_sink_hits(day, list(gem_bonus))
                    pred += sum((gem_bonus.get(k) or {}).get("value", 0) for k in hits)
                    out["gem"].append({"iso": day["iso"], "dow": dow, "pred": pred, "actual": day["gemMagnitude"], "hits": hits})
    return out


def render_economy_backtest() -> str:
    rows = _economy_backtest_rows()
    cards = ""
    detail_blocks = ""
    for metric, label, color in (("coin", "Coin balance velocity", "#f59e0b"), ("gem", "Gem balance velocity", "#a855f7")):
        rs = rows[metric]
        if not rs:
            continue
        abs_err = [abs(r["actual"] - r["pred"]) for r in rs]
        bias = st.mean([r["actual"] - r["pred"] for r in rs])
        dir_ok = sum(
            (r["actual"] >= 5 and r["pred"] >= 5) or
            (r["actual"] <= -5 and r["pred"] <= -5) or
            (-5 < r["actual"] < 5 and -5 < r["pred"] < 5)
            for r in rs
        )
        monthly = []
        for month_key in ("2026-04", "2026-05", "2026-06"):
            mrs = [r for r in rs if r["iso"].startswith(month_key)]
            if not mrs:
                continue
            monthly.append(f'{month_key[-2:]}: {st.mean(abs(r["actual"] - r["pred"]) for r in mrs):.1f}pp')
        cards += (f'<div class="kpi"><div class="v" style="color:{color}">{st.mean(abs_err):.1f}pp</div>'
                  f'<div class="l">{label} MAE · Apr-Jun ({", ".join(monthly)})</div></div>'
                  f'<div class="kpi"><div class="v" style="color:{color}">{dir_ok/len(rs):.0%}</div>'
                  f'<div class="l">{label} direction hit-rate · bias {bias:+.1f}pp</div></div>')
        worst = sorted(rs, key=lambda r: abs(r["actual"] - r["pred"]), reverse=True)[:8]
        trs = ""
        for r in worst:
            err = r["actual"] - r["pred"]
            hits = ", ".join(_esc(SINK_LABEL.get(k, k)) for k in r["hits"]) or "DOW only"
            trs += (f'<tr><td class="nm">{r["iso"]}</td><td>{r["dow"]}</td><td class="num">{r["pred"]:+.1f}%</td>'
                    f'<td class="num">{r["actual"]:+.1f}%</td><td class="num {"g" if abs(err) <= st.mean(abs_err) else "r"}">{err:+.1f}pp</td>'
                    f'<td>{hits}</td></tr>')
        detail_blocks += (f'<details class="card"><summary>{label}: worst Apr-Jun daily misses</summary>'
                          f'<table class="rank" style="margin-top:10px"><thead><tr><th>Date</th><th>DOW</th><th class="num">Pred</th><th class="num">Actual</th><th class="num">Error</th><th>Detected sinks/surfaces</th></tr></thead><tbody>{trs}</tbody></table></details>')
    return (f'<div class="sec-title">📉 Economy forecast backtest — Apr/May/Jun daily actuals</div>'
            f'<div class="kpis">{cards}</div>'
            f'<div class="warn"><b>What this means:</b> gem velocity is usable directionally; coin velocity is much noisier day-to-day. I tested a previous-day mean-reversion correction and it improved coin MAE only marginally (~0.2pp), so the safer model decision is not to overfit it. For planning, use the predicted balance % as a <b>risk band</b>, not as an exact daily outcome: coin days need roughly ±8pp tolerance, gem days ±4pp.</div>'
            f'{detail_blocks}')


def render_august_recommendations() -> str:
    a = compute_calendar_audit()
    return (
        f'<div class="sec-title">🗓️ August recommendations — improve result without stressing economy</div>'
        f'<div class="grid2">'
        f'<div class="ins"><h4 style="color:#22c55e">1. Keep depth on Saturdays, add breadth to weak weekdays</h4>'
        f'<p>Saturdays should stay anchored with real depth (Custom Pod / Coin Sale / MGAP BOGO). Tue/Thu are weaker revenue days; use breadth or value mechanics there rather than burning the best depth anchors. Current hard-rule audit: <b>{len(a["violations"])} violations</b> across {a["rules_checked"]} checks.</p></div>'
        f'<div class="ins"><h4 style="color:#4f9cff">2. Fix Week 3 risk</h4>'
        f'<p>15–21 Aug is the historical trough. Add or protect at least one stronger revenue/PU lever around 17 Aug, preferably x2 GGS / Rolling More-for-Less / Boosted Gemback if it fits CRM and economy guidelines.</p></div>'
        f'<div class="ins"><h4 style="color:#a855f7">3. Gems: plan around surfaces, not random “gem promos”</h4>'
        f'<p>Gem planning should be Short Term / Mid Term / Album / Shiny Show only. Place gem amplifiers near real gem demand surfaces; do not treat unrelated purchase offers as gem sinks.</p></div>'
        f'<div class="ins"><h4 style="color:#f59e0b">4. Economy guardrail</h4>'
        f'<p>Because Apr-Jun backtest shows coin velocity is noisy, do not react to a single predicted coin %. Use the tolerance band: if several adjacent August days stack positive coin velocity and no real coin sink, add/strengthen PYP / Spin Zone / M.E.S content; if coin velocity is already negative, avoid adding another heavy sink.</p></div>'
        f'</div>'
    )


def render_relationships() -> str:
    # DOW table
    mxr = max(r[1] for r in DOW_DATA)
    dtr = ""
    for day, rev, pay, arppu, note, col in DOW_DATA:
        w = rev / mxr * 100
        dtr += (f'<tr><td class="nm">{day}</td><td class="num g">${rev:,}</td><td class="num">{pay:,}</td>'
                f'<td class="num">${arppu}</td><td class="num" style="color:{col}">{_esc(note)}</td>'
                f'<td class="track"><div class="hbar"><div class="fill" style="width:{w:.1f}%;background:{col}"></div></div></td></tr>')
    # week-of-month table
    mxw = max(r[1] for r in WOM_DATA)
    wtr = ""
    for lbl, rev, conv, note in WOM_DATA:
        col = "#22c55e" if rev >= 660000 else ("#ef4444" if rev < 615000 else "#4f9cff")
        w = rev / mxw * 100
        wtr += (f'<tr><td class="nm">{_esc(lbl)}</td><td class="num g">${rev:,}</td><td class="num">{conv}%</td>'
                f'<td class="num" style="color:{col}">{_esc(note)}</td>'
                f'<td class="track"><div class="hbar"><div class="fill" style="width:{w:.1f}%;background:{col}"></div></div></td></tr>')
    # connection segments
    mxc = max(r[4] for r in CONN_DATA)
    ctr = ""
    for seg, users, pctd, conv, rev, pctr in CONN_DATA:
        col = "#22c55e" if seg == "Daily" else ("#ef4444" if conv < 4 else "#8b97ae")
        w = rev / mxc * 100
        ctr += (f'<tr><td class="nm">{_esc(seg)}</td><td class="num">{users:,}</td><td class="num">{pctd}%</td>'
                f'<td class="num" style="color:{col}">{conv}%</td><td class="num g">${rev:,}</td><td class="num">{pctr}%</td>'
                f'<td class="track"><div class="hbar"><div class="fill" style="width:{w:.1f}%;background:{col}"></div></div></td></tr>')
    new_insights = render_planning_insights() + render_economy_backtest() + render_growth_vs_economy_insights() + render_august_recommendations()
    legacy_open = '<details class="cal-fc-card"><summary>Legacy: Deep insights — Nov 2025–Jul 2026 242-day snapshot (historical reference, not auto-updating)</summary>'
    return (
        new_insights
        + legacy_open
        + f'<div class="sec-title">🔗 Deep insights — data-grounded (v2: 1.11.25–2.7.26, 242 Days · baseline $650K/Day)</div>'
        f'<div class="kpis">'
        f'<div class="kpi"><div class="v" style="color:#22c55e">Sat</div><div class="l">Revenue peak $710K (real depth: Custom Pod/Coin Sale)</div></div>'
        f'<div class="kpi"><div class="v" style="color:#22c55e">Week 1</div><div class="l">$671K · conv 6.78% (strong, modest gap vs v1)</div></div>'
        f'<div class="kpi"><div class="v" style="color:#ef4444">Tue/Thu</div><div class="l">Weaker days (~$610K)</div></div>'
        f'<div class="kpi"><div class="v">Daily 90%</div><div class="l">of revenue from 79% of DAU</div></div></div>'
        f'<div class="grid2">'
        f'<div class="card"><div class="sec-sub">📅 By day of week</div>'
        f'<table class="rank"><thead><tr><th>Day</th><th class="num">Revenue/Day</th><th class="num">Payers</th><th class="num">ARPPU</th><th>Read</th><th class="track"></th></tr></thead><tbody>{dtr}</tbody></table></div>'
        f'<div class="card"><div class="sec-sub">🗓️ By week of month</div>'
        f'<table class="rank"><thead><tr><th>Period</th><th class="num">Revenue/Day</th><th class="num">conv</th><th>Read</th><th class="track"></th></tr></thead><tbody>{wtr}</tbody></table></div>'
        f'</div>'
        f'<div class="sec-title">👥 User connection (login frequency) — who monetizes</div>'
        f'<div class="card"><div class="note">Daily-connected users are <b>79% of DAU but ~90% of revenue</b> (conv 7.8% vs 2.7% for new). Retention = monetization.</div>'
        f'<table class="rank"><thead><tr><th>Segment</th><th class="num">Users</th><th class="num">% DAU</th><th class="num">conv</th><th class="num">Revenue</th><th class="num">% Revenue</th><th class="track"></th></tr></thead><tbody>{ctr}</tbody></table></div>'
        f'<div class="sec-title">🧠 Key placement insights</div>'
        f'<div class="grid2">'
        f'<div class="ins"><h4 style="color:#22c55e">Real depth vs conditional toppers</h4><p><b>True standalone depth</b> (survives holiday-clean): Custom Pod (+8.9%), Coin Sale (+4.2%) → peak days/Saturday. '
        f'<b>Extreme Stamp/MGAP Bigger</b> looked strong but were holiday-confounded — conditional toppers (Revenue tab). '
        f'<b>Breadth</b> (many payers, lower ARPPU): Price Cut → widen funnel, Mondays.</p></div>'
        f'<div class="ins"><h4 style="color:#4f9cff">Economy</h4><p><b>MGAP</b> = largest coin sink (246–248M spins). <b>Gem amplifiers</b> (Rolling MoreForLess $51K, Coin Sale $48K, GGS $47K, Boosted Gemback $42K) drive gem purchases. Gem balance ~9–10K · Slotobucks ~385K.</p></div>'
        f'<div class="ins"><h4 style="color:#eab308">Timing</h4><p><b>Front-load Week 1</b> (strongest, but gap more modest than v1 — see v2), protect <b>Week 3</b> (trough) with retention/value. Do not waste amplifiers on Tue/Thu. Sat→depth, Mon→breadth.</p></div>'
        f'<div class="ins"><h4 style="color:#ec4899">Momentum</h4><p>Sale/Extreme days cause next-day drop of only <b>a mild (~$8K)</b> still above baseline → back-to-back amplifiers (Fri→Sat) are safe. ⚠️ part of this is holidays (Revenue tab).</p></div>'
        f'</div>'
        f'<div class="sec-title">📈 User trend (quarterly)</div>'
        f'<div class="card"><div class="note">DAU slowly declining <b>424K → 406K (~4%/quarter)</b>, but revenue holds ($620–650K) via <b>rising ARPU</b> and stable engagement (sessions ~4.2). Monetization works harder on a shrinking base → support retention.</div></div>'
        f'<div class="warn">⚠️ Day-level correlations (multiple promos live together). Direction consistent across independent cuts and daily reports. Coin balances in hyperinflation — measure via wager/spins.</div>'
        + '</details>')


def render_revenue_reco() -> str:
    top_sc = sorted(SC_VALUE, key=lambda r: r[2], reverse=True)[:3]
    bot_sc = sorted(SC_VALUE, key=lambda r: r[2])[:2]
    top_prize = sorted([p for p in PRIZES if "removed" not in p[3].lower() and "⛔" not in p[0]], key=lambda r: r[2], reverse=True)[0]
    weak_prize = [p for p in PRIZES if "weak" in p[3].lower()]
    sc_top_txt = ", ".join(f"{_esc(f)} (+{(v/SC_BASELINE-1)*100:.0f}%)" for f, _, v in top_sc)
    sc_bot_txt = ", ".join(f"{_esc(f)} ({(v/SC_BASELINE-1)*100:.0f}%)" for f, _, v in bot_sc)
    weak_txt = ", ".join(_esc(p[0]) for p in weak_prize) or "—"
    return ('<div class="card" style="border-color:#eab308">'
            '<div class="sec-sub">🎯 Recommendations — Revenue</div>'
            '<div class="grid2">'
            f'<div class="ins"><h4 style="color:#22c55e">Peak anchors (depth / Sat / event)</h4><p>{sc_top_txt} — top Smart Calendar × revenue lift. '
            f'Strongest DD prize: <b>{_esc(top_prize[0])}</b> (${top_prize[2]:,}/day).</p></div>'
            f'<div class="ins"><h4 style="color:#ef4444">Do not waste on peak days</h4><p>{sc_bot_txt} — below baseline; use on quiet days (Tue/Thu). Weak DD prizes: <b>{weak_txt}</b> — reduce.</p></div>'
            '</div></div>')


def render_top_reco() -> str:
    a = compute_calendar_audit()
    sc_top = sorted(SC_VALUE, key=lambda r: r[2], reverse=True)[0]
    sc_bot = sorted(SC_VALUE, key=lambda r: r[2])[0]
    kb = (load_calibration().get("product_knowledge") or {})
    top_pair = (kb.get("top_pairs") or [{}])[0]
    weak_pair = (kb.get("weak_pairs") or [{}])[0]
    top_pair_txt = ""
    if top_pair.get("keys"):
        top_pair_txt = " + ".join(_esc(PROMO_LABEL.get(k, k)) for k in top_pair["keys"])
    weak_pair_txt = ""
    if weak_pair.get("keys"):
        weak_pair_txt = " + ".join(_esc(PROMO_LABEL.get(k, k)) for k in weak_pair["keys"])
    v_txt = "0 violations" if not a["violations"] else f"{len(a['violations'])} violations"
    sat_reco = (f'All {a["sat_total"]} Saturdays anchored with real depth ✅ (Coin Sale/Custom Pod/MGAP BOGO — not Extreme Stamp/Bigger, conditional toppers in v2 analysis).' if a["sat_anchored"] == a["sat_total"]
                else f'Saturday {", ".join(str(d) for d in a["sat_gap"])} missing depth — Sat = empirical peak ($710K/day). Prefer Coin Sale/Custom Pod/MGAP BOGO.')
    week3_reco = f'Week 3 (15–21 Aug) is the historical trough (−6% vs week 1 in v2); add {a["trough_ggs"]} x2 GGS days (17 Aug) to defend the trough.'
    items = [
        ("📅 Calendar", sat_reco),
        ("📅 Calendar", week3_reco),
        ("💰 Revenue", f'<b>{_esc(sc_top[0])}</b> remains the strongest broad-history family, but planning should use the v11 live-calibrated forecast plus the Jan+ combinations table.'),
        ("🧠 Combos", f'Strong Jan+ combo signal: <b>{top_pair_txt}</b> ({top_pair.get("avg_residual_k", 0):+.0f}K vs DOW+month). Avoid/pressure-test: <b>{weak_pair_txt}</b> ({weak_pair.get("avg_residual_k", 0):+.0f}K).') if top_pair_txt and weak_pair_txt else ("🧠 Combos", "Jan+ combination table added in Revenue; use it as directional planning context, not causal proof."),
        ("📡 Game Health", 'Game Health now uses 45 DWH days, not manual samples; DAU/PU are declining, while ARPU partially offsets.'),
        ("💰 Revenue", f'<b>{_esc(sc_bot[0])}</b> below baseline ({(sc_bot[2]/SC_BASELINE-1)*100:.0f}%) — save for quiet days (Tue/Thu), not peak days.'),
        ("🪙 Core", "Spin Zone + PYP are coin-sink workhorses (positive wager correlation); Dash Challenge is inverse — do not rely on it for sink."),
        ("💎 Gems", 'Joker-Different Prizes (+89%) and Wild Guaranteed (+71%) are top Shiny Show variants — place before/after gem amplifiers (Rolling More-for-Less / GGS).'),
        ("👥 Users", 'Daily-connected = 79% of DAU but ~90% of revenue — retention / login-habit investment directly protects the revenue engine.'),
        ("✅ Validation", f'{v_txt} from {a["rules_checked"]} HARD rules on {a["n_days"]} days (validate_calendar.py, every build).'),
    ]
    grid = "".join(
        f'<div class="reco-item"><span class="reco-cat">{_esc(cat)}</span><div>{txt}</div></div>'
        for cat, txt in items
    )
    return f'<div class="reco-grid">{grid}</div>'


def render_header_chips() -> str:
    a = compute_calendar_audit()
    ok = not a["violations"]
    v_txt = "0 violations" if ok else f"{len(a['violations'])} violations"
    chip_ok = " ok" if ok else ""
    cal_chip = ""
    if CALIBRATION_FILE.is_file():
        try:
            meta = json.loads(CALIBRATION_FILE.read_text(encoding="utf-8")).get("meta", {})
            computed_at = (meta.get("computed_at") or "")[:16].replace("T", " ")
            n_rev = meta.get("n_revenue_days", "?")
            err = meta.get("self_check_mean_abs_pct_error")
            err_txt = f" · ±{err}% cross-validated" if err is not None else ""
            cal_chip = (
                f'<span class="chip cal-live" title="Self-calibrated automatically from real data, '
                f'accuracy measured by 5-fold cross-validation (held-out days, not the same days used '
                f'to fit) — see scripts/calibrate_model.py"><strong>🔄 Live-calibrated</strong> {n_rev}d'
                f'{err_txt} · {computed_at}</span>'
            )
        except Exception:
            pass
    return (
        f'<span class="chip{chip_ok}"><strong>{v_txt}</strong> · {a["rules_checked"]} HARD</span>'
        f'<span class="chip v5"><strong>Forecast v11</strong> self-calibrating</span>'
        + cal_chip +
        f'<span class="chip"><strong>August 2026</strong></span>'
        f'<span class="chip"><strong>{PLAN_DAU / 1000:.0f}K</strong> DAU · {PLAN_PAY / 1000:.1f}K PU</span>'
    )



def build_app_js(days: str, variant_dates: str, months_json: str, calibration_json: str) -> str:
    app = APP_JS_FILE.read_text(encoding="utf-8")
    return (
        app.replace("__DAYS__", days)
        .replace("__VARIANT_DATES__", variant_dates)
        .replace("__MONTHS__", months_json)
        .replace("__CALIBRATION__", calibration_json)
    )


def assemble_html(style_block: str, footer: str, app_js: str, last_updated: str) -> str:
    shell = SHELL_FILE.read_text(encoding="utf-8")
    script_block = "<script>\n" + app_js + "\n</script>"
    return (
        shell.replace("__STYLE_BLOCK__", style_block)
        .replace("__BUILD_FOOTER__", footer)
        .replace("__HEADER_CHIPS__", render_header_chips())
        .replace("__LAST_UPDATED__", _esc(last_updated))
        .replace("__APP_SCRIPT__", script_block)
    )


# ===== Live DWH data (Vertica) =====
# trend: last 45 days from agg.agg_sm_daily_users_stats
TREND = [
    ('05-19', 419667, 519942, 22126),
    ('05-20', 418799, 573974, 26950),
    ('05-21', 417411, 519860, 23468),
    ('05-22', 413894, 724900, 27466),
    ('05-23', 413022, 694313, 25956),
    ('05-24', 414072, 673948, 27306),
    ('05-25', 416929, 755390, 35515),
    ('05-26', 416303, 511939, 23724),
    ('05-27', 416976, 542088, 24753),
    ('05-28', 415415, 670092, 23210),
    ('05-29', 411617, 695444, 23478),
    ('05-30', 407454, 618176, 24969),
    ('05-31', 412238, 595397, 27656),
    ('06-01', 415077, 728108, 34584),
    ('06-02', 415843, 544902, 25120),
    ('06-03', 415855, 620506, 27446),
    ('06-04', 415357, 591240, 25645),
    ('06-05', 411614, 647804, 25853),
    ('06-06', 408486, 646385, 24108),
    ('06-07', 413482, 583263, 25873),
    ('06-08', 416300, 599183, 33434),
    ('06-09', 414993, 641178, 26490),
    ('06-10', 415569, 583335, 25488),
    ('06-11', 413334, 571885, 24740),
    ('06-12', 409576, 585954, 26562),
    ('06-13', 407074, 872009, 28128),
    ('06-14', 411492, 691833, 28045),
    ('06-15', 411485, 557541, 32930),
    ('06-16', 413097, 608878, 24964),
    ('06-17', 410704, 619042, 25434),
    ('06-18', 406648, 531915, 25009),
    ('06-19', 405054, 549239, 23549),
    ('06-20', 404290, 712278, 26590),
    ('06-21', 405968, 703970, 29325),
    ('06-22', 408967, 619576, 33321),
    ('06-23', 409067, 587105, 23533),
    ('06-24', 408636, 604951, 25677),
    ('06-25', 406811, 522394, 22033),
    ('06-26', 403942, 625207, 25348),
    ('06-27', 400490, 676767, 27195),
    ('06-28', 405315, 597833, 31245),
    ('06-29', 407850, 641888, 32673),
    ('06-30', 406950, 515780, 23592),
    ('07-01', 406943, 762122, 29146),
    ('07-02', 406564, 615657, 24115),
]
# revenue by product (30d, tran_status_id=2) from sm_fact_payments × SM_DIM_Products
LIVE_PRODUCTS = [
    ('MGAPP', 5400788, 50398),
    ('Sticky Bundle PP', 3533353, 60316),
    ('Payment Page', 1722954, 41592),
    ('Seasonals', 1619310, 34985),
    ('Gems', 1173062, 25731),
    ('Rolling Offer', 859247, 31278),
    ('Reveal Your Deal', 780040, 42717),
    ('Clan Dash Bundle', 496845, 24305),
    ('LBP Multi Ball', 471963, 35196),
    ('Offers', 351345, 24873),
    ('Buy All', 325465, 21529),
    ('Prize Mania', 298123, 22092),
    ('Daily Dash Plus', 296898, 46198),
    ('Gems MGAP', 285007, 3037),
    ('Piggy', 269914, 18955),
    ('Dice Deluxe', 199927, 16034),
    ('Mega Pods Pass', 190005, 7202),
    ('Clan Bar - Pass', 110578, 15496),
    ('Golden Spin', 90391, 10894),
    ('Unknown', 86431, 9988),
    ('Mystery Buy All', 54603, 4366),
    ('Counter PO', 43222, 2793),
    ('Sloto Store Offers', 30183, 3344),
    ('RLAP', 18892, 938),
    ('Ballinko', 11, 4),
]
# gameplay/velocity (date, spinners, spins_per_spinner, win_rate, sessions_per_user) — 45d
GAMEPLAY = [
    ('05-19', 288999, 780, 88.5, 4.3),
    ('05-20', 293568, 810, 99.6, 4.3),
    ('05-21', 284940, 767, 123.3, 4.1),
    ('05-22', 283446, 786, 109.7, 4.1),
    ('05-23', 285171, 796, 97.1, 4.1),
    ('05-24', 291794, 853, 109.8, 4.0),
    ('05-25', 289319, 855, 88.8, 4.3),
    ('05-26', 285448, 797, 90.5, 4.2),
    ('05-27', 290550, 838, 86.6, 4.3),
    ('05-28', 292604, 811, 98.6, 4.2),
    ('05-29', 286814, 792, 96.3, 4.0),
    ('05-30', 280013, 811, 90.7, 4.0),
    ('05-31', 288385, 850, 92.7, 4.1),
    ('06-01', 284238, 809, 89.5, 4.2),
    ('06-02', 285567, 773, 93.0, 4.2),
    ('06-03', 289073, 812, 103.0, 4.3),
    ('06-04', 295809, 811, 94.1, 4.2),
    ('06-05', 296019, 840, 111.5, 4.1),
    ('06-06', 284297, 835, 94.7, 4.0),
    ('06-07', 292808, 872, 88.8, 4.1),
    ('06-08', 291235, 848, 87.0, 4.2),
    ('06-09', 288759, 793, 97.0, 4.2),
    ('06-10', 293399, 831, 82.8, 4.2),
    ('06-11', 286748, 799, 91.0, 4.2),
    ('06-12', 287159, 811, 92.0, 4.1),
    ('06-13', 281522, 799, 93.0, 4.2),
    ('06-14', 289691, 858, 88.7, 4.1),
    ('06-15', 286121, 840, 81.8, 4.2),
    ('06-16', 286407, 806, 59.5, 4.2),
    ('06-17', 286484, 783, 83.8, 4.1),
    ('06-18', 277170, 765, 100.6, 4.1),
    ('06-19', 274369, 798, 105.1, 4.1),
    ('06-20', 272327, 798, 120.9, 4.2),
    ('06-21', 284736, 874, 92.5, 4.2),
    ('06-22', 286411, 869, 71.3, 4.3),
    ('06-23', 284195, 824, 94.4, 4.3),
    ('06-24', 286086, 838, 87.0, 4.3),
    ('06-25', 286945, 794, 96.3, 4.1),
    ('06-26', 286566, 811, 90.3, 4.1),
    ('06-27', 277263, 795, 86.1, 4.1),
    ('06-28', 285641, 846, 92.2, 4.2),
    ('06-29', 282957, 844, 99.3, 4.3),
    ('06-30', 280870, 801, 91.0, 4.2),
    ('07-01', 285046, 820, 111.4, 4.2),
    ('07-02', 278162, 777, 140.7, 4.1),
]
# revenue/gameplay by tier (last 30d): (tier, users, avg_spins, rev_30d, payers)
TIERS = [
    (1, 293054, 162, 9777, 2199),
    (2, 172369, 275, 68654, 5591),
    (3, 153805, 382, 219084, 9069),
    (4, 202717, 542, 919909, 25597),
    (5, 159454, 791, 3371862, 56688),
    (6, 38110, 892, 5675843, 23849),
    (7, 11681, 1295, 8405277, 8938),
]


def _spark(series, fmt, unit_lo=None):
    """series: list of (label, value, tooltip). Returns spark HTML with green>=avg else blue."""
    vals = [v for _, v, _ in series]
    avg = sum(vals) / len(vals)
    mx = max(vals)
    bars = ""
    for lab, v, tip in series:
        h = v / mx * 100
        col = "#22c55e" if v >= avg else "#4f9cff"
        bars += f'<div class="spk" title="{tip}"><div style="height:{h:.0f}%;background:{col}"></div><span>{lab}</span></div>'
    return bars


def render_game_health() -> str:
    n = len(TREND)
    avg_dau = sum(r[1] for r in TREND) / n
    avg_rev = sum(r[2] for r in TREND) / n
    avg_pay = sum(r[3] for r in TREND) / n
    arpu = avg_rev / avg_dau; conv = avg_pay / avg_dau * 100; arppu = avg_rev / avg_pay
    avg_spinners = sum(r[1] for r in GAMEPLAY) / len(GAMEPLAY)
    avg_vel = sum(r[2] for r in GAMEPLAY) / len(GAMEPLAY)
    avg_sess = sum(r[4] for r in GAMEPLAY) / len(GAMEPLAY)
    spin_pct = avg_spinners / avg_dau * 100
    # sparklines
    rev_spark = _spark([(d[3:], rev, f"{d}: ${rev/1000:.0f}K · DAU {dau/1000:.0f}K · {pay/1000:.1f}K payers") for d, dau, rev, pay in TREND], None)
    vel_spark = _spark([(g[0][3:], g[2], f"{g[0]}: {g[2]} spins/spinner · {g[1]/1000:.0f}K spinners · {g[4]} sess") for g in GAMEPLAY], None)
    # tiers
    tot_u = sum(t[1] for t in TIERS); tot_r = sum(t[3] for t in TIERS)
    trs = ""
    for tier, users, spins, rev, pay in TIERS:
        hot = tier >= 6
        rw = rev / max(t[3] for t in TIERS) * 100
        row_attr = ' style="background:#1c2842"' if hot else ""
        bar_col = "#ec4899" if hot else "#4f9cff"
        trs += (f'<tr{row_attr}><td class="nm">Tier {tier}{" 🐋" if hot else ""}</td>'
                f'<td class="num">{users/1000:.0f}K</td><td class="num">{spins}</td>'
                f'<td class="num g">${rev/1e6:.2f}M</td><td class="num">{rev/tot_r*100:.0f}%</td>'
                f'<td class="num">{pay/1000:.1f}K</td><td class="track"><div class="hbar"><div class="fill" style="width:{rw:.0f}%;background:{bar_col}"></div></div></td></tr>')
    t67_u = sum(t[1] for t in TIERS if t[0] >= 6) / tot_u * 100
    t67_r = sum(t[3] for t in TIERS if t[0] >= 6) / tot_r * 100
    return (
        '<div class="sec-title" style="margin-top:4px">📡 Game health — live from DWH (SM · last 45d)</div>'
        '<div class="kpis">'
        f'<div class="kpi"><div class="v">{avg_dau/1000:.0f}K</div><div class="l">DAU / day (45d avg)</div></div>'
        f'<div class="kpi"><div class="v" style="color:#22c55e">${avg_rev/1000:.0f}K</div><div class="l">Revenue/Day</div></div>'
        f'<div class="kpi"><div class="v">{avg_pay/1000:.1f}K</div><div class="l">Payers/Day · {conv:.1f}% conv</div></div>'
        f'<div class="kpi"><div class="v">${arpu:.2f} · ${arppu:.0f}</div><div class="l">ARPU · ARPPU</div></div>'
        '</div>'
        '<div class="card"><div class="note">💵 Daily revenue (45 days) — green = above average. Source: <code>agg.agg_sm_daily_users_stats</code>. Uses full DWH daily actuals, not manual report samples.</div>'
        f'<div class="spark">{rev_spark}</div></div>'
        '<div class="sec-title">🎮 Gameplay & velocity</div>'
        '<div class="kpis">'
        f'<div class="kpi"><div class="v">{avg_spinners/1000:.0f}K</div><div class="l">Spinners/Day ({spin_pct:.0f}% of DAU)</div></div>'
        f'<div class="kpi"><div class="v">{avg_vel:.0f}</div><div class="l">Velocity (spins/spinner)</div></div>'
        f'<div class="kpi"><div class="v">{avg_sess:.1f}</div><div class="l">Sessions/user</div></div>'
        f'<div class="kpi"><div class="v">~90%</div><div class="l">Win rate (volatile · hyperinflation)</div></div>'
        '</div>'
        '<div class="card"><div class="note">⚡ Velocity — spins per spinner (45 DWH days). Use trend shape, not single-day spikes, for planning.</div>'
        f'<div class="spark">{vel_spark}</div></div>'
        '<div class="sec-title">🐋 Revenue & gameplay by tier (7 days)</div>'
        '<div class="card"><table class="rank"><thead><tr><th>Tier</th><th class="num">Users</th><th class="num">avg spins</th><th class="num">Revenue 30d</th><th class="num">% Revenue</th><th class="num">Payers</th><th class="track">Revenue</th></tr></thead>'
        f'<tbody>{trs}</tbody></table></div>'
        '<div class="grid2">'
        f'<div class="ins"><h4 style="color:#ec4899">Revenue concentration in whales</h4><p>Tiers 6-7 = <b>{t67_u:.0f}% of users</b> but <b>{t67_r:.0f}% of revenue</b>. Tier 7 alone (~12K users) ≈ $8.4M/30d. Declining tier 6–7 activity = red flag (per daily reports).</p></div>'
        f'<div class="ins"><h4 style="color:#22c55e">Higher velocity = higher tiers</h4><p>avg spins rise sharply with tier (T1 164 → T7 1282). End-of-album MES raised velocity — sink + engagement.</p></div>'
        '</div>'
        '<div class="warn">⚠️ Win rate and avg bet very volatile under coin hyperinflation — not reliable daily KPIs. Use percentiles for balances (evening reports).</div>'
    )


def render_live_products() -> str:
    rows = sorted(LIVE_PRODUCTS, key=lambda r: r[1], reverse=True)
    mx = max(r[1] for r in rows)
    trs = ""
    for name, rev, pay in rows:
        w = rev / mx * 100
        trs += (f'<tr><td class="nm">{_esc(name)}</td><td class="num g">${rev/1e6:.2f}M</td>'
                f'<td class="num">${rev/30/1000:.0f}K</td><td class="num">{pay/1000:.1f}K</td>'
                f'<td class="track"><div class="hbar"><div class="fill" style="width:{w:.1f}%;background:#4f9cff"></div></div></td></tr>')
    return (
        '<div class="sec-title">💰 Live revenue by product — 30 days (DWH)</div>'
        '<div class="card"><div class="note">Net revenue (tran_status_id=2) from <code>sm_fact_payments</code> × <code>SM_DIM_Products</code>. always-on: MGAPP/Sticky Bundle/Payment Page/Gems/Reveal.</div>'
        '<table class="rank"><thead><tr><th>Product</th><th class="num">30 Day</th><th class="num">$/day</th><th class="num">Payers</th><th class="track">Share</th></tr></thead>'
        f'<tbody>{trs}</tbody></table></div>'
    )


def render_calibration_status() -> str:
    if not CALIBRATION_FILE.is_file():
        return "Calibration file not found — run <code>scripts/calibrate_model.py</code>."
    try:
        meta = json.loads(CALIBRATION_FILE.read_text(encoding="utf-8")).get("meta", {})
    except Exception:
        return "Could not read calibration metadata."
    computed_at = (meta.get("computed_at") or "unknown")[:16].replace("T", " ")
    n_rev = meta.get("n_revenue_days", "?")
    n_pu = meta.get("n_pu_days", "?")
    n_gp = meta.get("n_gameplay_days", "?")
    rev_window = meta.get("revenue_window_days", "?")
    pu_window = meta.get("pu_window_days", "?")
    err = meta.get("self_check_mean_abs_pct_error")
    pu_err = meta.get("pu_self_check_mean_abs_pct_error")
    in_sample = meta.get("self_check_in_sample_pct_error")
    rev_range = meta.get("revenue_date_range") or meta.get("date_range") or ["?", "?"]
    pu_range = meta.get("pu_date_range") or ["?", "?"]
    err_txt = f"±{err}%" if err is not None else "n/a"
    pu_err_txt = f"±{pu_err}%" if pu_err is not None else "n/a"
    in_sample_txt = f" (in-sample fit was ±{in_sample}%, always looks better — the CV number is the honest one)" if in_sample is not None else ""
    return (
        f"Last calibrated <b>{computed_at}</b> from <b>{n_rev} real revenue days</b> "
        f"(trailing {rev_window}d, {rev_range[0]} → {rev_range[1]}) and <b>{n_pu} real PU days</b> "
        f"(trailing {pu_window}d, {pu_range[0]} → {pu_range[1]}), pulled from the wide DWH promo-history table — see <code>mm_calendar/smart_calendar.md</code> — "
        f"not just the Monday-board window. Revenue CV: <b>{err_txt}</b>; PU CV: <b>{pu_err_txt}</b>{in_sample_txt}. Gameplay remains <b>{n_gp}</b> real days."
    )


def fill_dashboard(html: str, days: str, variant_dates: str) -> str:
    return (
        html.replace("__DAYS__", days)
        .replace("__VARIANT_DATES__", variant_dates)
        .replace("__CALIBRATION_STATUS__", render_calibration_status())
        .replace("__GAME_HEALTH__", render_game_health())
        .replace("__CAL_AUDIT__", render_calendar_audit())
        .replace("__CORE_PERF__", render_core_perf())
        .replace("__CORE_RECO__", render_core_reco())
        .replace("__GEMS_PERF__", render_gems_perf())
        .replace("__GEMS_RECO__", render_gems_reco())
        .replace("__LIVE_PRODUCTS__", render_live_products())
        .replace("__SC_VALUE__", render_sc_value() + _product_knowledge_table() + '<div class="sec-title">🧬 Promo × prize/content — what to replicate</div>' + _revenue_content_table())
        .replace("__REVENUE_RECO__", render_revenue_reco())
        .replace("__RELATIONSHIPS__", render_relationships())
        .replace("__TOP_RECO__", render_top_reco())
        .replace("__REVENUE_PERF__", render_revenue_perf())
    )


def main():
    days = extract_days()
    vd_file = ROOT / "mm_calendar" / "data" / "variant_dates.json"
    variant_dates = vd_file.read_text(encoding="utf-8") if vd_file.is_file() else "{}"
    months, draft_month_keys = load_months_for_dashboard()
    months_json = json.dumps(months, ensure_ascii=False)
    cal_obj: dict = {}
    if CALIBRATION_FILE.is_file():
        try:
            cal_obj = json.loads(CALIBRATION_FILE.read_text(encoding="utf-8"))
        except Exception:
            cal_obj = {}
    cal_obj = patch_calibration_for_draft_months(cal_obj, draft_month_keys)
    calibration_json = json.dumps(cal_obj, ensure_ascii=False)
    css = CSS_FILE.read_text(encoding="utf-8")
    built = datetime.now().strftime("%Y-%m-%d %H:%M")
    cache_v = datetime.now().strftime("%Y%m%d%H%M")
    footer = f"MM Dashboard · Slotomania · Built {built} · Forecast v11 (CV-selected forecast windows + Jan+ product/combo knowledge, wide-DWH, PU + gameplay) · <code>mm_calendar/public</code>"
    app_js = build_app_js(days, variant_dates, months_json, calibration_json)

    html_data = fill_dashboard(
        assemble_html(f"<style>\n{css}\n</style>", footer, app_js, built),
        days,
        variant_dates,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_data, encoding="utf-8")

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_CSS.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CSS_FILE, PUBLIC_CSS)
    html_public = fill_dashboard(
        assemble_html(
            f'<link rel="stylesheet" href="assets/dashboard.css?v={cache_v}"/>',
            footer,
            app_js,
            built,
        ),
        days,
        variant_dates,
    )
    PUBLIC_INDEX.write_text(html_public, encoding="utf-8")

    # OneDrive share: single file must be self-contained (no relative assets/ path).
    html_standalone = fill_dashboard(
        assemble_html(f"<style>\n{css}\n</style>", footer, app_js, built),
        days,
        variant_dates,
    )

    # Sync to OneDrive (auto-update on every build)
    ONEDRIVE_DIR = Path("/Users/itayg/Library/CloudStorage/OneDrive-PlaytikaLtd/Calendar Maker")
    if ONEDRIVE_DIR.is_dir():
        onedrive_dest = ONEDRIVE_DIR / "MM_Calendar_August_2026.html"
        onedrive_dest.write_text(html_standalone, encoding="utf-8")
        print(f"Synced to OneDrive (standalone): {onedrive_dest}")
        # Optional folder layout for local http.server — keeps linked index in sync too
        od_assets = ONEDRIVE_DIR / "mm_calendar_public"
        od_assets.mkdir(exist_ok=True)
        (od_assets / "assets").mkdir(exist_ok=True)
        shutil.copy2(CSS_FILE, od_assets / "assets" / "dashboard.css")
        (od_assets / "index.html").write_text(html_public, encoding="utf-8")
    else:
        print(f"Warning: OneDrive folder not found at {ONEDRIVE_DIR} — skipping sync")

    print(f"Wrote: {OUT}")
    print(f"Published: {PUBLIC_INDEX}")
    print(f"  → cd \"{PUBLIC_DIR}\" && python3 -m http.server 8765")
    print(f"  → http://localhost:8765/")


if __name__ == "__main__":
    main()
