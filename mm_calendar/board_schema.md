# MM Calendar - חוזה בורד Monday

מסמך זה מתעד את המבנה הטכני של בורד התכנון ב-Monday.com, כדי שהאייג'נט יוכל לקרוא ולכתוב פריטים בבטחה.

## זיהוי הבורד

| בורד | שם | Board ID | תפקיד |
|---|---|---|---|
| **ייצור (המקור ⭐)** | `MM calendar` | **`18388590642`** | **מקור האמת** ללמידה (2600 פריטים). View: https://playtika.monday.com/boards/18388590642 |
| Sandbox | `Duplicate of MM calendar Roy AI test` | `18413621867` | עותק בטוח לבדיקות/כתיבת טסט |

- Workspace: Slotomania (SM). גישה: `scripts/monday_client.py` (טוקן ב-`.cursor/monday.env`, gitignored).
- **למידה/כרייה**: מהבורד האמיתי `18388590642`.
- **כתיבה**: לבורד הייצור רק באישור מפורש; אחרת לבצע ב-sandbox.
- שני הבורדים חולקים אותו מבנה עמודות ואותו `group_mky2rn6g` (Days calandar). לבורד האמיתי יש בנוסף עמודות **Creative** (`multiple_person_mm4k7v3z`) ו-**Creative Label** (`color_mm4kygty`).

## קבוצות (Groups)

| Group ID | כותרת | תיאור |
|---|---|---|
| `group_mky2rn6g` | Days calandar | הקבוצה הראשית - עוגני `Day` + כל הפרומואים |
| `topics` | Group Title | ברירת מחדל / שונות |

## עמודות (Columns)

| Column ID | כותרת | סוג | שימוש |
|---|---|---|---|
| `name` | Name | name | שם הפרומו (ראו מוסכמות שמות) |
| `status` | **Product** | status | **המסלול** - ציר השיבוץ המרכזי |
| `color_mky9aesm` | **Pricing** | status | עומק תמחור: High / Max / Mid / Low |
| `date_mky27nx7` | Date | date | תאריך יחיד (פרומו של יום) |
| `timerange_mkz3t5qy` | Date | timeline | טווח תאריכים (פיצ'רים/עונות) |
| `long_text_mkxzgg1v` | Description | long_text | תיאור הפרומו/בריף — **חייב להתאים ל-Name (כותרת)**; אם יש סתירה, מתקנים Description (ולעיתים Pricing) לפי הכותרת, לא להפך |
| `person` | MM | people | מנהל מוניטיזציה אחראי |
| `multiple_person_mky0jahx` | Economiest | people | אחראי כלכלה |
| `color_mky0czxd` | Economy status | status | Comment / Approved / Not approved / No need / Approved day / Event |
| `multiple_person_mm4k7v3z` | Creative | people | אחראי קריאייטיב (בורד ייצור בלבד) |
| `color_mm4kygty` | Creative Label | status | סטטוס קריאייטיב (בורד ייצור בלבד) |
| `color_mkztqb24` | Config Status | status | Config needed / Done / MCP needed / In progress / On Hold |
| `file_mky0y0r3` | Config | file | קובץ קונפיג |
| `timerange_mm0vc5fk` | Config due date | timeline | דדליין קונפיג |
| `multiple_person_mky213as` | Ops | people | אחראי Ops |
| `color_mky2sdgt` | Ops Status | status | Day / Reuse / New |
| `button_mkxzbhb` | Art | button | קישור לבריף ארט |
| `color_mkyfye85` | Add to smart calendar | status | Add |
| `subtasks_mkxzszxd` | Subitems | subtasks | תתי-פריטים |

## תוויות Product (המסלולים)

```
Rolling offer, Short Term, RYD, Daily deal, Buy all, Mid Term, Gems,
Event, Core, SlotoBucks, MGAP, Day, Clan-Dash, Counter PO,
Extreme stamp, Album, Offers & coin sale, Black Diamond, DTC, ADS, Prize Mania
```

> `Day` = עוגן תאריך (פריט שמייצג יום בלוח), לא פרומו. משמש לעיגון וסידור ויזואלי.

## סמנטיקת Pricing

| ערך | משמעות | מתי |
|---|---|---|
| `High` | עומק/אגרסיביות גבוהה | ברירת המחדל לפרומו מתומחר |
| `Max` | המקסימום | רגעי שיא, DD segmented, ימי סייל גדולים |
| `Mid` | בינוני | |
| `Low` | נמוך | נדיר (בעיקר DPU PO) |

## מוסכמות שמות (מתוך פריטים אמיתיים)

- Daily Deal: `DD - <reward> | <P> Pricing`, או מפוצל לחלונות `DD (1) - <reward> 00:00-06:00 UTC`.
- Segmented DD: `DD Segmented - Non Finishers: <reward>` / `Finishers: <reward>`.
- Rolling: `Rolling Offer - <mechanic> | H Price`.
- Mid Term עונות: `Quest Season YYYY-MM-DD`, `Mega Pods YYYY-MM-DD`, `Winovate Season YYYY-MM-DD`, `Globez`, `Figz Season`.
- Short Term: `Blast - <theme>`, `Battlesheep`, `SNL`.
- ADS: `ADS PO - <reward>`.
- Album: `Shiny Show - <variant>`, `Gold Trading Day #N`.
- ביטול: קידומת `Cancelled - ...` בתוך השם (הפריט נשאר).

## דפוסי קריאה/כתיבה בטוחים

### קריאה (pagination)
`items_page(limit:200)` ואז `next_items_page(cursor)` עד ש-cursor הוא null. (כ-2063 פריטים => ~11 דפים.)

### כתיבת פריט חדש (לשלב הבנייה - לא בשלב זה)
1. `create_item(board_id, group_id: "group_mky2rn6g", item_name)`
2. `change_multiple_column_values` - להגדיר `status` (Product), `color_mky9aesm` (Pricing), `date_mky27nx7` או `timerange_mkz3t5qy`, ו-`long_text_mkxzgg1v`.
3. תוויות status חייבות להתאים **בדיוק** לתוויות הקיימות בבורד.

> בשלב הנוכחי (בניית בסיס ידע) אין כתיבה לבורד. הכתיבה תתווסף בשלב בניית הקלנדר בפועל.
