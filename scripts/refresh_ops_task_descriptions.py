#!/usr/bin/env python3
"""Refresh descriptions in existing reviewed Ops specs without changing task scope.

The script reads the live MM rows and Ops history, but never writes to Monday.
It preserves the reviewed task set and all operational fields, replacing only
description/reference metadata for tasks matched to their exact MM source row.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from build_ops_tasks_from_live_days import (
    build_task,
    family,
    fetch_live_rows,
    fetch_ops_history,
    should_create,
)
from ops_description import compose_description

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "mm_calendar" / "data" / "ops_tasks"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", action="append", required=True, help="YYYY-MM-DD")
    parser.add_argument("--spec-dir", type=Path, default=SPEC_DIR)
    parser.add_argument("--write", action="store_true", help="Write reviewed specs; default is preview")
    return parser.parse_args()


def verified_reference(value: str | None) -> bool:
    return bool(value and re.search(r"\b20\d{2}-\d{2}-\d{2}\s+item\s+\d+", value))


def choose_reference(
    generated: dict[str, Any],
    existing: dict[str, Any],
) -> tuple[bool, str | None]:
    new_reference = generated.get("recent_ops_reference")
    old_reference = existing.get("recent_ops_reference")
    if not verified_reference(new_reference) and verified_reference(old_reference):
        return bool(existing.get("reuse")), old_reference
    return bool(generated.get("reuse")), new_reference


def compose_for_existing(
    existing: dict[str, Any],
    generated: dict[str, Any],
    reuse: bool,
    reference: str | None,
) -> str:
    return compose_description(
        task_name=existing["task_name"],
        product=generated.get("product") or existing.get("product") or "",
        detail=generated.get("source_detail") or "",
        pricing=existing.get("pricing") or generated.get("pricing"),
        reference=reference,
        reuse=reuse,
        template_source=generated.get("template_source"),
        config_status=generated.get("config_status"),
        creative_label=generated.get("creative_label"),
        night_plan=(
            existing.get("m_and_m_status") == "Night Plan"
            or "night plan" in existing["task_name"].lower()
        ),
    )


def build_generated_tasks(target: str, rows: list[dict[str, Any]], history: list[dict[str, str]]) -> list[dict[str, Any]]:
    active_rows = [row for row in rows if should_create(row)]
    lbp_rows = [row for row in active_rows if family(row["name"]) == "lbp"]
    if len(lbp_rows) >= 2 and any("peak" in row["name"].lower() for row in lbp_rows):
        for row in lbp_rows:
            row["night_plan_override"] = True
    return [build_task(row, target, history) for row in active_rows]


def merge_spec(existing_spec: dict[str, Any], generated_tasks: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    by_source = {
        str(task.get("source_mm_item_id")): task
        for task in generated_tasks
        if task.get("source_mm_item_id")
    }
    merged_tasks: list[dict[str, Any]] = []
    changed: list[str] = []
    for existing in existing_spec["tasks"]:
        generated = by_source.get(str(existing.get("source_mm_item_id")))
        if not generated:
            merged_tasks.append(existing)
            continue
        reuse, reference = choose_reference(generated, existing)
        updated = dict(existing)
        updated["description"] = compose_for_existing(existing, generated, reuse, reference)
        updated["reuse"] = reuse
        updated["recent_ops_reference"] = reference
        if generated.get("template_source"):
            updated["template_source"] = generated["template_source"]
        merged_tasks.append(updated)
        if updated["description"] != existing.get("description"):
            changed.append(existing["task_name"])
    merged = dict(existing_spec)
    merged["tasks"] = merged_tasks
    merged["task_count"] = len(merged_tasks)
    return merged, changed


def main() -> None:
    args = parse_args()
    dates = sorted(set(args.date))
    rows_by_date = fetch_live_rows(dates)
    history = fetch_ops_history()
    for target in dates:
        path = args.spec_dir / f"{target}.json"
        existing = json.loads(path.read_text(encoding="utf-8"))
        generated = build_generated_tasks(target, rows_by_date[target], history)
        merged, changed = merge_spec(existing, generated)
        print(f"{target}: {len(changed)}/{len(existing['tasks'])} description(s) refreshed")
        for name in changed:
            print(f"  - {name}")
        if args.write:
            path.write_text(
                json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )


if __name__ == "__main__":
    main()
