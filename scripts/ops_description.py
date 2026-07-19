#!/usr/bin/env python3
"""Promo-aware, natural-language description composer for Ops tasks."""

from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timedelta
from typing import Any, Iterable

OPS_BOARD_ID = "2109172490"


def normalize_name(value: str) -> str:
    value = re.sub(r"^\d{4}-\d{2}-\d{2}\s*\|\s*", "", value or "").strip()
    return re.sub(r"\s+", " ", value.replace("—", "-").replace("–", "-"))


def has_alias(text: str, alias: str) -> bool:
    escaped = re.escape(alias.strip()).replace(r"\ ", r"\s+")
    return bool(re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text))


def promo_family(name: str, product: str = "", detail: str = "") -> str:
    rules: list[tuple[str, tuple[str, ...]]] = [
        ("rlap", ("rlap", "stash booster")),
        ("ace_heist", ("ace heist",)),
        ("extreme_stamp", ("x2 extreme stamp",)),
        ("x2_ggs", ("x2 ggs",)),
        ("stickers_sources", ("sticker sources", "stickers sources")),
        ("happy_hour", ("hh -", "happy hour")),
        ("gatcha_promo", ("gatcha",)),
        ("golden_spin", ("golden spin",)),
        ("ads_personal_offer", ("ads po", "po ads", "ads personal offer")),
        ("daily_deal", ("daily deal", "daily_deal", "dd -")),
        ("rolling_offer", ("rolling offer", "buy more for less", "buy x get y", "bmfl", "bxgy")),
        ("ryd", (" ryd ", "reveal your deal")),
        ("buy_all", ("buy all",)),
        ("decoy_offer", ("decoy", "bonanza")),
        ("equal_offer", ("equal offer", "equal triple")),
        ("limited_po", ("limited po", "limited personal offer")),
        ("mgap", ("mgap", "make good any purchase")),
        ("prize_mania", ("prize mania",)),
        ("clan_dash", ("clan dash", "clan-dash", "dash pass")),
        ("shiny_show", ("shiny show",)),
        ("dice_promo", ("dice deluxe", "dice promotion")),
        ("lbp_lotto", (" lbp ", "lotto bonus premium", "lotto peak", "lotto - peak")),
        ("mes", ("m.e.s", " mes ", "mission event system", "win master")),
        (
            "gameplay",
            (
                "spin zone",
                "pick your path",
                "pyp",
                "custom pod",
                "battlesheep",
                "spinner clash",
                "piggy",
                " core ",
            ),
        ),
        ("season_blast", ("blast", "mid term", "short term", "album handover")),
        (
            "sales_store",
            ("coin sale", "gems sale", "gem sale", "coupon", "store denom", "biggest store"),
        ),
    ]
    texts = [
        f" {normalize_name(name)} {product} ".lower(),
        f" {detail[:300]} ".lower(),
    ]
    for text in texts:
        for family_name, aliases in rules:
            if any(has_alias(text, alias) for alias in aliases):
                return family_name
    return "other"


_INTERNAL_LINE_SKIP = re.compile(
    r"(?i)(?:^season rhythm:|^plan notes:|^window:\s*phase|full tables:|mm_calendar/|"
    r"nivi_collector_album|configure ranks in liveops|per nivi promo boundaries|"
    r"winovate scene milestones by album phase|mega pods freemium/premium milestones)"
)


def strip_internal_reference_noise(text: str) -> str:
    """Remove repo paths and internal doc references — not for Ops Description."""
    if not text:
        return text
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            out.append("")
            continue
        if _INTERNAL_LINE_SKIP.search(stripped):
            continue
        if re.match(r"^Collector'?s Album phase \d+", stripped, re.I):
            continue
        cleaned = _strip_internal_inline(stripped)
        if cleaned:
            out.append(cleaned)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out).strip()


def finalize_ops_description(text: str) -> str:
    return strip_internal_reference_noise((text or "").strip())


def _strip_internal_inline(value: str) -> str:
    patterns = [
        r"\.\s*Collector'?s Album phase \d+[^.\n]*(?:\.\s*Full tables:\s*\S+)?",
        r"\s*Full tables:\s*\S+",
        r"mm_calendar/\S+",
        r"nivi_collector_album_prizes\.md",
        r"(?i)\s*[—–-]?\s*configure ranks in liveops per \S+",
        r"(?i)\bsee nivi_collector[^\s]*",
        r"(?i)\bper nivi_collector[^\s]*",
        r"(?i)\bper nivi promo boundaries[^.]*",
    ]
    result = value
    for pat in patterns:
        result = re.sub(pat, "", result)
    result = re.sub(r"\s+", " ", result).strip().rstrip(".,;")
    return result


def clean_detail(value: str) -> str:
    if value.strip() == "Required mechanic/config details are missing from the MM source.":
        return ""
    lines: list[str] = []
    for raw_line in (value or "").splitlines():
        line = raw_line.strip()
        if not line:
            if lines and lines[-1]:
                lines.append("")
            continue
        if re.search(r"\b20\d{2}-\d{2}-\d{2}\b|\b(?:start|end)\s*:?\s*\d", line, re.I):
            continue
        if re.match(r"^(?:duration|pricing)\s*:", line, re.I) or re.fullmatch(
            r"(?:all day|production)", line, re.I
        ):
            continue
        if re.search(r"\breset\b.*\b\d{1,2}:\d{2}\b", line, re.I):
            continue
        if re.search(
            r"\b(?:once(?:-|\s+)per(?:-|\s+)player|multiple(?:\s+(?:times|purchases))?)\b",
            line,
            re.I,
        ):
            continue
        if _INTERNAL_LINE_SKIP.search(line):
            continue
        if re.match(r"^Collector'?s Album phase \d+", line, re.I):
            continue
        inline = _strip_internal_inline(line)
        if inline:
            lines.append(inline)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines).strip()


