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
REUSE_TASK_NAME = "REUSE - No Creative Action"

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


def source_reference_path(source: dict[str, Any]) -> str:
    if source.get("art_link"):
        return str(source["art_link"])
    texts = [update.get("text_body") or "" for update in source.get("updates") or []]
    for subitem in source.get("subitems") or []:
        texts.extend(update.get("text_body") or "" for update in subitem.get("updates") or [])
    for text in texts:
        for line in text.splitlines():
            line = line.strip()
            if line.startswith(("Q:\\", "/Volumes/CRM3/")):
                return line
    raise RuntimeError(f"No CRM3 reference path found for source {source['id']} {source['name']}")


def reference_html(source: dict[str, Any], allow_missing_path: bool = False) -> str:
    source_url = f"https://playtika.monday.com/boards/{BOARD}/pulses/{source['id']}"
    try:
        path = f"<code>{esc(source_reference_path(source))}</code>"
    except RuntimeError:
        if not allow_missing_path:
            raise
        path = "No valid prior CRM3 art reference — new structure."
    return (
        f'<a href="{source_url}">Monday source</a><br>'
        f"{path}"
    )


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
            items {
              id name
              updates(limit:1) { id body }
              subitems { id name updates(limit:1) { id body } }
            }
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


def create_bare_item(group_id: str, name: str) -> str:
    mutation = """
    mutation($board:ID!,$group:String!,$name:String!) {
      create_item(board_id:$board,group_id:$group,item_name:$name){id}
    }
    """
    return gql(mutation, {"board": BOARD, "group": group_id, "name": name})["create_item"]["id"]


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


def edit_update(update_id: str, body: str) -> None:
    mutation = "mutation($id:ID!,$body:String!){edit_update(id:$id,body:$body){id}}"
    gql(mutation, {"id": update_id, "body": body})


def upsert_update(item_id: str, updates: list[dict[str, Any]], body: str) -> None:
    if updates:
        edit_update(str(updates[0]["id"]), body)
    else:
        create_update(item_id, body)


def delete_item(item_id: str) -> None:
    mutation = "mutation($item:ID!){delete_item(item_id:$item){id}}"
    gql(mutation, {"item": item_id})


def brief_name(row: dict[str, str], source: dict[str, Any]) -> str:
    del source
    return normalize_name(row["name"])


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


def concise_requirement(row: dict[str, str]) -> str:
    title = normalize_name(row["name"])
    lines = [re.sub(r"\s+", " ", line).strip() for line in row["description"].splitlines()]
    first_block: list[str] = []
    for line in lines:
        if not line and first_block:
            break
        if line:
            first_block.append(line)
    details = " · ".join(first_block)
    if details and details.lower() not in title.lower():
        return f"{title} — {details}"[:700]
    return title


def parent_body(row: dict[str, str], source: dict[str, Any], assets: list[str]) -> str:
    rows = [
        ("Creative Label", esc(row["label"])),
        ("Change", esc(f"{source['name']} → {concise_requirement(row)}")),
        (
            "Reference",
            f"{reference_html(source, row['label'] == 'New promo')}<br>"
            f"Reference date: {esc(source_date(source))}",
        ),
        ("Assets", esc(", ".join(assets) if assets else "No asset scope yet")),
    ]
    if row["label"] == "New promo":
        rows.append(
            (
                "Skeleton",
                "Itay must complete missing mechanic and art direction. Do not invent copy, values, CTA, timer, or theme.",
            )
        )
    return table(rows)


def subitem_body(row: dict[str, str], source: dict[str, Any], asset: str) -> str:
    return table(
        [
            ("Task", esc(f"Apply the parent Change to {asset}.")),
            ("Keep", "Match the reference for everything else."),
            ("Reference", reference_html(source, row["label"] == "New promo")),
        ]
    )


def reuse_body(rows: list[dict[str, str]], catalog: dict[str, dict[str, Any]]) -> str:
    header = (
        "<thead><tr><th><p><strong>Promotion</strong></p></th>"
        "<th><p><strong>Reuse from</strong></p></th>"
        "<th><p><strong>Reference</strong></p></th></tr></thead>"
    )
    body = []
    for row in rows:
        source = source_for(row, catalog)
        body.append(
            "<tr>"
            f"<td><p>{esc(normalize_name(row['name']))}</p></td>"
            f"<td><p>{esc(source_date(source))}</p></td>"
            f"<td><p>{reference_html(source)}</p></td>"
            "</tr>"
        )
    return "<table>" + header + "<tbody>" + "".join(body) + "</tbody></table>"


