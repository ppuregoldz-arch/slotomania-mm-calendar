# Router — איך בונים קלנדר ולאן להסתכל (סוכנים + אנשים)

**מטרה:** תשובה מהירה לשאלה *"על מה לקרוא עכשיו?"* בלי לסרוק את כל `mm_calendar/`.  
**לא** מחליף את הגיידליינים החודשיים — רק **ניווט**.

**עודכן:** יולי 2026

---

## 0. לפני הכל (30 שניות)

| שאלה | קובץ |
|------|------|
| מה הסמכות העליונה / מה אסור להסיק? | `00_GUIDELINES_ITAY.md` |
| **עץ החלטות בניית חודש (צבעים)?** | `documentation/MONTH_BUILD_DECISION_TREE_COLORED_HE.md` |
| איזה חודש? caps ו**בנק קלפים**? | `monthly_guidelines/YYYY-MM.md` |
| כללי HARD בקצרה? | `rules_cheatsheet.md` |
| עדיפות פרסים + pipeline חודש? | `PRIZE_PRIORITY_AND_MONTH_BUILD.md` |
| תחום ספציפי (DD / Rolling / …)? | `topics/<תחום>/README.md` |
| **Stash Booster** (RLAP rows)? | `stash_booster.md` |
| דוגמאות מהבורד (3 חודשים)? | `documentation/monday_refs/sm_monday_ref_<feature>.md` |

⛔ **Monday:** אל תסנכרן / תשנה שיבוץ בבורד אלא אם המשתמש ביקש במפורש (`upload_mm_calendar_day_monday.py`).

**אוגוסט 1–15/2026:** השיבוץ על Monday הוא מקור האמת (read-only). Dashboard + תחזיות: `monday_board_live_by_date.json` → `august_2026_monday_days_1-15.json`. לא לדרוס דרך builder/sync בלי אישור Itay.

---

## 1. בניית חודש — סדר עבודה

```
monthly_guidelines → עונות + שלב אלבום → עוגנים (sale/MGAP/Dash/…)
  → DD + ledger קלפים → הצעה שנייה + תמחור → Core + Shiny/Winovate + Clan → מגבירים → **ADS (מוצר נפרד, בסוף)**
  → validate (builder + audit)
```

| שלב | מה עושים | איפה |
|-----|-----------|------|
| 1 | קרא caps + טבלת קלפים | `monthly_guidelines/`, `topics/07_seasons_album_cards/` |
| 2 | שבץ always-on + עוגנים | `recurring_events.md`, `topics/08_anchors_timing/` |
| 3 | DD לכל יום | `topics/02_daily_deal/` |
| 4 | הצעה שנייה (VFM) + רוטציה | `topics/04_second_offers/`, `topics/03_rolling_offer/` |
| 5 | MGAP / Gems / מגבירים | `topics/05_mgap_gems_amplifiers/` |
| 6a | Core / MES / Clan (ניקוז **קוינס**) | `topics/06_core_coin_sink/` |
| 6b | Shiny Show / Winovate (ניקוז **ג׳מס**) | `topics/11_gem_sink_shiny_winovate/` |
| 7 | ולידציה | `constraints.md`, `scripts/validate_calendar.py`, builder rule |
| 8 | פלט אנושי | `examples/YYYY-MM_calendar.md`, `data/*_plan.json` |

**אוגוסט 2026 (קוד):** `scripts/build_august_2026_plan.py` → `data/august_2026_plan.json`.

---

## 2. בניית יום — סדר שכבות (בעת קונפליקט — לחתוך מלמטה)

1. **רכישה:** DD + הצעה שנייה אמיתית (לא Clan-Dash כ-VFM)  
2. **מגבירי רבניו:** MGAP, Extreme, Gemback, HH, Price Cut  
3. **גיימפליי / ניקוז:** Core, MES, Spin Zone, Custom Pod  
4. **שאר:** Piggy, Lotto, LBP, features  
5. **ADS** — אחרון, פרסים נמוכים  

פרטים: `day_planning_template.md`, `topics/08_anchors_timing/README.md`.

---

## 3. Router לפי סוג משימה

