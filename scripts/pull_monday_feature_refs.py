#!/usr/bin/env python3
"""Pull MM calendar Monday board (last 3 months) and write per-feature reference markdown."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from monday_client import gql  # noqa: E402

BOARD_ID = 18388590642
BOARD_URL = f"https://playtika.monday.com/boards/{BOARD_ID}"
OUT_DIR = REPO / "mm_calendar" / "documentation" / "monday_refs"
CACHE_PATH = REPO / "mm_calendar" / "data" / "monday_pull_last_3mo.json"

COLS = [
    "status",
    "date_mky27nx7",
    "timerange_mkz3t5qy",
    "long_text_mkxzgg1v",
    "color_mky9aesm",
]

Q_FIRST = """
query ($board: [ID!], $cols: [String!]) {
  boards(ids: $board) {
    items_page(limit: 500) {
      cursor
      items {
        id
        name
        column_values(ids: $cols) { id text }
      }
    }
  }
}
"""
Q_NEXT = """
query ($cursor: String!, $cols: [String!]) {
  next_items_page(cursor: $cursor, limit: 500) {
    cursor
    items {
      id
      name
      column_values(ids: $cols) { id text }
    }
  }
}
"""

FEATURES = (
    "Blast",
    "Battlesheep",
    "SNL",
    "Daily Deal",
    "Prize Mania",
    "Rolling Offer",
    "ADS PO",
    "Core",
    "Time Limited Promotions",
    "Winovate",
    "Mega Pods",
    "Golden Spin",
    "Lotto Bonus & L.B.P",
    "Buy All",
    "Reveal Your Deal",
    "Album",
)

SKU_PATTERNS: tuple[tuple[str, str], ...] = (
    ("Regular card", r"\d\s*★\s*reg|\d\*?\s*reg\b|regular card"),
    ("Gold card", r"\d\s*★\s*gold|\d\*?\s*gold\b|gold card|gold pack"),
    ("Ace card", r"\d\s*★\s*ace|ace card|wild ace"),
    ("Shiny card", r"shiny"),
    ("Wild Ordinary", r"wild ordinary"),
    ("Wild Gold", r"wild gold"),
    ("Wild Any", r"wild any"),
    ("Wild Supreme", r"wild supreme"),
    ("Hammers", r"\d+\s*hammers?|\bhammers?\b"),
    ("Picks (Blast)", r"\d+\s*picks?|\bpicks?\b"),
    ("PAB / Parasheep", r"\bpab\b|parasheep|para ?sheep"),
    ("Airstrike / AS", r"\bas\b|airstrike|air strike"),
    ("Quest Booster", r"quest booster"),
    ("Hero Coins", r"hero coins"),
    ("Dice Booster", r"dice booster"),
    ("SNL Dice", r"snl dice"),
    ("Multiwheel", r"multiwheel"),
    ("Superboom", r"superboom|super boom"),
    ("Clan Pack", r"clan pack"),
    ("SB / % SlotoBucks", r"\d+%\s*sb|sloto\s*bucks|slotobucks"),
    ("RDS", r"\brds\b|rolling deal stamp|deal stamp"),
    ("GGS", r"\bggs\b|gold gem stamp"),
    ("Extreme Stamp", r"extreme stamp"),
    ("Coins + Gems (bundle)", r"coins.*gems|gems.*coins"),
    ("Gems", r"\bgems\b"),
    ("Shield", r"shield"),
    ("Globez", r"globez"),
    ("Figz", r"figz"),
)


def cv(item: dict, cid: str) -> str:
    for c in item.get("column_values") or []:
        if c["id"] == cid:
            return (c.get("text") or "").strip()
    return ""


def pull_all_items() -> list[dict]:
    data = gql(Q_FIRST, {"board": [BOARD_ID], "cols": COLS})
    page = data["boards"][0]["items_page"]
    items = list(page["items"])
    cursor = page.get("cursor")
    while cursor:
        d = gql(Q_NEXT, {"cursor": cursor, "cols": COLS})
        page = d["next_items_page"]
        items.extend(page["items"])
        cursor = page.get("cursor")
    rows = []
    for it in items:
        rows.append(
            {
                "id": it["id"],
                "name": (it.get("name") or "").strip(),
                "product": cv(it, "status"),
                "date": cv(it, "date_mky27nx7"),
                "timeline": cv(it, "timerange_mkz3t5qy"),
                "description": cv(it, "long_text_mkxzgg1v"),
                "pricing": cv(it, "color_mky9aesm"),
            }
        )
    return rows


def parse_timeline(tl: str) -> tuple[date | None, date | None]:
    if not tl:
        return None, None
    parts = re.split(r"\s*-\s*", tl.strip())
    out: list[date] = []
    for p in parts[:2]:
        p = p.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", p):
            try:
                out.append(date.fromisoformat(p))
            except ValueError:
                pass
    if not out:
        return None, None
    if len(out) == 1:
        return out[0], out[0]
    return out[0], out[1]


def row_overlaps_window(row: dict, start: date, end: date) -> bool:
    iso = row.get("date") or ""
    if re.match(r"^\d{4}-\d{2}-\d{2}$", iso):
        try:
            d = date.fromisoformat(iso)
            if start <= d <= end:
                row["iso"] = iso
                return True
        except ValueError:
            pass
    t0, t1 = parse_timeline(row.get("timeline") or "")
    if t0 and t1:
        if t1 < start or t0 > end:
            return False
        row["iso"] = t0.isoformat() if t0 >= start else start.isoformat()
        row["iso_end"] = t1.isoformat()
        return True
    return False


def cancelled(name: str) -> bool:
    return name.lower().startswith("cancelled")


def classify(row: dict) -> set[str]:
    name = row["name"]
    nl = name.lower()
    prod = (row.get("product") or "").lower()
    desc = (row.get("description") or "").lower()
    text = f"{nl} {desc}"
    tags: set[str] = set()

    if cancelled(name) or prod == "day":
        return tags

    if prod == "daily deal" or re.search(r"\bdd\b|daily deal", nl):
        tags.add("Daily Deal")
    if prod == "prize mania" or "prize mania" in nl:
        tags.add("Prize Mania")
    if prod == "rolling offer" or ("rolling" in nl and "rolling offer" not in prod):
        tags.add("Rolling Offer")
    if prod == "ads" or nl.startswith("ads po"):
        tags.add("ADS PO")
    if prod == "core" or any(
        k in nl
        for k in (
            "win master",
            "pick your path",
            " pyp",
            "spin zone",
            "ace heist",
            "spinner clash",
            "custom pod",
            " m.e.s",
            " mes ",
            "mega winner",
            "jackpot",
        )
    ):
        tags.add("Core")
    if prod == "buy all" or "buy all" in nl or "mystery buy" in nl:
        tags.add("Buy All")
    if prod == "ryd" or "reveal your deal" in nl or re.search(r"\bryd\b", nl):
        tags.add("Reveal Your Deal")
    if prod == "album" or "shiny show" in nl or "gold trading" in nl or "album" in nl:
        tags.add("Album")
    if "golden spin" in nl:
        tags.add("Golden Spin")
    if "lotto" in nl or "lbp" in nl or "lotto bonus" in text:
        tags.add("Lotto Bonus & L.B.P")
    if "winovate" in nl:
        tags.add("Winovate")
    if "mega pods" in nl or "mega pod" in nl:
        tags.add("Mega Pods")

    if prod == "short term" or prod == "mid term" or "short term" in nl or "mid term" in nl:
        if "blast" in nl or "blast" in desc:
            tags.add("Blast")
        if "battlesheep" in nl or "battlesheep" in desc:
            tags.add("Battlesheep")
        if re.search(r"\bsnl\b", nl) or re.search(r"\bsnl\b", desc):
            tags.add("SNL")

    # Time limited
    if (
        "time limited" in nl
        or prod == "counter po"
        or "counter po" in nl
        or "piggy" in nl
        or prod == "mgap"
        or "mgap" in nl
        or "happy hour" in nl
        or "jumbo giveaway" in nl
        or "fortune dip" in nl
        or "dice deluxe" in nl
        or "boosted gemback" in nl
        or re.search(r"x2 ggs", nl)
        or re.search(r"\d{1,2}:\d{2}\s*utc", nl)
        or re.search(r"\d+\s*h(?:ours?)?\b", nl)
    ):
        tags.add("Time Limited Promotions")

    return tags


def dedupe_key(row: dict) -> str:
    return re.sub(r"\s+", " ", row["name"].lower()).strip()


def extract_skus(text: str) -> set[str]:
    t = text.lower()
    found: set[str] = set()
    for label, rgx in SKU_PATTERNS:
        if re.search(rgx, t, re.I):
            found.add(label)
    return found


def write_feature_doc(feature: str, rows: list[dict], start: date, end: date) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", feature.lower()).strip("_")
    path = OUT_DIR / f"sm_monday_ref_{slug}.md"

    by_name: dict[str, dict] = {}
    for r in sorted(rows, key=lambda x: (x.get("iso") or "", x["name"])):
        k = dedupe_key(r)
        if k not in by_name:
            by_name[k] = r

    lines = [
        f"# Monday reference — {feature}",
        "",
        f"**Source:** [MM calendar board]({BOARD_URL}) (`{BOARD_ID}`) · **read-only pull**",
        f"**Window:** {start.isoformat()} → {end.isoformat()} (last 3 calendar months)",
        f"**Generated:** {date.today().isoformat()}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Distinct promo titles | {len(by_name)} |",
        f"| Row instances in window | {len(rows)} |",
        "",
        "## Distinct promotions (deduped by title)",
        "",
        "| Dates (sample) | Product | Pricing | Monday row | Link |",
        "|----------------|---------|---------|------------|------|",
    ]
    for r in by_name.values():
        iso = r.get("iso") or "—"
        link = f"{BOARD_URL}/pulses/{r['id']}"
        name_esc = r["name"].replace("|", "\\|")
        lines.append(
            f"| {iso} | {r.get('product') or '—'} | {r.get('pricing') or '—'} | {name_esc} | [open]({link}) |"
        )

    lines.extend(["", "## All instances (chronological)", ""])
    for r in sorted(rows, key=lambda x: (x.get("iso") or "9999", x["name"])):
        iso = r.get("iso") or "—"
        link = f"{BOARD_URL}/pulses/{r['id']}"
        lines.append(f"- **{iso}** — [{r['name']}]({link}) · _{r.get('product') or ''}_")
        if r.get("description"):
            snippet = r["description"].replace("\n", " ")[:200]
            lines.append(f"  - {snippet}…" if len(r["description"]) > 200 else f"  - {snippet}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sku_catalog(all_rows: list[dict], sku_counts: dict[str, int]) -> None:
    path = OUT_DIR / "sm_monday_rewards_skus.md"
    canonical = [
        ("Coins / Gems", "Base currencies in offer slots"),
        ("RDS (Red Diamond Stamp)", "Rolling stamp; → Extreme Stamp on Extreme days"),
        ("GGS (Gold Gem Stamp)", "Gem-path stamp"),
        ("% SlotoBucks", "100 / 150 / 200 / 300 / 500%+ (not 155% legacy)"),
        ("Extreme Stamp / Superboom", "Amplifiers / burst prizes"),
        ("Hammers", "Single hammer source per day across products"),
        ("Picks", "Blast picks"),
        ("PAB / Parasheep", "Battlesheep seasonal SKU"),
        ("Airstrike (AS)", "Battlesheep seasonal SKU"),
        ("Dice Booster", "6h / 12h / 24h"),
        ("SNL Dice / Multiwheel / Shield", "SNL seasonal SKUs (dice often ×2 or ×3)"),
        ("Quest Booster", "Quest Mid-Term season"),
        ("3000 Hero Coins", "Globez / Figz Mid-Term prize"),
        ("Reg / Ace / Gold / Wild / Shiny cards", "From weekly card bank; album-last-week → Wild purchase only"),
        ("Free Spins / Ace Spins", "Machine / event hooks"),
        ("Clan Pack", "Clan-Dash rewards"),
    ]
    lines = [
        "# Rewards / SKUs — Monday observations + canonical pool",
        "",
        f"**Monday pull:** board `{BOARD_ID}` · window last ~3 months · {date.today().isoformat()}",
        "",
        "## Canonical reward pool (what we *can* give — `mm_calendar/offer_construction.md`)",
        "",
        "| SKU family | Notes |",
        "|------------|-------|",
    ]
    for fam, note in canonical:
        lines.append(f"| {fam} | {note} |")
    lines.extend(
        [
            "",
            "## Observed on Monday (keyword scan of names + descriptions)",
            "",
            "| SKU / reward family | # rows mentioning (approx) |",
            "|-------------------|---------------------------|",
        ]
    )
    for label, n in sorted(sku_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {label} | {n} |")
    lines.extend(["", "## Raw mentions (top examples per SKU)", ""])
    examples: dict[str, list[str]] = defaultdict(list)
    for r in all_rows:
        blob = f"{r['name']} {r.get('description') or ''}"
        for label in extract_skus(blob):
            if len(examples[label]) < 5 and r["name"] not in examples[label]:
                examples[label].append(r["name"])
    for label in sorted(examples.keys()):
        lines.append(f"### {label}")
        for ex in examples[label]:
            lines.append(f"- {ex}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    end = date.today()
    start = end - timedelta(days=92)  # ~3 months
    print(f"Pulling Monday board {BOARD_ID} …")
    items = pull_all_items()
    print(f"Total items on board: {len(items)}")

    filtered: list[dict] = []
    for row in items:
        if cancelled(row["name"]):
            continue
        if (row.get("product") or "").strip() == "Day":
            continue
        if not row_overlaps_window(row, start, end):
            continue
        filtered.append(row)

    print(f"Items in date window: {len(filtered)}")

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(
            {"pulled": date.today().isoformat(), "start": start.isoformat(), "end": end.isoformat(), "items": filtered},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    by_feature: dict[str, list[dict]] = {f: [] for f in FEATURES}
    unclassified: list[dict] = []
    sku_counts: dict[str, int] = defaultdict(int)

    for row in filtered:
        tags = classify(row)
        blob = f"{row['name']} {row.get('description') or ''}"
        for sku in extract_skus(blob):
            sku_counts[sku] += 1
        if not tags:
            unclassified.append(row)
            continue
        for t in tags:
            if t in by_feature:
                by_feature[t].append(row)

    for feature in FEATURES:
        write_feature_doc(feature, by_feature[feature], start, end)
        print(f"  {feature}: {len(by_feature[feature])} instances")

    write_sku_catalog(filtered, sku_counts)
    print(f"Wrote docs under {OUT_DIR}")

    if unclassified:
        misc = OUT_DIR / "sm_monday_ref_unclassified.md"
        lines = ["# Unclassified rows (last 3 months)", ""]
        for r in sorted(unclassified, key=lambda x: (x.get("iso") or "", x["name"]))[:200]:
            lines.append(f"- {r.get('iso')} — {r['name']} ({r.get('product')})")
        misc.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  Unclassified: {len(unclassified)} (see sm_monday_ref_unclassified.md)")


if __name__ == "__main__":
    main()
