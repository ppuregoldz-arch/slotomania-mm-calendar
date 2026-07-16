#!/usr/bin/env python3
"""Boosted Gemback impact — בוחן שתי השפעות:
1) האם Gemback מעלה צריכת ג'מס בכלל המשחק (Gems Consumption.csv, דלתא יומית).
2) "Amplifier Halo" — האם ביום Gemback עולה ההכנסה של *כלל* האופרים (Revenue By Product), לא רק ג'מס.
"""
from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from promo_revenue_join import load_csv_daily  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GEMS_CSV = Path("/Users/itayg/Downloads/Gems Consumption.csv")
VD = ROOT / "mm_calendar" / "data" / "variant_dates.json"
WINDOW_H = 5  # Boosted Gemback = 5 שעות


def load_gems():
    raw = GEMS_CSV.read_bytes()
    txt = None
    for enc in ("utf-16", "utf-8-sig", "utf-8", "latin-1"):
        try:
            txt = raw.decode(enc); break
        except (UnicodeDecodeError, LookupError):
            continue
    out = {}
    for line in txt.replace("\x00", "").splitlines():
        c = line.split("\t")
        if not c or "/" not in c[0]:
            continue
        m, d, y = c[0].split("/")
        iso = f"{y}-{int(m):02d}-{int(d):02d}"
        for cell in c[1:]:
            cell = cell.strip().replace("M", "").replace(",", "")
            if cell:
                try:
                    out[iso] = float(cell)
                    break
                except ValueError:
                    pass
    return out


def gemback_dates():
    d = json.load(open(VD))
    return sorted(x["d"] for x in d.get("Boosted Gemback", []))


def summarize(label, on, off):
    mon = st.mean(on) if on else 0
    mof = st.mean(off) if off else 0
    print(f"{label}")
    print(f"  ימי Gemback (n={len(on)}): ממוצע {mon:+.2f}")
    print(f"  ימים אחרים (n={len(off)}): ממוצע {mof:+.2f}")
    print(f"  הפרש: {mon - mof:+.2f}  ({'✅ Gemback גבוה יותר' if mon > mof else '❌'})")
    return mon, mof


def main():
    gems = load_gems()
    gb_all = gemback_dates()
    gb = [d for d in gb_all if d in gems]
    print(f"תאריכי Boosted Gemback עם דאטת צריכה: {gb}\n")

    print("=== 1) צריכת ג'מס בכלל המשחק (דלתא יומית, M) ===")
    on = [gems[d] for d in gems if d in gb]
    off = [gems[d] for d in gems if d not in gb]
    mon, mof = summarize("כל הימים:", on, off)
    # ניכוי חריג קיצוני (6/19 = +115M, לא Gemback)
    off2 = [v for k, v in gems.items() if k not in gb and abs(v) < 80]
    print(f"  (ללא חריג >80M): ימים אחרים ממוצע {st.mean(off2):+.2f}  →  הפרש {mon - st.mean(off2):+.2f}")
    # window gross-up: הדלתא היומית מדוללת על פני יום; החלון 5 שעות
    grossed = (mon - st.mean(off2)) * 24 / WINDOW_H
    print(f"  💡 Window gross-up (חלון {WINDOW_H}h): העודף בחלון עצמו ≈ {grossed:+.1f}M ג'מס (פי {24/WINDOW_H:.0f} מהאות היומי)")

    print("\n=== 2) Amplifier Halo — הכנסת כלל האופרים ביום Gemback ===")
    prod = load_csv_daily()
    keys = [k for k in ("MGAPP", "Sticky Bundle PP", "Rolling Offer", "Buy All", "Gems", "Reveal Your Deal", "Prize Mania") if k in prod]
    # סך הכנסה יומית על פני כל האופרים
    all_days = sorted({d for k in keys for d in prod[k]})
    tot = {d: sum(prod[k].get(d, 0) for k in keys) for d in all_days}
    on_t = [tot[d] for d in tot if d in gb]
    off_t = [tot[d] for d in tot if d not in gb]
    summarize("סך הכנסת אופרים ($):", on_t, off_t)

    print("\n  פירוק לפי מוצר — כמה מוצרים עולים ביום Gemback (halo breadth):")
    lifts = []
    for k in keys:
        base = st.mean(prod[k].values()) if prod[k] else 0
        on_k = [prod[k][d] for d in prod[k] if d in gb]
        if not on_k or not base:
            continue
        lift = st.mean(on_k) / base - 1
        lifts.append((k, lift))
        print(f"    {k:20s} lift {lift*100:+6.1f}%  (ימים={len(on_k)})")
    up = sum(1 for _, l in lifts if l > 0)
    print(f"  → {up}/{len(lifts)} מוצרים עולים ביום Gemback (halo {'רחב ✅' if up > len(lifts)/2 else 'צר'})")


if __name__ == "__main__":
    main()
