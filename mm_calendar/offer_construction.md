# MM Calendar - איך ממלאים תוכן ל-Offer (Offer Construction)

> נלמד מהתיאורים האמיתיים (בורד MM calendar + Operation-Monetization). זהו המדריך לבניית **התוכן (SKUs) של כל הצעה** - מה שנכנס ל-Description כמו במאנדיי.

## ⭐ עיקרון-על: כל Offer/Promo הוא פלטפורמה, לא מתכון קבוע
**כל אחד מהאופרים והפרומואים שלנו הוא מיכל (container/platform) עם מבנה slots — לא רשימת SKUs נעולה.** לכל סוג יש:
- **מבנה קבוע** = כמה denoms/slots, מטבע בסיס, וההוק (hook) שמאפיין אותו.
- **מאגר פרסים גמיש** = לתוך כל slot אפשר להזרים **כל אחד** מהפרסים מהמאגר המשותף (למטה). ה-SKU ה"טיפוסי" הוא רק דוגמה נפוצה — לא הכרח.

**המנהל בוחר מה להזריק לכל slot לפי:**
1. **תמחור** (M/H/Max) — קובע כמות/דרגת הפרס.
2. **מטרה** — coin sink / gem sink / חלוקת קלפים / דחיפת SB / winback.
3. **בנק הקלפים השבועי** (`album_cards.md`) — איזה קלפים מותר לחלק השבוע.
4. **סגמנט** (DPU / NPU / Non-Finishers / Inner Circle / Black Diamond).
5. **מה כבר משובץ באותו יום** — הימנעות מקניבליזציה (VFM) וגיוון פרסים.

> לכן: לאותו "Rolling More for Less" ב-3 ימים שונים יכולים להיות 3 תכנים שונים לגמרי. אותו דבר לגבי Buy All, Decoy, DD, RYD, Prize Mania וכו'.

## 🎁 מאגר הפרסים המשותף (Reward Pool) — מה אפשר להזריק לכל slot
- **מטבעות בסיס**: Coins, Gems.
- **Stamps / מגברים**: RDS (Red Diamond Stamp), GGS (Gold Gem Stamp), % SB (SlotoBucks 100/150/200/300/500%+), Superboom, Extreme Stamp.
- **גיימפליי / boosters**: Hammers, Picks, PAB, Airstrike (AS), Parasheep, Dice Booster (6/12/24h), Free Spins, Ace Spins, SNL Dice.
- **פרס עונת Mid-Term**: Quest → **Quest Booster** · **Globez / Figz → 3000 Hero Coins** (פרס העונה הקבוע — לא Booster). **ניתן לשבץ 3000 Hero Coins כ-SKU של DD/הצעה כשעונת Globez/Figz באוויר.**
- **קלפים** (לפי בנק שבועי): Reg (2★-5★), Ace (3★-5★), Gold, Wild (Ordinary/Ace/Any/Supreme/Gold), Shiny.
- **הוקים מיוחדים**: 48h access למכונה חדשה, prize wheel, price cut, chance-based (עד 500%).

> כל SKU מהמאגר יכול להיכנס כמעט לכל slot — כפוף לתמחור, למטרה ולכללי ה-Gold (Gold מותר רק ב-slot של רכישה, לא בצ'אלנג' משחקי).

### ⚡ החלפת חותמות בימי Extreme Stamp (HARD)
ביום שבו רץ **Extreme Stamp** במשחק, כל ההצעות משדרגות את החותמת:
- **Extreme Stamp במקום Red Diamond Stamp (RDS)** בכל הדנומים.
- **במקום 4 RDS → 2 Extreme Stamps** (ערך גבוה יותר לשחקן).
- **Rolling Offer (BXGY / BMFL) on Extreme days:** per-cycle rules in `rolling_offer.md` § **Extreme Stamp day + Rolling** (cycle 1 unchanged; from cycle 2 — Extreme on pay + free stamp steps, not RDS).

## מבנה לפי סוג הצעה (STRUCTURE = קבוע · CONTENT = גמיש מהמאגר)