| המשתמש שואל / אתה עושה | קרא קודם | אחר כך |
|-------------------------|----------|--------|
| **למלא תוכן DD** | `topics/02_daily_deal/README.md` | `offer_construction.md` §DD, monday ref DD |
| **Rolling 5/6 cycles / Description** | `topics/03_rolling_offer/README.md` | `rolling_offer.md` (קנוני) |
| **BMFL / More for Less** | `topics/03_rolling_offer/README.md` §BMFL | `constraints.md`, `learnings.md` |
| **RYD / Buy All / Decoy** | `topics/04_second_offers/README.md` | `offer_construction.md`, monday refs |
| **MGAP / Coin Sale / Gems** | `topics/05_mgap_gems_amplifiers/README.md` | `learnings.md`, `promo_revenue_analysis.md` |
| **Core / MES (ניקוז קוינס)** | `topics/06_core_coin_sink/README.md` | `core_mes_references.md`, `nivi_collector_album_prizes.md` |
| **Shiny Show / Winovate (ניקוז ג׳מס)** | `topics/11_gem_sink_shiny_winovate/README.md` | `shiny_show_performance.md`, `boosted_gemback_impact.md` |
| **איזה קלף מותר השבוע** | `topics/07_seasons_album_cards/README.md` | `monthly_guidelines` טבלה |
| **Blast / SNL / עונה קצרה** | `topics/07_seasons_album_cards/README.md` | monday ref blast/battlesheep/snl |
| **שני / Sale / Lotto / Dash** | `topics/08_anchors_timing/README.md` | `recurring_events.md` |
| **מה עולה ל-Monday (עמודות)** | `topics/09_monday_board/README.md` | `board_schema.md` |
| **איך כותבים משימת Ops ליום מאושר** | `ops_task_construction.md` | `ops_board_schema.md`, `documentation/ops_task_refs/README.md` |
| **Creative Label / בריף Monetization-Art** | `creative/CREATIVE_LABEL_RULES.md` | `creative/PROMOTION_GLOSSARY.md`, `creative/overrides.yaml`, `creative/BRIEF_WRITING_STANDARDS.md`, `creative/CRM3_REFERENCE_MAP.md`, `creative/PRODUCT_PLAYBOOK.md` |
| **מה חזק/חלש ברבניו** | `topics/10_data_performance/README.md` | `smart_calendar_insights.md` |
| **תוצאת וריאנט קנונית / תאריכים** | `performance/README.md` | `performance/by_kpi/`, `performance/instances/promo_instances.jsonl` |
| **איך מודדים / איזה baseline** | `measurement/MEASUREMENT_METHODOLOGY.md` | `measurement/DATA_MODEL.md` |
| **חסר או סותר בדאטה** | `measurement/MISSING_DATA_REGISTER.md` | `measurement/UNRESOLVED_CONFLICTS.md` |
| **חיזוי / המלצה** | `prediction/PREDICTION_AND_OPTIMIZATION.md` | `prediction/BACKTEST_RESULTS.md` |
| **מקור אמת / freshness** | `measurement/SOURCE_INVENTORY.md` | `smart_calendar.md`, `dwh_reference.md` |
| **DPU / סגמנט** | `dpu_calendar.md` | `topics/01_foundation/README.md` |
| **ולידציה / למה נכשל audit** | `topics/01_foundation/README.md` | `constraints.md`, builder `.mdc` |

---

## 4. מפת תיקיות `topics/`

| תיקייה | תחום |
|--------|------|
| `topics/01_foundation/` | כללים, caps, ולידציה, סדר סמכות |
| `topics/02_daily_deal/` | DD — מבנה, once/multiple, דוגמאות |
| `topics/03_rolling_offer/` | BXGY 5/6, BMFL, Supersized |
| `topics/04_second_offers/` | RYD, Buy All, Decoy, PM, Coin Sale |
| `topics/05_mgap_gems_amplifiers/` | MGAP, Gems Sale, Gemback, Extreme, SB |
| `topics/06_core_coin_sink/` | Core, MES, Clan — ניקוז קוינס |
| `topics/07_seasons_album_cards/` | עונות, בנק קלפים, SKU עונתי |
| `topics/08_anchors_timing/` | עוגנים, Promo Time, Night Plan, צפיפות |
| `topics/09_monday_board/` | חוזה בורד (לא שיבוץ) |
| `topics/10_data_performance/` | דאטה, ליפטים, דפוסים |
| `topics/11_gem_sink_shiny_winovate/` | Shiny Show, Winovate — ניקוז ג׳מס |

רשימה מורחבת: `topics/README.md`.

---

## 5. פקודות אחרי שינוי תוכנית (לא Monday)

```bash
python3 scripts/build_august_2026_plan.py
python3 scripts/audit_august_2026_plan.py
python3 scripts/validate_season_skus.py
```

אחרי רענון ידע/ביצועים:

```bash
python3 scripts/build_promo_knowledge_base.py
python3 scripts/backtest_promo_prediction.py
python3 scripts/validate_promo_knowledge_base.py
```

רענון dashboard/DWH מלא: `./scripts/daily_update.sh`. נכון ל-10/7/2026 ה-refresh האחרון נכשל ב-Vertica; `validate_calendar.py` עדיין תלוי ב-canvas יולי ולכן **לא** מחליף את audit אוגוסט.

רישום: `TEAM_WORKLOG.md` (שורש הריפו).
