# MM Calendar - 10 הפרומואים החוזרים ביותר: איך עובדים ואיך לנתח

> מבוסס על תדירות הופעה בבורד (ללא מבוטלים) + ראיון. מקור הדירוג: כריית `/tmp/board_items.json`.

| # | פרומו | הופעות | מסלול |
|---|-------|--------|-------|
| 1 | Daily Deal | 234 | Daily Deal |
| 2 | Shiny Show | 79 | Album |
| 3 | X2 Badges / Clan Go | 79 | Clan-Dash |
| 4 | Buy All / Bonanza | 70 | Buy all |
| 5 | Rolling Offer | 69 | Rolling offer |
| 6 | MGAP | 67 | MGAP |
| 7 | Spin Zone / MES | 56 | Core |
| 8 | X2 Dash Points | 54 | Clan-Dash |
| 9 | ADS PO (SPO) | 48 | ADS |
| 10 | Extreme Stamp | 43 | Extreme stamp |

---

## 1. Daily Deal
- **מה**: הצעה (offer) שעולה **פעם ביום**. חלק ממשפחת ה-Offers.
- **תוכן**: שני מטבעות הבסיס - **Coins + Gems** - ובנוסף SKU נוסף.
- **Pricing -> SKU**: לכל הצעה יש אפשרויות תמחור Medium / High / Max. עומק התמחור קובע את נדיבות ה-SKU. דוגמה: **Max = 12 Hammers, High = 8 Hammers**.
- **ניתוח**: מנצחים ברמת פרומו (ראו `promo_revenue_analysis.md`): Hammers (עוגן יציב), Clan Pack, Superboom. חלשים: Wild Any, Parasheep/AS.

## 2. Shiny Show
- **מה**: פרומו **גיימפליי** (לא הצעת רכישה ישירה).
- **KPI**: **צריכת ג'מס (gem usage)** - ככל שה-Shiny Show טוב יותר, צריכת הג'מס של השחקנים גבוהה יותר.
- **וריאציות**: סוגי Shiny Show שונים.
- **גיידליין (HARD)**: **3 Shiny Shows בשבוע.**
- מזין את ה-Shiny Collection (ראו `album_cards.md`).

## 3. X2 Badges / Clan Go (Clan-Dash)
- מכניקת קלאן סטנדרטית. אין דגשים מיוחדים.

## 4. Buy All / Bonanza
- **מה**: הצעות (offers), **לא** חיות כל יום.
- **רוטציה (HARD)**: Buy All, Bonanza, **Rolling Offer**, **RYD** הם **רוטציוניים** - לא להשתמש באותו אחד כל פעם; לפזר ביניהם.
- וריאציות ביצועים: Coins / Decoy Bonanza / Wild (דומים בהכנסה במדגם הנוכחי).

## 5. Rolling Offer
- **מה**: הצעה מתגלגלת במחזורים. חלק מקבוצת הרוטציה (#4).
- **מנצח**: Buy More for Less (~$132K/יום); חלש: Supersized.

## 6. MGAP
- **מה**: **מוצר שתמיד חי** במשחק; מריצים עליו פרומואים (Bigger Multipliers, BOGO, Matched, Wild Symbols, Night Plan).
- מנוע ההכנסה מס' 1. מנצח: Bigger Multipliers; יציב: BOGO.

## 7. Spin Zone / MES
- **מה**: **אתגר גיימפליי** שמטרתו **לשרוף קוינז (coin sink)** לשחקנים.
- תפקיד כלכלי: ניקוז מטבעות (איזון אינפלציה), לא מכירה ישירה.

## 8. X2 Dash Points (Clan-Dash)
- מכניקת דאש סטנדרטית. אין דגשים מיוחדים.

## 9. ADS PO (SPO)
- הצעה מבוססת פרסומת. אין דגשים מיוחדים. `ADS PO - <reward>`.

## 10. Extreme Stamp
- **מה**: מנגנון שנותן **ערך מוסף לכל ההצעות** שלנו.
- **השפעה**: כשה-Extreme Stamp פעיל, רואים **הכנסה גבוהה יותר מכל המוצרים** (מגביר רוחבי).
- **השלכה לשיבוץ**: לשבץ Extreme Stamp בחלונות שבהם רוצים להגביר את כלל המכירות (סינרגיה עם DD/PP/Rolling/Buy All).

---

## מגבירי הכנסה רוחביים (Amplifiers) - קטגוריה קריטית

ארבעה מנגנונים שמטרתם להגדיל את ההכנסה של **כל** ההצעות בו-זמנית. ה-KPI שלהם = הכנסה כוללת מכל המוצרים + Payment Page (לא מכירה ישירה משלהם):

### Boosted Gemback ⭐ (top promo)
- **מה**: כשהשחקן קונה משהו בזמן ש-Boosted Gemback חי, הוא זכאי להטבה - מקבל **gems back על כל שימוש בג'מס**.
- **KPI**: הכנסה של **כל ההצעות + Payment Page**. בהשקה -> צפי להכנסה גבוהה יותר מכל המוצרים.
- מנצח ברמת פרומו: Boosted Gemback מוביל ב-Gems (ראו `promo_revenue_analysis.md`).

### Gold Gem Stamp (GGS)
- **מה**: נותן לשחקן **יותר ג'מס** מעבר להצעה שהוא קונה. בד"כ נותנים 1; אם נותנים 2 - הטבה נוספת.
- **שימוש**: time-limited או על הצעות ספציפיות. צפי להכנסה גבוהה יותר באזור הזה.

### Jumbo Giveaway
- **מה**: קנייה בזמן ש-Jumbo Giveaway חי -> כניסה ל**הגרלה** עם פרסים גדולים. מגביר הצעות אחרות.

### Extreme Stamp
- (ראו #10 למעלה) - מגביר ערך רוחבי לכל ההצעות.

---

## פרומואים 11-20 (השלמות)

- **11. RYD (Reveal Your Deal)**: הצעה רוטציונית (קבוצת Buy All/Bonanza/Rolling/RYD).
- **13. Jumbo Giveaway / HH**: מגביר (ראו למעלה).
- **17. Pick Your Path (PYP)**: פרומו **גיימפליי**.
- **12 GGS / 14 Quest / 15 Gem Machine / 16 Dash Max / 18 Globez / 19 Blast / 20 Battlesheep**: GGS=Gold Gem Stamp (למעלה); השאר כוסו/ללא דגשים מיוחדים.

---

## כלל קריטי: פרומו ניקוז קוינז יומי (HARD)

**בכל יום** חייב לרוץ פרומו גיימפליי אחד לפחות שדוחף **צריכת קוינז (coin consumption)**. אפשרויות (תחת טאב **Core**):
- Spin Zone / Spins-on
- Win Master (MES)
- Pick Your Path (PYP)
- Machine Launch
- וכד'

תפקיד: איזון כלכלי - ניקוז מטבעות מול הזרקות.

## עדכון: יוני 2026.
