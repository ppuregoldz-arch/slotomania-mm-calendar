#!/usr/bin/env python3
"""חקר מעמיק: השפעת כל סוג פרס / פרומו / שילוב פרומואים על הרבניו (אפריל-יולי 2026).
מצליב את כל פריטי בורד ה-MM calendar מול Revenue By Product (1).csv (סך + לכל מוצר).
פלט: mm_calendar/deep_research_insights.md
"""
from __future__ import annotations

import json
import statistics as st
import sys
from collections import defaultdict
from datetime import date, timedelta
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monday_client import gql  # noqa: E402
import promo_revenue_join as prj  # noqa: E402

prj.CSV_PATH = "/Users/itayg/Downloads/Revenue By Product (1).csv"
BOARD = 18388590642
CACHE = "/tmp/board_items_full.json"
OUT = Path(__file__).resolve().parents[1] / "mm_calendar" / "deep_research_insights.md"
MONTHS = ("2026-04", "2026-05", "2026-06", "2026-07")

Q1 = 'query($b:[ID!],$c:[String!]){boards(ids:$b){items_page(limit:200){cursor items{name column_values(ids:$c){id text}}}}}'
QN = 'query($cur:String!,$c:[String!]){next_items_page(cursor:$cur,limit:200){cursor items{name column_values(ids:$c){id text}}}}'
COLS = ["status", "date_mky27nx7", "timerange_mkz3t5qy"]


def cv(it, cid):
    for c in it["column_values"]:
        if c["id"] == cid:
            return c.get("text") or ""
    return ""


def pull_board():
    data = gql(Q1, {"b": [BOARD], "c": COLS})
    pg = data["boards"][0]["items_page"]
    items = list(pg["items"]); cur = pg["cursor"]
    while cur:
        d = gql(QN, {"cur": cur, "c": COLS}); pg = d["next_items_page"]
        items.extend(pg["items"]); cur = pg["cursor"]
    out = []
    for it in items:
        out.append({"name": it["name"], "lane": cv(it, "status").strip(),
                    "date": cv(it, "date_mky27nx7"), "timeline": cv(it, "timerange_mkz3t5qy")})
    json.dump(out, open(CACHE, "w"), ensure_ascii=False)
    return out


PRIZE_KW = [
    ("Hammers", r"hammer"), ("Superboom", r"superboom|super boom"),
    ("Wild Supreme", r"wild supreme"), ("Wild Gold", r"wild gold"),
    ("Wild Any", r"wild any"), ("Wild Ace", r"wild ace"), ("Wild Ordinary", r"wild ordinary"),
    ("Clan Pack", r"clan pack"), ("SB Wheel", r"sb wheel"),
    ("Parasheep/AS", r"parasheep|air ?strike|\bas\b"), ("PAB", r"\bpab\b|para"),
    ("Picks", r"pick"), ("Dice Booster", r"dice booster|dice \d"),
    ("Gold Card", r"gold \d|\dgold|gold pack"), ("Ace Card", r"ace \d|\dace|ace pack"),
    ("Shiny", r"shiny"), ("% SB", r"\d+% ?sb|100%|150%|200%"),
    ("GGS", r"ggs|gold gem"), ("Quest Booster", r"quest booster"),
]
import re


