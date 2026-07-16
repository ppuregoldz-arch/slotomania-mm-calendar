#!/usr/bin/env python3
"""Split Creative brief references into image and link rows.

This repair updates only existing parent/subitem update bodies. It never creates,
deletes, moves, renames, or changes columns.
"""

from __future__ import annotations

import argparse
from typing import Any

from apply_selected_august_creative_briefs import (
    REUSE_TASK_NAME,
    brief_name,
    edit_update,
    fetch_rows,
    group_map,
    items_in_group,
    load_source_assets,
    normalize_name,
    parent_body,
    reference_asset,
    reuse_body,
    source_catalog,
    source_for,
    subitem_body,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", action="append", required=True, help="YYYY-MM-DD")
    parser.add_argument("--commit", action="store_true", help="Edit existing Monday updates")
    return parser.parse_args()


def matching_item(
    row: dict[str, str],
    source: dict[str, Any],
    items: list[dict[str, Any]],
) -> dict[str, Any] | None:
    expected = brief_name(row, source)
    base = normalize_name(row["name"])
    return next(
        (
            item
            for item in items
            if item["name"] == expected
            or item["name"] == base
            or item["name"].startswith(base + " | Reuse from ")
        ),
        None,
    )


def update_existing(update: dict[str, Any], body: str, commit: bool) -> bool:
    if not update or update.get("body") == body:
        return False
    if commit:
        edit_update(str(update["id"]), body)
    return True


def main() -> None:
    args = parse_args()
    dates = sorted(set(args.date))
    rows_by_date = fetch_rows(dates)
    catalog = source_catalog()
    load_source_assets(rows_by_date, catalog)
    groups = group_map()
    changed = 0
    missing_png: list[str] = []

    for target in dates:
        group_id = groups.get(target)
        if not group_id:
            print(f"{target}: no Creative group")
            continue
        items = items_in_group(group_id)
        reuse_rows = [row for row in rows_by_date[target] if row["label"] == "Reuse"]
        reuse_item = next((item for item in items if item["name"] == REUSE_TASK_NAME), None)
        if reuse_item and reuse_rows:
            if update_existing(
                (reuse_item.get("updates") or [{}])[0],
                reuse_body(reuse_rows, catalog),
                args.commit,
            ):
                changed += 1

        active_rows = [row for row in rows_by_date[target] if row["label"] != "Reuse"]
        date_changed = 0
        for row in active_rows:
            source = source_for(row, catalog)
            item = matching_item(row, source, items)
            if not item:
                print(f"{target}: missing existing brief for {normalize_name(row['name'])}")
                continue
            subitems = item.get("subitems") or []
            if update_existing(
                (item.get("updates") or [{}])[0],
                parent_body(row, source, [subitem["name"] for subitem in subitems]),
                args.commit,
            ):
                changed += 1
                date_changed += 1
            for subitem in subitems:
                if not reference_asset(source, subitem["name"]):
                    missing_png.append(f"{target} | {item['name']} | {subitem['name']}")
                if update_existing(
                    (subitem.get("updates") or [{}])[0],
                    subitem_body(row, source, subitem["name"]),
                    args.commit,
                ):
                    changed += 1
                    date_changed += 1
        print(f"{target}: {date_changed} active update body/bodies {'updated' if args.commit else 'would update'}")

    print(f"Total: {changed} update body/bodies {'updated' if args.commit else 'would update'}")
    print(f"Asset-specific PNG unavailable for {len(missing_png)} subitem(s); Reference row omitted:")
    for entry in missing_png:
        print(f"  - {entry}")
    if not args.commit:
        print("DRY RUN - no Monday changes made.")


if __name__ == "__main__":
    main()
