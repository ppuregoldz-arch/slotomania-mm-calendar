# 09 — Monday board (חוזה — לא שיבוץ)

## מטרת התיקייה
להבין **איך שורה נראית בבורד** (Product, Pricing, Description) — **לא** לשנות / לסנכרן ללא אישור מפורש.

## מקורות
- `board_schema.md` — board id, עמודות, תוויות Product
- `documentation/monday_refs/README.md` — דוגמאות היסטוריות לפי Product
- `upload_mm_calendar_day_monday.py` — רק `build_rows()`; sync מוחק יתומים

## Planner vs Monday
- **⭐ מקור אמת לשיבוץ (Itay · 12/7/2026):** בורד Monday החי — snapshot read-only ב-`data/monday_board_live_snapshot.json` (+ `monday_board_live_by_date.json`). ראה `data/MONDAY_BOARD_AUTHORITY.md`.
- **`august_2026_plan.json` / builder** = תכנון ווולידציה; **לא** מחליף את Monday אחרי עריכות ידניות על הבורד.
- **Monday** = תת-קבוצת מוצרים; Clan-Dash לא נספר כ-second offer
- רענון snapshot (ללא כתיבה ל-Monday): `python3 scripts/pull_monday_live_snapshot.py`

## כשממלאים Description
- **רק instance:** SKUs / פרס / hook / `ALL ABOVE` / task (BOGO) / once-per-player — **בלי** `Platform:` ו**בלי** `Duration: 2h post 12:00 UTC` (תזמון ב-Config).
- השתמש ב-`topics/` + `offer_construction.md` / `rolling_offer.md`
- compact: `python3 scripts/apply_monday_description_compact.py --from YYYY-MM-DD --to YYYY-MM-DD`
- תוויות Product **חייבות** להתאים ל-schema

## ⛔ אל תעשה (אלא אם נתבקש)
- `upload_mm_calendar_day_monday.py --all`
- מחיקת/דריסת שורות ידניות בבורד
