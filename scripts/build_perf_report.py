#!/usr/bin/env python3
"""בונה שני דוחות HTML בסגנון דוח ה-wager: רבניו (Revenue By Product) וצריכת ג'מס (Shiny Experience).
מקור נתונים: promo_revenue_analysis.md (מ-Revenue By Product.csv) + shiny_show_performance.md (מ-Shiny Experience.csv).
פלט: mm_calendar/data/revenue_report.html · gems_usage_report.html
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "mm_calendar" / "data"

LANE_COLOR = {
    "MGAP": "#ec4899", "Rolling": "#4f9cff", "Daily Deal": "#22c55e",
    "Gems": "#eab308", "Buy All": "#06b6d4", "RYD": "#a855f7",
}

# (variant, lane, solo_days, revenue_per_day$) — מ-promo_revenue_analysis.md
REVENUE = [
    ("MGAP Bigger Multipliers", "MGAP", 3, 235387),
    ("MGAP BOGO", "MGAP", 7, 190992),
    ("MGAP Matched", "MGAP", 5, 183760),
    ("MGAP Wild Symbols", "MGAP", 2, 178453),
    ("DD Clan Pack ⛔", "Daily Deal", 4, 151389),
    ("DD Superboom", "Daily Deal", 2, 132904),
    ("DD Hammers ⭐", "Daily Deal", 21, 132528),
    ("Rolling Buy More for Less ⭐", "Rolling", 4, 131689),
    ("DD Wild Supreme", "Daily Deal", 2, 129187),
    ("DD SB Wheel", "Daily Deal", 4, 127011),
    ("DD Wild Any", "Daily Deal", 7, 106075),
    ("DD Parasheep/AS", "Daily Deal", 8, 104774),
    ("Rolling bar/cycles", "Rolling", 2, 104080),
    ("Rolling Supersized", "Rolling", 2, 73745),
    ("RYD 100% SB", "RYD", 2, 71672),
    ("Buy All Coins", "Buy All", 2, 70232),
    ("Buy All Decoy Bonanza", "Buy All", 1, 56650),
    ("Buy All Wild", "Buy All", 4, 55461),
    ("RYD Wild Gold", "RYD", 1, 36368),
    ("Gems Boosted Gemback", "Gems", 2, 42848),
    ("RYD 150% SB", "RYD", 6, 31750),
    ("Gems GGS", "Gems", 5, 34111),
    ("Gems Sale", "Gems", 5, 32918),
]

# (variant, days, gem_usage_M, lift%) — מ-shiny_show_performance.md · baseline 48.7M
GEMS = [
    ("Joker - Different Prizes ⭐", 4, 92.3, 89),
    ("Wild Guaranteed", 1, 83.6, 71),
    ("All Cards - Joker", 5, 76.6, 57),
    ("All Cards", 5, 75.1, 54),
    ("Find the Flower / Betty", 1, 69.3, 42),
    ("Growing Shiny Show", 2, 68.3, 40),
    ("JP Symbol", 2, 67.9, 39),
    ("Clan Pack Guaranteed ⛔", 3, 67.4, 38),
    ("Different Prizes", 7, 67.1, 38),
    ("SnL dice", 1, 62.7, 29),
    ("For Every 2 Dashes", 2, 57.0, 17),
    ("Crazy with Aces ⚠️", 5, 47.9, -2),
    ("Finish Sticker ⚠️", 1, 44.6, -8),
]

CSS = """
  :root{--bg:#0b0f17;--card:#141b2b;--card2:#1b2436;--stroke:#26314a;--txt:#e7ecf5;--mut:#8b96ad;--g:#22c55e;--r:#ef4444;}
  *{box-sizing:border-box;}
  body{margin:0;background:linear-gradient(180deg,#0b0f17,#0d1320);color:var(--txt);font-family:-apple-system,"Segoe UI",Rubik,Arial,sans-serif;}
  .wrap{max-width:1000px;margin:0 auto;padding:30px 20px 60px;}
  h1{font-size:24px;margin:0 0 4px;}
  .sub{color:var(--mut);font-size:12.5px;margin-bottom:22px;}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px;}
  .kpi{background:var(--card);border:1px solid var(--stroke);border-radius:14px;padding:14px 16px;}
  .kpi .v{font-size:20px;font-weight:700;}
  .kpi .l{color:var(--mut);font-size:11.5px;margin-top:2px;}
  .card{background:var(--card);border:1px solid var(--stroke);border-radius:16px;padding:20px 22px;margin-bottom:22px;}
  .card h2{font-size:16px;margin:0 0 4px;}
  .card .note{color:var(--mut);font-size:12px;margin-bottom:16px;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  th{text-align:right;color:var(--mut);font-weight:600;font-size:11px;padding:6px 8px;border-bottom:1px solid var(--stroke);}
  td{padding:8px;border-bottom:1px solid #1e2740;}
  td.num{text-align:center;font-variant-numeric:tabular-nums;white-space:nowrap;}
  .nm{font-weight:600;white-space:nowrap;}
  .dot{display:inline-block;width:9px;height:9px;border-radius:3px;margin-left:7px;vertical-align:middle;}
  .track{width:42%;}
  .bar{position:relative;height:15px;background:#0e1524;border-radius:8px;overflow:hidden;}
  .bar .fill{position:absolute;right:0;top:0;height:100%;border-radius:8px;}
  .barc{position:relative;height:15px;background:#0e1524;border-radius:8px;}
  .barc .fill{position:absolute;height:100%;}
  .barc .fill.pos{right:50%;border-radius:8px 0 0 8px;}
  .barc .fill.neg{left:50%;border-radius:0 8px 8px 0;}
  .g{color:var(--g);}.r{color:var(--r);}
  .legend{display:flex;flex-wrap:wrap;gap:12px;margin-top:14px;font-size:11px;color:var(--mut);}
  .legend span{display:inline-flex;align-items:center;gap:5px;}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  .ins{background:var(--card2);border:1px solid var(--stroke);border-radius:12px;padding:14px 16px;}
  .ins h3{margin:0 0 6px;font-size:14px;}
  .ins p{margin:0;color:#c3ccdd;font-size:13px;line-height:1.5;}
  .warn{background:#2a1e12;border:1px solid #5a3d1a;color:#f0c890;border-radius:12px;padding:11px 15px;font-size:12px;line-height:1.5;margin-top:6px;}
"""


def html_head(title):
    return f'<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{title}</title><style>{CSS}</style></head><body><div class="wrap">'


def build_revenue():
    rows = sorted(REVENUE, key=lambda r: r[3], reverse=True)
    mx = max(r[3] for r in rows)
    trs = []
    for name, lane, n, val in rows:
        col = LANE_COLOR[lane]
        w = val / mx * 100
        trs.append(f'''<tr>
          <td class="nm"><span class="dot" style="background:{col}"></span>{name}</td>
          <td class="num" style="color:{col}">{lane}</td>
          <td class="num">{n}</td>
          <td class="num g">${val:,}</td>
          <td class="track"><div class="bar"><div class="fill" style="width:{w:.1f}%;background:{col}"></div></div></td>
        </tr>''')
    legend = "".join(f'<span><i class="dot" style="background:{c};display:inline-block;width:9px;height:9px;border-radius:3px"></i>{l}</span>' for l, c in LANE_COLOR.items())
    html = html_head("Revenue by Promo — מאי-יוני 2026")
    html += '''<h1>Revenue — הכנסה לפי פרומו</h1>
    <div class="sub">avg הכנסה יומית לפי וריאציית פרומו · ימי "solo" (רץ סוג אחד מהמסלול) · מקור: Revenue By Product.csv × בורד MM calendar</div>
    <div class="kpis">
      <div class="kpi"><div class="v" style="color:#ec4899">$235K</div><div class="l">MGAP Bigger Multipliers (#1)</div></div>
      <div class="kpi"><div class="v" style="color:#22c55e">$133K</div><div class="l">DD Hammers (העוגן, n=21)</div></div>
      <div class="kpi"><div class="v" style="color:#4f9cff">$132K</div><div class="l">Rolling Buy More for Less</div></div>
      <div class="kpi"><div class="v">מאי-יוני</div><div class="l">טווח (מדגם קצר)</div></div>
    </div>
    <div class="card"><h2>דירוג פרומואים לפי הכנסה/יום</h2>
    <div class="note">מיון לפי avg $/יום. צבע = מסלול. ⭐ מנצח · ⛔ Clan Pack הוסר (מוצג לרפרנס בלבד).</div>
    <table><thead><tr><th>פרומו</th><th class="num">מסלול</th><th class="num">ימים</th><th class="num">$/יום</th><th class="track">חוזק</th></tr></thead>
    <tbody>''' + "".join(trs) + f'''</tbody></table><div class="legend">{legend}</div></div>
    <div class="grid2">
      <div class="ins"><h3 style="color:#ec4899">מנועי ההכנסה</h3><p><b>MGAP Bigger Multipliers</b> (~$235K) החזק ביותר, ואחריו <b>BOGO</b> (~$191K, n=7 יציב). <b>DD Hammers</b> העוגן (~$133K על 21 ימים) ו-<b>Rolling Buy More for Less</b> (~$132K).</p></div>
      <div class="ins"><h3 style="color:#ef4444">חלשים יחסית</h3><p><b>Rolling Supersized</b> (~$74K מול $132K ל-BMFL) · <b>DD Wild Any / Parasheep</b> (~$105K מול $133K ל-Hammers). RYD 150% נמוך (~$32K).</p></div>
    </div>
    <div class="warn">⚠️ <b>מדגם קצר</b> (מאי-יוני) · סוגים עם n<3 = רעש · ייחוס DD חלקי (Sticky Bundle PP proxy) · קורלציה לא סיבתיות.</div>'''
    html += "</div></body></html>"
    (OUT_DIR / "revenue_report.html").write_text(html, encoding="utf-8")
    print("נכתב:", OUT_DIR / "revenue_report.html")


def build_gems():
    rows = sorted(GEMS, key=lambda r: r[3], reverse=True)
    mx = max(abs(r[3]) for r in rows)
    trs = []
    for name, n, usage, lift in rows:
        pos = lift >= 0
        col = "#22c55e" if lift >= 38 else ("#eab308" if lift >= 0 else "#ef4444")
        w = abs(lift) / mx * 48
        fill = f'<div class="fill {"pos" if pos else "neg"}" style="width:{w:.1f}%;background:{col}"></div>'
        trs.append(f'''<tr>
          <td class="nm">{name}</td>
          <td class="num">{n}</td>
          <td class="num">{usage:.1f}M</td>
          <td class="num {'g' if pos else 'r'}">{lift:+d}%</td>
          <td class="track"><div class="barc">{fill}</div></td>
        </tr>''')
    html = html_head("Gems Usage — Shiny Show")
    html += '''<h1>Gems Usage — צריכת ג'מס (Shiny Show)</h1>
    <div class="sub">lift ב-Shiny Show Gems Usage מול baseline (~48.7M/יום) · אפריל-יוני 2026 · מקור: Shiny Experience.csv</div>
    <div class="kpis">
      <div class="kpi"><div class="v" style="color:#22c55e">+89%</div><div class="l">Joker - Different Prizes (#1)</div></div>
      <div class="kpi"><div class="v" style="color:#22c55e">+57%</div><div class="l">All Cards - Joker</div></div>
      <div class="kpi"><div class="v">48.7M</div><div class="l">Baseline ג'מס/יום</div></div>
      <div class="kpi"><div class="v" style="color:#ef4444">−2%</div><div class="l">Crazy with Aces (מאכזב)</div></div>
    </div>
    <div class="card"><h2>דירוג וריאציות Shiny Show לפי צריכת ג'מס</h2>
    <div class="note">lift מול baseline. ⭐ מנצח · ⚠️ מתחת ל-baseline · ⛔ Clan Pack Guaranteed הוסר (לרפרנס בלבד).</div>
    <table><thead><tr><th>וריאציה</th><th class="num">ימים</th><th class="num">gem usage</th><th class="num">lift</th><th class="track">חוזק</th></tr></thead>
    <tbody>''' + "".join(trs) + '''</tbody></table></div>
    <div class="grid2">
      <div class="ins"><h3 style="color:#22c55e">מנצחים (n≥4)</h3><p><b>Joker - Different Prizes</b> (+89%), <b>All Cards - Joker</b> (+57%), <b>All Cards</b> (+54%), <b>Different Prizes</b> (+38%, n=7 יציב). וריאציות Joker/All Cards מובילות.</p></div>
      <div class="ins"><h3 style="color:#ef4444">מאכזבים</h3><p><b>Crazy with Aces</b> (−2%, n=5) ו-<b>Finish Sticker</b> (−8%) מתחת ל-baseline — למעט בהם למרות שהם חוזרים הרבה.</p></div>
    </div>
    <div class="warn">⚠️ מדגם קטן לחלק מהוריאציות (n=1) · אותות חזקים n≥3 · צריכת ג'מס מושפעת גם מאירועים/סופ"ש/שלב אלבום.</div>'''
    html += "</div></body></html>"
    (OUT_DIR / "gems_usage_report.html").write_text(html, encoding="utf-8")
    print("נכתב:", OUT_DIR / "gems_usage_report.html")


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_revenue()
    build_gems()
