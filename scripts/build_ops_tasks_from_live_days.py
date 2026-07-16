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

sys.path.insert(0, str(ROOT / "scripts"))
from monday_client import gql  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", action="append", required=True, help="YYYY-MM-DD")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
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
        ("gems sale", ("gems sale",)),
        ("gems coupon", ("gems coupon", "gem coupon")),
        ("golden spin", ("golden spin",)),
        ("prize mania", ("prize mania",)),
        ("battlesheep", ("battlesheep",)),
        ("shiny show", ("shiny show",)),
        ("ace heist", ("ace heist",)),
        ("lbp", ("lbp",)),
        ("lotto peak", ("lotto", "peak")),
        ("snl", ("snl",)),
        ("stickers sources", ("sticker sources", "stickers sources")),
        ("dice deluxe", ("dice deluxe",)),
        ("ryd", ("ryd", "reveal your deal")),
        ("globez", ("globez",)),
        ("winovate", ("winovate",)),
    ]
    for result, aliases in rules:
        if all(alias in text for alias in aliases):
            return result
        if len(aliases) > 1 and any(alias in text for alias in aliases):
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
    best = candidates[0]
    score = similarity(row["name"], best["name"])
    exact_reuse = score >= 0.5 and (row.get("creative_label") == "Reuse")
    return exact_reuse, f"{best['date']} item {best['id']} ({best['name']})"


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
    detail = sanitize_description(row.get("description") or "") or "Required mechanic/config details are missing from the MM source."
    reference_item = re.search(r"item (\d+)", reference)
    description_reference = (
        f"Ops item {reference_item.group(1)}"
        if reference_item
        else "No recent Ops precedent found"
    )
    description = "\n".join(
        [
            "Night Plan" if night else "Production",
            "Audience: No segment override is stated in the MM source.",
            f"Mechanic / contents: {detail}",
            *( [f"Pricing: {row['pricing']}"] if row.get("pricing") else [] ),
            "",
            f"Reuse: {'YES' if reuse else 'NO'} - {'reuse the verified recent operational shell; apply the current MM mechanic and contents.' if reuse else 'no exact recent operational reuse was verified.'}",
            "",
            "Dependencies:",
            f"- Config status from MM: {row.get('config_status') or 'not specified'}.",
            f"- Creative handoff: {row.get('creative_label') or 'not specified'}.",
            "- Missing IDs/files/parameters remain owned by the relevant MM/Ops owner.",
            "",
            f"Source: MM calendar item {row['id']}",
            f"Recent Ops reference: {description_reference}",
        ]
    )
    return {
        "parent_day": target,
        "source_calendar_day": target,
        "source_row_name": row["name"],
        "source_mm_item_id": row["id"],
        "task_name": normalize_name(row["name"]),
        "product": row.get("product"),
        "pricing": row.get("pricing") or None,
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
    args.output_dir.mkdir(parents=True, exist_ok=True)
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
        path = args.output_dir / f"{target}.json"
        path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: {len(tasks)} task(s)")


if __name__ == "__main__":
    main()
