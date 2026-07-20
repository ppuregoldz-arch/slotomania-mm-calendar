#!/usr/bin/env python3
"""Validate ops task JSON against current builder rules (pricing titles, MES subtitle, no dates in title)."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ops_description import (  # noqa: E402
    apply_pricing_to_ops_task_name,
    is_mes_board_task,
    mes_subtitle_from_mm,
    mes_subtitle_missing,
    parse_duration_hours,
    promo_family,
    task_name_has_explicit_utc_prefix,
    title_mentions_pricing,
)

ISO_IN_TITLE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
OFFER_FAMILIES_NEED_PRICING = frozenset(
    {
        "daily_deal",
        "ryd",
        "buy_all",
        "decoy_offer",
        "equal_offer",
        "limited_po",
        "prize_mania",
        "counter_po",
        "ads_personal_offer",
        "rolling_offer",
    }
)


def monday_api_value(day: str, clock: str) -> tuple[str, str]:
    intended = datetime.fromisoformat(f"{day}T{clock}")
    shifted = intended - timedelta(hours=3)
    return shifted.date().isoformat(), shifted.time().isoformat(timespec="seconds")


def validate_timing_task(task: dict) -> list[str]:
    errors: list[str] = []
    name = task.get("task_name") or ""
    source_name = task.get("source_row_name") or name
    detail = task.get("source_detail") or ""
    start_date = task.get("start_date")
    start_time = task.get("start_time")
    end_date = task.get("end_date")
    end_time = task.get("end_time")

    if all((start_date, start_time)):
        expected = monday_api_value(start_date, start_time)
        actual = (task.get("monday_start_date"), task.get("monday_start_time"))
        if actual != expected:
            errors.append(
                f"Monday Start must compensate UTC+3: {name!r} -> {actual}, expected {expected}"
            )
    if all((end_date, end_time)):
        expected = monday_api_value(end_date, end_time)
        actual = (task.get("monday_end_date"), task.get("monday_end_time"))
        if actual != expected:
            errors.append(
                f"Monday End must compensate UTC+3: {name!r} -> {actual}, expected {expected}"
            )

    if task.get("m_and_m_status") == "Night Plan":
        if (start_time, end_time) != ("00:00:00", "11:00:00"):
            errors.append(f"Night Plan must run 00:00–11:00 UTC: {name!r}")

    duration = parse_duration_hours(detail)
    source_has_clock = task_name_has_explicit_utc_prefix(source_name) or bool(
        re.search(r"\b\d{1,2}:\d{2}\s*UTC\b", detail, re.I)
    )
    if duration == 24 and not source_has_clock:
        if (start_time, end_time) != ("11:00:00", "11:00:00"):
            errors.append(f"24-hour promo must run Promo Time to Promo Time: {name!r}")

    if is_mes_board_task(source_name) and not source_has_clock and not re.search(
        r"\btime[- ]limited\b", detail, re.I
    ):
        if (start_time, end_time) != ("11:00:00", "11:00:00"):
            errors.append(f"MES reward duration changed production window: {name!r}")

    if (
        task_name_has_explicit_utc_prefix(source_name)
        and source_name.strip().lower().startswith("00:00 utc")
        and duration is None
        and (start_time, end_time) != ("00:00:00", "11:00:00")
    ):
        errors.append(f"00:00 task without duration must end at Promo Time: {name!r}")
    return errors


def validate_task(task: dict) -> list[str]:
    errors: list[str] = []
    name = task.get("task_name") or ""
    detail = task.get("source_detail") or task.get("description") or ""
    pricing = task.get("pricing") or ""
    product = task.get("product") or ""

    if ISO_IN_TITLE.search(name):
        errors.append(f"task_name contains calendar date: {name!r}")

    family = promo_family(name, product, detail)
    if pricing and family in OFFER_FAMILIES_NEED_PRICING and not title_mentions_pricing(name):
        expected = apply_pricing_to_ops_task_name(
            name.rsplit("|", 1)[0].strip() if "|" in name else name,
            pricing,
            product=product,
            detail=detail,
        )
        if expected != name:
            errors.append(f"pricing suffix missing: got {name!r}, expected {expected!r}")

    if is_mes_board_task(name):
        mm_sub = mes_subtitle_from_mm(detail)
        desc = task.get("description") or ""
        if re.search(
            r"^(?:for\s+)?\d+(?:\.\d+)?\s*(?:hours?|hrs?|days?)\s*"
            r"(?:m\.?e\.?s\.?|mes)(?:\s+challenge)?\s*$",
            desc,
            re.I | re.M,
        ):
            errors.append(f"MES Description contains production duration: {name!r}")
        if mm_sub is None:
            if re.search(r"^Sub title\s*-", desc, re.I | re.M):
                errors.append(f"MES has invented Sub title in Description: {name!r}")
            status = (task.get("m_and_m_status") or "").lower()
            if "missing art" not in status:
                errors.append(f"MES without MM Sub title must be Missing art (+Config): {name!r} -> {status!r}")
        elif mm_sub not in desc:
            errors.append(f"MES Description missing MM Sub title line: {name!r}")
        source_milestones = re.findall(
            r"^(?:\d+(?:st|nd|rd|th)?\s+milestone(?!s)|milestone\s+(\d+))\s*:?",
            detail,
            re.I | re.M,
        )
        if source_milestones:
            blocks = re.split(r"(?=^Milestone \d+:$)", desc, flags=re.M)
            milestone_blocks = [block for block in blocks if re.match(r"^Milestone \d+:$", block, re.M)]
            if len(milestone_blocks) != len(source_milestones):
                errors.append(f"MES milestone count changed in Description: {name!r}")
            for block in milestone_blocks:
                if not re.search(r"^Mission:", block, re.M) or not re.search(r"^Prize:", block, re.M):
                    errors.append(f"MES milestone must pair Mission and Prize: {name!r}")
                    break

    if mes_subtitle_missing(name, detail) and task.get("m_and_m_status") == "Waiting for MM Approval":
        errors.append(f"MES missing subtitle should not be Waiting for MM Approval: {name!r}")

    return errors


def main() -> None:
    paths = sorted((ROOT / "mm_calendar/data/ops_tasks").glob("2026-*.json"))
    if not paths:
        raise SystemExit("No ops task specs found")
    total_errors = 0
    for path in paths:
        if "extreme_only" in path.name:
            continue
        spec = json.loads(path.read_text(encoding="utf-8"))
        day_errors: list[str] = []
        for task in spec.get("tasks") or []:
            day_errors.extend(validate_task(task))
            if spec.get("timing_contract_version", 0) >= 2:
                day_errors.extend(validate_timing_task(task))
        if day_errors:
            print(f"\n{path.name}:")
            for err in day_errors:
                print(f"  - {err}")
            total_errors += len(day_errors)
    if total_errors:
        raise SystemExit(f"{total_errors} rule violation(s)")
    print(f"OK — {len(paths)} spec file(s) match current Ops builder rules.")


if __name__ == "__main__":
    main()
