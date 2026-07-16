#!/usr/bin/env python3
"""Build reviewed Ops-task specs from live MM calendar rows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "mm_calendar" / "data" / "monday_board_live_by_date.json"
OUTPUT_DIR = ROOT / "mm_calendar" / "data" / "ops_tasks"
MM_BOARD = "18388590642"
OPS_BOARD = "2109172490"
OPS_SUBITEM_BOARD = "2109172677"
MONDAY_DISPLAY_OFFSET_HOURS = 3

TEMPLATE_GROUPS: dict[str, tuple[str, str]] = {
    "daily deal": ("group_mkv1971m", "Daily Deal"),
    "rolling": ("group_mkv1b6ky", "Rolling Offer"),
    "ryd": ("group_mkv1q8yw", "RYD"),
    "buy all": ("group_mkv12864", "Buy All"),
    "decoy": ("group_mkzvt95x", "Triple Offer - Decoy"),
    "mgap": ("group_mkv1vqxx", "MGAP"),
    "ads": ("group_mm15y5em", "PO ADS"),
}

sys.path.insert(0, str(ROOT / "scripts"))
from monday_client import gql  # noqa: E402
from ops_description import compose_description  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", action="append", required=True, help="YYYY-MM-DD")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--stdout", action="store_true", help="Print JSON; do not write files")
    return parser.parse_args()


def normalize_name(value: str) -> str:
    value = re.sub(r"^\d{4}-\d{2}-\d{2}\s*\|\s*", "", value).strip()
    return re.sub(r"\s+", " ", value.replace("—", "-").replace("–", "-"))


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
        ("win master", ("win master",)),
        ("custom pod", ("custom pod",)),
        ("gems sale", ("gems sale",)),
        ("gems coupon", ("gems coupon", "gem coupon")),
        ("golden spin", ("golden spin",)),
        ("prize mania", ("prize mania",)),
        ("battlesheep", ("battlesheep",)),
        ("shiny show", ("shiny show",)),
        ("ace heist", ("ace heist",)),
        ("lbp", ("lbp", "lotto bonus premium")),
        ("lotto peak", ("lotto peak", "lotto - peak", "lotto — peak")),
        ("snl", ("snl",)),
        ("stickers sources", ("sticker sources", "stickers sources")),
        ("dice deluxe", ("dice deluxe",)),
        ("ryd", ("ryd", "reveal your deal")),
        ("buy all", ("buy all",)),
        ("decoy", ("decoy", "bonanza")),
        ("globez", ("globez",)),
        ("winovate", ("winovate",)),
    ]
    for result, aliases in rules:
        if any(alias in text for alias in aliases):
            return result
    return re.sub(r"[^a-z0-9]+", " ", text).strip().split(" ")[0]


def tokens(value: str) -> set[str]:
    value = normalize_name(value).lower().replace("★", " star ")
    stop = {
        "high", "mid", "low", "price", "pricing", "theme", "generic", "promo",
        "offer", "night", "plan", "peak", "reuse", "from", "the", "with", "and",
    }
    return {
        token
        for token in re.sub(r"[^a-z0-9%×*]+", " ", value).split()
        if token not in stop and len(token) > 1
    }


def similarity(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    return len(a & b) / len(a | b) if a and b else 0.0


def variant_tags(value: str) -> set[str]:
    text = normalize_name(value).lower()
    tags: set[str] = set()
    patterns = {
        "bogo": r"\bbogo\b",
        "bmfl": r"\bbmfl\b|buy more for less",
        "supersized": r"\bsupersized\b",
        "matched": r"\bmatched\b",
        "bigger": r"\bbigger\b|% bigger",
        "golden_balls": r"\bgolden balls?\b",
        "extreme_stamp": r"\bextreme stamps?\b",
        "multiball": r"\bmultiballs?\b",
        "joker": r"\bjoker\b",
        "all_cards": r"\ball cards\b",
        "wild_symbol": r"\bwild symbols?\b",
    }
    for tag, pattern in patterns.items():
        if re.search(pattern, text):
            tags.add(tag)
    cycle = re.search(r"\b([1-6])\s*cycles?\b", text)
    if cycle:
        tags.add(f"cycles_{cycle.group(1)}")
    ball_count = re.search(r"\b([2-6])\s+balls?\b", text)
    if ball_count:
        tags.add(f"balls_{ball_count.group(1)}")
    return tags


def pricing_tag(value: str) -> str:
    text = normalize_name(value).lower()
    match = re.search(r"\b(high|mid|max|low|h|m|l)\s*(?:price|pricing)\b", text)
    if not match:
        return ""
    return {"h": "high", "m": "mid", "l": "low"}.get(match.group(1), match.group(1))


def compatible_variant(current: str, candidate: str, family_name: str) -> bool:
    current_lower = current.lower()
    candidate_lower = candidate.lower()
    if ("internal" in candidate_lower or re.search(r"\bui\b", candidate_lower)) and not (
        "internal" in current_lower or re.search(r"\bui\b", current_lower)
    ):
        return False
    current_tags = variant_tags(current)
    candidate_tags = variant_tags(candidate)
    critical_groups = [
        {"bogo"},
        {"bmfl"},
        {"supersized"},
        {"matched"},
        {"bigger", "golden_balls"},
        {"extreme_stamp"},
        {"multiball"},
        {"joker"},
        {"all_cards"},
        {"wild_symbol"},
    ]
    for group in critical_groups:
        current_values = current_tags & group
        candidate_values = candidate_tags & group
        if current_values != candidate_values:
            return False
    current_cycle = {tag for tag in current_tags if tag.startswith("cycles_")}
    candidate_cycle = {tag for tag in candidate_tags if tag.startswith("cycles_")}
    if current_cycle and current_cycle != candidate_cycle:
        return False
    current_balls = {tag for tag in current_tags if tag.startswith("balls_")}
    candidate_balls = {tag for tag in candidate_tags if tag.startswith("balls_")}
    if current_balls != candidate_balls:
        return False
    current_price, candidate_price = pricing_tag(current), pricing_tag(candidate)
    if current_price and candidate_price and current_price != candidate_price:
        return False
    score = similarity(current, candidate)
    shell_families = {"daily deal", "ryd", "buy all", "ads", "decoy", "win master"}
    threshold = 0.1 if family_name in shell_families else 0.25
    if family_name in {"blast", "snl"}:
        threshold = 0.5
    return score >= threshold


def sanitize_description(value: str) -> str:
    clean_lines: list[str] = []
    for line in value.splitlines():
        if re.search(r"\b20\d{2}-\d{2}-\d{2}\b|\b\d{1,2}:\d{2}\b", line):
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines).strip()


def monday_api_value(day: str, clock: str) -> tuple[str, str]:
    intended = datetime.fromisoformat(f"{day}T{clock}")
    shifted = intended - timedelta(hours=MONDAY_DISPLAY_OFFSET_HOURS)
    return shifted.date().isoformat(), shifted.time().isoformat()


def fetch_live_rows(dates: list[str]) -> dict[str, list[dict[str, Any]]]:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["by_date"]
    ids: list[str] = []
    snapshot_by_id: dict[str, dict[str, Any]] = {}
    for target in dates:
        for row in snapshot.get(target, []):
            if row.get("product") == "Day":
                continue
            ids.append(str(row["id"]))
            snapshot_by_id[str(row["id"])] = row
    query = """
    query($ids:[ID!]!) {
      items(ids:$ids) {
        id name
        column_values(ids:[
          "date_mky27nx7","status","long_text_mkxzgg1v","color_mm4kygty",
          "color_mky9aesm","timerange_mkz3t5qy"
        ]) { id text }
      }
    }
    """
    live: list[dict[str, Any]] = []
    for offset in range(0, len(ids), 20):
        live.extend(gql(query, {"ids": ids[offset:offset + 20]})["items"])
    result = {target: [] for target in dates}
    for item in live:
        columns = {column["id"]: column.get("text") or "" for column in item["column_values"]}
        title_date = item["name"][:10] if re.match(r"^\d{4}-\d{2}-\d{2}", item["name"]) else ""
        live_date = title_date or columns.get("date_mky27nx7")
        if live_date not in result:
            continue
        source = snapshot_by_id.get(str(item["id"]), {})
        description = columns.get("long_text_mkxzgg1v") or source.get("description") or ""
        if str(item["id"]) == "12464458902":
            description = "ADS Personal Offer prize: Hammers. The MM row title is authoritative."
        result[live_date].append(
            {
                "id": str(item["id"]),
                "name": item["name"],
                "product": columns.get("status") or source.get("product") or "",
                "pricing": columns.get("color_mky9aesm") or source.get("pricing") or "",
                "description": description,
                "creative_label": columns.get("color_mm4kygty") or "",
                "config_status": source.get("config_status") or "",
                "timeline": columns.get("timerange_mkz3t5qy") or "",
            }
        )
    return result


def fetch_ops_history() -> list[dict[str, str]]:
    query = """
    query {
      boards(ids:[2109172490]) {
        groups(ids:["group_mm0t6mxh","group_mkzhwecm"]) {
          items_page(limit:500) {
            items {
              name
              subitems {
                id name
                column_values(ids:["long_text"]) { id text }
              }
            }
          }
        }
      }
    }
    """
    history: list[dict[str, str]] = []
    for group in gql(query)["boards"][0]["groups"]:
        for parent in group["items_page"]["items"]:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", parent["name"].strip()):
                continue
            for subitem in parent.get("subitems") or []:
                description = next(
                    (column.get("text") or "" for column in subitem["column_values"] if column["id"] == "long_text"),
                    "",
                )
                history.append(
                    {
                        "date": parent["name"].strip(),
                        "id": str(subitem["id"]),
                        "name": subitem["name"],
                        "description": description,
                    }
                )
    return history


def should_create(row: dict[str, Any]) -> bool:
    name = row["name"].lower()
    if "backup" in name:
        return False
    if row["product"] in {"Clan-Dash", "Extreme stamp"}:
        return False
    if any(term in name for term in ("x2 badges", "x2 dash points", "dash picker")):
        return False
    return True


def is_night_plan(row: dict[str, Any]) -> bool:
    if row.get("night_plan_override"):
        return True
    text = f"{row['name']}\n{row['description']}".lower()
    return "night plan" in text


def template_source(row: dict[str, Any]) -> dict[str, str] | None:
    source = TEMPLATE_GROUPS.get(family(row["name"]))
    if not source:
        return None
    return {"group_id": source[0], "group_title": source[1]}


def range_end(row: dict[str, Any], target: str) -> str:
    match = re.findall(r"\d{4}-\d{2}-\d{2}", row.get("timeline") or "")
    last = match[-1] if match else target
    return (date.fromisoformat(last) + timedelta(days=1)).isoformat()


def status_for(row: dict[str, Any]) -> str:
    if is_night_plan(row):
        return "Night Plan"
    config = row.get("config_status") or ""
    label = row.get("creative_label") or ""
    if config == "MCP needed":
        return "Missing MCP"
    if label in {"New promo", "New theme for promo", "Prize Change"} and config == "Config needed":
        return "Missing Art+Config"
    if label in {"New promo", "New theme for promo", "Prize Change"}:
        return "Missing art"
    if config == "Config needed":
        return "Missing Config"
    if not row.get("description"):
        return "More Info required"
    return "M&M Completed"


def recent_reference(row: dict[str, Any], target: str, history: list[dict[str, str]]) -> tuple[bool, str]:
    start = date.fromisoformat(target)
    month_index = start.year * 12 + start.month - 4
    year, month_zero = divmod(month_index, 12)
    lower = date(year, month_zero + 1, 1).isoformat()
    candidates = [
        item
        for item in history
        if lower <= item["date"] < target and family(item["name"]) == family(row["name"])
    ]
    if not candidates:
        return False, f"No recent Ops precedent found ({lower} through {(start - timedelta(days=1)).isoformat()})"
    candidates.sort(key=lambda item: (similarity(row["name"], item["name"]), item["date"]), reverse=True)
    compatible = [
        item
        for item in candidates
        if compatible_variant(row["name"], item["name"], family(row["name"]))
    ]
    best = compatible[0] if compatible else candidates[0]
    can_duplicate = bool(compatible)
    return can_duplicate, f"{best['date']} item {best['id']} ({best['name']})"


def build_task(row: dict[str, Any], target: str, history: list[dict[str, str]]) -> dict[str, Any]:
    night = is_night_plan(row)
    if night:
        start_date = (date.fromisoformat(target) + timedelta(days=1)).isoformat()
        end_date = start_date
        start_time, end_time = "00:00:00", "11:00:00"
    else:
        start_date = target
        end_date = range_end(row, target)
        start_time = end_time = "11:00:00"
    monday_start_date, monday_start_time = monday_api_value(start_date, start_time)
    monday_end_date, monday_end_time = monday_api_value(end_date, end_time)
    reuse, reference = recent_reference(row, target, history)
    template = template_source(row)
    detail = sanitize_description(row.get("description") or "") or "Required mechanic/config details are missing from the MM source."
    description = compose_description(
        task_name=normalize_name(row["name"]),
        product=row.get("product") or "",
        detail=detail,
        pricing=row.get("pricing") or None,
        reference=reference,
        reuse=reuse,
        template_source=template,
        config_status=row.get("config_status") or None,
        creative_label=row.get("creative_label") or None,
        night_plan=night,
    )
    return {
        "parent_day": target,
        "source_calendar_day": target,
        "source_row_name": row["name"],
        "source_mm_item_id": row["id"],
        "source_detail": detail,
        "config_status": row.get("config_status") or None,
        "creative_label": row.get("creative_label") or None,
        "task_name": normalize_name(row["name"]),
        "product": row.get("product"),
        "pricing": row.get("pricing") or None,
        "template_source": template,
        "start_date": start_date,
        "end_date": end_date,
        "start_at": f"{start_date} {start_time[:5]} UTC",
        "end_at": f"{end_date} {end_time[:5]} UTC",
        "start_time": start_time,
        "end_time": end_time,
        "monday_start_date": monday_start_date,
        "monday_start_time": monday_start_time,
        "monday_end_date": monday_end_date,
        "monday_end_time": monday_end_time,
        "monday_display_offset_hours": MONDAY_DISPLAY_OFFSET_HOURS,
        "due_date": (date.fromisoformat(target) - timedelta(days=2)).isoformat(),
        "m_and_m_status": status_for(row),
        "times_per_player": None,
        "reuse": reuse,
        "recent_ops_reference": reference,
        "requires_review": False,
        "warnings": [],
        "description": description,
    }


def main() -> None:
    args = parse_args()
    dates = sorted(set(args.date))
    rows_by_date = fetch_live_rows(dates)
    history = fetch_ops_history()
    specs: list[dict[str, Any]] = []
    for target in dates:
        rows = [row for row in rows_by_date[target] if should_create(row)]
        lbp_rows = [row for row in rows if family(row["name"]) == "lbp"]
        if len(lbp_rows) >= 2 and any("peak" in row["name"].lower() for row in lbp_rows):
            for row in lbp_rows:
                row["night_plan_override"] = True
        tasks = [build_task(row, target, history) for row in rows]
        spec = {
            "schema_version": 2,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_plan": "Live MM calendar board 18388590642",
            "board_id": OPS_BOARD,
            "view_id": "57490550",
            "subitem_board_id": OPS_SUBITEM_BOARD,
            "day": target,
            "parent_day": target,
            "promo_time": "11:00 UTC",
            "requires_review": False,
            "task_count": len(tasks),
            "tasks": tasks,
        }
        specs.append(spec)
    if args.stdout:
        print(json.dumps(specs[0] if len(specs) == 1 else specs, indent=2, ensure_ascii=False))
        return
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        target = spec["day"]
        path = args.output_dir / f"{target}.json"
        path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        try:
            display_path = path.relative_to(ROOT)
        except ValueError:
            display_path = path
        print(f"{display_path}: {spec['task_count']} task(s)")


if __name__ == "__main__":
    main()
