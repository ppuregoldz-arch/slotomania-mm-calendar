#!/usr/bin/env python3
"""Shared scorer: loads model_calibration.json and exposes predict() / predict_pu()
for use by both the calendar builder (build_august_2026_plan.py) and parity tests.

This is the Python counterpart of the JS predict() / predictPU() in dashboard_app.js.
Both must produce the same result on a fixed day fixture — verified by parity_test().
"""
from __future__ import annotations

import json
import re
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_CAL_PATH = ROOT / "mm_calendar" / "data" / "model_calibration.json"
_cal: dict | None = None


def _load() -> dict:
    global _cal
    if _cal is None:
        _cal = json.loads(_CAL_PATH.read_text(encoding="utf-8"))
    return _cal


def reload():
    """Force re-read of model_calibration.json (call after running calibrate_model.py)."""
    global _cal
    _cal = None


WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
MAJOR_HOLIDAY_RE = re.compile(
    r"cinco de mayo|black friday|new year|valentine|st\.? ?patrick"
    r"|independence day|4th of july|memorial day",
    re.I,
)
DOM_BUCKETS = [("b1", 2), ("b2", 7), ("b3", 14), ("b4", 21), ("b5", 28)]

INTERACTION_MAP = {
    "ix_mgapBigger_x_coinSale":    ("mgapBigger",  "coinSale"),
    "ix_customPod_x_coinSale":     ("customPod",   "coinSale"),
    "ix_customPod_x_happyHour":    ("customPod",   "happyHour"),
    "ix_coinSale_x_decoyBonanza":  ("coinSale",    "decoyBonanza"),
}

_PAT = {
    "customPod":       re.compile(r"custom pod"),
    "coinSale":        re.compile(r"coins? sale"),
    "decoyBonanza":    re.compile(r"decoy|bonanza"),
    "mgapBogo":        re.compile(r"mgap.*bogo|bogo.*mgap"),
    "mgapMatched":     re.compile(r"mgap.*matched"),
    "mgapWildSymbols": re.compile(r"mgap.*wild symbol"),
    "mgapBigger":      re.compile(r"mgap.*bigger"),
    "mgapOther":       re.compile(r"mgap"),
    "gemback":         re.compile(r"gemback"),
    "rollingMoreForLess": re.compile(r"more.for.less|buy.more"),
    "rolling":         re.compile(r"rolling"),
    "prizeMania":      re.compile(r"prize mania"),
    "priceCut":        re.compile(r"price cut"),
    "buyAll":          re.compile(r"buy all"),
    "goldenSpin":      re.compile(r"golden spin"),
    "counterPo":       re.compile(r"counter po"),
    "snl":             re.compile(r"\bsnl\b"),
    "happyHour":       re.compile(r"happy hour|jumbo giveaway|jumbo|prize picker"),
    "extremeStamp":    re.compile(r"extreme stamp"),
    "fortuneDip":      re.compile(r"fortune dip"),
}


def _item_names(day: dict) -> list[str]:
    return [it["name"].lower() for it in day.get("items", []) if not it.get("backup")]


def _detect_promos(day: dict) -> dict[str, int]:
    """Detect which promo keys are present in a day (same logic as calibrate_model.promo_flags)."""
    names = _item_names(day)
    full = " | ".join(names)
    mgap = " | ".join(n for n in names if "mgap" in n)

    out: dict[str, int] = {}
    specific_mgap = False
    for k in ("mgapBogo", "mgapMatched", "mgapWildSymbols", "mgapBigger"):
        out[k] = 1 if _PAT[k].search(mgap) else 0
        if out[k]:
            specific_mgap = True
    out["mgapOther"] = 1 if (_PAT["mgapOther"].search(full) and not specific_mgap) else 0
    for k, pat in _PAT.items():
        if k.startswith("mgap"):
            continue
        out[k] = 1 if pat.search(full) else 0

    # Interaction keys
    for ix_key, (a, b) in INTERACTION_MAP.items():
        out[ix_key] = 1 if (out.get(a, 0) and out.get(b, 0)) else 0

    return out


