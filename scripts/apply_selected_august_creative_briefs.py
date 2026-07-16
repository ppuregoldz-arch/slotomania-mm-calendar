#!/usr/bin/env python3
"""Create concise Monetization-Art briefs for selected approved August dates."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "mm_calendar" / "data" / "monday_board_live_by_date.json"
ART_CACHE = ROOT / "mm_calendar" / "data" / "monetization_art_board_full.json"
BOARD = "18112190666"
SUBITEM_BOARD = "18112200937"

sys.path.insert(0, str(ROOT / "scripts"))
from monday_client import gql  # noqa: E402


SOURCE_BY_FAMILY = {
    "ads": "10860770073",
    "clan": "12464700711",
    "spinner clash": "12448958742",
    "daily deal": "12464772873",
    "mgap": "12466613934",
    "piggy": "12448968305",
    "rolling": "12036503175",
    "spin zone": "12097033909",
    "gems sale": "11850575803",
    "rlap": "12049563283",
    "golden spin": "12299965527",
    "prize mania": "12448382886",
    "battlesheep": "11009518880",
    "shiny show": "11850563784",
    "ace heist": "11619181740",
    "lbp": "12367526035",
    "extreme": "12309916897",
    "snl": "10968800690",
    "gems coupon": "11621408835",
    "stickers sources": "11913837798",
    "dice deluxe": "11890715396",
    "ryd": "11727887975",
    "globez": "11360876494",
    "winovate": "12407252858",
}

SOURCE_OVERRIDES = {
    "12510879320": "11513974436",  # Rolling Supersized
    "12464188536": "12093534228",  # MGAP BOGO
    "12464219580": "11850552580",  # Clan Go 200 badges
    "12464261622": "10933889405",  # ADS Gems
    "12464289413": "11850582717",  # X2 Dash Points
    "12464437476": "11327499360",  # Dash picker
    "12464175520": "12367526035",  # Extreme Stamp on LBP
    "12464563980": "10770996717",  # Two multiballs
    "12511214687": "12148706201",  # Generic bigger multipliers
    "12475750417": "12337043899",  # DD SB wheel structure
    "12475732350": "11223800692",  # DD wheel structure
    "12475100661": "11868921934",  # Generic MES Ace Heist structure
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", action="append", required=True, help="YYYY-MM-DD")
    parser.add_argument("--commit", action="store_true", help="Write to Monday")
    return parser.parse_args()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def table(rows: list[tuple[str, str]]) -> str:
    return "<table><tbody>" + "".join(
        f"<tr><td><p><strong>{esc(key)}</strong></p></td><td><p>{value}</p></td></tr>"
        for key, value in rows
    ) + "</tbody></table>"


def normalize_name(value: str) -> str:
    value = re.sub(r"^\d{4}-\d{2}-\d{2}\s*\|\s*", "", value).strip()
    return re.sub(r"\s+", " ", value.replace("—", "-").replace("–", "-"))


def slug(value: str) -> str:
    value = normalize_name(value)
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", value)).strip("_")[:80]


def family(value: str) -> str:
    text = value.lower()
    rules = [
        ("ads", ("ads po", "po ads")),
        ("daily deal", ("daily deal",)),
        ("rolling", ("rolling",)),
        ("mgap", ("mgap",)),
        ("rlap", ("rlap", "stash booster")),
        ("piggy", ("piggy",)),
        ("spinner clash", ("spinner clash",)),
        ("spin zone", ("spin zone",)),
        ("gems sale", ("gems sale",)),
        ("gems coupon", ("gems coupon", "gem coupon")),
        ("golden spin", ("golden spin",)),
        ("prize mania", ("prize mania",)),
        ("battlesheep", ("battlesheep",)),
        ("shiny show", ("shiny show",)),
        ("ace heist", ("ace heist",)),
        ("lbp", ("lbp",)),
        ("extreme", ("x2 extreme",)),
        ("snl", ("snl",)),
        ("stickers sources", ("sticker sources", "stickers sources")),
        ("dice deluxe", ("dice deluxe",)),
        ("ryd", ("ryd", "reveal your deal")),
        ("globez", ("globez",)),
        ("winovate", ("winovate",)),
        ("clan", ("clan go", "x2 badges", "x2 dash", "dash picker")),
    ]
    for result, aliases in rules:
        if any(alias in text for alias in aliases):
            return result
    return ""


def adjusted_due(promo_date: str, days_before: int) -> str:
    result = date.fromisoformat(promo_date) - timedelta(days=days_before)
    while result.weekday() in (4, 5):
        result -= timedelta(days=1)
    return result.isoformat()


def priority(label: str) -> str:
    return {
        "New promo": "High",
        "New theme for promo": "High",
        "Prize Change": "Medium",
        "Reuse": "Low",
    }[label]


def fetch_rows(dates: list[str]) -> dict[str, list[dict[str, str]]]:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["by_date"]
    ids: list[str] = []
    for target in dates:
        ids.extend(str(row["id"]) for row in snapshot.get(target, []) if row.get("product") != "Day")
    query = """
    query($ids:[ID!]!) {
      items(ids:$ids) {
        id name
        column_values(ids:[
          "date_mky27nx7","status","long_text_mkxzgg1v","color_mm4kygty","color_mky9aesm"
        ]) { id text }
      }
    }
    """
    items: list[dict[str, Any]] = []
    for offset in range(0, len(ids), 20):
        items.extend(gql(query, {"ids": ids[offset:offset + 20]})["items"])
    result = {target: [] for target in dates}
    for item in items:
        columns = {column["id"]: column.get("text") or "" for column in item["column_values"]}
        title_date = item["name"][:10] if re.match(r"^\d{4}-\d{2}-\d{2}", item["name"]) else ""
        target = title_date or columns.get("date_mky27nx7")
        if target not in result:
            continue
        normalized = normalize_name(item["name"])
        if re.search(r"lotto\s*-\s*peak", normalized, re.I) or normalized.lower() == "lbp peak":
            continue
        label = columns.get("color_mm4kygty") or ("Reuse" if family(item["name"]) == "rlap" else "")
        if label not in {"Reuse", "Prize Change", "New theme for promo", "New promo"}:
            raise RuntimeError(f"Missing Creative Label for {item['name']}")
        description = columns.get("long_text_mkxzgg1v") or ""
        if str(item["id"]) == "12464458902":
            description = "ADS Personal Offer prize: Hammers. The MM row title is authoritative."
        result[target].append(
            {
                "id": str(item["id"]),
                "name": item["name"],
                "product": columns.get("status") or "",
                "pricing": columns.get("color_mky9aesm") or "",
                "description": description,
                "label": label,
            }
        )
    return result


def source_catalog() -> dict[str, dict[str, Any]]:
    items = json.loads(ART_CACHE.read_text(encoding="utf-8"))["items"]
    return {str(item["id"]): item for item in items}


def source_for(row: dict[str, str], catalog: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source_id = SOURCE_OVERRIDES.get(row["id"]) or SOURCE_BY_FAMILY.get(family(row["name"]))
    if not source_id or source_id not in catalog:
        raise RuntimeError(f"No Creative source/template mapped for {row['name']}")
    return catalog[source_id]


def art_path(row: dict[str, str], source: dict[str, Any], target: str) -> str:
    source_path = source.get("art_link") or ""
    if row["label"] == "Reuse" and source_path:
        return source_path
    suffix = f"{target.replace('-', '_')}_{slug(row['name'])}"
    match = re.match(r"^(.*?\\2026\\)", source_path, re.I)
    if match:
        return match.group(1) + suffix
    root = source_path.rsplit("\\", 1)[0] if "\\" in source_path else r"Q:\Slotomania\CRM3\Creative_Briefs"
    return root + "\\" + suffix


def source_date(source: dict[str, Any]) -> str:
    if source.get("promo_date"):
        return str(source["promo_date"])
    match = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", source.get("group") or "")
    return match.group(0) if match else "reference-missing"


def create_group(title: str) -> str:
    mutation = "mutation($board:ID!,$name:String!){create_group(board_id:$board,group_name:$name){id}}"
    return gql(mutation, {"board": BOARD, "name": title})["create_group"]["id"]


def group_map() -> dict[str, str]:
    query = "query{boards(ids:[18112190666]){groups{id title}}}"
    return {group["title"]: group["id"] for group in gql(query)["boards"][0]["groups"]}


def items_in_group(group_id: str) -> list[dict[str, Any]]:
    query = """
    query($groups:[String!]) {
      boards(ids:[18112190666]) {
        groups(ids:$groups) {
          items_page(limit:100) {
            items { id name subitems { id name updates(limit:1) { id } } }
          }
        }
      }
    }
    """
    groups = gql(query, {"groups": [group_id]})["boards"][0]["groups"]
    return groups[0]["items_page"]["items"] if groups else []


def duplicate_item(source_id: str) -> str:
    mutation = "mutation($board:ID!,$item:ID!){duplicate_item(board_id:$board,item_id:$item){id}}"
    return gql(mutation, {"board": BOARD, "item": source_id})["duplicate_item"]["id"]


def set_columns(board: str, item: str, values: dict[str, Any]) -> None:
    mutation = """
    mutation($board:ID!,$item:ID!,$values:JSON!) {
      change_multiple_column_values(board_id:$board,item_id:$item,column_values:$values){id}
    }
    """
    gql(mutation, {"board": board, "item": item, "values": json.dumps(values)})


def move_item(item: str, group: str) -> None:
    mutation = "mutation($item:ID!,$group:String!){move_item_to_group(item_id:$item,group_id:$group){id}}"
    gql(mutation, {"item": item, "group": group})


def create_update(item: str, body: str) -> None:
    mutation = "mutation($item:ID!,$body:String!){create_update(item_id:$item,body:$body){id}}"
    gql(mutation, {"item": item, "body": body})


def brief_name(row: dict[str, str], source: dict[str, Any]) -> str:
    name = normalize_name(row["name"])
    if row["label"] == "Reuse":
        return f"{name} | Reuse from {source_date(source)}"
    return name


def parent_values(row: dict[str, str], source: dict[str, Any], target: str) -> dict[str, Any]:
    return {
        "name": brief_name(row, source),
        "date4": {"date": target},
        "date_mkwj8wwp": {"date": adjusted_due(target, 7)},
        "date_mkwep612": {"date": adjusted_due(target, 2)},
        "color_mkws3h8e": {"label": priority(row["label"])},
        "text_mkwe4jsr": art_path(row, source, target),
        "status": {"label": "done" if row["label"] == "Reuse" else "Design in progress"},
    }


def parent_body(row: dict[str, str], source: dict[str, Any]) -> str:
    source_url = f"https://playtika.monday.com/boards/{BOARD}/pulses/{source['id']}"
    mm_url = f"https://playtika.monday.com/boards/18388590642/pulses/{row['id']}"
    rows = [
        ("Creative Label", esc(row["label"])),
        ("Source", f'<a href="{source_url}">{source_url}</a>'),
        ("Scope", esc(row["description"] or normalize_name(row["name"]))),
    ]
    if row["label"] != "Reuse":
        rows.append(("Change", esc(f"{source['name']} → {normalize_name(row['name'])}")))
        ask = "Apply only the exact visible mechanic/reward/theme stated in the MM source."
        if row["label"] == "New promo":
            ask = "New promo skeleton — Itay must complete missing mechanic and art direction; do not invent them."
    else:
        ask = "Reuse. No Creative action."
    rows.extend(
        [
            ("Creative Ask", esc(ask)),
            ("MM Source", f'<a href="{mm_url}">{mm_url}</a>'),
        ]
    )
    return table(rows)


def subitem_body(row: dict[str, str], source: dict[str, Any], asset: str) -> str:
    source_url = f"https://playtika.monday.com/boards/{BOARD}/pulses/{source['id']}"
    if row["label"] == "Reuse":
        rows = [
            ("Action", esc(f"Reuse {asset} from {source_date(source)}. No changes.")),
            ("Reference Link", f'<a href="{source_url}">{source_url}</a>'),
            ("Status", "Completed"),
        ]
    elif row["label"] == "New promo":
        rows = [
            ("Asset", esc(asset)),
            ("Change", "New structure. Use only the MM source; Itay must complete missing direction."),
            ("Keep", "Do not invent copy, CTA, timer, values, theme, or mechanic."),
            ("Reference Link", f'<a href="{source_url}">{source_url}</a>'),
            ("Status", "Pending Creative input"),
        ]
    else:
        required = row["description"] or normalize_name(row["name"])
        rows = [
            ("Asset", esc(asset)),
            ("Change", esc(f"{source['name']} → {required}")),
            ("Keep", esc(f"Keep the established {asset} structure; do not invent CTA, timer, or extra rewards.")),
            ("Reference Link", f'<a href="{source_url}">{source_url}</a>'),
            ("Status", "Pending Creative work"),
        ]
    return table(rows)


def write_brief(
    row: dict[str, str],
    target: str,
    group_id: str,
    existing: dict[str, dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
) -> tuple[str, int]:
    source = source_for(row, catalog)
    name = brief_name(row, source)
    item = existing.get(name)
    if item:
        item_id = str(item["id"])
    else:
        item_id = duplicate_item(str(source["id"]))
        set_columns(BOARD, item_id, {"name": name})
        move_item(item_id, group_id)
        time.sleep(3)
    set_columns(BOARD, item_id, parent_values(row, source, target))
    create_update(item_id, parent_body(row, source))
    query = "query($ids:[ID!]!){items(ids:$ids){subitems{id name}}}"
    subitems = gql(query, {"ids": [item_id]})["items"][0].get("subitems") or []
    if not subitems:
        time.sleep(4)
        subitems = gql(query, {"ids": [item_id]})["items"][0].get("subitems") or []
    for subitem in subitems:
        if row["label"] == "Reuse":
            sub_values = {"status": {"label": "Done"}, "color_mkwerpn6": {"label": "Done"}}
        else:
            sub_values = {"status": None, "color_mkwerpn6": None}
        set_columns(SUBITEM_BOARD, str(subitem["id"]), sub_values)
        create_update(str(subitem["id"]), subitem_body(row, source, subitem["name"]))
    return item_id, len(subitems)


def main() -> None:
    args = parse_args()
    dates = sorted(set(args.date))
    rows_by_date = fetch_rows(dates)
    catalog = source_catalog()
    groups = group_map()
    total = 0
    if not args.commit:
        for target in dates:
            print(f"\n{target}: {len(rows_by_date[target])} Creative brief(s)")
            for row in rows_by_date[target]:
                source = source_for(row, catalog)
                print(f"  {row['label']:<19} {normalize_name(row['name'])} <- {source['promo_date']} {source['name']}")
        print("\nDRY RUN - no Monday changes made.")
        return
    for target in dates:
        group_id = groups.get(target) or create_group(target)
        existing = {item["name"]: item for item in items_in_group(group_id)}
        for row in rows_by_date[target]:
            name = brief_name(row, source_for(row, catalog))
            base_name = normalize_name(row["name"])
            existing_item = existing.get(name) or next(
                (
                    item
                    for existing_name, item in existing.items()
                    if existing_name == base_name or existing_name.startswith(base_name + " | Reuse from ")
                ),
                None,
            )
            if existing_item:
                if existing_item["name"] != name:
                    set_columns(BOARD, str(existing_item["id"]), {"name": name})
                source = source_for(row, catalog)
                set_columns(BOARD, str(existing_item["id"]), parent_values(row, source, target))
                for subitem in existing_item.get("subitems") or []:
                    if subitem.get("updates"):
                        continue
                    if row["label"] == "Reuse":
                        sub_values = {"status": {"label": "Done"}, "color_mkwerpn6": {"label": "Done"}}
                    else:
                        sub_values = {"status": None, "color_mkwerpn6": None}
                    set_columns(SUBITEM_BOARD, str(subitem["id"]), sub_values)
                    create_update(str(subitem["id"]), subitem_body(row, source, subitem["name"]))
                print(f"{target} SKIPPED existing {existing_item['id']} {name}")
                total += 1
                continue
            item_id, subitem_count = write_brief(row, target, group_id, existing, catalog)
            total += 1
            print(f"{target} {item_id} {row['label']:<19} subitems={subitem_count} {brief_name(row, source_for(row, catalog))}")
        time.sleep(10)
        for item in items_in_group(group_id):
            match = next((row for row in rows_by_date[target] if brief_name(row, source_for(row, catalog)) == item["name"]), None)
            if match:
                set_columns(BOARD, str(item["id"]), {"status": {"label": "done" if match["label"] == "Reuse" else "Design in progress"}})
    print(f"CREATED/UPDATED {total} Creative briefs across {len(dates)} dates.")


if __name__ == "__main__":
    main()
