# Rolling Offer — מקור אמת לתוכן ולמבנה (BXGY / BMFL)

> **מטרה:** להגדיר איך **בונים ומתארים** Rolling Offer בקלנדר וב-Description — לפי **מאנדיי תפעולי** (`offer_construction.md` + דוגמאות חיות).  
> **לא** מחליף שיבוץ ימים בבורד — רק אנטומיה של המוצר.  
> **היסטוריית בורד (pull):** `documentation/monday_refs/sm_monday_ref_rolling_offer.md` — דוגמאות ישנות, לא כלל שיבוץ.

**עודכן:** יולי 2026

---

## שתי משפחות (אל תערבב)

| משפחה | מחזורים | מבנה | תמחור (אוג׳ 2026+) |
|--------|---------|------|---------------------|
| **Buy X Get Y (BXGY)** | 1 / 2 / **5** / **6** | Pay + שרשרת denoms חינמיים **לכל cycle** | M / High / Max לפי יום |
| **Buy More for Less (BMFL)** | **3 בלבד** | 3 denoms — כל אחד bundle מלא (coins+gems+SB+פרסים) | **High בלבד**; עוגני MFL בלבד |

- **BMFL** ≠ BXGY 5/6. שם שונה, לוגיקה שונה, cooldown נפרד (`constraints.md` / `learnings.md`).
- **Supersized** = וריאציית **BXGY** (בד"כ **5 cycles** + supersized %), לא סתם "שם יפה".

---

## BXGY — שלד קנוני: **6 denoms לכל cycle**

זה המבנה שמופיע בפועל ב-Description במאנדיי (למשל **2026-07-01 — Rolling 6 cycles**, **Rolling -15.05 — 5 cycles supersized**).

| Denom | תפקיד | תוכן |
|-------|--------|------|
| **1** | **Pay (רכישה)** | **Coins + Gems + 1 RDS + 1 GGS** |
| **2** | SlotoBucks | **% SB** — עולה ממחזור למחזור (100 → 150 → 200 → 250 → 300…) |
| **3** | Hook | **משתנה לפי יום** — supersized % / Picks / קלף / **SKU עונה** (Parasheep, AS, SNL Dice…) |
| **4** | פטישים | **Hammers** — מקור הפטישים **היחיד** באותו יום (מותר לעלות לאורך המחזורים) |
| **5** | RDS נוסף | **2 RDS** או **3 RDS** (לא פיצול 1+3 ב-denoms 1–4 של החינמיים) |
| **6** | GGS | **1 GGS** |

**פריסה במאנדיי:** לעיתים מסומן `Cycle N` + מספרי denom גלובליים (1–36 ל-6 cycles). המשמעות נשארת: **6 שלבים לכל cycle**.

### איך לפרק Description

1. זהה **כמה cycles** (5 / 6 / 2 / 1).
2. בכל cycle חפש **Pay** (denom 1) → חייב **1 RDS + 1 GGS** על הרכישה.
3. denom **2** = SB%; **3** = hook; **4** = Hammers; **5** = RDS; **6** = GGS.
4. **חריגים מוכרים:** cycle 2 ב-5-cycle supersized **בלי denom 3**; cycle 5 ב-supersized לפעמים **7 denoms** (RDS/GGS בשלבים 6–7).

### ⛔ מודל שגוי (לא ללמד / לא להעתיק ל-Monday)

בבילדר `scripts/build_august_2026_plan.py` יש עזר ישן `rolling_bxgy_cycle_body`:

- Pay **בלי** חותמות
- Free 1 = 1 RDS, Free 2 = 3 RDS, Free 3–4 = GGS…

**זה לא המבנה התפעולי של BXGY 5/6 במאנדיי.** עד שיישרו את הבילדר — לכתוב Description לפי **המסמך הזה** ולפי דוגמאות למטה, לא לפי JSON ישן של אוגוסט.

---

## BXGY — 5 cycles · Supersized (תבנית build reference)

**מתי:** BXGY (לא BMFL); דגש Blast — **supersized 1% / 3% / 5%**, **3 Picks** ב-cycle 4.  
**Pay בכל cycle:** Coins + Gems + 1 RDS + 1 GGS

| Cycle | 2 SB% | 3 Hook | 4 Hammers | 5 RDS | 6 GGS |
|-------|-------|--------|-----------|-------|-------|
| 1 | 100% | supersized **1%** | 3 | 2 RDS | 1 GGS |
| 2 | 150% | *(אין denom 3)* | 5 | 2 RDS | 1 GGS |
| 3 | 200% | supersized **3%** | 7 | 2 RDS | 1 GGS |
| 4 | 250% | **3 Picks** | 10 | 2 RDS | 1 GGS |
| 5 | 300% | supersized **5%** | 12 | 2 RDS (step 6) | 1 GGS (step 7) |

**שורות תמצית:**

```
Cycle 1:  pay · 100% SB · supersized 1% · 3 Hammers · 2 RDS · 1 GGS
Cycle 2:  pay · 150% SB · (skip 3) · 5 Hammers · 2 RDS · 1 GGS
Cycle 3:  pay · 200% SB · supersized 3% · 7 Hammers · 2 RDS · 1 GGS
Cycle 4:  pay · 250% SB · 3 Picks · 10 Hammers · 2 RDS · 1 GGS
Cycle 5:  pay · 300% SB · supersized 5% · 12 Hammers · 2 RDS (step 6) · 1 GGS (step 7)
```

**גיוון:** ב-cycle 4 אפשר **3 Parasheeps** במקום 3 Picks (Battlesheep חי).  
**ולידציה:** סכום RDS/GGS **למחזור** על הטקסט המלא (כולל Pay), לא רק "6 free steps" גנריים.

---

## BXGY — 6 cycles · דוגמה חיה (2026-07-01, M Pricing)

**מתי:** מנוע **משלמים** (למידה: 5–6 cycles **M** משלים ל-BOGO).  
**denom 3** = SKU **עונה** (כאן Battlesheep); **denom 4** = Hammers עולים.

| Cycle | 2 SB% | 3 Hook | 4 Hammers | 5 RDS |
|-------|-------|--------|-----------|-------|
| 1 | 100% | 2 Parasheep | 5 | 2 RDS |
| 2 | 150% | AS | 5 | 3 RDS |
| 3 | 200% | 3 Parasheep | 10 | 3 RDS |
| 4 | 250% | 2 AS | 10 | 3 RDS |
| 5 | 300% | 3 Parasheep | 12 | 3 RDS |
| 6 | 300% | 3 AS | 15 | 3 RDS |

כל cycle: **Pay** = Coins + Gems + 1 RDS + 1 GGS · **denom 6** = 1 GGS.

**תבנית טקסט (להעתקה ל-Description):**

```
Rolling — Buy X Get Y (6 cycles) | M Pricing
Cycle 1: 1 Pay — Coins + Gems + 1 RDS + 1 GGS | 2 100% SB | 3 2 Parasheep | 4 5 Hammers | 5 2 RDS | 6 1 GGS
Cycle 2: 1 Pay — … | 2 150% SB | 3 AS | 4 5 Hammers | 5 3 RDS | 6 1 GGS
Cycle 3: 1 Pay — … | 2 200% SB | 3 3 Parasheep | 4 10 Hammers | 5 3 RDS | 6 1 GGS
Cycle 4: 1 Pay — … | 2 250% SB | 3 2 AS | 4 10 Hammers | 5 3 RDS | 6 1 GGS
Cycle 5: 1 Pay — … | 2 300% SB | 3 3 Parasheep | 4 12 Hammers | 5 3 RDS | 6 1 GGS
Cycle 6: 1 Pay — … | 2 300% SB | 3 3 AS | 4 15 Hammers | 5 3 RDS | 6 1 GGS
```

**החלפת עונה:** ביום **SNL** — denom 3 = Dice / Multiwheel / Shield (כפולות 2/3 ל-Dice); ביום **Blast** — Superboom / PAB; וכו' (`offer_construction.md` §SKU עונתי).

---

## BXGY — וריאציות נוספות (שמות במאנדיי)

| וריאציה | cycles | הערה |
|---------|--------|------|
| Buy 1 Get 8 | 1 | 1 Pay + **8** free denoms (לא שלד 6 ל-cycle) |
| 2 cycles | 2 | אותו שלד 6 denoms × 2 |
| Supersized (שם בלבד) | 5 | תבנית supersized למעלה |
| 6 cycles + **Wilds on the bar** | 5–6 | Wildים על **בר התקדמות** + cycles; לעיתים **חלון שעות** |
| Rolling Pay with gems | 2–4 | Pay ב-**ג׳מים** / PAB / Superboom — אותו רעיון Pay→Free |
| Night plan / until 00:00 | 6 | אותו תוכן, **טווח זמן** על הבורד |

**ביצועים (למידה):** Supersized = לרוב **חלש/יקר** יחסית; **5–6 cycles M** = חזק למשלמים. BMFL = מנצח ב-VFM אחרי cooldown (`promo_revenue_analysis` / `learnings.md`).

---

## BMFL — 3 cycles (תזכורת קצרה)

- **3 denoms מדורגים**, כל denom = **הכל ביחד** בשורה אחת (לא Pay+Free נפרדים).
- דוגמת אוג׳ 2026 (בילדר):

```
Cycle 1: Coins (low) + Gems | 100% SB | 3★ Reg | 2 Hammers | 3 RDS | 1 GGS
Cycle 2: Coins (mid)  + Gems | 200% SB | 4★ Reg | 4 Hammers | 3 RDS | 1 GGS
Cycle 3: Coins (high) + Gems | 300% SB | 5★ Reg | 6 Hammers | 3 RDS | 2 GGS
```

- עד **1/שבוע**, cooldown ~10 ימים, **לא** ביום sale, **לא** בשני — ראה `constraints.md`.

---

## Extreme Stamp day + Rolling (HARD — Itay Jul 2026)

When **Extreme Stamp** (incl. **X2 Extreme Stamp**) runs the same calendar day as a **Rolling offer**, stamp slots follow this **per-cycle** logic. GGS, % SB, Hammers, hooks, cards — unchanged unless another rule applies.

### Buy X Get Y (BXGY — 6 denoms per cycle)

| Cycle | Denom 1 (Pay) | Denom 5 (extra stamps) | Denoms 2–4, 6 |
|-------|----------------|-------------------------|---------------|
| **1** | **As usual:** Coins + Gems + **1 RDS** + 1 GGS | **As usual:** **2 RDS** (or template amount; often **3 RDS** from cycle 2 upward on non-extreme days) | Unchanged |
| **2+** | Coins + Gems + **1 Extreme Stamp** + 1 GGS (replaces **1 RDS** on pay) | **1 Extreme Stamp** (replaces **2 RDS** or **3 RDS** on that step) | Unchanged |

- **Do not** leave RDS on pay or on denom 5 from cycle 2 onward on Extreme days.
- **Reference (Monday ops):** `Rolling Offer 6 Cycles | M Pricing | Extreme Stamp` — 2026-06-19 (`12278175352`); cycle 1 keeps RDS on denom 5; cycles 2–6 use Extreme on pay + denom 5.
- **Builder / legacy JSON** that uses “Pay without stamps + Free1=1 RDS + Free2=3 RDS” is **not** this skeleton — write Monday Description from **this section** and `rolling_offer.md` BXGY tables.

### Buy More for Less (BMFL — 3 cycles, one bundle per cycle)

| Cycle | Stamp line in cycle row |
|-------|-------------------------|
| **1** | **Unchanged** vs non-extreme day (RDS + GGS as planned) |
| **2–3** | Replace **all RDS** in that cycle row with **Extreme Stamp(s)** using **4 RDS → 2 Extreme** for the RDS total in that row (e.g. **3 RDS → 2 Extreme Stamps**, **4 RDS → 2 Extreme Stamps**). GGS counts stay as planned. |

**Example (Extreme day, H pricing):**

```
Cycle 1: Coins (low) + Gems | 100% SB | 3★ Reg | 5 Hammers | 2 RDS | 1 GGS
Cycle 2: Coins (mid) + Gems | 200% SB | 4★ Reg | 7 Hammers | 2 Extreme Stamps | 2 GGS
Cycle 3: Coins (high) + Gems | 300% SB | 5★ Reg | 9 Hammers | 2 Extreme Stamps | 3 GGS
```

Pair with **X2 Extreme Stamp** row same day when calendar marks an Extreme day.

---

## כללי תוכן (חובה בכל Rolling)

1. **Hammers** — רק ב-Rolling (או BMFL) באותו יום; כמויות לפי תמחור (`offer_construction.md`).
2. **קלפים** — רק מבנק השבוע; Wild ≤1 per source.
3. **Extreme Stamp day** — global: RDS → Extreme; 4 RDS → 2 Extreme; **Rolling** also § **Extreme Stamp day + Rolling** above (cycle 1 vs 2+).
4. **מאגר פרסים** — denom 3/4/5/6 יכולים לשאת כל SKU מותר; השלד **6 denoms** קבוע ב-BXGY 5/6.
5. **לא** לסנכרן / לשנות שורות במאנדיי מתוך מסמך זה — רק לכתוב Description נכון כשמבקשים תוכן.

---

## קישורים

| קובץ | תפקיד |
|------|--------|
| `offer_construction.md` | פלטפורמה + מאגר פרסים |
| `lanes.md` | תדירות / תפקיד מסלול |
| `learnings.md` | למידות ביצועים + BMFL ברירת מחדל |
| `scripts/promo_guidelines_catalog.py` | שמות וריאציות לטפסי מנהל |
| `documentation/monday_refs/sm_monday_ref_rolling_offer.md` | היסטוריית בורד (3 חודשים) |
