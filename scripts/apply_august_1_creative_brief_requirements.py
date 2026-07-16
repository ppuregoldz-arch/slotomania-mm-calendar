#!/usr/bin/env python3
"""Apply final Creative requirements to the 2026-08-01 Monetization-Art briefs."""

from __future__ import annotations

import html
import json
import re
import sys
import time
from dataclasses import dataclass, field

sys.path.insert(0, str(__file__).rsplit("/", 1)[0])
from monday_client import gql


BOARD = "18112190666"
SUBITEM_BOARD = "18112200937"
GROUP = "group_mm5a7m54"
PROMO_DATE = "2026-08-01"
BRIEF_DUE = "2026-07-23"  # 7 days before is Saturday; moved back to Thursday.
ART_DUE = "2026-07-30"


@dataclass(frozen=True)
class Reference:
    url: str
    path: str
    provenance: str = ""


@dataclass(frozen=True)
class Promo:
    label: str
    priority: str
    source_date: str
    source_pulse: str
    source_folder: str
    change_from: str | None = None
    change_to: str | None = None
    change_from_by_asset: dict[str, str] = field(default_factory=dict)
    historical_scope: str = ""
    required_assets: frozenset[str] = field(default_factory=frozenset)
    historical_patterns: dict[str, str] = field(default_factory=dict)
    unchanged_by_asset: dict[str, str] = field(default_factory=dict)
    actions: dict[str, str] = field(default_factory=dict)
    references: dict[str, Reference | tuple[Reference, ...]] = field(default_factory=dict)


def r(url: str, path: str, provenance: str = "") -> Reference:
    return Reference(url, path, provenance)


