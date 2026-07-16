#!/usr/bin/env python3
"""Pull REAL Smart-Calendar / Monday board content for May, June, July 2026
and merge in whatever real outcome data is actually available locally:
  - exact daily net revenue (cached DWH trend, Jun 11-Jul 1)
  - approximate daily closing revenue (Teams "daily mm evening report" diary, gaps allowed)
  - real median-wager day-over-day change (CSV, Jun 4-30) as a coin-pressure proxy
  - keyword-inferred coin/gem balance direction from the same diary notes (low confidence)

This replaces the fabricated July canvas as the source for calendar content.
Output: mm_calendar/data/real_months.json
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monday_client import gql  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BOARD = 18388590642
OUT = ROOT / "mm_calendar" / "data" / "real_months.json"
CACHE_RAW = ROOT / "mm_calendar" / "data" / "_monday_raw_cache.json"
DIARY = ROOT / "mm_calendar" / "daily_mm_reports.md"
WAGER_CSV = Path("/Users/itayg/Downloads/Daily Wager (W_O Migrated Users).csv")
PU_BALANCE_FILE = ROOT / "mm_calendar" / "data" / "pu_balance_raw.json"
WIDE_DAILY_OUTCOMES_FILE = ROOT / "mm_calendar" / "data" / "wide_revenue_pu.json"
WIDE_PROMO_KEYS_FILE = ROOT / "mm_calendar" / "data" / "wide_promo_keys.json"

TODAY = dt.date.today()  # dynamic: this pipeline is meant to be re-run daily (see scripts/daily_update.sh)

COLS = [
    "status", "color_mky9aesm", "date_mky27nx7", "timerange_mkz3t5qy",
    "color_mky0czxd", "long_text_mkxzgg1v",
]

Q_FIRST = """
query ($board: [ID!], $cols: [String!]) {
  boards(ids: $board) {
    items_page(limit: 200) { cursor items { name group { id } column_values(ids: $cols) { id text } } }
  }
}
"""
Q_NEXT = """
query ($cursor: String!, $cols: [String!]) {
  next_items_page(cursor: $cursor, limit: 200) { cursor items { name group { id } column_values(ids: $cols) { id text } } }
}
"""

STATUS_CAT = {
    "Daily deal": "dd",
    "Offers & coin sale": "offers",
    "Rolling offer": "offers",
    "Buy all": "offers",
    "RYD": "offers",
    "Counter PO": "offers",
    "Prize Mania": "offers",
    "SlotoBucks": "offers",
    "Extreme stamp": "offers",
    "DTC": "offers",
    "Black Diamond": "anchor",
    "MGAP": "mgap",
    "Gems": "gems",
    "Core": "gameplay",
    "Clan-Dash": "gameplay",
    "Album": "anchor",
    "Short Term": "anchor",
    "Mid Term": "anchor",
    "Event": "anchor",
    "ADS": "ads",
}
SEASON_STATUSES = {"Short Term", "Mid Term", "Album"}
HOLIDAY_PATTERNS = [
    r"cinco de mayo", r"mother.?s day", r"father.?s day", r"4th of july",
    r"independence day", r"new year", r"st\.? patrick", r"memorial day",
    r"lucy.?s \d+th", r"valentine",
]

PROMO_KEY_PATTERNS = {
    "customPod": r"custom pod",
    "coinSale": r"coins? sale",
    "decoyBonanza": r"decoy|bonanza",
    "mgapBogo": r"mgap.*bogo|bogo.*mgap",
    "mgapMatched": r"mgap.*matched",
    "mgapWildSymbols": r"mgap.*wild symbol",
    "mgapBigger": r"mgap.*bigger",
    "gemback": r"gemback",
    "rollingMoreForLess": r"more.?for.?less|buy.?more",
    "rolling": r"rolling",
    "prizeMania": r"prize mania",
    "priceCut": r"price cut",
    "buyAll": r"buy all|mystery buy all",
    "goldenSpin": r"golden spin",
    "counterPo": r"counter po|limited po",
    "snl": r"\bsnl\b",
    "happyHour": r"happy hour|jumbo giveaway|jumbo|prize picker|eyes on|fortune dip",
    "extremeStamp": r"extreme stamp",
    "fortuneDip": r"fortune dip",
    "ryd": r"\bryd\b|reveal your deal",
}


def smart_key_label(key: str) -> str:
    return {
        "customPod": "Custom Pod",
        "coinSale": "Coin Sale",
        "decoyBonanza": "Decoy/Bonanza",
        "mgapBogo": "MGAP BOGO",
        "mgapMatched": "MGAP Matched",
        "mgapWildSymbols": "MGAP Wild Symbols",
        "mgapBigger": "MGAP Bigger",
        "mgapOther": "MGAP Other",
        "gemback": "Boosted Gemback",
        "rollingMoreForLess": "Rolling More-for-Less",
        "rolling": "Rolling",
        "prizeMania": "Prize Mania",
        "priceCut": "Price Cut",
        "buyAll": "Buy All",
        "goldenSpin": "Golden Spin",
        "counterPo": "Counter PO",
        "snl": "SNL",
        "happyHour": "Happy Hour/Jumbo",
        "extremeStamp": "Extreme Stamp",
        "fortuneDip": "Fortune Dip",
        "ryd": "RYD",
    }.get(key, key)


def monday_promo_keys(entries: list[tuple[str, str, str, str]]) -> set[str]:
    """Classify Monday MM-calendar item names into the same broad promo-family keys used by
    the Smart Calendar DWH cache. This is for cross-checking, not for display; display still
    shows the real Monday item text."""
    keys = set()
    names = [n.lower() for n, _s, _p, _d in entries if not is_backup(n)]
    mgap_names = [n for n in names if "mgap" in n]
    mgap_seen = False
    for name in names:
        for key, pat in PROMO_KEY_PATTERNS.items():
            if key.startswith("mgap"):
                continue
            if re.search(pat, name):
                keys.add(key)
        if "mgap" in name:
            mgap_seen = True
    mgap_text = " | ".join(mgap_names)
    if re.search(PROMO_KEY_PATTERNS["mgapBogo"], mgap_text):
        keys.add("mgapBogo")
    elif re.search(PROMO_KEY_PATTERNS["mgapMatched"], mgap_text):
        keys.add("mgapMatched")
    elif re.search(PROMO_KEY_PATTERNS["mgapWildSymbols"], mgap_text):
        keys.add("mgapWildSymbols")
    elif re.search(PROMO_KEY_PATTERNS["mgapBigger"], mgap_text):
        keys.add("mgapBigger")
    elif mgap_seen:
        keys.add("mgapOther")
    return keys


def cv(item, cid):
    for c in item["column_values"]:
        if c["id"] == cid:
            return c.get("text") or ""
    return ""


def fetch_all():
    cache_age_hours = None
    if CACHE_RAW.is_file():
        cache_age_hours = (dt.datetime.now().timestamp() - CACHE_RAW.stat().st_mtime) / 3600
    force_refresh = "--refresh" in sys.argv
    if CACHE_RAW.is_file() and not force_refresh and cache_age_hours is not None and cache_age_hours < 20:
        print(f"Using cached raw pull ({cache_age_hours:.1f}h old, <20h): {CACHE_RAW}", file=sys.stderr)
        return json.loads(CACHE_RAW.read_text())
    print(f"Fetching fresh from Monday (cache was {'forced refresh' if force_refresh else (f'{cache_age_hours:.1f}h old' if cache_age_hours is not None else 'missing')})...", file=sys.stderr)
    items = []
    data = gql(Q_FIRST, {"board": [BOARD], "cols": COLS})
    page = data["boards"][0]["items_page"]
    items.extend(page["items"])
    cursor = page["cursor"]
    n = 1
    while cursor:
        data = gql(Q_NEXT, {"cursor": cursor, "cols": COLS})
        page = data["next_items_page"]
        items.extend(page["items"])
        cursor = page["cursor"]
        n += 1
        print(f"  page {n}: +{len(page['items'])} (total {len(items)})", file=sys.stderr)
    CACHE_RAW.write_text(json.dumps(items, ensure_ascii=False))
    return items


def parse_date(s: str):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return dt.date.fromisoformat(s[:10])
    except ValueError:
        return None


def is_noise(name: str, status: str) -> bool:
    n = name.lower()
    return "cancel" in n or "cancel" in status.lower() or "operation - daily view" in n


def is_backup(name: str) -> bool:
    """Contingency promo prepped in case the primary plan underperforms — not committed,
    so it should never feed the forecast (revenue bonus, item-density, event/machine tag,
    sale flag). Still shown in the day's item list, clearly labeled, for reference."""
    return "backup" in name.lower()


