# MM Calendar - Core / MES: צ'אלנג' עם פרס בסוף + רפרנסים מוכנים

> **Core = צ'אלנג' לשחקן** (גיימפליי) שבסופו השחקן **מקבל פרס**. מנגנונים: MES (Mission), Spin Zone, Win Master, Ace Heist, Gold Hunter, PYP. תפקיד כפול: ניקוז קוינז (coin sink) + חלוקת קלפים (הפרס).
> ⭐ **PYP (Pick Your Path)**: השלמת **3 מתוך 4 משימות** → פרס (פרס בשם השורה). **Description ב-Monday = רשימת משימות בלבד** — 3 קבועות + 1 לפי Short Term (Blast→Superboom · Battlesheep→2 Airstrikes · SNL→4 Dice Rolls). ראו `pyp_missions_description()` בבילדר.
> ⭐ **Ace Heist**: **Description = משימות קבועות** (פרס בשם השורה): Spin 30 — any game · Reach final act — Shiny Show · Open 8 pods. ראו `ace_heist_missions_description()` בבילדר.
> מקור רפרנסים: `CRM3/Features/MES`.

## מבנה הצ'אלנג' (מאומת ויזואלית)
- מסך פתיחה (arena / missions) -> השחקן מתקדם ע"י ספינים/משימות -> **מסך זכייה** עם הפרס.
- דוגמה מאומתת (`2026_06_14_Spin_Zone_Generic_NEW/Winner_Inapp`): **"SPIN MASTER! YOU WON"** + **Rare Pack (Gold + Ace cards)**.
- **הפרס בסוף הוא בד"כ חבילת קלפים** (Rare/Gold/Ace) - מתואם לחלוקת הקלפים השבועית של ניבי.
- מבנה תיקייה: `UI/` (arena_missions_bg, Grand-Prize, sku_icon) + `Winner_Inapp/` + `Banner/`.

## רפרנסים מוכנים ב-CRM3/Features/MES

### Generic (ניתן לשימוש חוזר)
- Spin Zone (03/23) · Spin Zone New Sheriff · Spin Zone Generic NEW (06/14) · Spin Zone Sticker 5Ace (07/02)
- Win Master (03/24, 05/01) · Win Master Sticker (07/01)
- Ace Heist (05/31) · Gold Hunter (03/23) · MES Wild Supreme (06/18)
- **Card Challenge - End of Album (06/29)** - ייעודי לסוף אלבום
- Gems Machine (05/26, 06/30, 07/02)

### Themed (לאירוע/חג)
- Cinco de Mayo (05/05) · World Cup (06/13) · Red Carpet (06/21) · Woofing Wins (06/25) · 4th of July (07/04)

### Machine-tied (קשור להשקת מכונה)
- Tumbling Totems (05/15) · Sweet Ambrosia (05/28-29) · Jewel Grove (06/04) · SlotoLand (05/22) · SB Machines (06/08, 06/15, 06/30)

### Segment-tied
- BD Safe N Spin (07/02) - **Black Diamond** (VIP)
- Purchase Streak / SlotoLand Purchase (05/26)
- Clan Packs (05/17) - פרס Clan Pack

## השלכות לשיבוץ
- **כל Core בקלנדר = צ'אלנג' עם פרס בסוף** - לציין את הפרס (קלף/pack) שמתואם למאגר השבועי.
- ⚠️ **פרס צ'אלנג' משחקי לא יכול להיות Gold** (Gold רק ברכישות). פרסי Core = Regular / Ace / Shiny / Wild. Gold מותר רק כשהצ'אלנג' גייטד ברכישה (Pay-to-Play).
- ביום עם השקת מכונה -> להעדיף MES machine-tied (Spin Zone/Win Master עם קלפי המכונה).
- בסוף אלבום -> "Card Challenge - End of Album".
- אירוע/חג -> רפרנס themed מתאים; אחרת -> generic מוכן (reuse).
- הפרס משרת **גם** את חלוקת הקלפים (לא רק ADS PO / Shiny Show / DD).

---
**עודכן:** יוני 2026.
