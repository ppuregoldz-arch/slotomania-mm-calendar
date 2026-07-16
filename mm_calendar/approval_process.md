# MM Calendar - תהליך אישורים (Approvals)

> בניית קלנדר כוללת תהליך אישורים מובנה. **אישורי חודש N מתקיימים בחודש N-1** (בערך ימים 5-17), ברצף של 6 תחנות עם חלונות זמן.
> ⚠️ **אין לתאם אישורים בשישי/שבת** (weekend). רק ימים א'-ה'.

## רצף התחנות (6)
1. **TL Approval H1 & H2** - אישור Team Lead לשני חצאי החודש (פותח את התהליך).
2. **Economy Approval part 1** - אישור כלכלה, חלק 1.
3. **Creative Approvals** - אישורי קריאייטיב.
4. **Economy Approval part 2** - אישור כלכלה, חלק 2.
5. **Operations Approvals** - אישורי Ops.
6. **Final Presentation** - הצגה סופית (סוגר את התהליך).

- מרווח ~יומיים בין תחנות; מדלגים על שישי/שבת.
- הכלכלה מאשרת ב**שני שלבים** (part 1 מוקדם, part 2 אחרי הקריאייטיב).

## דוגמה: אישורי קלנדר יוני (התקיימו במאי 2026)
| # | תחנה | תאריך |
|---|---|---|
| 1 | TL Approval H1 & H2 | 05/05 |
| 2 | Economy Approval part 1 | 07/05 |
| 3 | Creative Approvals | 09/05 |
| 4 | Economy Approval part 2 | 11/05 |
| 5 | Operations Approvals | 12/05 |
| 6 | Final Presentation | 14/05 |

## אישורי קלנדר יולי (מתקיימים ביוני 2026, ללא שישי/שבת)
| # | תחנה | תאריך | יום |
|---|---|---|---|
| 1 | TL Approval H1 & H2 | 07/06 | Sun |
| 2 | Economy Approval part 1 | 09/06 | Tue |
| 3 | Creative Approvals | 11/06 | Thu |
| 4 | Economy Approval part 2 | 14/06 | Sun |
| 5 | Operations Approvals | 15/06 | Mon |
| 6 | Final Presentation | 17/06 | Wed |

## הצגה בקנבס
טאב **"אישורים"** נפרד בקנבס `july-2026-calendar.canvas.tsx` (מפריד את לוח האישורים מלוח הפרומואים).

---
**עודכן:** יולי 2026.
