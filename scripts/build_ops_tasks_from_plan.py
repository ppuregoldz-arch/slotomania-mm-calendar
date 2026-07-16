#!/usr/bin/env python3
"""Build reviewable Ops-task specs from approved August calendar days.

This script never writes to Monday. A day (or --all) must be explicitly selected.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN_FILE = ROOT / "mm_calendar" / "data" / "august_2026_plan.json"
OUTPUT_DIR = ROOT / "mm_calendar" / "data" / "ops_tasks"
PROMO_TIME = "11:00 UTC"
MONDAY_DISPLAY_OFFSET_HOURS = 3

# build_rows is the canonical filter for which approved calendar rows need config.
from upload_mm_calendar_day_monday import build_rows  # noqa: E402


TEMPLATE_GROUPS: dict[str, tuple[str, str]] = {
    "Daily deal": ("group_mkv1971m", "Daily Deal"),
    "Rolling offer": ("group_mkv1b6ky", "Rolling Offer"),
    "RYD": ("group_mkv1q8yw", "RYD"),
    "Buy all": ("group_mkv12864", "Buy All"),
    "MGAP": ("group_mkv1vqxx", "MGAP"),
    "ADS": ("group_mm15y5em", "PO ADS"),
    "Mid Term": ("group_mky2tww7", "Mid Term"),
    "Short Term": ("group_mky2tww7", "Mid Term"),
    "Album": ("group_mkx57gcq", "Album handover"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--day", type=int, action="append", help="August day (repeatable)")
    choice.add_argument("--all", action="store_true", help="Build all August days")
    parser.add_argument("--plan", type=Path, default=PLAN_FILE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--stdout", action="store_true", help="Print JSON; do not write files")
    return parser.parse_args()


def normalize_task_name(name: str) -> str:
    clean = re.sub(r"^\d{4}-\d{2}-\d{2}\s*\|\s*", "", name).strip()
    clean = clean.replace("—", "-")
    clean = re.sub(r"\s+", " ", clean)
    return clean


def name_key(name: str) -> str:
    value = normalize_task_name(name).lower().replace("★", "*")
    value = re.sub(r"\bdaily deal\b", "dd", value)
    value = re.sub(r"\bpricing\b|\bprice\b", "", value)
    return re.sub(r"[^a-z0-9*%]+", " ", value).strip()


def inclusive_end_date(start_iso: str, until_iso: str) -> str:
    start = date.fromisoformat(start_iso)
    until = date.fromisoformat(until_iso)
    if until < start:
        raise ValueError(f"Invalid task range: {start_iso}..{until_iso}")
    return (until + timedelta(days=1)).isoformat()


def monday_api_date_time(date_iso: str, time_value: str) -> tuple[str, str]:
    intended = datetime.fromisoformat(f"{date_iso}T{time_value}")
    api_value = intended - timedelta(hours=MONDAY_DISPLAY_OFFSET_HOURS)
    return api_value.date().isoformat(), api_value.time().isoformat()


def three_month_history_start(target_iso: str) -> str:
    target = date.fromisoformat(target_iso)
    month_index = target.year * 12 + (target.month - 1) - 3
    year, zero_based_month = divmod(month_index, 12)
    return date(year, zero_based_month + 1, 1).isoformat()


def times_per_player(name: str, description: str) -> str | None:
    text = f"{name}\n{description}".lower()
    text = re.sub(r"unless marked once[- ]per[- ]player", "", text)
    if re.search(r"\bonce(?:-per-player|\s+per\s+player)?\b", text):
        return "Once"
    if re.search(r"\bmultiple(?:\s+(?:purchases|times)(?:\s+per\s+player)?)?\b", text):
        return "Multiple"
    return None


def source_description(day: dict[str, Any], row: dict[str, Any]) -> str:
    task_name = name_key(row["name"])
    candidates = list(day.get("items") or [])
    candidates.extend(day.get("seasons") or [])
    candidates.extend(day.get("purchaseDrivers") or [])
    best: tuple[float, str] | None = None
    task_tokens = set(task_name.split())
    for item in candidates:
        raw_name = name_key(item.get("name") or item.get("label") or "")
        if raw_name and (raw_name in task_name or task_name in raw_name):
            return (item.get("desc") or "").strip()
        raw_tokens = set(raw_name.split())
        if not raw_tokens:
            continue
        score = len(task_tokens & raw_tokens) / len(task_tokens | raw_tokens)
        if best is None or score > best[0]:
            best = (score, (item.get("desc") or "").strip())
    if best and best[0] >= 0.45:
        return best[1]
    return (row.get("desc") or "").strip()


def template_source(row: dict[str, Any]) -> dict[str, str] | None:
    name = row["name"].lower()
    if "decoy" in name or "bonanza" in name:
        return {"group_id": "group_mkzvt95x", "group_title": "Triple Offer- Decoy"}
    if "limited po" in name:
        return {"group_id": "group_mm4h2685", "group_title": "Limited PO"}
    value = TEMPLATE_GROUPS.get(row.get("product") or "")
    if not value:
        return None
    return {"group_id": value[0], "group_title": value[1]}


def missing_dependencies(row: dict[str, Any], description: str) -> list[str]:
    config = row.get("config") or ""
    missing: list[str] = []
    if config == "MCP needed":
        missing.append("MCP / Economy task: TBD - owner required")
        return missing
    missing.append("Config: TBD - owner required")
    if re.search(r"\bart\b|\bwidget\b|\bbanner\b|\binapp\b", description, re.I):
        missing.append("Art: TBD - owner required")
    return missing


def m_and_m_status(row: dict[str, Any], missing: list[str]) -> str:
    if row.get("config") == "MCP needed":
        return "Missing MCP"
    if any(entry.startswith("Art:") for entry in missing):
        return "Missing art"
    return "More Info required"


def operational_description(
    *,
    row: dict[str, Any],
    detail: str,
    missing: list[str],
) -> str:
    lines = [
        "Production",
        "Audience: TBD - owner required",
        f"Mechanic / contents: {detail or 'TBD - owner required'}",
    ]
    if row.get("pricing"):
        lines.append(f"Pricing: {row['pricing']}")
    lines.extend(
        [
            "",
            "Journey / flow:",
            "Trigger: TBD - owner required",
            "Actions / reset behavior: TBD - owner required",
            "",
            "Dependencies:",
        ]
    )
    lines.extend(f"- {entry}" for entry in missing)
    lines.append("- Source files / links: TBD - owner required")
    lines.extend(
        [
            "",
            f"Source: MM calendar item - {normalize_task_name(row['name'])}",
            "Recent Ops reference: TBD - owner required (3-month window)",
            "Reuse: TBD - verify exact recent execution and current delta",
        ]
    )
    return "\n".join(lines)


def build_task(day: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    start_iso = row["date_start"]
    end_iso = inclusive_end_date(start_iso, row["date_until"])
    monday_start_date, monday_start_time = monday_api_date_time(start_iso, "11:00:00")
    monday_end_date, monday_end_time = monday_api_date_time(end_iso, "11:00:00")
    detail = source_description(day, row)
    frequency = times_per_player(row["name"], detail)
    missing = missing_dependencies(row, detail)
    template = template_source(row)
    warnings = [
        "Audience is not defined in the calendar source.",
        "Journey triggers/actions require Ops-owner review.",
        "Source files/links are not present in the calendar source.",
        "Recent Ops reference/reuse must be verified within the 3-month window.",
    ]
    if not frequency:
        warnings.append("Times per player is not defined.")
    if not template:
        warnings.append("No exact offer-template group; use same-promo history.")
    return {
        "parent_day": start_iso,
        "source_calendar_day": day["iso"],
        "source_row_name": row["name"],
        "task_name": normalize_task_name(row["name"]),
        "product": row.get("product"),
        "pricing": row.get("pricing"),
        "template_source": template,
        "start_date": start_iso,
        "end_date": end_iso,
        "start_at": f"{start_iso} {PROMO_TIME}",
        "end_at": f"{end_iso} {PROMO_TIME}",
        "start_time": "11:00:00",
        "end_time": "11:00:00",
        "monday_start_date": monday_start_date,
        "monday_start_time": monday_start_time,
        "monday_end_date": monday_end_date,
        "monday_end_time": monday_end_time,
        "monday_display_offset_hours": MONDAY_DISPLAY_OFFSET_HOURS,
        "m_and_m_status": m_and_m_status(row, missing),
        "times_per_player": frequency,
        "reuse": None,
        "recent_ops_reference": None,
        "description": operational_description(
            row=row,
            detail=detail,
            missing=missing,
        ),
        "requires_review": True,
        "warnings": warnings,
    }


def build_day_spec(day: dict[str, Any]) -> dict[str, Any]:
    rows = build_rows(day)
    config_rows = [
        row
        for row in rows
        if row.get("config") and row.get("date_start") == day["iso"]
    ]
    skipped_misaligned = [
        row["name"]
        for row in rows
        if row.get("config") and row.get("date_start") != day["iso"]
    ]
    tasks = [build_task(day, row) for row in config_rows]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_plan": str(PLAN_FILE.relative_to(ROOT)),
        "board_id": "2109172490",
        "view_id": "57490550",
        "subitem_board_id": "2109172677",
        "day": day["iso"],
        "parent_day": day["iso"],
        "promo_time": PROMO_TIME,
        "history_window": {
            "start": three_month_history_start(day["iso"]),
            "end": (date.fromisoformat(day["iso"]) - timedelta(days=1)).isoformat(),
            "rule": "Newest relevant matching execution within the previous 3 calendar months",
        },
        "requires_review": True,
        "task_count": len(tasks),
        "skipped_misaligned_rows": skipped_misaligned,
        "tasks": tasks,
    }


def selected_days(plan: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    wanted = {d["date"] for d in plan["days"]} if args.all else set(args.day or [])
    available = {d["date"] for d in plan["days"]}
    missing = sorted(wanted - available)
    if missing:
        raise SystemExit(f"Days not found in plan: {missing}")
    return [d for d in plan["days"] if d["date"] in wanted]


def main() -> None:
    args = parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    specs = [build_day_spec(day) for day in selected_days(plan, args)]
    if args.stdout:
        print(json.dumps(specs[0] if len(specs) == 1 else specs, indent=2, ensure_ascii=False))
        return
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        path = args.output_dir / f"{spec['day']}.json"
        path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        try:
            display_path = path.relative_to(ROOT)
        except ValueError:
            display_path = path
        print(f"{display_path}: {spec['task_count']} review task(s)")


if __name__ == "__main__":
    main()
