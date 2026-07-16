#!/usr/bin/env python3
"""Compact Monday Description text — SKUs + instance notes only (no Platform/Duration boilerplate)."""

from __future__ import annotations

import re

_RE_DURATION_2H = re.compile(
    r"^Duration: 2h time-limited \(post 12:00 UTC\)\.?\s*$", re.I | re.M
)
_RE_NOT_2H_FOOTER = re.compile(
    r"^[^\n]*not a 2h window post 12:00 UTC[^\n]*\n?", re.I | re.M
)
_RE_NOT_2H_FOOTER2 = re.compile(
    r"^[^\n]*not 2h time-limited post 12:00 UTC[^\n]*\n?", re.I | re.M
)


def _line_after(label: str, desc: str) -> str | None:
    for line in (desc or "").splitlines():
        if line.strip().lower().startswith(label.lower()):
            rest = line.split(":", 1)[-1].strip()
            if rest:
                return rest.rstrip(".")
    return None


def _strip_platform_blocks(desc: str) -> str:
    lines = (desc or "").splitlines()
    out: list[str] = []
    skip_until_blank = False
    for line in lines:
        s = line.strip()
        if s.startswith("Platform:"):
            rest = s.split(":", 1)[-1].strip()
            if rest:
                out.append(rest)
            skip_until_blank = True
            continue
        if skip_until_blank:
            if not s:
                skip_until_blank = False
            else:
                out.append(line)
            continue
        out.append(line)
    return "\n".join(out).strip()


def _drop_generic_noise(desc: str) -> str:
    text = desc or ""
    text = _RE_DURATION_2H.sub("", text)
    text = _RE_NOT_2H_FOOTER.sub("", text)
    text = _RE_NOT_2H_FOOTER2.sub("", text)
    drop_prefixes = (
        "Rules: no Gold",
        "Stamps: RDS on reveal",
        "Rotation: regular six",
        "Peak night:",
        "Pairing: exactly one LBP",
    )
    kept: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            kept.append("")
            continue
        if any(s.startswith(p) for p in drop_prefixes):
            continue
        if s.startswith("Pricing:") and "SKU generosity" in s:
            continue
        if s.startswith("Purchase rule: standard DD"):
            continue
        kept.append(line.rstrip())
    text = "\n".join(kept)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def _ads_label(name: str, desc: str) -> str:
    prize = _line_after("Prize (this instance)", desc) or _line_after("Prize", desc)
    if not prize:
        m = re.search(r"ADS PO\s*[-–—]\s*(.+)$", name or "", re.I)
        prize = m.group(1).strip() if m else (name or "").strip()
    ctx = _line_after("Context", desc)
    if ctx:
        ctx = ctx.replace("Short-term ", "").replace("Mid-term ", "")
        return f"Prize: {prize} · {ctx}"
    return f"Prize: {prize}"


def _mgap_compact(name: str, desc: str) -> str:
    nl = (name or "").lower()
    if "bogo" in nl:
        lines = [
            "BOGO — buy-one-get-one multipliers on MGAP tiers.",
            "LiveOps: open BOGO config task.",
        ]
        return "\n".join(lines)
    if "slotobucks guaranteed" in nl or "guaranteed" in nl:
        body = desc or ""
        if "Extreme Lucky Spin" in body or "300%" in body:
            return (
                "Slotobucks Guaranteed (once per player).\n"
                "Extreme Lucky Spin → 300% SlotoBucks\n"
                "Epic Lucky Spin → 150% SlotoBucks"
            )
        return "Slotobucks Guaranteed (once per player) — Extreme 300% · Epic 150% SB."
    if "matched" in nl:
        return "Matched multipliers on MGAP tiers."
    if "wild symbol" in nl:
        return "Wild Symbols themed MGAP window."
    if "bigger multiplier" in nl:
        return "Bigger Multipliers — elevated MGAP tiers (sale day)."
    mech = _line_after("Mechanic (this instance)", desc) or _line_after("Mechanic", desc)
    return mech or (name or "").split("|")[-1].strip()


