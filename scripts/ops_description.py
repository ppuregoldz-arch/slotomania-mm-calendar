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
    """Compose a concise Ops handoff without inventing execution details."""

    family = promo_family(task_name, product, detail)
    lines = [opening_line(family, task_name, pricing)]
    if family == "ads_personal_offer":
        lines.append("Eligible players watch an ad and receive the configured prize.")
    elif family == "ryd":
        lines.append("The player reveals the largest personalized offer and can purchase it.")
    elif family == "mes" and "win master" in task_name.lower():
        lines.append("Players complete the configured win requirement and receive the listed rewards.")
        lines.append("Use the complete Win Master M.E.S task and asset/config set.")
    elif family == "season_blast" and "cozy" in task_name.lower():
        lines.append("Use the Cozy theme and Wild Ordinary reward in one Blast season task.")
    cleaned_detail = clean_detail(detail)
    if cleaned_detail:
        lines.extend(["", cleaned_detail])

    lines.extend(["", duplicate_line(reference, reuse)])
    delta = change_line(task_name, reference, reuse)
    if delta:
        lines.append(delta)
    fallback = template_line(template_source, reuse)
    if fallback:
        lines.append(fallback)

    dependencies = dependency_lines(missing, config_status, creative_label)
    if dependencies:
        lines.extend(["", "Needed before scheduling:"])
        lines.extend(f"- {sentence(entry)}" for entry in dependencies)

    if night_plan:
        lines.extend(["", "Run this as the approved Night Plan action."])

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
