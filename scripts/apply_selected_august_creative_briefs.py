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
STATUS_MM_COLUMN = "color_mkwes65f"
STATUS_CREATIVE_COLUMN = "status"
STATUS_MM_READY_FOR_BRIEF = "Ready for Brief"
STATUS_MM_REUSE = "Ready - no action needed"
STATUS_MM_NEW_PROMO_SKELETON = "MM work in progress"
# Status MM has duplicate label names; index 4 "Ready for Brief" is deactivated — use index 10.
STATUS_MM_INDEX = {
    STATUS_MM_READY_FOR_BRIEF: 10,
    STATUS_MM_REUSE: 6,
    STATUS_MM_NEW_PROMO_SKELETON: 8,
}
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
    "blast": "11058531907",
}

PIGGY_BREAK_REF_FOLDER = (
    r"Q:\Slotomania\CRM3\Features\Piggy_2.0\2026\2026_06_17_Piggy_5_Hammers"
)
SPINNER_REF_BASE = (
    r"Q:\Slotomania\CRM3\Features\Spinner_Clash\2026\2026_07_06_Spinner_Clash"
)
ADS_REWARDED_VIDEO_REF = (
    r"Q:\Slotomania\CRM3\Generic Promotions\Rewarded_Video"
)
GENERIC_DAILY_DEAL_PATH_HINTS = (
    "8hammers",
    "8_hammers",
    "hammer_wheel",
    "sb_wheel",
    "winovate_wheel",
    "wilda_hammers",
    "parasheep_hammers",
    "3reg_hammer",
)

THEMED_CRM3_TOKENS = (
    "holidays & events",
    "holidays\\ events",
    "4th_of_july",
    "4th of july",
    "july_4",
    "independence",
    "easter",
    "thanksgiving",
    "memorial",
    "christmas",
    "xmas",
    "valentine",
    "halloween",
    "st_patrick",
    "patrick",
    "carnival",
    "black_friday",
    "new_year",
    "world_cup",
    "xmasinJuly",
    "xmas_in_july",
)

GENERIC_DD_HAMMER_WHEEL_FOLDER = (
    r"Q:\Slotomania\CRM3\Features\Daily_Deal\2026\2026_07_09_DD_Hammer_Wheel"
)

GENERIC_ROLLING_SUPERSIZED_REF = (
    r"Q:\Slotomania\CRM3\Generic Promotions\Supersize_Wins\2025"
    r"\2025_04_06_Supersized_Wins_X_RO"
)

SOURCE_OVERRIDES = {
    "12464175428": "12448968305",  # Piggy break — same-trigger 5 Hammers ref
    "12475065098": "12448958742",  # Spinner Clash template
    "12486310516": "12475732350",  # DD SB + hammers → wheel structure chain
    "12464189091": "10904501949",  # ADS PO 2* Reg — Cards arts (not ROOC / paid PO)
    "12510879320": "18333371364",  # Rolling Supersized — generic Supersize_Wins base art
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
    "12476427941": "12475750417",  # DD Shiny+hammers wheel — generic SB/hammer structure
    "12475100661": "11868921934",  # Generic MES Ace Heist structure
}

REUSE_REFERENCE_FOLDER_OVERRIDES = {
    "12464189091": ADS_REWARDED_VIDEO_REF,
    "12510879320": GENERIC_ROLLING_SUPERSIZED_REF,
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
    "12548089680": {
        "date": "2026-05-14",
        "url": "https://playtika.monday.com/boards/2109172490/pulses/11978197029",
    },
}

