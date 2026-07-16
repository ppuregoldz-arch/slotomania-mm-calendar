# Core × Wager — ניתוח ביצועי Core לפי wager (יוני 2026)

> מקורות: Tableau export `Daily Wager (W_O Migrated Users).csv` (median/percentile wager+spins יומי, 4-30 ביוני 2026) × פריטי Core מבורד ה-MM calendar (Monday `18388590642`).
> סקריפטים: `scripts/wager_core_analysis.py` (join+דירוג), `scripts/pull_core_june.py` (משיכת Core מהבורד → `mm_calendar/data/core_june_2026.tsv`).
> **הערכים ב-e21+ תקינים** (היפר-אינפלציית קוינס). Baseline median_wager יוני ≈ 173.7e21, median_spins ≈ 621.

## 📈 קורלציה: מכניקות Core (פרומואי קוינס) × wager בקוינס — `scripts/wager_core_analysis.py`
> **המיקוד**: Core הוא ציבור פרומואי הקוינס (Spin Zone / Loot / Custom Pod / Spinner Clash / Win Master / PYP / MES / Jackpots / Dash / Mega Winner). הדשבורד = wager בקוינס. **ג'מס והצעות (Coin Sale/MGAP) אינם הנושא כאן.**

| מכניקת Core | ימים | avg wager uplift | Pearson r | אמינות |
|---|---|---|---|---|
| Ace/Card Loot | 1 | +30.8% | +0.31 | n=1 — לא אמין |
| Jackpots (MES) | 1 | +18.4% | +0.19 | n=1 |
| Mega Winner | 1 | +15.9% | +0.16 | n=1 |
| Spinner Clash | 2 | +10.1% | +0.15 | n=2 |
| ⭐ **Spin Zone** | **5** | **+4.1%** | **+0.10** | ✅ אמין יחסית |
| ⭐ **PYP** | **5** | **+3.0%** | **+0.07** | ✅ אמין יחסית |
| **Win Master** | **4** | **−6.7%** | **−0.14** | ✅ אמין יחסית |
| MES themed/cards | 3 | −8.8% | −0.16 | n=3 |
| Custom Pod | 1 | −11.8% | −0.12 | n=1 |
| ⛔ **Dash Challenge** | 2 | −21.9% | −0.32 | n=2 |

**קריאות קורלציה (רק המכניקות עם n≥4 אמינות):**
1. **Spin Zone (n=5, r=+0.10) ו-PYP (n=5, r=+0.07)** — קורלציה חיובית-מתונה עקבית ל-wager. סוסי העבודה של ניקוז הקוינז.
2. **Win Master (n=4, r=−0.14)** — קורלציה שלילית; תת-ביצע ביוני מול שאר ה-Core.
3. **Dash Challenge (n=2, r=−0.32)** — הקורלציה השלילית החזקה ביותר; מתגמל השלמת דאשים ולא ספינים → ניקוז נמוך. (n קטן — כיווני.)
4. שאר המכניקות (Loot/Jackpots/Mega Winner/Custom Pod/MES) רצו 1-3 פעמים בלבד ביוני → r לא יציב; ימי ה-wager הגבוהים שלהן (6/23, 6/29) חופפים לאירוע/סוף-אלבום.

**מגבלת n**: הקורלציות מבוססות על יוני בלבד (23 ימי-Core עם wager). כדי לייצב במיוחד את המכניקות n=1-2 צריך wager של עוד חודשים (Tableau) — את תאריכי ה-Core לחודשים נוספים אפשר למשוך מ-Monday מיידית.