def _ryd_compact(name: str, desc: str, on_extreme: bool) -> str:
    hook = _line_after("Hook / card prize (this instance)", desc)
    if not hook:
        hook = _line_after("Hook / card prize", desc)
    if not hook and "—" in (name or ""):
        hook = name.split("—", 1)[-1].strip()
    hook = (hook or name or "").rstrip(".")
    lines = [f"Hook: {hook}"]
    if on_extreme or "extreme stamp day" in (desc or "").lower():
        lines.append("Extreme Stamp day: RDS → Extreme (4 RDS → 2 Extreme).")
    return "\n".join(lines)


def _dd_compact(name: str, desc: str, pricing: str | None) -> str:
    central = _line_after("Central reward (this instance)", desc)
    if not central:
        m = re.search(r"Daily Deal\s*[-–—]\s*(.+?)(?:\s*\||$)", name or "", re.I)
        if m:
            central = m.group(1).strip()
        else:
            central = re.sub(r"^DD\s*[-–—]\s*", "", name or "", flags=re.I).strip()
    central = re.sub(r"\s*\|\s*[HML].*Pricing\s*$", "", central, flags=re.I).strip()
    lines = [f"Central reward: {central}."]
    low = (central + name).lower()
    if any(x in low for x in ("wild", "shiny limited")) and "multiple" not in low:
        lines.append("Once-per-player — pair with DD multiple same day.")
    elif "multiple" in low:
        lines.append("Multiple purchases.")
    if pricing and pricing not in (name or ""):
        lines[0] = f"{lines[0][:-1]} ({pricing} pricing)."
    return "\n".join(lines)


def _decoy_compact(desc: str) -> str:
    text = desc or ""
    text = re.sub(r"Platform: Decoy[^\n]*\n?", "", text, flags=re.I)
    text = re.sub(r"\nFull denoms:.*", "", text, flags=re.I | re.S).strip()
    return _drop_generic_noise(_strip_platform_blocks(text))


def _lbp_compact(name: str, desc: str) -> str:
    detail = _line_after("Mechanic (this instance)", desc)
    if not detail:
        detail = (desc or "").strip()
    if not detail:
        return (name or "").split("|")[-1].strip()
    for suffix in (
        " on this calendar day — not a 2h window post 12:00 UTC.",
        " on this calendar day — not 2h time-limited post 12:00 UTC.",
        " — not a 2h window post 12:00 UTC",
        " — not 2h time-limited post 12:00 UTC",
    ):
        detail = detail.replace(suffix, "")
    return detail.strip()


def _lotto_peak_compact(desc: str) -> str:
    window = _line_after("Peak window", desc) or ""
    window = window.split("—")[0].strip() if window else ""
    if window:
        return f"Night Plan Lotto peak · {window}"
    return "Night Plan Lotto peak (pair one LBP row this day)."


def _clan_dash_compact(desc: str) -> str:
    mech = _line_after("Mechanic (this instance)", desc)
    if mech:
        mech = re.sub(r"\s*Schedule:.*", "", mech, flags=re.I).strip()
        return mech
    return _strip_platform_blocks(desc)