OPS_PREP_RE = re.compile(r"^(reduce|increase|adjust|lower|raise|config|prep|test)\b")


def is_holiday(name: str) -> bool:
    n = name.lower()
    if OPS_PREP_RE.match(n):
        # e.g. "Reduce feature payouts (before cinco de mayo)" — an internal RTP/config
        # action taken AHEAD of a holiday, not the customer-facing holiday promo itself.
        # Matching "cinco de mayo" here would wrongly tag the prep day as the event day.
        return False
    return any(re.search(p, n) for p in HOLIDAY_PATTERNS)


def is_machine(name: str) -> bool:
    n = name.lower()
    return "machine" in n and ("launch" in n or "sneak peek" in n or "celebration" in n)


# ---- Exact revenue trend (cached DWH pull, Jun 11 - Jul 1) ----
EXACT_TREND = {
    "06-11": 571885, "06-12": 585954, "06-13": 872009, "06-14": 691833, "06-15": 557541,
    "06-16": 608878, "06-17": 619042, "06-18": 531915, "06-19": 549239, "06-20": 712278,
    "06-21": 703970, "06-22": 619576, "06-23": 587105, "06-24": 604951, "06-25": 522394,
    "06-26": 625207, "06-27": 676767, "06-28": 597833, "06-29": 641888, "06-30": 515780,
    "07-01": 762122,
}

