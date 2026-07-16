#!/usr/bin/env python3
"""Apply Itay-approved SKU/name fixes on Monday for 2026-08-01..15 (row-level only)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from monday_description_compact import compact_monday_description
from upload_mm_calendar_day_monday import norm_stars, rename_item, set_columns, title

UPDATES: list[tuple[str, str, str, str, str | None]] = [
    # item_id, iso, body (no date prefix), product, pricing
    (
        "12486384765",
        "2026-08-02",
        "Daily Deal - PAB + Quest Booster | High Pricing",
        "Daily deal",
        "High",
    ),
    (
        "12486217945",
        "2026-08-07",
        "Daily Deal - AS + 2 Parasheep | Max Pricing",
        "Daily deal",
        "Max",
    ),
    (
        "12486219042",
        "2026-08-06",
        "MES - Spin Zone + Option to purchase to progress | 4* Ace Card + 3* Ace topper",
        "Core",
        None,
    ),
    (
        "12487357465",
        "2026-08-12",
        "Daily Deal - Shield + 4 Dice (on purchase) | High Pricing",
        "Daily deal",
        "High",
    ),
    (
        "12475073774",
        "2026-08-13",
        "Spin Zone - 4* Reg card chase",
        "Core",
        None,
    ),
    (
        "12476428575",
        "2026-08-14",
        "RYD - 4* Reg + PAB + 100% SB - High Price",
        "RYD",
        "High",
    ),
    (
        "12488150682",
        "2026-08-15",
        "Daily Deal - Quest Booster + Shield + Multiwheel | Max Pricing",
        "Daily deal",
        "Max",
    ),
]

DESCRIPTIONS: dict[str, str] = {
    "12486384765": "Central reward: PAB + Quest Booster.",
    "12486217945": "Central reward: AS + 2 Parasheep.",
    "12486219042": (
        "Spin Zone — 4★ Ace card chase.\nTopper: 3★ Ace card (Nivi Ace_3 bank)."
    ),
    "12487357465": "Central reward: Shield + 4 Dice (on purchase).",
    "12475073774": "Prize: 4★ Reg card.\nShort-term: SNL.",
    "12476428575": "Hook: 4★ Reg + PAB + 100% SB.",
    "12488150682": "Central reward: Quest Booster + Shield + Multiwheel.",
}

PYP_2_8 = (
    "12486309356",
    "2026-08-02",
    "PYP - finish for 3* Ace card",
    "Missions:\n· Reach act 18 — Shiny Show\n· Spin 100 times — Gem Machine\n· Open 5 pods\n· Use PAB",
)


def apply_row(item_id: str, iso: str, body: str, product: str, pricing: str | None) -> None:
    name = title(iso, norm_stars(body))
    desc = compact_monday_description(
        name=body,
        product=product,
        pricing=pricing,
        description=DESCRIPTIONS.get(item_id, ""),
        on_extreme=False,
    )
    print(f"→ {name}")
    rename_item(item_id, name)
    set_columns(item_id, {"long_text_mkxzgg1v": {"text": desc}})


def main() -> None:
    for item_id, iso, body, product, pricing in UPDATES:
        apply_row(item_id, iso, body, product, pricing)
    iid, iso, body, desc_body = PYP_2_8
    name = title(iso, norm_stars(body))
    desc = compact_monday_description(
        name=body,
        product="Core",
        pricing=None,
        description=desc_body,
        on_extreme=False,
    )
    print(f"→ {name} (PYP missions)")
    rename_item(iid, name)
    set_columns(iid, {"long_text_mkxzgg1v": {"text": desc}})
    print("Done.")


if __name__ == "__main__":
    main()