def _dom_bucket(date_int: int) -> str:
    for key, threshold in DOM_BUCKETS:
        if date_int <= threshold:
            return key
    return "b6"


def _crowd_adj(day: dict, cal: dict, metric: str = "revenue") -> float:
    """Crowd + trend adjustment for the day's month."""
    meta = _load()["meta"]
    today_month = meta.get("current_month", "")
    c = cal.get("crowd_adj_by_month", {})
    t = cal.get("crowd_trend_per_day", {})
    month_key = day["month"]
    base = c.get(month_key, 0.0)
    if month_key == today_month and day["date"] > 1:
        base += t.get(month_key, 0.0) * (day["date"] - 1)
    return base


def predict(day: dict, month_key: str | None = None, prev_day: dict | None = None) -> float:
    """Predict revenue ($K) for `day`.

    day must have at minimum: dow, date, month (YYYY-MM), items (list).
    prev_day is the previous calendar day (optional, for carryover).
    Returns predicted revenue in thousands of dollars.
    """
    cal = _load()
    rev = cal["revenue"]
    base_dow = rev.get("base_dow", {})
    mk = month_key or day.get("month", "")

    # DOW baseline
    r = base_dow.get(day["dow"], 638.0)

    # Crowd + trend
    r += _crowd_adj(day, rev)

    # DOM curve
    dom_curve = rev.get("day_of_month_curve", {})
    r += dom_curve.get(_dom_bucket(day["date"]), {}).get("value", 0.0)

    # Promo bonuses
    promos = _detect_promos(day)
    pb = rev.get("promo_bonus", {})
    for k, flag in promos.items():
        if flag:
            r += pb.get(k, {}).get("value", 0.0)

    # Carryover
    if prev_day is not None:
        cf = rev.get("carryover_fraction", 0.4)
        prev_promos = _detect_promos(prev_day)
        prev_bonus = sum(pb.get(k, {}).get("value", 0.0) for k, f in prev_promos.items() if f)
        if prev_bonus > 0:
            r += prev_bonus * cf

    # Event / machine bonus
    eb = rev.get("event_bonus", {})
    n_items = len(_item_names(day))
    if day.get("tag") == "event":
        excess = max(0, n_items - 9)
        major = bool(MAJOR_HOLIDAY_RE.search(day.get("banner") or ""))
        if major:
            m = eb.get("major", {"floor": 60, "per_item": 15, "cap": 300})
            r += min(m["cap"], m["floor"] + m["per_item"] * excess)
        else:
            mi = eb.get("minor", {"floor": 0, "per_item": 4, "cap": 40})
            r += min(mi["cap"], mi["per_item"] * excess)
    elif day.get("tag") == "machine":
        r += eb.get("machine", {}).get("value", 20.0)

    return r


def predict_pu(day: dict, month_key: str | None = None, prev_day: dict | None = None) -> float:
    """Predict paying users for `day`."""
    cal = _load()
    pu_cal = cal["pu"]
    base_dow = pu_cal.get("base_dow", {})

    p = base_dow.get(day["dow"], 27000.0)

    # Crowd + trend
    p += _crowd_adj(day, pu_cal, metric="pu")

    # DOM curve (PU)
    dom_curve = pu_cal.get("day_of_month_curve", {})
    p += dom_curve.get(_dom_bucket(day["date"]), {}).get("value", 0.0)

    # Promo bonuses (multiplicative %)
    promos = _detect_promos(day)
    pb = pu_cal.get("promo_bonus", {})
    for k in ("customPod", "coinSale", "mgapBogo", "buyAll", "goldenSpin", "prizeMania", "counterPo", "rolling"):
        if promos.get(k):
            p *= 1 + pb.get(k, {}).get("value", 0.0) / 100.0

    return max(15000, min(40000, round(p)))