# ---- Exact payer (PU) trend, same cached DWH pull / same 21 days as EXACT_TREND ----
EXACT_PU_TREND = {
    "06-11": 24740, "06-12": 26562, "06-13": 28128, "06-14": 28045, "06-15": 32930,
    "06-16": 24963, "06-17": 25434, "06-18": 25009, "06-19": 23549, "06-20": 26590,
    "06-21": 29325, "06-22": 33319, "06-23": 23531, "06-24": 25677, "06-25": 22033,
    "06-26": 25348, "06-27": 27194, "06-28": 31244, "06-29": 32668, "06-30": 23591,
    "07-01": 29146,
}

# Exact gameplay trend, same cached DWH pull / same 21 days as EXACT_TREND (spinners,
# spins-per-spinner, win-rate %, sessions-per-user). No live DB access to extend this window.
EXACT_GAMEPLAY = {
    "05-19": (288999, 780, 88.5, 4.3),
    "05-20": (293568, 810, 99.6, 4.3),
    "05-21": (284940, 767, 123.3, 4.1),
    "05-22": (283446, 786, 109.7, 4.1),
    "05-23": (285171, 796, 97.1, 4.1),
    "05-24": (291794, 853, 109.8, 4.0),
    "05-25": (289319, 855, 88.8, 4.3),
    "05-26": (285448, 797, 90.5, 4.2),
    "05-27": (290550, 838, 86.6, 4.3),
    "05-28": (292604, 811, 98.6, 4.2),
    "05-29": (286814, 792, 96.3, 4.0),
    "05-30": (280013, 811, 90.7, 4.0),
    "05-31": (288385, 850, 92.7, 4.1),
    "06-01": (284238, 809, 89.5, 4.2),
    "06-02": (285567, 773, 93.0, 4.2),
    "06-03": (289073, 812, 103.0, 4.3),
    "06-04": (295809, 811, 94.1, 4.2),
    "06-05": (296019, 840, 111.5, 4.1),
    "06-06": (284297, 835, 94.7, 4.0),
    "06-07": (292808, 872, 88.8, 4.1),
    "06-08": (291235, 848, 87.0, 4.2),
    "06-09": (288759, 793, 97.0, 4.2),
    "06-10": (293399, 831, 82.8, 4.2),
    "06-11": (286748, 799, 91.0, 4.2),
    "06-12": (287159, 811, 92.0, 4.1),
    "06-13": (281522, 799, 93.0, 4.2),
    "06-14": (289691, 858, 88.7, 4.1),
    "06-15": (286121, 840, 81.8, 4.2),
    "06-16": (286407, 806, 59.5, 4.2),
    "06-17": (286484, 783, 83.8, 4.1),
    "06-18": (277170, 765, 100.6, 4.1),
    "06-19": (274369, 798, 105.1, 4.1),
    "06-20": (272327, 798, 120.9, 4.2),
    "06-21": (284736, 874, 92.5, 4.2),
    "06-22": (286411, 869, 71.3, 4.3),
    "06-23": (284195, 824, 94.4, 4.3),
    "06-24": (286086, 838, 87.0, 4.3),
    "06-25": (286945, 794, 96.3, 4.1),
    "06-26": (286566, 811, 90.3, 4.1),
    "06-27": (277263, 795, 86.1, 4.1),
    "06-28": (285641, 846, 92.2, 4.2),
    "06-29": (282957, 844, 99.3, 4.3),
    "06-30": (280870, 801, 91.0, 4.2),
    "07-01": (285046, 820, 111.4, 4.2),
    "07-02": (278162, 777, 140.7, 4.1),
}

