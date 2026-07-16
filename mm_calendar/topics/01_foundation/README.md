# 01 — Foundation (כללים · ולידציה)

## מה זה
שכבת ה-HARD/SOFT לפני תוכן: caps חודשיים, הדרות, רוטציה, סדר סמכות.

## סדר סמכות (קונפליקט)
1. הוראה מפורשת חיה מאיתי
2. `00_GUIDELINES_ITAY.md`
3. `monthly_guidelines/YYYY-MM.md` — תקרות ובנק קלפים נשארים HARD
4. `constraints.md` + `rules_cheatsheet.md`
5. `learnings.md` + `daily_mm_reports.md`
6. `performance/` + מקורות מצוטטים
7. `patterns_derived.md`

סתירה שלא נפתרה → `measurement/UNRESOLVED_CONFLICTS.md`; ערך חסר → `measurement/MISSING_DATA_REGISTER.md`.

## מה אפשר / לא לשבץ (תמצית)
- **VFM קוינס:** עד אחד ביום מ-{MGAP BOGO/Matched, BMFL, Coin Sale, Extreme, Price Cut}
- **שני:** לא MGAP/Coin Sale/Rolling כבד / Prize Mania גדול
- **Sale:** שישי+שבת בלבד
- **MGAP:** 2/שבוע (אוגוסט ברזל); BOGO פעם בחודש, לא ביום sale
- **Hammers:** מוצר **אחד** ביום
- **קלפים:** רק מבנק השבוע — לא להמציא

## ולידציה
- צ'קליסט: `.cursor/rules/mm_calendar_builder.mdc`
- **אוגוסט — מקור אמת:** `build_august_2026_plan.py` + `audit_august_2026_plan.py` + `validate_season_skus.py`
- `validate_calendar.py` עדיין תלוי ב-canvas יולי — כלי legacy/coverage, לא תחליף ל-audit אוגוסט

## קרא עומק
`00_GUIDELINES_ITAY.md` · `measurement/README.md` · `PRIZE_PRIORITY_AND_MONTH_BUILD.md` · `constraints.md` · `rules_cheatsheet.md`