def is_old_reuse_item(
    item: dict[str, Any],
    reuse_rows: list[dict[str, str]],
) -> bool:
    for row in reuse_rows:
        base = normalize_name(row["name"])
        if item["name"] == base or item["name"].startswith(base + " | Reuse from "):
            return True
    return False


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
    query = "query($ids:[ID!]!){items(ids:$ids){updates(limit:1){id body} subitems{id name updates(limit:1){id body}}}}"
    live_item = gql(query, {"ids": [item_id]})["items"][0]
    subitems = live_item.get("subitems") or []
    if not subitems:
        time.sleep(4)
        live_item = gql(query, {"ids": [item_id]})["items"][0]
        subitems = live_item.get("subitems") or []
    set_columns(BOARD, item_id, parent_values(row, source, target))
    upsert_update(
        item_id,
        live_item.get("updates") or [],
        parent_body(row, source, [subitem["name"] for subitem in subitems]),
    )
    for subitem in subitems:
        sub_values = {"status": None, "color_mkwerpn6": None}
        set_columns(SUBITEM_BOARD, str(subitem["id"]), sub_values)
        upsert_update(
            str(subitem["id"]),
            subitem.get("updates") or [],
            subitem_body(row, source, subitem["name"]),
        )
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
            reuse_rows = [row for row in rows_by_date[target] if row["label"] == "Reuse"]
            active_rows = [row for row in rows_by_date[target] if row["label"] != "Reuse"]
            group_id = groups.get(target)
            existing = items_in_group(group_id) if group_id else []
            old_reuse = [item for item in existing if is_old_reuse_item(item, reuse_rows)]
            print(
                f"\n{target}: one consolidated Reuse task ({len(reuse_rows)} promotions), "
                f"{len(active_rows)} active brief(s), delete {len(old_reuse)} old Reuse item(s)"
            )
            for row in reuse_rows:
                source = source_for(row, catalog)
                print(
                    f"  REUSE {normalize_name(row['name'])} <- {source_date(source)} "
                    f"{source_reference_path(source)}"
                )
            for row in active_rows:
                source = source_for(row, catalog)
                print(f"  {row['label']:<19} {normalize_name(row['name'])} <- {source_date(source)} {source['name']}")
        print("\nDRY RUN - no Monday changes made.")
        return
    for target in dates:
        group_id = groups.get(target) or create_group(target)
        current_items = items_in_group(group_id)
        reuse_rows = [row for row in rows_by_date[target] if row["label"] == "Reuse"]
        active_rows = [row for row in rows_by_date[target] if row["label"] != "Reuse"]

        reuse_item = next((item for item in current_items if item["name"] == REUSE_TASK_NAME), None)
        if reuse_item:
            reuse_item_id = str(reuse_item["id"])
        else:
            reuse_item_id = create_bare_item(group_id, REUSE_TASK_NAME)
            reuse_item = {"id": reuse_item_id, "name": REUSE_TASK_NAME, "updates": [], "subitems": []}
        set_columns(
            BOARD,
            reuse_item_id,
            {
                "name": REUSE_TASK_NAME,
                "date4": {"date": target},
                "color_mkws3h8e": {"label": "Low"},
                "status": {"label": "done"},
            },
        )
        upsert_update(reuse_item_id, reuse_item.get("updates") or [], reuse_body(reuse_rows, catalog))
        for subitem in reuse_item.get("subitems") or []:
            delete_item(str(subitem["id"]))

        deleted = 0
        for item in current_items:
            if str(item["id"]) == reuse_item_id:
                continue
            if is_old_reuse_item(item, reuse_rows):
                delete_item(str(item["id"]))
                deleted += 1
        print(
            f"{target} {reuse_item_id} consolidated {len(reuse_rows)} Reuse promotion(s); "
            f"deleted {deleted} old Reuse item(s)"
        )

        existing = {
            item["name"]: item
            for item in items_in_group(group_id)
            if item["name"] != REUSE_TASK_NAME
        }
        for row in active_rows:
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
                source = source_for(row, catalog)
                for subitem in existing_item.get("subitems") or []:
                    sub_values = {"status": None, "color_mkwerpn6": None}
                    set_columns(SUBITEM_BOARD, str(subitem["id"]), sub_values)
                    upsert_update(
                        str(subitem["id"]),
                        subitem.get("updates") or [],
                        subitem_body(row, source, subitem["name"]),
                    )
                set_columns(BOARD, str(existing_item["id"]), parent_values(row, source, target))
                upsert_update(
                    str(existing_item["id"]),
                    existing_item.get("updates") or [],
                    parent_body(
                        row,
                        source,
                        [subitem["name"] for subitem in existing_item.get("subitems") or []],
                    ),
                )
                print(f"{target} UPDATED existing {existing_item['id']} {name}")
                total += 1
                continue
            item_id, subitem_count = write_brief(row, target, group_id, existing, catalog)
            total += 1
            print(f"{target} {item_id} {row['label']:<19} subitems={subitem_count} {brief_name(row, source_for(row, catalog))}")
        time.sleep(10)
        for item in items_in_group(group_id):
            if item["name"] == REUSE_TASK_NAME:
                set_columns(
                    BOARD,
                    str(item["id"]),
                    {
                        "date4": {"date": target},
                        "color_mkws3h8e": {"label": "Low"},
                        "status": {"label": "done"},
                    },
                )
                continue
            match = next((row for row in rows_by_date[target] if brief_name(row, source_for(row, catalog)) == item["name"]), None)
            if match:
                set_columns(BOARD, str(item["id"]), {"status": {"label": "done" if match["label"] == "Reuse" else "Design in progress"}})
    print(f"CONSOLIDATED Reuse and created/updated {total} active Creative briefs across {len(dates)} dates.")


if __name__ == "__main__":
    main()