# Handful of clean day-TOTAL payer mentions found in the evening-report diary (most PU
# mentions there are for a single promo's own payers, not the day total — these three were
# manually verified to be day-level figures, not sub-promo counts).
DIARY_PU_POINTS = {
    "2026-04-06": 39000,   # "39K משלמים" (Dash Day)
    "2026-05-19": 22000,   # "22K PU (נמוך)" — explicitly a weak day
    "2026-05-24": 27300,   # "27.3K משלמים"
    "2026-06-05": 26000,   # "26K PU"
}


# DOW-specific closing/opening ratio, fit from every clean "open->close" diary row across
# the full diary (Apr-Jun, n=5-10/DOW) — used ONLY to estimate the handful of days where the
# team logged an opening read but never followed up with a close ("337->~" style rows).
OPEN_CLOSE_RATIO_BY_DOW = {"Sun": 2.41, "Mon": 2.68, "Tue": 2.55, "Wed": 2.50, "Thu": 2.35, "Fri": 2.74, "Sat": 2.36}
# Excluded from ratio-estimation even though they have an opening value: the ratio assumes a
# "normal" day shape, which breaks for a day whose opening is itself abnormal (e.g. still
# riding a mega-event's carryover). 2026-05-06 is explicitly the "absorption day after Cinco
# de Mayo" — its unusually high 430K opening is a hangover artifact, not a normal-day signal,
# so a flat DOW ratio would wildly overstate it (implied ~$1.08M, higher than Cinco itself).
OPEN_ONLY_EXCLUDE = {"2026-05-06"}


def parse_diary_revenue():
    """Return {iso_date: (close_$K, is_estimated)} from the Hebrew evening-report diary.
    Most rows have a real logged close ('X->Y'); a few only have an opening read ('X->~'),
    for which we estimate the close via a DOW-specific open/close ratio (flagged separately,
    lower confidence than a real logged close)."""
    if not DIARY.is_file():
        return {}
    text = DIARY.read_text(encoding="utf-8")
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*(\d{2})/(\d{2})\s*\|\s*([^|]+)\|", line)
        if not m:
            continue
        dd, mm, cell = int(m.group(1)), int(m.group(2)), m.group(3)
        try:
            iso = dt.date(2026, mm, dd).isoformat()
        except ValueError:
            continue
        nums = re.findall(r"→\s*~?(\d+(?:\.\d+)?)", cell)
        if nums:
            out[iso] = (round(float(nums[-1]) * 1000), False)
            continue
        # No close logged at all ("X->~", no digits after) — try to estimate from opening.
        if iso in OPEN_ONLY_EXCLUDE:
            continue
        om = re.match(r"^\s*(\d+(?:\.\d+)?)\s*K?\s*→", cell)
        if not om:
            continue
        opening = float(om.group(1))
        try:
            dow = dt.date(2026, mm, dd).strftime("%a")
        except ValueError:
            continue
        ratio = OPEN_CLOSE_RATIO_BY_DOW.get(dow)
        if not ratio:
            continue
        out[iso] = (round(opening * ratio * 1000), True)
    return out


