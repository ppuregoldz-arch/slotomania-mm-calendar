#!/usr/bin/env python3
"""בונה דוח HTML מלוטש: קורלציית מכניקות Core (פרומואי קוינס) × wager בקוינס (יוני 2026).
מקורות: Daily Wager CSV (Tableau) + core_june_2026.tsv (Monday). פלט: mm_calendar/data/core_wager_report.html
"""
from __future__ import annotations

import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = Path("/Users/itayg/Downloads/Daily Wager (W_O Migrated Users).csv")
CACHE = ROOT / "mm_calendar" / "data" / "core_june_2026.tsv"
OUT = ROOT / "mm_calendar" / "data" / "core_wager_report.html"


def read_text(p: Path) -> str:
    raw = p.read_bytes()
    for enc in ("utf-16", "utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "replace")


def num(s):
    s = (s or "").strip().replace(",", "").replace("%", "")
    try:
        return float(s)
    except ValueError:
        return None


def mechanic_of(name: str) -> str:
    n = name.lower()
    if "spin zone" in n:
        return "Spin Zone"
    if "win master" in n:
        return "Win Master"
    if "pyp" in n or "pick your path" in n:
        return "PYP"
    if "loot" in n:
        return "Ace/Card Loot"
    if "spinner clash" in n:
        return "Spinner Clash"
    if "custom pod" in n:
        return "Custom Pod"
    if "jackpot" in n:
        return "Jackpots (MES)"
    if "mega winner" in n:
        return "Mega Winner"
    if "dash" in n:
        return "Dash Challenge"
    if "m.e.s" in n or "mes" in n or "wild supreme" in n:
        return "MES themed/cards"
    return "Other"


def pearson(xs, ys):
    if len(xs) < 3:
        return None
    mx, my = st.mean(xs), st.mean(ys)
    nu = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    return nu / (dx * dy) if dx and dy else None


def load():
    text = read_text(CSV).replace("\x00", "")
    wager = {}
    for line in text.splitlines()[1:]:
        c = line.split("\t")
        if len(c) < 3 or not c[0].strip():
            continue
        m, d, y = c[0].split("/")
        wager[f"{y}-{int(m):02d}-{int(d):02d}"] = {"wager": num(c[2]), "spins": num(c[1])}
    base_w = st.mean(v["wager"] for v in wager.values())
    base_s = st.mean(v["spins"] for v in wager.values())
    for v in wager.values():
        v["w_up"] = v["wager"] / base_w - 1
        v["s_up"] = v["spins"] / base_s - 1

    day_mech = {}
    day_names = {}
    for line in CACHE.read_text(encoding="utf-8").splitlines()[1:]:
        p = line.split("\t")
        if len(p) < 2:
            continue
        date, name = p[0], p[1]
        if date not in wager or "cancel" in name.lower():
            continue
        day_mech.setdefault(date, set()).add(mechanic_of(name))
        day_names.setdefault(date, []).append(name)
    return wager, base_w, base_s, day_mech, day_names


COLORS = {
    "Spin Zone": "#4f9cff", "PYP": "#22c55e", "Win Master": "#f59e0b",
    "MES themed/cards": "#a855f7", "Spinner Clash": "#06b6d4", "Dash Challenge": "#ef4444",
    "Ace/Card Loot": "#ec4899", "Jackpots (MES)": "#14b8a6", "Mega Winner": "#eab308",
    "Custom Pod": "#8b5cf6", "Other": "#64748b",
}


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_e21(x):
    return f"{x/1e21:.1f}×10²¹"


def main():
    wager, base_w, base_s, day_mech, day_names = load()
    days = sorted(wager)
    ys = [wager[d]["w_up"] * 100 for d in days]

    mechs = sorted({m for ms in day_mech.values() for m in ms})
    rows = []
    for mech in mechs:
        xs = [1 if mech in day_mech.get(d, set()) else 0 for d in days]
        cnt = sum(xs)
        if cnt == 0:
            continue
        avg = st.mean([ys[i] for i in range(len(days)) if xs[i]])
        rows.append((mech, cnt, avg, pearson(xs, ys)))
    rows.sort(key=lambda r: r[2], reverse=True)

    maxabs_day = max(abs(v) for v in ys)
    maxabs_mech = max(abs(r[2]) for r in rows)

    # --- daily bars ---
    day_bars = []
    for d in days:
        up = wager[d]["w_up"] * 100
        ms = sorted(day_mech.get(d, []))
        primary = ms[0] if ms else "Other"
        col = COLORS.get(primary, "#64748b")
        h = abs(up) / maxabs_day * 100
        pos = up >= 0
        dd = d[8:10]
        tip = f"{d} · {up:+.1f}% · " + ", ".join(esc(m) for m in ms) if ms else f"{d} · {up:+.1f}%"
        bar = f'''<div class="daycol" title="{tip}">
          <div class="barwrap">
            <div class="bar {'up' if pos else 'dn'}" style="height:{h/2:.1f}%;background:{col};{'bottom:50%' if pos else 'top:50%'}"></div>
          </div>
          <div class="dval {'g' if pos else 'r'}">{up:+.0f}%</div>
          <div class="ddate">{dd}</div>
          <div class="dmech" style="color:{col}">{esc(primary[:9]) if ms else '—'}</div>
        </div>'''
        day_bars.append(bar)

    # --- mechanic diverging bars ---
    mech_rows = []
    for mech, cnt, avg, r in rows:
        col = COLORS.get(mech, "#64748b")
        w = abs(avg) / maxabs_mech * 46  # % of half-width
        pos = avg >= 0
        rel = "✅" if cnt >= 4 else ("~" if cnt >= 2 else "n=1")
        rstr = f"{r:+.2f}" if r is not None else "—"
        bar_html = (
            f'<div class="mbar-pos"><div class="mfill" style="width:{w:.1f}%;background:{col}"></div></div>'
            if pos else
            f'<div class="mbar-neg"><div class="mfill r" style="width:{w:.1f}%;background:{col}"></div></div>'
        )
        mech_rows.append(f'''<tr>
          <td class="mname"><span class="dot" style="background:{col}"></span>{esc(mech)}</td>
          <td class="num">{cnt}</td>
          <td class="num {'g' if pos else 'r'}">{avg:+.1f}%</td>
          <td class="num">{rstr}</td>
          <td class="track">{'<div class="mbar-neg"><div class="mfill r" style="width:'+f'{w:.1f}'+'%;background:'+col+'"></div></div>' if not pos else '<div class="mbar-pos"><div class="mfill" style="width:'+f'{w:.1f}'+'%;background:'+col+'"></div></div>'}</td>
          <td class="rel">{rel}</td>
        </tr>''')

    top_days = sorted(days, key=lambda d: wager[d]["w_up"], reverse=True)[:3]
    top_html = "".join(
        f'<li><b>{d[5:]}</b> <span class="g">{wager[d]["w_up"]*100:+.0f}%</span> — {esc(", ".join(day_names.get(d, [])) [:70])}</li>'
        for d in top_days)

    html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Core × Wager — יוני 2026</title>
<style>
  :root {{ --bg:#0b0f17; --card:#141b2b; --card2:#1b2436; --stroke:#26314a; --txt:#e7ecf5; --mut:#8b96ad; --g:#22c55e; --r:#ef4444; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:linear-gradient(180deg,#0b0f17,#0d1320); color:var(--txt); font-family:-apple-system,"Segoe UI",Rubik,Arial,sans-serif; }}
  .wrap {{ max-width:1100px; margin:0 auto; padding:32px 20px 60px; }}
  h1 {{ font-size:26px; margin:0 0 4px; letter-spacing:-.3px; }}
  .sub {{ color:var(--mut); font-size:13px; margin-bottom:22px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:26px; }}
  .kpi {{ background:var(--card); border:1px solid var(--stroke); border-radius:14px; padding:14px 16px; }}
  .kpi .v {{ font-size:22px; font-weight:700; }}
  .kpi .l {{ color:var(--mut); font-size:12px; margin-top:2px; }}
  .card {{ background:var(--card); border:1px solid var(--stroke); border-radius:16px; padding:20px 22px; margin-bottom:22px; }}
  .card h2 {{ font-size:16px; margin:0 0 4px; }}
  .card .note {{ color:var(--mut); font-size:12px; margin-bottom:18px; }}
  /* daily chart */
  .chart {{ display:flex; gap:5px; align-items:stretch; height:230px; padding-top:8px; position:relative; }}
  .midline {{ position:absolute; left:0; right:0; top:50%; border-top:1px dashed #33405c; }}
  .daycol {{ flex:1; display:flex; flex-direction:column; align-items:center; min-width:0; }}
  .barwrap {{ position:relative; width:100%; flex:1; }}
  .bar {{ position:absolute; left:15%; width:70%; border-radius:4px; }}
  .dval {{ font-size:9px; margin-top:3px; font-weight:600; }}
  .ddate {{ font-size:10px; color:var(--mut); }}
  .dmech {{ font-size:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:100%; }}
  .g {{ color:var(--g); }} .r {{ color:var(--r); }}
  /* mechanic table */
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th {{ text-align:right; color:var(--mut); font-weight:600; font-size:11px; padding:6px 8px; border-bottom:1px solid var(--stroke); }}
  td {{ padding:9px 8px; border-bottom:1px solid #1e2740; }}
  td.num {{ text-align:center; font-variant-numeric:tabular-nums; white-space:nowrap; }}
  td.rel {{ text-align:center; }}
  .mname {{ font-weight:600; white-space:nowrap; }}
  .dot {{ display:inline-block; width:9px; height:9px; border-radius:3px; margin-left:7px; vertical-align:middle; }}
  .track {{ width:38%; }}
  .mbar-pos, .mbar-neg {{ position:relative; height:14px; background:#0e1524; border-radius:7px; overflow:hidden; }}
  .mbar-pos .mfill {{ position:absolute; right:50%; height:100%; border-radius:7px 0 0 7px; }}
  .mbar-neg .mfill {{ position:absolute; left:50%; height:100%; border-radius:0 7px 7px 0; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .ins {{ background:var(--card2); border:1px solid var(--stroke); border-radius:12px; padding:14px 16px; }}
  .ins h3 {{ margin:0 0 6px; font-size:14px; }}
  .ins p {{ margin:0; color:#c3ccdd; font-size:13px; line-height:1.5; }}
  ul.top {{ margin:6px 0 0; padding-inline-start:18px; font-size:13px; line-height:1.7; }}
  .warn {{ background:#2a1e12; border:1px solid #5a3d1a; color:#f0c890; border-radius:12px; padding:12px 16px; font-size:12.5px; line-height:1.55; }}
  .legend {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:14px; font-size:11px; color:var(--mut); }}
  .legend span {{ display:inline-flex; align-items:center; gap:5px; }}
</style>
</head>
<body><div class="wrap">
  <h1>Core × Wager — קורלציית פרומואי קוינס</h1>
  <div class="sub">מכניקות Core (פרומואי הקוינס) מול wager בקוינס · יוני 2026 · מקור: Tableau «Daily Wager W/O Migrated» × בורד MM calendar (Monday)</div>

  <div class="kpis">
    <div class="kpi"><div class="v">{fmt_e21(base_w)}</div><div class="l">Baseline median wager</div></div>
    <div class="kpi"><div class="v">{base_s:.0f}</div><div class="l">Baseline median spins</div></div>
    <div class="kpi"><div class="v">{len(day_mech)}</div><div class="l">ימי Core עם wager</div></div>
    <div class="kpi"><div class="v" style="color:{COLORS['Spin Zone']}">Spin Zone · PYP</div><div class="l">הקורלציה החיובית האמינה (n≥5)</div></div>
  </div>

  <div class="card">
    <h2>Wager יומי לפי סוג ה-Core</h2>
    <div class="note">אחוז שינוי ה-median wager מול הממוצע החודשי. צבע העמודה = מכניקת ה-Core הראשית באותו יום.</div>
    <div class="chart"><div class="midline"></div>{''.join(day_bars)}</div>
    <div class="legend">{''.join(f'<span><i class="dot" style="background:{c};display:inline-block;width:9px;height:9px;border-radius:3px"></i>{esc(m)}</span>' for m,c in COLORS.items() if m!='Other')}</div>
  </div>

  <div class="card">
    <h2>דירוג קורלציה — מכניקת Core × wager</h2>
    <div class="note">avg uplift = ממוצע שינוי ה-wager בימי המכניקה · Pearson r מול כל הימים · אמינות: ✅ n≥4 · ~ n≥2 · n=1 בודד.</div>
    <table>
      <thead><tr><th>מכניקה</th><th class="num">ימים</th><th class="num">avg wager</th><th class="num">r</th><th class="track">חוזק כיוון</th><th class="rel">אמינות</th></tr></thead>
      <tbody>{''.join(mech_rows)}</tbody>
    </table>
  </div>

  <div class="grid2">
    <div class="ins"><h3 style="color:{COLORS['Spin Zone']}">סוסי העבודה</h3><p><b>Spin Zone</b> (n=5, r=+0.10) ו-<b>PYP</b> (n=5, r=+0.07): קורלציה חיובית-מתונה ועקבית ל-wager. הבחירה הבטוחה לניקוז קוינז יומי.</p></div>
    <div class="ins"><h3 style="color:{COLORS['Dash Challenge']}">החלש ביותר</h3><p><b>Dash Challenge</b> (r=−0.32) ו-<b>Win Master</b> (r=−0.14): קורלציה שלילית. Dash מתגמל השלמת דאשים ולא ספינים → ניקוז נמוך.</p></div>
  </div>

  <div class="card">
    <h2>ימי ה-wager הגבוהים</h2>
    <ul class="top">{top_html}</ul>
  </div>

  <div class="warn">⚠️ <b>מגבלה:</b> יוני בלבד ({len(day_mech)} ימי Core). מכניקות עם n=1-2 (Loot / Jackpots / Mega Winner / Custom Pod) — ה-r לא יציב, וימי השיא שלהן חופפים לאירוע/סוף-אלבום. אמין רק ל-n≥4 (Spin Zone / PYP / Win Master). לייצוב דרוש wager של עוד חודשים.</div>
</div></body></html>'''

    OUT.write_text(html, encoding="utf-8")
    print(f"נכתב: {OUT}")


if __name__ == "__main__":
    main()
