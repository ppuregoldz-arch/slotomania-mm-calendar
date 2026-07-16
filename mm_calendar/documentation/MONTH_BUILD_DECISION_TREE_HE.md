# איך משבצים חודש MM Calendar — מדריך החלטות (פשוט)

**למי:** Itay, המחלקה, סוכן Cursor  
**מטרה:** להבין **באיזה סדר** בונים, **מה שואלים** בכל צומת, ו**מה אסור לוותר**.  
**לא מחליף:** `monthly_guidelines/YYYY-MM.md`, `constraints.md` — רק **מפת דרכים**.

**GitHub:** [קובץ זה](https://github.com/ppuregoldz-arch/slotomania-mm-calendar/blob/main/mm_calendar/documentation/MONTH_BUILD_DECISION_TREE_HE.md)

---

## מילון קצר (3 שורות)

| מונח | משמעות |
|------|--------|
| **DD** | Daily Deal — ההצעה היומית המרכזית |
| **הצעה שנייה / VFM** | עוד הצעת רכישה «שווה» ביום (RYD, Buy All, Decoy, Rolling, Prize Mania) — **Clan-Dash לא נספר** |
| **בנק קלפים** | טבלה שבועית ב-guidelines — **רק** קלפים מהטבלה מותרים באותו שבוע |

---

# חלק א — לפני שמתחילים (3 שאלות)

ענה **בסדר**. אם נעצרת — לא בונים עד שיש תשובה.

| # | שאלה | אם כן | אם לא |
|---|------|-------|-------|
| **1** | יש **הוראה חיה מאיתי** על החודש/יום? | עושים **רק** את זה (גובר על הכל) | ממשיכים ל-2 |
| **2** | יש קובץ **`monthly_guidelines/YYYY-MM.md`** (תקרות + בנק קלפים)? | ממשיכים ל-3 | **עוצרים** — מבקשים מהכלכלה |
| **3** | זה **אוגוסט 2026, ימים 1–15**? | **Monday על הלוח = האמת** — לא מריצים builder/sync שמוחקים שיבוץ בלי אישור Itay | בונים לפי חלק ב |

**כלל זהב:** לא ממציאים מספרים, קלפים או כללים. חסר = שאלה, לא ניחוש.

**Monday:** מעלים ללוח **רק** אם Itay ביקש במפורש.

---

# חלק ב — בניית **כל החודש** (10 שלבים, תמיד באותו סדר)

חשוב על זה כמו **שכבות**: קודם שלד, אחר כך כסף, אחר כך משחק, בסוף ADS ובדיקות.

```
┌─────────────────────────────────────────────────────────┐
│  שלב 1–2: שלד (guidelines + עונות + אלבום)              │
│  שלב 3:   עוגנים קבועים (שני/רביעי/שישי/…)              │
│  שלב 4–6: כסף (DD → הצעה 2 → MGAP/מגבירים)              │
│  שלב 7–8: משחק + ADS                                    │
│  שלב 9–10: בדיקות → קובץ JSON → Monday רק באישור       │
└─────────────────────────────────────────────────────────┘
```

| שלב | מה עושים (במילים פשוטות) | מה **מחליטים** כאן |
|-----|---------------------------|---------------------|
| **1** | פותחים guidelines החודש | Hammers, MGAP, GGS, Gems Sale, **שורת קלפים לכל שבוע** |
| **2** | משרטטים עונות על ציר הזמן | Short Term ~5 ימים (Blast / Battlesheep / SNL), Mid (Quest/Globez/Figz + Winovate + Mega Pods), שלב Album |
| **3** | שמים «עוגנים» שלא זזים | שני Dash · חמישי Golden Spin · רביעי Piggy · Lotto peak · **2 MGAP בשבוע** · מכירת סופ"ש **שישי+שבת** · Price Cut פעמיים בחודש · Rolling BMFL בימי MFL |
| **4** | **לכל יום** — Daily Deal | איזה קלף/פרס מרכזי; אם DD **Once** (Wild/Shiny) → **חובה** DD **Multiple** באותו יום |
| **5** | **לכל יום** — הצעה שנייה (VFM) | RYD / Buy All / Decoy / Rolling / PM — ראה **חלק ג**; **לא** אותו סוג כמו אתמול |
| **6** | מגבירים ורכישות נוספות | MGAP, Extreme Stamp, Gemback, x2 GGS, Price Cut — **לא לערום** כמה «מנועי קוינס כבדים» באותו יום |
| **7** | ניקוז | **Core** (קוינס) — לפחות משהו ביום (בשני Dash Pass מספיק); **Shiny Show** ~3 בשבוע; Clan לפי יום בשבוע |
| **8** | ADS | פרס **נמוך** (מטבעות / ג'מס / reg נמוך) — **אחרון** ברשימה |
| **9** | בדיקה | `build_*_plan.py` חייב לצאת **0** + `audit_*` — תיקון ב-**builder**, לא «לתקן JSON ידנית» |
| **10** | פרסום | Markdown + JSON; Monday / dashboard **רק** אחרי אישור |

**אוגוסט בקוד:** `scripts/build_august_2026_plan.py` → `mm_calendar/data/august_2026_plan.json`

---

# חלק ג — בניית **יום אחד** (תבנית קבועה)

## ג.1 — מה חייב להיות ביום «רגיל» (לא אירוע ענק)

| # | חובה? | מה |
|---|--------|-----|
| 1 | **כן** | Daily Deal |
| 2 | **כן** | **לפחות הצעה שנייה אחת** (או Popup / Rolling MFL שממלאים את התפקיד — ראה טבלה למטה) |
| 3 | **כן** | משהו לניקוז קoינס (Core / MES / …) — **בשני:** Dash Pass מספיק |
| 4 | **כן** | ADS עם פרס נמוך |
| 5 | לפי שבוע | MGAP אם «נשאר מכסה» לשבוע (מקס **2**) |
| 6 | לפי template | Clan-Dash (לא נחשב VFM) |

**אם היום צפוף מדי:** מוחקים **מלמטה למעלה**: ADS מיותר → Lotto/Piggy → Core שני → מגבירים → **לא** נוגעים ב-DD וב-VFM.

---

## ג.2 — «מי מחליט» על ההצעה השנייה? (עץ פשוט)

עבור על השורות **מלמעלה למטה** — **השורה הראשונה שמתאימה** מנצחת.

| סדר | תנאי על היום | מה שמים כ-VFM |
|-----|----------------|----------------|
| 1 | **יום שני** + יום **Rolling MFL** (3/16/25 באוגוסט) | **Buy More for Less** בלבד — **בלי** VFM נוסף |
| 2 | **יום שני** (לא MFL) | RYD **או** Buy All **קל** — **בלי** MGAP / Coin Sale / Prize Mania כבד |
| 3 | **Popup Store** 12/8 או 19/8 | ה-VFM **בתוך** Popup (Decoy וכו') — **בלי** Decoy נפרד באותו יום |
| 4 | **Popup Store** 26/8 LAUNCH | **Popup** = ה-VFM; שורת RYD רק **BACKUP** אם LAUNCH לא עולה — **לא** לרוץ במקביל |
| 5 | **אירוע BTS** (22/8) | אשכול אירוע — **לא** second «רגיל» מלא |
| 6 | **Counter PO** | RYD (כלל builder) |
| 7 | **שישי/שבת sale** | Rolling **או** RYD **ליד** Coin Sale |
| 8 | **יום Extreme Stamp** | Decoy **או** RYD (לא אותו סוג כמו אתמול) |
| 9 | **כל השאר** | בוחרים מ-pool (Decoy / RYD / Rolling / Buy All / PM) + רוטציה חודשית + **לא** כמו אתמול |

---

## ג.3 — איך בוחרים **קלף / פרס** (4 שאלות)

| # | שאלה | תשובה → פעולה |
|---|------|----------------|
| **א** | זה **ADS**? | רק Coins / Gems / reg נמוך — **לא** Wild, Gold, Shiny, Ace גבוה |
| **ב** | הקלף **מופיע בבנק השבוע** ב-guidelines? | **לא** → עוצרים / שואלים · **כן** → ממשיכים |
| **ג** | זה **משחק** (Core/MES) או **רכישה** (DD/RYD/Decoy/…)? | משחק → **אין Gold** · רכישה → Gold מותר, Wild **לכל היותר 1** למקור הצעה |
| **ד** | יום **יוקרה** (sale / BTS / Decoy d3 / Counter PO)? | **כן** → Wild / Shiny Limited / 5★ · **לא** → reg/ace/gold לפי בנק + **SKU של העונה החיה** |

**SKU קצר (Short Term):** Blast→Superboom · Battlesheep→Parasheep · SNL→Dice×2/3, Multiwheel, Shield  
**יום Extreme:** בחותמות — Extreme במקום RDS; **בלי Wild** באותן הצעות  
**Hammers:** רק **מוצר אחד** ביום נותן Hammers

---

## ג.4 — תמחור (Pricing) באותו יום

| כלל | פירוש |
|-----|--------|
| DD + הצעה שנייה **שניהם** עם pricing | **חייבים רמות שונות** (למשל DD High + second Medium) |
| ברירת מחדל | High לימים חזקים; לא לרצף ארוך של Max |

---

# חלק ד — MGAP ומגבירים (צ'קlist קצר)

| # | שאלה | אם כן |
|---|------|-------|
| 1 | כבר **2 MGAP** השבוע? | **לא** שמים MGAP |
| 2 | **יום שני**? | **לא** MGAP |
| 3 | **יום sale** + רוצים BOGO? | BOGO **לא** על sale (כלל אוגוסט) |
| 4 | כבר יש היום **VFM כבד** (Coin Sale, Price Cut, Extreme, BMFL, …)? | **לא** מוסיפים עוד VFM כבד |
| 5 | MGAP + Bucks? | **אסור** (חלש) |

**x2 GGS:** עד 2 בשבוע · 3 שעות · אחרי 11:00 UTC · לא יום-אחרי-יום · לא עם Gems Sale.

---

# חלק ה — דוגמאות מספריות (אוגוסט 2026)

### דוגמה 1 — יום שלישי «רגיל» (לא Popup, לא MFL)

1. DD עם פרס מהבנק  
2. הצעה שנייה (למשל Decoy **או** RYD — לא מה שהיה אתמול)  
3. MGAP אם נשאר slot בשבוע  
4. Core אחד  
5. Shiny אם מגיע תור בשבוע  
6. Clan לפי יום  
7. ADS  

### דוגמה 2 — יום שני 11/8 (SNL + MGAP Rolling)

1. DD  
2. **Rolling 4 cycles MGAP ladder** = ה-VFM — **לא** Decoy נוסף כ-second  
3. **לא** Popup (Popup ב-12/8)  
4. Dash / Clan  
5. ADS  

### דוגמה 3 — יום 12/8 (Popup soft 1/3)

1. DD  
2. **Popup Store TEST** + תוכן VFM **בתוך** Popup (Decoy לקohorte)  
3. **ללא** Decoy Bonanza **נפרד**  
4. Rolling 6 cycles (לפי מה שסוכם)  
5. שאר שכבות — Gemback וכו' לפי לוח  

### דוגמה 4 — יום 26/8 (Popup LAUNCH)

1. DD  
2. **Popup LAUNCH** = VFM עיקרי  
3. RYD בשם **BACKUP cap** — רק אם LAUNCH לא עולה; **לא** לרוץ במקביל ל-Popup  
4. MGAP / Price Cut וכו' לפי לוח — בלי לשבור caps  

---

# חלק ו — סיום: מתי «סיימנו»?

| ✓ | בדיקה |
|---|--------|
| ☐ | `python3 scripts/build_august_2026_plan.py` → exit **0** |
| ☐ | `python3 scripts/audit_august_2026_plan.py` → אין הפרות HARD (או מתועדות ומאושרות) |
| ☐ | Popup רק **12 / 19 / 26** |
| ☐ | Rolling: ≤4 RDS / ≤2 GGS per cycle (BMFL/BXGY) |
| ☐ | רשומה ב-`TEAM_WORKLOG.md` אם נגענו בקבצים |
| ☐ | Monday sync **רק** אם Itay ביקש |

---

# חלק ז — איפה קוראים עומק

| נושא | קובץ |
|------|------|
| נקודת כניסה | `mm_calendar/BUILD_CALENDAR_ROUTER.md` |
| עדיפות פרסים | `mm_calendar/PRIZE_PRIORITY_AND_MONTH_BUILD.md` |
| כללי builder | `.cursor/rules/mm_calendar_builder.mdc` |
| DD | `mm_calendar/topics/02_daily_deal/README.md` |
| Rolling | `mm_calendar/rolling_offer.md` |
| הצעה שנייה | `mm_calendar/topics/04_second_offers/README.md` |

---

## סיכום במשפט אחד

**קודם guidelines ועונות → עוגנים → לכל יום DD + VFM → מגבירים → Core/Shiny → ADS → validate → Monday רק באישור; בקונפליקט חותכים מלמטה ולא נוגעים ב-DD+VFM.**

*עודכן: יולי 2026*
