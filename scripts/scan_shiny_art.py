#!/usr/bin/env python3
"""Classify Shiny Show in-app art folders (themed vs generic) from a list of
inapp png paths (produced by `find ... -iname '*inapp*.png'`).

Input:  /tmp/shiny_inapp.txt  (one path per line, relative to The_Shiny_Show)
Output: writes mm_calendar/art_inventory.md and prints a summary.
"""
from __future__ import annotations
import os, re, collections

SRC = "/tmp/shiny_inapp.txt"
OUT = "/Users/itayg/Desktop/Cursor Work/mm_calendar/art_inventory.md"

# theme keyword -> canonical label (checked in order)
THEMES = [
    (r"new[_ ]?year|_ny_|_ny\.", "New Year"),
    (r"valentine", "Valentine's Day"),
    (r"chinese|chinaney|chineseny", "Chinese New Year"),
    (r"st[_ ]?patrick|patricks", "St. Patrick's"),
    (r"cinco", "Cinco de Mayo"),
    (r"super[_ ]?bowl", "Super Bowl"),
    (r"world[_ ]?cup", "World Cup"),
    (r"4th_of_july|4_of_july|of_july|fourth", "4th of July"),
    (r"lucy|carnival", "Lucy's Carnivale"),
    (r"bday|birthday", "Birthday"),
    (r"easter", "Easter"),
    (r"halloween", "Halloween"),
    (r"christmas|xmas|santa", "Christmas"),
    (r"labor", "Labor Day"),
    (r"back[_ ]?to[_ ]?school", "Back to School"),
    (r"spring", "Spring"),
    (r"summer", "Summer"),
    (r"betty", "Betty Boop (branded)"),
    (r"thanksgiving", "Thanksgiving"),
    (r"black[_ ]?friday", "Black Friday"),
]


def classify(path: str):
    p = path.lower()
    for rgx, label in THEMES:
        if re.search(rgx, p):
            return "themed", label
    return "generic", ""


def folder_of(path: str) -> str:
    # promo folder = first path component after the year/Joker root
    parts = path.split("/")
    # paths look like: 2026/2026_05_05_CincoDeMayo/....png  OR Joker Promotions/<promo>/..
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return path


def main():
    lines = [l.strip() for l in open(SRC) if l.strip()]
    folders = collections.OrderedDict()
    for path in lines:
        f = folder_of(path)
        folders.setdefault(f, []).append(os.path.basename(path))

    rows = []
    for folder, files in folders.items():
        kind, theme = classify(folder + " " + " ".join(files))
        rows.append((folder, kind, theme, len(files)))

    themed = [r for r in rows if r[1] == "themed"]
    generic = [r for r in rows if r[1] == "generic"]
    theme_counts = collections.Counter(r[2] for r in themed)

    with open(OUT, "w") as o:
        o.write("# MM Calendar - אינוונטר ארטים מוכנים (Shiny Show In-App)\n\n")
        o.write("> נסרק אוטומטית מ-CRM3: `The_Shiny_Show/{2025,2026,Joker Promotions}`.\n")
        o.write("> מקור: `scripts/scan_shiny_art.py` (ניתן להרצה חוזרת). ספירה ברמת תיקיית-פרומו (כל תיקיה = פרומו עם Inapp art מוכן).\n\n")
        o.write("## סיכום\n\n")
        o.write(f"- סך פרומואים עם Inapp art מוכן: **{len(rows)}**\n")
        o.write(f"- **Generic** (מכניקה, ניתן לשימוש חוזר בכל זמן): **{len(generic)}**\n")
        o.write(f"- **Themed** (קשור לאירוע/חג/מותג): **{len(themed)}**\n\n")
        o.write("### פירוק themed לפי תמה\n\n| תמה | פרומואים מוכנים |\n|---|---|\n")
        for t, c in theme_counts.most_common():
            o.write(f"| {t} | {c} |\n")
        o.write("\n## איך האייג'נט משתמש בזה\n\n")
        o.write("- כשמשבצים Shiny Show ביום ללא אירוע -> להעדיף ארט **Generic** מוכן (reuse, ללא עלות ארט).\n")
        o.write("- כשיש אירוע/חג -> לבדוק אם יש ארט **Themed** מוכן לאותה תמה לפני הזמנת ארט חדש.\n")
        o.write("- שמות התיקיות מקודדים `YYYY_MM_DD_<תיאור>` - התאריך = מתי שומש לאחרונה.\n\n")
        for title, data in (("Themed", themed), ("Generic", generic)):
            o.write(f"## פרומואים {title}\n\n| תיקיה (פרומו) | תמה | קבצי Inapp |\n|---|---|---|\n")
            for folder, kind, theme, n in sorted(data):
                o.write(f"| {folder} | {theme or '-'} | {n} |\n")
            o.write("\n")

    print(f"folders={len(rows)} themed={len(themed)} generic={len(generic)}")
    print("themes:", dict(theme_counts.most_common()))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