PROMOS: dict[str, Promo] = {
    "ADS PO - Coins": Promo(
        "Reuse", "Low", "2026-03-19", "11534434371",
        r"Q:\Slotomania\CRM3\Generic Promotions\Rewarded_Video\Coins\PO\New_Version",
    ),
    "Shiny Show - Joker All Cards": Promo(
        "Reuse", "Low", "2026-05-10", "11849785302",
        r"Q:\Slotomania\CRM3\Features\SlotoCards\X_SlotoCard_FEATURES\The_Shiny_Show\Joker Promotions\2026_03_24_SS_All_Cards",
        references={
            "Inapp": r("https://playtika.monday.com/protected_static/7996532/resources/2926451368/Shiny_Show_ShowJoker_inapp.png", r"Q:\Slotomania\CRM3\Features\SlotoCards\X_SlotoCard_FEATURES\The_Shiny_Show\Joker Promotions\2026_03_24_SS_All_Cards\Inapp\Shiny_Show_ShowJoker_inapp.png"),
            "Banner": r("https://playtika.monday.com/protected_static/7996532/resources/2926453359/Shiny_Show_Different_Prizes_Banner.jpg", r"Q:\Slotomania\CRM3\Features\SlotoCards\X_SlotoCard_FEATURES\The_Shiny_Show\Joker Promotions\2026_03_24_SS_All_Cards\Banner\Shiny_Show_Different_Prizes_Banner.jpg"),
            "PJMS": r("https://playtika.monday.com/protected_static/7996532/resources/2926451509/SS_Joker_AllCard_PJMS_1300x600.jpg", r"Q:\Slotomania\CRM3\Features\SlotoCards\X_SlotoCard_FEATURES\The_Shiny_Show\Joker Promotions\2026_03_24_SS_All_Cards\PJMS\SS_Joker_AllCard_PJMS_1300x600.jpg"),
            "Intro": r("https://playtika.monday.com/protected_static/7996532/resources/2926451557/SS_Joker_AllCards_Intro_461x310.png", r"Q:\Slotomania\CRM3\Features\SlotoCards\X_SlotoCard_FEATURES\The_Shiny_Show\Joker Promotions\2026_03_24_SS_All_Cards\Intro\SS_Joker_AllCards_Intro_461x310.png"),
            "Tooltip": r("https://playtika.monday.com/protected_static/7996532/resources/2926453256/Shiny_Show_Tool_Tip_Cards.png", r"Q:\Slotomania\CRM3\Features\SlotoCards\X_SlotoCard_FEATURES\The_Shiny_Show\Joker Promotions\2026_03_24_SS_All_Cards\Tooltip\Shiny_Show_Tool_Tip_Cards.png"),
        },
    ),
    "Custom Pod - X1000": Promo(
        "Reuse", "Low", "2025-11-07", "10944964121",
        r"Q:\Slotomania\CRM3\Features\Mega_Pods\2025\2025_11_07_Generic_Pod",
        references={
            "Main Inapp": r("https://playtika.monday.com/protected_static/7996532/resources/2667044946/Mega_Pods_Generic_Pod_Inapp.png", r"Q:\Slotomania\CRM3\Features\Mega_Pods\2025\2025_11_07_Generic_Pod\Inapp\Mega_Pods_Generic_Pod_Inapp.png"),
            "Banner": r("https://playtika.monday.com/protected_static/7996532/resources/2667046228/Funtastic_POD_Banner.jpg", r"Q:\Slotomania\CRM3\Features\Mega_Pods\2025\2025_09_18_Funtastic_POD\Banner\Funtastic_POD_Banner.jpg"),
        },
    ),
    "Win Master - 3* Reg Card + PAB": Promo(
        "Prize Change", "Medium", "2026-07-20", "12515008775",
        r"Q:\Slotomania\CRM3\Generic Promotions\Win_Master\2026\2026_03_27_Generic_Wheel_Master",
        change_from="3★ Ace Card",
        change_to="3★ Regular Card + PAB",
        historical_scope="Banner only. The latest Win Master 3★ Ace task contained only a Banner; the 2026-07-05 parent brief also explicitly documented Banner-only scope.",
        required_assets=frozenset({"Banner"}),
        change_from_by_asset={
            "Banner": "3★ Ace Card (latest Win Master task attachment: 2026-07-20)",
        },
        historical_patterns={
            "Banner": "Latest execution: generic Win Master Banner only; Creative changed only the prize callout to 3★ Ace. Established structure: Win Master in-app banner, Generic theme, CTA/destination to Win Master MES.",
        },
        unchanged_by_asset={
            "Banner": "Generic Win Master composition and theme; Win Master in-app banner message structure; CTA/destination to Win Master MES.",
        },
        actions={
            "Banner": "Banner only. Replace the prize callout 3★ Ace Card → 3★ Regular Card + PAB. Keep the latest generic Win Master composition, Win Master in-app banner message structure, and CTA/destination to Win Master MES unchanged.",
        },
        references={
            "Banner": r("https://playtika.monday.com/protected_static/7996532/resources/3108370668/Win_Master_Generic_Banner.png", r"Q:\Slotomania\CRM3\Features\MES\2026_03_24_Win_Master\Banner\Win_Master_Generic_Banner.png", "Latest Creative Banner attachment — update 5371897882, pulse 12515008775"),
        },
    ),
    "Daily Deal - 3* Reg Card + Hammers Wheel | High Pricing": Promo(
        "Reuse", "Low", "2025-12-10", "10679163597",
        r"Q:\Slotomania\CRM3\Features\Daily_Deal\2025\2025_07_31_DD_Hammer_wheel\DD",
        references={
            "DD (in store)": r("https://playtika.monday.com/protected_static/7996532/resources/2591589595/Daily_Deal_100Hammers.png", r"Q:\Slotomania\CRM3\Features\Daily_Deal\2025\2025_07_31_DD_Hammer_wheel\DD\Daily_Deal_100Hammers.png"),
        },
    ),
    "Status Boost": Promo(
        "Reuse", "Low", "2026-04-17", "11334801875",
        r"Q:\Slotomania\CRM3\Generic Promotions\Status_Boost\2026\2026_04_17_Status_Boost_Rebrand",
        references={
            "Coupon": (
                r("https://playtika.monday.com/protected_static/7996532/resources/2894509855/Coupon_PU_50_percent_FP_Inapp.png", r"Q:\Slotomania\CRM3\Features\Coupon Center\2025\2025_06_29_Coupon_50_75percent\Inapp\Coupon_PU_50_percent_FP_Inapp.png"),
                r("https://playtika.monday.com/protected_static/7996532/resources/2894509999/Coupon_IC_75_percent_FP_Inapp.png", r"Q:\Slotomania\CRM3\Features\Coupon Center\2025\2025_06_29_Coupon_50_75percent\Inapp\Coupon_IC_75_percent_FP_Inapp.png"),
            ),
            "LBP/Dice New theme": (
                r("https://playtika.monday.com/protected_static/7996532/resources/2902543452/image.png", "Monday source update 5102000666: latest LBP/Dice attachment"),
                r("https://playtika.monday.com/protected_static/7996532/resources/2902552299/image.png", "Monday source update 5102000666: latest LBP/Dice attachment"),
            ),
            "Benefit animations": (
                r("https://playtika.monday.com/protected_static/7996532/resources/2898720445/Intro_Animation_RD.png", "Monday source update 5097717225: RD"),
                r("https://playtika.monday.com/protected_static/7996532/resources/2898720447/Intro_Animation_Boosted_BD.png", "Monday source update 5097717225: Boosted BD"),
                r("https://playtika.monday.com/protected_static/7996532/resources/2898720453/Intro_Animation_SILVER.png", "Monday source update 5097717225: Silver"),
                r("https://playtika.monday.com/protected_static/7996532/resources/2898720455/Intro_Animation_DIAMOND.png", "Monday source update 5097717225: Diamond"),
                r("https://playtika.monday.com/protected_static/7996532/resources/2898720457/Intro_Animation_BD.png", "Monday source update 5097717225: BD"),
                r("https://playtika.monday.com/protected_static/7996532/resources/2898720641/Intro_Animation_GOLD.png", "Monday source update 5097717225: Gold"),
                r("https://playtika.monday.com/protected_static/7996532/resources/2898720649/Intro_Animation_PLATINUM.png", "Monday source update 5097717225: Platinum"),
            ),
            "Denom": r("https://playtika.monday.com/protected_static/7996532/resources/2905066438/DD_Dice_SB.png", r"Q:\Slotomania\CRM3\Features\Daily_Deal\2026\2026_02_25_Dice_SB\DD_Dice_SB.png"),
        },
    ),
    "1st of Month - Biggest Store Denom": Promo(
        "Reuse", "Low", "2025-01-12", "12212758850",
        r"Q:\Slotomania\CRM3\Features\Daily_Deal\2025\2025_01_12_Bigger_Coin_Packages",
        references={
            "Inapp": r("https://playtika.monday.com/protected_static/7996532/resources/3026218388/DF_DD_Bigger_Coins_Packages.png", r"Q:\Slotomania\CRM3\Features\Daily_Deal\2025\2025_01_08_NY_Bigger_Coin_Packages\DF\DF_DD_Bigger_Coins_Packages.png"),
            "Denom": r("https://playtika.monday.com/protected_static/7996532/resources/3026218409/Daily_Deal_X250_CoinsGems_4stGoldPack_L.png", r"Q:\Slotomania\CRM3\Features\Daily_Deal\2025\2025_01_12_Bigger_Coin_Packages\DD\Daily_Deal_X250_CoinsGems_4stGoldPack_L.png"),
            "Banner": r("https://playtika.monday.com/protected_static/7996532/resources/3026218437/BiggerCoinsPackages_EQ_Banner.jpg", r"Q:\Slotomania\CRM3\Features\Daily_Deal\2025\2025_01_08_NY_Bigger_Coin_Packages\Banner\BiggerCoinsPackages_EQ_Banner.jpg"),
        },
    ),
    "LBP - 30% Bigger Balls (Night Plan Peak)": Promo(
        "Reuse", "Low", "2025-12-16", "10770988191",
        r"Q:\Slotomania\CRM3\Features\Lotto_Bonus\2025\2025_12_16_Bigger_30or50",
        references={
            "inapp": r("https://playtika.monday.com/protected_static/7996532/resources/2618751312/PlasmaBall_Inapp_30.png", r"Q:\Slotomania\CRM3\Features\Lotto_Bonus\2025\2025_12_16_Bigger_30or50\Inapp\PlasmaBall_Inapp_30.png"),
            "UI": r("https://playtika.monday.com/protected_static/7996532/resources/2618636651/Multi_Ball_UI_4_Balls_30_Bigger.png", r"Q:\Slotomania\CRM3\Features\Lotto_Bonus\2024\2024_09_21_30_Bigger_4_Balls\UI\Multi_Ball_UI_4_Balls_30_Bigger.png"),
        },
    ),
    "Lotto - Peak (Night Plan)": Promo(
        "Reuse", "Low", "2026-07-11", "12420670025",
        r"Q:\Slotomania\CRM3\Features\Lotto_Bonus",
    ),
    "BACKUP - Coin Coupon 30%/50% on Status Boost": Promo(
        "Prize Change", "Low", "2026-07-07", "12337081885",
        r"Q:\Slotomania\CRM3\Features\Coupon Center\2026\2026_08_01_Coin_Coupon_30_50_Status_Boost",
        change_from="30% PU + 55% PRAS; Crazy Train machine skin",
        change_to="30% PU + 50% PRAS; Status Boost styling",
        historical_scope="One main Inapp with two versions: PU and PRAS.",
        required_assets=frozenset({"Inapp"}),
        historical_patterns={
            "Inapp": "Latest execution used one coupon Inapp with two versions (PU and PRAS), CTA to store, Timer yes, and FP once per player. The previous theme and message were Wacky Weeds-specific.",
        },
        unchanged_by_asset={
            "Inapp": "One Inapp with two versions (PU and PRAS); CTA to store; Timer yes; FP once per player.",
        },
        actions={
            "Inapp": "BACKUP only. Keep the established one-Inapp/two-version structure, CTA to store, Timer yes, and FP once per player. Change PU 30% → PU 30% (unchanged), PRAS 55% → PRAS 50%, and Wacky Weeds/Crazy Train treatment → Status Boost styling. Remove all machine-specific copy; exact replacement headline remains for Itay/Copy. Produce only if MM activates the backup.",
        },
        references={
            "Inapp": r("https://playtika.monday.com/protected_static/7996532/resources/3061558852/The_Craziest_Games_Coupon_Inapp_PU.png", r"Q:\Slotomania\CRM3\New Games\Crazy_Train_Games\Crazy_Train_Celebration\2026\2026_01_22_Celebration\Coupon\The_Craziest_Games_Coupon_Inapp_PU.png"),
        },
    ),
    "RYD - 5* Gold Card + 100% SB | High Price": Promo(
        "Reuse", "Low", "2026-03-28", "11350945008",
        r"Q:\Slotomania\CRM3\Features\Reveal_Your_Deal\2026\2026_03_28_RYD_100SB_5GoldCard",
        references={
            "Background": r("https://playtika.monday.com/protected_static/7996532/resources/2781130702/RYD_Wild_BG.png", r"Q:\Slotomania\CRM3\Features\Reveal_Your_Deal\2026\2026_03_28_RYD_100SB_5GoldCard\BG\RYD_Wild_BG.png"),
            "Denom On": r("https://playtika.monday.com/protected_static/7996532/resources/2781121571/Denom_100.png", r"Q:\Slotomania\CRM3\Features\Reveal_Your_Deal\2026\2026_03_28_RYD_100SB_5GoldCard\Denom\Denom_100.png"),
            "Denom Off": r("https://playtika.monday.com/protected_static/7996532/resources/2781121571/Denom_100.png", r"Q:\Slotomania\CRM3\Features\Reveal_Your_Deal\2026\2026_03_28_RYD_100SB_5GoldCard\Denom\Denom_100.png"),
        },
    ),
    "Blast - Short Term Season (Cozy)": Promo(
        "Reuse", "Low", "2026-06-26", "12334017665",
        r"Q:\Slotomania\CRM3\Features\X_Blast\2026\2026_06_26_Cozy_Blast",
        references={
            "Main Inapp": r("https://playtika.monday.com/protected_static/7996532/resources/3057045831/Cozy_Blast_Inapp_01a.png", r"Q:\Slotomania\CRM3\Features\X_Blast\2026\2026_06_26_Cozy_Blast\Inapp\Cozy_Blast_Inapp_01a.png"),
            "2nd Inapp": r("https://playtika.monday.com/protected_static/7996532/resources/3057046436/Cozy_Blast_Inapp_01_UV.png", r"Q:\Slotomania\CRM3\Features\X_Blast\2026\2026_06_26_Cozy_Blast\Inapp\Cozy_Blast_Inapp_01_UV.png"),
        },
    ),
    "Blast - Wild Ordinary | Cozy": Promo(
        "Reuse", "Low", "2025-12-15", "10719474051",
        r"Q:\Slotomania\CRM3\Features\X_Blast\2025\2024_01_26_Cozy_Blast",
        references={
            "Main Inapp": r("https://playtika.monday.com/protected_static/7996532/resources/2602916504/Cozy_Blast_Inapp_01_op2.png", r"Q:\Slotomania\CRM3\Features\X_Blast\2025\2024_01_26_Cozy_Blast\Inapp\Cozy_Blast_Inapp_01_op2.png"),
            "2nd Inapp": r("https://playtika.monday.com/protected_static/7996532/resources/2603816583/Cozy_Blast_Inapp.png", r"Q:\Slotomania\CRM3\Features\X_Blast\2025\2025_11_19\Cozy_Blast_Inapp.png"),
            "Winners Inapp": r("https://playtika.monday.com/protected_static/7996532/resources/2602922763/Cozy_Blast_Inapp_winner_Board__6.png", r"Q:\Slotomania\CRM3\Features\X_Blast\2025\2024_01_26_Cozy_Blast\Inapp\Cozy_Blast_Inapp_winner_Board__6.png"),
        },
    ),
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def table(rows: list[tuple[str, str]]) -> str:
    return "<table><tbody>" + "".join(
        f"<tr><td><p><strong>{esc(key)}</strong></p></td><td><p>{value}</p></td></tr>"
        for key, value in rows
    ) + "</tbody></table>"


def add_parent_requirements(body: str, promo: Promo) -> str:
    keys = (
        "Brief Due Date", "Art Due Date", "Priority", "Reuse Source",
        "Historical Execution Scope", "Required Asset Scope", "Current / Source",
        "Required / New", "Creative Request", "Completion",
    )
    for key in keys:
        body = re.sub(
            rf"<tr><td><p><strong>{re.escape(key)}</strong></p></td>.*?</tr>",
            "",
            body,
            flags=re.S,
        )
    source_url = f"https://playtika.monday.com/boards/{BOARD}/pulses/{promo.source_pulse}"
    if promo.label == "Reuse":
        request = f"No creative action. Reuse the approved package from {esc(promo.source_date)} unchanged."
    else:
        scope = ", ".join(sorted(promo.required_assets)) if promo.required_assets else ", ".join(sorted(promo.actions))
        request = f"Creative action required only for: <strong>{esc(scope)}</strong>. All other duplicated template assets are No Action."
    rows = [
        ("Brief Due Date", BRIEF_DUE),
        ("Art Due Date", ART_DUE),
        ("Priority", f"<strong>{esc(promo.priority)}</strong>"),
    ]
    if promo.label == "Reuse":
        rows.append(("Reuse Source", f'{esc(promo.source_date)} — <a href="{source_url}">source item</a>'))
    else:
        rows.extend([
            ("Historical Execution Scope", esc(promo.historical_scope)),
            ("Required Asset Scope", esc(", ".join(sorted(promo.required_assets)))),
            ("Current / Source", esc(promo.change_from)),
            ("Required / New", esc(promo.change_to)),
        ])
    rows.extend([
        ("Creative Request", request),
        ("Completion", "<strong>Completed</strong>" if promo.label == "Reuse" else "<strong>Creative deliverables required</strong>"),
    ])
    extra = "".join(
        f"<tr><td><p><strong>{esc(key)}</strong></p></td><td><p>{value}</p></td></tr>"
        for key, value in rows
    )
    return body.replace("</tbody></table>", extra + "</tbody></table>", 1)


def asset_requires_creative(promo: Promo, asset_name: str) -> bool:
    if promo.label == "Reuse":
        return False
    return asset_name in (promo.required_assets or frozenset(promo.actions))


def subitem_body(parent_name: str, asset_name: str, promo: Promo) -> str:
    required = asset_requires_creative(promo, asset_name)
    configured = promo.references.get(asset_name)
    references = configured if isinstance(configured, tuple) else ((configured,) if configured else ())
    if not required and promo.label != "Reuse":
        references = ()
    current_source = promo.change_from_by_asset.get(asset_name, promo.change_from)
    if promo.label == "Reuse":
        action = (
            f"No new creative production. Reuse the approved <strong>{esc(asset_name)}</strong> "
            f"from {esc(promo.source_date)} unchanged. Do not alter theme, composition, rewards, copy, CTA or timing."
        )
        completion = "<strong>Completed — no Creative action</strong>"
        historical_pattern = f"Reuse the evidenced {asset_name} execution from {promo.source_date} unchanged."
        unchanged = "Everything: asset scope, composition, theme, reward, message, CTA, Timer and FP."
    elif not required:
        action = (
            f"No Creative action. The latest comparable execution was {esc(promo.historical_scope)} "
            f"This duplicated <strong>{esc(asset_name)}</strong> subitem is outside the evidenced scope."
        )
        completion = "<strong>Completed — no Creative action</strong>"
        historical_pattern = f"Latest comparable execution did not request {asset_name}."
        unchanged = "Reuse standard product behavior; do not create or adapt this asset."
    else:
        action = esc(promo.actions[asset_name])
        completion = "<strong>Creative action required</strong>"
        historical_pattern = promo.historical_patterns[asset_name]
        unchanged = promo.unchanged_by_asset[asset_name]

    if references:
        preview = "<br>".join(
            f'<a href="{esc(reference.url)}"><img src="{esc(reference.url)}" alt="{esc(asset_name)} reference" width="600"></a>'
            for reference in references
        )
        ref_link = "<br>".join(f"<code>{esc(reference.path)}</code>" for reference in references)
        provenance = "<br>".join(
            esc(reference.provenance) if reference.provenance else
            f'Latest relevant attachment from {esc(promo.source_date)} — <a href="https://playtika.monday.com/boards/{BOARD}/pulses/{promo.source_pulse}">source item</a>.'
            for reference in references
        )
    else:
        preview = "No matching asset-type preview is attached; a different asset type must not be used as a substitute."
        ref_link = (
            f"<code>{esc(promo.source_folder)}</code> — use the existing {esc(asset_name)} from this source package; "
            "exact filename is not documented in Monday."
        )
        provenance = (
            f'No matching attached deliverable in the latest source task — '
            f'<a href="https://playtika.monday.com/boards/{BOARD}/pulses/{promo.source_pulse}">source item</a>.'
        )

    rows = [
        ("Promo", esc(parent_name)),
        ("Asset", f"<strong>{esc(asset_name)}</strong>"),
        ("Creative Label", f"<strong>{esc(promo.label)}</strong>"),
    ]
    if required:
        rows.extend([
            ("Current / Source", esc(current_source)),
            ("Required / New", esc(promo.change_to)),
        ])
    rows.extend([
        ("Historical Execution Pattern", esc(historical_pattern)),
        ("Exact Creative Action", action),
        ("What Stays Unchanged", esc(unchanged)),
        ("Reference Art", preview),
        ("Reference Link", ref_link),
        ("Reference Provenance", provenance),
        ("Brief Due Date", BRIEF_DUE),
        ("Art Due Date", ART_DUE),
        ("Priority", f"<strong>{esc(promo.priority)}</strong>"),
        ("Creative Completion", completion),
    ])
    return table(rows)


def main() -> None:
    query = """
    query($groups:[String!]) {
      boards(ids:[18112190666]) {
        groups(ids:$groups) {
          items_page(limit:100) {
            items {
              id name updates(limit:5) { id body }
              subitems { id name updates(limit:5) { id body } }
            }
          }
        }
      }
    }
    """
    items = gql(query, {"groups": [GROUP]})["boards"][0]["groups"][0]["items_page"]["items"]
    by_name = {item["name"]: item for item in items}
    missing = sorted(set(PROMOS) - set(by_name))
    if missing:
        raise RuntimeError(f"Missing August 1 briefs: {missing}")

    change_values = """
    mutation($board:ID!,$item:ID!,$values:JSON!) {
      change_multiple_column_values(board_id:$board,item_id:$item,column_values:$values) { id }
    }
    """
    edit_update = "mutation($id:ID!,$body:String!){edit_update(id:$id,body:$body){id}}"

    for name, promo in PROMOS.items():
        item = by_name[name]
        values: dict[str, object] = {
            "date_mkwj8wwp": {"date": BRIEF_DUE},
            "date_mkwep612": {"date": ART_DUE},
            "color_mkws3h8e": {"label": promo.priority},
            "status": {"label": "done" if promo.label == "Reuse" else "Copy Done"},
        }
        gql(change_values, {"board": BOARD, "item": item["id"], "values": json.dumps(values)})

        parent_update = item["updates"][0]
        gql(edit_update, {"id": parent_update["id"], "body": add_parent_requirements(parent_update["body"], promo)})

        for subitem in item["subitems"]:
            required = asset_requires_creative(promo, subitem["name"])
            if required and subitem["name"] not in promo.actions:
                raise RuntimeError(f"Missing exact action for {name} / {subitem['name']}")
            sub_values: dict[str, object] = {"status": {"label": "Done"}}
            if not required:
                sub_values["color_mkwerpn6"] = {"label": "Done"}
            gql(change_values, {"board": SUBITEM_BOARD, "item": subitem["id"], "values": json.dumps(sub_values)})
            gql(edit_update, {"id": subitem["updates"][0]["id"], "body": subitem_body(name, subitem["name"], promo)})

        print(f"UPDATED {item['id']} {promo.label:<12} {promo.priority:<6} {name}")

    # Subitem status automations can overwrite the parent status. Apply the
    # intended final parent status only after all subitems have settled.
    time.sleep(10)
    for name, promo in PROMOS.items():
        item = by_name[name]
        gql(change_values, {
            "board": BOARD,
            "item": item["id"],
            "values": json.dumps({"status": {"label": "done" if promo.label == "Reuse" else "Copy Done"}}),
        })
    time.sleep(5)

    verify = """
    query($groups:[String!]) {
      boards(ids:[18112190666]) {
        groups(ids:$groups) {
          items_page(limit:100) {
            items {
              id name
              column_values(ids:["status","date_mkwj8wwp","date_mkwep612","color_mkws3h8e"]) { id text }
              updates(limit:1) { body }
              subitems {
                name
                column_values(ids:["status","color_mkwerpn6"]) { id text }
                updates(limit:1) { body }
              }
            }
          }
        }
      }
    }
    """
    verified = gql(verify, {"groups": [GROUP]})["boards"][0]["groups"][0]["items_page"]["items"]
    errors: list[str] = []
    for item in verified:
        if item["name"] not in PROMOS:
            continue
        promo = PROMOS[item["name"]]
        columns = {column["id"]: column.get("text") or "" for column in item["column_values"]}
        expected_status = "done" if promo.label == "Reuse" else "Copy Done"
        if columns.get("status") != expected_status:
            errors.append(f"{item['name']}: parent status {columns.get('status')!r}")
        if columns.get("date_mkwj8wwp") != BRIEF_DUE or columns.get("date_mkwep612") != ART_DUE:
            errors.append(f"{item['name']}: due dates")
        if columns.get("color_mkws3h8e") != promo.priority:
            errors.append(f"{item['name']}: priority")
        if "Creative Request" not in item["updates"][0]["body"]:
            errors.append(f"{item['name']}: parent request")
        for subitem in item["subitems"]:
            body = subitem["updates"][0]["body"]
            if "Exact Creative Action" not in body or f'alt="{html.escape(subitem["name"], quote=True)} reference"' not in body and "No matching asset-type preview" not in body:
                errors.append(f"{item['name']} / {subitem['name']}: brief/reference")
            if not asset_requires_creative(promo, subitem["name"]):
                subcolumns = {column["id"]: column.get("text") or "" for column in subitem["column_values"]}
                if subcolumns.get("status") != "Done" or subcolumns.get("color_mkwerpn6") != "Done":
                    errors.append(f"{item['name']} / {subitem['name']}: completion")
    if errors:
        raise RuntimeError("Verification failed:\n- " + "\n- ".join(errors))
    print(f"VERIFIED {len(PROMOS)} parent briefs and {sum(len(item['subitems']) for item in verified if item['name'] in PROMOS)} subitem briefs")


if __name__ == "__main__":
    main()