MGAP_UI_OVERRIDES = {
    "12464188536": {
        "name": "MGAP UI - BOGO",
        "source_id": "12093534228",
        "change": "Existing MGAP BOGO UI → current MGAP BOGO UI.",
        "mechanic": "BOGO MGAP.",
        "skip_brief": True,
        "skip_reason": "MGAP BOGO UI already shipped — no new UI brief.",
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
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Delete Monetization-Art brief parents in each date group before recreate",
    )
    return parser.parse_args()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def table(rows: list[tuple[str, str]]) -> str:
    return "<table><tbody>" + "".join(
        f"<tr><td><p><strong>{esc(key)}</strong></p></td><td><p>{value}</p></td></tr>"
        for key, value in rows
    ) + "</tbody></table>"


def vertical_field_table(rows: list[tuple[str, str]]) -> str:
    """Monday brief table: one label row per field, top to bottom (see Battlesheep refs)."""
    return "<table><tbody>" + "".join(
        f"<tr><td><p>{esc(label)}</p></td><td>{cell}</td></tr>"
        for label, cell in rows
    ) + "</tbody></table>"


def prize_change_table(
    change_lines: list[str],
    reference_cell: str,
    reference_link_cell: str,
    theme: str = "",
    hook: str | None = None,
    sku: str = "",
    cta: str = "",
) -> str:
    rows: list[tuple[str, str]] = []
    for line in change_lines:
        rows.append(("What to change", f"<p>{esc(strip_pricing_prose(line))}</p>"))
    if theme:
        rows.append(("Theme", f"<p>{esc(theme)}</p>"))
    if hook:
        rows.append(("Hook", f"<p>{esc(hook)}</p>"))
    if sku:
        rows.append(("SKU", f"<p>{esc(sku)}</p>"))
    rows.append(("Reference", reference_cell or "<p></p>"))
    rows.append(("Reference Link", reference_link_cell or "<p></p>"))
    if cta:
        rows.append(("CTA", f"<p>{esc(cta)}</p>"))
    return vertical_field_table(rows)


def new_promo_subitem_table(
    asset: str,
    reference_cell: str,
    reference_link_cell: str,
) -> str:
    """New promo vertical template — skeleton for Itay; always includes CTA row."""
    key = normalize_subitem_key(asset)
    rows: list[tuple[str, str]] = []
    if asset_is_background(asset) or key in {"bg", "background", "theme/bo", "theme / bo"}:
        rows.append(
            (
                "BG",
                "<p>Skeleton — Itay to complete background / layout for this promo.</p>",
            )
        )
    else:
        rows.append(
            (
                "Main Message",
                f"<p>Skeleton — Itay to complete main message for {esc(asset)}.</p>",
            )
        )
    rows.append(
        ("Benefits", "<p>Skeleton — Itay to complete visible benefits / prizes.</p>")
    )
    rows.append(("Reference", reference_cell or "<p></p>"))
    rows.append(("Reference Link", reference_link_cell or "<p></p>"))
    rows.append(("CTA", "<p>Skeleton — Itay to complete CTA destination / label.</p>"))
    return vertical_field_table(rows)


def normalize_name(value: str) -> str:
    value = re.sub(r"^\d{4}-\d{2}-\d{2}\s*\|\s*", "", value).strip()
    return re.sub(r"\s+", " ", value.replace("—", "-").replace("–", "-"))


def strip_pricing_prose(text: str) -> str:
    """Remove MM pricing tiers from Creative brief text (not for Ops/config)."""
    if not text:
        return text
    text = re.sub(r"\s*\|\s*[HML](?:ax)?\s*Pricing\s*", "", text, flags=re.I)
    text = re.sub(r",?\s*\b[HML](?:ax)?\s+pricing\b", "", text, flags=re.I)
    text = re.sub(r",?\s*\b(?:high|medium|max)\s+pricing\b", "", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" ,;·|-")
    return text


def brief_display_name(row: dict[str, str]) -> str:
    return strip_pricing_prose(normalize_name(row["name"]))


def normalize_creative_label(label: str) -> str:
    """Brief labels: only Prize Change and New theme for promo use delta tables; else New promo."""
    label = (label or "").strip()
    if not label:
        return ""
    if label == "Reuse":
        return label
    if label in {"Prize Change", "New theme for promo"}:
        return label
    return "New promo"


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
        ("blast", ("blast vegas", "blast challenge", "vegas blast", "cozy blast")),
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


def normalized_traffic_people(assignment: dict[str, Any]) -> tuple[list[int], list[int]]:
    """Artist = Traffic 1st owner only; Copywriter = 2nd only (never both on Artist)."""
    artist_ids = list(assignment.get("artist_ids") or [])
    copywriter_ids = list(assignment.get("copywriter_ids") or [])
    if not copywriter_ids and artist_ids:
        artist_ids, copywriter_ids = split_creative_owner_ids(artist_ids)
    copy_set = set(copywriter_ids)
    artist_ids = [person_id for person_id in artist_ids if person_id not in copy_set]
    return artist_ids[:1], copywriter_ids[:1]


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
        raw_label = (
            LABEL_OVERRIDES.get(str(item["id"]))
            or columns.get("color_mm4kygty")
            or ("Reuse" if family(item["name"]) == "rlap" else "")
        )
        if not raw_label:
            raise RuntimeError(f"Missing Creative Label for {item['name']}")
        label = normalize_creative_label(raw_label)
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


def source_reference_path(
    source: dict[str, Any],
    row: dict[str, str] | None = None,
) -> str:
    if is_ads_po_source(source):
        art = source.get("art_link") or ""
        if art and "Rewarded_Video" in str(art):
            return str(art)
        for path in all_crm3_paths(source):
            if "Rewarded_Video" in path:
                return crm3_path_to_folder(path)
    if "supersized" in (source.get("name") or "").lower():
        generic = generic_rolling_supersized_folder(all_crm3_paths(source))
        if generic:
            return generic
    if source.get("art_link"):
        art = str(source["art_link"])
        if not is_themed_crm3_path(art) or (row and mm_allows_themed_crm3_reference(row)):
            if "easter_ro_supersized" not in art.lower():
                return art
        generic = generic_rolling_supersized_folder(all_crm3_paths(source))
        if generic:
            return generic
        if not is_themed_crm3_path(art):
            return art
    texts = [update.get("text_body") or "" for update in source.get("updates") or []]
    for subitem in source.get("subitems") or []:
        texts.extend(update.get("text_body") or "" for update in subitem.get("updates") or [])
    for text in texts:
        paths = prefer_generic_crm3_paths(crm3_paths_in_text(text), row)
        for line in paths:
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


def is_ads_po_source(source: dict[str, Any]) -> bool:
    name = (source.get("name") or "").lower()
    return "po ads" in name or "ads po" in name


def is_themed_crm3_path(path: str) -> bool:
    lowered = path.lower().replace("/", "\\")
    if "holidays & events" in lowered or "holidays\\ events" in lowered:
        return True
    compact = re.sub(r"[^a-z0-9]+", "_", lowered)
    for token in THEMED_CRM3_TOKENS:
        t = re.sub(r"[^a-z0-9]+", "_", token.lower())
        if t in compact:
            return True
    if re.search(r"\\20\d{2}_[01]\d_[01]\d_", lowered):
        # Date-stamped feature folders on holiday promos — treat as themed when under Events
        if "events" in lowered or "holiday" in lowered:
            return True
    return False


def themed_path_matches_mm_theme(path: str, row: dict[str, str]) -> bool:
    theme = (promo_theme_label(row) or "").lower()
    if not theme or theme == "generic":
        return False
    p = path.lower()
    checks = {
        "4th of july": ("july", "4th", "independence"),
        "betty boop": ("betty", "boop"),
        "valentine": ("valentine",),
        "easter": ("easter",),
        "halloween": ("halloween",),
        "thanksgiving": ("thanksgiving",),
        "christmas": ("christmas", "xmas"),
        "cozy": ("cozy",),
        "wonder": ("wonder",),
    }
    for key, needles in checks.items():
        if key in theme or theme in key:
            return any(n in p for n in needles)
    return theme.replace(" ", "_") in p.replace("-", "_").replace(" ", "_")


def mm_allows_themed_crm3_reference(row: dict[str, str] | None) -> bool:
    if not row or row["label"] != "New theme for promo":
        return False
    theme = promo_theme_label(row)
    return bool(theme and theme.lower() != "generic")


def prefer_generic_crm3_paths(
    paths: list[str],
    row: dict[str, str] | None,
) -> list[str]:
    if not paths:
        return paths
    if row and mm_allows_themed_crm3_reference(row):
        matched = [p for p in paths if is_themed_crm3_path(p) and themed_path_matches_mm_theme(p, row)]
        generic = [p for p in paths if not is_themed_crm3_path(p)]
        other_themed = [p for p in paths if is_themed_crm3_path(p) and p not in matched]
        return matched + generic + other_themed
    generic = [p for p in paths if not is_themed_crm3_path(p)]
    themed = [p for p in paths if is_themed_crm3_path(p)]
    return generic + themed


def score_daily_deal_path(path: str) -> int:
    lowered = path.lower()
    score = 0
    for hint in GENERIC_DAILY_DEAL_PATH_HINTS:
        if hint in lowered:
            score += 10
    if is_themed_crm3_path(path):
        score -= 50
    if "features\\daily_deal" in lowered.replace("/", "\\"):
        score += 2
    return score


def is_non_ads_po_crm3_path(path: str) -> bool:
    lowered = path.lower()
    if "rewarded_video" in lowered.replace("\\", "/"):
        return False
    blocked = (
        "/rooc",
        "\\rooc",
        "/personal_offer",
        "\\personal_offer",
        "/double_po",
        "\\double_po",
        "holidays & events",
    )
    return any(token in lowered for token in blocked)


def generic_rolling_supersized_folder(paths: list[str]) -> str:
    for path in paths:
        if "supersized_wins_x_ro" in path.lower().replace("\\", "/"):
            return crm3_path_to_folder(path)
    return ""


def crm3_folder_path(
    source: dict[str, Any],
    asset_name: str | None = None,
    row: dict[str, str] | None = None,
) -> str:
    if is_ads_po_source(source):
        art = source.get("art_link") or ""
        if art and "Rewarded_Video" in str(art):
            return crm3_asset_folder(str(art), asset_name)
        paths = all_crm3_paths(source, asset_name)
        for path in paths:
            if "Rewarded_Video" in path:
                return crm3_asset_folder(crm3_path_to_folder(path), asset_name)
        filtered = [path for path in paths if not is_non_ads_po_crm3_path(path)]
        folders = [crm3_path_to_folder(path) for path in filtered]
        if folders:
            return folders[0]
    if "supersized" in (source.get("name") or "").lower():
        paths = all_crm3_paths(source, asset_name)
        generic = generic_rolling_supersized_folder(paths)
        if generic:
            return crm3_asset_folder(generic, asset_name)
    if family(source.get("name") or "") == "piggy" or piggy_break_ref_folder(source):
        piggy_base = piggy_break_ref_folder(source) or PIGGY_BREAK_REF_FOLDER
        return crm3_asset_folder(piggy_base, asset_name)
    if family(source.get("name") or "") == "spinner clash":
        return crm3_asset_folder(SPINNER_REF_BASE, asset_name)
    row_fam = family(row["name"]) if row else ""
    source_fam = family(source.get("name") or "")
    if row_fam == "daily deal" or source_fam == "daily deal":
        paths = all_crm3_paths(source, asset_name)
        dd_paths = [
            p
            for p in paths
            if "daily_deal" in p.lower().replace("\\", "/")
        ]
        candidates = prefer_generic_crm3_paths(dd_paths or paths, row)
        candidates.sort(key=score_daily_deal_path, reverse=True)
        allowed = [
            p
            for p in candidates
            if not is_themed_crm3_path(p)
            or (
                row
                and mm_allows_themed_crm3_reference(row)
                and themed_path_matches_mm_theme(p, row)
            )
        ]
        pick = allowed[0] if allowed else ""
        if not pick and candidates and row and not mm_allows_themed_crm3_reference(row):
            pick = ""  # force fallback below
        elif not pick and candidates:
            pick = candidates[0]
        if pick:
            return crm3_asset_folder(crm3_path_to_folder(pick), asset_name)
        if row and not mm_allows_themed_crm3_reference(row):
            return crm3_asset_folder(GENERIC_DD_HAMMER_WHEEL_FOLDER, asset_name)
        if source.get("art_link"):
            art = str(source["art_link"])
            if not is_themed_crm3_path(art) or (row and mm_allows_themed_crm3_reference(row)):
                return crm3_asset_folder(art, asset_name)
    paths = prefer_generic_crm3_paths(all_crm3_paths(source, asset_name), row)
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
    paths = prefer_generic_crm3_paths(all_crm3_paths(source), row)
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
        art = str(source["art_link"])
        if not is_themed_crm3_path(art) or (row and mm_allows_themed_crm3_reference(row)):
            return crm3_asset_folder(art, asset_name)
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
    row: dict[str, str] | None = None,
) -> str:
    if folder_only:
        try:
            folder = crm3_folder_path(source, asset_name, row=row)
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
        return f"<code>{esc(source_reference_path(source, row))}</code>"
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
    folder_override = REUSE_REFERENCE_FOLDER_OVERRIDES.get(row["id"])
    if folder_override:
        link = f"<code>{esc(folder_override)}</code>"
    else:
        try:
            link = reference_link_html(source, folder_only=True)
        except RuntimeError:
            link = "No exact Creative reference found — prior live date confirmed."
    reference = reference_png_html(source)
    if folder_override and reference and re.search(r"rooc|easter_rolling", reference, re.I):
        reference = ""
    return {
        "date": source_date(source),
        "reference": reference,
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
        if "mgap" in key and "denom" in key:
            return (5, index)
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
    name = normalize_name(row["name"])
    fam = family(row["name"])
    if fam in {"battlesheep", "blast"} and not mm_defines_season_challenge(row):
        name = re.sub(r"\bbattlesheep\s+challenge\b", "Battlesheep", name, flags=re.I)
        name = re.sub(r"\bblast\s+challenge\b", "Blast", name, flags=re.I)
        name = re.sub(r"\s+challenge\b", "", name, flags=re.I)
        name = re.sub(r"\s+", " ", name).strip(" -|")
    return name


def is_short_term_season_promo(row: dict[str, str]) -> bool:
    return family(row["name"]) in {"battlesheep", "blast"}


def mm_defines_season_challenge(row: dict[str, str]) -> bool:
    """True only when MM Calendar *description* defines a season challenge mechanic.

    Product titles like \"Battlesheep Challenge\" do not count — ignore the promo name.
    """
    if not is_short_term_season_promo(row):
        return False
    desc = sanitized_description(row)
    if not desc.strip():
        return False
    patterns = (
        r"season\s+(?:long\s+)?challenge",
        r"every\s+\d+(?:st|nd|rd|th)?\s+ship",
        r"sink\s+\d+\s+ships?",
        r"\d+\s+days?\s+full?\s+launch",
        r"complete\s+(?:the\s+)?season\s+challenge",
        r"find\s+skus?\s+behind",
        r"ships?\s+you\s+sink",
        r"journey\s+inapp.*challenge|challenge.*journey",
        r"wheel\s+ui.*challenge|challenge.*wheel",
    )
    for pattern in patterns:
        if re.search(pattern, desc, re.I):
            return True
    if re.search(r"\bchallenge\b", desc, re.I) and re.search(
        r"season|ship|sku|sink|wheel|journey|wedge",
        desc,
        re.I,
    ):
        return True
    return False


def season_reward_sku(row: dict[str, str]) -> str:
    """Visible season SKU for challenge weeks only (from MM name)."""
    if not mm_defines_season_challenge(row):
        return ""
    name = normalize_name(row["name"])
    if "|" in name:
        head = name.split("|", 1)[0].strip()
        head = re.sub(r"^(?:battlesheep|blast)\s*[-–—]\s*", "", head, flags=re.I).strip()
        if head and head.lower() not in {"battlesheep", "blast"}:
            return head
    for part in name.split("|"):
        part = part.strip()
        if re.search(r"\b(?:wild|gold|reg|ace|pack|parasheep|airstrike|superboom|pab)\b", part, re.I):
            if "theme" not in part.lower():
                return part
    return ""


def promo_is_decoy_offer(row: dict[str, str]) -> bool:
    blob = f"{normalize_name(row['name'])}\n{row.get('description') or ''}".lower()
    return bool(re.search(r"\bdecoy\b|\bbonanza\b|triple offer", blob))


def calendar_active_brief_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Actionable MM rows for Monetization-Art (excludes Reuse and Decoy offers)."""
    return [
        row
        for row in rows
        if row["label"] != "Reuse" and not promo_is_decoy_offer(row)
    ]


def is_decoy_structure_subitem(name: str) -> bool:
    key = normalize_subitem_key(name)
    if "decoy" in key:
        return True
    if re.match(r"^denom\s*[23]$", key):
        return True
    if key in {"big denom", "coupon inapp", "denom buy", "denom free"}:
        return True
    return False


def is_challenge_only_subitem(name: str, row: dict[str, str]) -> bool:
    if not is_short_term_season_promo(row) or mm_defines_season_challenge(row):
        return False
    key = normalize_subitem_key(name)
    if "theme" in key and ("bo" in key or "background" in key):
        return True
    if "journey" in key and "inapp" in key:
        return True
    if "wheel" in key and "ui" in key:
        return True
    if key in {"wedges", "theme/bo", "theme / bo"}:
        return True
    return False


def status_mm_label(row: dict[str, str]) -> str:
    if row["label"] == "New promo":
        return STATUS_MM_NEW_PROMO_SKELETON
    return STATUS_MM_READY_FOR_BRIEF


def status_mm_column_value(label: str) -> dict[str, Any]:
    index = STATUS_MM_INDEX.get(label)
    if index is not None:
        return {"index": index}
    return {"label": label}


def assignment_values(assignment: dict[str, Any]) -> dict[str, Any]:
    artist_ids, copywriter_ids = normalized_traffic_people(assignment)
    return {
        "date_mkwj8wwp": {"date": assignment["brief_date"]},
        "multiple_person_mkwetsg8": people_value(artist_ids),
        "multiple_person_mkwev9a5": people_value(copywriter_ids),
        "person": people_value(assignment["mm_ids"]),
        "multiple_person_mkwetd0y": people_value(assignment["mm_tl_ids"]),
        "multiple_person_mkwez377": people_value(assignment["creative_tl_ids"]),
    }


def apply_traffic_people_columns(item_id: str, assignment: dict[str, Any]) -> None:
    """Overwrite Artist/Copywriter; duplicated templates often copy both onto Artist."""
    artist_ids, copywriter_ids = normalized_traffic_people(assignment)
    empty_people = {
        "multiple_person_mkwetsg8": people_value([]),
        "multiple_person_mkwev9a5": people_value([]),
    }
    set_columns(BOARD, item_id, empty_people)
    time.sleep(0.15)
    set_columns(
        BOARD,
        item_id,
        {
            **assignment_values(assignment),
            "multiple_person_mkwetsg8": people_value(artist_ids),
            "multiple_person_mkwev9a5": people_value(copywriter_ids),
        },
    )


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
        STATUS_CREATIVE_COLUMN: None,
        STATUS_MM_COLUMN: status_mm_column_value(status_mm_label(row)),
        **assignment_values(assignment),
    }


def reuse_values(target: str, assignment: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": REUSE_TASK_NAME,
        "date4": {"date": target},
        "color_mkws3h8e": {"label": "Low"},
        STATUS_CREATIVE_COLUMN: {"label": "done"},
        STATUS_MM_COLUMN: status_mm_column_value(STATUS_MM_REUSE),
        **assignment_values(assignment),
    }


def sanitized_description(row: dict[str, str]) -> str:
    """Drop wrong MM boilerplate (e.g. Golden Spin mislabeled as timed gem)."""
    raw = row.get("description") or ""
    if family(row["name"]) != "golden spin":
        return raw
    kept: list[str] = []
    for line in raw.splitlines():
        if re.search(
            r"timed gem|gem feature|gem machine|2h post 12:00|time-limited \(post",
            line,
            re.I,
        ):
            continue
        kept.append(line)
    return "\n".join(kept)


def promo_theme_label(row: dict[str, str]) -> str:
    """Theme from MM name/description only; empty when not explicitly stated."""
    name = normalize_name(row["name"])
    desc = sanitized_description(row)
    blob = f"{name}\n{desc}"
    if re.search(r"\b(?:generic|gemeric)\s+theme\b", blob, re.I):
        return "Generic"
    match = re.search(r"\|\s*([^|]+?)\s+theme\s*$", name, re.I)
    if match:
        segment = match.group(1).strip()
        if "|" in segment:
            segment = segment.rsplit("|", 1)[-1].strip()
        if segment.lower() not in ("generic", "gemeric"):
            return re.sub(r"\s+theme$", "", segment, flags=re.I).strip() or segment
    match = re.search(r"\|\s*([^|]+?)\s+Theme\s*$", name)
    if match:
        return match.group(1).strip()
    for line in desc.splitlines():
        theme_match = re.match(r"^Theme:\s*(.+)$", line.strip(), re.I)
        if theme_match:
            val = theme_match.group(1).strip()
            if val.lower() in ("generic", "gemeric"):
                return "Generic"
            return val
    if re.search(r"\bcozy\b", name, re.I) and re.search(r"\bblast\b", name, re.I):
        return "Cozy"
    return ""


def promo_hook_line(row: dict[str, str]) -> str | None:
    """Player-facing hook from MM name/description; None when nothing distinct."""
    name = normalize_name(row["name"])
    desc = sanitized_description(row)
    blob = f"{name}\n{desc}".lower()
    fam = family(row["name"])

    if fam == "golden spin":
        for part in name.split("|"):
            part = part.strip()
            if re.match(r"golden\s*spin", part, re.I):
                continue
            if re.search(r"\btheme\s*$", part, re.I):
                continue
            pct_bigger = re.search(r"(\d+%\s*Bigger)", part, re.I)
            if pct_bigger:
                return f"{pct_bigger.group(1).title()} Wedges"
            if re.search(r"bigger\s+multipliers", part, re.I):
                return "Bigger Multipliers"
        if re.search(r"extra\s+black\s+wedge", blob):
            return "Extra Black Wedge"
        if re.search(r"gold\s+cards?\s+on\s+wedges", blob):
            return "Gold Cards on Wedges"
        if re.search(r"bigger\s+multipliers", blob):
            return "Bigger Multipliers"
        return None

    if re.search(r"\bbogo\b", blob):
        return "BOGO"

    if re.search(r"supersiz(ed|e)", blob):
        return "Supersized Wins" if "win" in blob else "Supersized"

    if re.search(r"bigger\s+multipliers", blob):
        return "Bigger Multipliers"

    if fam == "rolling" and rolling_has_mgap_ladder(row):
        hint = rolling_mgap_denom_hint(row)
        return f"{hint} ladder" if hint else "MGAP ladder"

    if re.search(r"\bx1000\b", name, re.I):
        return "X1000"

    return None


def concise_requirement(row: dict[str, str]) -> str:
    title = normalize_name(row["name"])
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in sanitized_description(row).splitlines()
    ]
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
    if family(row["name"]) == "golden spin":
        name = normalize_name(row["name"])
        tail = name.split("|", 1)[-1].strip() if "|" in name else name
        tail = re.sub(r"\s*\|\s*[^|]+\s+theme\s*$", "", tail, flags=re.I).strip()
        if tail.lower().startswith("golden spin"):
            tail = re.sub(r"^golden spin\s*[-–—|]\s*", "", tail, flags=re.I).strip()
        return tail or name
    if family(row["name"]) == "daily deal":
        title = normalize_name(row["name"])
        if " - " in title:
            tail = title.split(" - ", 1)[1]
            tail = re.sub(r"\s*\|\s*H Pricing\s*$", "", tail, flags=re.I)
            if tail:
                return tail.strip()
        for line in row.get("description", "").splitlines():
            if re.search(r"central reward|100%|hammer", line, re.I):
                match = re.search(r":\s*(.+)$", line.strip())
                if match:
                    return re.sub(
                        r"\s*\([^)]*\)\s*$",
                        "",
                        match.group(1).strip(),
                    )
    if family(row["name"]) == "piggy":
        if "2 PAB" in normalize_name(row["name"]).upper():
            return "2 PAB"
    fam = family(row["name"])
    if fam in {"battlesheep", "blast"}:
        name = normalize_name(row["name"])
        head = name.split("|", 1)[0].strip()
        head = re.sub(r"^(?:battlesheep|blast)\s*[-–—]\s*", "", head, flags=re.I).strip()
        head = re.sub(r"\s+challenge\s*$", "", head, flags=re.I).strip()
        if head and head.lower() not in {"battlesheep", "blast"}:
            return head
    for line in sanitized_description(row).splitlines():
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
    if req == "inapp" and cur == "inapp":
        return True
    if req == "inapp" and cur.startswith("main") and "inapp" in cur and "winner" not in cur:
        return True
    if req == "mgap denom" and "mgap" in cur and "denom" in cur and "buy" not in cur:
        return True
    return False


def spinner_rank_prize_lines(row: dict[str, str]) -> list[str]:
    lines: list[str] = []
    for raw in (row.get("description") or "").splitlines():
        stripped = raw.strip()
        match = re.match(
            r"^(\d+(?:st|nd|rd|th))\s*:\s*(.+)$",
            stripped,
            re.I,
        )
        if match:
            lines.append(f"{match.group(1)}: {match.group(2).strip()}")
    return lines


def daily_deal_reward_blob(row: dict[str, str]) -> str:
    return f"{normalize_name(row['name'])}\n{row.get('description') or ''}".lower()


def daily_deal_has_sb_and_hammers(row: dict[str, str]) -> bool:
    """DD store + inapp hub when both SB and hammers are in the offer (Itay)."""
    blob = daily_deal_reward_blob(row)
    has_sb = bool(re.search(r"\b\d+%\s*sb\b|\b100%\s*sb\b|\bsb\b", blob))
    has_hammers = bool(re.search(r"\b\d+\s*hammers?\b|\bhammer\b", blob))
    return has_sb and has_hammers


def rolling_promo_blob(row: dict[str, str]) -> str:
    return f"{normalize_name(row['name'])}\n{sanitized_description(row)}".lower()


def rolling_has_mgap_ladder(row: dict[str, str]) -> bool:
    blob = rolling_promo_blob(row)
    return "mgap" in blob and ("ladder" in blob or "denom" in blob)


def rolling_mgap_denom_hint(row: dict[str, str]) -> str:
    desc = sanitized_description(row) or row.get("description") or ""
    match = re.search(
        r"mgap:\s*denom\s*(\d+)(?:\s*only)?(?:\s*[·•-]\s*(cycles?\s*[\d\s–—\-]+))?",
        desc,
        re.I,
    )
    if match:
        denom = match.group(1)
        cycles = (match.group(2) or "").strip()
        if cycles:
            return f"MGAP denom {denom} ({cycles})"
        return f"MGAP denom {denom}"
    if rolling_has_mgap_ladder(row):
        return "MGAP denom"
    return ""


def is_rolling_buy_denom_subitem(name: str) -> bool:
    """Buy/Free denom slots — never auto-brief on Rolling (Itay)."""
    key = normalize_subitem_key(name)
    if "buy" in key and "denom" in key:
        return True
    if "free" in key and "denom" in key and "mgap" not in key:
        return True
    if key in {
        "denom buy",
        "denom buy/free",
        "denom free",
        "buy denom",
        "free denom",
        "denoms",
    }:
        return True
    return False


def asset_is_rolling_mgap_denom(asset: str) -> bool:
    key = normalize_subitem_key(asset)
    return "mgap" in key and "denom" in key


def infer_source_theme_name(source: dict[str, Any]) -> str:
    name = normalize_name(source.get("name") or "")
    for label in (
        "4th of July",
        "Valentine",
        "Easter",
        "Halloween",
        "Thanksgiving",
        "Betty Boop",
        "Generic",
        "Wonder",
        "Cozy",
    ):
        if label.lower() in name.lower():
            return label
    if " - " in name:
        tail = name.split(" - ", 1)[-1].strip()
        if len(tail) <= 45 and not re.search(r"^\d+\s*cycles?", tail, re.I):
            return tail
    return ""


def rolling_cycle_mechanic_clause(row: dict[str, str]) -> str:
    name = strip_pricing_prose(normalize_name(row["name"]))
    match = re.search(r"(\d+)\s*cycles?", name, re.I)
    if match:
        return f"{match.group(1)} cycles Buy X Get Y"
    return ""


def rolling_cycle_pricing_clause(row: dict[str, str]) -> str:
    """Deprecated alias — pricing must not appear in Creative briefs."""
    return rolling_cycle_mechanic_clause(row)


def short_parent_change(row: dict[str, str], source: dict[str, Any]) -> str:
    """One short creative-visible delta for parent Change — never MM Description dumps."""
    fam = family(row["name"])
    if fam == "rolling":
        parts: list[str] = []
        src_theme = infer_source_theme_name(source)
        dst_theme = promo_theme_label(row) or (
            "Generic" if row["label"] == "New theme for promo" else ""
        )
        if row["label"] == "New theme for promo" and (src_theme or dst_theme):
            parts.append(f"Theme: {src_theme or 'prior'} → {dst_theme or 'required theme'}")
        elif row["label"] == "Prize Change":
            ref = inferred_reference_prize(source)
            req = required_prize_from_row(row)
            if ref and req and len(req) <= 72:
                parts.append(f"{ref} → {req}")
        if rolling_has_mgap_ladder(row):
            hint = rolling_mgap_denom_hint(row) or "MGAP denom"
            parts.append(f"Add {hint} on Rolling ladder")
        cycle_clause = rolling_cycle_pricing_clause(row)
        if cycle_clause and not any("cycles" in part for part in parts):
            parts.append(cycle_clause)
        if parts:
            return strip_pricing_prose("; ".join(parts))[:220]
        return "Rolling offer creative update"

    if fam == "golden spin" and row["label"] == "New theme for promo":
        src = infer_source_theme_name(source) or "prior theme"
        dst = promo_theme_label(row) or "required theme"
        line = f"Theme: {src} → {dst}"
        hook = promo_hook_line(row)
        if hook:
            line = f"{line}; {hook}"
        return strip_pricing_prose(line)[:220]

    if row["label"] == "New theme for promo":
        src = infer_source_theme_name(source) or normalize_name(source.get("name") or "")[:35]
        dst = promo_theme_label(row) or "required theme"
        return strip_pricing_prose(f"Theme: {src} → {dst}")[:220]

    if row["label"] == "New promo":
        title = brief_display_name(row).split("|", 1)[0].strip()
        return strip_pricing_prose(
            f"New promo — Itay to complete mechanic and art direction ({title})."
        )[:220]

    if row["label"] == "Prize Change" and fam == "golden spin":
        hook = promo_hook_line(row)
        dst = promo_theme_label(row)
        if hook and dst:
            return strip_pricing_prose(f"Theme: → {dst}; {hook}")[:220]
        if hook:
            return strip_pricing_prose(hook)[:220]

    if fam in {"battlesheep", "blast"}:
        req = required_prize_from_row(row)
        theme = promo_theme_label(row)
        if row["label"] == "New theme for promo" and theme:
            src = infer_source_theme_name(source) or "prior theme"
            return strip_pricing_prose(f"Theme: {src} → {theme}")[:220]
        if req and len(req) <= 80:
            if theme:
                return strip_pricing_prose(f"{req} · {theme} theme")[:220]
            return strip_pricing_prose(req)[:220]
        if theme:
            return strip_pricing_prose(f"{theme} theme")[:220]

    return ""


def playbook_required_subitems(row: dict[str, str]) -> list[str]:
    if row["label"] not in {"Prize Change", "New theme for promo", "New promo"}:
        return []
    fam = family(row["name"])
    winners: list[str] = []
    if fam == "piggy":
        winners = ["Winners Inapp"]
    if fam == "spinner clash":
        return ["Main Inapp", "Journey Inapp", "Banner"]
    if fam == "piggy":
        return ["Main Inapp", *winners, "Banner"]
    if fam == "daily deal":
        if daily_deal_has_sb_and_hammers(row):
            return ["store denom", "Inapp"]
        return ["store denom"]
    if fam == "rolling":
        subs = ["Background", "Banner"]
        if rolling_has_mgap_ladder(row):
            subs.append("MGAP denom")
        return subs
    if fam in {"battlesheep", "blast"}:
        if mm_defines_season_challenge(row):
            return [
                "Main Inapp",
                "Theme/BO",
                "Journey Inapps",
                "Banner",
                "Winners Inapp",
            ]
        return ["Main Inapp", "Banner", "Winners Inapp"]
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


def prune_non_playbook_subitems(
    parent_id: str,
    row: dict[str, str],
    subitems: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    required = playbook_required_subitems(row)
    if not required:
        return subitems
    kept: list[dict[str, Any]] = []
    for subitem in subitems:
        if family(row["name"]) == "rolling" and is_rolling_buy_denom_subitem(subitem["name"]):
            delete_item(str(subitem["id"]))
            print(
                f"REMOVED {parent_id} subitem {subitem['name']!r} "
                "(Rolling: no Buy/Free denom in scope)"
            )
            time.sleep(0.25)
            continue
        if is_challenge_only_subitem(subitem["name"], row):
            delete_item(str(subitem["id"]))
            print(
                f"REMOVED {parent_id} subitem {subitem['name']!r} "
                "(no MM season challenge — challenge assets out of scope)"
            )
            time.sleep(0.25)
            continue
        if promo_is_decoy_offer(row) or (
            not promo_is_decoy_offer(row) and is_decoy_structure_subitem(subitem["name"])
        ):
            if is_decoy_structure_subitem(subitem["name"]):
                delete_item(str(subitem["id"]))
                print(
                    f"REMOVED {parent_id} subitem {subitem['name']!r} "
                    "(single-offer brief — no decoy/multi-denom structure)"
                )
                time.sleep(0.25)
                continue
        if any(subitem_matches(name, subitem["name"]) for name in required):
            kept.append(subitem)
            continue
        delete_item(str(subitem["id"]))
        print(f"REMOVED {parent_id} subitem {subitem['name']!r} (not in playbook scope)")
        time.sleep(0.25)
    return kept


def spinner_prize_lines(row: dict[str, str]) -> list[str]:
    return spinner_rank_prize_lines(row)


def change_summary(row: dict[str, str], source: dict[str, Any]) -> str:
    if row["label"] == "New promo":
        short = short_parent_change(row, source)
        if short:
            return short
    if row["label"] == "New theme for promo":
        short = short_parent_change(row, source)
        if short:
            return short
    if family(row["name"]) == "rolling":
        short = short_parent_change(row, source)
        if short:
            return short
    if row["label"] == "Prize Change" and family(row["name"]) == "piggy":
        ref_prize = inferred_reference_prize(source) or "prior break prize"
        return strip_pricing_prose(
            f"Break prize: {ref_prize} → {required_prize_from_row(row)}"
        )
    if row["label"] == "Prize Change":
        ref_prize = inferred_reference_prize(source)
        req = required_prize_from_row(row)
        if family(row["name"]) == "spinner clash":
            prizes = spinner_rank_prize_lines(row)
            if prizes:
                return strip_pricing_prose(" · ".join(prizes))
        if ref_prize and req and len(req) <= 72:
            return strip_pricing_prose(f"{ref_prize} → {req}")
        if req and len(req) <= 72:
            return strip_pricing_prose(req)
    src_name = strip_pricing_prose(normalize_name(source.get("name") or "")[:40])
    dst_name = strip_pricing_prose(normalize_name(row["name"]).split("|")[0].strip()[:40])
    return strip_pricing_prose(f"{src_name} → {dst_name}")


def numbered_steps_html(steps: list[str]) -> str:
    items = "".join(f"<li><p>{esc(step)}</p></li>" for step in steps)
    return f"<ol>{items}</ol>"


def asset_is_background(asset: str) -> bool:
    key = normalize_subitem_key(asset)
    if key in {"background", "bg", "theme/bo", "theme / bo"}:
        return True
    return "background" in key or key.startswith("theme/")


def asset_is_banner(asset: str) -> bool:
    key = normalize_subitem_key(asset)
    return "banner" in key and "pp banner" not in key


def display_change_summary(row: dict[str, str], source: dict[str, Any]) -> str:
    """Short delta for subitem copy — never MM Description dumps."""
    short = short_parent_change(row, source)
    if short:
        return short
    return change_summary(row, source)


def theme_hook_lines(row: dict[str, str], source: dict[str, Any], asset: str) -> list[str]:
    """Plain-language theme/hook instructions for Background and similar assets."""
    theme = promo_theme_label(row)
    title = normalize_name(row["name"]).lower()
    asset_l = asset.lower()
    hook = promo_hook_line(row)

    if "mgap" in title and "rolling" in title and asset_is_background(asset):
        return ["Make the MGAP ladder the main visual hook of this Rolling offer."]

    if row["label"] == "New theme for promo" and (
        asset_is_background(asset) or asset_is_banner(asset) or "theme" in asset_l
    ):
        lines: list[str] = []
        if theme:
            lines.append(f"Reskin this {asset} to the {theme} theme.")
        else:
            lines.append(f"Reskin this {asset} to the required theme.")
        if hook and family(row["name"]) == "golden spin":
            lines.append(f"Show hook on wheel/arena: {hook}.")
        elif family(row["name"]) == "rolling":
            lines.append("Keep Buy X Get Y Rolling layout visible.")
        return lines

    if row["label"] == "New theme for promo" and family(row["name"]) == "golden spin":
        if theme and hook:
            return [f"Apply {theme} theme to Golden Spin {asset}.", f"Hook: {hook}."]
        if theme:
            return [f"Apply {theme} theme to Golden Spin {asset}."]
        return [f"Apply required theme to Golden Spin {asset}."]

    return []


def what_to_change_lines(row: dict[str, str], source: dict[str, Any], asset: str) -> list[str]:
    req = required_prize_from_row(row)
    ref_prize = inferred_reference_prize(source) or "prior prize"
    asset_l = asset.lower()
    fam = family(row["name"])

    hook = theme_hook_lines(row, source, asset)
    if hook:
        return hook

    if row["label"] == "New promo":
        return [
            f"Itay must complete mechanic, prizes, and format for {normalize_name(row['name'])}.",
            f"This asset: {asset}.",
        ]

    if fam == "piggy" and "winner" in asset_l:
        return [
            f"Show break payout: {req}.",
            "Match PAB art from Main Inapp.",
        ]
    if fam == "piggy" and "inapp" in asset_l and "winner" not in asset_l:
        return [f"Break prize: {ref_prize} → {req}."]
    if fam == "piggy" and "banner" in asset_l:
        return [f"Banner prize: {ref_prize} → {req}."]

    if fam == "spinner clash":
        ranks = spinner_rank_prize_lines(row)
        if ranks:
            if "banner" in asset_l:
                return [f"Banner — {line}" for line in ranks]
            return [f"Show {line}" for line in ranks]
        return [f"Update rank prizes to: {req}."]

    if fam in {"battlesheep", "blast"}:
        if "winner" in asset_l:
            return [f"Show season payout: {req}."]
        if "banner" in asset_l:
            return [f"Show {req} on banner."]
        if "main" in asset_l:
            return [f"Show {req} on main inapp."]
        if mm_defines_season_challenge(row) and "journey" in asset_l:
            return ["Update journey frames for the season challenge progress."]
        if mm_defines_season_challenge(row) and asset_is_background(asset):
            return ["Update Theme/BO for the season challenge."]
        return [f"Update {req} on {asset}."]

    if fam == "daily deal":
        if "inapp" in asset_l and "winner" not in asset_l and "journey" not in asset_l:
            return [f"Inapp reward: {req}."]
        if "dd" in asset_l or "store" in asset_l or "denom" in asset_l:
            return [f"Store reward: {req}."]

    if fam == "rolling":
        if is_rolling_buy_denom_subitem(asset):
            return []
        if asset_is_rolling_mgap_denom(asset) or (
            normalize_subitem_key(asset) == "mgap denom"
        ):
            hint = rolling_mgap_denom_hint(row) or "MGAP denom"
            return [f"Build {hint} — new for this Rolling promo."]
        if asset_is_banner(asset):
            if row["label"] == "Prize Change":
                ref = inferred_reference_prize(source) or "prior"
                req = required_prize_from_row(row)
                if len(req) <= 72:
                    return [f"Update visible Rolling prizes on banner: {ref} → {req}."]
            theme = promo_theme_label(row)
            if theme:
                return [f"Reskin Rolling banner to {theme} theme."]
            return ["Update Rolling banner for this promo."]
        if asset_is_background(asset):
            hook = theme_hook_lines(row, source, asset)
            if hook:
                return hook
            return ["Update Rolling background for this promo."]

    change = change_summary(row, source)
    if asset_is_background(asset) or asset_is_banner(asset):
        if row["label"] == "Prize Change":
            return [f"Update {asset}: {change}."]
    return [f"Update {asset} for: {change}."]


def reference_cell_html(source: dict[str, Any], asset: str) -> str:
    """Reference row: embedded preview only — no prose (Itay)."""
    return reference_png_html(source, asset) or "<p></p>"


def reference_label_html(
    source: dict[str, Any],
    asset: str,
    row: dict[str, str] | None = None,
) -> str:
    ref_date = source_date(source)
    if row and family(row["name"]) == "piggy":
        return esc(f"2026-06-17 Piggy break 5 Hammers — {asset}")
    if row and family(row["name"]) == "spinner clash":
        return esc(f"{ref_date} Spinner Clash — {asset}")
    name = normalize_name(source.get("name") or "")
    return esc(f"{ref_date} {name} — {asset}")


def parent_body(row: dict[str, str], source: dict[str, Any], assets: list[str]) -> str:
    del assets
    rows: list[tuple[str, str]] = [
        ("Creative Label", esc(row["label"])),
        ("Change", esc(change_summary(row, source))),
    ]
    theme = promo_theme_label(row)
    if theme:
        rows.append(("Theme", esc(theme)))
    hook = promo_hook_line(row)
    if hook:
        rows.append(("Hook", esc(hook)))
    return table(rows)


def subitem_body(row: dict[str, str], source: dict[str, Any], asset: str) -> str:
    reference_cell = reference_cell_html(source, asset)
    link_cell = reference_link_html(
        source,
        asset,
        allow_missing_path=row["label"] == "New promo",
        folder_only=row["label"] in {"Prize Change", "New theme for promo", "New promo"},
        row=row,
    )
    if row["label"] == "New promo":
        return new_promo_subitem_table(asset, reference_cell, link_cell)
    lines = what_to_change_lines(row, source, asset)
    if not lines:
        lines = [f"Update {asset} per parent Change."]
    theme = promo_theme_label(row)
    sku = season_reward_sku(row) if mm_defines_season_challenge(row) else ""
    return prize_change_table(
        lines,
        reference_cell,
        link_cell,
        theme=theme,
        hook=promo_hook_line(row),
        sku=sku,
    )


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


def is_monetization_art_brief_item(
    item: dict[str, Any],
    reuse_rows: list[dict[str, str]],
    active_brief_names: set[str],
) -> bool:
    """Art brief parents in a date group (not unrelated comms without subitems)."""
    name = item["name"]
    if name == REUSE_TASK_NAME:
        return True
    if name.startswith("MGAP UI"):
        return True
    if is_old_reuse_item(item, reuse_rows):
        return True
    if name in active_brief_names:
        return True
    if normalize_name(name) in active_brief_names:
        return True
    if item.get("subitems"):
        return True
    return False


def delete_group_art_briefs(
    group_id: str,
    reuse_rows: list[dict[str, str]],
    active_brief_names: set[str],
    allow_in_flight: bool,
) -> int:
    deleted = 0
    for item in items_in_group(group_id):
        if not is_monetization_art_brief_item(item, reuse_rows, active_brief_names):
            continue
        assert_brief_editable(str(item["id"]), allow_in_flight)
        delete_item(str(item["id"]))
        deleted += 1
        print(f"REBUILD deleted {item['id']} {item['name'][:72]}")
    return deleted


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
        STATUS_CREATIVE_COLUMN: None,
        STATUS_MM_COLUMN: status_mm_column_value(STATUS_MM_READY_FOR_BRIEF),
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
    reference_cell = reference_cell_html(source, asset_name)
    link_cell = reference_link_html(source, asset_name, folder_only=True)
    lines = [
        f"Update MGAP UI: {spec['change']}",
        f"Mechanic: {spec['mechanic']}",
    ]
    return prize_change_table(lines, reference_cell, link_cell)


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
    allow_in_flight: bool = False,
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
            if spec.get("skip_brief"):
                reason = spec.get("skip_reason") or "UI already ready"
                existing_item = existing.get(spec["name"])
                if not commit:
                    if existing_item:
                        print(
                            f"{target} DELETE skip_brief: {spec['name']} "
                            f"({reason})"
                        )
                    else:
                        print(f"{target} SKIP brief: {spec['name']} ({reason})")
                    continue
                if existing_item:
                    assert_brief_editable(
                        str(existing_item["id"]),
                        allow_in_flight=allow_in_flight,
                    )
                    delete_item(str(existing_item["id"]))
                    print(
                        f"{target} DELETED {spec['name']} "
                        f"({existing_item['id']}) — {reason}"
                    )
                    existing.pop(spec["name"], None)
                else:
                    print(f"{target} SKIP brief: {spec['name']} ({reason})")
                continue
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
        apply_traffic_people_columns(item_id, assignment)
        time.sleep(3)
    query = "query($ids:[ID!]!){items(ids:$ids){updates(limit:1){id body} subitems{id name updates(limit:1){id body}}}}"
    live_item = gql(query, {"ids": [item_id]})["items"][0]
    subitems = live_item.get("subitems") or []
    if not subitems:
        time.sleep(4)
        live_item = gql(query, {"ids": [item_id]})["items"][0]
        subitems = live_item.get("subitems") or []
    subitems = ensure_playbook_subitems(item_id, row, subitems)
    subitems = prune_non_playbook_subitems(item_id, row, subitems)
    if playbook_required_subitems(row):
        live_item = gql(query, {"ids": [item_id]})["items"][0]
        subitems = live_item.get("subitems") or []
    set_columns(BOARD, item_id, parent_values(row, source, target, assignment))
    apply_traffic_people_columns(item_id, assignment)
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
            args.allow_in_flight,
        )
        if not args.commit:
            print("DRY RUN - no Monday changes made.")
        else:
            print(f"CREATED/SKIPPED {created} standalone MGAP UI task(s).")
        return
    if not args.commit:
        for target in dates:
            reuse_rows = [row for row in rows_by_date[target] if row["label"] == "Reuse"]
            active_rows = calendar_active_brief_rows(rows_by_date[target])
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
            for row in rows_by_date[target]:
                if row["label"] == "Reuse" or not promo_is_decoy_offer(row):
                    continue
                print(f"  SKIP (decoy)        {normalize_name(row['name'])} — single-offer only; no Art brief")
        print("\nStandalone MGAP UI tasks:")
        apply_mgap_ui_tasks(mgap_specs, assignments, groups, catalog, False, False)
        print("\nDRY RUN - no Monday changes made.")
        return
    for target in dates:
        assignment = assignments[target]
        group_id = groups.get(target) or create_group(target)
        reuse_rows = [row for row in rows_by_date[target] if row["label"] == "Reuse"]
        decoy_rows = [
            row
            for row in rows_by_date[target]
            if row["label"] != "Reuse" and promo_is_decoy_offer(row)
        ]
        active_rows = calendar_active_brief_rows(rows_by_date[target])
        active_brief_names = {
            brief_name(row, source_for(row, catalog)) for row in active_rows
        }
        if args.rebuild:
            removed = delete_group_art_briefs(
                group_id,
                reuse_rows,
                active_brief_names,
                args.allow_in_flight,
            )
            print(f"{target} rebuild removed {removed} Monetization-Art brief item(s)")
            time.sleep(2)
        current_items = items_in_group(group_id)

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
        for row in decoy_rows:
            decoy_names = {
                normalize_name(row["name"]),
                brief_name(row, source_for(row, catalog)),
            }
            for decoy_name in decoy_names:
                item = existing.pop(decoy_name, None)
                if not item:
                    continue
                assert_brief_editable(str(item["id"]), args.allow_in_flight)
                delete_item(str(item["id"]))
                print(
                    f"{target} DELETED decoy brief (no Monetization-Art scope): "
                    f"{item['name']} ({item['id']})"
                )
                time.sleep(0.3)
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
                apply_traffic_people_columns(str(existing_item["id"]), assignment)
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
            apply_traffic_people_columns(str(item["id"]), assignment)
            if item["name"] == REUSE_TASK_NAME:
                set_columns(BOARD, str(item["id"]), reuse_values(target, assignment))
                continue
            match = next((row for row in rows_by_date[target] if brief_name(row, source_for(row, catalog)) == item["name"]), None)
            if match:
                set_columns(
                    BOARD,
                    str(item["id"]),
                    {
                        STATUS_CREATIVE_COLUMN: None,
                        STATUS_MM_COLUMN: status_mm_column_value(status_mm_label(match)),
                    },
                )
    apply_mgap_ui_tasks(
        mgap_specs, assignments, groups, catalog, True, args.allow_in_flight
    )
    print(f"CONSOLIDATED Reuse and created/updated {total} active Creative briefs across {len(dates)} dates.")


if __name__ == "__main__":
    main()