def compact_monday_description(
    *,
    name: str,
    product: str,
    pricing: str | None = None,
    description: str | None = None,
    on_extreme: bool = False,
) -> str:
    """Return compact Description for a Monday row."""
    desc = (description or "").strip()
    prod = product or ""
    nl = (name or "").lower()

    if prod == "Day":
        return ""

    if prod == "ADS" or nl.startswith("ads po"):
        return _ads_label(name, desc)

    if prod == "MGAP" or "mgap" in nl:
        return _mgap_compact(name, desc)

    if prod == "RYD" or nl.startswith("ryd"):
        return _ryd_compact(name, desc, on_extreme)

    if prod == "Daily deal" or "daily deal" in nl or nl.startswith("dd "):
        if not desc and not name:
            return ""
        if desc and not desc.lower().startswith("platform:") and "central reward" in desc.lower():
            return _drop_generic_noise(desc)
        return _dd_compact(name, desc, pricing)

    if "decoy" in nl or "bonanza" in nl:
        if desc:
            return _decoy_compact(desc)
        return ""

    if prod == "Buy all" or "buy all" in nl:
        if "mystery buy all" in nl and desc:
            return _drop_generic_noise(_strip_platform_blocks(desc))
        if desc and ("denom" in desc.lower() or "coins denom" in desc.lower()):
            return _drop_generic_noise(_strip_platform_blocks(desc))
        return _strip_platform_blocks(desc)

    if "price cut" in nl:
        return "20% storewide discount."

    if "shiny collection" in nl:
        mech = _line_after("Mechanic", desc)
        return mech or _strip_platform_blocks(desc)

    if prod == "Counter PO" or "counter po" in nl:
        prize = _line_after("Prize line", desc)
        return prize or (name or "").split("|")[-1].strip()

    if prod == "Rolling offer" or "rolling offer" in nl:
        if desc:
            return _drop_generic_noise(_strip_platform_blocks(desc))
        return ""

    if prod == "Prize Mania" or "prize mania" in nl:
        pack = _line_after("Bundle focus (this instance)", desc)
        if not pack and "—" in (name or ""):
            pack = name.split("—", 1)[-1].strip()
        return f"Bundle: {pack}" if pack else _drop_generic_noise(_strip_platform_blocks(desc))

    if prod == "Clan-Dash":
        return _clan_dash_compact(desc) if desc else ""

    if re.search(r"lotto\s*[—-]\s*peak", nl):
        return _lotto_peak_compact(desc) if desc else ""

    if nl.startswith("lbp") or "| lbp" in nl:
        return _lbp_compact(name, desc)

    if "piggy" in nl:
        prize = _line_after("Prize on break", desc)
        return f"Prize on break: {prize}" if prize else _strip_platform_blocks(desc)

    if "golden spin" in nl:
        return "Golden Spin — timed gem feature."

    if "dice deluxe" in nl:
        return "Dice Deluxe — weekly dice offer."

    if "shiny show" in nl:
        var = _line_after("Variant / prizes (this day)", desc)
        if not var and "—" in (name or ""):
            var = name.split("—", 1)[-1].strip()
        return f"Variant: {var}" if var else desc

    if re.search(r"\bx2\s*extreme\s*stamp", nl, re.I):
        return "Doubles Extreme Stamps in offers today (RDS → Extreme)."

    if "x2 ggs" in nl:
        return "Doubles GGS earned in offers (3h post 11:00 UTC)."

    if "gemback" in nl:
        pct = "500%" if "500" in nl else "300%"
        return f"Boosted Gemback {pct} — exclude DD."

    if "gems sale" in nl or "gem sale" in nl:
        return "Gems Sale — 30% store / 20% offers."

    if "coin sale" in nl:
        themed = "Back to School" if "back to school" in nl else ""
        return f"Coin Sale{(' · ' + themed) if themed else ''}."

    if "status boost" in nl:
        return "Top store denom visibility (Status Boost)."

    if re.search(r"spinner\s*clash", nl):
        return _drop_generic_noise(_strip_platform_blocks(desc))

    if re.search(r"spin zone", nl):
        prize = _line_after("Prize (this instance)", desc)
        ctx = _line_after("Short-term context", desc)
        parts: list[str] = []
        if prize:
            parts.append(f"Prize: {prize}")
        if ctx:
            parts.append(f"Short-term: {ctx}")
        if parts:
            return "\n".join(parts)
        return _drop_generic_noise(_strip_platform_blocks(desc))

    if prod == "Core" and desc:
        if "Gameplay Core" in desc:
            lines = [ln for ln in desc.splitlines() if ln.strip() and not ln.strip().startswith("Gameplay Core")]
            return "\n".join(lines).strip() or desc.splitlines()[-1].strip()
        return desc

    if desc:
        cleaned = _drop_generic_noise(_strip_platform_blocks(desc))
        cleaned = re.sub(r"^Mechanic \(this instance\):\s*", "", cleaned, flags=re.I | re.M)
        cleaned = re.sub(r"^Mechanic:\s*", "", cleaned, flags=re.I | re.M)
        return cleaned.strip()

    return ""
