#!/usr/bin/env python3
"""Compute the MM Dashboard's prediction-model constants FRESH from whatever real data
currently exists in real_months.json — this is the "learns and improves every day" piece.

Every time this runs (as part of scripts/daily_update.sh), it recomputes:
  - revenue & PU baselines per day-of-week (exact means from real days)
  - month-level "crowd" adjustment (declining user base), with continuous-trend
    extrapolation for the current/partially-observed month
  - promo-specific $ / PU bonuses (diff-in-means, gated by a minimum sample size so a
    promo seen only 1-2 times doesn't swing the whole model — falls back to a documented
    prior from smart_calendar_insights.md when data is too thin)
  - event/machine bonus density coefficients
  - gameplay (spins / win-rate / sessions) baselines, where DWH data exists
  - coin/gem magnitude patterns

Output: mm_calendar/data/model_calibration.json (embedded into the dashboard at build time).
Re-run this any time real_months.json changes; it never needs hand-editing.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REAL_MONTHS = ROOT / "mm_calendar" / "data" / "real_months.json"
WIDE_REVENUE_PU = ROOT / "mm_calendar" / "data" / "wide_revenue_pu.json"
WIDE_PROMO_KEYS = ROOT / "mm_calendar" / "data" / "wide_promo_keys.json"
OUT = ROOT / "mm_calendar" / "data" / "model_calibration.json"

# 8 documented holiday dates (smart_calendar_insights.md §1) — excluded from "normal day"
# baselines the same way real_months.json's tag="event" days already are, so the wide
# Nov'25-Jul'26 dataset doesn't let Black Friday/New Year/etc. distort the DOW/promo means.
WIDE_HOLIDAYS = {
    "2025-11-28", "2025-11-29",  # Thanksgiving + Black Friday
    "2026-01-01", "2026-01-02",  # New Year
    "2026-02-14",                # Valentine's Day
    "2026-03-17",                # St. Patrick's Day
    "2026-04-04",                # Easter 2026
    "2026-05-05",                # Cinco de Mayo
    "2026-05-25",                # Memorial Day 2026
    "2026-07-04",                # Independence Day 2026
}
# Day-before and day-after proximity (for event decay / lead-up features)
WIDE_HOLIDAYS_EVE = {
    (dt.date.fromisoformat(h) - dt.timedelta(days=1)).isoformat()
    for h in WIDE_HOLIDAYS
}
WIDE_HOLIDAYS_AFTER = {
    (dt.date.fromisoformat(h) + dt.timedelta(days=1)).isoformat()
    for h in WIDE_HOLIDAYS
}

WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
MIN_N_FOR_PURE_DATA = 4  # below this, blend with the documented prior instead of trusting data alone

# ---- Documented priors (fallback when real-data sample is too thin) ----
# Revenue: from smart_calendar_insights.md §2 (242-day clean DOW-matched residuals, 0.8x applied)
REVENUE_PRIORS = {
    "customPod": 30, "coinSale": 14, "decoyBonanza": 15, "mgapBogo": 12, "mgapMatched": -4,
    "mgapWildSymbols": -7, "mgapBigger": 0, "mgapOther": 5,
    "gemback": 10, "rollingMoreForLess": 7, "rolling": 14,
    "prizeMania": 5, "priceCut": -5, "buyAll": -10, "goldenSpin": -30, "counterPo": 8, "snl": 8,
    "happyHour": 15, "extremeStamp": 8, "fortuneDip": 10,
    # Holiday proximity (day before / day after an event — distinct from the event bonus itself)
    "holidayEve": 10,   # lead-up to a holiday: slightly above normal (anticipation spending)
    "holidayAfter": -8, # day after: below normal (hangover / spent-up)
    # Interaction / combo terms (prior = half product_knowledge combo_edge, shrunk).
    # Positive = synergy when co-present; negative = cannibalization.
    "ix_customPod_x_coinSale": 15,      # +44.8K raw combo edge, shrunk conservatively
    "ix_customPod_x_happyHour": 20,     # +63.5K raw combo edge
    "ix_coinSale_x_decoyBonanza": 15,   # +58K raw combo edge
    "ix_mgapBigger_x_coinSale": -8,     # MGAP+Coin Sale cannibalization signal
}
# PU: from smart_calendar_insights.md §4 (242-day ΔPU), as % of that day's base
PU_PRIORS_PCT = {
    "customPod": 1.8, "coinSale": 1.6, "mgapBogo": 1.0, "buyAll": -0.2, "goldenSpin": -4.6,
    "prizeMania": 2.5, "counterPo": 2.0, "rolling": 1.5,
}

PROMO_PATTERNS = {
    "customPod": r"custom pod", "coinSale": r"coins? sale", "decoyBonanza": r"decoy|bonanza",
    "mgapBogo": r"mgap.*bogo|bogo.*mgap", "mgapMatched": r"mgap.*matched",
    "mgapWildSymbols": r"mgap.*wild symbol", "mgapBigger": r"mgap.*bigger",
    # mgapOther: any MGAP variant not classified above (was a JS-only +5K hardcoded term;
    # with 52 days in the wide data it's now calibrated here instead)
    "mgapOther": r"mgap",
    "gemback": r"gemback", "rollingMoreForLess": r"more.for.less|buy.more", "rolling": r"rolling",
    "prizeMania": r"prize mania", "priceCut": r"price cut", "buyAll": r"buy all",
    "goldenSpin": r"golden spin", "counterPo": r"counter po", "snl": r"\bsnl\b",
    "happyHour": r"happy hour|jumbo giveaway|jumbo|prize picker", "extremeStamp": r"extreme stamp",
    "fortuneDip": r"fortune dip",
    # Holiday proximity — not matched via item names; handled via day-level flags in promo_flags
    "holidayEve": None,
    "holidayAfter": None,
}

# Interaction key pairs — product of two base indicators. Order matters: each key name
# encodes which two promos must BOTH be present on the same day.
INTERACTION_PAIRS = [
    ("ix_customPod_x_coinSale",     "customPod",  "coinSale"),
    ("ix_customPod_x_happyHour",    "customPod",  "happyHour"),
    ("ix_coinSale_x_decoyBonanza",  "coinSale",   "decoyBonanza"),
    ("ix_mgapBigger_x_coinSale",    "mgapBigger", "coinSale"),
]

PRICE_FAMILY_PATTERNS = {
    "dailyDeal": r"daily deal|^dd\b",
    "rolling": r"rolling",
    "decoyBonanza": r"decoy|bonanza|triple offer",
    "ryd": r"\bryd\b|reveal your deal",
    "buyAll": r"buy all|mystery buy all",
}
PRICE_TIERS = ("medium", "high", "max")
PRICE_REV_LAMBDA = 180.0
PRICE_PU_LAMBDA = 260.0


def load_days():
    data = json.loads(REAL_MONTHS.read_text(encoding="utf-8"))
    out = []
    for mkey, days in data.items():
        for d in days:
            d = dict(d)
            d["month"] = mkey
            out.append(d)
    out.sort(key=lambda d: d["iso"])
    return out


def live_names(day):
    return [it["name"].lower() for it in day["items"] if not it.get("backup")]


def normalize_pricing(value):
    s = (value or "").strip().lower()
    if s in {"m", "mid", "medium"}:
        return "medium"
    if s in {"h", "high"}:
        return "high"
    if s in {"max", "maximum"}:
        return "max"
    return None


def price_family_for_item(item):
    name = (item.get("name") or "").lower()
    status = (item.get("status") or "").lower()
    if status == "daily deal" or re.search(PRICE_FAMILY_PATTERNS["dailyDeal"], name):
        return "dailyDeal"
    if status == "rolling offer" or re.search(PRICE_FAMILY_PATTERNS["rolling"], name):
        return "rolling"
    if status == "buy all" or re.search(PRICE_FAMILY_PATTERNS["buyAll"], name):
        return "buyAll"
    if status == "ryd" or re.search(PRICE_FAMILY_PATTERNS["ryd"], name):
        return "ryd"
    if re.search(PRICE_FAMILY_PATTERNS["decoyBonanza"], name):
        return "decoyBonanza"
    return None


def pricing_flags(day, keys):
    out = {k: 0 for k in keys}
    for item in day.get("items", []):
        if item.get("backup"):
            continue
        family = price_family_for_item(item)
        tier = normalize_pricing(item.get("pricing"))
        if not family or not tier:
            continue
        key = f"{family}:{tier}"
        if key in out:
            out[key] += 1
    return out


def has(names, pattern):
    rx = re.compile(pattern)
    return any(rx.search(n) for n in names)


def promo_flags(day, keys):
    """Uniform 0/1 promo-presence lookup that works for BOTH day representations:
    real_months.json days (have 'items', matched via PROMO_PATTERNS regex against live_names)
    and wide-dataset days (already pre-classified server-side into '_keys', see load_wide_days).
    Also handles interaction keys (ix_*) as the product of their two constituent indicators.
    Every regression/curve function below goes through this so the two data sources are
    interchangeable."""
    # Build base PROMO_PATTERNS flags first (needed for interaction keys)
    if "_keys" in day:
        base = {k: (1 if (PROMO_PATTERNS.get(k) is not None and k in day["_keys"]) else 0) for k in PROMO_PATTERNS}
        # Wide data from refresh_dwh_snapshots classifies MGAP subtypes before mgapOther.
        # If any specific MGAP variant is present, mgapOther should be 0 to avoid double-count.
        if any(base.get(k) for k in ("mgapBogo","mgapMatched","mgapWildSymbols","mgapBigger")):
            base["mgapOther"] = 0
        # Holiday proximity from day-level flags
        base["holidayEve"] = 1 if day.get("holiday_eve") else 0
        base["holidayAfter"] = 1 if day.get("holiday_after") else 0
    else:
        names = live_names(day)
        full_text = " | ".join(names)
        mgap_text = " | ".join(n for n in names if "mgap" in n)
        base = {}
        specific_mgap_found = False
        for k in ("mgapBogo","mgapMatched","mgapWildSymbols","mgapBigger"):
            pat = PROMO_PATTERNS[k]
            base[k] = 1 if re.search(pat, mgap_text) else 0
            if base[k]:
                specific_mgap_found = True
        for k in PROMO_PATTERNS:
            if k.startswith("mgap"):
                if k not in base:
                    base[k] = 0
                continue
            if PROMO_PATTERNS[k] is None:
                base[k] = 0  # handled below via day-level flags
                continue
            base[k] = 1 if re.search(PROMO_PATTERNS[k], full_text) else 0
        # mgapOther = MGAP present but no specific subtype matched
        if "mgapOther" in PROMO_PATTERNS:
            base["mgapOther"] = 1 if (re.search(r"\bmgap\b", full_text) and not specific_mgap_found) else 0
        # Holiday proximity from day-level flags (set by load_wide_days)
        base["holidayEve"] = 1 if day.get("holiday_eve") else 0
        base["holidayAfter"] = 1 if day.get("holiday_after") else 0

    out = {}
    for k in keys:
        if k.startswith("ix_"):
            # Interaction key — look it up in INTERACTION_PAIRS
            pair = next((p for p in INTERACTION_PAIRS if p[0] == k), None)
            out[k] = 1 if pair and base.get(pair[1], 0) and base.get(pair[2], 0) else 0
        else:
            out[k] = base.get(k, 0)
    return out


def all_promo_keys():
    """Full list of promo feature keys: base PROMO_PATTERNS + interaction pairs."""
    return list(PROMO_PATTERNS.keys()) + [p[0] for p in INTERACTION_PAIRS]


def load_wide_days():
    """Wide, exact-revenue dataset (Nov 1 2025 - Jul 2 2026, ~243 days) pulled live from
    dwh.sm_fact_smart_calendar_promotion_updates (promo classification, server-side ILIKE
    matching into the same PROMO_PATTERNS families) joined with agg.agg_sm_daily_users_stats
    (exact daily revenue + PU count) — see wide_revenue_pu.json / wide_promo_keys.json for the
    exact queries. This is ~3.3x the sample size of real_months.json alone (243 vs ~74 days),
    all EXACT (no diary estimation), and is the reason promo bonuses stopped being almost
    entirely prior-driven — see REV_RIDGE_LAMBDA's note for the before/after.

    Not a replacement for real_months.json: that file still drives the calendar UI itself
    (seasons, banners, backup items, coin/gem/gameplay data this wide pull doesn't have) —
    this is purely an additional, much larger sample for the DOW/promo/day-of-month
    regressions.

    Event/machine tagging: WIDE_HOLIDAYS is a small hand-maintained list of major US holidays,
    used only as a fallback for dates that predate real_months.json's coverage. Wherever
    real_months.json HAS a day for that ISO date, its tag/banner is authoritative and used
    instead — this matters a lot: real_months.json tags plenty of event/machine days
    (Mother's/Father's Day sales, machine sneak-peeks/launches, the pre-4th-of-July stickers
    run) that WIDE_HOLIDAYS never had a chance to know about. Without this, those days silently
    got counted as "normal" days in the DOW baseline / crowd-trend / promo-bonus regressions,
    which is exactly the kind of not-grounded-in-what-we-know contamination that made a
    just-refreshed month (a holiday cluster landing right at the trailing edge of the trend fit)
    swing the crowd adjustment to an unrealistic extreme."""
    if not WIDE_REVENUE_PU.is_file():
        return []
    rev_data = json.loads(WIDE_REVENUE_PU.read_text(encoding="utf-8")).get("days", {})
    key_data = json.loads(WIDE_PROMO_KEYS.read_text(encoding="utf-8")).get("days", {}) if WIDE_PROMO_KEYS.is_file() else {}
    real_tags = {}
    for d in load_days():
        if d.get("tag"):
            real_tags[d["iso"]] = (d["tag"], d.get("banner"))
    out = []
    for iso, v in rev_data.items():
        d = dt.date.fromisoformat(iso)
        keys = set(key_data[iso].split(",")) if key_data.get(iso) else set()
        if iso in real_tags:
            tag, banner = real_tags[iso]
        else:
            tag, banner = ("event" if iso in WIDE_HOLIDAYS else None), None
        # Holiday proximity tags — used as features (not filters) in regression
        holiday_eve = iso in WIDE_HOLIDAYS_EVE and tag != "event"
        holiday_after = iso in WIDE_HOLIDAYS_AFTER and tag != "event"
        out.append({
            "iso": iso, "date": d.day, "dow": WEEKDAYS[(d.weekday() + 1) % 7],
            "month": f"{d.year}-{d.month:02d}",
            "actualRev": v["rev"], "actualPU": v["pu"],
            "tag": tag, "banner": banner,
            "holiday_eve": holiday_eve, "holiday_after": holiday_after,
            "_keys": keys, "_source": "wide",
        })
    out.sort(key=lambda d: d["iso"])
    return out


REVENUE_REGRESSION_WINDOW_DAYS = 90
PU_REGRESSION_WINDOW_DAYS = 60
# Metric-specific trailing windows selected by grid search over all available DWH history
# (Nov 2025-Jul 2026, 246 days). Revenue optimal at 90d (CV=7.07%); PU optimal at 60d (CV=5.46%).
# Both windows slide forward automatically and are re-tested as more data accumulates.
# Set REGRID_ON_STARTUP=True to re-run the grid search every calibration run (slow ~30s).
REGRID_ON_STARTUP = False


def grid_search_windows(today_month_key, event_bonus, windows=(30, 45, 60, 75, 90, 105, 120, 150, 180, 246)):
    """Re-grid-search the CV-optimal trailing window for revenue and PU.
    Returns (best_rev_window, best_rev_cv, best_pu_window, best_pu_cv).
    Called from main() when REGRID_ON_STARTUP=True or via --regrid CLI flag."""
    best_rev = (REVENUE_REGRESSION_WINDOW_DAYS, 999.0)
    best_pu = (PU_REGRESSION_WINDOW_DAYS, 999.0)
    for w in windows:
        try:
            rdays = [d for d in build_regression_dataset(w) if d.get("actualRev") is not None]
            if len(rdays) < 20:
                continue
            for d in rdays:
                d["_revK"] = d["actualRev"] / 1000
            bd, _ = compute_base_dow(rdays, "_revK")
            cr, tr = compute_month_crowd(rdays, bd, "_revK", today_month_key)
            cv_e, _ = cross_validate_revenue(rdays, bd, cr, tr, today_month_key, event_bonus)
            if cv_e is not None and cv_e < best_rev[1]:
                best_rev = (w, cv_e)
        except Exception:
            pass
        try:
            pdays = [d for d in build_regression_dataset(w) if d.get("actualPU") is not None]
            if len(pdays) < 15:
                continue
            bd_p, _ = compute_base_dow(pdays, "actualPU")
            cp, tp = compute_month_crowd(pdays, bd_p, "actualPU", today_month_key)
            pb = compute_promo_bonus_pu(pdays, bd_p, cp)
            cv_p, _ = cross_validate_pu(pdays, bd_p, cp, tp, today_month_key)
            if cv_p is not None and cv_p < best_pu[1]:
                best_pu = (w, cv_p)
        except Exception:
            pass
    return best_rev[0], best_rev[1], best_pu[0], best_pu[1]


def build_regression_dataset(window_days):
    """Merge the wide DWH dataset with real_months.json for the DOW / promo-bonus /
    day-of-month regressions: wide data wins on any date it covers (exact > diary-estimated),
    real_months.json fills in the rest (currently just the tail of July not yet in the wide
    pull, and any future days once real_months.json gets ahead of the last wide refresh).
    Restricted to a metric-specific trailing window — see constants above."""
    wide = load_wide_days()
    wide_isos = {d["iso"] for d in wide}
    supplement = [d for d in load_days() if d["iso"] not in wide_isos and d.get("actualRev") is not None]
    merged = wide + supplement
    merged.sort(key=lambda d: d["iso"])
    cutoff = (dt.date.today() - dt.timedelta(days=window_days)).isoformat()
    return [d for d in merged if d["iso"] >= cutoff]


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def compute_base_dow(days, value_key):
    """Mean actual value per weekday, excluding event/machine days (keeps the baseline
    representing a 'normal' day; event bonuses are modeled separately)."""
    by_dow = {w: [] for w in WEEKDAYS}
    for d in days:
        v = d.get(value_key)
        if v is None or d.get("tag"):
            continue
        by_dow[d["dow"]].append(v)
    base = {}
    n_by_dow = {}
    overall = [v for lst in by_dow.values() for v in lst]
    fallback = mean(overall) if overall else 0
    for w in WEEKDAYS:
        vals = by_dow[w]
        base[w] = round(mean(vals), 1) if vals else round(fallback, 1)
        n_by_dow[w] = len(vals)
    return base, n_by_dow


MIN_DAYS_FOR_FLAT_MONTH = 10  # below this, a month's own mean is too noisy/contaminated by
# individual promo days (e.g. July with 1 real day showed +112K "crowd" just because that
# one day happened to run MGAP BOGO — that's a promo effect, not a crowd-size effect).
# Use the cross-month trend line instead for thinly-observed months.


def compute_month_crowd(days, base_dow, value_key, today_month_key):
    """Flat mean residual per month for well-observed months (>=MIN_DAYS_FOR_FLAT_MONTH real
    days — enough for individual promo-day noise to average out). For thinly-observed months
    (a month that just started), a single day's residual is contaminated by whatever promo
    ran that day, so use a continuous linear trend fit across the trailing real days instead,
    evaluated at that month's own days — this is also what lets the current month's forecast
    keep declining smoothly day-by-day rather than freezing at one anchor point."""
    by_month = {}
    all_resid = []
    for d in days:
        v = d.get(value_key)
        if v is None or d.get("tag"):
            continue
        resid = v - base_dow[d["dow"]]
        by_month.setdefault(d["month"], []).append((d["date"], resid))
        try:
            iso_date = dt.date.fromisoformat(d["iso"])
            all_resid.append((iso_date.toordinal(), resid))
        except ValueError:
            pass
    all_resid.sort()

    # Fit trend on the trailing ~21 real days (recency-weighted without a full time-decay
    # model — 21 was chosen to match the exact-DWH window size that first surfaced this
    # decline; a much longer window dilutes a recent inflection with older, less relevant
    # history).
    trailing = all_resid[-21:] if len(all_resid) >= 6 else all_resid
    slope, intercept = 0.0, (mean([y for _, y in trailing]) if trailing else 0.0)
    if len(trailing) >= 6:
        xs = [x for x, _ in trailing]
        ys = [y for _, y in trailing]
        mx, my = mean(xs), mean(ys)
        den = sum((x - mx) ** 2 for x in xs)
        if den:
            slope = sum((x - mx) * (y - my) for x, y in trailing) / den
            intercept = my - slope * mx

    crowd = {}
    trend_per_day = {}
    for mkey, pairs in by_month.items():
        n = len(pairs)
        if n >= MIN_DAYS_FOR_FLAT_MONTH:
            crowd[mkey] = round(mean([r for _, r in pairs]), 1)
        else:
            # Thin month: evaluate the trend line at this month's first day-of-month=1
            # ordinal, rather than trusting the noisy 1-2 raw points directly.
            y, m = int(mkey[:4]), int(mkey[5:7])
            anchor_ord = dt.date(y, m, 1).toordinal()
            crowd[mkey] = round(slope * anchor_ord + intercept, 1)
    trend_per_day[today_month_key] = round(slope, 3)
    return crowd, trend_per_day


# ---- Pure-Python ridge regression (no numpy available in this environment) ----
# Why: the old diff-in-means approach fits each promo's bonus in ISOLATION — "mean residual
# on days X is present" minus "mean residual on days X is absent". That has a real
# confounding problem: promos that frequently co-occur (e.g. Custom Pod often lands on the
# same days as a Coin Sale) each get credited with the OTHER's effect too, since diff-in-means
# never controls for what else was running that day. A joint multivariate regression across
# ALL promo indicators at once lets each promo's coefficient reflect its effect holding the
# others constant — the standard fix for this kind of confounding. Ridge-regularized (shrunk
# toward the documented priors, same spirit as the old empirical-Bayes blending) so it stays
# stable even with 18 correlated predictors and ~70 rows.
def _mat_transpose(m):
    return [list(row) for row in zip(*m)]


def _mat_mul(a, b):
    bt = _mat_transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def _mat_vec(a, v):
    return [sum(x * y for x, y in zip(row, v)) for row in a]


def _solve_linear(a, b):
    """Gaussian elimination with partial pivoting. a: NxN, b: length-N. Returns length-N x."""
    n = len(a)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            continue
        m[col], m[pivot] = m[pivot], m[col]
        pv = m[col][col]
        m[col] = [x / pv for x in m[col]]
        for r in range(n):
            if r != col and abs(m[r][col]) > 1e-15:
                factor = m[r][col]
                m[r] = [x - factor * y for x, y in zip(m[r], m[col])]
    return [m[i][n] for i in range(n)]


REV_RIDGE_LAMBDA = 800.0
PU_RIDGE_LAMBDA = 1200.0
KNOWLEDGE_START_DATE = "2026-01-01"


def ridge_regress(rows, y, priors, lam=120.0):
    """Solve min ||y - Xb||^2 + lam*||b - priors||^2. rows: list of feature-vectors (each a
    list of 0/1s), y: list of targets, priors: list of prior values per column."""
    if not rows:
        return list(priors)
    n_cols = len(rows[0])
    xt = _mat_transpose(rows)
    xtx = _mat_mul(xt, rows)
    for i in range(n_cols):
        xtx[i][i] += lam
    xty = _mat_vec(xt, y)
    rhs = [xty[i] + lam * priors[i] for i in range(n_cols)]
    return _solve_linear(xtx, rhs)


def compute_promo_bonus_revenue(days, base_dow, crowd_by_month):
    """Joint ridge regression across all promo indicators simultaneously (see note above),
    on the residual after DOW+crowd. Includes interaction/combo features (ix_*) so synergistic
    pairs (customPod+coinSale, customPod+happyHour) and cannibalization pairs (MGAP+CoinSale)
    get calibrated coefficients rather than fixed hardcoded terms."""
    keys = all_promo_keys()
    rows, y, presence = [], [], {k: 0 for k in keys}
    for d in days:
        if d.get("actualRev") is None or d.get("tag"):
            continue
        flags = promo_flags(d, keys)
        base = base_dow[d["dow"]] + crowd_by_month.get(d["month"], 0)
        resid = d["actualRev"] / 1000 - base
        row = [float(flags[k]) for k in keys]
        for k in keys:
            if flags[k]:
                presence[k] += 1
        rows.append(row)
        y.append(resid)

    priors = [REVENUE_PRIORS.get(k, 0) for k in keys]
    coefs = ridge_regress(rows, y, priors, lam=REV_RIDGE_LAMBDA)
    out = {}
    for i, k in enumerate(keys):
        n = presence[k]
        basis = "data" if n >= MIN_N_FOR_PURE_DATA else ("blended" if n > 0 else "prior")
        out[k] = {"value": round(coefs[i], 1), "n": n, "basis": basis}
    return out


def compute_promo_bonus_pu(days, base_dow, crowd_by_month):
    """Same joint-regression approach as revenue, in %-of-base units."""
    keys = list(PU_PRIORS_PCT.keys())
    rows, y, presence = [], [], {k: 0 for k in keys}
    for d in days:
        if d.get("actualPU") is None or d.get("tag"):
            continue
        flags = promo_flags(d, keys)
        base = base_dow[d["dow"]] + crowd_by_month.get(d["month"], 0)
        if base <= 0:
            continue
        resid_pct = (d["actualPU"] - base) / base * 100
        row = [float(flags[k]) for k in keys]
        for k in keys:
            if flags[k]:
                presence[k] += 1
        rows.append(row)
        y.append(resid_pct)

    priors = [PU_PRIORS_PCT[k] for k in keys]
    coefs = ridge_regress(rows, y, priors, lam=PU_RIDGE_LAMBDA)  # also cross-validated, see below
    out = {}
    for i, k in enumerate(keys):
        n = presence[k]
        basis = "data" if n >= MIN_N_FOR_PURE_DATA else ("blended" if n > 0 else "prior")
        out[k] = {"value": round(coefs[i], 2), "n": n, "basis": basis}
    return out


DOM_BUCKETS = [
    ("b1", lambda dt_: dt_ <= 2), ("b2", lambda dt_: dt_ <= 7), ("b3", lambda dt_: dt_ <= 14),
    ("b4", lambda dt_: dt_ <= 21), ("b5", lambda dt_: dt_ <= 28), ("b6", lambda dt_: True),
]
DOM_SHRINKAGE_K = 0.0  # cross-validated (5-fold, multi-seed): a data-fit day-of-month curve
# beats the old hand-fixed shape (+25/+12/0/-10/0/-12) at every shrinkage level tested from 0
# to 8 on the refreshed DWH-backed dataset. With the revenue window shortened to 105 days,
# the unshrunk curve (K=0) now has the best held-out revenue CV, so use it until the next
# scheduled grid-search says otherwise.


def dom_bucket(date):
    for key, test in DOM_BUCKETS:
        if test(date):
            return key
    return "b6"


def compute_day_of_month_curve(days, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus):
    """Mean residual after DOW+crowd+promo, grouped by day-of-month position, shrunk toward 0.
    Replaces the old fixed +25/+12/0/-10/0/-12 shape — with 74 real days spanning 4 months this
    is now directly measurable, and it turned out to be quite different from the old hand-fit
    guess (week 1 is actually a net NEGATIVE vs DOW baseline, not positive; month-end is a much
    deeper dip than -12). See DOM_SHRINKAGE_K note above for validation."""
    buckets = {k: [] for k, _ in DOM_BUCKETS}
    keys = list(PROMO_PATTERNS.keys())
    for d in days:
        if d.get("actualRev") is None or d.get("tag"):
            continue
        base = base_dow[d["dow"]] + crowd_by_month.get(d["month"], 0)
        if d["month"] == today_month_key and d["date"] > 1:
            base += trend_by_month.get(today_month_key, 0) * (d["date"] - 1)
        flags = promo_flags(d, keys)
        for key in keys:
            if flags[key]:
                base += promo_bonus[key]["value"]
        buckets[dom_bucket(d["date"])].append(d["actualRev"] / 1000 - base)
    out = {}
    for key, vals in buckets.items():
        n = len(vals)
        m = mean(vals) if vals else 0.0
        w = n / (n + DOM_SHRINKAGE_K) if n else 0.0
        out[key] = {"value": round(w * m, 1), "n": n}
    return out


def compute_event_bonus(days, base_dow, crowd_by_month):
    """Fit major/minor holiday bonus as (floor + per_item*excess_items), separately for
    major (flagship) vs minor holidays, from real event-tagged days. Falls back to the
    v6.2 hand-fit values when too few real event days exist to refit confidently."""
    major_re = re.compile(r"cinco de mayo|black friday|new year|valentine|st\.? ?patrick|independence day|4th of july|memorial day", re.I)
    major_pts, minor_pts = [], []
    machine_vals = []
    for d in days:
        if d.get("actualRev") is None:
            continue
        base = base_dow[d["dow"]] + crowd_by_month.get(d["month"], 0)
        resid = d["actualRev"] / 1000 - base
        n_items = len([it for it in d["items"] if not it.get("backup")])
        excess = max(0, n_items - 9)
        if d.get("tag") == "event":
            if major_re.search(d.get("banner") or ""):
                major_pts.append((excess, resid))
            else:
                minor_pts.append((excess, resid))
        elif d.get("tag") == "machine":
            machine_vals.append(resid)

    def fit_floor_rate(pts, default_floor, default_rate, default_cap):
        if len(pts) < 2:
            return {"floor": default_floor, "per_item": default_rate, "cap": default_cap, "n": len(pts)}
        xs = [x for x, _ in pts]
        ys = [y for _, y in pts]
        mx, my = mean(xs), mean(ys)
        den = sum((x - mx) ** 2 for x in xs)
        rate = (sum((x - mx) * (y - my) for x, y in pts) / den) if den else default_rate
        floor = my - rate * mx
        # Sanity clamp — a handful of real points shouldn't be able to produce an absurd
        # extrapolation; keep within a reasonable band of the documented defaults.
        rate = max(2, min(30, rate))
        floor = max(20, min(150, floor))
        return {"floor": round(floor, 1), "per_item": round(rate, 2), "cap": default_cap, "n": len(pts)}

    major = fit_floor_rate(major_pts, 60, 15, 300)
    minor = fit_floor_rate(minor_pts, 0, 4, 40)
    machine = {"value": round(mean(machine_vals), 1) if machine_vals else 20, "n": len(machine_vals)}
    return {"major": major, "minor": minor, "machine": machine}


def compute_carryover_absorption(rev_days_sorted, base_dow, crowd_by_month, trend_by_month,
                                  today_month_key, promo_bonus, event_bonus, dom_curve,
                                  default_carryover=0.4, default_absorption=-18):
    """Fit carryover_fraction and absorption_penalty from data rather than using hardcoded values.

    carryover_fraction: fraction of the previous day's total promo bonus that bleeds into the
    next day. Estimated as the OLS slope of (next_day_residual vs prev_day_promo_bonus) on
    consecutive non-event days with non-trivial promo activity the day before.

    absorption_penalty: additional suppression on a non-event day that follows a standalone
    Coin Sale. Models the 'spent up' effect where players who bought coins yesterday buy less
    today. Estimated as the mean residual on such days after subtracting expected carryover.
    """
    keys = all_promo_keys()
    pair_xs, pair_ys = [], []     # (prev_promo_sum, next_residual)
    absorption_resids = []

    for i in range(1, len(rev_days_sorted)):
        cur = rev_days_sorted[i]
        prev = rev_days_sorted[i - 1]
        if cur.get("tag") or cur.get("actualRev") is None:
            continue
        if prev.get("actualRev") is None:
            continue
        # Must be truly consecutive calendar days
        try:
            gap = dt.date.fromisoformat(cur["iso"]).toordinal() - dt.date.fromisoformat(prev["iso"]).toordinal()
        except Exception:
            continue
        if gap != 1:
            continue

        # Predict today without carryover
        pred = simulate_predict(cur, base_dow, crowd_by_month, trend_by_month, today_month_key,
                                promo_bonus, event_bonus, dom_curve)
        residual = cur["actualRev"] / 1000 - pred

        prev_flags = promo_flags(prev, keys)
        prev_promo = sum(promo_bonus.get(k, {}).get("value", 0) * prev_flags.get(k, 0) for k in keys)

        if abs(prev_promo) > 2:   # only pairs where carryover would be meaningful
            pair_xs.append(prev_promo)
            pair_ys.append(residual)

        # Absorption: prev was a plain Coin Sale day (no tag, no event)
        prev_all = promo_flags(prev, keys)
        if (prev_all.get("coinSale") and not prev_all.get("customPod")
                and not prev.get("tag") and not cur.get("tag")):
            # Residual after expected carryover
            carryover_component = prev_promo * default_carryover
            absorption_resids.append(residual - carryover_component)

    # Fit carryover fraction
    carryover = default_carryover
    if len(pair_xs) >= 8:
        mx, my = mean(pair_xs), mean(pair_ys)
        num = sum((x - mx) * (y - my) for x, y in zip(pair_xs, pair_ys))
        den = sum((x - mx) ** 2 for x in pair_xs)
        if den > 0:
            raw = num / den
            carryover = round(max(0.10, min(0.70, raw)), 3)

    # Fit absorption penalty
    absorption = default_absorption
    if len(absorption_resids) >= 4:
        raw = mean(absorption_resids)
        absorption = round(max(-60.0, min(0.0, raw)), 1)

    return {
        "carryover_fraction": carryover,
        "carryover_n": len(pair_xs),
        "absorption_penalty": absorption,
        "absorption_n": len(absorption_resids),
        "basis": "data" if len(pair_xs) >= 8 else "prior",
    }


SINK_KEYS_FILE = ROOT / "mm_calendar" / "data" / "sink_mechanic_keys.json"
COIN_SINK_KEYS = [
    "pyp", "mesTokens", "spinnerClash", "aceCardLoot", "customPod", "clanPoints",
    "dashChallenge", "machine", "winMaster", "spinZone", "jackpot", "megaWinner",
]
GEM_SINK_KEYS = ["shortTerm", "midTerm", "album", "shinyShow"]
COIN_SINK_LABEL = {
    "pyp": "PYP", "mesTokens": "M.E.S Tokens/Steps", "spinnerClash": "Spinner Clash",
    "aceCardLoot": "Ace/Card Loot", "customPod": "Custom Pod", "clanPoints": "Clan points/badges",
    "dashChallenge": "Dash Challenge", "machine": "Gameplay machine", "winMaster": "Win Master",
    "spinZone": "Spin Zone", "jackpot": "Jackpot (MES)", "megaWinner": "Mega Winner"
}
GEM_SINK_LABEL = {
    "shortTerm": "Short Term", "midTerm": "Mid Term", "album": "Album", "shinyShow": "Shiny Show"
}
SINK_FAMILY_LABEL = {
    **COIN_SINK_LABEL,
    **GEM_SINK_LABEL,
}


def load_sink_keys():
    """Coin/gem SINK mechanics (PYP, M.E.S, Spinner Clash, Ace/Card Loot, Custom Pod, Clan
    Dash/points, gameplay machines, Win Master, Spin Zone, Jackpot, Mega Winner = coin sinks;
    Shiny Show, Sneak Peek = gem sinks) — pulled from the same DWH table as wide_promo_keys.json
    but classified into GAMEPLAY/SINK families, matching dashboard_app.js's classify()
    'gameplay' category. Critically different from PROMO_PATTERNS (which is purchase/injection
    offers — Coin Sale, Buy All, MGAP, Rolling — the right regressor set for the REVENUE tab,
    but the WRONG one for 'what drains the coin/gem economy', which is what Core/Gems are
    about). See sink_mechanic_keys.json for the exact query."""
    if not SINK_KEYS_FILE.is_file():
        return {}
    return json.loads(SINK_KEYS_FILE.read_text(encoding="utf-8")).get("days", {})


def sink_flags(day, keys, sink_keys_by_iso):
    present = set((sink_keys_by_iso.get(day["iso"]) or "").split(",")) if sink_keys_by_iso.get(day["iso"]) else set()
    season_statuses = {s.get("status") for s in day.get("seasons", [])}
    if "Short Term" in season_statuses:
        present.add("shortTerm")
    if "Mid Term" in season_statuses:
        present.add("midTerm")
    if "Album" in season_statuses:
        present.add("album")
    return {k: (1 if k in present else 0) for k in keys}


ECON_RIDGE_LAMBDA = 200.0  # cross-validated (5-fold, multi-seed, see cross_validate_economy):
# promo composition adds ESSENTIALLY NOTHING beyond the plain DOW baseline for predicting
# PU balance % change — held-out error is ~29pp (coin) / ~10pp (gem) whether or not promo
# terms are included at all, and only gets marginally WORSE as lambda decreases (i.e. as the
# model is allowed to actually use the promo data). Honest conclusion: this metric is mostly
# unexplained day-to-day noise once DOW is accounted for — heavy shrinkage reflects that
# rather than pretending precision that isn't there. Revisit as more days accumulate.


def compute_economy_curve(days, mag_key, source_key, keys, lam=ECON_RIDGE_LAMBDA):
    """DOW baseline + joint-regression promo deltas for Active-PU balance velocity.

    Source: agg.agg_sm_daily_user_currency_balance filtered to pu_segment='Active PU' and
    non-Playtika users, matching the Tableau Velocity / Balance / Index / Consumption style
    of economy analysis more closely than daily_payments>0. The metric is today's end-of-day
    median balance vs yesterday's end-of-day median. Same-day start->end remains a secondary
    diagnostic, not the planning signal."""
    econ_days = [d for d in days if d.get(source_key) == "active_pu_balance_dwh" and d.get(mag_key) is not None]
    by_dow = {w: [] for w in WEEKDAYS}
    for d in econ_days:
        by_dow[d["dow"]].append(d[mag_key])
    overall = [v for lst in by_dow.values() for v in lst]
    fallback = mean(overall) if overall else 0.0
    base_dow = {w: round(mean(by_dow[w]), 2) if by_dow[w] else round(fallback, 2) for w in WEEKDAYS}
    n_dow = {w: len(by_dow[w]) for w in WEEKDAYS}

    sink_keys_by_iso = load_sink_keys()
    priors = [0.0 for _ in keys]

    rows, y, presence = [], [], {k: 0 for k in keys}
    for d in econ_days:
        flags = sink_flags(d, keys, sink_keys_by_iso)
        row = [float(flags[k]) for k in keys]
        rows.append(row)
        y.append(d[mag_key] - base_dow[d["dow"]])
        for k in keys:
            if flags[k]:
                presence[k] += 1
    coefs = ridge_regress(rows, y, priors, lam=lam) if rows else priors
    promo_delta = {}
    for i, k in enumerate(keys):
        n = presence[k]
        basis = "data" if n >= MIN_N_FOR_PURE_DATA else ("blended" if n > 0 else "no-data")
        promo_delta[k] = {"value": round(coefs[i], 2), "n": n, "basis": basis}
    return base_dow, n_dow, promo_delta, len(econ_days)


def cross_validate_economy(days, mag_key, source_key, keys, lam=ECON_RIDGE_LAMBDA, k=5, seeds=(7, 11, 42, 99, 123)):
    """Honest held-out check for the economy model — same multi-seed 5-fold approach as
    cross_validate_revenue. Compares full model (DOW+promo) against DOW-only, so we can see
    whether promo composition adds anything beyond day-of-week for this metric."""
    import random
    econ_days = [d for d in days if d.get(source_key) == "active_pu_balance_dwh" and d.get(mag_key) is not None]
    if len(econ_days) < k * 2:
        return None, None, 0
    sink_keys_by_iso = load_sink_keys()
    priors = [0.0 for _ in keys]

    def row_for(d):
        flags = sink_flags(d, keys, sink_keys_by_iso)
        return [float(flags[k]) for k in keys]

    errs_full, errs_dow_only = [], []
    for seed in seeds:
        rng = random.Random(seed)
        order = list(range(len(econ_days)))
        rng.shuffle(order)
        folds = [order[i::k] for i in range(k)]
        for fold in folds:
            test_idx = set(fold)
            train = [econ_days[i] for i in order if i not in test_idx]
            by_dow = {w: [] for w in WEEKDAYS}
            for d in train:
                by_dow[d["dow"]].append(d[mag_key])
            overall = [v for lst in by_dow.values() for v in lst]
            fb = mean(overall) if overall else 0.0
            base_dow = {w: mean(by_dow[w]) if by_dow[w] else fb for w in WEEKDAYS}
            rows = [row_for(d) for d in train]
            y = [d[mag_key] - base_dow[d["dow"]] for d in train]
            coefs = ridge_regress(rows, y, priors, lam=lam)
            for i in order:
                if i not in test_idx:
                    continue
                d = econ_days[i]
                actual = d[mag_key]
                pred_full = base_dow[d["dow"]] + sum(c * x for c, x in zip(coefs, row_for(d)))
                pred_dow = base_dow[d["dow"]]
                errs_full.append(abs(actual - pred_full))
                errs_dow_only.append(abs(actual - pred_dow))
    return mean(errs_full), mean(errs_dow_only), len(errs_full)


def compute_gameplay(days):
    """Spins/win-rate/sessions baselines — only ever available for the 21-day exact DWH
    window (no live DB access to extend this), so explicitly thin. Kept separate from
    revenue/PU so the UI can show the right confidence level."""
    by_dow = {w: {"spinners": [], "spins_per": [], "win_rate": [], "sessions": []} for w in WEEKDAYS}
    for d in days:
        gp = d.get("gameplay")
        if not gp:
            continue
        b = by_dow[d["dow"]]
        b["spinners"].append(gp["spinners"])
        b["spins_per"].append(gp["spinsPerSpinner"])
        b["win_rate"].append(gp["winRate"])
        b["sessions"].append(gp["sessionsPerUser"])
    out = {}
    n_total = 0
    for w in WEEKDAYS:
        b = by_dow[w]
        n_total += len(b["spinners"])
        out[w] = {
            "spinners": round(mean(b["spinners"]), 0) if b["spinners"] else None,
            "spinsPerSpinner": round(mean(b["spins_per"]), 0) if b["spins_per"] else None,
            "winRate": round(mean(b["win_rate"]), 1) if b["win_rate"] else None,
            "sessionsPerUser": round(mean(b["sessions"]), 2) if b["sessions"] else None,
        }
    return out, n_total


MAJOR_HOLIDAY_RE = re.compile(r"cinco de mayo|black friday|new year|valentine|st\.? ?patrick|independence day|4th of july|memorial day", re.I)


def n_items_for(day):
    """Item-density proxy for the event/machine bonus — real_months.json days have a full
    'items' list (every board item); wide-dataset days only have classified family '_keys'
    (a smaller count by construction, since untracked items aren't in the ~19 families we
    match). Only matters for the handful of holiday-tagged days in the wide dataset during
    cross-validation; compute_event_bonus itself is still fit exclusively on real_months.json
    where the true item count is available."""
    if "_keys" in day:
        return len(day["_keys"])
    return len([it for it in day.get("items", []) if not it.get("backup")])


def simulate_predict(day, base_dow, crowd_by_month, trend_by_month, today_month_key,
                     promo_bonus, event_bonus, dom_curve=None,
                     pricing_adjustments=None, prev_day=None, carryover_fraction=0.4):
    """Python port of predict()'s core. Now includes optional carryover from prev_day and
    pricing adjustments — both are needed for an honest CV that matches the live predict() path.
    prev_day should be the day dict for yesterday (or None for the first day)."""
    rev = base_dow[day["dow"]]
    base = crowd_by_month.get(day["month"], 0)
    if day["month"] == today_month_key and day["date"] > 1:
        base += trend_by_month.get(today_month_key, 0) * (day["date"] - 1)
    rev += base
    if dom_curve:
        rev += dom_curve.get(dom_bucket(day["date"]), {}).get("value", 0)
    keys = all_promo_keys()
    flags = promo_flags(day, keys)
    for key in keys:
        if flags[key]:
            rev += promo_bonus.get(key, {}).get("value", 0)
    # Carryover: fraction of yesterday's promo bonus bleeds into today's revenue
    if prev_day is not None:
        prev_flags = promo_flags(prev_day, keys)
        prev_promo_sum = sum(promo_bonus.get(k, {}).get("value", 0) for k in keys if prev_flags.get(k))
        if prev_promo_sum > 0:
            rev += prev_promo_sum * carryover_fraction
    # Pricing effect (only available for real_months.json days)
    if pricing_adjustments:
        rev += pricing_component(day, pricing_adjustments)
    n_items = n_items_for(day)
    if day.get("tag") == "event":
        excess = max(0, n_items - 9)
        major = bool(MAJOR_HOLIDAY_RE.search(day.get("banner") or ""))
        eb = event_bonus["major"] if major else event_bonus["minor"]
        rev += min(eb["cap"], eb["floor"] + eb["per_item"] * excess) if major else min(eb["cap"], eb["per_item"] * excess)
    elif day.get("tag") == "machine":
        rev += event_bonus["machine"]["value"]
    return rev


def self_validate(rev_days, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus, event_bonus, dom_curve=None):
    """IN-SAMPLE fit quality (same data used to fit) — always looks better than reality
    because ridge regression is doing its job of fitting the training data. Reported
    alongside the honest cross-validated number below, never instead of it."""
    errs = []
    for d in rev_days:
        pred = simulate_predict(d, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus, event_bonus, dom_curve)
        actual = d["actualRev"] / 1000
        if pred > 0:
            errs.append(abs(actual - pred) / pred * 100)
    return (mean(errs), len(errs)) if errs else (None, 0)


def cross_validate_revenue(rev_days_all, base_dow, crowd_by_month, trend_by_month, today_month_key, event_bonus, k=5, seeds=(7, 11, 42, 99, 123)):
    """HONEST accuracy estimate: refits promo-bonus regression, day-of-month curve, AND the
    DOW baseline / crowd-by-month INSIDE each fold (previously those leaked from the full
    dataset). Also includes carryover component when scoring test days, matching the live
    predict() path more closely. Averaged over several random fold-splits to reduce noise."""
    import random
    if len(rev_days_all) < k * 2:
        return None, 0
    keys = all_promo_keys()
    priors = [REVENUE_PRIORS.get(key, 0) for key in keys]
    # Build an index: iso -> sorted position (for carryover prev-day lookup)
    iso_to_pos = {d["iso"]: i for i, d in enumerate(rev_days_all)}

    def row_for(d):
        flags = promo_flags(d, keys)
        return [float(flags[k]) for k in keys]

    all_errs = []
    for seed in seeds:
        rng = random.Random(seed)
        order = list(range(len(rev_days_all)))
        rng.shuffle(order)
        folds = [order[i::k] for i in range(k)]
        for fold in folds:
            test_idx = set(fold)
            train_days = [rev_days_all[i] for i in order if i not in test_idx and not rev_days_all[i].get("tag")]
            if not train_days:
                continue
            # Refit DOW baseline inside this fold (fixes CV leakage)
            fold_base_dow, _ = compute_base_dow(train_days, "actualRev")
            fold_base_dow = {k_: round(v / 1000, 1) for k_, v in fold_base_dow.items()}
            for td in train_days:
                td["_revK"] = td["actualRev"] / 1000
            fold_base_dow_k, _ = compute_base_dow(train_days, "_revK")
            fold_crowd, fold_trend = compute_month_crowd(train_days, fold_base_dow_k, "_revK", today_month_key)
            rows = [row_for(d) for d in train_days]
            y = [d["actualRev"] / 1000 - (fold_base_dow_k[d["dow"]] + fold_crowd.get(d["month"], 0)) for d in train_days]
            coefs = ridge_regress(rows, y, priors, lam=REV_RIDGE_LAMBDA)
            fold_promo_bonus = {key: {"value": coefs[i]} for i, key in enumerate(keys)}
            fold_dom_curve = compute_day_of_month_curve(train_days, fold_base_dow_k, fold_crowd, fold_trend, today_month_key, fold_promo_bonus)
            for i in order:
                if i not in test_idx:
                    continue
                d = rev_days_all[i]
                # Find prev day for carryover
                pos = iso_to_pos.get(d["iso"])
                prev_d = rev_days_all[pos - 1] if pos is not None and pos > 0 else None
                pred = simulate_predict(d, fold_base_dow_k, fold_crowd, fold_trend, today_month_key,
                                        fold_promo_bonus, event_bonus, fold_dom_curve, prev_day=prev_d)
                actual = d["actualRev"] / 1000
                if pred > 0:
                    all_errs.append(abs(actual - pred) / pred * 100)
    return (mean(all_errs), len(all_errs)) if all_errs else (None, 0)


def simulate_predict_pu(day, base_dow, crowd_by_month, trend_by_month, today_month_key,
                        promo_bonus, dom_curve=None, prev_day=None, carryover_fraction=0.4):
    """PU prediction: DOW + crowd/trend + promo bonuses (multiplicative %) + optional DOM curve
    and carryover. Structurally symmetric with simulate_predict now so CV covers the full path."""
    pred = base_dow[day["dow"]] + crowd_by_month.get(day["month"], 0)
    if day["month"] == today_month_key and day["date"] > 1:
        pred += trend_by_month.get(today_month_key, 0) * (day["date"] - 1)
    if dom_curve:
        # PU DOM curve is applied additively in absolute PU count (not %)
        pred += dom_curve.get(dom_bucket(day["date"]), {}).get("value", 0)
    flags = promo_flags(day, list(PU_PRIORS_PCT.keys()))
    for key in PU_PRIORS_PCT.keys():
        if flags[key]:
            pred *= 1 + promo_bonus.get(key, {}).get("value", 0) / 100
    # Carryover: fraction of yesterday's PU promo bonus bleeds into today
    if prev_day is not None:
        prev_keys = list(PU_PRIORS_PCT.keys())
        prev_flags = promo_flags(prev_day, prev_keys)
        # Compute prev base PU for scaling
        prev_base = base_dow[prev_day["dow"]] + crowd_by_month.get(prev_day["month"], 0)
        if prev_base > 0:
            prev_pct_bonus = sum(promo_bonus.get(k, {}).get("value", 0) for k in prev_keys if prev_flags.get(k))
            pred += prev_base * (prev_pct_bonus / 100) * carryover_fraction * 0.5  # PU carryover is weaker
    return pred


def event_component(day, event_bonus):
    """Return the event/machine component used by simulate_predict, without the rest of the
    forecast. This lets the current-month nowcast shrink a holiday uplift when the first
    observed day of that event materially underperforms the historical holiday curve."""
    n_items = n_items_for(day)
    if day.get("tag") == "event":
        excess = max(0, n_items - 9)
        major = bool(MAJOR_HOLIDAY_RE.search(day.get("banner") or ""))
        eb = event_bonus["major"] if major else event_bonus["minor"]
        value = min(eb["cap"], eb["floor"] + eb["per_item"] * excess) if major else min(eb["cap"], eb["per_item"] * excess)
        return value, major
    if day.get("tag") == "machine":
        return event_bonus["machine"]["value"], False
    return 0.0, False


def compute_current_month_revenue_nowcast(days, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus, event_bonus, dom_curve, pricing_adjustments=None):
    """Online correction for the current month.

    The broad model is cross-validated over a rolling window, but a live month can still start
    in a new local regime: holiday weaker/stronger than historical holidays, lower payer base,
    different event execution, etc. Use only actual days already observed in the current month
    to (a) damp a current-month major-event curve when it overstates the actual event, and
    (b) add a conservative residual bias correction for future days.
    """
    actual_days = [d for d in days if d.get("month") == today_month_key and d.get("actualRev") is not None]
    actual_days.sort(key=lambda d: d["iso"])
    if not actual_days:
        return {"adjustment_k": 0.0, "n": 0, "observed_bias_k": 0.0, "major_event_factor": 1.0, "major_event_n": 0}

    factor_samples = []
    for d in actual_days:
        pred = simulate_predict(d, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus, event_bonus, dom_curve)
        pred += pricing_component(d, pricing_adjustments)
        ev, is_major = event_component(d, event_bonus)
        if is_major and ev > 0:
            needed = d["actualRev"] / 1000 - (pred - ev)
            factor_samples.append((d["iso"], max(0.35, min(1.05, needed / ev))))

    # Current-month holiday execution is a local regime signal, but it must not overreact to a
    # single weak event day. If the latest observed day in the same holiday cluster validates
    # the historical curve, stop damping the remaining event days.
    if factor_samples:
        latest_factor = factor_samples[-1][1]
        if latest_factor >= 0.95:
            major_event_factor = 1.0
        elif len(factor_samples) == 1:
            major_event_factor = max(0.8, min(1.0, latest_factor))
        else:
            major_event_factor = max(0.65, min(1.0, mean([v for _iso, v in factor_samples])))
    else:
        major_event_factor = 1.0

    non_event_errors = []
    fallback_errors = []
    for d in actual_days:
        pred = simulate_predict(d, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus, event_bonus, dom_curve)
        pred += pricing_component(d, pricing_adjustments)
        ev, is_major = event_component(d, event_bonus)
        if is_major:
            pred += ev * (major_event_factor - 1.0)
        err = pred - d["actualRev"] / 1000
        fallback_errors.append(err)
        if not is_major:
            non_event_errors.append(err)

    # Generic current-month bias should come from normal days when possible. Holiday execution
    # is handled by major_event_factor; otherwise a weak/strong holiday would incorrectly drag
    # every future non-event day in the month.
    errors = non_event_errors if non_event_errors else fallback_errors
    observed_bias = mean(errors)
    # Positive bias means over-prediction; correction is negative. Shrink strongly with low n.
    adjustment = -observed_bias * (len(errors) / (len(errors) + 2))
    adjustment = max(-80.0, min(40.0, adjustment))
    return {
        "adjustment_k": round(adjustment, 1),
        "n": len(errors),
        "observed_bias_k": round(observed_bias, 1),
        "major_event_factor": round(major_event_factor, 3),
        "major_event_n": len(factor_samples),
    }


def compute_current_month_pu_nowcast(days, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus, pricing_adjustments=None):
    actual_days = [d for d in days if d.get("month") == today_month_key and d.get("actualPU") is not None]
    actual_days.sort(key=lambda d: d["iso"])
    if not actual_days:
        return {"adjustment_pct": 0.0, "n": 0, "observed_bias_pct": 0.0}
    errors = []
    for d in actual_days:
        pred = simulate_predict_pu(d, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus)
        pred *= 1 + pricing_component(d, pricing_adjustments) / 100
        if pred > 0:
            errors.append((pred - d["actualPU"]) / pred * 100)
    if not errors:
        return {"adjustment_pct": 0.0, "n": 0, "observed_bias_pct": 0.0}
    observed_bias = mean(errors)
    adjustment = -observed_bias * (len(errors) / (len(errors) + 2))
    adjustment = max(-8.0, min(5.0, adjustment))
    return {"adjustment_pct": round(adjustment, 2), "n": len(errors), "observed_bias_pct": round(observed_bias, 2)}


def compute_pricing_adjustments_revenue(days, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus, event_bonus, dom_curve):
    """Learn Medium/High/Max pricing effects for the key offer platforms.

    Pricing only exists in the Monday board, not the wide DWH Smart Calendar history, so this is
    fit on real_months.json actual days. Coefficients are heavily shrunk and capped because
    pricing is correlated with event strength and prize quality.
    """
    keys = [f"{family}:{tier}" for family in PRICE_FAMILY_PATTERNS for tier in PRICE_TIERS]
    rows, y, presence = [], [], {k: 0 for k in keys}
    for d in days:
        if d.get("actualRev") is None:
            continue
        flags = pricing_flags(d, keys)
        if not any(flags.values()):
            continue
        pred_without_pricing = simulate_predict(d, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus, event_bonus, dom_curve)
        rows.append([float(flags[k]) for k in keys])
        y.append(d["actualRev"] / 1000 - pred_without_pricing)
        for k in keys:
            if flags[k]:
                presence[k] += flags[k]
    coefs = ridge_regress(rows, y, [0.0] * len(keys), lam=PRICE_REV_LAMBDA)
    out = {}
    for i, k in enumerate(keys):
        n = presence[k]
        # Per-offer adjustment, capped to prevent one tier from dominating the family signal.
        out[k] = {"value": round(max(-20.0, min(20.0, coefs[i])), 1), "n": n, "basis": "data" if n >= MIN_N_FOR_PURE_DATA else ("blended" if n > 0 else "no-data")}
    return out


def pricing_component(day, pricing_adjustments):
    if not pricing_adjustments:
        return 0.0
    flags = pricing_flags(day, pricing_adjustments.keys())
    return sum((pricing_adjustments[k]["value"] * count) for k, count in flags.items() if count)


def compute_pricing_adjustments_pu(days, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus):
    keys = [f"{family}:{tier}" for family in PRICE_FAMILY_PATTERNS for tier in PRICE_TIERS]
    rows, y, presence = [], [], {k: 0 for k in keys}
    for d in days:
        if d.get("actualPU") is None:
            continue
        flags = pricing_flags(d, keys)
        if not any(flags.values()):
            continue
        pred_without_pricing = simulate_predict_pu(d, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus)
        if pred_without_pricing <= 0:
            continue
        rows.append([float(flags[k]) for k in keys])
        y.append((d["actualPU"] - pred_without_pricing) / pred_without_pricing * 100)
        for k in keys:
            if flags[k]:
                presence[k] += flags[k]
    coefs = ridge_regress(rows, y, [0.0] * len(keys), lam=PRICE_PU_LAMBDA)
    out = {}
    for i, k in enumerate(keys):
        n = presence[k]
        out[k] = {"value": round(max(-2.5, min(2.5, coefs[i])), 2), "n": n, "basis": "data" if n >= MIN_N_FOR_PURE_DATA else ("blended" if n > 0 else "no-data")}
    return out


def compute_pu_dom_curve(pu_days, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus, shrinkage_k=5.0):
    """Day-of-month adjustment for PU, analogous to revenue's DOM curve. Additive in absolute
    PU count. Shrunk more aggressively than revenue (k=5 vs 0) because PU has lower day count
    and more day-to-day noise."""
    buckets = {k: [] for k, _ in DOM_BUCKETS}
    keys = list(PU_PRIORS_PCT.keys())
    for d in pu_days:
        if d.get("actualPU") is None or d.get("tag"):
            continue
        pred = simulate_predict_pu(d, base_dow, crowd_by_month, trend_by_month, today_month_key, promo_bonus)
        if pred <= 0:
            continue
        resid = d["actualPU"] - pred
        buckets[dom_bucket(d["date"])].append(resid)
    out = {}
    for key, vals in buckets.items():
        n = len(vals)
        m = mean(vals) if vals else 0.0
        w = n / (n + shrinkage_k) if n else 0.0
        out[key] = {"value": round(w * m, 0), "n": n}
    return out


def cross_validate_pu(pu_days_all, base_dow, crowd_by_month, trend_by_month, today_month_key, k=5, seeds=(7, 11, 42, 99, 123)):
    """Held-out PU accuracy. Now refits DOW+crowd per fold (same leakage fix as revenue CV)
    and includes the DOM curve in scoring."""
    import random
    if len(pu_days_all) < k * 2:
        return None, 0
    keys = list(PU_PRIORS_PCT.keys())
    priors = [PU_PRIORS_PCT[key] for key in keys]
    iso_to_pos = {d["iso"]: i for i, d in enumerate(pu_days_all)}

    def row_for(d):
        flags = promo_flags(d, keys)
        return [float(flags[k]) for k in keys]

    all_errs = []
    for seed in seeds:
        rng = random.Random(seed)
        order = list(range(len(pu_days_all)))
        rng.shuffle(order)
        folds = [order[i::k] for i in range(k)]
        for fold in folds:
            test_idx = set(fold)
            train_days = [pu_days_all[i] for i in order if i not in test_idx and not pu_days_all[i].get("tag")]
            if not train_days:
                continue
            # Refit DOW+crowd inside this fold
            fold_base_dow, _ = compute_base_dow(train_days, "actualPU")
            fold_crowd, fold_trend = compute_month_crowd(train_days, fold_base_dow, "actualPU", today_month_key)
            rows = [row_for(d) for d in train_days]
            y = []
            for d in train_days:
                base = fold_base_dow[d["dow"]] + fold_crowd.get(d["month"], 0)
                y.append((d["actualPU"] - base) / base * 100 if base > 0 else 0)
            coefs = ridge_regress(rows, y, priors, lam=PU_RIDGE_LAMBDA)
            fold_promo_bonus = {key: {"value": coefs[i]} for i, key in enumerate(keys)}
            fold_dom_curve = compute_pu_dom_curve(train_days, fold_base_dow, fold_crowd, fold_trend, today_month_key, fold_promo_bonus)
            for i in order:
                if i not in test_idx:
                    continue
                d = pu_days_all[i]
                pos = iso_to_pos.get(d["iso"])
                prev_d = pu_days_all[pos - 1] if pos is not None and pos > 0 else None
                pred = simulate_predict_pu(d, fold_base_dow, fold_crowd, fold_trend, today_month_key,
                                           fold_promo_bonus, dom_curve=fold_dom_curve, prev_day=prev_d)
                if pred > 0:
                    all_errs.append(abs(d["actualPU"] - pred) / pred * 100)
    return (mean(all_errs), len(all_errs)) if all_errs else (None, 0)


def compute_product_knowledge(today_month_key):
    """Broad product-learning layer, deliberately separate from the forecast window.

    Forecast coefficients stay on CV-selected rolling windows because the revenue/PU regime drifts.
    This knowledge base uses every clean exact-DWH day from January onward to explain the product:
    which families appear often, how they behave vs DOW+month baseline, and which combinations
    repeatedly co-occur. Pair "synergy" is directional, not causal; the forecast model remains the
    joint ridge regression above.
    """
    days = [dict(d) for d in load_wide_days() if d["iso"] >= KNOWLEDGE_START_DATE and d.get("actualRev") is not None]
    clean_days = [d for d in days if not d.get("tag")]
    for d in clean_days:
        d["_revK"] = d["actualRev"] / 1000
    base_dow, _ = compute_base_dow(clean_days, "_revK")
    crowd, _ = compute_month_crowd(clean_days, base_dow, "_revK", today_month_key)
    keys = list(PROMO_PATTERNS.keys())
    family_stats = {k: {"n": 0, "rev": [], "resid": [], "pu": []} for k in keys}
    pair_stats = {}
    for d in clean_days:
        day_keys = [k for k in keys if k in d.get("_keys", set())]
        if not day_keys:
            continue
        baseline = base_dow[d["dow"]] + crowd.get(d["month"], 0)
        resid = d["_revK"] - baseline
        for k in day_keys:
            family_stats[k]["n"] += 1
            family_stats[k]["rev"].append(d["_revK"])
            family_stats[k]["resid"].append(resid)
            family_stats[k]["pu"].append(d.get("actualPU") or 0)
        for i, a in enumerate(day_keys):
            for b in day_keys[i + 1:]:
                pair = tuple(sorted((a, b)))
                pair_stats.setdefault(pair, {"n": 0, "rev": [], "resid": [], "pu": []})
                pair_stats[pair]["n"] += 1
                pair_stats[pair]["rev"].append(d["_revK"])
                pair_stats[pair]["resid"].append(resid)
                pair_stats[pair]["pu"].append(d.get("actualPU") or 0)

    family_rows = []
    family_mean_resid = {}
    for k, s in family_stats.items():
        if s["n"] <= 0:
            continue
        avg_resid = mean(s["resid"])
        family_mean_resid[k] = avg_resid
        family_rows.append({
            "key": k,
            "n": s["n"],
            "avg_rev_k": round(mean(s["rev"]), 1),
            "avg_residual_k": round(avg_resid, 1),
            "avg_pu": round(mean(s["pu"]), 0),
        })
    family_rows.sort(key=lambda r: (-r["avg_residual_k"], -r["n"]))

    pair_rows = []
    for (a, b), s in pair_stats.items():
        if s["n"] < 4:
            continue
        avg_resid = mean(s["resid"])
        expected = (family_mean_resid.get(a, 0) + family_mean_resid.get(b, 0)) / 2
        pair_rows.append({
            "keys": [a, b],
            "n": s["n"],
            "avg_rev_k": round(mean(s["rev"]), 1),
            "avg_residual_k": round(avg_resid, 1),
            "synergy_k": round(avg_resid - expected, 1),
            "avg_pu": round(mean(s["pu"]), 0),
        })
    pair_rows.sort(key=lambda r: (-r["avg_residual_k"], -r["synergy_k"], -r["n"]))

    return {
        "source": "Exact DWH days from Jan 1 onward; clean days exclude documented holiday confounds. Used for product understanding and combo planning, not as the forecast coefficient window.",
        "start_date": KNOWLEDGE_START_DATE,
        "date_range": [clean_days[0]["iso"], clean_days[-1]["iso"]] if clean_days else None,
        "n_clean_days": len(clean_days),
        "families": family_rows,
        "top_pairs": pair_rows[:12],
        "weak_pairs": sorted(pair_rows, key=lambda r: (r["avg_residual_k"], r["synergy_k"]))[:8],
    }


def main():
    import sys
    regrid = REGRID_ON_STARTUP or "--regrid" in sys.argv
    days = load_days()  # real_months.json only — still drives the calendar UI + economy/gameplay
    rev_reg_days = build_regression_dataset(REVENUE_REGRESSION_WINDOW_DAYS)
    pu_reg_days = build_regression_dataset(PU_REGRESSION_WINDOW_DAYS)
    today = dt.date.today()
    today_month_key = f"{today.year}-{today.month:02d}"

    rev_days = [d for d in rev_reg_days if d.get("actualRev") is not None]
    pu_days = [d for d in pu_reg_days if d.get("actualPU") is not None]
    # event_bonus needs a true raw item count (see n_items_for's note) — only real_months.json
    # days have that, so it stays fit on the narrower, original dataset.
    rev_days_for_events = [d for d in days if d.get("actualRev") is not None]

    base_dow_rev, n_dow_rev = compute_base_dow(rev_days, "actualRev")
    base_dow_rev = {k: round(v / 1000, 1) for k, v in base_dow_rev.items()}  # -> $K
    # recompute directly in $K to keep compute_month_crowd's units consistent
    for d in rev_days:
        d["_revK"] = d["actualRev"] / 1000
    for d in rev_days_for_events:
        d["_revK"] = d["actualRev"] / 1000
    base_dow_rev_k, n_dow_rev = compute_base_dow(rev_days, "_revK")
    crowd_rev, trend_rev = compute_month_crowd(rev_days, base_dow_rev_k, "_revK", today_month_key)
    if sum(1 for d in rev_days if d.get("month") == today_month_key) < MIN_DAYS_FOR_FLAT_MONTH:
        trend_rev[today_month_key] = min(0.0, trend_rev.get(today_month_key, 0.0))
    # Extrapolate crowd adjustment to the next planning month (e.g. August) so the
    # dashboard doesn't fall back to a hard-coded -10K default for future months.
    _next_month_ord = dt.date(today.year + (1 if today.month == 12 else 0),
                              (today.month % 12) + 1, 1).toordinal()
    _next_month_key = f"{today.year}-{(today.month % 12) + 1:02d}" if today.month < 12 else f"{today.year + 1}-01"
    if _next_month_key not in crowd_rev:
        # Use the same trend line already computed inside compute_month_crowd
        # Approximate: evaluate slope*ord+intercept at next-month day 1
        _slope = trend_rev.get(today_month_key, 0.0)
        _today_crowd = crowd_rev.get(today_month_key, 0.0)
        _today_ord = dt.date(today.year, today.month, 1).toordinal()
        crowd_rev[_next_month_key] = round(_today_crowd + _slope * (_next_month_ord - _today_ord), 1)
        trend_rev[_next_month_key] = round(_slope, 3)
    promo_bonus_rev = compute_promo_bonus_revenue(rev_days, base_dow_rev_k, crowd_rev)
    event_bonus = compute_event_bonus(rev_days_for_events, base_dow_rev_k, crowd_rev)
    dom_curve = compute_day_of_month_curve(rev_days, base_dow_rev_k, crowd_rev, trend_rev, today_month_key, promo_bonus_rev)
    pricing_bonus_rev = compute_pricing_adjustments_revenue(days, base_dow_rev_k, crowd_rev, trend_rev, today_month_key, promo_bonus_rev, event_bonus, dom_curve)
    # Fit carryover_fraction and absorption_penalty from data (replaces hardcoded 0.4 / -18)
    carryover_fit = compute_carryover_absorption(rev_days, base_dow_rev_k, crowd_rev, trend_rev, today_month_key, promo_bonus_rev, event_bonus, dom_curve)
    fitted_carryover = carryover_fit["carryover_fraction"]
    fitted_absorption = carryover_fit["absorption_penalty"]
    revenue_nowcast = compute_current_month_revenue_nowcast(days, base_dow_rev_k, crowd_rev, trend_rev, today_month_key, promo_bonus_rev, event_bonus, dom_curve, pricing_bonus_rev)

    base_dow_pu, n_dow_pu = compute_base_dow(pu_days, "actualPU")
    crowd_pu, trend_pu = compute_month_crowd(pu_days, base_dow_pu, "actualPU", today_month_key)
    if sum(1 for d in pu_days if d.get("month") == today_month_key) < MIN_DAYS_FOR_FLAT_MONTH:
        trend_pu[today_month_key] = min(0.0, trend_pu.get(today_month_key, 0.0))
    # Same next-month extrapolation for PU crowd
    if _next_month_key not in crowd_pu:
        _slope_pu = trend_pu.get(today_month_key, 0.0)
        _today_crowd_pu = crowd_pu.get(today_month_key, 0.0)
        crowd_pu[_next_month_key] = round(_today_crowd_pu + _slope_pu * (_next_month_ord - _today_ord), 1)
        trend_pu[_next_month_key] = round(_slope_pu, 3)
    promo_bonus_pu = compute_promo_bonus_pu(pu_days, base_dow_pu, crowd_pu)
    pu_dom_curve = compute_pu_dom_curve(pu_days, base_dow_pu, crowd_pu, trend_pu, today_month_key, promo_bonus_pu)
    pricing_bonus_pu = compute_pricing_adjustments_pu(days, base_dow_pu, crowd_pu, trend_pu, today_month_key, promo_bonus_pu)
    pu_nowcast = compute_current_month_pu_nowcast(days, base_dow_pu, crowd_pu, trend_pu, today_month_key, promo_bonus_pu, pricing_bonus_pu)
    product_knowledge = compute_product_knowledge(today_month_key)

    gameplay_base, n_gameplay = compute_gameplay(days)

    coin_base_dow, coin_n_dow, coin_promo_delta, n_coin_days = compute_economy_curve(days, "coinMagnitude", "coinSource", COIN_SINK_KEYS)
    gem_base_dow, gem_n_dow, gem_promo_delta, n_gem_days = compute_economy_curve(days, "gemMagnitude", "gemSource", GEM_SINK_KEYS)
    coin_cv_full, coin_cv_dow, n_coin_cv = cross_validate_economy(days, "coinMagnitude", "coinSource", COIN_SINK_KEYS)
    gem_cv_full, gem_cv_dow, n_gem_cv = cross_validate_economy(days, "gemMagnitude", "gemSource", GEM_SINK_KEYS)

    calibration = {
        "meta": {
            "computed_at": dt.datetime.now().isoformat(timespec="seconds"),
            "today": today.isoformat(),
            "current_month": today_month_key,
            "n_revenue_days": len(rev_days),
            "n_pu_days": len(pu_days),
            "n_gameplay_days": n_gameplay,
            "revenue_window_days": REVENUE_REGRESSION_WINDOW_DAYS,
            "pu_window_days": PU_REGRESSION_WINDOW_DAYS,
            "revenue_date_range": [rev_days[0]["iso"], rev_days[-1]["iso"]] if rev_days else None,
            "pu_date_range": [pu_days[0]["iso"], pu_days[-1]["iso"]] if pu_days else None,
            "date_range": [rev_days[0]["iso"], rev_days[-1]["iso"]] if rev_days else None,
            "calendar_date_range": [days[0]["iso"], days[-1]["iso"]] if days else None,
            "min_n_for_pure_data": MIN_N_FOR_PURE_DATA,
            "regression_data_source": "wide DWH pull (dwh.sm_fact_smart_calendar_promotion_updates x agg.agg_sm_daily_users_stats, exact, Nov 2025-Jul 2026) + real_months.json supplement for dates the wide pull doesn't cover yet; metric-specific trailing windows chosen by held-out grid search",
        },
        "product_knowledge": product_knowledge,
        "revenue": {
            "base_dow": base_dow_rev_k,
            "n_dow": n_dow_rev,
            "crowd_adj_by_month": crowd_rev,
            "crowd_trend_per_day": trend_rev,
            "promo_bonus": promo_bonus_rev,
            "pricing_bonus": pricing_bonus_rev,
            "event_bonus": event_bonus,
            "day_of_month_curve": dom_curve,
            "current_month_nowcast": revenue_nowcast,
            "carryover_fraction": fitted_carryover,
            "absorption_penalty": fitted_absorption,
            "carryover_fit": carryover_fit,
        },
        "pu": {
            "base_dow": base_dow_pu,
            "n_dow": n_dow_pu,
            "crowd_adj_by_month": crowd_pu,
            "crowd_trend_per_day": trend_pu,
            "promo_bonus": promo_bonus_pu,
            "pricing_bonus": pricing_bonus_pu,
            "day_of_month_curve": pu_dom_curve,
            "current_month_nowcast": pu_nowcast,
        },
        "gameplay": {
            "base_dow": gameplay_base,
            "n_days": n_gameplay,
        },
        "economy": {
            "source": "agg.agg_sm_daily_user_currency_balance, pu_segment='Active PU', is_playtika_user=0. VELOCITY = today's median end-of-day balance vs the prior day's close. This follows the Tableau Velocity / Balance / Index / Consumption reference more closely than daily_payments>0; same-day start->end is only a secondary diagnostic. See mm_calendar/data/pu_balance_raw.json",
            "n_coin_days": n_coin_days,
            "n_gem_days": n_gem_days,
            "coin_pct_base_dow": coin_base_dow,
            "coin_pct_n_dow": coin_n_dow,
            "coin_pct_promo_delta": coin_promo_delta,
            "coin_cv_full_pp": round(coin_cv_full, 2) if coin_cv_full is not None else None,
            "coin_cv_dow_only_pp": round(coin_cv_dow, 2) if coin_cv_dow is not None else None,
            "gem_pct_base_dow": gem_base_dow,
            "gem_pct_n_dow": gem_n_dow,
            "gem_pct_promo_delta": gem_promo_delta,
            "gem_cv_full_pp": round(gem_cv_full, 2) if gem_cv_full is not None else None,
            "gem_cv_dow_only_pp": round(gem_cv_dow, 2) if gem_cv_dow is not None else None,
            "note": "Coin regressors are core coin-sink mechanics (PYP, M.E.S, Spinner Clash, Ace/Card Loot, Custom Pod, Clan Dash/points, gameplay machines, Win Master, Spin Zone, Jackpot, Mega Winner). Gem regressors are the gem-relevant planning surfaces requested by the business: Short Term, Mid Term, Album, and Shiny Show. Purchase/injection offers (Coin Sale, Buy All, MGAP, Rolling, Gems Sale, Gemback, GGS) are deliberately excluded from economy regressions. Cross-validation shows composition adds little beyond the DOW baseline, so deltas are heavily shrunk toward 0 rather than overfitting noise.",
        },
    }
    OUT.write_text(json.dumps(calibration, indent=1), encoding="utf-8")

    in_sample_err, n_err = self_validate(rev_days, base_dow_rev_k, crowd_rev, trend_rev, today_month_key, promo_bonus_rev, event_bonus, dom_curve)
    # Optionally re-grid-search windows and update global constants
    if regrid:
        print("  Running window grid search (may take ~30s)...")
        best_rev_w, best_rev_cv, best_pu_w, best_pu_cv = grid_search_windows(today_month_key, event_bonus)
        print(f"  Grid search: revenue best_window={best_rev_w}d (CV={best_rev_cv:.2f}%), PU best_window={best_pu_w}d (CV={best_pu_cv:.2f}%)")
        calibration["meta"]["grid_search_rev_window"] = best_rev_w
        calibration["meta"]["grid_search_pu_window"] = best_pu_w

    cv_err, n_cv = cross_validate_revenue(rev_days, base_dow_rev_k, crowd_rev, trend_rev, today_month_key, event_bonus)
    pu_cv_err, n_pu_cv = cross_validate_pu(pu_days, base_dow_pu, crowd_pu, trend_pu, today_month_key)
    calibration["meta"]["self_check_in_sample_pct_error"] = round(in_sample_err, 2) if in_sample_err is not None else None
    calibration["meta"]["self_check_mean_abs_pct_error"] = round(cv_err, 2) if cv_err is not None else (round(in_sample_err, 2) if in_sample_err is not None else None)
    calibration["meta"]["self_check_method"] = "5-fold cross-validated (DOW+crowd refit per fold, carryover included)" if cv_err is not None else "in-sample (too few days for CV yet)"
    calibration["meta"]["pu_self_check_mean_abs_pct_error"] = round(pu_cv_err, 2) if pu_cv_err is not None else None
    calibration["meta"]["pu_self_check_scored_days"] = n_pu_cv
    OUT.write_text(json.dumps(calibration, indent=1), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"  revenue: {len(rev_days)} real days ({REVENUE_REGRESSION_WINDOW_DAYS}d window), PU: {len(pu_days)} real days ({PU_REGRESSION_WINDOW_DAYS}d window), gameplay: {n_gameplay} real days")
    print(f"  current month for trend extrapolation: {today_month_key} (slope {trend_rev.get(today_month_key, 0)}$K/day)")
    print(f"  carryover_fraction: {fitted_carryover} (n={carryover_fit['carryover_n']}, basis={carryover_fit['basis']}), absorption_penalty: {fitted_absorption} (n={carryover_fit['absorption_n']})")
    if in_sample_err is not None:
        print(f"  IN-SAMPLE fit (optimistic): {in_sample_err:.2f}% over {n_err} days")
    if cv_err is not None:
        print(f"  CROSS-VALIDATED (honest, held-out) accuracy: {cv_err:.2f}% over {n_cv} scored days  <-- trust this one")
    if pu_cv_err is not None:
        print(f"  PU CROSS-VALIDATED accuracy: {pu_cv_err:.2f}% over {n_pu_cv} scored days")
    if cv_err is not None and cv_err > 15:
        print("  ⚠ WARNING: cross-validated error is high — inspect model_calibration.json before trusting this build")
    print(f"  economy: {n_coin_days} real PU-coin-balance days, {n_gem_days} real PU-gem-balance days (new DWH pull)")
    if coin_cv_full is not None:
        print(f"    coin % change: DOW+sink-mechanic CV={coin_cv_full:.1f}pp vs DOW-only CV={coin_cv_dow:.1f}pp (sink mechanics add ~{coin_cv_dow-coin_cv_full:+.2f}pp)")
    if gem_cv_full is not None:
        print(f"    gem % change:  DOW+sink-mechanic CV={gem_cv_full:.1f}pp vs DOW-only CV={gem_cv_dow:.1f}pp (sink mechanics add ~{gem_cv_dow-gem_cv_full:+.2f}pp)")


if __name__ == "__main__":
    main()
