#!/usr/bin/env python3
"""Read-only smoke checks for the four shared MM Cursor tools."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_ops_tasks_from_live_days import monday_api_value  # noqa: E402
from ops_description import resolve_ops_production_window  # noqa: E402

GOLDEN = ROOT / "tests" / "golden" / "department_tools.json"

REQUIRED_PLATFORM_FILES = (
    "DEPARTMENT_CURSOR_START.md",
    "DEPARTMENT_TOOL_CONTRACTS.md",
    "CONTRIBUTING.md",
    ".cursor/mcp.json.example",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/tool-improvement.yml",
    ".github/workflows/department-smoke.yml",
)

SKILL_GUARDS = {
    "mm-calendar-planning": ("explicitly approves exact dates", "Never infer"),
    "mm-calendar-forecast": ("insufficient evidence", "read-only for Monday"),
    "mm-brief-maker": ("dry-run", "explicit"),
    "mm-ops-monday-creator": ("Dry-run by default", "Never write Operation Status"),
}


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, re.S)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def validate_skills(fixture: dict) -> list[str]:
    errors: list[str] = []
    skills = fixture.get("skills") or {}
    if len(skills) != 4:
        errors.append(f"golden fixture must define exactly four skills; found {len(skills)}")
    for expected_name, contract in skills.items():
        path = ROOT / contract["path"]
        if not path.exists():
            errors.append(f"missing skill: {contract['path']}")
            continue
        text = path.read_text(encoding="utf-8")
        meta = frontmatter(text)
        if meta.get("name") != expected_name:
            errors.append(f"{contract['path']}: name is {meta.get('name')!r}, expected {expected_name!r}")
        description = meta.get("description") or ""
        if not description or len(description) > 1024:
            errors.append(f"{contract['path']}: invalid description length")
        if len(text.splitlines()) > 500:
            errors.append(f"{contract['path']}: SKILL.md exceeds 500 lines")
        for reference in contract.get("required_references") or []:
            if not (ROOT / reference).exists():
                errors.append(f"{contract['path']}: missing canonical reference {reference}")
            if reference not in text:
                errors.append(f"{contract['path']}: does not route to {reference}")
        for required_phrase in SKILL_GUARDS.get(expected_name, ()):
            if required_phrase not in text:
                errors.append(f"{contract['path']}: missing safety guard {required_phrase!r}")
    return errors


def validate_forecast_policy(fixture: dict) -> list[str]:
    expected = {
        "revenue": "calibrated_range",
        "paying_users": "baseline_range_no_family_adjustment",
        "gems": "insufficient_evidence_without_separate_validation",
        "coins_wager": "insufficient_evidence_without_separate_validation",
    }
    actual = fixture.get("forecast_policy")
    return [] if actual == expected else [f"forecast policy changed: {actual!r}"]


def validate_ops_timing(fixture: dict) -> list[str]:
    errors: list[str] = []
    for case in fixture.get("ops_timing_cases") or []:
        actual = resolve_ops_production_window(**case["input"])
        for key, expected in case["expected"].items():
            if actual.get(key) != expected:
                errors.append(
                    f"{case['name']}: {key} is {actual.get(key)!r}, expected {expected!r}"
                )
    if monday_api_value("2026-07-26", "00:00:00") != ("2026-07-25", "21:00:00"):
        errors.append("Monday midnight payload must compensate UTC+3")
    if monday_api_value("2026-07-26", "11:00:00") != ("2026-07-26", "08:00:00"):
        errors.append("Monday Promo Time payload must compensate UTC+3")
    return errors


def validate_platform_files() -> list[str]:
    errors = [f"missing platform file: {path}" for path in REQUIRED_PLATFORM_FILES if not (ROOT / path).exists()]
    mcp_path = ROOT / ".cursor" / "mcp.json.example"
    if mcp_path.exists():
        try:
            mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f".cursor/mcp.json.example is invalid JSON: {exc}")
        else:
            serialized = json.dumps(mcp)
            if "mcpServers" not in mcp:
                errors.append(".cursor/mcp.json.example has no mcpServers object")
            if re.search(r"(?:ghp_|github_pat_|eyJ[A-Za-z0-9_-]{20})", serialized):
                errors.append(".cursor/mcp.json.example appears to contain a real credential")
    return errors


def main() -> None:
    if not GOLDEN.exists():
        raise SystemExit(f"missing {GOLDEN.relative_to(ROOT)}")
    fixture = json.loads(GOLDEN.read_text(encoding="utf-8"))
    errors = [
        *validate_platform_files(),
        *validate_skills(fixture),
        *validate_forecast_policy(fixture),
        *validate_ops_timing(fixture),
    ]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(f"{len(errors)} department-tooling validation error(s)")
    print("OK — four Cursor Skills, governance files, forecast policy, and Ops timing goldens validated.")


if __name__ == "__main__":
    main()