def parse_diary_notes():
    """Return {iso_date: note_text} for keyword-based coin/gem inference."""
    if not DIARY.is_file():
        return {}
    text = DIARY.read_text(encoding="utf-8")
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*(\d{2})/(\d{2})\s*\|\s*([^|]+)\|\s*([^|]*)\|", line)
        if not m:
            continue
        dd, mm, note = int(m.group(1)), int(m.group(2)), m.group(4)
        try:
            iso = dt.date(2026, mm, dd).isoformat()
        except ValueError:
            continue
        out[iso] = note.strip()
    return out


COIN_UP_KW = ["בלנס קוינס גבוה", "בלנסים גבוה"]
COIN_DOWN_KW = ["ניקוז בלנסים", "wager חזק", "wager גבוה", "בלנס נמוך", "צריכה משמעותית ניקזה"]
GEM_UP_KW = ["בלנס ג'מס גבוה", "דלתא ג'מס +", "צריכת ג'מס שלילית", "ג'מס יוסג' נטו"]
GEM_DOWN_KW = ["בלנס ג'מס נמוך", "שריפת ג'מס", "ניקוז ג'מס", "צריכת ג'מס מצוינת", "צריכת ג'מס טובה"]

# Explicit per-day gem-flow magnitudes mentioned in the diary (rare — only where a number
# is directly tied to that day's own entry, not a generic multi-day reference).
GEM_MAGNITUDE_PATTERNS = [
    (re.compile(r"דלתא\s*ג'?מס\s*([+\-–]?\d+(?:\.\d+)?)\s*M"), "net"),  # e.g. "דלתא ג'מס +32M" = net delta
    (re.compile(r"(\d+(?:\.\d+)?)\s*M\s*ג'?מס\s*(?:בשייני שואו|יוסג'? נטו)"), "burn"),  # e.g. "72M ג'מס בשייני שואו"
]


def infer_direction(note: str, up_kw: list[str], down_kw: list[str]):
    if any(k in note for k in down_kw):
        return "down"
    if any(k in note for k in up_kw):
        return "up"
    return None


def parse_gem_magnitude(note: str):
    """Return (signed_millions, label) for the rare days with an explicit gem number in the diary."""
    for pat, kind in GEM_MAGNITUDE_PATTERNS:
        m = pat.search(note)
        if not m:
            continue
        val = float(m.group(1))
        if kind == "net":
            return val, "net delta (diary)"
        # "burn"/usage phrasing describes gems spent that day -> balance pressure is downward
        return -abs(val), "gems burned (diary)"
    return None, None


def parse_wager_csv():
    """Return {iso_date: pct_change_vs_prev_day} for median_wager, Jun 4-30 only."""
    if not WAGER_CSV.is_file():
        return {}
    text = WAGER_CSV.read_text(encoding="utf-8", errors="replace").replace("\x00", "")
    lines = [l for l in text.splitlines() if l.strip()]
    out = {}
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        date_s = parts[0].strip()
        pct_s = parts[3].strip().replace("%", "") if len(parts) > 3 else ""
        try:
            m, d, y = date_s.split("/")
            iso = dt.date(int(y), int(m), int(d)).isoformat()
        except Exception:
            continue
        if not pct_s:
            continue
        try:
            out[iso] = float(pct_s)
        except ValueError:
            continue
    return out


def wager_pct_to_dir(pct):
    if pct is None:
        return None
    if pct >= 5:
        return "up"
    if pct <= -5:
        return "down"
    return "stable"