### Rolling More for Less — פלטפורמה של 3 denoms מדורגים
- **מבנה קבוע**: 3 denoms, כל אחד "הכל-כלול", ערך עולה d1<d2<d3.
- **Slots בכל denom (מלא מהמאגר)**: מטבע בסיס (coins/gems) · Stamps (GGS/RDS) · % SB מדורג · **+ 1-2 פרסים חופשיים מהמאגר** (hammers / קלף / superboom / dice / picks / AS...).
- **תמחור**: Buy More for Less = **High** (H).
- **תבנית תיאור מומלצת (BMFL, 3 cycles)** — פרסים **בשורת המחזור** (לא לערום יותר מדי; אוג׳ 2026):
  - `Cycle 1: Coins (low tier) + Gems | 100% SB | 3★ Reg card | 2 Hammers | 3 RDS | 1 GGS`
  - `Cycle 2: … mid … | 200% SB | 4★ Reg | 4 Hammers | 3 RDS | 1 GGS`
  - `Cycle 3: … high … | 300% SB | 5★ Reg | 6 Hammers | 3 RDS | 2 GGS`
- **גמיש לגמרי**: אפשר לבנות Rolling More for Less שכולו קלפים, או שכולו hammers, או מיקס — לפי המטרה של אותו יום. ה-%SB המדורג (100→200→300) הוא הדפוס הנפוץ אבל לא חובה.
- דוגמאות אפשריות (אותה פלטפורמה, תוכן שונה):
  - *coin sink*: d1 coins+100%SB+5H · d2 coins+200%SB+10H+PAB · d3 coins+300%SB+Superboom+3★ Gold.
  - *card push*: d1 coins+4RDS+2★ reg · d2 gems+4★ reg+GGS · d3 GGS+Wild Ace+Superboom.
  - *gem sink*: d1 gems+GGS · d2 gems+2 GGS+Dice Booster · d3 gems+3 GGS+Ace 5★.

### Rolling Offer (Buy X Get Y) — פלטפורמה של denom רכישה + N denoms חינמיים
- **מקור אמת למבנה 5/6 cycles:** `rolling_offer.md` (שלד 6 denoms לכל cycle — Pay עם חותמות, לא מודל Free1=1RDS/Free2=3RDS).
- **מבנה קבוע (BXGY 2 / 5 / 6 cycles):** בכל **cycle** — **6 denoms**: (1) Pay = coins/gems + **1 RDS + 1 GGS** → (2) % SB → (3) hook (supersized / picks / עונה / קלף) → (4) Hammers → (5) 2–3 RDS → (6) 1 GGS. **5-cycle supersized** ו-**6-cycle עונתי** — תבניות מלאות שם.
- **Buy 1 Get 8:** cycle יחיד — 1 Pay + **8** free steps (לא אותו שלד 6).
- **Slots חינמיים (3–6 ומעלה)**: % SB / Hammers / AS / קלף / Dice / Quest Booster / RDS / GGS / PAB — מהמאגר, לפי יום.

### Buy All — פלטפורמה של 2 denoms (בסיס מטבע+חותמת)
- **מבנה קבוע**: 2 denoms, קונים את שניהם. כל denom = מטבע + חותמת תואמת + פרסים נוספים.
  - **Coins+Red denom**: מבוסס **Coins + Red Stamps (RDS)** + פרסים נוספים מהמאגר (hammers / card wheel / dash-point wheel / coin grab).
  - **Gems+Gold denom**: מבוסס **Gems + Gold Gem Stamps (GGS)** + פרסים נוספים מהמאגר (Hammer wheel / SNL dice / ace spins / shiny card / superboom).
- **על שני הדנומים יש פרסים נוספים** מעבר לבסיס.

### Decoy / Bonanza / Triple Offer — פלטפורמה של 3 denoms
- **מבנה קבוע**:
  - **denom 1 (M)**: **Coins + RDS** + פרס(ים) מהמאגר (Dice, Reg, Superboom, PAB, …).
  - **denom 2 (H — decoy middle)**: **Gems + GGS** + פרס(ים) מהמאגר (3000 Hero Coins / Quest Booster / קלף / AS / …) — **Mid-Term פעיל** (Globez/Figz → Hero Coins; Quest → Quest Booster).
  - **denom 3 (H / Max — bundle)**: **Coins + Gems + חבילת חותמות מלאה** — בדרך כלל **4 RDS + 2 GGS**, **מותר גם 4 RDS + 1 GGS** (Itay, יולי 2026) + **כל הפרסים מ-d1 ומ-d2** + **פרס נוסף שמיועד ל-d3 בלבד** (hook עליון).
