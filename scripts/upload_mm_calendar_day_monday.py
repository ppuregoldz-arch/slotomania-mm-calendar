#!/usr/bin/env python3
"""Upload / sync August 2026 plan days to MM calendar Monday board (18388590642).

WARNING: Full-day sync overwrites matched rows from the plan and DELETES board items
not in build_rows(). Do NOT run --all or wide --from/--to after manual board edits
unless the user explicitly approves scope. Prefer updating the builder/JSON only.
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from monday_client import gql  # noqa: E402
from monday_description_compact import compact_monday_description  # noqa: E402

# Block windows from plan builder
from build_august_2026_plan import (  # noqa: E402
    EXTREME,
    FIGZ_DAYS,
    GLOBEZ_DAYS,
    MID_TERM_BLOCKS,
    MEGA_PODS_CYCLE_DAYS,
    POPUP_STORE_DAYS,
    QUEST_DAYS,
    WINOVATE_CYCLE_DAYS,
    desc_has_offer_structure,
    enrich_item_description,
    is_popup_store_item,
    is_popup_store_paired_offer,
    mega_pods_season_bounds,
    winovate_season_bounds,
    is_puzzle_mes_item,
    puzzle_mes_item_name,
    short_term as plan_short_term,
)

ALBUM_PHASE3_END = "2026-09-22"  # album_cards.md — cycle ends 22/09
MEGA_PODS_WEEK_DAYS = MEGA_PODS_CYCLE_DAYS

BOARD_ID = 18388590642
GROUP_ID = "group_mky2rn6g"
PLAN_FILE = ROOT / "mm_calendar" / "data" / "august_2026_plan.json"

SHORT_TERM_BLOCKS = [
    (1, 5, "Blast"),
    (6, 10, "Battlesheep"),
    (11, 15, "SNL"),
    (16, 20, "Blast"),
    (21, 25, "Battlesheep"),
    (26, 31, "SNL"),
]

ECONOMISTS = {
    "nivi": 46760771,
    "kfir": 97782375,
    "ohad": 96420441,
    "yahav": 68089452,  # Yahav Mizrahi — Core gameplay challenges
    "tom_sharlo": 100474785,  # Tom Sharlo — Spinner Clash
}

WINOVATE_MONDAYS: frozenset[int] = frozenset()  # legacy — seasons driven by plan isFirst rows
THEME_RE = re.compile(
    r"betty|nostalgic|back to school|hoppin|machine|launch|sneak|bts|"
    r"carnival|birthday|sticker|shiny collection|status boost|puzzle",
    re.I,
)


def people(*keys: str) -> dict:
    return {"personsAndTeams": [{"id": ECONOMISTS[k], "kind": "person"} for k in keys]}


def has_card(text: str) -> bool:
    t = text.lower()
    return bool(
        re.search(r"\d\s*★|\d\s*\*|★|reg card|gold card|ace card|wild", t)
        or ("hammers wheel" in t and "card" in t)
    )


def norm_stars(s: str) -> str:
    return s.replace("★", "*").replace("—", "-").replace("–", "-").strip()


def pricing_label(p: str | None) -> str | None:
    if not p:
        return None
    p = str(p).strip()
    if p == "Medium":
        p = "Mid"
    return p if p in ("High", "Max", "Mid", "Low") else None


# Monday Pricing column — only monetization offers (not gameplay / toppers without offer lane).
PRICING_PRODUCTS = frozenset(
    {
        "Daily deal",
        "Rolling offer",
        "Buy all",
        "RYD",
        "Offers & coin sale",
        "Counter PO",
    }
)


# Monday board Product column labels (must match board status options exactly).
BOARD_PRODUCT_LABEL: dict[str, str] = {
    "Extreme Stamp": "Extreme stamp",
}


def board_product_label(product: str) -> str:
    return BOARD_PRODUCT_LABEL.get(product, product)


def monday_pricing(monday_product: str, plan_pricing: str | None) -> str | None:
    if monday_product not in PRICING_PRODUCTS:
        return None
    return pricing_label(plan_pricing)


def title(iso: str, body: str) -> str:
    body = norm_stars(body)
    return body if body.startswith(iso) else f"{iso} | {body}"


def config_due(iso: str) -> str:
    y, m, d = map(int, iso.split("-"))
    return (date(y, m, d) - timedelta(days=2)).isoformat()


def iso_end(day_num: int) -> str:
    return f"2026-08-{day_num:02d}"


def plan_day_to_date(day_num: int) -> date:
    """August plan day index (1=Aug 1) — may extend into September."""
    return date(2026, 8, 1) + timedelta(days=day_num - 1)


def plan_day_to_iso(day_num: int) -> str:
    return plan_day_to_date(day_num).isoformat()


def season_spills_to_september(until_iso: str) -> bool:
    return until_iso > "2026-08-31"


def season_window_note(until_iso: str) -> str:
    if season_spills_to_september(until_iso):
        return "Timeline continues into September per monthly/album guidelines (expected)."
    return ""


def short_term_window(d: int) -> tuple[str, str, str]:
    for a, b, name in SHORT_TERM_BLOCKS:
        if a <= d <= b:
            return name, iso_end(a), iso_end(b)
    return plan_short_term(d), iso_end(d), iso_end(d)


def mid_term_window(d: int) -> tuple[str, str, str]:
    for a, b, name in MID_TERM_BLOCKS:
        if a <= d <= b:
            return name, plan_day_to_iso(a), plan_day_to_iso(b)
    return "Quest", plan_day_to_iso(d), plan_day_to_iso(d)


def winovate_window(d: int) -> tuple[str, str]:
    a, b = winovate_season_bounds(d)
    return plan_day_to_iso(a), plan_day_to_iso(b)


def mega_pods_window(d: int) -> tuple[str, str]:
    a, b = mega_pods_season_bounds(d)
    return plan_day_to_iso(a), plan_day_to_iso(b)


def album_window(d: int) -> tuple[str, str, str]:
    if d >= 25:
        return "Album — Phase 3 (Shiny MS3)", "2026-08-25", ALBUM_PHASE3_END
    return "Album — Phase 2 (Shiny MS2)", "2026-08-04", "2026-08-24"


def season_row_name(iso: str, season: dict, d: int) -> str:
    name = season.get("name") or ""
    st = season.get("status") or ""
    if st == "Short Term":
        st_name, _, _ = short_term_window(d)
        return title(iso, f"{st_name} - Short Term")
    if st == "Mid Term" and name in ("Winovate", "Mega Pods"):
        return title(iso, f"{name} Season")
    if st == "Mid Term" and "Winovate" in name and "Mega" in name:
        return title(iso, "Winovate + Mega Pods")
    if st == "Mid Term":
        mt, _, _ = mid_term_window(d)
        return title(iso, f"{mt} Season")
    if st == "Album":
        label, _, _ = album_window(d)
        return title(iso, label.replace("Album — ", "Album - "))
    return title(iso, name)


def promo_display_name(iso: str, it: dict) -> str:
    name = norm_stars(it.get("name") or "")
    status = it.get("status") or ""
    if is_puzzle_mes_item(it):
        dnum = int(iso.split("-")[2])
        return title(iso, puzzle_mes_item_name(dnum))
    product = monday_product(name, status)
    pr = monday_pricing(product, it.get("pricing"))
    if status == "Daily deal":
        body = re.sub(r"^DD\s*[-–—]\s*", "", name, flags=re.I).strip()
        label = f"Daily Deal — {body}" if body else "Daily Deal"
        if pr and "pricing" not in label.lower():
            return title(iso, f"{label} | {pr} Pricing")
        return title(iso, label)
    if status == "RYD" and pr and "price" not in name.lower():
        return title(iso, f"{name} - {pr} Price")
    if status == "Offers & coin sale" and "coin sale" in name.lower():
        return title(iso, f"Coin Sale | {pr} Pricing" if pr else "Coin Sale")
    return title(iso, name)


def promo_until(iso: str, it: dict) -> tuple[str, str]:
    nm = (it.get("name") or "").lower()
    desc = (it.get("desc") or "").lower()
    # Night Plan peak / LBP — single calendar day (name carries the window; no 2-day board span).
    if ("lotto" in nm and "peak" in nm) or re.match(r"^lbp\s", nm) or "night plan" in nm:
        return iso, iso
    if "night plan" in desc and ("lotto" in nm or "lbp" in nm):
        return iso, iso
    return iso, iso


def build_description(day: dict, extra: str = "") -> str:
    parts: list[str] = []
    if day.get("banner"):
        parts.append(f"Anchor / banner: {day['banner']}.")
    if day.get("sale"):
        parts.append("SALE day (weekend coin sale).")
    seasons = day.get("seasons") or []
    if seasons:
        parts.append(
            "Season rhythm: "
            + " · ".join(f"{s.get('status')}: {s.get('name')}" for s in seasons)
        )
        for s in seasons:
            if s.get("isFirst") and (s.get("desc") or "").strip():
                parts.append(f"{s.get('status')} ({s.get('name')}): {(s.get('desc') or '').strip()}")
    for drv in day.get("purchaseDrivers") or []:
        parts.append(f"Purchase driver: {drv.get('label')} — {drv.get('desc', '').strip()}")
    if day.get("notes"):
        parts.append(f"Plan notes: {day['notes'].strip()}")
    if extra:
        parts.append(extra.strip())
    return "\n\n".join(p for p in parts if p)


def monday_item_description(day: dict, it: dict, product: str) -> str:
    """Offer rows: structure + prizes. Other rows: day context + notes."""
    raw_name = it.get("name") or ""
    extra = (it.get("desc") or "").strip()
    dnum = day["date"]
    on_extreme = dnum in EXTREME
    status = it.get("status") or product or ""

    def finalize(body: str) -> str:
        return compact_monday_description(
            name=raw_name,
            product=status or product,
            pricing=it.get("pricing"),
            description=body,
            on_extreme=on_extreme,
        )

    offer_like = product in PRICING_PRODUCTS or product in (
        "Buy all",
        "MGAP",
        "Prize Mania",
        "Popup Store",
        "Segmented test",
    )
    st = status.lower()
    if offer_like or st in (
        "daily deal",
        "offers & coin sale",
        "rolling offer",
        "buy all",
        "ryd",
        "prize mania",
        "counter po",
        "mgap",
    ):
        body = extra
        if not desc_has_offer_structure(body):
            body = enrich_item_description(
                raw_name,
                it.get("status"),
                it.get("pricing"),
                extra,
                dnum,
                on_extreme=on_extreme,
            )
        if "bogo" in raw_name.lower() and "task" not in body.lower():
            body = f"{body}\n\nConfig: open BOGO task in LiveOps."
        if "decoy" in raw_name.lower() and "bonanza" in raw_name.lower():
            body = re.sub(r"\nFull denoms:.*", "", body, flags=re.I).strip()
        return finalize(body)
    needs_enrich = (
        st in ("core", "clan-dash", "ads")
        or re.search(
            r"shiny show|pyp|win master|ace heist|piggy|custom pod|spin zone|spinner|"
            r"dash pass|status boost|shiny collection|lotto\s*[—-]\s*peak|^lbp\s|ace loot",
            raw_name,
            re.I,
        )
    )
    if needs_enrich:
        if not desc_has_offer_structure(extra):
            return finalize(
                enrich_item_description(
                    raw_name,
                    it.get("status"),
                    it.get("pricing"),
                    extra,
                    dnum,
                    on_extreme=on_extreme,
                )
            )
        return finalize(extra)
    return build_description(day, extra)


def config_status_for(product: str, name: str, cards: bool) -> str | None:
    nl = name.lower()
    if "status boost" in nl:
        return None
    # Night Plan Lotto peak + LBP promo — rotate in LiveOps by calendar name only; no config task.
    if re.search(r"lotto\s*[—-]\s*peak", nl) or re.match(r"^lbp\s", nl):
        return None
    # Album marketing — Shiny Collection last day / opening (calendar comms, not a LiveOps config promo).
    if "shiny collection" in nl:
        return None
    # X2 Extreme Stamp — calendar amplifier row (no LiveOps config task, no pricing tier).
    if product == "Extreme Stamp" or re.search(r"\bx2\s*extreme\s*stamp", nl):
        return None
    # x2 GGS — timed gem amplifier (reuse creative; no config task).
    if re.search(r"\bx2\s*ggs", nl):
        return None
    if product == "Clan-Dash":
        return None
    if product in ("Short Term", "Mid Term", "Album"):
        return "Config needed"
    if cards:
        return "MCP needed"
    if product == "ADS":
        return "Config needed"
    return "Config needed"


def economist_for(product: str, name: str) -> tuple[str, ...]:
    nl = name.lower()
    if "spinner clash" in nl:
        return ("tom_sharlo",)
    if product == "ADS" or "custom pod" in nl:
        return ("ohad",)
    if product == "Short Term":
        return ("kfir",)
    if product == "Mid Term":
        return ("ohad",)
    if product == "Album":
        return ("nivi",)
    if product == "Core":
        return ("yahav",)
    if has_card(name):
        return ("nivi",)
    return ("nivi",)


def economy_status(product: str, name: str) -> str:
    nl = name.lower()
    if "status boost" in nl:
        return "No need of Economie approval"
    if product in ("Short Term", "Mid Term") and (
        "season" in nl or "blast" in nl or "figz" in nl or "quest" in nl or "globez" in nl
    ):
        return "No need of Economie approval"
    return "Comment"


def creative_label(row: dict, day: dict) -> str | None:
    """Monday Creative Label: Reuse | New promo | New theme for promo | Prize Change."""
    name = row["name"].lower()
    product = row["product"]
    desc = (row.get("desc") or "").lower()
    banner = (day.get("banner") or "").lower()

    # Mega Pods weekly Mon→Mon season row reuses existing mid-term creative (not a new theme).
    if product == "Mid Term" and "mega pods" in name:
        return "Reuse"
    if re.search(r"\bx2\s*ggs", name):
        return "Reuse"
    if product in ("Short Term", "Mid Term", "Album") and (
        "season" in name or "short term" in name or "album" in name
    ):
        return "New theme for promo"
    if product == "SlotoBucks" or "biggest store denom" in name:
        return "Reuse"
    if THEME_RE.search(name) or THEME_RE.search(desc) or THEME_RE.search(banner):
        return "New promo"
    if day.get("tag") in ("event", "machine") and product in ("Event", "Core", "Offers & coin sale"):
        return "New promo"
    if "coin sale" in name and (day.get("banner") or "themed" in desc):
        return "New theme for promo"
    if "decoy" in name or "bonanza" in name:
        if "wild" in desc or "shiny" in desc:
            return "Prize Change"
        return "Reuse"
    if product in ("Daily deal", "RYD", "Rolling offer", "Buy all", "MGAP", "Gems", "ADS", "Core", "Album"):
        if "shiny show" in name or "shiny despicable" in name:
            return "New promo"
        if "shiny limited" in name or "once" in name or "bogo" in name.lower():
            return "Prize Change"
        return "Reuse"
    if product == "Prize Mania":
        return "Reuse"
    return "Reuse"


def is_album_feature(name: str) -> bool:
    nl = name.lower()
    return (
        "shiny show" in nl
        or "shiny collection" in nl
        or re.search(r"\bgold trading day\b", nl) is not None
    )


def monday_product(raw_name: str, plan_status: str) -> str:
    nl = raw_name.lower()
    if is_album_feature(raw_name):
        return "Album"
    if re.search(r"dash pass\s*[—-]\s*dash day", nl):
        return "Clan-Dash"
    if re.search(
        r"win master|ace heist|pyp|spinner clash|spin zone|puzzle m\.e\.s|ace loot|custom pod|mes —",
        nl,
    ):
        return "Core"
    if "lotto" in nl and "peak" in nl:
        return "Offers & coin sale"
    if "golden spin" in nl:
        return "Offers & coin sale"
    if "piggy" in nl:
        return "Offers & coin sale"
    if re.search(r"\bx2\s*extreme\s*stamp", nl):
        return "Extreme Stamp"
    product = plan_status or ""
    if product == "Segmented test":
        return "Offers & coin sale"
    if product == "Popup Store":
        return "Offers & coin sale"
    if product == "Core" and "custom pod" in raw_name.lower():
        return "Mid Term"
    if product == "Core" and "status boost" in raw_name.lower():
        return "Event"
    return product


def row_key(name: str) -> str:
    n = norm_stars(name).lower()
    if "|" in n:
        n = n.split("|", 1)[1].strip()
    return re.sub(r"\s+", " ", n)


def board_name_is_popup_store(name: str) -> bool:
    return "popup store" in row_key(name)


def remove_orphan_day_items(existing: list[dict], keep_ids: set[str]) -> list[str]:
    """Delete items on this start-date that are no longer in the plan (fixes add-only drift)."""
    removed_ids: list[str] = []
    for ex in existing:
        if ex["id"] in keep_ids:
            continue
        delete_item(ex["id"])
        removed_ids.append(ex["id"])
        time.sleep(0.05)
    return removed_ids


COMBINED_WINOVATE_MEGA_RE = re.compile(
    r"winovate\s*\+\s*mega\s*pods|mega\s*pods\s*\+\s*winovate",
    re.I,
)


def remove_stale_combined_winovate_mega(existing: list[dict], keep_ids: set[str]) -> list[str]:
    """Drop legacy single row that bundled Winovate + Mega Pods (now two season rows)."""
    removed_ids: list[str] = []
    for ex in existing:
        if ex["id"] in keep_ids:
            continue
        if not COMBINED_WINOVATE_MEGA_RE.search(ex.get("name") or ""):
            continue
        delete_item(ex["id"])
        removed_ids.append(ex["id"])
        time.sleep(0.05)
    return removed_ids


def remove_stale_popup_store_items(existing: list[dict], keep_ids: set[str]) -> list[str]:
    """Delete Popup Store rows on this date that are not part of the current plan sync."""
    removed_ids: list[str] = []
    for ex in existing:
        if ex["id"] in keep_ids:
            continue
        if not board_name_is_popup_store(ex["name"]):
            continue
        delete_item(ex["id"])
        removed_ids.append(ex["id"])
        time.sleep(0.05)
    return removed_ids


def dedupe_rows(rows: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for r in rows:
        k = row_key(r["name"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def build_rows(day: dict) -> list[dict]:
    iso = day["iso"]
    dnum = day["date"]
    rows: list[dict] = []

    if dnum == 1:
        for drv in day.get("purchaseDrivers") or []:
            rows.append(
                {
                    "name": title(iso, drv.get("label") or "1st of month - biggest store denom"),
                    "product": drv.get("monday_product") or "Offers & coin sale",
                    "economist": ("nivi",),
                    "pricing": None,
                    "desc": (drv.get("desc") or "").strip(),
                    "config": "Config needed",
                    "date_start": iso,
                    "date_until": iso,
                }
            )

    for s in day.get("seasons") or []:
        if not s.get("isFirst"):
            continue
        st = s.get("status") or ""
        sname = s.get("name") or ""
        if st == "Mid Term" and sname == "Winovate":
            t_from, t_to = winovate_window(dnum)
            w_note = season_window_note(t_to)
            rows.append(
                {
                    "name": season_row_name(iso, s, dnum),
                    "product": "Mid Term",
                    "economist": ("ohad",),
                    "pricing": None,
                    "desc": build_description(
                        day,
                        f"Winovate season start ({WINOVATE_CYCLE_DAYS}d cycle). Through {t_to}. {w_note}".strip(),
                    ),
                    "config": config_status_for("Mid Term", sname, False),
                    "date_start": t_from,
                    "date_until": t_to,
                }
            )
            continue
        if st == "Mid Term" and sname == "Mega Pods":
            t_from, t_to = mega_pods_window(dnum)
            w_note = season_window_note(t_to)
            rows.append(
                {
                    "name": season_row_name(iso, s, dnum),
                    "product": "Mid Term",
                    "economist": ("ohad",),
                    "pricing": None,
                    "desc": build_description(
                        day,
                        f"Mega Pods season start (Mon→Mon, {MEGA_PODS_WEEK_DAYS}d). Through {t_to}. {w_note}".strip(),
                    ),
                    "config": config_status_for("Mid Term", sname, False),
                    "date_start": t_from,
                    "date_until": t_to,
                }
            )
            continue
        if "Winovate" in sname and "Mega" in sname:
            continue
        if st == "Short Term":
            _, t_from, t_to = short_term_window(dnum)
            extra = f"Short Term season start: {plan_short_term(dnum)}."
            note = season_window_note(t_to)
            desc = build_description(day, f"{extra} {note}".strip())
        elif st == "Mid Term":
            _, t_from, t_to = mid_term_window(dnum)
            extra = f"Mid Term season start: {sname}. Through {t_to}."
            note = season_window_note(t_to)
            desc = build_description(day, f"{extra} {note}".strip())
        elif st == "Album":
            label, t_from, t_to = album_window(dnum)
            extra = f"Album rhythm: {label}. Active through {t_to}."
            note = season_window_note(t_to)
            desc = build_description(day, f"{extra} {note}".strip())
        else:
            continue
        rows.append(
            {
                "name": season_row_name(iso, s, dnum),
                "product": monday_product(sname, st),
                "economist": economist_for(st, sname),
                "pricing": None,
                "desc": desc,
                "config": config_status_for(st, sname, False),
                "date_start": t_from,
                "date_until": t_to,
            }
        )

    for it in day.get("items", []):
        if it.get("backup"):
            continue
        if is_popup_store_item(it) and dnum not in POPUP_STORE_DAYS:
            continue
        if is_popup_store_paired_offer(it) and dnum not in POPUP_STORE_DAYS:
            continue
        raw_name = it.get("name") or ""
        name = promo_display_name(iso, it)
        product = monday_product(raw_name, it.get("status") or "")
        pr = monday_pricing(product, it.get("pricing"))
        cards = has_card(raw_name)
        t_from, t_to = promo_until(iso, it)
        extra = (it.get("desc") or "").strip()
        rows.append(
            {
                "name": name,
                "product": product,
                "economist": economist_for(product, raw_name),
                "pricing": pr,
                "desc": monday_item_description(day, it, product),
                "config": config_status_for(product, raw_name, cards),
                "date_start": t_from,
                "date_until": t_to,
            }
        )

    for row in rows:
        row["creative"] = creative_label(row, day)
    if dnum not in POPUP_STORE_DAYS:
        rows = [r for r in rows if not board_name_is_popup_store(r["name"])]
    return dedupe_rows(rows)


def create_item(name: str) -> str:
    q = """
    mutation ($board: ID!, $group: String!, $name: String!) {
      create_item(board_id: $board, group_id: $group, item_name: $name) { id }
    }
    """
    return gql(q, {"board": str(BOARD_ID), "group": GROUP_ID, "name": name})["create_item"]["id"]


def set_columns(item_id: str, values: dict) -> None:
    q = """
    mutation ($board: ID!, $item: ID!, $vals: JSON!) {
      change_multiple_column_values(board_id: $board, item_id: $item, column_values: $vals) { id }
    }
    """
    gql(q, {"board": str(BOARD_ID), "item": item_id, "vals": json.dumps(values)})


def rename_item(item_id: str, name: str) -> None:
    gql(
        'mutation($b:ID!,$item:ID!,$v:String!){change_simple_column_value(board_id:$b,item_id:$item,column_id:"name",value:$v){id}}',
        {"b": str(BOARD_ID), "item": item_id, "v": name},
    )


def apply_row(row: dict, item_id: str | None = None) -> str:
    if not item_id:
        item_id = create_item(row["name"])
    iso_start = row["date_start"]
    iso_until = row["date_until"]
    due = config_due(iso_start)

    vals: dict = {
        "status": {"label": board_product_label(row["product"])},
        "long_text_mkxzgg1v": {"text": row.get("desc") or ""},
        "date_mky27nx7": {"date": iso_start},
        "timerange_mkz3t5qy": {"from": iso_start, "to": iso_until},
        "color_mky0czxd": None,
        "color_mky9aesm": None,
    }
    if row.get("economist"):
        vals["multiple_person_mky0jahx"] = people(*row["economist"])
    if row.get("pricing"):
        vals["color_mky9aesm"] = {"label": row["pricing"]}
    if row.get("config"):
        vals["color_mkztqb24"] = {"label": row["config"]}
    if row.get("creative"):
        vals["color_mm4kygty"] = {"label": row["creative"]}
    set_columns(item_id, vals)
    if row.get("config"):
        set_columns(item_id, {"timerange_mm0vc5fk": {"from": due, "to": due}})
        # Config due mutation can clear Promo Time on some items — re-assert visibility window.
        set_columns(item_id, {"timerange_mkz3t5qy": {"from": iso_start, "to": iso_until}})
    return item_id


def fetch_august_index() -> dict[str, list[dict]]:
    """Map iso date -> non-Day items with that date_mky27nx7."""
    by_date: dict[str, list[dict]] = {}
    cursor = None
    for _ in range(35):
        q = """
        query ($cursor: String) {
          boards(ids: [18388590642]) {
            items_page(limit: 500, cursor: $cursor) {
              cursor
              items {
                id name
                column_values(ids: ["date_mky27nx7", "status"]) { id text }
              }
            }
          }
        }
        """
        page = gql(q, {"cursor": cursor})["boards"][0]["items_page"]
        for it in page["items"]:
            cols = {c["id"]: c.get("text") for c in it["column_values"]}
            iso = cols.get("date_mky27nx7")
            if not iso or not iso.startswith("2026-08"):
                continue
            if cols.get("status") == "Day":
                continue
            by_date.setdefault(iso, []).append(it)
        cursor = page.get("cursor")
        if not cursor:
            break
    return by_date


def match_existing(existing: list[dict], row: dict) -> str | None:
    target = row_key(row["name"])
    for ex in existing:
        if row_key(ex["name"]) == target:
            return ex["id"]
    return None


def delete_item(item_id: str) -> None:
    gql("mutation($id:ID!){delete_item(item_id:$id){id}}", {"id": item_id})


def dedupe_board_items(existing: list[dict], keep_ids: set[str]) -> list[str]:
    """Remove duplicate Monday items on same date (same row_key), keep matched rows."""
    by_key: dict[str, list[dict]] = {}
    for ex in existing:
        by_key.setdefault(row_key(ex["name"]), []).append(ex)
    removed_ids: list[str] = []
    for group in by_key.values():
        if len(group) < 2:
            continue
        group.sort(key=lambda x: x["id"])
        survivors = [g for g in group if g["id"] in keep_ids]
        keeper = survivors[0] if survivors else group[0]
        for g in group:
            if g["id"] == keeper["id"]:
                continue
            delete_item(g["id"])
            removed_ids.append(g["id"])
            time.sleep(0.05)
    return removed_ids


def sync_day(day: dict, existing: list[dict]) -> tuple[int, int, int]:
    rows = build_rows(day)
    created = updated = 0
    used: set[str] = set()
    for row in rows:
        pool = [e for e in existing if e["id"] not in used]
        eid = match_existing(pool, row)
        if eid:
            used.add(eid)
            ex = next(e for e in existing if e["id"] == eid)
            apply_row(row, item_id=eid)
            if ex["name"] != row["name"]:
                rename_item(eid, row["name"])
            updated += 1
        else:
            new_id = apply_row(row)
            used.add(new_id)
            existing.append({"id": new_id, "name": row["name"]})
            created += 1
        time.sleep(0.08)
    removed_ids = dedupe_board_items(existing, used)
    removed_ids.extend(remove_orphan_day_items(existing, used))
    stale_popup = remove_stale_popup_store_items(existing, used)
    removed_ids.extend(stale_popup)
    removed_ids.extend(remove_stale_combined_winovate_mega(existing, used))
    if removed_ids:
        dead = set(removed_ids)
        existing[:] = [e for e in existing if e["id"] not in dead]
    return created, updated, len(removed_ids)


def parse_day_range() -> list[int]:
    argv = sys.argv[1:]
    start, end = 1, 31
    has_from = "--from" in argv
    has_to = "--to" in argv
    if has_from:
        start = int(argv[argv.index("--from") + 1])
    if has_to:
        end = int(argv[argv.index("--to") + 1])
    if has_from or has_to or "--all" in argv:
        return list(range(start, end + 1))
    nums = [int(a) for a in argv if a.isdigit()]
    if nums:
        return nums
    return list(range(start, end + 1))


def main() -> None:
    plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    days = plan["days"]
    day_nums = parse_day_range()

    print("Indexing existing August items on board...", flush=True)
    by_date = fetch_august_index()
    total_c = total_u = total_r = 0
    for n in day_nums:
        day = next(d for d in days if d["date"] == n)
        iso = day["iso"]
        ex = by_date.get(iso, [])
        c, u, r = sync_day(day, ex)
        by_date[iso] = ex
        total_c += c
        total_u += u
        total_r += r
        print(f"{iso}: +{c} ~{u} -{r} dup (rows {len(build_rows(day))})", flush=True)

    print(f"Done. Created {total_c}, updated {total_u}, removed dupes {total_r}.")


if __name__ == "__main__":
    main()
