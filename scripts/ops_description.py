#!/usr/bin/env python3
"""Promo-aware, natural-language description composer for Ops tasks."""

from __future__ import annotations

import re
from typing import Any, Iterable

OPS_BOARD_ID = "2109172490"


def normalize_name(value: str) -> str:
    value = re.sub(r"^\d{4}-\d{2}-\d{2}\s*\|\s*", "", value or "").strip()
    return re.sub(r"\s+", " ", value.replace("—", "-").replace("–", "-"))


def has_alias(text: str, alias: str) -> bool:
    escaped = re.escape(alias.strip()).replace(r"\ ", r"\s+")
    return bool(re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text))


def promo_family(name: str, product: str = "", detail: str = "") -> str:
    text = f" {normalize_name(name)} {product} {detail[:300]} ".lower()
    rules: list[tuple[str, tuple[str, ...]]] = [
        ("rlap", ("rlap", "stash booster")),
        ("stickers_sources", ("sticker sources", "stickers sources")),
        ("ads_personal_offer", ("ads po", "po ads", "ads personal offer")),
        ("daily_deal", ("daily deal", "daily_deal")),
        ("rolling_offer", ("rolling offer", "buy more for less", "buy x get y", "bmfl", "bxgy")),
        ("ryd", (" ryd ", "reveal your deal")),
        ("buy_all", ("buy all",)),
        ("decoy_offer", ("decoy", "bonanza")),
        ("equal_offer", ("equal offer", "equal triple")),
        ("limited_po", ("limited po", "limited personal offer")),
        ("mgap", ("mgap", "make good any purchase")),
        ("clan_dash", ("clan dash", "clan-dash", "dash pass")),
        ("shiny_show", ("shiny show",)),
        ("lbp_lotto", (" lbp ", "lotto bonus premium", "lotto peak", "lotto - peak")),
        ("mes", ("m.e.s", " mes ", "mission event system", "win master")),
        (
            "gameplay",
            (
                "spin zone",
                "pick your path",
                "custom pod",
                "battlesheep",
                "spinner clash",
                "ace heist",
                "piggy",
                "prize mania",
                " core ",
            ),
        ),
        ("season_blast", ("blast", "mid term", "short term", "album handover")),
        (
            "sales_store",
            ("coin sale", "gems sale", "gem sale", "coupon", "store denom", "biggest store"),
        ),
    ]
    for family_name, aliases in rules:
        if any(has_alias(text, alias) for alias in aliases):
            return family_name
    return "other"


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
        lines.append(line)
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
    "sales_store",
}


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
        "daily_deal": r"^daily deal\s*[-|:]?\s*",
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
    return result or name_payload(task_name, family)


def labeled_values(detail: str, labels: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    pattern = "|".join(re.escape(label) for label in labels)
    for line in (detail or "").splitlines():
        match = re.match(rf"^\s*(?:{pattern})\s*\d*\s*[:\-]\s*(.+)$", line, re.I)
        if match and match.group(1).strip():
            values.append(match.group(1).strip().rstrip("."))
    return values


def trigger_value(task_name: str, family: str, detail: str) -> str:
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


def promotion_prizes(task_name: str, family: str, detail: str) -> str:
    if family in OFFER_FAMILIES or family == "rolling_offer":
        return offer_prizes(task_name, family, detail)
    if family == "ads_personal_offer":
        return name_payload(task_name, family)
    if family == "mgap":
        if "bogo" in task_name.lower():
            return "Matching BOGO reward according to config"
        if "bigger" in task_name.lower():
            return "Bigger multipliers according to config"
    labeled = labeled_values(detail, ("prize", "prizes", "reward", "rewards", "contents"))
    if labeled:
        return "; ".join(dict.fromkeys(labeled))
    lower = task_name.lower()
    if "piggy" in lower and " for " in lower:
        return task_name.split(" for ", 1)[1]
    feature_prefixes = (
        "win master",
        "ace heist",
        "shiny show",
        "lbp",
        "lotto",
        "mgap",
        "prize mania",
        "battlesheep",
    )
    if lower.startswith(feature_prefixes) and " - " in task_name:
        return task_name.split(" - ", 1)[1]
    if re.search(
        r"\b(?:card|pack|wheel|hammer|dice|stamp|multiball|pab|pick|sb|coins|gems)\b|%",
        task_name,
        re.I,
    ):
        return normalize_name(task_name)
    return "Not specified in MM source"


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
    """Compose the minimum execution fields requested by Monetization."""
    family = promo_family(task_name, product, detail)
    segment = segment_value(task_name, detail, family)
    lines = [
        f"Prizes: {promotion_prizes(task_name, family, detail)}",
        f"Segment: {segment}",
    ]
    if family in OFFER_FAMILIES or family == "rolling_offer":
        lines.append(f"Pricing: {price_label(pricing) or 'Not specified in MM source'}")
    trigger = trigger_value(task_name, family, detail)
    if trigger != "Not specified in MM source":
        lines.append(f"Trigger: {trigger}")
    return "\n".join(lines).strip()


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
