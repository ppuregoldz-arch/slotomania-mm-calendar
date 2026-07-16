# MM Calendar - ביצועי Shiny Show (צריכת ג'מס)

> מקור: `Shiny Experience.csv` + `Shiny Experience (1).csv` (אפריל-יוני 2026, Royal + Funky Family; ימים חופפים מנוכים). KPI: **Shiny Show Gems Usage in MG** (צריכת ג'מס במיני-גיים). סקריפט: `scripts/shiny_gem_analysis.py`.
> **Baseline** (Play X / יום ללא פרומו): ~48.7M ג'מס/יום (n=39).

## דירוג וריאציות Shiny Show (lift מול baseline)

| וריאציה | ימים | avg gem usage | vs baseline |
|---|---|---|---|
| **Joker - Different Prizes** 🥇 | 4 | 92.3M | **+89%** |
| Wild Guaranteed | 1 | 83.6M | +71% |
| **All Cards - Joker** | 5 | 76.6M | **+57%** |
| **All Cards** | 5 | 75.1M | **+54%** |
| Find the Flower / Betty | 1 | 69.3M | +42% |
| Growing Shiny Show | 2 | 68.3M | +40% |
| JP Symbol | 2 | 67.9M | +39% |
| **Clan Pack Guaranteed** | 3 | 67.4M | **+38%** |
| **Different Prizes** | 7 | 67.1M | **+38%** |
| SnL dice | 1 | 62.7M | +29% |
| For Every 2 Dashes | 2 | 57.0M | +17% |
| **Crazy with Aces** | 5 | 47.9M | **−2%** ⚠️ |
| Finish Sticker | 1 | 44.6M | −8% ⚠️ |

## מסקנות (אותות חזקים, n≥3-4)
- **המנצחים**: Joker - Different Prizes (**+89%**), All Cards - Joker (+57%), All Cards (+54%), Clan Pack Guaranteed (+38%), Different Prizes (+38%, n=7 - יציב).
- **חלש מתחת ל-baseline**: **Crazy with Aces (−2%, n=5)** ו-Finish Sticker (−8%).
- **תובנה**: וריאציות **Joker** ו-**All Cards / Wild Guaranteed** מניעות הכי הרבה צריכת ג'מס. **Crazy with Aces מאכזב** למרות שהוא חוזר הרבה.

> ⚠️ **Clan Pack Guaranteed הוסר לחלוטין** - לא לשבץ למרות ה-lift (+38%). בחר וריאציה אחרת מהמנצחות.

## כיצד האייג'נט משתמש בזה
- בבחירת 3 ה-Shiny Shows השבועיים, **להעדיף**: Joker (Different Prizes / All Cards), All Cards, Wild Guaranteed, Clan Pack Guaranteed.
- **למעט ב-Crazy with Aces** ו-Finish Sticker (אלא אם יש סיבת אירוע/גיוון).
- ביום אחרי Gems Sale -> לשבץ Shiny Show חזק (Joker/All Cards) כ-follow-up צריכת ג'מס (ראו `learnings.md`).
- לתאם לארט מוכן (`art_inventory.md`).

## הסתייגויות
- מדגם קטן לחלק מהוריאציות (n=1). אותות חזקים: n≥3.
- צריכת ג'מס מושפעת גם מאירועים/סופ"ש/שלב אלבום (קורלציה).

---
**עודכן:** יוני 2026.
