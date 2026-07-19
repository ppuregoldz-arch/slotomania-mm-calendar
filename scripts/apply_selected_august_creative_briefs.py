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

PIGGY_BREAK_REF_FOLDER = (
    r"Q:\Slotomania\CRM3\Features\Piggy_2.0\2026\2026_06_17_Piggy_5_Hammers"
)
SPINNER_REF_BASE = (
    r"Q:\Slotomania\CRM3\Features\Spinner_Clash\2026\2026_07_06_Spinner_Clash"
)

SOURCE_OVERRIDES = {
    "12464175428": "12448968305",  # Piggy break — same-trigger 5 Hammers ref
    "12475065098": "12448958742",  # Spinner Clash template
    "12486310516": "12475732350",  # DD SB + hammers → wheel structure chain
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

MGAP_UI_OVERRIDES = {
    "12464188536": {
        "name": "MGAP UI - BOGO",
        "source_id": "12093534228",
        "change": "Existing MGAP BOGO UI → current MGAP BOGO UI.",
        "mechanic": "BOGO MGAP.",
    },
    "12547639977": {
        "name": "MGAP UI - Rolling MGAP Ladder",
        "source_id": "12466613934",
        "change": "Existing MGAP UI → Rolling denom 3 MGAP ladder UI for cycles 2–4.",
        "mechanic": "Three MGAP configs: lower, mid, and higher.",
    },
    "12511214687": {
        "name": "MGAP UI - Bigger Multipliers - Generic",
        "source_id": "12148706201",
        "change": "Existing MGAP Bigger Multipliers UI → Generic Bigger Multipliers MGAP UI.",
        "mechanic": "Bigger Multipliers, Generic theme.",
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
    parser.add_argument(
        "--mgap-ui-only",
        action="store_true",
        help="Create only the separate MGAP UI tasks for the selected dates",
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


def split_creative_owner_ids(owner_ids: list[int]) -> tuple[list[int], list[int]]:
    """Creative Traffic `Creative Owner` → Artist (1st) + Copywriter (2nd)."""
    if not owner_ids:
        return [], []
    if len(owner_ids) == 1:
        return owner_ids[:1], []
    return owner_ids[:1], owner_ids[1:2]


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
        owner_ids = people_ids(columns["people3"].get("value"))
        artist_ids, copywriter_ids = split_creative_owner_ids(owner_ids)
        result[target] = {
            "item_id": str(item["id"]),
            "item_name": item["name"],
            "brief_date": brief_date,
            "artist_ids": artist_ids,
            "copywriter_ids": copywriter_ids,
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
    seen: set[str] = set()
    while source_id and source_id in SOURCE_OVERRIDES:
        if source_id in seen:
            break
        seen.add(source_id)
        mapped = SOURCE_OVERRIDES[source_id]
        if not mapped or mapped == source_id:
            break
        source_id = mapped
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
            if line.startswith(("Q:\\", "/Volumes/CRM3/", "/Volumes/studios/")):
                return line
    raise RuntimeError(f"No CRM3 reference path found for source {source['id']} {source['name']}")


def crm3_paths_in_text(text: str) -> list[str]:
    paths: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(("Q:\\", "/Volumes/CRM3/", "/Volumes/studios/")):
            paths.append(line)
    return paths


def all_crm3_paths(source: dict[str, Any], asset_name: str | None = None) -> list[str]:
    paths: list[str] = []
    for update in source.get("updates") or []:
        paths.extend(crm3_paths_in_text(update.get("text_body") or ""))
    for subitem in source.get("subitems") or []:
        if asset_name and subitem["name"].lower() != asset_name.lower():
            continue
        for update in subitem.get("updates") or []:
            paths.extend(crm3_paths_in_text(update.get("text_body") or ""))
    if source.get("art_link"):
        paths.append(str(source["art_link"]))
    return paths


def crm3_path_to_folder(path: str) -> str:
    path = path.strip().rstrip("\\/")
    if re.search(r"\.(?:png|jpe?g|webp)$", path, re.I):
        if "\\" in path:
            return path.rsplit("\\", 1)[0]
        return path.rsplit("/", 1)[0]
    return path


def crm3_asset_folder(base: str, asset_name: str | None) -> str:
    base = base.rstrip("\\/")
    if not asset_name:
        return base
    asset = asset_name.lower()
    if "banner" in asset and not base.lower().endswith("banner"):
        return base + "\\Banner"
    if "inapp" in asset and not base.lower().endswith("inapp"):
        return base + "\\Inapp"
    return base


def piggy_break_ref_folder(source: dict[str, Any]) -> str:
    for path in all_crm3_paths(source):
        if "2026_06_17_Piggy_5_Hammers" in path:
            return PIGGY_BREAK_REF_FOLDER
    if source.get("art_link") and "Piggy" in str(source.get("art_link")):
        return PIGGY_BREAK_REF_FOLDER
    return ""


def crm3_folder_path(source: dict[str, Any], asset_name: str | None = None) -> str:
    if family(source.get("name") or "") == "piggy" or piggy_break_ref_folder(source):
        piggy_base = piggy_break_ref_folder(source) or PIGGY_BREAK_REF_FOLDER
        return crm3_asset_folder(piggy_base, asset_name)
    if family(source.get("name") or "") == "spinner clash":
        return crm3_asset_folder(SPINNER_REF_BASE, asset_name)
    if family(source.get("name") or "") == "daily deal":
        for path in all_crm3_paths(source):
            if "Daily_Deal" in path:
                return crm3_asset_folder(crm3_path_to_folder(path), asset_name)
        if source.get("art_link"):
            return crm3_asset_folder(str(source["art_link"]), asset_name)
    paths = all_crm3_paths(source, asset_name)
    folders = [crm3_path_to_folder(path) for path in paths]
    if asset_name:
        asset_key = asset_name.lower()
        for folder in folders:
            if "banner" in asset_key and "banner" in folder.lower():
                return folder
            if "inapp" in asset_key and "inapp" in folder.lower():
                return folder
            if "winner" in asset_key and "winner" in folder.lower():
                return folder
    if folders:
        return folders[0]
    paths = all_crm3_paths(source)
    folders = [crm3_path_to_folder(path) for path in paths]
    if asset_name:
        asset_key = asset_name.lower()
        for folder in folders:
            if "banner" in asset_key and "banner" in folder.lower():
                return folder
            if "inapp" in asset_key and "inapp" in folder.lower():
                return folder
    if folders:
        return folders[0]
    if source.get("art_link"):
        return crm3_asset_folder(str(source["art_link"]), asset_name)
    raise RuntimeError(f"No CRM3 folder path found for source {source['id']} {source['name']}")


def load_source_assets(
    rows_by_date: dict[str, list[dict[str, str]]],
    catalog: dict[str, dict[str, Any]],
    extra_source_ids: set[str] | None = None,
) -> None:
    source_ids = sorted(
        ({
            str(source_for(row, catalog)["id"])
            for rows in rows_by_date.values()
            for row in rows
        } | (extra_source_ids or set()))
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
    folder_only: bool = False,
) -> str:
    if folder_only:
        try:
            folder = crm3_folder_path(source, asset_name)
        except RuntimeError:
            if not allow_missing_path:
                raise
            source_url = f"https://playtika.monday.com/boards/{BOARD}/pulses/{source['id']}"
            return f'<a href="{source_url}">{source_url}</a>'
        return f"<code>{esc(folder)}</code>"
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
        if "inapp" in key and "winners" not in key and "journey" not in key:
            return (0, index)
        if "journey" in key and "inapp" in key:
            return (1, index)
        if (
            key == "dd (in store)"
            or key.startswith("store denom")
            or key == "denom"
            or key.startswith("big denom")
        ):
            return (2, index)
        if "winner" in key and "inapp" in key:
            return (3, index)
        if key in {"background", "bg", "theme/bo", "theme / bo"}:
            return (4, index)
        if key == "df":
            return (5, index)
        if key.startswith("denom"):
            return (6, index)
        if key == "banner":
            return (6, index)
        if key == "pp banner":
            return (7, index)
        return (8, index)

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
    copywriter_ids = assignment.get("copywriter_ids")
    if copywriter_ids is None:
        _, copywriter_ids = split_creative_owner_ids(assignment.get("artist_ids") or [])
    return {
        "date_mkwj8wwp": {"date": assignment["brief_date"]},
        "multiple_person_mkwetsg8": people_value(assignment["artist_ids"]),
        "multiple_person_mkwev9a5": people_value(copywriter_ids or []),
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


def required_prize_from_row(row: dict[str, str]) -> str:
    for line in row.get("description", "").splitlines():
        if re.search(r"prize", line, re.I):
            match = re.search(r":\s*(.+)$", line.strip())
            if match:
                return match.group(1).strip()
    return concise_requirement(row)


def inferred_reference_prize(source: dict[str, Any]) -> str:
    for path in all_crm3_paths(source):
        match = re.search(r"Piggy[_\s-]*(\d+)[_\s-]*Hammers", path, re.I)
        if match:
            return f"{match.group(1)} Hammers"
        match = re.search(r"(\d+)\s*Hammers", path, re.I)
        if match:
            return f"{match.group(1)} Hammers"
    for update in source.get("updates") or []:
        text = update.get("text_body") or ""
        match = re.search(r"(\d+)\s*RDS", text, re.I)
        if match:
            return f"{match.group(1)} RDS"
    for subitem in source.get("subitems") or []:
        for update in subitem.get("updates") or []:
            text = update.get("text_body") or ""
            match = re.search(r"(\d+)\s*Hammers", text, re.I)
            if match:
                return f"{match.group(1)} Hammers"
            match = re.search(r"(\d+)\s*RDS", text, re.I)
            if match:
                return f"{match.group(1)} RDS"
    return ""


def promo_trigger_phrase(row: dict[str, str]) -> str:
    fam = family(row["name"])
    return {
        "piggy": "break piggy",
        "spinner clash": "Spinner Clash tournament",
        "daily deal": "DD purchase",
    }.get(fam, fam or "promo")


def is_card_only_reward(row: dict[str, str]) -> bool:
    blob = f"{normalize_name(row['name'])}\n{row.get('description') or ''}".lower()
    if re.search(
        r"\b(pab|hammer|sb\b|coins?|gems?|wheel|rds|ggs|dice|booster|parasheep|"
        r"superspin|airstrike|shield|figz|blast)\b",
        blob,
    ):
        return False
    if re.search(r"\+\s*", blob):
        return False
    if re.search(r"card.only|card only", blob):
        return True
    if re.search(r"\d+\s*★|\d+\*\s*(reg|ace|gold|shiny|wild)", blob):
        return True
    return False


def reference_match_tier(row: dict[str, str], source: dict[str, Any]) -> str:
    req = required_prize_from_row(row)
    ref_prize = inferred_reference_prize(source)
    if row["label"] == "Prize Change":
        trigger = promo_trigger_phrase(row)
        if ref_prize:
            return f"Same trigger: {trigger}; prize differs: {ref_prize} → {req}"
        return f"Same feature: {normalize_name(source.get('name') or '')}; prize differs → {req}"
    if row["label"] == "New theme for promo":
        return (
            f"Same mechanic; theme differs: "
            f"{normalize_name(source.get('name') or '')} → {concise_requirement(row)}"
        )
    return ""


def normalize_subitem_key(name: str) -> str:
    key = re.sub(r"\s+", " ", name.strip().lower())
    key = key.replace("journey/winners", "journey winners")
    return key


def subitem_matches(required: str, existing: str) -> bool:
    req = normalize_subitem_key(required)
    cur = normalize_subitem_key(existing)
    if req == cur:
        return True
    if "winner" in req and "winner" in cur and "inapp" in req and "inapp" in cur:
        return True
    if req in {"dd (in store)", "store denom"} and cur in {
        "dd (in store)",
        "store denom",
        "dd in store",
    }:
        return True
    if req == "main inapp" and cur.startswith("main") and "inapp" in cur:
        return True
    if req == "journey inapp" and "journey" in cur and "inapp" in cur:
        return True
    return False


def playbook_required_subitems(row: dict[str, str]) -> list[str]:
    if row["label"] not in {"Prize Change", "New theme for promo", "New promo"}:
        return []
    fam = family(row["name"])
    card_only = is_card_only_reward(row)
    winners: list[str] = [] if card_only else ["Winners Inapp"]
    if fam == "piggy":
        return ["Main Inapp", *winners, "Banner"]
    if fam == "spinner clash":
        return ["Main Inapp", "Journey Inapp", *winners, "Banner"]
    if fam == "daily deal":
        return ["DD (in store)", *winners]
    return []


def ensure_playbook_subitems(
    parent_id: str,
    row: dict[str, str],
    subitems: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    required = playbook_required_subitems(row)
    if not required:
        return subitems
    result = list(subitems)
    existing_names = [subitem["name"] for subitem in result]
    for name in required:
        if any(subitem_matches(name, existing) for existing in existing_names):
            continue
        subitem_id = create_subitem(parent_id, name)
        result.append({"id": subitem_id, "name": name, "updates": []})
        existing_names.append(name)
        clear_subitem_fields(subitem_id)
        time.sleep(0.35)
    return result


def spinner_prize_lines(row: dict[str, str]) -> list[str]:
    lines: list[str] = []
    for line in (row.get("description") or "").splitlines():
        stripped = line.strip()
        if re.match(r"^\d+(st|nd|rd|th)?\s*:", stripped, re.I) or re.match(
            r"^\d+\s*:", stripped
        ):
            lines.append(re.sub(r"\s+", " ", stripped))
        if re.match(r"^\s*\d+(st|nd|rd)\s*:", stripped, re.I):
            lines.append(re.sub(r"\s+", " ", stripped.lstrip()))
    if lines:
        return lines
    return [
        line.strip()
        for line in (row.get("description") or "").splitlines()
        if re.search(r"★|\*|ace|reg|coins|pack", line, re.I)
        and line.strip()
    ][:8]


def change_summary(row: dict[str, str], source: dict[str, Any]) -> str:
    if row["label"] == "Prize Change" and family(row["name"]) == "piggy":
        ref_prize = inferred_reference_prize(source) or "prior break prize"
        return f"Break prize: {ref_prize} → {required_prize_from_row(row)}"
    if row["label"] == "Prize Change":
        ref_prize = inferred_reference_prize(source)
        req = required_prize_from_row(row)
        if family(row["name"]) == "spinner clash":
            prizes = spinner_prize_lines(row)
            if prizes:
                return f"Rank prizes: {' · '.join(prizes)}"
        if ref_prize:
            return f"{ref_prize} → {req}"
    if row["label"] == "New theme for promo":
        return f"{normalize_name(source.get('name') or '')} → {concise_requirement(row)}"
    return f"{source['name']} → {concise_requirement(row)}"


def numbered_steps_html(steps: list[str]) -> str:
    items = "".join(f"<li><p>{esc(step)}</p></li>" for step in steps)
    return f"<ol>{items}</ol>"


def what_to_change_html(row: dict[str, str], source: dict[str, Any], asset: str) -> str:
    change = change_summary(row, source)
    if row["label"] == "New theme for promo":
        return numbered_steps_html(
            [
                f"Re-theme {asset} per parent Change: {change}.",
                "Keep mechanic layout, prize placement, and CTA structure matching the reference unless Change says otherwise.",
                "Do not alter prizes, amounts, or copy unless the parent Change lists them.",
            ]
        )
    req = required_prize_from_row(row)
    ref_prize = inferred_reference_prize(source) or "reference prize"
    asset_l = asset.lower()
    if family(row["name"]) == "piggy" and "winner" in asset_l:
        return numbered_steps_html(
            [
                "Keep winner/results layout, piggy framing, and claim CTA structure matching the reference.",
                f"Show the break payout the player won: {req} (match Main Inapp PAB treatment).",
                "Update any prize-count badge or callout on the payout cluster to match 2 PAB.",
            ]
        )
    if family(row["name"]) == "piggy" and "inapp" in asset_l and "winner" not in asset_l:
        return numbered_steps_html(
            [
                "Keep layout unchanged: piggy bank, BREAK ME TODAY FOR headline block, prize pedestal, TAKE A BREAK CTA, and coin framing.",
                f"Replace break prize art: {ref_prize} → {req} (two PAB shown per standard PAB treatment).",
                "Update any prize-count badge or callout on the prize cluster to match 2 PAB.",
                "If footer/fine print names the break reward, update hammer wording to PAB.",
            ]
        )
    if family(row["name"]) == "piggy" and "banner" in asset_l:
        return numbered_steps_html(
            [
                "Keep banner layout, piggy key art, and CTA destination unchanged.",
                f"Swap visible break prize from {ref_prize} to {req}.",
                "Update prize callout text or count on the banner if present.",
            ]
        )
    if family(row["name"]) == "spinner clash":
        prizes = spinner_prize_lines(row)
        prize_block = "; ".join(prizes) if prizes else req
        if "main" in asset_l and "journey" not in asset_l and "winner" not in asset_l:
            return numbered_steps_html(
                [
                    "Keep Spinner Clash hub layout, tournament framing, rank ladder structure, and CTA unchanged.",
                    f"Update visible rank prizes on the main inapp to: {prize_block}.",
                    "Keep coin amounts in the reference format unless parent Change lists new coin values.",
                ]
            )
        if "journey" in asset_l:
            return numbered_steps_html(
                [
                    "Keep journey/progress frame layout and rank progression structure matching the reference.",
                    f"Update interim rank prize art/text to the new ladder (top ranks): {prize_block}.",
                    "Keep coin callouts in the reference style where ranks still pay coins.",
                ]
            )
        if "winner" in asset_l:
            return numbered_steps_html(
                [
                    "Keep winner/results/podium layout and claim CTA matching the reference.",
                    f"Update the visible payout for the player's finishing rank per parent Change: {prize_block}.",
                    "Show pack/card art matching the configured rank prizes (Ace packs/cards + coins where listed).",
                ]
            )
        if "banner" in asset_l:
            return numbered_steps_html(
                [
                    "Keep banner layout, Spinner Clash key art, and CTA destination unchanged.",
                    f"Update top rank callouts on the banner to: {prize_block}.",
                ]
            )
    if family(row["name"]) == "daily deal":
        if "dd" in asset_l or "store" in asset_l or "denom" in asset_l:
            return numbered_steps_html(
                [
                    "Keep DD store-card layout, coin/gem tiers, central reward slot, and CTA unchanged.",
                    f"Swap central purchase reward art to: {req}.",
                    "Update SB badge/callout and hammer count art to match 100% SB + 6 Hammers.",
                    "Keep pricing tier skin (High) matching the reference structure.",
                ]
            )
        if "winner" in asset_l:
            return numbered_steps_html(
                [
                    "Keep DD winner/claim frame layout matching the reference.",
                    f"Show the purchased reward payout: {req} (100% SB + 6 Hammers visible).",
                    "Update hammer count and SB callout on the claim art.",
                ]
            )
    return numbered_steps_html(
        [
            f"Apply parent Change to {asset}: {change}.",
            "Keep all non-prize layout, framing, and CTA structure matching the reference.",
            "Update prize art, amount badges, callouts, and footer legal lines that name the old prize.",
        ]
    )


def reference_label_html(
    source: dict[str, Any],
    asset: str,
    row: dict[str, str] | None = None,
) -> str:
    ref_date = source_date(source)
    name = normalize_name(source.get("name") or "")
    tier = reference_match_tier(row, source) if row else ""
    prefix = f"{tier}. " if tier else ""
    return esc(f"{prefix}{ref_date} {name} — {asset}; see attached ref in Monday if needed")


def parent_body(row: dict[str, str], source: dict[str, Any], assets: list[str]) -> str:
    del assets
    return table(
        [
            ("Creative Label", esc(row["label"])),
            ("Change", esc(change_summary(row, source))),
        ]
    )


def subitem_body(row: dict[str, str], source: dict[str, Any], asset: str) -> str:
    if row["label"] in {"Prize Change", "New theme for promo"}:
        reference_cell = reference_label_html(source, asset, row)
        reference_png = reference_png_html(source, asset)
        if reference_png:
            reference_cell = f"{reference_cell}<br>{reference_png}"
        rows = [
            ("What to change", what_to_change_html(row, source, asset)),
            ("Reference", reference_cell),
            (
                "Reference Link",
                reference_link_html(
                    source,
                    asset,
                    allow_missing_path=row["label"] == "New promo",
                    folder_only=True,
                ),
            ),
        ]
        return table(rows)
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


def mgap_ui_specs(
    rows_by_date: dict[str, list[dict[str, str]]],
) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    for target, rows in rows_by_date.items():
        result[target] = []
        for row in rows:
            configured = MGAP_UI_OVERRIDES.get(row["id"])
            if not configured:
                continue
            result[target].append(
                {
                    **configured,
                    "source_mm_item_id": row["id"],
                    "source_row_name": row["name"],
                }
            )
    return result


def mgap_ui_values(
    spec: dict[str, str],
    target: str,
    assignment: dict[str, Any],
) -> dict[str, Any]:
    return {
        "name": spec["name"],
        "date4": {"date": target},
        "date_mkwep612": {"date": adjusted_due(target, 2)},
        "color_mkws3h8e": {"label": "Medium"},
        "color_mky3swe2": {"label": "MGAP"},
        "text_mkwe4jsr": "",
        "status": None,
        "color_mkwes65f": {"label": "Brief Done"},
        **assignment_values(assignment),
    }


def mgap_ui_parent_body(spec: dict[str, str]) -> str:
    return table(
        [
            ("Creative Label", "Prize Change"),
            ("Change", esc(spec["change"])),
        ]
    )


def mgap_ui_subitem_body(
    spec: dict[str, str],
    source: dict[str, Any],
    asset_name: str,
) -> str:
    rows = [
        ("Task", esc(f"Apply the parent Change to {asset_name}.")),
        ("Keep", "Keep the existing MGAP UI structure."),
        ("Mechanic", esc(spec["mechanic"])),
    ]
    reference_png = reference_png_html(source, asset_name)
    if reference_png:
        rows.append(("Reference", reference_png))
    rows.append(("Reference Link", reference_link_html(source, asset_name)))
    return table(rows)


def write_mgap_ui_task(
    spec: dict[str, str],
    target: str,
    assignment: dict[str, Any],
    group_id: str,
    existing: dict[str, dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
) -> tuple[str, int]:
    existing_item = existing.get(spec["name"])
    if existing_item:
        return str(existing_item["id"]), 0
    source = catalog[spec["source_id"]]
    item_id = duplicate_item(spec["source_id"])
    set_columns(BOARD, item_id, {"name": spec["name"]})
    move_item(item_id, group_id)
    time.sleep(4)
    query = """
    query($ids:[ID!]!) {
      items(ids:$ids) {
        updates(limit:1) { id body }
        subitems { id name updates(limit:1) { id body } }
      }
    }
    """
    item = gql(query, {"ids": [item_id]})["items"][0]
    subitems = item.get("subitems") or []
    if not subitems:
        time.sleep(4)
        item = gql(query, {"ids": [item_id]})["items"][0]
        subitems = item.get("subitems") or []
    ui_subitems = [
        subitem for subitem in subitems
        if "ui" in subitem["name"].lower()
    ]
    if not ui_subitems:
        subitem_id = create_subitem(item_id, "MGAP UI")
        ui_subitems = [{"id": subitem_id, "name": "MGAP UI", "updates": []}]
    keep_ids = {str(subitem["id"]) for subitem in ui_subitems}
    for subitem in subitems:
        if str(subitem["id"]) not in keep_ids:
            delete_item(str(subitem["id"]))
    set_columns(BOARD, item_id, mgap_ui_values(spec, target, assignment))
    upsert_update(item_id, item.get("updates") or [], mgap_ui_parent_body(spec))
    for subitem in ui_subitems:
        clear_subitem_fields(str(subitem["id"]))
        upsert_update(
            str(subitem["id"]),
            subitem.get("updates") or [],
            mgap_ui_subitem_body(spec, source, subitem["name"]),
        )
    time.sleep(10)
    item = gql(query, {"ids": [item_id]})["items"][0]
    for subitem in item.get("subitems") or []:
        if "ui" not in subitem["name"].lower():
            delete_item(str(subitem["id"]))
    set_columns(BOARD, item_id, mgap_ui_values(spec, target, assignment))
    return item_id, len(ui_subitems)


def apply_mgap_ui_tasks(
    specs_by_date: dict[str, list[dict[str, str]]],
    assignments: dict[str, dict[str, Any]],
    groups: dict[str, str],
    catalog: dict[str, dict[str, Any]],
    commit: bool,
) -> int:
    total = 0
    for target, specs in specs_by_date.items():
        if not specs:
            continue
        group_id = groups.get(target)
        existing = {
            item["name"]: item
            for item in items_in_group(group_id)
        } if group_id else {}
        for spec in specs:
            action = "SKIP existing" if spec["name"] in existing else "CREATE"
            if not commit:
                print(
                    f"{target} {action}: {spec['name']} "
                    f"<- {spec['source_row_name']}"
                )
                continue
            if not group_id:
                group_id = create_group(target)
                groups[target] = group_id
            item_id, ui_count = write_mgap_ui_task(
                spec,
                target,
                assignments[target],
                group_id,
                existing,
                catalog,
            )
            print(f"{target} {action}: {spec['name']} ({item_id}); UI subitems={ui_count}")
            existing = {
                item["name"]: item
                for item in items_in_group(group_id)
            }
            total += 1
    return total


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
    subitems = ensure_playbook_subitems(item_id, row, subitems)
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
    mgap_specs = mgap_ui_specs(rows_by_date)
    load_source_assets(
        rows_by_date,
        catalog,
        {
            spec["source_id"]
            for specs in mgap_specs.values()
            for spec in specs
        },
    )
    groups = group_map()
    total = 0
    if args.mgap_ui_only:
        created = apply_mgap_ui_tasks(
            mgap_specs,
            assignments,
            groups,
            catalog,
            args.commit,
        )
        if not args.commit:
            print("DRY RUN - no Monday changes made.")
        else:
            print(f"CREATED/SKIPPED {created} standalone MGAP UI task(s).")
        return
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
        print("\nStandalone MGAP UI tasks:")
        apply_mgap_ui_tasks(mgap_specs, assignments, groups, catalog, False)
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
                query = "query($ids:[ID!]!){items(ids:$ids){updates(limit:1){id body} subitems{id name updates(limit:1){id body}}}}"
                live_existing = gql(query, {"ids": [str(existing_item["id"])]})["items"][0]
                subitems = ensure_playbook_subitems(
                    str(existing_item["id"]),
                    row,
                    live_existing.get("subitems") or [],
                )
                for subitem in subitems:
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
                    live_existing.get("updates") or [],
                    parent_body(
                        row,
                        source,
                        [subitem["name"] for subitem in subitems],
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
    apply_mgap_ui_tasks(mgap_specs, assignments, groups, catalog, True)
    print(f"CONSOLIDATED Reuse and created/updated {total} active Creative briefs across {len(dates)} dates.")


if __name__ == "__main__":
    main()
