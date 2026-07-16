#!/usr/bin/env python3
"""Read Operation-Monetization examples and build a promo-aware reference library.

This script is read-only with respect to Monday. It only queries the board and
writes a local JSON cache plus Markdown reference files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BOARD_ID = "2109172490"
CACHE_FILE = ROOT / "mm_calendar" / "data" / "ops_task_samples.json"
DOCS_DIR = ROOT / "mm_calendar" / "documentation" / "ops_task_refs"
DEFAULT_TARGET_DATE = "2026-08-01"

sys.path.insert(0, str(ROOT / "scripts"))
from monday_client import gql  # noqa: E402
from ops_description import promo_family as classify_promo_family  # noqa: E402


GROUPS: dict[str, str] = {
    "group_mm0t6mxh": "Monday days",
    "group_mkzhwecm": "Monday dates",
    "group_mkv1971m": "Daily Deal",
    "group_mkv1b6ky": "Rolling Offer",
    "group_mkv1q8yw": "RYD",
    "group_mkv12864": "Buy All",
    "group_mkzvt95x": "Triple Offer - Decoy",
    "group_mm0928d4": "Triple Offer - Equal offers",
    "group_mm4h2685": "Limited PO",
    "group_mkv1vqxx": "MGAP",
    "group_mm15y5em": "PO ADS",
    "group_mky2tww7": "Mid Term",
    "group_mkx57gcq": "Album handover",
    "new_group30880": "Used templates",
    "new_group3154": "Next Month Tasks from Template",
}

FAMILY_ORDER = [
    "daily_deal",
    "rolling_offer",
    "ryd",
    "buy_all",
    "decoy_offer",
    "equal_offer",
    "limited_po",
    "mgap",
    "ads_personal_offer",
    "mes",
    "clan_dash",
    "gameplay",
    "shiny_show",
    "season_blast",
    "lbp_lotto",
    "sales_store",
    "other",
]

FAMILY_TITLES = {
    "daily_deal": "Daily Deal",
    "rolling_offer": "Rolling Offer",
    "ryd": "Reveal Your Deal",
    "buy_all": "Buy All",
    "decoy_offer": "Triple Offer / Decoy",
    "equal_offer": "Equal Triple Offer",
    "limited_po": "Limited Personal Offer",
    "mgap": "MGAP",
    "ads_personal_offer": "ADS Personal Offer",
    "mes": "M.E.S",
    "clan_dash": "Clan Dash",
    "gameplay": "Gameplay / Core",
    "shiny_show": "Shiny Show",
    "season_blast": "Season / Blast",
    "lbp_lotto": "Lotto Bonus Premium / Lotto",
    "sales_store": "Sales / Store Configuration",
    "other": "Other",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-date", default=DEFAULT_TARGET_DATE, help="Target task date (YYYY-MM-DD)")
    parser.add_argument("--max-per-family", type=int, default=6)
    parser.add_argument("--cache", type=Path, default=CACHE_FILE)
    parser.add_argument("--docs-dir", type=Path, default=DOCS_DIR)
    parser.add_argument("--from-cache", action="store_true", help="Regenerate Markdown without querying Monday")
    return parser.parse_args()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("—", "-").replace("–", "-")).strip()


def publishable_description(value: str) -> str:
    def replace_url(match: re.Match[str]) -> str:
        url = match.group(0)
        if url.startswith("https://playtika.monday.com/"):
            return url
        return "[internal link omitted]"

    return re.sub(r"https?://[^\s)>\]]+", replace_url, value).strip()


def promo_family(name: str, description: str = "", group_title: str = "") -> str:
    return classify_promo_family(name, group_title, description)


def three_month_start(target_iso: str) -> str:
    target = date.fromisoformat(target_iso)
    month_index = target.year * 12 + target.month - 4
    year, month_zero = divmod(month_index, 12)
    return date(year, month_zero + 1, 1).isoformat()


def column_text(columns: list[dict[str, Any]], column_id: str) -> str:
    return next((column.get("text") or "" for column in columns if column["id"] == column_id), "")


def extract_iso_date(value: str) -> str:
    match = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", value or "")
    return match.group(0) if match else ""


def is_canceled(statuses: list[str]) -> bool:
    return any(re.search(r"\bcancel(?:ed|led)?\b", status, re.I) for status in statuses if status)


def fetch_group(group_id: str, group_title: str) -> list[dict[str, Any]]:
    query = f"""
    query($cursor:String) {{
      boards(ids:[{BOARD_ID}]) {{
        groups(ids:["{group_id}"]) {{
          items_page(limit:100,cursor:$cursor) {{
            cursor
            items {{
              id name
              column_values(ids:["long_text","date4","date0","status_15","color_mkv5jjn5"]) {{
                id text
              }}
              subitems {{
                id name
                column_values(ids:[
                  "long_text","date_mm0f8tdb","date_mm0fr8sp","status","dup__of_m_m_status1"
                ]) {{ id text }}
              }}
            }}
          }}
        }}
      }}
    }}
    """
    cursor: str | None = None
    items: list[dict[str, Any]] = []
    while True:
        groups = gql(query, {"cursor": cursor})["boards"][0]["groups"]
        if not groups:
            break
        page = groups[0]["items_page"]
        items.extend(page["items"])
        cursor = page.get("cursor")
        if not cursor:
            break
    print(f"{group_title}: {len(items)} parent item(s)")
    return items


def record(
    *,
    item_id: str,
    name: str,
    description: str,
    promo_date: str,
    group_id: str,
    group_title: str,
    source_type: str,
    parent_id: str | None = None,
    parent_name: str | None = None,
    statuses: list[str] | None = None,
) -> dict[str, Any]:
    family = promo_family(name, description, group_title)
    return {
        "id": str(item_id),
        "name": normalize(name),
        "family": family,
        "family_title": FAMILY_TITLES[family],
        "description": publishable_description(description),
        "promo_date": promo_date,
        "group_id": group_id,
        "group_title": group_title,
        "source_type": source_type,
        "parent_id": str(parent_id) if parent_id else None,
        "parent_name": parent_name,
        "statuses": [status for status in statuses or [] if status],
        "url": f"https://playtika.monday.com/boards/{BOARD_ID}/pulses/{item_id}",
    }


def collect_examples(target_iso: str) -> list[dict[str, Any]]:
    lower = three_month_start(target_iso)
    examples: list[dict[str, Any]] = []
    day_groups = {"group_mm0t6mxh", "group_mkzhwecm"}
    for group_id, group_title in GROUPS.items():
        for parent in fetch_group(group_id, group_title):
            parent_columns = parent.get("column_values") or []
            parent_statuses = [
                column_text(parent_columns, "status_15"),
                column_text(parent_columns, "color_mkv5jjn5"),
            ]
            parent_date = extract_iso_date(parent["name"]) or extract_iso_date(
                column_text(parent_columns, "date4")
            )
            parent_description = column_text(parent_columns, "long_text")
            if (
                group_id not in day_groups
                and parent_description.strip()
                and not is_canceled(parent_statuses)
            ):
                examples.append(
                    record(
                        item_id=parent["id"],
                        name=parent["name"],
                        description=parent_description,
                        promo_date=parent_date,
                        group_id=group_id,
                        group_title=group_title,
                        source_type="template_item",
                        statuses=parent_statuses,
                    )
                )
            for subitem in parent.get("subitems") or []:
                columns = subitem.get("column_values") or []
                description = column_text(columns, "long_text")
                if not description.strip():
                    continue
                statuses = [
                    column_text(columns, "status"),
                    column_text(columns, "dup__of_m_m_status1"),
                ]
                if is_canceled(statuses):
                    continue
                promo_date = parent_date or extract_iso_date(column_text(columns, "date_mm0f8tdb"))
                if group_id in day_groups and not (lower <= promo_date < target_iso):
                    continue
                examples.append(
                    record(
                        item_id=subitem["id"],
                        name=subitem["name"],
                        description=description,
                        promo_date=promo_date,
                        group_id=group_id,
                        group_title=group_title,
                        source_type="dated_subitem" if group_id in day_groups else "template_subitem",
                        parent_id=parent["id"],
                        parent_name=parent["name"],
                        statuses=statuses,
                    )
                )
    return examples


def score_example(example: dict[str, Any]) -> tuple[int, str, int]:
    source_score = {"dated_subitem": 3, "template_subitem": 2, "template_item": 1}.get(
        example["source_type"], 0
    )
    description_score = min(len(example["description"]), 2000)
    return source_score, example.get("promo_date") or "", description_score


def select_examples(examples: list[dict[str, Any]], limit: int) -> dict[str, list[dict[str, Any]]]:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for example in examples:
        by_family[example["family"]].append(example)
    selected: dict[str, list[dict[str, Any]]] = {}
    for family_name in FAMILY_ORDER:
        candidates = sorted(by_family.get(family_name, []), key=score_example, reverse=True)
        dated = [item for item in candidates if item["source_type"] == "dated_subitem"]
        templates = [item for item in candidates if item["source_type"] != "dated_subitem"]
        chosen = dated[: max(1, limit - 2)]
        chosen.extend(templates[: max(0, limit - len(chosen))])
        if len(chosen) < limit:
            chosen_ids = {item["id"] for item in chosen}
            chosen.extend(item for item in candidates if item["id"] not in chosen_ids)
        selected[family_name] = chosen[:limit]
    return selected


def safe_code_block(value: str) -> str:
    cleaned = value.replace("```", "'''").strip()
    return "\n".join(line.rstrip() for line in cleaned.splitlines())


def write_family_doc(path: Path, family_name: str, examples: list[dict[str, Any]]) -> None:
    title = FAMILY_TITLES[family_name]
    lines = [
        f"# {title} — real Ops description examples",
        "",
        "Read-only samples from Operation - Monetization. Use these to learn voice and structure;",
        "duplicate only after verifying the same promo/variant inside the current three-month window.",
        "",
    ]
    if not examples:
        lines.extend(["No usable recent or template example was found.", ""])
    for example in examples:
        date_label = example.get("promo_date") or "template"
        lines.extend(
            [
                f"## {date_label} — {example['name']}",
                "",
                f"- Source: [{example['id']}]({example['url']})",
                f"- Group: `{example['group_title']}`",
                f"- Type: `{example['source_type']}`",
                "",
                "```text",
                safe_code_block(example["description"]),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_docs(payload: dict[str, Any], docs_dir: Path) -> None:
    docs_dir.mkdir(parents=True, exist_ok=True)
    selected = payload["selected_by_family"]
    index_lines = [
        "# Operation task description references",
        "",
        f"Generated read-only from board `{BOARD_ID}` on {payload['generated_at']}.",
        f"Target date: `{payload['target_date']}`; dated-history window starts `{payload['history_start']}`.",
        "",
        "These are writing and duplication references, not permission to copy blindly.",
        "Use the newest exact promo/variant in the valid window; otherwise use the template group and keep unknowns explicit.",
        "",
        "| Promo family | Real examples | Reference file |",
        "|---|---:|---|",
    ]
    for family_name in FAMILY_ORDER:
        filename = f"{family_name}.md"
        examples = selected.get(family_name, [])
        index_lines.append(
            f"| {FAMILY_TITLES[family_name]} | {len(examples)} | [{filename}]({filename}) |"
        )
        write_family_doc(docs_dir / filename, family_name, examples)
    (docs_dir / "README.md").write_text(
        "\n".join(index_lines).rstrip() + "\n", encoding="utf-8"
    )


def main() -> None:
    args = parse_args()
    if args.from_cache:
        payload = json.loads(args.cache.read_text(encoding="utf-8"))
    else:
        raw_examples = collect_examples(args.target_date)
        payload = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "board_id": BOARD_ID,
            "target_date": args.target_date,
            "history_start": three_month_start(args.target_date),
            "group_sources": GROUPS,
            "raw_example_count": len(raw_examples),
            "selected_by_family": select_examples(raw_examples, args.max_per_family),
        }
        args.cache.parent.mkdir(parents=True, exist_ok=True)
        args.cache.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    write_docs(payload, args.docs_dir)
    selected_count = sum(len(items) for items in payload["selected_by_family"].values())
    try:
        cache_display = args.cache.relative_to(ROOT)
    except ValueError:
        cache_display = args.cache
    try:
        docs_display = args.docs_dir.relative_to(ROOT)
    except ValueError:
        docs_display = args.docs_dir
    print(f"{cache_display}: {payload['raw_example_count']} raw example(s)")
    print(f"{docs_display}: {selected_count} selected example(s)")


if __name__ == "__main__":
    main()