## ⚠️ אזהרת סיבתיות (קריטי לקריאה נכונה)
ה-wager היומי הוא **median על כלל השחקנים (WO migrated)** — לא על משתתפי ה-Core. לכן uplift ביום נתון משקף את **כל** מה שרץ באותו יום (סייל, אירוע, סופ"ש, סוף-חודש, סוף-אלבום), לא את ה-Core לבדו. זהו אות **כיווני** בלבד, לא הוכחה סיבתית. לניתוח סיבתי נדרש participant-level (wager של משתתפי ה-Core מול לא-משתתפים באותו יום).

## דירוג מכניקות Core לפי ממוצע wager uplift (day-level, יוני)
| מכניקה | ימים | avg wager uplift | קריאה |
|---|---|---|---|
| Ace/Card Loot | 1 | **+30.8%** | n=1 (6/23, World Cup, סופ"ש+אירוע — מנופח) |
| Jackpots Challenge (MES) | 1 | +18.4% | n=1 (6/25) |
| Mega Winner | 1 | +15.9% | n=1 (6/22, חלון 17-21 UTC) |
| **Spinner Clash** | 2 | **+10.1%** | 6/28 (+29%) מול 6/11 (-9%) — שונות גבוהה |
| **Spin Zone** | 6 | **+3.2%** | ⭐ סוס-עבודה יציב, נפח הכי גבוה |
| **PYP** | 5 | **+3.0%** | ⭐ סוס-עבודה יציב |
| Win Master | 4 | -6.7% | תת-ביצוע ביוני למרות תדירות |
| MES (themed/cards) | 3 | -8.8% | ממוצע מטעה — ראו למטה |
| Custom Pod | 1 | -11.8% | n=1 (6/27) |
| **Dash Challenge** | 2 | **-21.9%** | ⛔ החלש ביותר (complete-5-dashes) |

## ימי ה-WAGER הגבוהים ביותר ומה רץ בהם
| יום | wager uplift | Core שרץ | הערה (confound) |
|---|---|---|---|
| 6/29 | **+35.3%** | M.E.S Cards - 2 Weeks Album (9 milestones→Wild Supreme) | סוף מחזור אלבום + סוף-חודש |
| 6/23 | +30.8% | Ace Loot 3/4/5★ (World Cup 48h) + Woofing Wins Slot Smashes | סופ"ש + אירוע World Cup |
| 6/28 | +29.3% | Spinner Clash | סופ"ש |
| 6/25 | +18.4% | Jackpots Challenge MES (4★ Ace) | — |
| 6/22 | +15.9% | Spin Zone Rare Pack + Mega Winner | סופ"ש |

## ימי ה-WAGER הנמוכים ביותר
| יום | wager uplift | Core שרץ |
|---|---|---|
| 6/18 | -32.9% | Wild Supreme M.E.S (יום 1 מתוך 3) |
| 6/12 | -28.8% | MES 48HR World Cup (יום 1) |
| 6/9 | -24.4% | Dash complete 5 dashes → bundle |
| 6/17 | -24.1% | Win Master 5★ Ace |
| 6/7 | -19.4% | Finish 5 super dashes → 3★ reg + AS |

## מסקנות כיווניות (לשיבוש בזהירות)
1. **Spin Zone ו-PYP = סוסי העבודה** — הכי הרבה ריצות (6 ו-5), uplift חיובי-מתון ועקבי. בחירה בטוחה ל-coin-sink יומי.
2. **Dash-completion challenges = החלשים ל-wager** (-19% עד -24%). הם מתגמלים השלמת דאשים, לא ספינים אינטנסיביים → ניקוז קוינז נמוך. עדיף לא להסתמך עליהם כ-coin sink מרכזי.
3. **ימי ה-wager הגבוהים = MES רב-מיילסטון / אירוע / סוף-אלבום** (6/29, 6/23) — אבל **מנופחים** ע"י סייל/סופ"ש/אירוע. ה-MES הגדול לסוף-אלבום כן נראה כמנוע ניקוז חזק ראוי לשחזור.
4. **spins uplift מתון בהרבה מ-wager uplift** (בד"כ ±3-4% מול ±20-35%) → Core משפיע יותר על **גודל הבט / ניקוז קוינז** מאשר על מספר הספינים.
5. **Win Master** תת-ביצע ביוני — לבדוק וריאציה/פרס לפני הסתמכות.

## הצעד הסיבתי הנכון (כשיהיה חיבור SQL/participant data)
```sql
-- wager של משתתפי Core מול לא-משתתפים באותו יום (two-step)
WITH core_participants AS (SELECT user_id, calc_date FROM <core_participation>),
daily AS (
  SELECT a.calc_date,
         CASE WHEN p.user_id IS NOT NULL THEN 'core' ELSE 'non' END AS grp,
         SUM(a.bet_coins) AS wager, SUM(a.spins) AS spins,
         COUNT(DISTINCT a.user_id) AS users
  FROM agg.agg_sm_daily_users_stats a
  LEFT JOIN core_participants p ON p.user_id=a.user_id AND p.calc_date=a.calc_date
  GROUP BY a.calc_date, grp)
SELECT calc_date, grp, wager/NULLIF(users,0) AS wager_per_user FROM daily ORDER BY calc_date, grp;
```

---
**עודכן:** יולי 2026. n קטן (חודש אחד, day-level) — לרענן עם עוד חודשים ו-participant-level לפני החלטות מחייבות.