def main():
    board = json.load(open(CACHE)) if Path(CACHE).is_file() else pull_board()
    prj.BOARD_CACHE = CACHE
    prod_daily = prj.load_csv_daily()
    all_days = sorted({d for k in prod_daily for d in prod_daily[k]})
    total = {d: sum(prod_daily[k].get(d, 0) for k in prod_daily) for d in all_days}
    good = {d: v for d, v in total.items() if v > 150000}
    base_mean = st.mean(good.values())

    # יום -> lanes present, ו-day -> names
    lane_days = prj.board_days_by_lane()
    day_lanes = defaultdict(set)
    day_names = defaultdict(list)
    for lane, dd in lane_days.items():
        for d, names in dd.items():
            if lane and lane != "Day":
                day_lanes[d].add(lane)
                day_names[d].extend(names)

    lines = []
    P = lines.append
    P("# חקר מעמיק — השפעת פרסים / פרומואים / שילובים על הרבניו")
    P("")
    P(f"> מקור: בורד MM calendar × `Revenue By Product (1).csv` · **אפריל-יולי 2026** · {len(good)} ימים תקינים · סך רבניו ממוצע **${base_mean:,.0f}**/יום.")
    P("> ⚠️ קורלציה לא סיבתיות · הרבניו היומי מיוחס לכל הפרומואים שרצו יחד · n קטן = כיווני.")
    P("")
    P("## ⭐ תובנות מפתח (Top Insights)")
    P("1. **Extreme Stamp = מגבֵּר-העל.** כל שילובי הרבניו הגבוהים כוללים Extreme Stamp (+17-24% מעל baseline, ~$750-780K/יום). מגביר את *כל* ההצעות בו-זמנית — לשבץ בחלונות שיא (סייל/אירוע/אלבום).")
    P("2. **הפרסים החזקים ב-DD**: SB Wheel (+15%), Wild Supreme (+10%), Quest Booster (+8%), %SB/Wild Ace/Shiny (~+6%). **החלשים**: Clan Pack (−11%), Ace Card (−12%), Superboom (−7%), Picks (−6%), GGS (−5%). ⚠️ Hammers ≈ baseline (−1%) על מדגם 92 יום — לא 'עוגן' כפי שנראה בחודשיים.")
    P("3. **קניבליזציה מאוששת**: MGAP + Coin Sale ביחד = **−4.6%** (שני פרומו-קוינס חזקים באותו יום פוגעים). מחזק את כלל ה-VFM (עד VFM אחד ליום).")
    P("4. **שילובי אופרים עובדים**: Buy All + Rolling (+16%) · Album + SlotoBucks (+15%). שילובים חלשים: Buy All + Clan-Dash (−6%), Clan-Dash + Gems (−3.5%).")
    P("5. **זמן**: שישי שיא ($714K) > שבת ($679K) > שני ($649K) > חמישי/ראשון (~$606K) > **רביעי הכי נמוך ($545K)**. חצי ראשון של החודש > חצי שני (~+4%).")
    P("6. **מסקנת שיבוץ**: לרכז Extreme Stamp + אופרים חזקים (Buy All/Rolling/Prize Mania) בימי שיא (שישי/סופ\u05f4ש/אירוע/סוף-אלבום); לפזר MGAP ו-Coin Sale לימים נפרדים; לחזק ימי רביעי החלשים.")
    P("")

    # ===== A. פרומו TYPE — סך רבניו יומי כשהמסלול פעיל =====
    P("## A. השפעת כל מסלול פרומו על סך הרבניו היומי")
    P("| מסלול | ימים פעילים | סך רבניו ממוצע/יום | מול baseline |")
    P("|---|---|---|---|")
    rows = []
    for lane in set(l for ls in day_lanes.values() for l in ls):
        days = [d for d in good if lane in day_lanes.get(d, set())]
        if len(days) < 3:
            continue
        m = st.mean(good[d] for d in days)
        rows.append((lane, len(days), m, m / base_mean - 1))
    for lane, n, m, lift in sorted(rows, key=lambda r: -r[2]):
        P(f"| {lane} | {n} | ${m:,.0f} | {lift*100:+.1f}% |")
    P("")

    # ===== B. פרס TYPE (Daily deal → Sticky Bundle PP) =====
    P("## B. השפעת סוג הפרס (Daily Deal → Sticky Bundle PP revenue)")
    dd = prod_daily.get("Sticky Bundle PP", {})
    dd_base = st.mean(dd.values()) if dd else 0
    P(f"> baseline DD ≈ ${dd_base:,.0f}/יום.")
    P("| פרס | ימים | avg DD rev | מול baseline |")
    P("|---|---|---|---|")
    prize_rev = defaultdict(list)
    for d in dd:
        names = " ".join(day_names.get(d, [])).lower()
        for label, rgx in PRIZE_KW:
            if re.search(rgx, names):
                prize_rev[label].append(dd[d])
    prows = [(lab, len(v), st.mean(v), st.mean(v) / dd_base - 1) for lab, v in prize_rev.items() if len(v) >= 3]
    for lab, n, m, lift in sorted(prows, key=lambda r: -r[2]):
        P(f"| {lab} | {n} | ${m:,.0f} | {lift*100:+.1f}% |")
    P("")

    # ===== C. שילובי פרומואים (pairs) — אינטראקציה =====
    P("## C. שילובי פרומואים — סך רבניו יומי לזוגות מסלולים (top synergies)")
    P("| שילוב | ימים | סך רבניו ממוצע | מול baseline |")
    P("|---|---|---|---|")
    pair_rev = defaultdict(list)
    for d in good:
        ls = sorted(day_lanes.get(d, set()))
        for a, b in combinations(ls, 2):
            pair_rev[(a, b)].append(good[d])
    prs = [(f"{a} + {b}", len(v), st.mean(v), st.mean(v) / base_mean - 1) for (a, b), v in pair_rev.items() if len(v) >= 4]
    for lab, n, m, lift in sorted(prs, key=lambda r: -r[2])[:15]:
        P(f"| {lab} | {n} | ${m:,.0f} | {lift*100:+.1f}% |")
    P("")
    P("**שילובים חלשים (תחתית):**")
    P("| שילוב | ימים | סך רבניו ממוצע | מול baseline |")
    P("|---|---|---|---|")
    for lab, n, m, lift in sorted(prs, key=lambda r: r[2])[:6]:
        P(f"| {lab} | {n} | ${m:,.0f} | {lift*100:+.1f}% |")
    P("")

    # ===== D. יום-בשבוע / יום-בחודש / קונטקסט =====
    import datetime as dt
    P("## D. דפוסי זמן")
    dow = defaultdict(list)
    for d, v in good.items():
        dow[dt.date.fromisoformat(d).strftime("%a")].append(v)
    P("**יום-בשבוע:** " + " · ".join(f"{w} ${st.mean(dow[w]):,.0f}" for w in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] if w in dow))
    # חצי-חודש
    first = [v for d, v in good.items() if int(d[8:10]) <= 15]
    second = [v for d, v in good.items() if int(d[8:10]) > 15]
    P(f"**חצי ראשון של החודש (1-15):** ${st.mean(first):,.0f} · **חצי שני (16-31):** ${st.mean(second):,.0f}")
    P("")

    P("---")
    P("**עודכן:** יולי 2026 · `scripts/deep_research.py` (בר-הרצה חוזרת).")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"נכתב: {OUT}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