- ⭐ **denom 3 = d1 + d2 + עוד (HARD — תפעול Monday)**  
  השחקן צריך לראות ש-d3 **כולל את מה שקיבל ב-d1 וב-d2**, בתוספת ערך bundle:
  1. **מטבעות + חותמות:** Coins + Gems + **4 RDS** + **1 או 2 GGS** (d1≈RDS, d2≈1 GGS; d3 = לפחות 4 RDS, GGS לא חייב לעלות ל-2).
  2. **פרסי d1 + d2:** כל SKU שמופיע ב-d1 **וגם** ב-d2 חוזר ב-d3 (למשל 2 Dice + 3000 Hero Coins; PAB + 3★ Reg).
  3. **פרס נוסף ב-d3:** hook שלא מחליף את (2) — % SB, Hammers (אם מקור יחיד ליום), **5★ Gold / Wild / Shiny Limited**, וכו'.
  - בתיאור Monday מומלץ: **`d3 (bundle): ALL ABOVE + …`** או רשימה מפורשת שמכילה **את כל** פרסי d1/d2.
  - **לא** לשים ב-d3 רק “שילוב בסיסים + Gold” **בלי** פרסי d1/d2 — זה שובר את לוגיקת Decoy.
- **תמחור:** בדרך כלל **M · H · H** (d3 לפעמים **Max** כשה-hook עליון).
- **Triple Equal**: וריאציה עם 3 denoms שווים (לא Decoy קלאסי — כלל d3 למעלה לא חל).

**דוגמה (SNL + Globez, premium d3):**
```
d1: Coins + 4 RDS + 2 Dice
d2: Gems + 1 GGS + 3000 Hero Coins
d3: Coins + Gems + 4 RDS + 2 GGS + 2 Dice + 3000 Hero Coins + 100% SB + 5★ Gold
     ↑ ALL d1/d2 prizes        ↑ hook d3-only (Hammers only if single hammer source that day)
```
**דוגמה (d3 עם 1 GGS — תקף):** `d3: Coins + Gems + 4 RDS + 1 GGS + … + ALL d1/d2 prizes + hook` (Monday ref: Decoy עם `1 GGS, 4 RDS` ב-bundle — `sm_monday_ref_buy_all.md` 2026-05-11).

מקורות board: `documentation/monday_refs/sm_monday_ref_buy_all.md` (Decoy Bonanza), למשל “ALL ABOVE + …”.

### Daily Deal (DD) — פלטפורמה של bundle יומי
- **מבנה קבוע**: Coins + Gems + **SKU מרכזי אחד** (או כמה), + תמחור.
- **Slot מרכזי (מהמאגר)**: Hammers / Wild X / SB Wheel / Superboom+Gold / 100%SB+AS / picks / קלף / Dice — **כל דבר מהמאגר**.
- נדיבות לפי תמחור: Max≈12 Hammers / High≈8 / Med≈3-6 (וכך יחסית לכל SKU אחר).
- וריאציות מבנה: segmented (Finishers/Non-Finishers), After Purchase / 2nd purchase, Upsale (Double PO), חלונות שעה.
- ⭐ **Multiple מול Once-per-player (HARD)**: DD רגיל = **multiple** (השחקן קונה כמה שירצה). **DD עם Wild או Shiny Limited = once-per-player** — ואז **חובה לשבץ DD multiple נוסף** שמחליף אותו לאחר הרכישה (הפרס המחליף בלי Wild/Shiny Limited; רצוי SB Wheel/Hammers). כך השחקן לא נשאר בלי DD פעיל.

### RYD (Reveal Your Deal) — פלטפורמה רוטציונית
- **מבנה קבוע**: Coins + Gems + **hook** + RDS + % SB.
- **Slot ה-hook (מהמאגר)**: קלף / Superboom / 48h access למכונה חדשה / free spins / Surprise Gift — מתחלף ברוטציה.
- ⭐ **תמיד לשבץ פרסים נוספים מעבר ל-SlotoBucks** (קלף / Hammers / Booster) — ה-SB לבדו לא מספיק.
- ⛔ **אין להשתמש ב-155% SB** — זהו ערך תמתי חד-פעמי (Cinco de Mayo). השתמש בערכי SB סטנדרטיים (100/150/200%).

### Prize Mania — פלטפורמה של חבילת פרסים
- **מבנה קבוע**: אוסף פרסים בחבילה אחת.
- **Slots (מהמאגר)**: כל מיקס — לדוגמה 4 RDS + Wild Gold + 2 GGS + Dice Booster + coins + gems, או coins/gems/4 RDS/1 GGS/6 Hammers/100% SB.

