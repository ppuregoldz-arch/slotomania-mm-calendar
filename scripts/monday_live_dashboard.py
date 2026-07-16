#!/usr/bin/env python3
"""Merge live Monday board rows into dashboard month shape (read-only authority windows)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONDAY_BY_DATE = ROOT / "mm_calendar" / "data" / "monday_board_live_by_date.json"
AUGUST_PLAN = ROOT / "mm_calendar" / "data" / "august_2026_plan.json"
AUTHORITY_DOC = ROOT / "mm_calendar" / "data" / "august_2026_monday_authority_1-15.md"
AUTHORITY_JSON = ROOT / "mm_calendar" / "data" / "august_2026_monday_days_1-15.json"

# Itay: first two calendar weeks on August board = committed plan (do not edit via builder/upload without approval).
AUGUST_MONDAY_AUTHORITY_DAYS = frozenset(range(1, 16))  # 2026-08-01 … 2026-08-15

AUTHORITY_NOTE = (
    "READ-ONLY planning truth for 2026-08-01 … 2026-08-15: live Monday MM calendar board "
    "(snapshot monday_board_live_by_date.json). Do not change these days via build_august_2026_plan.py "
    "or upload_mm_calendar_day_monday.py unless Itay explicitly approves."
)

PRODUCT_STATUS_MAP = {
    "Extreme stamp": "Extreme Stamp",
    "Black Diamond": "Black Diamond",
}


def strip_iso_prefix(name: str, iso: str) -> str:
    n = (name or "").strip()
    for prefix in (f"{iso} | ", f"{iso}| "):
        if n.startswith(prefix):
            return n[len(prefix) :].strip()
    return n


def monday_row_to_item(row: dict, iso: str) -> dict:
    product = PRODUCT_STATUS_MAP.get(row.get("product") or "", row.get("product") or "")
    pr = (row.get("pricing") or "").strip()
    if pr == "Mid":
        pr = "Medium"
    return {
        "name": strip_iso_prefix(row.get("name") or "", iso),
        "status": product,
        "pricing": pr,
        "desc": (row.get("description") or "").strip(),
        "backup": False,
        "mondayItemId": row.get("id"),
    }


def day_from_monday(plan_day: dict, monday_rows: list[dict]) -> dict:
    iso = plan_day["iso"]
    items = []
    for row in monday_rows:
        if (row.get("product") or "") == "Day":
            continue
        items.append(monday_row_to_item(row, iso))
    out = {
        "date": plan_day["date"],
        "iso": iso,
        "dow": plan_day["dow"],
        "hasAnchor": bool(plan_day.get("tag") or plan_day.get("banner")),
        "seasons": plan_day.get("seasons") or [],
        "items": items,
        "sale": bool(plan_day.get("sale")),
        "tag": plan_day.get("tag"),
        "banner": plan_day.get("banner"),
        "isPast": False,
        "draftSource": "monday_live",
        "planNotes": (plan_day.get("notes") or "").strip(),
        "mondayAuthority": True,
    }
    if any("coin sale" in (it.get("name") or "").lower() for it in items):
        if out["dow"] in ("Fri", "Sat"):
            out["sale"] = True
    for it in items:
        if (it.get("status") or "").lower() == "event":
            out["hasAnchor"] = True
            break
    return out


def load_monday_by_date() -> dict[str, list[dict]]:
    if not MONDAY_BY_DATE.is_file():
        return {}
    data = json.loads(MONDAY_BY_DATE.read_text(encoding="utf-8"))
    return data.get("by_date") or {}


def merge_august_plan_days(plan_days: list[dict], by_date: dict[str, list[dict]]) -> list[dict]:
    merged: list[dict] = []
    for plan_day in plan_days:
        d = int(plan_day["date"])
        if d in AUGUST_MONDAY_AUTHORITY_DAYS:
            iso = plan_day["iso"]
            rows = by_date.get(iso, [])
            merged.append(day_from_monday(plan_day, rows))
        else:
            merged.append(plan_day)
    return merged


def write_authority_artifacts(plan_days: list[dict], by_date: dict[str, list[dict]]) -> None:
    days = [day_from_monday(p, by_date.get(p["iso"], [])) for p in plan_days if p["date"] in AUGUST_MONDAY_AUTHORITY_DAYS]
    AUTHORITY_JSON.parent.mkdir(parents=True, exist_ok=True)
    AUTHORITY_JSON.write_text(
        json.dumps(
            {
                "meta": {
                    "authority": AUTHORITY_NOTE,
                    "source": str(MONDAY_BY_DATE.relative_to(ROOT)),
                    "date_range": ["2026-08-01", "2026-08-15"],
                    "read_only": True,
                },
                "days": days,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# August 2026 — Monday authority (days 1–15)",
        "",
        f"> {AUTHORITY_NOTE}",
        "",
        "Source snapshot: `mm_calendar/data/monday_board_live_by_date.json` (refresh with `pull_monday_live_snapshot.py`).",
        "",
        "Machine JSON for agents: `mm_calendar/data/august_2026_monday_days_1-15.json`.",
        "",
        "---",
        "",
    ]
    for day in days:
        lines.append(f"## {day['iso']} ({day['dow']}){' — SALE' if day.get('sale') else ''}")
        if day.get("banner"):
            lines.append(f"**Banner:** {day['banner']}")
        if day.get("planNotes"):
            lines.append(f"**Notes:** {day['planNotes']}")
        lines.append("")
        lines.append("| Product | Pricing | Name |")
        lines.append("|---------|---------|------|")
        for it in day["items"]:
            nm = (it["name"] or "").replace("|", "\\|")
            lines.append(f"| {it.get('status') or ''} | {it.get('pricing') or ''} | {nm} |")
        lines.append("")
    AUTHORITY_DOC.write_text("\n".join(lines), encoding="utf-8")
