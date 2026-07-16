#!/usr/bin/env python3
"""נתח את קובץ ה-Daily Wager (Tableau export) ודרג ימים לפי wager/spins.
אופציונלי: הצלב מול תאריכי Core מבורד ה-MM calendar (Monday) לזיהוי הפרומו החזק ביותר.
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

CSV_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/itayg/Downloads/Daily Wager (W_O Migrated Users).csv"
)


def num(s: str) -> float | None:
    s = (s or "").strip().replace(",", "").replace("%", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def read_text() -> str:
    raw = CSV_PATH.read_bytes()
    for enc in ("utf-16", "utf-16-le", "utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def load():
    rows = []
    text = read_text().replace("\x00", "")
    reader = csv.reader(text.splitlines(), delimiter="\t")
    header = next(reader)
    if True:
        for r in reader:
            if not r or not r[0].strip():
                continue
            rows.append({
                "date": r[0].strip(),
                "spins": num(r[1]),
                "wager": num(r[2]),
                "wager_pct_diff": num(r[3]),
                "spins_p75": num(r[4]),
                "spins_p95": num(r[5]),
                "wager_p75": num(r[6]),
                "wager_p95": num(r[8]) if len(r) > 8 else None,
            })
    return header, rows


def fmt(x: float | None) -> str:
    if x is None:
        return "-"
    if x >= 1e21:
        return f"{x/1e21:.2f}e21"
    if abs(x) < 1000 and x == int(x):
        return str(int(x))
    return f"{x:,.0f}"


def main():
    header, rows = load()
    print(f"קובץ: {CSV_PATH.name}  |  שורות: {len(rows)}  |  טווח: {rows[0]['date']} → {rows[-1]['date']}\n")

    wagers = [r["wager"] for r in rows if r["wager"] is not None]
    spins = [r["spins"] for r in rows if r["spins"] is not None]
    base_w = statistics.mean(wagers)
    base_s = statistics.mean(spins)
    print(f"Baseline median_wager (avg): {fmt(base_w)}  |  median_spins (avg): {fmt(base_s)}\n")

    for r in rows:
        r["w_uplift"] = (r["wager"] / base_w - 1) if r["wager"] else None
        r["s_uplift"] = (r["spins"] / base_s - 1) if r["spins"] else None

    print("=== TOP 8 ימי WAGER (median_wager) ===")
    print(f"{'date':<11}{'wager':>12}{'uplift':>10}{'spins':>8}{'s_uplift':>10}")
    for r in sorted(rows, key=lambda x: x["wager"] or 0, reverse=True)[:8]:
        print(f"{r['date']:<11}{fmt(r['wager']):>12}{r['w_uplift']*100:>9.1f}%{fmt(r['spins']):>8}{r['s_uplift']*100:>9.1f}%")

    print("\n=== BOTTOM 5 ימי WAGER ===")
    for r in sorted(rows, key=lambda x: x["wager"] or 0)[:5]:
        print(f"{r['date']:<11}{fmt(r['wager']):>12}{r['w_uplift']*100:>9.1f}%{fmt(r['spins']):>8}{r['s_uplift']*100:>9.1f}%")

    print("\n=== כל הימים (date | wager | uplift% | spins) ===")
    for r in rows:
        print(f"{r['date']:<11} {fmt(r['wager']):>12} {r['w_uplift']*100:>7.1f}%  spins={fmt(r['spins'])}")

    join_core(rows)


MECHANICS = [
    "Spin Zone", "Win Master", "PYP", "Pick your Path", "Pick Your Path",
    "Ace Loot", "Card Loot", "MES", "M.E.S", "Spinner Clash", "Custom Pod",
    "Jackpots", "Mega Winner", "Gems machine", "Dash", "Win Challenge", "Smash It", "Wild Supreme",
]


def mechanic_of(name: str) -> str:
    n = name.lower()
    if "spin zone" in n or "spinzone" in n:
        return "Spin Zone"
    if "win master" in n:
        return "Win Master"
    if "pyp" in n or "pick your path" in n:
        return "PYP"
    if "ace loot" in n or "card loot" in n or ("loot" in n):
        return "Ace/Card Loot"
    if "spinner clash" in n:
        return "Spinner Clash"
    if "custom pod" in n:
        return "Custom Pod"
    if "jackpot" in n:
        return "Jackpots Challenge (MES)"
    if "mega winner" in n:
        return "Mega Winner"
    if "dash" in n:
        return "Dash Challenge"
    if "gems machine" in n:
        return "Gems Machine Challenge"
    if "wild supreme" in n or "m.e.s" in n or "mes" in n:
        return "MES (themed/cards)"
    if "win challenge" in n or "smash it" in n:
        return "Other Challenge"
    return "Other"


def pearson(xs, ys):
    import statistics as st
    n = len(xs)
    if n < 3:
        return None
    mx, my = st.mean(xs), st.mean(ys)
    numr = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    return numr / (dx * dy) if dx and dy else None


def join_core(rows):
    cache = Path(__file__).resolve().parents[1] / "mm_calendar" / "data" / "core_june_2026.tsv"
    if not cache.is_file():
        print("\n(אין cache של Core - הרץ pull_core_june.py כדי להצליב)")
        return
    import statistics as st
    # מפה date(YYYY-MM-DD) -> uplift; רק ימים עם wager
    up = {}
    for r in rows:
        m, d, y = r["date"].split("/")
        up[f"{y}-{int(m):02d}-{int(d):02d}"] = r["w_uplift"] * 100

    # date -> set(mechanics) מה-cache (ללא cancelled)
    day_mech: dict[str, set] = {}
    print("\n=== הצלבת Core × wager uplift (day-level) ===")
    print(f"{'date':<12}{'mechanic':<26}{'wager uplift':>12}  name")
    for line in cache.read_text(encoding="utf-8").splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        date, name = parts[0], parts[1]
        if date not in up:
            continue
        cancelled = "cancel" in name.lower()
        mech = mechanic_of(name)
        flag = "  (Cancelled)" if cancelled else ""
        print(f"{date:<12}{mech:<26}{up[date]:>11.1f}%  {name[:44]}{flag}")
        if not cancelled:
            day_mech.setdefault(date, set()).add(mech)

    wager_days = sorted(up)
    ys = [up[d] for d in wager_days]
    all_mechs = sorted({m for ms in day_mech.values() for m in ms})

    print("\n=== קורלציה + דירוג מכניקות Core מול wager בקוינס ===")
    print(f"{'mechanic':<26}{'days':>5}{'avg uplift':>12}{'Pearson r':>11}")
    res = []
    for mech in all_mechs:
        xs = [1 if mech in day_mech.get(d, set()) else 0 for d in wager_days]
        cnt = sum(xs)
        avg = st.mean([ys[i] for i in range(len(ys)) if xs[i]])
        res.append((mech, cnt, avg, pearson(xs, ys)))
    for mech, cnt, avg, r in sorted(res, key=lambda x: x[2], reverse=True):
        rstr = f"{r:+.2f}" if r is not None else "n<3"
        print(f"{mech:<26}{cnt:>5}{avg:>11.1f}%{rstr:>11}")


if __name__ == "__main__":
    main()
