# 03 — Rolling Offer

## שתי משפחות (אל תערבב)

| משפחה | Cycles | מבנה |
|--------|--------|------|
| **BXGY** | 1 / 2 / **5** / **6** | כל cycle: **6 denoms** (ראה למטה) |
| **BMFL** | **3** | 3 denoms — bundle מלא בכל cycle; **High**; ימי MFL בלבד |

## BXGY — שלד קנוני (5 / 6 cycles)

| Denom | תוכן |
|-------|------|
| 1 Pay | Coins + Gems + **1 RDS + 1 GGS** |
| 2 | % SB (עולה במחזורים) |
| 3 | Hook: supersized % / Picks / קלף / **SKU עונה** |
| 4 | Hammers (מקור יחיד ליום) |
| 5 | 2–3 RDS |
| 6 | 1 GGS |

⛔ לא מודל Pay בלי חותמות + Free1=1RDS/Free2=3RDS (עזר ישן בבילדר).

## תבניות מוכנות
- **5-cycle Supersized:** `rolling_offer.md` §5-cycle
- **6-cycle עונתי (7/1):** `rolling_offer.md` §6-cycle (Parasheep/AS)
- **BMFL 3-cycle:** `rolling_offer.md` §BMFL · `learnings.md` §BMFL אוגוסט

## מה אפשר לשבץ
- BXGY: SB מדורג, supersized, Picks, Parasheep/AS/SNL Dice, Reg/Gold ב-hook (לבנק)
- BMFL: %SB 100/200/300 + Reg מדורג + Hammers + RDS/GGS בשורה אחת
- וריאציות: Buy 1 Get 8 · bar+Wild · Pay with gems · Night plan

## ביצועים
- **BMFL** עבר gate מוגבל לכיוון רבניו ב-backtest; עדיין correlation עם טווח שגיאה רחב.
- **Supersized** חלש יותר ב-product proxy קטן; לא מסקנה סיבתית.
- cooldown ~10 ימים, 1/שבוע מקס' נשאר כלל תפעולי.

## דוגמאות
- **קנוני:** `../rolling_offer.md`
- בורד: `documentation/monday_refs/sm_monday_ref_rolling_offer.md`
- קטלוג שמות: `scripts/promo_guidelines_catalog.py` §BXGY/BMFL

## קרא עומק
`../rolling_offer.md` · `offer_construction.md` §Rolling · `lanes.md` §Rolling

## ביצועים קנוניים
`../../performance/README.md` → משפחת `rolling-offer` · `../../prediction/BACKTEST_RESULTS.md`
