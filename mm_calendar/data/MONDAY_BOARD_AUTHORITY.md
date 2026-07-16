# Monday board — מקור אמת לשיבוץ (read-only)

**הוראת Itay · 12 יולי 2026:** מה שמופיע על בורד **MM calendar** ב-Monday (`18388590642`) הוא **הקובץ המעודכן** לשאלות “מה משובץ”, “מה על הלוח”, “מה ביום X”.  
**אין לשנות כלום ב-Monday** אלא באישור מפורש.

## קבצי snapshot (נמשכים read-only)

| קובץ | תוכן |
|------|------|
| `monday_board_live_snapshot.json` | כל הפריטים (~2957) + meta + Description מלא |
| `monday_board_live_by_date.json` | אותו תוכן מקובץ לפי `date` (כולל `_no_date`) |

עדכון snapshot: הרץ מ-repo root:

```bash
python3 scripts/pull_monday_live_snapshot.py
```

(או pull ידני דרך `monday_client.gql` — רק queries.)

## כללי עבודה לסוכנים

1. **שיבוץ / תאריך / שם שורה על Monday** → קרא מ-`monday_board_live_snapshot.json` (או `…_by_date.json`), לא מ-`august_2026_plan.json`.
2. **`august_2026_plan.json` + builder** → תכנון/וולידציה/דשבורד; יכול **לסטות** מ-Monday אחרי עריכות ידניות.
3. **שורה בלי עמודת Date** → לא “יום בלוח”; השם עלול עדיין להכיל `2026-08-XX` — אל תספור כשיבוץ יומי.
4. **Product = `Day`** → עוגן יום, לא פרומו.
5. **Monday לא נוגע** — אין upload/sync/mutations בלי בקשה מפורשת.

## meta אחרון

ראה `meta.pulled_at_utc` ו-`meta.item_count` בתוך `monday_board_live_snapshot.json`.
