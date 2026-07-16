#!/usr/bin/env python3
"""Validate the MM promo knowledge base and acceptance criteria."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MM = ROOT / "mm_calendar"
JSONL = MM / "performance" / "instances" / "promo_instances.jsonl"

REQUIRED = {
    "schema_version", "instance_id", "family_id", "family_name", "variant_id",
    "variant_name", "promo_name", "start_date", "end_date", "segment", "day_type",
    "placement", "pricing", "main_kpi", "main_kpi_level", "actual_results",
    "known_confounders", "result_confidence", "evidence_type", "validation_status",
    "source_refs",
}
KPIS = {"revenue", "paying_users", "wager", "gem_usage"}
SEGMENTS = {"all", "dpu", "npu", "dormant", "pu", "ic", "black-diamond", "finishers", "tier-6-7", "mixed", "unknown"}
DAY_TYPES = {"normal", "sale", "dash-day", "event", "holiday", "album-open", "album-end", "machine-launch", "lbp-peak", "lotto-peak", "month-start", "month-end"}
PLACEMENTS = {"promo-time", "night-plan", "time-limited", "multi-day", "unknown"}
PRICING = {"low", "medium", "high", "max", "mixed", "none", "unknown"}
CONFIDENCE = {"high", "medium", "low", "insufficient"}
EVIDENCE = {"observed-result", "measured-lift", "attributed-lift", "correlation", "causal-evidence", "insufficient-evidence"}
VALIDATION = {"source-only", "existing-reproduced", "existing-unverified", "dwh-snapshot", "dwh-validated", "conflicting", "missing", "not-applicable"}
CONFOUNDERS = {"concurrent-promotions", "holiday-event", "album-timing", "lbp-lotto-peak", "dash-day", "segment-mix", "weekday-placement", "pricing", "duration-window", "audience-size", "missing-control", "small-sample", "source-mismatch", "future-or-incomplete-day"}


def validate_records() -> tuple[list[dict], list[str]]:
    errors = []
    records = []
    ids = Counter()
    if not JSONL.exists():
        return [], [f"missing {JSONL}"]
    with JSONL.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_no}: invalid JSON: {exc}")
                continue
            records.append(row)
            missing = REQUIRED - set(row)
            if missing:
                errors.append(f"line {line_no}: missing fields {sorted(missing)}")
            rid = row.get("instance_id")
            ids[rid] += 1
            family, variant = row.get("family_id", ""), row.get("variant_id", "")
            if not variant.startswith(family + "--"):
                errors.append(f"line {line_no}: variant/family mismatch {variant}/{family}")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row.get("start_date", "")):
                errors.append(f"line {line_no}: invalid start_date")
            if not row.get("source_refs"):
                errors.append(f"line {line_no}: no source_refs")
            if row.get("main_kpi") is not None and row["main_kpi"] not in KPIS:
                errors.append(f"line {line_no}: invalid main_kpi {row['main_kpi']}")
            if row.get("segment") not in SEGMENTS:
                errors.append(f"line {line_no}: invalid segment {row.get('segment')}")
            if not set(row.get("day_type", [])) <= DAY_TYPES:
                errors.append(f"line {line_no}: invalid day_type")
            if row.get("placement") not in PLACEMENTS:
                errors.append(f"line {line_no}: invalid placement")
            if row.get("pricing") not in PRICING:
                errors.append(f"line {line_no}: invalid pricing")
            if row.get("result_confidence") not in CONFIDENCE:
                errors.append(f"line {line_no}: invalid confidence")
            if row.get("evidence_type") not in EVIDENCE:
                errors.append(f"line {line_no}: invalid evidence")
            if row.get("validation_status") not in VALIDATION:
                errors.append(f"line {line_no}: invalid validation")
            if not set(row.get("known_confounders", [])) <= CONFOUNDERS:
                errors.append(f"line {line_no}: invalid confounder")
            override = row.get("main_kpi_override")
            if override and (not override.get("reason") or not override.get("source")):
                errors.append(f"line {line_no}: incomplete KPI override")
            for kpi, value in row.get("actual_results", {}).items():
                if kpi not in KPIS:
                    errors.append(f"line {line_no}: invalid actual KPI {kpi}")
                needed = {"value", "unit", "scope", "source", "confidence", "evidence_type", "validation_status"}
                if not needed <= set(value):
                    errors.append(f"line {line_no}: numeric KPI missing provenance {kpi}")
    for rid, count in ids.items():
        if count > 1:
            errors.append(f"duplicate instance_id {rid}: {count}")
    return records, errors


def check_links() -> list[str]:
    errors = []
    docs = list(MM.rglob("*.md")) + [ROOT / "AGENTS.md"]
    for doc in docs:
        if not doc.exists():
            errors.append(f"missing routed document: {doc.relative_to(ROOT)}")
            continue
        text = doc.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = target.split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            candidate = (doc.parent / target).resolve()
            if not candidate.exists():
                errors.append(f"broken link {doc.relative_to(ROOT)} -> {target}")
    return errors


def main() -> int:
    records, errors = validate_records()
    required_artifacts = [
        MM / "measurement" / "SOURCE_INVENTORY.md",
        MM / "measurement" / "PROMO_IDENTITY.md",
        MM / "measurement" / "DATA_MODEL.md",
        MM / "measurement" / "MEASUREMENT_METHODOLOGY.md",
        MM / "measurement" / "MONTHLY_REFRESH_SOP.md",
        MM / "measurement" / "MISSING_DATA_REGISTER.md",
        MM / "measurement" / "UNRESOLVED_CONFLICTS.md",
        MM / "performance" / "README.md",
        MM / "performance" / "COVERAGE_REPORT.md",
        MM / "prediction" / "PREDICTION_AND_OPTIMIZATION.md",
        MM / "prediction" / "BACKTEST_RESULTS.md",
        MM / "prediction" / "backtest_results.json",
    ]
    errors.extend(f"missing required artifact: {path.relative_to(ROOT)}" for path in required_artifacts if not path.exists())
    errors.extend(check_links())
    if records:
        with_identity = sum(bool(r.get("start_date") and r.get("family_id") and r.get("variant_id") and r.get("source_refs")) for r in records)
        numeric = sum(len(r.get("actual_results", {})) for r in records)
        print(f"records={len(records)} identity_and_source={with_identity}/{len(records)} numeric_results={numeric}")
        print(f"families={len({r['family_id'] for r in records})} variants={len({r['variant_id'] for r in records})}")
    if errors:
        print(f"FAILED: {len(errors)} errors", file=sys.stderr)
        for error in errors[:100]:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PASS: JSONL schema, IDs, vocabularies, provenance, and routed links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
