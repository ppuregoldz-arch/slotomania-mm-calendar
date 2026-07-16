#!/usr/bin/env python3
"""Duplicate Buy All template, configure Christmas brief on board 18112190666."""

from __future__ import annotations

import json
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monday_client import gql  # noqa: E402

BOARD_ID = 18112190666
TEMPLATE_ITEM_ID = 18112990829
GROUP_ID = "group_mm3r560a"
ART_ROOT = r"Q:\Slotomania\CRM3\Features\Buy_All\2026\2026_12_13_Buy_All_Christmas"
REF_2025 = r"Q:\Slotomania\CRM3\Features\Buy_All\2025\2025_12_10_Buy_All_Winter_Theme"


def main() -> None:
    dup = gql(
        "mutation ($board: ID!, $item: ID!) { duplicate_item(board_id: $board, item_id: $item) { id } }",
        {"board": str(BOARD_ID), "item": str(TEMPLATE_ITEM_ID)},
    )
    new_id = dup["duplicate_item"]["id"]
    print("duplicated:", new_id)

    cols = {
        "name": "Buy All - Christmas",
        "date4": {"date": "2026-12-13"},
        "text_mkwe4jsr": ART_ROOT,
        "color_mky3swe2": {"label": "Buy all"},
    }
    gql(
        """
        mutation ($board: ID!, $item: ID!, $vals: JSON!) {
          change_multiple_column_values(board_id: $board, item_id: $item, column_values: $vals) { id }
        }
        """,
        {"board": str(BOARD_ID), "item": new_id, "vals": json.dumps(cols)},
    )

    gql(
        "mutation ($item: ID!, $group: String!) { move_item_to_group(item_id: $item, group_id: $group) { id } }",
        {"item": new_id, "group": GROUP_ID},
    )

    parent_body = (
        "<p><strong>Theme:</strong> Christmas Buy All</p><br>"
        "<p><strong>Mechanic:</strong> Two-step Buy All — coin purchase + gems purchase</p><br>"
        "<p><strong>Coin denom:</strong> Coins + 4 RDS + PaB + Shiny card</p><br>"
        "<p><strong>Gems denom:</strong> Gems + 1 GGS + 3★ regular card</p><br>"
        f"<p><strong>Art folder:</strong> {ART_ROOT}</p><br>"
        "<p><strong>Promo date:</strong> 2026-12-13 (group: 2026-13-13)</p><br>"
        f"<p><strong>CRM3:</strong> Use 2025 winter production refs under {REF_2025} until 2026 assets exist. "
        "Upload embedded previews when CRM3 is mounted.</p>"
    )
    gql(
        "mutation ($item: ID!, $body: String!) { create_update(item_id: $item, body: $body) { id } }",
        {"item": new_id, "body": parent_body},
    )

    time.sleep(3)
    sub = gql(
        "{ items(ids: [%s]) { subitems { id name } } }" % new_id,
    )["items"][0]["subitems"]
    print("subitems:", [(s["id"], s["name"]) for s in sub])

    by_name = {s["name"].lower(): s["id"] for s in sub}

    bg_body = (
        "<table><tbody>"
        "<tr><td><p>Main Messages</p></td><td>"
        "<p><strong>SLEIGH THE DAY WHEN YOU BUY 'EM ALL!</strong><br>"
        "Two-step offer: coin purchase + gems purchase — <strong>Christmas</strong> art "
        "(festive Slotomania: snow, lights, red/green; not religious).</p></td></tr>"
        "<tr><td><p>Theme / Art Guidelines</p></td><td>"
        "<p><strong>Christmas / Winter</strong> — match prior Buy All winter tone. "
        "SKUs on screen: coin bundle (4 RDS + PaB + Shiny card) + gems bundle (1 GGS + 3★ reg card). "
        "Keep standard Buy All fine print.</p></td></tr>"
        "<tr><td><p>Numbers / Prizes / Amounts</p></td><td>"
        "<p>Per live MM config — coin step: <strong>Coins + 4 RDS + PaB + Shiny card</strong>; "
        "gems step: <strong>Gems + 1 GGS + 3★ regular card</strong>.</p></td></tr>"
        "<tr><td><p>Reference</p></td><td><p>Upload preview from CRM3 when available</p></td></tr>"
        "<tr><td><p>Reference Link</p></td><td>"
        f"<p>{REF_2025}\\BG</p></td></tr>"
        "<tr><td><p>FP</p></td><td><p>Standard Buy All FP / disclaimers per product</p></td></tr>"
        "</tbody></table>"
    )

    denoms_body = (
        "<table><tbody>"
        "<tr><td><p>Denom 1 - Coin / Prizes / Amounts</p></td><td>"
        "<p><strong>Christmas design.</strong> Coins + 4 RDS + PaB + Shiny card</p></td></tr>"
        "<tr><td><p>Denom 2 - Gems / Prizes / Amounts</p></td><td>"
        "<p><strong>Christmas design.</strong> Gems + 1 GGS + 3★ regular card</p></td></tr>"
        "<tr><td><p>Reference</p></td><td><p>Upload preview from CRM3 when available</p></td></tr>"
        "<tr><td><p>Reference Link</p></td><td>"
        f"<p>{REF_2025}\\UI\\big-M_Denom_Coins.png<br>"
        f"{REF_2025}\\UI\\big-M_Denom_Gems.png</p></td></tr>"
        "</tbody></table>"
    )

    banner_body = (
        "<table><tbody>"
        "<tr><td><p>Main Messages</p></td><td>"
        "<p><strong>Christmas theme</strong><br><strong>BUY 'EM ALL!</strong></p></td></tr>"
        "<tr><td><p>Numbers / Prizes / Amounts to be shown</p></td><td>"
        "<p>Coins + 4 RDS + PaB + Shiny card | Gems + 1 GGS + 3★ reg card</p></td></tr>"
        "<tr><td><p>Reference</p></td><td><p>Upload preview from CRM3 when available</p></td></tr>"
        "<tr><td><p>Reference Link</p></td><td>"
        f"<p>{REF_2025}\\Banner\\big-Buy_All_Winter_Theme_Banner.jpg</p></td></tr>"
        "<tr><td><p>CTA</p></td><td><p>Open buy all offer</p></td></tr>"
        "</tbody></table>"
    )

    bodies = {
        "background": bg_body,
        "denoms": denoms_body,
        "banner": banner_body,
    }

    for key, body in bodies.items():
        sid = by_name.get(key)
        if not sid:
            print("skip missing subitem:", key)
            continue
        gql(
            "mutation ($item: ID!, $body: String!) { create_update(item_id: $item, body: $body) { id } }",
            {"item": sid, "body": body},
        )
        print("briefed:", key, sid)

    print("PULSE: https://playtika.monday.com/boards/18112190666/pulses/" + new_id)


if __name__ == "__main__":
    main()
