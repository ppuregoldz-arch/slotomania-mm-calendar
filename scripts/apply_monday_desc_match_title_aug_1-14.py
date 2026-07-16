#!/usr/bin/env python3
"""Align Monday Description (and Pricing when title defines tier) with row title — Aug 1–14 2026.

Itay 2026-07-16: board **title** is source of truth; fix Description only (no renames).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from upload_mm_calendar_day_monday import pricing_label, set_columns  # noqa: E402

# item_id -> full description text (replace long_text column)
DESCRIPTIONS: dict[str, str] = {
    "12510663452": (
        "30/50% coin coupon — stacks on Status Boost / top store denom.\n"
        "BACKUP row if the coupon promo is not live."
    ),
    "12464095650": (
        "Hook: 2026-08-01 | RYD - 5* Gold Card + 100% SB - High Price"
    ),
    "12486308528": (
        "Central reward: Shiny Card (multiple) (High pricing).\nMultiple purchases."
    ),
    "12488279081": (
        "Time Limited Prize — 4★ Regular Card.\nTimed clan reward window (Monday Dash Day)."
    ),
    "12511356491": (
        "Time Limited Prize — 4★ Regular Card.\nTimed clan reward window (Monday Dash Day)."
    ),
    "12465729256": "Variant: Crazy with Aces",
    "12467787872": (
        "Missions:\n"
        "· Reach act 18 — Shiny Show\n"
        "· Spin 100 times — Gem Machine\n"
        "· Open 5 pods\n"
        "· Use Quest Booster"
    ),
    "12464188765": (
        "Doubles GGS earned in offers — 3h window post 11:00 UTC.\n"
        "BACKUP row (use only if primary x2 GGS slot is not scheduled)."
    ),
    "12475693695": (
        "Season rhythm: Short Term: Battlesheep · Mid Term: Quest · Mid Term: Winovate · "
        "Mid Term: Mega Pods · Album: Album — Phase 2 (Shiny MS2)\n\n"
        "Mid Term (Winovate): Winovate scene milestones by album phase — nivi_collector_album_prizes.md\n\n"
        "Winovate season start (8d cycle). Through 2026-08-12."
    ),
    "12510753242": (
        "Central reward: 8 Hammers + Quest Booster (High pricing)."
    ),
    "12464329723": (
        "Doubles GGS earned in offers — 18:00–20:00 UTC this day."
    ),
    "12488284260": (
        "Coins denom: Coins+RDS + 2 Parasheep + AS\n"
        "Gems denom: Gems + 1 GGS + 3000 Hero Coins"
    ),
    "12488284460": (
        "Time Limited Prize — Shiny Card.\nTimed clan reward window (Monday Dash Day)."
    ),
    "12510648211": (
        "Central reward: 3 Hammers + 3000 Globez Coins (High pricing).\n\n"
        "Config: Daily Deal offer size must be **Large** (Size Large in Monday title / Smart Calendar)."
    ),
    "12510661815": (
        "Central reward: 3★ Gold Card + 2 Parasheep (High pricing)."
    ),
    "12547639977": None,  # patch in main — long rolling body
    "12486443701": (
        "Boosted Gemback 300% for 5 hours post 11:00 UTC — exclude DD."
    ),
    "12476428147": (
        "Central reward: 5★ Reg card + Despicable Wolf MG (High pricing)."
    ),
    "12475698163": (
        "Season rhythm: Short Term: Blast · Mid Term: Globez · Mid Term: Winovate · "
        "Mid Term: Mega Pods · Album: Album — Phase 2 (Shiny MS2)\n\n"
        "Mid Term (Quest): Mid-term rotation — Quest / Figz / Globez prizes by phase: "
        "nivi_collector_album_prizes.md (Winovate scenes · Mega Pods · Quest islands).\n\n"
        "Mid Term season start: Quest. Through 2026-08-19."
    ),
    "12464370814": (
        "Doubles GGS earned in offers — 3h window post 11:00 UTC."
    ),
    "12475071262": (
        "Win Master — 4★ Reg card + 2 Dice + 6 Hrs Dice.\n"
        "Starts Night Plan with timer & communications.\n\n"
        "Ghost Motel gives more; other machines give regular."
    ),
    "12476428575": (
        "Hook: 2026-08-14 | RYD - 4* Reg + Superboom + 100% SB - High Price"
    ),
}

# item_id -> Monday Pricing column label (only when title tier ≠ column)
PRICING_FROM_TITLE: dict[str, str] = {
    "12464095650": "High",
    "12486308528": "High",
}

ROLLING_11_ID = "12547639977"


def patch_rolling_11_desc(current: str) -> str:
    if not current:
        return current
    line0 = "Platform: Rolling Offer — Buy X Get Y (4 cycles) | H Pricing"
    lines = current.splitlines()
    if lines and "Buy X Get Y" in lines[0]:
        lines[0] = line0
        return "\n".join(lines)
    return current.replace("| M Pricing", "| H Pricing", 1)


def main() -> None:
    snap = Path(__file__).resolve().parents[1] / "mm_calendar/data/monday_board_live_by_date.json"
    import json

    by_date = json.loads(snap.read_text())["by_date"]
    by_id: dict[str, dict] = {}
    for rows in by_date.values():
        for r in rows:
            by_id[r["id"]] = r

    for item_id, desc in DESCRIPTIONS.items():
        if item_id == ROLLING_11_ID:
            cur = by_id.get(item_id, {}).get("description") or ""
            desc = patch_rolling_11_desc(cur)
        if not desc:
            print(f"skip empty {item_id}")
            continue
        name = by_id.get(item_id, {}).get("name", item_id)
        print(f"→ {name[:75]}")
        vals: dict = {"long_text_mkxzgg1v": {"text": desc}}
        pr = PRICING_FROM_TITLE.get(item_id)
        if pr and pricing_label(pr):
            vals["color_mky9aesm"] = {"label": pr}
        set_columns(item_id, vals)

    print("Done.")


if __name__ == "__main__":
    main()
