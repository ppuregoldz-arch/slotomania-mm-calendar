# MM Calendar - למידות תפעוליות (Best Practices)

> למידות מצטברות מסקירות חודשיות. כללי אצבע שהאייג'נט מיישם בעת שיבוץ ואיזון. רובם SOFT (best practice) אלא אם צוין HARD.

## מתודולוגיית ניתוח (HARD)
- ⭐ **בסיס ליפט = ממוצע ≥20 יום אחרון (trailing 20d)**. בכל השוואת אחוזי-ליפט של פרומו/רכישתי — משווים לממוצע נע של לפחות 20 הימים האחרונים. **לעולם לא להשוות ליום בודד** (±יום קדימה/אחורה).
- **אין להשתמש בעמודת "% Difference" יום-מול-יום** שמגיעה מדשבורדים (day-over-day) — היא רועשת; לחשב ליפט מול trailing-20d.
- **דעיכה נומינלית**: המשחק יורד מיום ליום → להשוות **בתוך תקופה** (relative ל-trailing-20d), לא על פני חודשים.
- מדגם: אות אמין רק ב-n≥3-4 ימים לאותו סוג; לסמן n קטן כ"כיווני".

## ברזל מתפעול (Itay — יולי 2026)
- **MGAP: בדיוק 2 פרומואים בשבוע** — לא 3, לא יותר. שבוע חלקי בסוף חודש (פחות מ-4 ימים בבלוק `(יום-1)//7`) = **מינימום 1**. גובר על גיידליין כלכלה "עד 3/שבוע" כשמתנגש.
- **מרווח בין MGAP ובין Shiny Show:** לפחות **2 ימים** בין פרומואים מאותו סוג (לא רצף).
- **Dash Pass — Dash Day:** לא שורה נפרדת בקלנדר (הוסר `Dash Pass — Dash Day`). ימי שני = תבנית Clan-Dash (Bundle · Go Premium · Monday Max · **Time Limited Prize** עם פרס מטבלת Dash של ניבי).
- **Puzzle M.E.S:** **18–24/8** · שורת Puzzle ל־~20% + **Core challenge נפרד** לקונטרול (~80%) באותו יום.
- **Spinner Clash:** **בדיוק 1× לכל שבועיים ISO** (ימים: `SPINNER_CLASH_DAYS` בבילדר — לא פעם בשבוע).
- **DD BOGO:** רק פרסים **repeatable** (Hammers, seasonal/mid-term SKUs, Reg וכו') — **לא** Shiny Limited / Wild once-only.
- **Piggy:** סטטוס **Offers & coin sale** (לא Core) — גם ב-Monday ובדשבורד.
- **Decoy Bonanza — d3 GGS (Itay, יולי 2026):** ב-denom האחרון **לא חובה 2 GGS**; **1 GGS + 4 RDS** תקף כשמתאים לכלכלה/ערך. **HARD** נשאר: d3 כולל **כל** פרסי d1+d2 + hook. בילדר August משתמש ב-2 GGS כברירת מחדל בלבד.

## צפיפות לוח Monday — סטנדרט שיבוץ חודש (Itay, מאושר אוגוסט 2026)

> **עקרון:** לא רק להוסיף — **למחוק/למזג** לפני סנכרון. מטרה: פוקוס, לא "מסך מלא".

### לכל יום (HARD על הלוח)
| כלל | פירוט |
|-----|--------|
| **Core משחקי** | **לכל היותר 1** ביום (PYP / Win Master / Ace Heist / Spinner / Spin Zone / Puzzle M.E.S / MES מכונה). **PYP:** לסובב פרס בכותרת (Reg/Ace, דרגה) — `pyp_finish_prize`, לא אותו 3★ Reg פעמיים באותו שבוע. **Spin Zone chase:** `spin_zone_chase_prize()` — לא **2 Dice / 2 Picks** בכותרת (SNL → Ace card; Blast → Superboom; Battlesheep → Parasheep). |
| **Shiny Show** | **1** ביום; **לא בימי שני** (Dash Day). מרווח ≥2 ימים בין Shiny Show. **וריאנט שונה בכל שבוע** (לא שני פעמים All Cards באותו שבוע — `assign_shiny_show_variants`). |
| **שילוב Shiny + Core** | Shiny Show + **פרומו gameplay אחד** — לא לערום שני gameplay + Shiny. |
| **Daily Deal** | **שורה אחת** ב-Monday: זוג Once+repeatable **ממוזג** (SKU השני בתיאור). |
| **Album / עוגן שיווקי** | פתיחת Shiny Collection וכד' → סטטוס **Album** (לא Core). **Config:** שורות Shiny Collection (Last Day / Opening) — **ללא** Config Status ב-Monday (כמו LBP / Lotto peak). |
| **יום שני** | DD + תבנית Clan-Dash (4 שורות) — **בלי** Rolling/RYD/Decoy/Prize Mania/MGAP/Coin Sale/Price Cut/Gemback/Shiny Show/Ace Loot כשורות נוספות. |
| **מגברי רכישה (GGS / Gemback / Price Cut)** | **לא לערום את שלושתם ביום אחד** — מקסימום שניים; אם יום חזק (Popup Store, Lotto peak) — להעביר **אחד** ליום שכן חלש (למשל Gemback 11→12 באוגוסט). ולידציה: `day_gem_revenue_amplifier_count` בבילדר. |

### סנכרון Monday (חובה)
- **⛔ HARD — לא לדרוס עריכות ידניות:** אם Itay/הצוות תיקנו שורות ב-Monday, **אסור** להריץ `upload_mm_calendar_day_monday.py --all` או טווח ימים רחב בלי אישור מפורש. הסקריפט **מעדכן כל שורה תואמת** לפי `august_2026_plan.json` + **מוחק יתומים** — זה מבטל תיאורים, תמחור, Config ו-Creative שעשיתם ידנית.
- **מתי מעלים:** רק **ימים/שורות ספציפיים** שהמשתמש ביקש במפורש (למשל `python3 scripts/upload_mm_calendar_day_monday.py 17`), או תיקון נקודתי שאתם מאשרים אחרי שמסמנים אילו ימים **off-limits** (כבר מתוקנים ידנית).
- **ברירת מחדל לסוכן:** עדכון **בילדר + JSON + learnings**; Monday = **לא** אלא אם נכתב במפורש "תסנכרן ל-Monday" / "תתקן במאנדיי" **ו**מוגדר scope (איזה תאריכים).
- `upload_mm_calendar_day_monday.py`: אחרי sync — **מחיקת יתומים** (`remove_orphan_day_items`) + dedupe + ניקוי Popup מחוץ ל-12–16.
- **לא** sync "add-only": כל פריט בתאריך שלא ב-`build_rows` → **delete** (עוד סיבה לא לסנכרן ימים שעברו עריכה ידנית).

### יישום בקוד (תבנית לחודשים הבאים)
- בילדר חודשי (`scripts/build_*_plan.py`): `is_gameplay_core_challenge`, `can_add_gameplay_core_challenge`, `consolidate_paired_daily_deals`, Shiny ללא Mon, `assign_second_offers` → Mon = None.
- ולידציה + `scripts/audit_*_plan.py`: Core משחקי ≤1, DD ≤1, Shiny ≤1.
- רפרנס: **אוגוסט 2026** (`build_august_2026_plan.py`, `august_2026_plan.json`).

## יצירתיות בשיבוץ (מותר)
- **מותר ליצור קומבינציות פרומו חדשות** — כל עוד הן מגיעות מהבנה של המכניקות והפרסים ותואמות: עונה חיה (Short/Mid-Term SKU), בנק קלפים, VFM, ותובנות הרבניו (להעדיף SB Wheel/Wild Supreme, להמעיט Clan Pack/Ace/Superboom-כללי). דוגמאות: DD "SB Wheel + <SKU עונתי>" · Buy All עונתי (SNL: Dice/Multiwheel · Battlesheep: Parasheep/Airstrike · Blast: Superboom/PAB).

## תובנות חקר רבניו (אפריל-יולי, `deep_research_insights.md`)
- **Extreme Stamp = מגבֵּר-העל**: כל שילובי הרבניו הגבוהים כוללים אותו (+17-24%, ~$750-780K/יום). לשבץ בחלונות שיא.
- **פרסי DD חזקים**: SB Wheel (+15%), Wild Supreme (+10%), Quest Booster (+8%), %SB/Wild Ace/Shiny (~+6%). **חלשים**: Clan Pack (−11%), Ace Card (−12%), Superboom (−7%), Picks (−6%), GGS (−5%). Hammers ≈ baseline על 92 יום.
- **קניבליזציה**: MGAP + Coin Sale יחד = −4.6% (מחזק VFM: עד אחד ליום). שילובים חלשים: Buy All+Clan-Dash (−6%), Clan-Dash+Gems (−3.5%).
- **שילובים טובים**: Buy All+Rolling (+16%), Album+SlotoBucks (+15%).
- **זמן**: שישי שיא ($714K) > שבת ($679K) > שני ($649K) > רביעי הכי נמוך ($545K). חצי ראשון של החודש > שני.

## למידות מדוח הערב היומי (Teams — ראו `daily_mm_reports.md`)
- **MGAP מרים את כל היום** (BOGO/Matched הפכו פתיחה 197→627). **Rolling 5-6 cycles M = מנוע משלמים** (משלים ל-BOGO); **Supersized חלש ויקר**.
- **ימי MGAP BOGO / Matched:** ההצעה השנייה **High Pricing** (בבילדר); DD → **Medium** אם היה High (כלל tier שונה).
- **Reveal פטיגה**: אל תריץ Reveal בפרומו-טיים אם רץ Reveal ב-night plan הקודם.
- **DDs מדורגים**: DD ראשון חייב להיות אטרקטיבי אחרת לא מניע רכישה.
- **Dice Deluxe דורש סורס דייס חינמי פעיל** כדי להניע רכישות.
- **בלנס ג'מס נמוך → חיזוקי ג'מס** (x2 GGS + Gemback + Coupon); **Gem Coupon חלש ברבניו**.
- **MES סוף-אלבום 72h → wager חזק מאוד בכל הטירים** (מנוע ניקוז). **MES min-bet מנפח wager, spins נמוכים**.
- **⚠️ ניטור טירים 6-7**: ירידת משחקיות = לשקול הורדת Extreme/Sale לשמירת מומנטום שבועי.
- **רוויה**: לא לרצף ימי-שיא (יום חזק → למחרת חלש). **סוף חודש מחלישים · תחילת חודש night plan חזק**.
- **FTD גבוה מ-Counter PO + Prize Mania** (לא DD).
- **DD עם Seasonal SKUs עבד טוב** (מחזק כלל התאמת-עונה); **Dash/Super-Dash challenges לא מזיזים wager**.
- **מכונה שנפתחת לכולם** (לא רק MES) מקניבלת רבניו/קונטרול.
- ⛔ **הפניית שחקנים למכונות Bucks מורידה את כל ה-KPIs/רבניו** (אושש בטסט 8/6) — להימנע כשרוצים רבניו.
- **דפוס יומי**: בוקר 00-02 UTC חזק · שפל 03-10 · התאוששות מ-Promo Time 11:00 (לתזמן בקאפים בשפל).
- **Dash Day לוקח פוקוס** (הצעות אחרות ממוצעות) · **Price Cut לא טריטמנט משלמים נכון למחיר-נמוך** · **Prize Mania בסייל = מנוע משלמים**.
- **DD BOGO נשחק** (עולה כל שבוע — לגוון) · **לא לערום 2 לילות Boosted רצופים** (בלנס ג'מס גבוה פוגע ב-Gems Sale) · **Dice Deluxe צריך Dice Loot/100% Bucks על הרכישה**.
- **Golden Spin featured → חזק** · **ימי שלישי PU עולה** · **Payment Page חזק בסייל/דאש**.
- ⭐⭐ **DD BOGO = מנוע ניקוז הג'מס הטוב ביותר** (ימי השיא בשריפת ג'מס — 44M/52M — היו BOGO, למרות שלא נותן ג'מס!). יום עם בלנס ג'מס גבוה → DD BOGO.
- **MGAP BOGO מרים DD דרמטית** (86K מול 32K ממוצע) · **MGAP עם Bucks מגיב חלש** — להעדיף BOGO/Bigger/Matched.
- **טריטמנט משלמים אפקטיבי**: "Make any purchase → bundle" (DPU30+/NPU) · "Wild ברכישת חבילת חנות גבוהה" (מרים חנות) · DD עם Wild מתחזק בכל רכישה (109K).
- **Gems Sale עם בלנסים גבוהים → חובה פרומו משחקי לג'מס (מכונה)** לשריפה, אחרת רבניו נמוך.
- **MES 3 ימים לא מחזיק גיים-פליי לבד → לחזק ביום 3** · **Rolling More for Less לא מחזיק יום שלם → לתמוך בטופר/HH/DDs**.
- **פתיחת ADS לאוכלוסייה רחבה → ליפט רבניו** · **News feed לא ריק** · **פיצ'רים סוציאליים מייצרים engagement**.
- ⭐ **Rolling More for Less: cooldown ~1.5-2 שבועות** (כלי חזק אך נשחק — לא פעמיים באותו שבוע). וריאציות חלשות: **סייקל-בודד**, **Buy & Get 8**. המנצח = Buy More for Less.
- **Buy More for Less (BMFL) — תבנית ברירת מחדל (אוג׳ 2026, 3/8):** תמחור **High** (לא Medium). תיאור מחזורי — **ללא** ערימת פרסים (לא 5/7/9 Hammers + כותרת stamps ארוכה). לכל cycle בשורה אחת:
  - Cycle 1: Coins (low) + Gems \| 100% SB \| 3★ Reg \| **2 Hammers \| 3 RDS \| 1 GGS**
  - Cycle 2: mid \| 200% SB \| 4★ Reg \| **4 Hammers \| 3 RDS \| 1 GGS**
  - Cycle 3: high \| 300% SB \| 5★ Reg \| **6 Hammers \| 3 RDS \| 2 GGS**
  - קבועים בבילדר: `BMFL_*_BY_CYCLE`, `ROLLING_BMFL_PRICING = High`.
- **קניבליזציה**: לא לערום DD + הצעות נוספות עם SKUs חזקים (Buy All נחלש) · **MGAP Matched הרבניו צונח כשהוא יורד** (לתזמן) · **Progress Pack חזק ב-Dash Day**.
- **ניהול טופרי ג'מס**: לרוטט (GGS/Coupon לא יחד) · לבטל כשהבלנסים גבוהים · **עונות/Stickers + Dash missions מניעים ג'מס בלי טופר ג'מס ייעודי**.

## למידות כלליות

- **הזזת פיק LBP**: כשמזיזים את פיק ה-LBP ליום אחר, **לשמור את הפיק הרגיל באותו יום** - כדי לשמר הרגל משחק יציב.
- **Daily Deal BOGO Coins** ביצע מצוין **גם בלי Gems**.
- **MGAP SB promo** - להשתמש כ-**topper** (תוספת), לא כפרומו המרכזי של היום.
- **Rolling Offer M Pricing עם מספר cycles** עבד טוב על **Buy X Get Y** (לא BMFL). **Buy More for Less = תמיד High.**
- **להוסיף alerts לעונות Mid & Short** - לוודא שהן עולות בפועל (HARD תפעולי).
- **להוסיף PU supported offers בימי MGAP.**
- **בימי Dash** - לתמחר לפחות הצעה אחת ב-**Max price** כדי להעלות AVG TRX.
- **במהלך sales - להשהות תקשורת DPU Treatment** (לא להריץ winback של DPU בזמן סייל כללי).

## למידות Gems

- **כל Gems Sale חייב כולל תוכנית follow-up של 24-48 שעות** שמתמקדת בצריכת ג'מס. דוגמאות follow-up טובות אחרי Gems Sale:
  - Daily Deal BOGO ללא Gems
  - Shiny Show חזק
  - פרומו ממוקד מכונה (Machine-focused)
- **בימי Gems** - להוסיף עוד פרומואי צריכת ג'מס.
- **HARD**: **אין x2 GGS יחד עם Gems Sale.**

## למידות נוספות (פיצ'רים)

- **SB Machines** - פרומואים time-limited משפיעים **שלילית על הרבניו בטווח הקצר**. דרושים לפחות 2 טסטים נוספים לבדוק אם יש השפעה חיובית בטווח הארוך. (זהירות בשימוש.)
- **Extreme Stamp** - כלי standalone חזק; **להימנע משימוש בו על sales** (4 ביולי = יוצא דופן). (HARD exclusion - ראו `constraints.md` §6.)
- **שורת לוח (X2):** **`X2 Extreme Stamp`** — Product **Extreme Stamp**; **ללא** Config ו**ללא** Pricing (מגביר כמו x2 GGS, לא Offers & coin sale).
- **x2 GGS:** Product **Gems**; **Creative Label = Reuse**; **ללא** Config (מגביר timed — לא Gems Sale).
- **New looks לפרומואים מתמשכים** - Boosted Gemback, MGAP Wild Symbols, MGAP Bigger Multipliers (לרענן ויזואלית).
- **Machine Launches** - צומצמו ל-**2 מכונות בחודש** (במקום 3) מ-Slots Central. **להגדיל פעילויות Core מצד MM כדי לגשר על הפער.**

## תהליך עבודה - Creative & MM Collaboration

- **Briefs** - תדריך פנים-אל-פנים כשאפשר + הקלטה לשימוש עתידי.
- **Draft sketches** - לפרומואים חדשים, סייל גדול והשקות, לפני המשך לגרסאות סופיות.
- **ערוץ תקשורת מאוחד** - ערוץ יחיד למניעת side chats.
- **Major Events** - נציג Creative משולב בתכנון אירועים גדולים.
- **PLC** - שלב נוסף ב-PLC (שלב הביצוע) עם פגישת handover לשיתוף ידע (Product Manager, UX, MM Creative, Copy Writer).
- **Calendar Planning** - נציג Creative מצטרף ל-MM owner של אותו חודש לתכנן **פרומו חדש אחד בשבוע** בשלב התכנון.
- **Monday upload — Creative Label:** שורת **Mega Pods Season** (Mid Term) = **Reuse** (לא New theme for promo); Winovate Season / Short Term / Album נשארים לפי הכללים הקיימים.

## מטרות חודשיות (Monthly Objectives) - נלוות לגיידליין החודשי

בנוסף ל-caps, הכלכלה מגדירה **מטרות חודשיות** שמכוונות את הדגשים. דוגמה (יוני 2026):
- Focus on PU (paying users)
- השקות: Buy All 2.0 (Soft+Full), Extreme Gem Stamp (Soft), SNL (Soft #2+Full), Social Streak (Full)
- World Cup celebrations
- **Reduce Balances towards 4th of July** (דחיפת coin sinks/צריכה לקראת אירוע)
- Maintain weekend sales strategy

> מטרות אלה משפיעות על תעדוף: למשל "Reduce Balances" -> יותר coin sinks (MES/Spin Zone); "Focus on PU" -> יותר הצעות למשלמים; השקות -> לשבץ Soft/Full Launch בתאריכים שנקבעו.

## השקות פיצ'רים (Feature Launches) - קלט חיצוני
השקות (Soft Launch / Full Launch) מתוזמנות בתיאום, ומשובצות כאבני דרך בקלנדר (דוגמת יוני: Jewel Grove machine, Yard Sale, Super Dads' Sale, Woofing Wins). לבקש מהמשתמש את לוח ההשקות אם לא ידוע.

## Rolling Offer — מבנה BXGY (5 / 6 cycles)

⭐ **מקור אמת מלא:** `rolling_offer.md` — שלד **6 denoms לכל cycle** (Pay + 1 RDS + 1 GGS על הרכישה; SB → hook → Hammers → RDS → GGS).  
⛔ **לא** מודל Pay בלי חותמות + Free1=1RDS/Free2=3RDS (עזר ישן בבילדר אוגוסט).

- **5 cycles:** תבנית **Supersized** (1% / 3% / 5% + Picks) — בקובץ למעלה.
- **6 cycles:** דוגמה חיה **2026-07-01** (M, Parasheep/AS) — בקובץ למעלה.
- **ביצועים:** 5–6 cycles **M** = מנוע משלמים; Supersized לרוב חלש/יקר; **BMFL** = VFM נפרד (3 cycles, High).

---
**עודכן:** יולי 2026.
