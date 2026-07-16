# גישת קריאה בלבד למחלקה — `slotomania-mm-calendar`

Repo: **https://github.com/ppuregoldz-arch/slotomania-mm-calendar**

ב-GitHub **אין** מצב כמו Google Drive של «לינק לצפייה בלבד» על repo **פרטי** בלי להזמין משתמשים. יש שתי דרכים עיקריות:

---

## אופציה 1 — לינק אחד לכולם (בלי הזמנה per user)

**Repository → Public (ציבורי)**

| מי | צפייה / Clone | עריכה / Push |
|----|----------------|--------------|
| כל מי שיש לו את הלינק | כן | **לא** (אלא אם תוסיף Write) |
| אתה (בעלים) | כן | כן |

**שלבים:**

1. היכנס ל-repo → **Settings** → **General**
2. **Danger zone** → **Change repository visibility** → **Make public**
3. שלח למחלקה:  
   `https://github.com/ppuregoldz-arch/slotomania-mm-calendar`

**חשוב:** Public = גלוי גם מחוץ ל-Playtika (אינטרנט). אם יש ב-repo מידע רגיש פנימי — **לא** מתאים. העדף אופציה 2.

**להקשיח (עדיין Public):**

- **Settings → General:** כבה Wiki אם לא צריך
- **Settings → Collaborators:** אל תוסיף Write למי שלא חייב לערוך
- אופציונלי: **Settings → Branches → Branch protection** על `main` (רק אתה דוחף / דרך PR)

---

## אופציה 2 — פרטי, רק Slotomania (מומלץ לתוכן פנימי)

**Repository נשאר Private**

כל עובד צריך **חשבון GitHub** (עדיף ארגוני Playtika אם קיים). אתה מזמין עם הרשאה **Read** בלבד.

**שלבים:**

1. Repo → **Settings** → **Collaborators** (או **Manage access**)
2. **Add people** (או **Add teams** אם ה-repo תחת Organization)
3. בחר משתמש / צוות → Role: **Read** (לא Write / Maintain / Admin)
4. שלח להם את **אותו לינק** — אחרי שאישרו את ההזמנה במייל, יוכלו לצפות ו-clone; **לא** יוכלו לדחוף קוד

**Read =** browse, clone, download ZIP, פתיחה ב-Cursor — **בלי** push ל-`main`.

אם המחלקה על **GitHub Organization** (למשל `playtika`):

- העבר/שכפל את ה-repo לארגון (או צור org repo חדש)
- **Settings → Manage access → Add teams** → צוות MM/CRM → **Read**

---

## מה לשלוח במיil / Teams

```
נושא: MM Calendar — קריאה בלבד (GitHub)

היי,
הקוד והידע של MM Calendar (אוגוסט 2026, builders, guidelines):

https://github.com/ppuregoldz-arch/slotomania-mm-calendar

• צפייה ו-clone — כן
• עריכה ב-GitHub / push — לא (קריאה בלבד)

Clone:
git clone https://github.com/ppuregoldz-arch/slotomania-mm-calendar.git

ב-Cursor: File → Open Folder → תיקיית ה-clone
```

(אם Private — הוסף: «תקבלו הזמנה מ-GitHub לאישור».)

---

## טוקן push (רק אצלך)

נשמר **מקומית** ב-`.cursor/github.env` (לא עולה ל-GitHub). Push:

```bash
cd "/Users/itayg/Desktop/Cursor Work"
python3 scripts/github_push_origin.py
```

אל תשתף את הקובץ הזה עם המחלקה.

---

## סיכום החלטה

| צורך | בחירה |
|------|--------|
| לינק אחד, בלי חשבון GitHub | **Public** |
| פנימי Playtika בלבד | **Private + Read** לכל משתמש / צוות |
| אתה היחיד שדוחף עדכונים | Read לכולם; Write רק לך |