def load_pu_balance():
    """Real Active-PU balance-segment median coin + gem balances, start/end of day, pulled
    from agg.agg_sm_daily_user_currency_balance — the same family of data behind the
    Tableau Velocity / Balance / Index / Consumption reference. This is deliberately NOT the
    daily-payers metric used for the PU forecast: filtering to people who paid today makes
    balance movement look like purchase injection. Active PU is the stable balance segment
    used for economy health.

    The surfaced economy signal is day-over-day velocity: today's end-of-day median vs
    yesterday's end-of-day median. Same-day start->end is kept as a secondary diagnostic only,
    because it mixes consumption, injections, and segment-composition changes within the day."""
    if not PU_BALANCE_FILE.is_file():
        return {}
    data = json.loads(PU_BALANCE_FILE.read_text(encoding="utf-8")).get("days", {})
    dates = sorted(data.keys())
    out = {}
    for i, iso in enumerate(dates):
        v = data[iso]
        same_day_coin_pct = (v["coin_e"] / v["coin_s"] - 1) * 100 if v.get("coin_s") else None
        same_day_gem_pct = (v["gem_e"] / v["gem_s"] - 1) * 100 if v.get("gem_s") else None
        coin_velocity, gem_velocity = None, None
        if i > 0:
            prev = data[dates[i - 1]]
            if prev.get("coin_e"):
                coin_velocity = (v["coin_e"] / prev["coin_e"] - 1) * 100
            if prev.get("gem_e"):
                gem_velocity = (v["gem_e"] / prev["gem_e"] - 1) * 100
        out[iso] = {
            "n_pu": v.get("n_pu"),
            "coin_s": v.get("coin_s"), "coin_e": v.get("coin_e"),
            "coin_same_day_pct": same_day_coin_pct, "coin_velocity_pct": coin_velocity,
            "gem_s": v.get("gem_s"), "gem_e": v.get("gem_e"),
            "gem_same_day_pct": same_day_gem_pct, "gem_velocity_pct": gem_velocity,
        }
    return out


def load_wide_daily_outcomes():
    """Exact daily revenue + daily-payer PU from DWH.

    This is the primary source for historical actuals in the Calendar. Diary and older
    hardcoded snippets are kept only as fallback for dates not present in the DWH cache.
    """
    if not WIDE_DAILY_OUTCOMES_FILE.is_file():
        return {}
    try:
        return json.loads(WIDE_DAILY_OUTCOMES_FILE.read_text(encoding="utf-8")).get("days", {})
    except Exception:
        return {}


def load_wide_promo_keys():
    """Smart Calendar live-at-snapshot promo family keys from DWH.

    Used as a cross-check against the Monday MM board pull. Monday gives the full item text
    needed for UX/content; Smart Calendar gives the operational live/scheduled truth and
    catches missing/cancelled/misclassified promos.
    """
    if not WIDE_PROMO_KEYS_FILE.is_file():
        return {}
    try:
        return json.loads(WIDE_PROMO_KEYS_FILE.read_text(encoding="utf-8")).get("days", {})
    except Exception:
        return {}


def build_smart_calendar_check(iso: str, entries: list[tuple[str, str, str, str]], smart_keys_raw: dict) -> dict:
    monday_keys = monday_promo_keys(entries)
    smart_keys = set(filter(None, (smart_keys_raw.get(iso) or "").split(",")))
    missing_in_monday = sorted(smart_keys - monday_keys)
    missing_in_smart = sorted(monday_keys - smart_keys)
    if not smart_keys:
        status = "monday_only" if monday_keys else "no_smart_data"
    elif not monday_keys:
        status = "smart_only"
    elif missing_in_monday or missing_in_smart:
        status = "mismatch"
    else:
        status = "matched"
    return {
        "status": status,
        "mondayKeys": sorted(monday_keys),
        "smartKeys": sorted(smart_keys),
        "missingInMonday": missing_in_monday,
        "missingInSmart": missing_in_smart,
        "missingInMondayLabels": [smart_key_label(k) for k in missing_in_monday],
        "missingInSmartLabels": [smart_key_label(k) for k in missing_in_smart],
    }