def sentence(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        return value
    return value if value[-1] in ".!?" else f"{value}."


def price_label(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.strip().lower().replace(" pricing", "").replace(" price", "")
    mapping = {"h": "High", "m": "Mid", "max": "Max", "l": "Low"}
    return mapping.get(normalized, normalized.title())


PRICING_IN_TITLE_RE = re.compile(
    r"(?:"
    r"\|\s*[^|]*\b(?:price|pricing)\b"
    r"|\b(?:high|mid|max|low)\s+(?:price|pricing)\b"
    r"|\b(?:h|m|l)\s+price\b"
    r"|\|\s*(?:h|m|l|max)\s*,\s*(?:h|m|l|max)"
    r")",
    re.I,
)


def title_mentions_pricing(name: str) -> bool:
    return bool(PRICING_IN_TITLE_RE.search(normalize_name(name)))


def pricing_title_suffix(mm_pricing: str | None) -> str:
    if not mm_pricing or not mm_pricing.strip():
        return ""
    raw = mm_pricing.strip().lower()
    mapping = {
        "high": "H Pricing",
        "mid": "M Pricing",
        "max": "Max Pricing",
        "low": "L Pricing",
        "h": "H Pricing",
        "m": "M Pricing",
        "l": "L Pricing",
    }
    if raw in mapping:
        return f"| {mapping[raw]}"
    letter = price_label(mm_pricing)
    if letter in {"High", "Mid", "Max", "Low"}:
        short = {"High": "H", "Mid": "M", "Max": "Max", "Low": "L"}[letter]
        return f"| {short} Pricing"
    return f"| {letter} Pricing"


def reference_parts(reference: str | None) -> dict[str, str]:
    value = reference or ""
    match = re.search(r"(?P<date>20\d{2}-\d{2}-\d{2})\s+item\s+(?P<id>\d+)", value)
    if not match:
        return {}
    remainder = value[match.end() :].strip()
    name = remainder[1:-1].strip() if remainder.startswith("(") and remainder.endswith(")") else ""
    return {
        "date": match.group("date"),
        "id": match.group("id"),
        "name": name,
    }


def duplicate_line(reference: str | None, reuse: bool | None) -> str:
    parts = reference_parts(reference)
    if not parts:
        if reuse is False:
            return "No verified recent task to duplicate."
        return "Duplicate source: TBD - verify the newest exact task in the three-month window."
    label = parts["name"] or "matching Ops task"
    link = f"https://playtika.monday.com/boards/{OPS_BOARD_ID}/pulses/{parts['id']}"
    if reuse:
        return f"Duplicate from: {label}, {parts['date']} ({link})."
    return f"Structure reference only: {label}, {parts['date']} ({link}); do not duplicate until the variant is confirmed."


def template_line(template_source: dict[str, str] | None, reuse: bool | None) -> str:
    if not template_source or reuse:
        return ""
    title = template_source.get("group_title") or "matching offer"
    return f"If no exact dated task exists, start from the {title} template group."


def change_line(task_name: str, reference: str | None, reuse: bool | None) -> str:
    if not reuse:
        return ""
    parts = reference_parts(reference)
    source_name = normalize_name(parts.get("name") or "")
    current_name = normalize_name(task_name)
    if not source_name or source_name.lower() == current_name.lower():
        return ""
    return f"Change: {source_name} → {current_name}."


def opening_line(family: str, task_name: str, pricing: str | None) -> str:
    name = normalize_name(task_name)
    price = price_label(pricing)
    if family == "daily_deal":
        return f"Set up a {price + '-price ' if price else ''}Daily Deal."
    if family == "rolling_offer":
        return f"Set up {name}{f' at {price} price' if price else ''}."
    if family == "ryd":
        return f"Set up {name}{f' at {price} price' if price else ''}."
    if family in {"buy_all", "decoy_offer", "equal_offer", "limited_po", "mgap"}:
        return f"Set up {name}{f' at {price} price' if price else ''}."
    if family == "ads_personal_offer":
        return f"Set up {name} for the eligible ADS audience."
    if family == "rlap":
        return f"Set up {name} using the approved Stash Booster / RLAP configuration."
    if family == "stickers_sources":
        return f"Publish {name} with the approved source list and art."
    if family == "mes":
        return f"Set up {name} in M.E.S."
    if family == "clan_dash":
        return f"Update the {name} Clan Dash component."
    if family == "gameplay":
        return f"Set up {name}."
    if family == "shiny_show":
        return f"Open {name}."
    if family == "season_blast":
        return f"Open {name}."
    if family == "lbp_lotto":
        return f"Open {name}."
    if family == "sales_store":
        return f"Set up {name}."
    return f"Set up {name}."


def dependency_lines(
    missing: Iterable[str] = (),
    config_status: str | None = None,
    creative_label: str | None = None,
) -> list[str]:
    lines: list[str] = []
    for entry in missing:
        cleaned = entry.strip().rstrip(".")
        if cleaned and cleaned not in lines:
            lines.append(cleaned)
    if config_status and config_status not in {"Config not needed", "No config needed"}:
        line = f"Config: {config_status}"
        if not any(item.lower().startswith("config:") for item in lines):
            lines.append(line)
    if creative_label and creative_label not in {"Reuse", "Completed"}:
        line = f"Art: {creative_label}"
        if not any(item.lower().startswith("art:") for item in lines):
            lines.append(line)
    return lines


OFFER_FAMILIES = {
    "daily_deal",
    "ryd",
    "buy_all",
    "decoy_offer",
    "equal_offer",
    "limited_po",
    "ads_personal_offer",
    "prize_mania",
    "counter_po",
}

VARIANT_FAMILIES = {
    "mgap",
    "shiny_show",
    "golden_spin",
    "lbp_lotto",
    "dice_promo",
}

GAMEPLAY_RANK_PRIZE_FEATURES = (
    "spinner clash",
    "battlesheep",
    "snl",
    "blast",
    "winovate",
    "globez",
)


def is_offer_family(family: str) -> bool:
    return family in OFFER_FAMILIES


def apply_pricing_to_ops_task_name(
    task_name: str,
    pricing: str | None,
    *,
    product: str = "",
    detail: str = "",
) -> str:
    """Append `| H Pricing` (etc.) when MM pricing is set and the title omits it."""
    base = normalize_name(task_name)
    if not pricing or title_mentions_pricing(base):
        return base
    family = promo_family(base, product, detail)
    if family not in OFFER_FAMILIES and family != "rolling_offer":
        return base
    suffix = pricing_title_suffix(pricing)
    return f"{base} {suffix}".strip() if suffix else base


MAIN_OFFER_FAMILIES = {
    "rolling_offer",
    "ryd",
    "buy_all",
    "decoy_offer",
    "equal_offer",
    "limited_po",
    "counter_po",
}

MAIN_OFFER_RESET_LINE = "Reset at 00:00 UTC"

REGULAR_SALE_PRAS_GEMS_BONUS = 20
REGULAR_SALE_PRAS_COINS_BONUS = 25


def is_coupon_task(task_name: str, detail: str) -> bool:
    return bool(re.search(r"\bcoupon\b", f"{task_name}\n{detail}", re.I))


def parse_coupon_percents(task_name: str, detail: str) -> tuple[int, int] | None:
    blob = f"{task_name}\n{detail}"
    match = re.search(r"(\d+)\s*%\s*/\s*(\d+)\s*%", blob, re.I)
    if match:
        return int(match.group(1)), int(match.group(2))
    match = re.search(r"(\d+)\s*/\s*(\d+)\s*%", blob, re.I)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None


def parse_pu_sale_percents(task_name: str, detail: str) -> tuple[int, int] | None:
    if is_coupon_task(task_name, detail):
        return None
    blob = f"{task_name}\n{detail}"
    match = re.search(r"(\d+)\s*%\s*store\s*/\s*(\d+)\s*%\s*offers?", blob, re.I)
    if match:
        return int(match.group(1)), int(match.group(2))
    match = re.search(r"(\d+)\s*%\s*store\s*/\s*(\d+)\s*offers?", blob, re.I)
    if match:
        return int(match.group(1)), int(match.group(2))
    if re.search(r"\bstore\b|\boffers?\b", blob, re.I):
        match = re.search(r"(\d+)\s*%\s*/\s*(\d+)\s*%", blob, re.I)
        if match:
            return int(match.group(1)), int(match.group(2))
    return None


def pras_sale_bonus(currency: str) -> int:
    if currency == "Coins":
        return REGULAR_SALE_PRAS_COINS_BONUS
    return REGULAR_SALE_PRAS_GEMS_BONUS


def format_pu_amount(store_pct: int, offers_pct: int) -> str:
    return f"{store_pct}% store | {offers_pct}% offers"


def format_pras_amount(store_pct: int, offers_pct: int, currency: str) -> str:
    bonus = pras_sale_bonus(currency)
    store_pras = store_pct + bonus
    offers_pras = offers_pct + bonus
    return (
        f"{store_pras}% ({store_pct}+{bonus}) store | "
        f"{offers_pras}% ({offers_pct}+{bonus}) offers"
    )


def compose_sales_store_description(task_name: str, detail: str) -> str:
    currency = sales_currency(task_name, detail)
    if is_coupon_task(task_name, detail):
        coupon = parse_coupon_percents(task_name, detail)
        if coupon:
            pu_pct, pras_pct = coupon
            return finalize_ops_description(
                "\n".join(
                    [
                        f"Currency: {currency}",
                        "Segment: PU",
                        f"Amount: {pu_pct}%",
                        "Segment: PRAS",
                        f"Amount: {pras_pct}%",
                    ]
                ).strip()
            )
    percents = parse_pu_sale_percents(task_name, detail)
    if not percents:
        return finalize_ops_description(
            "\n".join(
                [
                    f"Currency: {currency}",
                    "Segment: PU",
                    f"Amount: {sales_amount(task_name, detail)}",
                    "Segment: PRAS",
                    "Amount: Not specified in MM source",
                ]
            ).strip()
        )
    store_pct, offers_pct = percents
    return finalize_ops_description(
        "\n".join(
            [
                f"Currency: {currency}",
                "Segment: PU",
                f"Amount: {format_pu_amount(store_pct, offers_pct)}",
                "Segment: PRAS",
                f"Amount: {format_pras_amount(store_pct, offers_pct, currency)}",
            ]
        ).strip()
    )


def should_omit_times_per_player(task_name: str, product: str = "", detail: str = "") -> bool:
    if is_machine_launch_task(task_name, product):
        return True
    prod = (product or "").strip().lower()
    if prod in {"short term", "mid term", "season", "long term"}:
        return True
    if "short term" in prod or "mid term" in prod:
        return True
    name = normalize_name(task_name).lower()
    if name.endswith(" season") or re.search(r"\bseason\b", name):
        return True
    if family := promo_family(task_name, product, detail):
        if family in {"season_blast", "extreme_stamp"} and not re.search(
            r"\b(?:coin sale|gems sale|gem sale|coupon|store denom)\b", name
        ):
            return True
    return False


def is_main_offer(family: str, task_name: str) -> bool:
    if family in {"daily_deal", "rlap", "ads_personal_offer", "sales_store"}:
        return False
    if family == "prize_mania":
        return True
    if family in MAIN_OFFER_FAMILIES:
        return True
    return "prize mania" in normalize_name(task_name).lower()


def with_main_offer_reset(lines: list[str], family: str, task_name: str) -> str:
    body = "\n".join(lines).strip()
    if is_main_offer(family, task_name):
        body = f"{MAIN_OFFER_RESET_LINE}\n\n{body}".strip()
    return finalize_ops_description(body)


def infer_times_per_player(*, task_name: str, product: str = "", detail: str = "") -> str | None:
    if should_omit_times_per_player(task_name, product, detail):
        return None
    text = detail or ""
    if re.search(r"once\s*(?:per|-)\s*player", text, re.I):
        return "Once"
    if re.search(r"multiple\s*(?:times\s*)?(?:per\s*player)?", text, re.I):
        return "Multiple"
    name_lower = normalize_name(task_name).lower()
    if "piggy" in name_lower:
        return "Once"
    if "win master" in name_lower:
        return "Once"
    family = promo_family(task_name, product, detail)
    if family == "daily_deal":
        if re.search(r"\bonce\b", name_lower):
            return "Once"
        return "Multiple"
    if is_main_offer(family, task_name):
        return "Once"
    return "Multiple"


def sales_currency(task_name: str, detail: str) -> str:
    blob = f"{task_name}\n{detail}".lower()
    if re.search(r"\bgems?\s+sale\b|\bgems\b", blob) and "coin" not in blob.split("gems")[0][-20:]:
        if "coin" in blob and "gems sale" not in blob:
            return "Coins and Gems"
    if "gems" in blob:
        return "Gems"
    if "coin" in blob:
        return "Coins"
    return "Not specified in MM source"


def sales_amount(task_name: str, detail: str) -> str:
    blob = f"{task_name}\n{detail}"
    for pattern in (
        r"(\d+%\s*store\s*/\s*\d+%\s*offers?)",
        r"(\d+%\s*/\s*\d+%)",
        r"(\d+%\s+store\s*/\s*\d+\s*offers?)",
    ):
        match = re.search(pattern, blob, re.I)
        if match:
            return match.group(1).strip()
    dash = re.search(r"[—–-]\s*(.+)$", normalize_name(task_name))
    if dash:
        return dash.group(1).strip()
    cleaned = clean_detail(detail)
    return cleaned.splitlines()[0] if cleaned else "Not specified in MM source"


def prize_mania_bundle_prizes(detail: str, task_name: str) -> str:
    for line in (detail or "").splitlines():
        match = re.match(r"^\s*Bundle\s*:\s*(.+)$", line, re.I)
        if match:
            return sanitize_prize_text(match.group(1).strip())
    match = re.search(r"Bundle:\s*(.+)", detail or "", re.I)
    if match:
        return sanitize_prize_text(match.group(1).strip())
    parts: list[str] = []
    for raw in (detail or "").splitlines():
        line = raw.strip().strip(",")
        if not line or re.match(r"^prize mania\b", line, re.I):
            continue
        if re.match(r"^h\s*price\b", line, re.I):
            continue
        parts.append(line)
    if parts:
        return sanitize_prize_text(", ".join(parts))
    return sanitize_prize_text(name_payload(task_name, "prize_mania"))


def rlap_eligible_offers(detail: str) -> str:
    triggers = labeled_values(detail, ("triggers", "trigger"))
    if triggers:
        return triggers[0]
    return "Not specified in MM source"


def rlap_reward_lines(detail: str) -> str:
    lines_out: list[str] = []
    for raw in (detail or "").splitlines():
        line = raw.strip()
        if re.match(r"^CZ\s", line, re.I):
            lines_out.append(line.rstrip("."))
    if lines_out:
        return "\n".join(lines_out)
    labeled = labeled_values(detail, ("prize", "prizes", "reward", "rewards"))
    if labeled:
        return "\n".join(dict.fromkeys(labeled))
    return "Not specified in MM source"


def sanitize_prize_text(value: str) -> str:
    """Strip pricing boilerplate and 'Central reward' wording from prize lines."""
    text = (value or "").strip()
    if not text:
        return text
    text = re.sub(r"(?i)^central reward\s*:?\s*", "", text)
    text = re.sub(
        r"(?i)\s*\(\s*(?:high|mid|max|low|h|m|l)\s*(?:price|pricing)\s*\)\s*\.?\s*$",
        "",
        text,
    )
    text = re.sub(
        r"(?i)\s*\|\s*(?:high|mid|max|low|h|m|l)\s*(?:price|pricing)\s*$",
        "",
        text,
    )
    text = re.sub(r"(?i)\s+(?:high|mid|max|low|h|m|l)\s+pricing\s*$", "", text)
    text = re.sub(r"\s+", " ", text).strip().rstrip(".")
    return _strip_internal_inline(text)


def segment_value(task_name: str, detail: str, family: str = "") -> str:
    text = f"{task_name}\n{detail}"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = re.match(r"^(?:segment|audience|open to)\s*:?\s*(.+)$", line, re.I)
        if match and match.group(1).strip():
            return match.group(1).strip().rstrip(".")
        if re.search(r"\b(?:all players|all users|all eligible players)\b", line, re.I):
            return "All Users"
    segment_tokens = re.findall(r"\b(?:DPU|NPU|PU|PRAS|IC|BD|Black Diamond)\b", task_name, re.I)
    if segment_tokens:
        return " / ".join(dict.fromkeys(token.upper() for token in segment_tokens))
    if family == "ads_personal_offer":
        return "ADS Segment"
    return "All Users"


def name_payload(task_name: str, family: str) -> str:
    value = normalize_name(task_name)
    prefixes = {
        "daily_deal": r"^(?:daily deal|dd)\s*[-|:]?\s*",
        "ryd": r"^(?:ryd|reveal your deal)\s*[-|:]?\s*",
        "buy_all": r"^buy all\s*[-|:]?\s*",
        "decoy_offer": r"^(?:decoy|bonanza)\s*[-|:]?\s*",
        "limited_po": r"^limited (?:po|personal offer)\s*[-|:]?\s*",
        "ads_personal_offer": r"^(?:ads po|po ads)\s*[-|:]?\s*",
    }
    value = re.sub(prefixes.get(family, r"$^"), "", value, flags=re.I)
    value = re.sub(
        r"\s*(?:\||-)\s*(?:high|mid|max|low|h|m|l)\s*(?:price|pricing)\b.*$",
        "",
        value,
        flags=re.I,
    )
    return value.strip(" -|") or "Not specified in MM source"


def offer_prizes(task_name: str, family: str, detail: str) -> str:
    lower = task_name.lower()
    if family == "mgap":
        if "bogo" in lower:
            return "Matching BOGO per approved config"
        if "bigger" in lower:
            return "Bigger multipliers per approved config"
        if "matched" in lower:
            return "Matched multiplier per approved config"
        if "wild" in lower:
            return "Wild symbols per approved config"
    if family == "prize_mania":
        return prize_mania_bundle_prizes(detail, task_name)
    if family == "ads_personal_offer":
        return sanitize_prize_text(name_payload(task_name, family))
    cleaned = clean_detail(detail)
    kept: list[str] = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if not stripped:
            if kept and kept[-1]:
                kept.append("")
            continue
        if re.match(
            r"^(?:platform|season context|short term|mid term|album context|purchase rule|"
            r"trigger|condition|action\d*|flow|config|art|re-use|reuse)\s*:",
            stripped,
            re.I,
        ):
            continue
        if re.match(r"^(?:daily deal|ryd|rolling\b|buy all)\b", stripped, re.I):
            continue
        kept.append(stripped)
    while kept and not kept[-1]:
        kept.pop()
    result = "\n".join(kept).strip()
    payload = sanitize_prize_text(result or name_payload(task_name, family))
    if family == "daily_deal" and payload:
        payload = re.sub(r"\s*[-–—]\s*(?:fallback|once)\s*$", "", payload, flags=re.I).strip()
    return payload or "Not specified in MM source"


def labeled_values(detail: str, labels: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    pattern = "|".join(re.escape(label) for label in labels)
    for line in (detail or "").splitlines():
        match = re.match(rf"^\s*(?:{pattern})\s*\d*\s*[:\-]\s*(.+)$", line, re.I)
        if match and match.group(1).strip():
            values.append(match.group(1).strip().rstrip("."))
    return values


def mission_values(detail: str) -> list[str]:
    missions: list[str] = []
    in_missions = False
    for raw_line in (detail or "").splitlines():
        line = raw_line.strip()
        if re.match(r"^missions?\s*:", line, re.I):
            in_missions = True
            remainder = line.split(":", 1)[1].strip()
            if remainder:
                missions.append(remainder)
            continue
        if not in_missions:
            continue
        if not line:
            if missions:
                break
            continue
        if re.match(r"^[A-Za-z][A-Za-z /&_-]+\s*:", line) and not re.match(
            r"^(?:mission\s*\d+|[·•*-]|\d+[.)])", line, re.I
        ):
            break
        cleaned = re.sub(r"^(?:[·•*-]|\d+[.)])\s*", "", line).strip()
        if cleaned:
            missions.append(cleaned)
    return missions


def trigger_value(task_name: str, family: str, detail: str) -> str:
    if family == "gameplay" and re.search(r"\b(?:ace heist|pyp|pick your path)\b", task_name, re.I):
        missions = mission_values(detail)
        if missions:
            return " → ".join(missions)
    triggers = labeled_values(detail, ("trigger", "triggers", "condition"))
    if triggers:
        return "; ".join(dict.fromkeys(triggers))
    lower = task_name.lower()
    if family == "ads_personal_offer":
        return "Eligible player watches an ad"
    if "piggy" in lower and "break" in lower:
        return "Player breaks the Piggy"
    if family == "mes" and "win master" in lower:
        return "Player completes the configured win requirement"
    if family == "mgap":
        return "Player purchases an eligible MGAP tier"
    if family == "shiny_show":
        return "Player completes the configured Shiny Show requirement"
    if family == "lbp_lotto":
        return "Eligible player participates during the scheduled Lotto/LBP window"
    return "Not specified in MM source"


def action_value(task_name: str, family: str, detail: str) -> str:
    actions = labeled_values(detail, ("action", "actions"))
    if actions:
        return "; ".join(dict.fromkeys(actions))
    lower = task_name.lower()
    payload = name_payload(task_name, family)
    if family == "ads_personal_offer":
        return f"Give {payload}"
    if "piggy" in lower and " for " in lower:
        return f"Give {task_name.split(' for ', 1)[1]}"
    if family == "mes" and "win master" in lower:
        reward = task_name.split(" - ", 1)[1] if " - " in task_name else "the listed rewards"
        return (
            f"Give {reward}; show the winner inapp; "
            "if the configuration is linear, give the next mission"
        )
    if family == "mgap":
        if "bogo" in lower:
            return "Grant the BOGO reward according to the approved MGAP config"
        if "bigger" in lower:
            return "Apply the approved bigger multipliers and show the matching winner state"
    if family == "shiny_show":
        return "Grant the configured rewards and show the matching winner state"
    if family == "lbp_lotto":
        mechanic = re.sub(r"\s*\(night plan(?: peak)?\)", "", task_name, flags=re.I)
        return f"Apply {mechanic}"
    if family == "stickers_sources":
        return "Show the approved daily Sticker Sources in the inapp"
    return "Not specified in MM source"


def config_value(
    reference: str | None,
    reuse: bool | None,
    template_source: dict[str, str] | None,
    config_status: str | None,
) -> str:
    source = duplicate_line(reference, reuse)
    fallback = template_line(template_source, reuse)
    status = config_status or ""
    parts = [source]
    if fallback:
        parts.append(fallback)
    if status and status not in {"Config not needed", "No config needed"}:
        parts.append(f"Status: {status}.")
    return " ".join(parts)


def rank_prize_lines(detail: str) -> list[str]:
    lines_out: list[str] = []
    for raw in (detail or "").splitlines():
        line = raw.strip()
        match = re.match(r"^(\d+(?:st|nd|rd|th))\s*:\s*(.+)$", line, re.I)
        if match:
            prize = _strip_internal_inline(match.group(2).strip().rstrip("."))
            lines_out.append(f"{match.group(1)}: {prize}")
    return lines_out


def _append_rolling_cycle_header(out: list[str], cycle_num: str) -> None:
    header = f"Cycle {cycle_num}:"
    if out and out[-1] != "":
        out.append("")
    out.append(header)


def rolling_denom_lines(detail: str) -> list[str]:
    """Cycle headers plus numbered denoms (global index across the offer)."""
    structured = _rolling_denom_structured(detail)
    if structured:
        return structured
    return _rolling_denom_prose(detail)


def _rolling_denom_structured(detail: str) -> list[str]:
    out: list[str] = []
    index = 0
    for raw in (detail or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        cycle_match = re.match(r"^cycle\s+(\d+)\s*:?\s*$", line, re.I)
        if cycle_match:
            _append_rolling_cycle_header(out, cycle_match.group(1))
            continue
        label = reward = ""
        match = re.match(r"^(\d+)\s+(Buy|Free)\s+(.+)$", line, re.I)
        if match:
            label = "Pay" if match.group(2).lower() == "buy" else "Free"
            reward = match.group(3).strip()
        else:
            pay = re.match(r"^(\d+)\s+Pay\s*[—–-]\s*(.+)$", line, re.I)
            if pay:
                label = "Pay"
                reward = pay.group(2).strip()
            else:
                free = re.match(r"^(\d+)\s*[—–-]\s*(.+)$", line)
                if free:
                    label = "Free"
                    reward = free.group(2).strip()
                else:
                    parts = [part.strip() for part in re.split(r"\t+", line) if part.strip()]
                    if len(parts) >= 3 and parts[0].isdigit() and parts[1].lower() in {
                        "buy",
                        "free",
                        "pay",
                    }:
                        label = "Pay" if parts[1].lower() in {"buy", "pay"} else "Free"
                        reward = " ".join(parts[2:])
        if not label:
            continue
        if index == 0 and not (out and out[-1].endswith(":")):
            _append_rolling_cycle_header(out, "1")
        index += 1
        out.append(f"{index} {label}: {reward}")
    return out


def _rolling_denom_prose(detail: str) -> list[str]:
    out: list[str] = []
    index = 0
    current_cycle: str | None = None

    def ensure_cycle_header() -> None:
        nonlocal current_cycle
        if current_cycle is None:
            current_cycle = "1"
        header = f"Cycle {current_cycle}:"
        if not out:
            _append_rolling_cycle_header(out, current_cycle)
            return
        if out[-1] == header:
            return
        if out[-1].endswith(":"):
            return

    for raw in (detail or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.match(r"^rolling offer\b", line, re.I):
            continue
        if re.search(r"^h price\b", line, re.I):
            continue
        if re.match(r"^pay with cash\b", line, re.I):
            continue
        cycle_match = re.match(r"^(\d+)\s+cycle\b", line, re.I)
        if cycle_match:
            current_cycle = cycle_match.group(1)
            _append_rolling_cycle_header(out, current_cycle)
            continue
        pay_cash = re.match(r"^pay cash denom\s*[-–—]\s*(.+)$", line, re.I)
        if pay_cash:
            ensure_cycle_header()
            index += 1
            out.append(f"{index} Pay: {pay_cash.group(1).strip()}")
            continue
        pay_sb = re.match(r"^pay with SB\s*[-–—]\s*(.+)$", line, re.I)
        if pay_sb:
            ensure_cycle_header()
            index += 1
            out.append(f"{index} Pay (SB): {pay_sb.group(1).strip()}")
            continue
        free = re.match(r"^free\s*[-–—]\s*(.+)$", line, re.I)
        if free:
            ensure_cycle_header()
            index += 1
            out.append(f"{index} Free: {free.group(1).strip()}")
    return out


def ace_heist_final_prize(task_name: str, detail: str) -> str:
    for line in (detail or "").splitlines():
        match = re.match(r"^Ace Heist\s*[—–-]\s*(.+)$", line.strip(), re.I)
        if match:
            return sanitize_prize_text(match.group(1).strip())
    name = normalize_name(task_name)
    if " - " in name:
        return sanitize_prize_text(name.split(" - ", 1)[1])
    if " — " in name:
        return sanitize_prize_text(name.split(" — ", 1)[1])
    return sanitize_prize_text(name_payload(name, "ace_heist"))


def compose_ace_heist_description(task_name: str, detail: str, segment: str) -> str:
    missions = mission_values(detail)
    prize = ace_heist_final_prize(task_name, detail)
    lines = [f"Segment: {segment}", "Missions:"]
    if missions:
        for index, mission in enumerate(missions, start=1):
            lines.append(f"{index}. {mission}")
    else:
        lines.append("Not specified in MM source — add the three Ace Heist missions from the approved calendar row")
    lines.append(
        "Flow: Linear three-mission Ace Heist — after each mission show winner inapp and update widget; "
        "after mission 3 grant the final prize and close banner / NF / journey surfaces"
    )
    lines.append(f"Prize: {prize}")
    return finalize_ops_description("\n".join(lines).strip())


def compose_stickers_sources_description(task_name: str, detail: str, segment: str) -> str:
    _ = task_name
    lines = [f"Segment: {segment}", "Prize:"]
    found = False
    for raw in (detail or "").splitlines():
        match = re.match(r"^\s*(\d+)\.\s*(.+)$", raw.strip())
        if match:
            lines.append(f"{match.group(1)}. {match.group(2).strip()}")
            found = True
    if not found:
        cleaned = clean_detail(detail)
        if cleaned:
            lines.append(cleaned)
        else:
            lines.append("Not specified in MM source")
    return finalize_ops_description("\n".join(lines).strip())


def is_x2_ggs_promo(task_name: str, product: str = "", detail: str = "") -> bool:
    text = f" {normalize_name(task_name)} {product} {detail} ".lower()
    return has_alias(text, "x2 ggs")


def ui_reminder_lines(*, family: str, task_name: str) -> list[str]:
    """Ops voice from historical tasks (MGAP UI subitems, X2 GGS buy_all sample)."""
    name = normalize_name(task_name).lower()
    if family == "mgap":
        if any(term in name for term in ("matched", "wild", "bogo")) or "extreme" in name or "epic" in name:
            return ["Make sure to set UI for both Extreme + Epic"]
        return ["don't forget UI"]
    if family == "extreme_stamp":
        return ["don't forget UI"]
    if family == "x2_ggs" or is_x2_ggs_promo(task_name):
        return ["don't forget UI", "please add timer to the inapp"]
    return []


def append_ui_reminder(description: str, *, task_name: str, product: str = "", detail: str = "") -> str:
    family = promo_family(task_name, product, detail)
    extras = ui_reminder_lines(family=family, task_name=task_name)
    if not extras:
        return description
    blob = (description or "").lower()
    if "don't forget ui" in blob or "make sure to set ui" in blob:
        return description
    lines = [description.rstrip(), *extras]
    return "\n".join(line for line in lines if line).strip()


def compose_extreme_stamp_description(task_name: str, detail: str, segment: str) -> str:
    _ = (task_name, detail)
    body = append_ui_reminder(
        f"Segment: {segment}",
        task_name=task_name,
        product="Extreme stamp",
        detail=detail,
    )
    return finalize_ops_description(body)


def compose_mechanism_promo_description(task_name: str, detail: str, segment: str) -> str:
    _ = task_name
    body = clean_detail(detail)
    lines = [f"Segment: {segment}"]
    if body:
        for chunk in body.splitlines():
            chunk = chunk.strip()
            if chunk:
                lines.append(f"Trigger: {chunk}")
    else:
        lines.append("Trigger: Not specified in MM source")
    return finalize_ops_description("\n".join(lines).strip())


def is_machine_launch_task(task_name: str, product: str = "") -> bool:
    name = normalize_name(task_name).lower()
    prod = (product or "").strip().lower()
    skip = (
        "progress pack",
        "golden spin",
        "rlap",
        "stash booster",
        "mes full",
        "safe busters",
        "wild goddesses",
    )
    if any(term in name for term in skip):
        return False
    if prod == "event" and "machine" in name and "launch" in name:
        return True
    if "machine" in name and re.search(r"full launch|\blaunch\b", name):
        return True
    return False


OPS_HANDOFF_PLACEHOLDER = "Not specified in MM source"


def ops_handoff_sufficient(
    *,
    task_name: str,
    product: str = "",
    detail: str = "",
    mm_description: str = "",
    composed_description: str = "",
) -> bool:
    """True when Ops can work from MM Name (+ optional Description) without More Info."""
    if (mm_description or "").strip():
        return True
    if is_machine_launch_task(task_name, product):
        return True
    family = promo_family(task_name, product, detail)
    name = normalize_name(task_name)
    name_lower = name.lower()
    if family == "daily_deal":
        prizes = offer_prizes(task_name, family, detail)
        if prizes and prizes != OPS_HANDOFF_PLACEHOLDER:
            return True
        payload = name_payload(task_name, family)
        if payload and payload != OPS_HANDOFF_PLACEHOLDER:
            return True
    if "win master" in name_lower:
        prize = promotion_prize(task_name, family, detail)
        if prize and prize != OPS_HANDOFF_PLACEHOLDER:
            return True
    if has_alias(name_lower, "spinner clash"):
        if gameplay_rank_prizes(task_name, detail):
            return True
        if re.search(r"\btournament\b|\b6\s*hr\b|\b6-hour\b", detail or "", re.I):
            return True
    if composed_description.strip():
        critical_prefixes = ("Prize:", "Prizes:", "Trigger:", "Action:", "Variant:", "Denoms:")
        critical = [
            line
            for line in composed_description.splitlines()
            if line.startswith(critical_prefixes)
        ]
        if critical and all(OPS_HANDOFF_PLACEHOLDER not in line for line in critical):
            return True
        if OPS_HANDOFF_PLACEHOLDER not in composed_description:
            return True
    return False


def compose_spinner_clash_description(task_name: str, detail: str, segment: str) -> str:
    """Spinner Clash — 6hr tournament cadence (matches historical Ops handoffs)."""
    _ = task_name
    lines = [
        f"Segment: {segment}",
        "4 consecutive tournaments of 6hr each; when a tournament ends a new one starts (24h total).",
        "Config attached in economy task",
    ]
    rank_block = gameplay_rank_prizes(task_name, detail)
    if rank_block:
        lines.append("Prize:")
        lines.extend(rank_block.splitlines())
    else:
        prize = promotion_prize(task_name, "gameplay", detail)
        if prize and prize != OPS_HANDOFF_PLACEHOLDER:
            if "\n" in prize:
                lines.append("Prize:")
                lines.extend(prize.splitlines())
            else:
                lines.append(f"Prize: {prize}")
    trigger_blob = clean_detail(detail)
    if re.search(r"trigger", trigger_blob, re.I):
        for raw in trigger_blob.splitlines():
            if re.match(r"^\s*trigger", raw, re.I):
                lines.append(f"Trigger: {raw.split(':', 1)[-1].strip()}")
                break
    return finalize_ops_description("\n".join(lines).strip())


def compose_machine_launch_description(task_name: str, detail: str, segment: str) -> str:
    """New slot machine full launch — aligned with prior Ops launch tasks (inapp + playlists + DF)."""
    _ = task_name
    lines = [
        f"Segment: {segment}",
        "Action:",
        "Open the new machine to all players:",
        "1. Widget — open Main Inapp (Reg / Scrolldown / UV per approved creative)",
        "2. Add the machine to Figz and Winovate playlist",
        "3. New Machines DF — Big (Day 1+2) and Small (Day 3) per launch playbook",
        "4. CTA Reg → machine · UV → app store / Google Play",
    ]
    note = clean_detail(detail)
    if note and not note.startswith("Required mechanic"):
        lines.append(f"Note: {note.replace(chr(10), ' ')}")
    return finalize_ops_description("\n".join(lines).strip())


def variant_value(task_name: str, family: str, detail: str) -> str:
    name = normalize_name(task_name)
    lower = name.lower()
    if family == "mgap":
        if "bogo" in lower:
            return "BOGO"
        if "bigger" in lower:
            return "Bigger multipliers"
        if "matched" in lower:
            return "Matched multiplier"
        if "wild" in lower:
            return "Wild symbols"
        for line in (detail or "").splitlines():
            cleaned = line.strip()
            if cleaned and not re.match(r"^(?:liveops|config)\b", cleaned, re.I):
                return cleaned.rstrip(".")
        return name or "Not specified in MM source"
    if family == "golden_spin":
        match = re.search(r"golden spin\s*[-–—]\s*(.+)$", name, re.I)
        if match:
            return match.group(1).strip().rstrip(".")
        parts = [part.strip() for part in name.split("|")]
        if len(parts) > 1:
            return " | ".join(parts[1:])
        return sanitize_prize_text(name_payload(name, family))
    if family == "shiny_show":
        if " - " in name:
            return sanitize_prize_text(name.split(" - ", 1)[1])
        match = re.search(r"variant\s*:\s*(.+)$", detail or "", re.I | re.M)
        if match:
            return match.group(1).strip().rstrip(".")
        return sanitize_prize_text(name_payload(name, family))
    if family == "lbp_lotto":
        mechanic = re.sub(r"\s*\(night plan(?: peak)?\)", "", name, flags=re.I)
        mechanic = re.sub(r"^lbp\s*[-–—]\s*", "", mechanic, flags=re.I)
        return mechanic.strip() or name
    if family == "dice_promo":
        return name
    return name or "Not specified in MM source"


def gameplay_rank_prizes(task_name: str, detail: str) -> str:
    lower = normalize_name(task_name).lower()
    if not any(has_alias(lower, feature) for feature in GAMEPLAY_RANK_PRIZE_FEATURES):
        return ""
    ranks = rank_prize_lines(detail)
    if ranks:
        return "\n".join(ranks)
    labeled = labeled_values(
        detail,
        ("prize", "prizes", "reward", "rewards", "rank prizes", "collector"),
    )
    if labeled:
        return "\n".join(dict.fromkeys(labeled))
    return ""


def snl_cycle_prize_lines(detail: str) -> list[str]:
    lines_out: list[str] = []
    for raw in (detail or "").splitlines():
        match = re.search(r"cycle prizes\s*[—–-]\s*(.+)$", raw, re.I)
        if match:
            chunk = match.group(1)
            for segment in (part.strip() for part in chunk.split("·") if part.strip()):
                cycle = re.match(r"^\((\d+)\)\s*(.+)$", segment)
                if cycle:
                    prize = _strip_internal_inline(cycle.group(2).strip().rstrip("."))
                    lines_out.append(f"({cycle.group(1)}) {prize}")
                elif re.match(r"^\(\d+\)", segment):
                    lines_out.append(_strip_internal_inline(segment.rstrip(".")))
            if not lines_out:
                for part in chunk.split("·"):
                    cleaned = _strip_internal_inline(part.strip().rstrip("."))
                    if cleaned:
                        lines_out.append(cleaned)
    return lines_out


def promotion_prize(task_name: str, family: str, detail: str) -> str:
    """Single prize line for non-offer promos."""
    rank_block = gameplay_rank_prizes(task_name, detail)
    if rank_block:
        return rank_block
    if "snl" in normalize_name(task_name).lower():
        cycles = snl_cycle_prize_lines(detail)
        if cycles:
            return "\n".join(cycles)
    if family == "golden_spin":
        parts = [part.strip() for part in task_name.split("|")]
        return sanitize_prize_text(parts[1] if len(parts) > 1 else "Coins")
    labeled = labeled_values(detail, ("prize", "prizes", "reward", "rewards", "contents"))
    if labeled:
        return sanitize_prize_text("; ".join(dict.fromkeys(labeled)))
    lower = task_name.lower()
    if "piggy" in lower and " for " in lower:
        return sanitize_prize_text(task_name.split(" for ", 1)[1])
    norm = normalize_name(task_name)
    if "win master" in norm.lower():
        match = re.search(r"win master\s+(?:for\s+)?(.+)$", norm, re.I)
        if match:
            return sanitize_prize_text(match.group(1))
    feature_prefixes = (
        "win master",
        "ace heist",
        "pyp",
        "pick your path",
        "shiny show",
        "lbp",
        "lotto",
        "battlesheep",
        "spinner clash",
        "custom pod",
        "mes",
        "rlap",
    )
    if any(norm.lower().startswith(prefix) for prefix in feature_prefixes) and " - " in norm:
        return sanitize_prize_text(norm.split(" - ", 1)[1])
    if re.search(
        r"\b(?:card|pack|wheel|hammer|dice|stamp|multiball|pab|pick|sb|coins|gems)\b|%",
        norm,
        re.I,
    ):
        return sanitize_prize_text(name_payload(task_name, family))
    return "Not specified in MM source"


def promotion_prizes(task_name: str, family: str, detail: str) -> str:
    if is_offer_family(family):
        return offer_prizes(task_name, family, detail)
    return promotion_prize(task_name, family, detail)


def is_mes_board_task(task_name: str) -> bool:
    name = normalize_name(task_name).lower()
    if "win master" in name and not re.search(r"\bm\.?e\.?s\b", name) and not name.startswith("mes"):
        return False
    return bool(
        re.search(r"\bm\.?e\.?s\b", name)
        or name.startswith("mes ")
        or name.startswith("mes-")
        or name.startswith("mes —")
    )


def mes_subtitle_from_mm(detail: str) -> str | None:
    """Return Sub title line only when MM Description states it explicitly."""
    for raw in (detail or "").splitlines():
        line = raw.strip()
        if re.match(r"^sub\s*title\s*[-:]", line, re.I):
            text = re.sub(r"^sub\s*title\s*[-:]\s*", "", line, flags=re.I).strip()
            if text:
                return f"Sub title - {text}"
            return None
    return None


def mes_subtitle_missing(task_name: str, detail: str) -> bool:
    """MES Ops needs art when MM did not supply an explicit Sub title line."""
    if not is_mes_board_task(task_name):
        return False
    return mes_subtitle_from_mm(detail) is None


def mes_detail_body(detail: str) -> str:
    lines: list[str] = []
    for raw in (detail or "").splitlines():
        line = raw.strip()
        if not line or re.match(r"^sub\s*title", line, re.I):
            continue
        # Production duration belongs only in Start/End columns. Keep reward
        # durations such as "dice booster 6 hours" because those do not start
        # the line and are part of the exact prize.
        if re.fullmatch(
            r"(?:for\s+)?\d+(?:\.\d+)?\s*(?:hours?|hrs?|days?)\s*"
            r"(?:m\.?e\.?s\.?|mes)?(?:\s+challenge)?",
            line,
            re.I,
        ):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


MES_MILESTONE_RE = re.compile(
    r"^(?:(?P<ordinal>\d+)(?:st|nd|rd|th)?\s+milestone|"
    r"milestone\s+(?P<number>\d+))\s*:?\s*(?P<remainder>.*)$",
    re.I,
)
MES_PRIZE_RE = re.compile(r"^(?:grand\s+)?prize\s*[-:]\s*(.+)$", re.I)


def mes_semantic_lines(detail: str) -> list[str]:
    """Format MES source as context plus mission/prize pairs per milestone."""
    body = mes_detail_body(detail)
    context: list[str] = []
    milestones: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        milestone = MES_MILESTONE_RE.match(line)
        if milestone:
            number = milestone.group("ordinal") or milestone.group("number")
            current = {"number": number, "missions": [], "prizes": []}
            milestones.append(current)
            remainder = milestone.group("remainder").strip()
            if remainder:
                current["missions"].append(remainder)
            continue
        if re.fullmatch(r"\d+\s+milestones?", line, re.I) or re.match(
            r"^milestones?,\s*missions?\s+and\s+prizes?\s*:?\s*$",
            line,
            re.I,
        ):
            continue
        prize = MES_PRIZE_RE.match(line)
        if prize:
            if current is not None:
                current["prizes"].append(prize.group(1).strip())
            else:
                context.append(f"Prize: {prize.group(1).strip()}")
            continue
        if current is not None:
            current["missions"].append(line)
        else:
            context.append(line)

    if not milestones:
        return context

    out: list[str] = []
    for line in context:
        if re.match(r"^(?:mission|prize)\s*:", line, re.I):
            out.append(line)
        else:
            out.append(f"Mission: {line}")
    for milestone in milestones:
        if out:
            out.append("")
        out.append(f"Milestone {milestone['number']}:")
        missions = milestone["missions"]
        prizes = milestone["prizes"]
        if missions:
            out.append(f"Mission: {missions[0]}")
            out.extend(missions[1:])
        if prizes:
            out.append(f"Prize: {prizes[0]}")
            out.extend(prizes[1:])
    return out


def compose_mes_description(task_name: str, detail: str, segment: str) -> str:
    subtitle = mes_subtitle_from_mm(detail)
    semantic = mes_semantic_lines(detail)
    lines = [
        f"Segment: {segment}",
        "banner - open M.E.S",
    ]
    if subtitle:
        lines.extend(["", subtitle])
    if semantic:
        lines.extend(["", *semantic])
    else:
        prize = promotion_prize(task_name, "mes", detail)
        lines.extend(["", f"Prize: {prize}"])
    return finalize_ops_description("\n".join(lines).strip())


def compose_description(
    *,
    task_name: str,
    product: str = "",
    detail: str = "",
    pricing: str | None = None,
    reference: str | None = None,
    reuse: bool | None = None,
    template_source: dict[str, str] | None = None,
    missing: Iterable[str] = (),
    config_status: str | None = None,
    creative_label: str | None = None,
    night_plan: bool = False,
) -> str:
    """Compose Ops Description field order and labels for Monetization handoff."""
    _ = (reference, reuse, template_source, missing, config_status, creative_label, night_plan)
    family = promo_family(task_name, product, detail)
    segment = segment_value(task_name, detail, family)

    if family == "rlap":
        offers = rlap_eligible_offers(detail)
        rewards = rlap_reward_lines(detail)
        lines = [f"Segment: {segment}"]
        if offers != "Not specified in MM source":
            lines.append(f"Trigger: Eligible offers: {offers}")
        if "\n" in rewards:
            lines.append("Prize:")
            lines.extend(rewards.splitlines())
        else:
            lines.append(f"Prize: {rewards}")
        return finalize_ops_description("\n".join(lines).strip())

    if family == "ace_heist":
        return compose_ace_heist_description(task_name, detail, segment)

    if is_machine_launch_task(task_name, product):
        return compose_machine_launch_description(task_name, detail, segment)

    if has_alias(normalize_name(task_name).lower(), "spinner clash"):
        return compose_spinner_clash_description(task_name, detail, segment)

    if family in {"happy_hour", "gatcha_promo"}:
        return compose_mechanism_promo_description(task_name, detail, segment)

    if family == "stickers_sources":
        return compose_stickers_sources_description(task_name, detail, segment)

    if family == "extreme_stamp":
        return compose_extreme_stamp_description(task_name, detail, segment)

    if family == "sales_store":
        return compose_sales_store_description(task_name, detail)

    if family == "ads_personal_offer":
        return finalize_ops_description(
            "\n".join(
                [
                    f"Segment: {segment}",
                    f"Prizes: {promotion_prizes(task_name, family, detail)}",
                ]
            ).strip()
        )

    if family == "x2_ggs":
        body = append_ui_reminder(
            f"Segment: {segment}",
            task_name=task_name,
            product=product,
            detail=detail,
        )
        return finalize_ops_description(body)

    if family in VARIANT_FAMILIES:
        variant_body = "\n".join(
            [
                f"Segment: {segment}",
                f"Variant: {variant_value(task_name, family, detail)}",
            ]
        ).strip()
        if family == "mgap":
            variant_body = append_ui_reminder(
                variant_body,
                task_name=task_name,
                product=product,
                detail=detail,
            )
        return finalize_ops_description(variant_body)

    if family == "rolling_offer":
        denoms = rolling_denom_lines(detail)
        lines = [
            f"Segment: {segment}",
            f"Pricing: {price_label(pricing) or 'Not specified in MM source'}",
            "Denoms:",
        ]
        if denoms:
            lines.extend(denoms)
        else:
            lines.append("Not specified in MM source")
        return with_main_offer_reset(lines, family, task_name)

    if is_offer_family(family):
        lines = [f"Segment: {segment}"]
        lines.append(f"Prizes: {promotion_prizes(task_name, family, detail)}")
        lines.append(f"Pricing: {price_label(pricing) or 'Not specified in MM source'}")
        return with_main_offer_reset(lines, family, task_name)

    if is_mes_board_task(task_name):
        return compose_mes_description(task_name, detail, segment)

    trigger = trigger_value(task_name, family, detail)
    prize = promotion_prize(task_name, family, detail)
    lines = [f"Segment: {segment}"]
    if trigger != "Not specified in MM source":
        lines.append(f"Trigger: {trigger}")
    if "\n" in prize:
        lines.append("Prize:")
        lines.extend(prize.splitlines())
    else:
        lines.append(f"Prize: {prize}")
    return finalize_ops_description("\n".join(lines).strip())


TIME_LIMITED_START_SLOTS_UTC = ("14:00:00", "16:00:00", "17:00:00", "21:00:00")

TITLE_UTC_PREFIX_RE = re.compile(
    r"^(?P<hour>\d{1,2}):(?P<minute>\d{2})\s*UTC\s*-\s*",
    re.I,
)

ISO_DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\s*(?:\|\s*|-\s*)")


def ops_task_short_name(name: str) -> str:
    """Ops subitem title label — no calendar date, no leading UTC clock prefix."""
    base = normalize_name(name)
    base = ISO_DATE_PREFIX_RE.sub("", base)
    base = TITLE_UTC_PREFIX_RE.sub("", base)
    return base.strip()

MAIN_OFFER_FAMILIES = frozenset(
    {
        "rolling_offer",
        "daily_deal",
        "ryd",
        "buy_all",
        "decoy_offer",
        "prize_mania",
        "mgap",
        "equal_offer",
        "limited_po",
    }
)


def task_name_has_explicit_utc_prefix(name: str) -> bool:
    return bool(TITLE_UTC_PREFIX_RE.match(normalize_name(name)))


def parse_title_utc_start(name: str) -> str | None:
    match = TITLE_UTC_PREFIX_RE.match(normalize_name(name))
    if not match:
        return None
    return f"{int(match.group('hour')):02d}:{match.group('minute')}:00"


def parse_detail_utc_start(text: str) -> tuple[str | None, str | None]:
    """Return (start_time, end_time) when MM description states explicit UTC clocks."""
    blob = text or ""
    range_match = re.search(
        r"\b(?P<h1>\d{1,2}):(?P<m1>\d{2})\s*UTC\s*(?:-|–|—|to)\s*"
        r"(?P<h2>\d{1,2}):(?P<m2>\d{2})\s*UTC\b",
        blob,
        re.I,
    )
    if range_match:
        start = f"{int(range_match.group('h1')):02d}:{range_match.group('m1')}:00"
        end = f"{int(range_match.group('h2')):02d}:{range_match.group('m2')}:00"
        return start, end
    for pattern in (
        r"(?:starts?|start)\s+(?:at\s+)?(?P<h>\d{1,2}):(?P<m>\d{2})\s*UTC",
        r"(?:from\s+)(?P<h>\d{1,2}):(?P<m>\d{2})\s*UTC",
        r"\bat\s+(?P<h>\d{1,2}):(?P<m>\d{2})\s*UTC\b",
    ):
        match = re.search(pattern, blob, re.I)
        if match:
            return f"{int(match.group('h')):02d}:{match.group('m')}:00", None
    return None, None


def parse_duration_hours(text: str) -> float | None:
    blob = text or ""
    patterns = (
        r"\bfor\s+(?P<n>\d+(?:\.\d+)?)\s*hours?\b",
        r"\b(?P<n>\d+(?:\.\d+)?)\s*hours?\s+(?:time[- ]limited|window|duration)\b",
        r"\b(?P<n>\d+(?:\.\d+)?)\s*hours?\s+in\s+detail\b",
    )
    for pattern in patterns:
        match = re.search(pattern, blob, re.I)
        if match:
            return float(match.group("n"))
    return None


def stable_time_limited_start_utc(parent_day: str, stable_key: str) -> str:
    digest = hashlib.md5(f"{parent_day}:{stable_key}".encode()).hexdigest()
    index = int(digest, 16) % len(TIME_LIMITED_START_SLOTS_UTC)
    return TIME_LIMITED_START_SLOTS_UTC[index]


def _add_hours(day: str, clock: str, hours: float) -> tuple[str, str]:
    start = datetime.fromisoformat(f"{day}T{clock}")
    end = start + timedelta(hours=hours)
    return end.date().isoformat(), end.time().isoformat(timespec="seconds")


def is_time_limited_promo(name: str, product: str, detail: str) -> bool:
    text = f"{normalize_name(name)}\n{detail or ''}".lower()
    family = promo_family(name, product, detail)
    if family in {"happy_hour", "gatcha_promo"}:
        return True
    if re.search(r"\btime[- ]limited\b", text):
        return True
    if re.search(r"\btimed wheel\b", text):
        return True
    if re.search(r"\bhappy hour\b", text):
        return True
    if parse_duration_hours(text) is not None and family not in MAIN_OFFER_FAMILIES:
        return True
    return False


def resolve_ops_production_window(
    *,
    parent_day: str,
    row_id: str,
    name: str,
    product: str,
    detail: str,
    night_plan: bool,
    standard_end_date: str,
) -> dict[str, Any]:
    """Resolve UTC production window, Monday API clocks, and Ops subitem title."""
    warnings: list[str] = []
    base_name = normalize_name(name)
    short_name = ops_task_short_name(name) or base_name
    timing_blob = f"{name}\n{detail or ''}"

    if night_plan:
        start_date = (date.fromisoformat(parent_day) + timedelta(days=1)).isoformat()
        return {
            "task_name": f"00:00 UTC - {short_name}",
            "start_date": start_date,
            "end_date": start_date,
            "start_time": "00:00:00",
            "end_time": "11:00:00",
            "warnings": warnings,
        }

    title_start = parse_title_utc_start(name)
    if title_start:
        hours = parse_duration_hours(timing_blob)
        if hours is None:
            hours = 1.0
            warnings.append(
                "Task title includes UTC start time but MM source has no duration; default 1h window."
            )
        start_date = parent_day
        end_date, end_time = _add_hours(start_date, title_start, hours)
        return {
            "task_name": f"{title_start[:5]} UTC - {short_name}",
            "start_date": start_date,
            "end_date": end_date,
            "start_time": title_start,
            "end_time": end_time,
            "warnings": warnings,
        }

    detail_start, detail_end = parse_detail_utc_start(detail or "")
    if detail_start:
        start_date = parent_day
        if detail_end:
            end_date = start_date
            end_time = detail_end
            if end_time <= detail_start:
                end_date, end_time = _add_hours(start_date, detail_start, 1.0)
        else:
            hours = parse_duration_hours(timing_blob)
            if hours is None:
                hours = 1.0
                warnings.append(
                    "MM description includes UTC start time but no end/duration; default 1h window."
                )
            end_date, end_time = _add_hours(start_date, detail_start, hours)
        task_name = f"{detail_start[:5]} UTC - {short_name}"
        return {
            "task_name": task_name,
            "start_date": start_date,
            "end_date": end_date,
            "start_time": detail_start,
            "end_time": end_time,
            "warnings": warnings,
        }

    if is_time_limited_promo(name, product, detail):
        start_time = stable_time_limited_start_utc(parent_day, row_id or base_name)
        hours = parse_duration_hours(timing_blob)
        if hours is None:
            hours = 1.0
            warnings.append(
                f"Time-limited promo has no duration in MM source; default 1h window "
                f"({start_time[:5]} UTC)."
            )
        start_date = parent_day
        end_date, end_time = _add_hours(start_date, start_time, hours)
        return {
            "task_name": f"{start_time[:5]} UTC - {short_name}",
            "start_date": start_date,
            "end_date": end_date,
            "start_time": start_time,
            "end_time": end_time,
            "warnings": warnings,
        }

    return {
        "task_name": short_name,
        "start_date": parent_day,
        "end_date": standard_end_date,
        "start_time": "11:00:00",
        "end_time": "11:00:00",
        "warnings": warnings,
    }


def reference_for_json(reference: str | None) -> str | None:
    """Keep the original machine-readable reference string unchanged."""
    return reference or None


def task_context(task: dict[str, Any]) -> dict[str, Any]:
    """Small helper for tests and preview tooling."""
    return {
        "family": promo_family(
            task.get("task_name") or "",
            task.get("product") or "",
            task.get("description") or "",
        ),
        "reference": reference_parts(task.get("recent_ops_reference")),
    }