### Stash Bundle / Surprise Box — פלטפורמה של "קופסה" חד-פעמית
- **מבנה קבוע**: surprise box, once per player.
- **Slots (מהמאגר)**: לדוגמה 3★ reg pack + quest booster + 7 hammers + 2 picks + Dice Booster 6HR + coins.

## ⛓️ שני מסננים מחייבים על תוכן ה-slots
לפני שקובעים מה נכנס לכל slot, כל פריט חייב לעבור:

### 1) תאימות לגיידליינים (HARD)
- **Hammers — מקור יחיד ליום (HARD)**: רק **מוצר אחד ביום** נותן Hammers. אם זה **Rolling** — מותר לתת Hammers **על פני כמה denoms/סייקלים** של אותו Rolling, אבל **לא במוצר נוסף** באותו יום. כמות לפי תמחור: Med 3-6 / High ≤8 / Max ≤12; ≤4/שבוע. שאר ההצעות באותו יום → פרס חלופי (Picks/PAB/קלף) במקום Hammers.
- **פרס עונה**: Globez/Figz = **3000 Hero Coins** (לא Booster); Quest = Quest Booster.
- **Gold**: רק ב-slot של **רכישה** (offers = רכישה → מותר). **אסור** כפרס בצ'אלנג' משחקי (Core/PYP/MES).
- **Wild**: ≤1 per source (מקסימום קלף Wild אחד לכל הצעה).
- **קלפים**: אך ורק מ**בנק הכלכלה של אותו שבוע** — סוג בבנק, כמות ≤ בנק (1★/2★ on top).
- **caps חודשיים** מהגיידליין (GGS ≤2/שבוע, Gems Sale ≤4/חודש וכו') — לא לחרוג דרך תוכן ההצעות.

### 2) התאמה לעונות שבאוויר (באותו יום)
- **Seasonal Booster** = הבוסטר של ה-**Mid-Term הפעיל** באותו יום (Quest/Globez/Figz Booster) — לא בוסטר של עונה שאינה חיה.
- **דרגת הקלפים** לפי **שלב האלבום**: פתיחת אלבום (wk1) → קלפים נמוכים (Reg 2★/Ace 3★) + Shiny M1; אמצע → בינוני.
- ⭐ **שבוע אחרון לסוף אלבום (HARD)**: בהצעות הרכישתיות משבצים **Wildים בלבד** (Wild Ordinary/Ace/Any/Gold) — **לא** Reg/Ace/Gold רגילים. בתקופה זו רק Wildים מזיזים (השלמת אלבום); שאר הקלפים לא אפקטיביים.
- **פריטים תמתיים**: ביום השקת מכונה → קלפי/פרסי מכונה themed; ביום אירוע → פרסים בנושא האירוע.
- ⭐ **SKU עונתי חייב להתאים ל-Short-Term הפעיל**: **Blast → Superboom / PAB** · **Battlesheep → Parasheep / Airstrike (AS)** · **SNL → Dice / Multiwheel / Shield**. אסור לשבץ SKU של עונה שאינה חיה (למשל AS ביום SNL). ⚠️ **SnL Dice בכפולות של 2 או 3 (לא 1).** אם מבינים את הקשר — מותר ליצור קומבינציות חדשות תואמות-עונה.

## איך למלא תוכן להצעה חדשה (תהליך)
1. זהה את **סוג ההצעה** = בחר את הפלטפורמה (Buy All / Decoy / DD / RYD / Rolling...).
2. קבע את **המטרה** של אותו יום (coin sink / gem sink / קלפים / SB / winback).
3. מלא כל **slot** בפריט מהמאגר שמשרת את המטרה — לא להיצמד ל"מתכון" ברירת-מחדל.
4. כוונן **תמחור** (M/H/Max) → משפיע על נדיבות/דרגת הפרס בכל slot.
5. **העבר כל slot בשני המסננים למעלה** (גיידליינים + עונות חיות): קלפים מבנק השבוע, Gold רק ברכישה, Seasonal Booster של העונה הפעילה, themed לאירוע/מכונה.
6. הוסף **תג סגמנט** אם רלוונטי, וּודא **גיוון** מול שאר הפריטים באותו יום (VFM / חזרתיות).

---
**עודכן:** יולי 2026. מקורות: בורד MM calendar (18388590642) + Operation-Monetization (2109172490).