def main():
    print("Fetching board items...", file=sys.stderr)
    raw = fetch_all()
    print(f"Total raw items: {len(raw)}", file=sys.stderr)

    RANGE_START = dt.date(2026, 4, 1)
    RANGE_END = dt.date(2026, 7, 31)

    day_anchors = set()
    by_date: dict[dt.date, list] = {}
    for it in raw:
        name = it["name"]
        status = cv(it, "status")
        pricing = cv(it, "color_mky9aesm")
        desc = cv(it, "long_text_mkxzgg1v")
        d1 = cv(it, "date_mky27nx7")
        sd = parse_date(d1)
        if status == "Day":
            if sd:
                day_anchors.add(sd)
            continue
        if not sd or not (RANGE_START <= sd <= RANGE_END):
            continue
        if is_noise(name, status):
            continue
        by_date.setdefault(sd, []).append((name, status, pricing, desc))

    revenue_exact = {f"2026-{k[:2]}-{k[3:]}": v for k, v in EXACT_TREND.items()}
    revenue_diary = parse_diary_revenue()
    diary_notes = parse_diary_notes()
    wager_pct = parse_wager_csv()
    pu_balance = load_pu_balance()
    wide_outcomes = load_wide_daily_outcomes()
    smart_promo_keys = load_wide_promo_keys()
    pu_exact = {f"2026-{k[:2]}-{k[3:]}": v for k, v in EXACT_PU_TREND.items()}
    gameplay_exact = {f"2026-{k[:2]}-{k[3:]}": v for k, v in EXACT_GAMEPLAY.items()}

    months = {"2026-04": 30, "2026-05": 31, "2026-06": 30, "2026-07": 31}
    out = {}
    for mkey, ndays in months.items():
        y, m = int(mkey[:4]), int(mkey[5:7])
        days = []
        for dnum in range(1, ndays + 1):
            cur = dt.date(y, m, dnum)
            iso = cur.isoformat()
            entries = by_date.get(cur, [])
            # Backup items are contingency promos, not the committed plan — keep them visible
            # in the day's lists (labeled) but exclude them from every forecast-driving signal
            # (event/machine tag, sale flag, item-density) computed below.
            pred_entries = [(n, s, p, d) for (n, s, p, d) in entries if not is_backup(n)]
            smart_calendar_check = build_smart_calendar_check(iso, pred_entries, smart_promo_keys)
            seasons = [{"name": n, "status": s, "desc": d} for (n, s, p, d) in entries if s in SEASON_STATUSES]
            promos = [
                {
                    "name": n, "cat": STATUS_CAT.get(s), "status": s, "pricing": p,
                    "desc": d, "backup": is_backup(n),
                }
                for (n, s, p, d) in entries if s not in SEASON_STATUSES
            ]
            names_lower = " | ".join(n.lower() for (n, s, p, d) in pred_entries)
            tag = None
            banner = None
            holiday_candidates = sorted(
                ((n, s) for (n, s, p, d) in pred_entries if is_holiday(n)),
                key=lambda ns: (0 if ns[1] == "Event" else 1, len(ns[0])),
            )
            if holiday_candidates:
                tag, banner = "event", holiday_candidates[0][0]
            if not tag:
                machine_candidates = sorted(
                    (n for (n, s, p, d) in pred_entries if is_machine(n)), key=len
                )
                if machine_candidates:
                    tag, banner = "machine", machine_candidates[0]
            sale = bool(re.search(r"coins? sale", names_lower))

            is_past = cur < TODAY
            actual_rev = None
            rev_source = None
            if iso in wide_outcomes and wide_outcomes[iso].get("rev") is not None:
                actual_rev = wide_outcomes[iso]["rev"]
                rev_source = "exact"
            elif iso in revenue_exact:
                actual_rev = revenue_exact[iso]
                rev_source = "exact"
            elif iso in revenue_diary:
                actual_rev, is_estimated = revenue_diary[iso]
                rev_source = "estimated" if is_estimated else "diary"

            actual_pu = None
            pu_source = None
            if iso in wide_outcomes and wide_outcomes[iso].get("pu") is not None:
                actual_pu = wide_outcomes[iso]["pu"]
                pu_source = "exact"
            elif iso in pu_exact:
                actual_pu = pu_exact[iso]
                pu_source = "exact"
            elif iso in DIARY_PU_POINTS:
                actual_pu = DIARY_PU_POINTS[iso]
                pu_source = "diary"

            gameplay = None
            if iso in gameplay_exact:
                spinners, spins_per, win_rate, sessions = gameplay_exact[iso]
                gameplay = {
                    "spinners": spinners, "spinsPerSpinner": spins_per,
                    "winRate": win_rate, "sessionsPerUser": sessions,
                }

            note = diary_notes.get(iso, "")
            pu_bal = pu_balance.get(iso)
            coin_actual, coin_source, coin_magnitude, coin_mag_label = None, None, None, None
            coin_balance_start, coin_balance_end, coin_same_day_pct = None, None, None
            if pu_bal and pu_bal["coin_velocity_pct"] is not None:
                pct = pu_bal["coin_velocity_pct"]
                coin_actual = wager_pct_to_dir(pct)
                coin_source = "active_pu_balance_dwh"
                coin_magnitude = round(pct, 1)
                coin_mag_label = "Active PU median coin balance velocity (today's close vs yesterday's close)"
                coin_balance_start, coin_balance_end = pu_bal["coin_s"], pu_bal["coin_e"]
                coin_same_day_pct = round(pu_bal["coin_same_day_pct"], 1) if pu_bal.get("coin_same_day_pct") is not None else None
            elif iso in wager_pct:
                pct = wager_pct[iso]
                coin_actual = wager_pct_to_dir(pct)
                coin_source = "wager_csv"
                coin_magnitude = round(pct, 1)
                coin_mag_label = "median wager Δ vs prior day (all users, not PU)"
            elif note:
                d = infer_direction(note, COIN_UP_KW, COIN_DOWN_KW)
                if d:
                    coin_actual, coin_source = d, "diary_kw"
            gem_actual, gem_source, gem_magnitude, gem_mag_label = None, None, None, None
            gem_balance_start, gem_balance_end, gem_same_day_pct = None, None, None
            if pu_bal and pu_bal["gem_velocity_pct"] is not None:
                pct = pu_bal["gem_velocity_pct"]
                gem_actual = "up" if pct >= 5 else ("down" if pct <= -5 else "stable")
                gem_source = "active_pu_balance_dwh"
                gem_magnitude = round(pct, 1)
                gem_mag_label = "Active PU median gem balance velocity (today's close vs yesterday's close)"
                gem_balance_start, gem_balance_end = pu_bal["gem_s"], pu_bal["gem_e"]
                gem_same_day_pct = round(pu_bal["gem_same_day_pct"], 1) if pu_bal.get("gem_same_day_pct") is not None else None
            elif note:
                mag, mag_label = parse_gem_magnitude(note)
                if mag is not None:
                    gem_actual = "up" if mag > 0 else "down"
                    gem_source = "diary_number"
                    gem_magnitude = mag
                    gem_mag_label = mag_label
                else:
                    d = infer_direction(note, GEM_UP_KW, GEM_DOWN_KW)
                    if d:
                        gem_actual, gem_source = d, "diary_kw"

            days.append({
                "date": dnum, "iso": iso, "dow": cur.strftime("%a"),
                "hasAnchor": cur in day_anchors,
                "seasons": seasons, "items": promos,
                "smartCalendarCheck": smart_calendar_check,
                "sale": sale, "tag": tag, "banner": banner,
                "isPast": is_past and (actual_rev is not None or coin_actual or gem_actual),
                "actualRev": actual_rev, "revSource": rev_source,
                "actualPU": actual_pu, "puSource": pu_source,
                "coinActual": coin_actual, "coinSource": coin_source,
                "coinMagnitude": coin_magnitude, "coinMagLabel": coin_mag_label,
                "coinBalanceStart": coin_balance_start, "coinBalanceEnd": coin_balance_end,
                "coinSameDayPct": coin_same_day_pct,
                "gemActual": gem_actual, "gemSource": gem_source,
                "gemMagnitude": gem_magnitude, "gemMagLabel": gem_mag_label,
                "gemBalanceStart": gem_balance_start, "gemBalanceEnd": gem_balance_end,
                "gemSameDayPct": gem_same_day_pct,
                "puCount": pu_bal.get("n_pu") if pu_bal else None,
                "gameplay": gameplay,
            })
        out[mkey] = days

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {OUT}", file=sys.stderr)
    for mkey, days in out.items():
        withitems = sum(1 for d in days if d["items"])
        totitems = sum(len(d["items"]) for d in days)
        withrev = sum(1 for d in days if d["actualRev"])
        print(f"{mkey}: {withitems}/{len(days)} days with promos ({totitems} total) · {withrev} days w/ actual revenue", file=sys.stderr)


if __name__ == "__main__":
    main()