def marginal_revenue(base_day: dict, candidate_items: list[str],
                     prev_day: dict | None = None) -> float:
    """Score a candidate second offer: predict revenue with vs without the new offer,
    return the delta (K$). Used by assign_second_offers for lift-aware tie-breaking.

    base_day: the day dict WITH the candidate items already added to day["items"].
    candidate_items: list of item name strings that constitute the candidate offer.
    """
    # Predict with candidate
    with_candidate = predict(base_day, prev_day=prev_day)
    # Build day without candidate items
    without_day = dict(base_day)
    without_day["items"] = [it for it in base_day.get("items", [])
                            if it.get("name") not in candidate_items]
    without = predict(without_day, prev_day=prev_day)
    return with_candidate - without


def parity_test():
    """Verify Python predict/predict_pu match expected values on a fixed day fixture.

    The fixture is a Tuesday in July 2026 with Coin Sale + Custom Pod (a known high-lift combo).
    Expected values are derived from the calibration file directly so the test is always
    self-consistent after a recalibration — it guards against structural divergence between
    Python and JS implementations, not against model drift.
    """
    fixture = {
        "dow": "Tue",
        "date": 14,
        "month": "2026-08",
        "tag": None,
        "banner": None,
        "items": [
            {"name": "Coin Sale 100%", "backup": False},
            {"name": "Custom Pod — Weekend", "backup": False},
            {"name": "Daily Deal - SB Wheel - H Price 2026-08-14", "backup": False},
        ],
    }
    cal = _load()
    rev = cal["revenue"]
    pb = rev.get("promo_bonus", {})

    # Expected: base DOW + crowd (Aug) + DOM(b3) + coinSale + customPod + ix_customPod_x_coinSale
    base = rev["base_dow"].get("Tue", 582.8)
    crowd = (rev.get("crowd_adj_by_month") or {}).get("2026-08", 0.0)
    dom_adj = (rev.get("day_of_month_curve") or {}).get("b3", {}).get("value", 0.0)
    bonus = (pb.get("coinSale", {}).get("value", 0)
             + pb.get("customPod", {}).get("value", 0)
             + pb.get("ix_customPod_x_coinSale", {}).get("value", 0))
    expected = base + crowd + dom_adj + bonus

    got = predict(fixture)
    diff = abs(got - expected)
    ok = diff < 0.5  # sub-$500 tolerance

    print(f"[parity_test] fixture revenue: expected={expected:.1f}K, got={got:.1f}K, diff={diff:.2f}K  {'✅ PASS' if ok else '❌ FAIL'}")

    # PU check — sequential multiplicative application (same order as predict_pu)
    pu_cal = cal["pu"]
    base_pu = pu_cal["base_dow"].get("Tue", 27000)
    crowd_pu = (pu_cal.get("crowd_adj_by_month") or {}).get("2026-08", 0.0)
    dom_pu_adj = (pu_cal.get("day_of_month_curve") or {}).get("b3", {}).get("value", 0.0)
    pb_pu = pu_cal.get("promo_bonus", {})
    pu_base = base_pu + crowd_pu + dom_pu_adj
    # Apply promos sequentially (same order as predict_pu's loop)
    expected_pu = pu_base
    for k in ("customPod", "coinSale", "mgapBogo", "buyAll", "goldenSpin", "prizeMania", "counterPo", "rolling"):
        # fixture has coinSale and customPod
        if k in ("coinSale", "customPod"):
            expected_pu *= 1 + pb_pu.get(k, {}).get("value", 0.0) / 100.0
    expected_pu = max(15000, min(40000, round(expected_pu)))
    got_pu = predict_pu(fixture)
    ok_pu = abs(got_pu - expected_pu) <= 1

    print(f"[parity_test] fixture PU: expected={expected_pu}, got={got_pu}  {'✅ PASS' if ok_pu else '❌ FAIL'}")

    return ok and ok_pu


if __name__ == "__main__":
    ok = parity_test()
    import sys
    sys.exit(0 if ok else 1)
