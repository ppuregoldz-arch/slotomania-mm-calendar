#!/usr/bin/env python3
"""Validate season-tied prize SKUs vs active Short / Mid Term (+ Winovate always-on)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from build_august_2026_plan import mid_term, short_term, ROLLING_SNL_SKU_OVERRIDE_DAYS  # noqa: E402

PLAN_JSON = ROOT / "mm_calendar" / "data" / "august_2026_plan.json"

# Approved cross-season SKU on specific offer rows (Itay sign-off).
SEASON_SKU_OFFER_EXCEPTIONS: dict[int, frozenset[str]] = {
    14: frozenset({"RYD"}),  # RYD — Reg + PAB + 100% SB (SNL week)
}

# Owner season for each detectable SKU (user mapping + Globez Hero Coins in offers).
SKU_CHECKS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Quest", re.compile(r"quest\s*booster", re.I)),
    ("Figz", re.compile(r"figz\s*coins", re.I)),
    ("Globez", re.compile(r"(?:globez\s*coins|hero\s*coins)", re.I)),
    ("Blast", re.compile(r"superboom", re.I)),
    ("Blast", re.compile(r"\bpab\b|pickaboom", re.I)),
    ("Blast", re.compile(r"\b\d+\s*picks\b|\bpicks\b", re.I)),
    ("Battlesheep", re.compile(r"parasheep", re.I)),
    ("Battlesheep", re.compile(r"airstrike", re.I)),
    ("Battlesheep", re.compile(r"\+\s*AS\b")),
    ("SNL", re.compile(r"(?<!\w)(?:\d+\s+)?dice(?!\s*booster)(?!\s*deluxe)", re.I)),
    ("SNL", re.compile(r"multiwheel", re.I)),
    ("SNL", re.compile(r"\bshield\b", re.I)),
    ("Winovate", re.compile(r"(?<!\w)\d*\s*hammers(?!\s*wheel)", re.I)),
)

EXCLUDE_LINE_RE = re.compile(
    r"short-term:|mid-term:|seasons\s*\"|winovate \+ mega pods|\bwinovate season\b|\bmega pods season\b",
    re.I,
)


def active_seasons(d: int) -> set[str]:
    return {short_term(d), mid_term(d), "Winovate"}


def scan_text(text: str, owner: str, pattern: re.Pattern[str]) -> bool:
    if EXCLUDE_LINE_RE.search(text):
        return False
    if owner == "SNL" and re.search(r"dice\s*deluxe|dice\s*booster", text, re.I):
        return False  # star-dice promos, not SNL seasonal dice SKU
    return bool(pattern.search(text))


def validate_days(days: list[dict]) -> list[str]:
    violations: list[str] = []
    for day in days:
        d = int(day["date"])
        active = active_seasons(d)
        st, mt = short_term(d), mid_term(d)
        for item in day.get("items") or []:
            st_status = item.get("status") or ""
            if d in SEASON_SKU_OFFER_EXCEPTIONS and st_status in SEASON_SKU_OFFER_EXCEPTIONS[d]:
                continue
            if d in ROLLING_SNL_SKU_OVERRIDE_DAYS and st_status == "Rolling offer":
                continue
            blob = f"{item.get('name') or ''}\n{item.get('desc') or ''}"
            for owner, pat in SKU_CHECKS:
                if owner in active:
                    continue
                if not scan_text(blob, owner, pat):
                    continue
                if owner == "Winovate":
                    continue  # always-on in Aug 2026
                # Picks inside "2 Picks" on non-Blast — still Blast SKU
                nm = (item.get("name") or "")[:80]
                violations.append(
                    f"Day {d} ({st} · {mt}): {owner} SKU in «{nm}»"
                )
    return violations


def main() -> int:
    path = PLAN_JSON
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    days = json.loads(path.read_text(encoding="utf-8"))["days"]
    v = validate_days(days)
    print(f"Season SKU validation — {path.name}")
    print(f"Active rules: Quest/Figz/Globez mid-term · Blast/Battlesheep/SNL short-term · Winovate=Hammers (always on)")
    if not v:
        print("OK — no cross-season SKU violations.")
        return 0
    print(f"FAIL — {len(v)} violation(s):\n")
    for line in v:
        print(f"  {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
