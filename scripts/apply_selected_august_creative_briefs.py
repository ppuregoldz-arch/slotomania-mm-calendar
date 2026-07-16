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
TRAFFIC_GROUP = "group_title"
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

LABEL_OVERRIDES = {
    "12464188536": "Reuse",  # MGAP BOGO confirmed live in Ops
    "12464318775": "Reuse",  # ADS PO 3* Reg confirmed live in Ops
    "12467506589": "Reuse",  # Exact prior Ace Heist 4* Ace execution
    "12511214687": "Reuse",  # Exact prior Generic Bigger Multipliers execution
}

REUSE_LIVE_OVERRIDES = {
    "12464188536": {
        "date": "2026-05-30",
        "url": "https://playtika.monday.com/boards/2109172490/pulses/11869424484",
    },
    "12464318775": {
        "date": "2026-05-29",
        "url": "https://playtika.monday.com/boards/2109172490/pulses/12113633298",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", action="append", required=True, help="YYYY-MM-DD")
    parser.add_argument("--commit", action="store_true", help="Write to Monday")
    parser.add_argument(
        "--allow-in-flight",
        action="store_true",
        help="Edit items with non-blank Status MM only after explicit Itay approval",
    )
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


def people_ids(value: str | None) -> list[int]:
    if not value:
        return []
    parsed = json.loads(value)
    return [
        int(person["id"])
        for person in parsed.get("personsAndTeams") or []
        if person.get("kind") == "person"
    ]


def people_value(ids: list[int]) -> dict[str, Any]:
    return {
        "personsAndTeams": [
            {"id": person_id, "kind": "person"}
            for person_id in ids
        ]
    }


def traffic_assignments(dates: list[str]) -> dict[str, dict[str, Any]]:
    query = """
    query($groups:[String!]) {
      boards(ids:[18041947639]) {
        groups(ids:$groups) {
          items_page(limit:500) {
            items {
              id name
              column_values(ids:[
                "dup__of_date","people3","person","multiple_person_mkw741g6","people_1"
              ]) { id text value }
            }
          }
        }
      }
    }
    """
    items = gql(query, {"groups": [TRAFFIC_GROUP]})["boards"][0]["groups"][0]["items_page"]["items"]
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        match = re.match(r"^(\d{1,2})/8(?:\D|$)", item["name"])
        if not match:
            continue
        target = f"2026-08-{int(match.group(1)):02d}"
        if target not in dates:
            continue
        columns = {column["id"]: column for column in item["column_values"]}
        brief_date = columns["dup__of_date"].get("text") or ""
        if not brief_date:
            raise RuntimeError(f"Traffic item {item['id']} {item['name']} has no Brief Date")
        result[target] = {
            "item_id": str(item["id"]),
            "item_name": item["name"],
            "brief_date": brief_date,
            "artist_ids": people_ids(columns["people3"].get("value")),
            "mm_ids": people_ids(columns["person"].get("value")),
            "mm_tl_ids": people_ids(columns["multiple_person_mkw741g6"].get("value")),
            "creative_tl_ids": people_ids(columns["people_1"].get("value")),
        }
    missing = sorted(set(dates) - set(result))
    if missing:
        raise RuntimeError(f"Missing Creative Traffic assignment(s): {missing}")
    return result


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
        label = (
            LABEL_OVERRIDES.get(str(item["id"]))
            or columns.get("color_mm4kygty")
            or ("Reuse" if family(item["name"]) == "rlap" else "")
        )
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


def load_source_assets(
    rows_by_date: dict[str, list[dict[str, str]]],
    catalog: dict[str, dict[str, Any]],
) -> None:
    source_ids = sorted(
        {
            str(source_for(row, catalog)["id"])
            for rows in rows_by_date.values()
            for row in rows
        }
    )
    query = """
    query($ids:[ID!]!) {
      items(ids:$ids) {
        id
        updates(limit:50) { id assets { id name url } }
        subitems {
          id name
          updates(limit:50) { id assets { id name url } }
        }
      }
    }
    """
    for offset in range(0, len(source_ids), 20):
        for item in gql(query, {"ids": source_ids[offset:offset + 20]})["items"]:
            assets: list[dict[str, str]] = []
            for update in item.get("updates") or []:
                for asset in update.get("assets") or []:
                    assets.append({**asset, "asset_type": "", "update_id": str(update["id"])})
            for subitem in item.get("subitems") or []:
                for update in subitem.get("updates") or []:
                    for asset in update.get("assets") or []:
                        assets.append(
                            {
                                **asset,
                                "asset_type": subitem["name"],
                                "update_id": str(update["id"]),
                            }
                        )
            if str(item["id"]) in catalog:
                catalog[str(item["id"])]["_reference_assets"] = assets


def reference_asset(source: dict[str, Any], asset_name: str | None = None) -> dict[str, str] | None:
    images = [
        asset
        for asset in source.get("_reference_assets") or []
        if re.search(r"\.(?:png|jpe?g|webp)$", asset.get("name") or "", re.I)
    ]
    if not images:
        return None
    if not asset_name:
        return next(
            (asset for asset in images if asset["name"].lower().endswith(".png")),
            images[0],
        )
    target_tokens = set(re.findall(r"[a-z0-9]+", asset_name.lower()))
    stop = {"asset", "final", "generic", "dynamic", "the"}
    target_tokens -= stop
    scored: list[tuple[float, int, dict[str, str]]] = []
    for index, asset in enumerate(images):
        candidate = f"{asset.get('asset_type') or ''} {asset.get('name') or ''}".lower()
        candidate_tokens = set(re.findall(r"[a-z0-9]+", candidate)) - stop
        overlap = len(target_tokens & candidate_tokens)
        score = overlap / max(1, len(target_tokens))
        if asset_name.lower() == (asset.get("asset_type") or "").lower():
            score += 2
        if score > 0:
            scored.append((score, -index, asset))
    if not scored:
        return None
    scored.sort(reverse=True, key=lambda item: (item[0], item[1]))
    return scored[0][2]


def reference_png_html(source: dict[str, Any], asset_name: str | None = None) -> str:
    asset = reference_asset(source, asset_name)
    if not asset:
        return ""
    url = esc(asset["url"])
    return f'<a href="{url}"><img src="{url}" alt="{esc(asset["name"])}" width="600"></a>'


def reference_link_html(
    source: dict[str, Any],
    asset_name: str | None = None,
    allow_missing_path: bool = False,
) -> str:
    asset = reference_asset(source, asset_name)
    if asset:
        url = esc(asset["url"])
        return f'<a href="{url}">{url}</a>'
    source_url = f"https://playtika.monday.com/boards/{BOARD}/pulses/{source['id']}"
    try:
        return f"<code>{esc(source_reference_path(source))}</code>"
    except RuntimeError:
        if not allow_missing_path:
            raise
        return f'<a href="{source_url}">{source_url}</a>'


def reuse_evidence(
    row: dict[str, str],
    catalog: dict[str, dict[str, Any]],
) -> dict[str, str]:
    live = REUSE_LIVE_OVERRIDES.get(row["id"])
    if live:
        return {
            "date": live["date"],
            "reference": "",
            "link": (
                f'<a href="{esc(live["url"])}">Ops live task</a><br>'
                "No exact Creative reference found — confirmed live in Ops."
            ),
        }
    source = source_for(row, catalog)
    try:
        link = reference_link_html(source)
    except RuntimeError:
        link = "No exact Creative reference found — prior live date confirmed."
    return {
        "date": source_date(source),
        "reference": reference_png_html(source),
        "link": link,
    }


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


def assert_brief_editable(item_id: str, allow_in_flight: bool = False) -> str:
    query = """
    query($ids:[ID!]!) {
      items(ids:$ids) {
        column_values(ids:["color_mkwes65f"]) { text }
      }
    }
    """
    items = gql(query, {"ids": [item_id]})["items"]
    status = ""
    if items and items[0]["column_values"]:
        status = (items[0]["column_values"][0].get("text") or "").strip()
    if status == "—":
        status = ""
    if status and not allow_in_flight:
        raise RuntimeError(
            f"Refusing to edit item {item_id}: Status MM={status!r}. "
            "Ask Itay first, then rerun with --allow-in-flight."
        )
    if status:
        print(f"WARNING: approved in-flight override for {item_id} (Status MM={status!r})")
    return status


def clear_subitem_fields(subitem_id: str) -> None:
    set_columns(
        SUBITEM_BOARD,
        subitem_id,
        {
            "status": None,
            "color_mkwerpn6": None,
            "color_mkwe6hz": None,
            "long_text_mkwyvrm1": "",
        },
    )


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


def create_subitem(parent_id: str, name: str) -> str:
    mutation = """
    mutation($parent:ID!,$name:String!) {
      create_subitem(parent_item_id:$parent,item_name:$name){id}
    }
    """
    return gql(mutation, {"parent": parent_id, "name": name})["create_subitem"]["id"]


def canonical_subitem_order(names: list[str]) -> list[str]:
    def rank(name: str, index: int) -> tuple[int, int]:
        key = name.strip().lower()
        if "inapp" in key and "winners" not in key:
            return (0, index)
        if key in {"background", "bg", "theme/bo", "theme / bo"}:
            return (1, index)
        if key == "df":
            return (2, index)
        if (
            key == "dd (in store)"
            or key.startswith("denom")
            or key.startswith("big denom")
            or key.startswith("store denom")
        ):
            return (3, index)
        if key == "banner":
            return (4, index)
        if key == "pp banner":
            return (5, index)
        return (6, index)

    return [
        name
        for _, name in sorted(
            enumerate(names),
            key=lambda pair: rank(pair[1], pair[0]),
        )
    ]


def reorder_subitems(parent_id: str) -> None:
    query = """
    query($ids:[ID!]!) {
      items(ids:$ids) {
        subitems { id name updates(limit:1) { body } }
      }
    }
    """
    subitems = gql(query, {"ids": [parent_id]})["items"][0]["subitems"]
    current = [subitem["name"] for subitem in subitems]
    desired = canonical_subitem_order(current)
    if current == desired:
        return
    by_name = {subitem["name"]: subitem for subitem in subitems}
    if len(by_name) != len(subitems):
        raise RuntimeError(f"Cannot safely reorder duplicate subitem names on {parent_id}: {current}")
    new_ids: list[str] = []
    for name in desired:
        subitem_id = create_subitem(parent_id, name)
        new_ids.append(subitem_id)
        updates = by_name[name].get("updates") or []
        if updates and updates[0].get("body"):
            create_update(subitem_id, updates[0]["body"])
        clear_subitem_fields(subitem_id)
        time.sleep(0.4)
    for subitem in subitems:
        delete_item(str(subitem["id"]))
    print(f"REORDERED {parent_id}: {current} -> {desired}; new subitems={new_ids}")


def brief_name(row: dict[str, str], source: dict[str, Any]) -> str:
    del source
    return normalize_name(row["name"])


def status_mm_label(row: dict[str, str]) -> str:
    if row["label"] == "New promo":
        return "MM work in progress"
    return "Brief Done"


def assignment_values(assignment: dict[str, Any]) -> dict[str, Any]:
    return {
        "date_mkwj8wwp": {"date": assignment["brief_date"]},
        "multiple_person_mkwetsg8": people_value(assignment["artist_ids"]),
        "person": people_value(assignment["mm_ids"]),
        "multiple_person_mkwetd0y": people_value(assignment["mm_tl_ids"]),
        "multiple_person_mkwez377": people_value(assignment["creative_tl_ids"]),
    }


def parent_values(
    row: dict[str, str],
    source: dict[str, Any],
    target: str,
    assignment: dict[str, Any],
) -> dict[str, Any]:
    return {
        "name": brief_name(row, source),
        "date4": {"date": target},
        "date_mkwep612": {"date": adjusted_due(target, 2)},
        "color_mkws3h8e": {"label": priority(row["label"])},
        "text_mkwe4jsr": "",
        "status": None,
        "color_mkwes65f": {"label": status_mm_label(row)},
        **assignment_values(assignment),
    }


def reuse_values(target: str, assignment: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": REUSE_TASK_NAME,
        "date4": {"date": target},
        "color_mkws3h8e": {"label": "Low"},
        "status": {"label": "done"},
        "color_mkwes65f": {"label": "Ready - no action needed"},
        **assignment_values(assignment),
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
    del assets
    return table(
        [
            ("Creative Label", esc(row["label"])),
            ("Change", esc(f"{source['name']} → {concise_requirement(row)}")),
        ]
    )


def subitem_body(row: dict[str, str], source: dict[str, Any], asset: str) -> str:
    rows = [
        ("Task", esc(f"Apply the parent Change to {asset}.")),
        ("Keep", "Match the reference for everything else."),
    ]
    if row["label"] == "New promo":
        rows.append(
            (
                "Skeleton",
                "Itay must complete missing mechanic, prizes, and format requirements. Do not invent them.",
            )
        )
    reference_png = reference_png_html(source, asset)
    if reference_png:
        rows.append(("Reference", reference_png))
    rows.append(
        (
            "Reference Link",
            reference_link_html(source, asset, row["label"] == "New promo"),
        )
    )
    return table(rows)


def reuse_body(rows: list[dict[str, str]], catalog: dict[str, dict[str, Any]]) -> str:
    header = (
        "<thead><tr><th><p><strong>Promotion</strong></p></th>"
        "<th><p><strong>Reuse from</strong></p></th>"
        "<th><p><strong>Reference</strong></p></th>"
        "<th><p><strong>Reference Link</strong></p></th></tr></thead>"
    )
    body = []
    for row in rows:
        evidence = reuse_evidence(row, catalog)
        body.append(
            "<tr>"
            f"<td><p>{esc(normalize_name(row['name']))}</p></td>"
            f"<td><p>{esc(evidence['date'])}</p></td>"
            f"<td><p>{evidence['reference']}</p></td>"
            f"<td><p>{evidence['link']}</p></td>"
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
    assignment: dict[str, Any],
    group_id: str,
    existing: dict[str, dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
    allow_in_flight: bool = False,
) -> tuple[str, int]:
    source = source_for(row, catalog)
    name = brief_name(row, source)
    item = existing.get(name)
    if item:
        item_id = str(item["id"])
        assert_brief_editable(item_id, allow_in_flight)
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
    set_columns(BOARD, item_id, parent_values(row, source, target, assignment))
    upsert_update(
        item_id,
        live_item.get("updates") or [],
        parent_body(row, source, [subitem["name"] for subitem in subitems]),
    )
    for subitem in subitems:
        clear_subitem_fields(str(subitem["id"]))
        upsert_update(
            str(subitem["id"]),
            subitem.get("updates") or [],
            subitem_body(row, source, subitem["name"]),
        )
    reorder_subitems(item_id)
    return item_id, len(subitems)


def main() -> None:
    args = parse_args()
    dates = sorted(set(args.date))
    rows_by_date = fetch_rows(dates)
    assignments = traffic_assignments(dates)
    catalog = source_catalog()
    load_source_assets(rows_by_date, catalog)
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
                f"{len(active_rows)} active brief(s), delete {len(old_reuse)} old Reuse item(s); "
                f"Brief Date {assignments[target]['brief_date']}"
            )
            for row in reuse_rows:
                evidence = reuse_evidence(row, catalog)
                print(
                    f"  REUSE {normalize_name(row['name'])} <- {evidence['date']} "
                    f"{re.sub('<[^>]+>', ' ', evidence['link'])}"
                )
            for row in active_rows:
                source = source_for(row, catalog)
                print(f"  {row['label']:<19} {normalize_name(row['name'])} <- {source_date(source)} {source['name']}")
        print("\nDRY RUN - no Monday changes made.")
        return
    for target in dates:
        assignment = assignments[target]
        group_id = groups.get(target) or create_group(target)
        current_items = items_in_group(group_id)
        reuse_rows = [row for row in rows_by_date[target] if row["label"] == "Reuse"]
        active_rows = [row for row in rows_by_date[target] if row["label"] != "Reuse"]

        reuse_item = next((item for item in current_items if item["name"] == REUSE_TASK_NAME), None)
        if reuse_item:
            reuse_item_id = str(reuse_item["id"])
            assert_brief_editable(reuse_item_id, args.allow_in_flight)
        else:
            reuse_item_id = create_bare_item(group_id, REUSE_TASK_NAME)
            reuse_item = {"id": reuse_item_id, "name": REUSE_TASK_NAME, "updates": [], "subitems": []}
        set_columns(BOARD, reuse_item_id, reuse_values(target, assignment))
        upsert_update(reuse_item_id, reuse_item.get("updates") or [], reuse_body(reuse_rows, catalog))
        for subitem in reuse_item.get("subitems") or []:
            delete_item(str(subitem["id"]))

        deleted = 0
        for item in current_items:
            if str(item["id"]) == reuse_item_id:
                continue
            if is_old_reuse_item(item, reuse_rows):
                assert_brief_editable(str(item["id"]), args.allow_in_flight)
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
                assert_brief_editable(str(existing_item["id"]), args.allow_in_flight)
                source = source_for(row, catalog)
                for subitem in existing_item.get("subitems") or []:
                    clear_subitem_fields(str(subitem["id"]))
                    upsert_update(
                        str(subitem["id"]),
                        subitem.get("updates") or [],
                        subitem_body(row, source, subitem["name"]),
                    )
                set_columns(
                    BOARD,
                    str(existing_item["id"]),
                    parent_values(row, source, target, assignment),
                )
                upsert_update(
                    str(existing_item["id"]),
                    existing_item.get("updates") or [],
                    parent_body(
                        row,
                        source,
                        [subitem["name"] for subitem in existing_item.get("subitems") or []],
                    ),
                )
                reorder_subitems(str(existing_item["id"]))
                print(f"{target} UPDATED existing {existing_item['id']} {name}")
                total += 1
                continue
            item_id, subitem_count = write_brief(
                row,
                target,
                assignment,
                group_id,
                existing,
                catalog,
                args.allow_in_flight,
            )
            total += 1
            print(f"{target} {item_id} {row['label']:<19} subitems={subitem_count} {brief_name(row, source_for(row, catalog))}")
        time.sleep(10)
        for item in items_in_group(group_id):
            if item["name"] == REUSE_TASK_NAME:
                set_columns(BOARD, str(item["id"]), reuse_values(target, assignment))
                continue
            match = next((row for row in rows_by_date[target] if brief_name(row, source_for(row, catalog)) == item["name"]), None)
            if match:
                set_columns(
                    BOARD,
                    str(item["id"]),
                    {
                        "status": None,
                        "color_mkwes65f": {"label": status_mm_label(match)},
                    },
                )
    print(f"CONSOLIDATED Reuse and created/updated {total} active Creative briefs across {len(dates)} dates.")


if __name__ == "__main__":
    main()
