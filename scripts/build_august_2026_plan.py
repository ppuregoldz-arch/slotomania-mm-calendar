#!/usr/bin/env python3
"""Build August 2026 MM calendar draft from monthly_guidelines/2026-08.md + repo rules."""
from __future__ import annotations

import copy
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

# Import the shared scorer for lift-aware placement
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
try:
    import scorer as _scorer
    _HAS_SCORER = True
except ImportError:
    _HAS_SCORER = False

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from mm_calendar.purchase_drivers import ensure_month_open_biggest_denom  # noqa: E402

OUT_JSON = ROOT / "mm_calendar" / "data" / "august_2026_plan.json"
OUT_MD = ROOT / "mm_calendar" / "examples" / "2026-08_calendar.md"

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Short Term 5-day blocks from Aug 1
def short_term(d: int) -> str:
    blocks = [(1, 5, "Blast"), (6, 10, "Battlesheep"), (11, 15, "SNL"), (16, 20, "Blast"), (21, 25, "Battlesheep"), (26, 31, "SNL")]
    for a, b, name in blocks:
        if a <= d <= b:
            return name
    return "SNL"


def pyp_seasonal_mission(d: int) -> str:
    st = short_term(d).lower()
    if "blast" in st:
        return "Use PAB"
    if "battlesheep" in st:
        return "Use 2 Airstrikes"
    if "snl" in st:
        return "Use 4 Dice Rolls"
    return "Use Superboom"


def pyp_missions_description(d: int) -> str:
    """Monday Description — mission list only (3 fixed + 1 seasonal). Prize is in the row title."""
    seasonal = pyp_seasonal_mission(d)
    return (
        "Missions:\n"
        "· Reach act 18 — Shiny Show\n"
        "· Spin 100 times — Gem Machine\n"
        "· Open 5 pods\n"
        f"· {seasonal}"
    )


def ace_heist_missions_description(d: int) -> str:
    """Monday Description — fixed Ace Heist mission trio. Prize is in the row title."""
    return (
        "Missions:\n"
        "· Spin 30 times — any game\n"
        "· Reach final act — Shiny Show\n"
        "· Open 8 pods"
    )


def time_limited_prize_nivi_label(d: int) -> str:
    """Prize for Time Limited Prize (Clan-Dash) from Nivi Dash milestone table."""
    mondays = [x for x in range(1, 32) if dow(x) == "Mon"]
    rotation = (
        "4★ Regular Card (Dash premium · milestone 4)",
        "Shiny Card (Dash premium · milestone 9)",
        "3★ Gold Card (Dash premium · milestone 11)",
        "5★ Regular Card (Dash premium · milestone 14)",
        "5★ Gold Card (Dash premium · milestone 17)",
    )
    if d in mondays:
        return rotation[mondays.index(d) % len(rotation)]
    ph = collector_album_phase(d)
    by_phase = {
        1: "4★ Regular Card (Dash premium · milestone 4)",
        2: "Shiny Card (Dash premium · milestone 9)",
        3: "Wild Any (Dash premium · milestone 20)",
    }
    return by_phase.get(ph, rotation[0])


def time_limited_prize_row_name(d: int) -> str:
    """Monday board title — prize must be visible in the row name (not Description only)."""
    label = time_limited_prize_nivi_label(d)
    short = re.sub(r"\s*\(Dash premium[^)]*\)", "", label, flags=re.I).strip()
    return f"Time Limited Prize — {short}"


def time_limited_prize_is_shiny_card(d: int) -> bool:
    return dow(d) == "Mon" and "shiny card" in time_limited_prize_nivi_label(d).lower()


# Monday Dash TLP uses Shiny Card — DD must not duplicate the same card same day.
TLP_SHINY_DD_FALLBACK_KEYS: tuple[str, ...] = ("ace_sb", "reg_hw", "sb8_h", "gold_as")


# Mid-term Aug 2026: Figz 4d → Quest 5d → Globez 6d → Quest 5d (repeat). Quest always between Figz & Globez.
FIGZ_DAYS = 4
QUEST_DAYS = 5
GLOBEZ_DAYS = 6
MID_TERM_CYCLE_ORDER: tuple[str, ...] = ("Figz", "Quest", "Globez", "Quest")

# July carryover + explicit August season starts (Mega Pods new 3/8 · Quest new 4/8 · Winovate new 5/8).
AUGUST_MID_TERM_BLOCKS: tuple[tuple[int, int, str], ...] = (
    (1, 3, "Quest"),   # July Quest season tail
    (4, 8, "Quest"),   # new Quest season from 4/8
    (9, 14, "Globez"),
    (15, 19, "Quest"),
    (20, 23, "Figz"),
    (24, 28, "Quest"),
    (29, 31, "Globez"),
)
MID_TERM_BLOCKS: tuple[tuple[int, int, str], ...] = AUGUST_MID_TERM_BLOCKS
# Monday / plan ★ — new rotating mid-term block (not 1/8 Quest carryover).
ROTATING_MID_TERM_FIRST_DAYS = frozenset({4, 9, 15, 20, 24, 29})

MEGA_PODS_CYCLE_DAYS = 7  # Mon→Mon
MEGA_PODS_FIRST_NEW_DAY = 3  # July Mega Pods ends 2/8; new season from 3/8
WINOVATE_CYCLE_DAYS = 8
WINOVATE_FIRST_NEW_DAY = 5  # July Winovate ends 4/8; new season from 5/8


def mega_pods_season_is_first(d: int) -> bool:
    if d < MEGA_PODS_FIRST_NEW_DAY:
        return False
    return (d - MEGA_PODS_FIRST_NEW_DAY) % MEGA_PODS_CYCLE_DAYS == 0


def winovate_season_is_first(d: int) -> bool:
    if d < WINOVATE_FIRST_NEW_DAY:
        return False
    return (d - WINOVATE_FIRST_NEW_DAY) % WINOVATE_CYCLE_DAYS == 0


def mega_pods_season_bounds(d: int) -> tuple[int, int]:
    if d < MEGA_PODS_FIRST_NEW_DAY:
        return (1, MEGA_PODS_FIRST_NEW_DAY - 1)
    start = MEGA_PODS_FIRST_NEW_DAY
    while start + MEGA_PODS_CYCLE_DAYS <= d:
        start += MEGA_PODS_CYCLE_DAYS
    return start, min(start + MEGA_PODS_CYCLE_DAYS - 1, 31)


def winovate_season_bounds(d: int) -> tuple[int, int]:
    if d < WINOVATE_FIRST_NEW_DAY:
        return (1, WINOVATE_FIRST_NEW_DAY - 1)
    start = WINOVATE_FIRST_NEW_DAY
    while start + WINOVATE_CYCLE_DAYS <= d:
        start += WINOVATE_CYCLE_DAYS
    return start, min(start + WINOVATE_CYCLE_DAYS - 1, 31)


def mid_term_blocks_markdown() -> str:
    return " · ".join(f"{name} {a}–{b}" for a, b, name in MID_TERM_BLOCKS)


def validate_mid_term_quest_buffer() -> list[str]:
    """Quest must sit between every Figz ↔ Globez transition."""
    bad: list[str] = []
    for d in range(2, 32):
        prev, cur = mid_term(d - 1), mid_term(d)
        if {prev, cur} == {"Figz", "Globez"}:
            bad.append(f"{d - 1}/{d}")
    return bad


def mid_term(d: int) -> str:
    for a, b, name in MID_TERM_BLOCKS:
        if a <= d <= b:
            return name
    return "Quest"


def collector_album_phase(d: int) -> int:
    """Shiny Series 1–3 inside Aug 2026 plan (promo boundaries 4/8 and 25/8)."""
    if d <= 3:
        return 1
    if d <= 24:
        return 2
    return 3


def album_phase(d: int) -> str:
    labels = {
        1: "Phase 1 (Shiny MS1)",
        2: "Phase 2 (Shiny MS2)",
        3: "Phase 3 (Shiny MS3)",
    }
    return labels[collector_album_phase(d)]


SHORT_TERM_CYCLE_PRIZES: dict[int, tuple[str, str, str]] = {
    1: ("Wild Ordinary", "5★ Regular Pack", "4★ Regular Pack"),
    2: ("Wild Gold", "5★ Regular Pack", "4★ Regular Pack"),
    3: ("Wild Any", "5★ Regular Pack", "4★ Regular Pack"),
}

SPINNER_CLASH_RANK_PRIZES: dict[int, tuple[str, str, str]] = {
    1: ("4★ Ace Card", "3★ Ace Card", "3★ Regular Card"),
    2: ("5★ Ace Pack", "4★ Ace Pack", "3★ Ace Card"),
    3: ("Wild Ace", "5★ Ace Pack", "3★ Ace Pack"),
}


def short_term_album_cycle_description(d: int) -> str:
    ph = collector_album_phase(d)
    c1, c2, c3 = SHORT_TERM_CYCLE_PRIZES[ph]
    return (
        f"Short-term board (~5d): cycle prizes — (1) {c1} · (2) {c2} · (3) {c3}. "
        f"Collector's Album phase {ph} (Shiny Series {ph}). "
        "Full tables: mm_calendar/nivi_collector_album_prizes.md"
    )


def album_season_description(d: int) -> str:
    ph = collector_album_phase(d)
    return (
        f"Shiny Series {ph} · album 14/07–22/09. "
        f"Window: phase {ph} per Nivi promo boundaries (see nivi_collector_album_prizes.md)."
    )


def spinner_clash_description(d: int) -> str:
    ph = collector_album_phase(d)
    first, second, third = SPINNER_CLASH_RANK_PRIZES[ph]
    return (
        "Platform: Spinner Clash — tournament Core coin sink; house adds % of wins to prize pot.\n"
        f"Collector's Album phase {ph} (Shiny Series {ph}) — rank prizes:\n"
        f"  1st: {first}\n"
        f"  2nd: {second}\n"
        f"  3rd: {third}\n"
        "Configure ranks in LiveOps per nivi_collector_album_prizes.md."
    )


def card_week(d: int) -> int:
    """Cards distribution week (image guideline): 1–9 · 10–16 · 17–23 · 24–31."""
    if d <= 9:
        return 1
    if d <= 16:
        return 2
    if d <= 23:
        return 3
    return 4


# Weekly ceilings — Cards Distribution by week (Aug 2026 image / Nivi)
CARD_BUDGETS: dict[int, dict[str, int]] = {
    1: {
        "Reg_3": 1,
        "Reg_5": 1,
        "Gold_3": 1,
        "Gold_4": 1,
        "Gold_5": 1,
        "Ace_3": 2,
        "Ace_4": 1,
        "Shiny Card": 1,
        "Shiny Limited": 1,
    },
    2: {
        "Reg_4": 2,
        "Reg_5": 2,
        "Gold_3": 2,
        "Gold_4": 1,
        "Gold_5": 1,
        "Ace_3": 1,
        "Ace_4": 1,
        "Ace_5": 1,
        "Shiny Card": 1,
        "Shiny Limited": 1,
    },
    3: {
        "Reg_4": 2,
        "Reg_5": 2,
        "Gold_3": 2,
        "Gold_4": 2,
        "Gold_5": 1,
        "Ace_3": 1,
        "Ace_4": 1,
        "Ace_5": 1,
        "Shiny Card": 1,
        "Shiny Limited": 1,
        "Wild Ord": 1,
    },
    4: {
        "Reg_4": 1,
        "Reg_5": 2,
        "Gold_3": 1,
        "Gold_4": 2,
        "Gold_5": 2,
        "Ace_3": 1,
        "Ace_4": 1,
        "Ace_5": 2,
        "Shiny Card": 1,
        "Shiny Limited": 2,
        "Wild Ord": 1,
        "Wild Gold": 1,
    },
}

# Higher score → reserve for premium purchase slots (Decoy d3, Counter PO, BTS, etc.)
CARD_VALUE_SCORE: dict[str, int] = {
    "Wild Gold": 100,
    "Wild Ord": 95,
    "Shiny Limited": 90,
    "Shiny Card": 85,
    "Ace_5": 82,
    "Gold_5": 80,
    "Reg_5": 72,
    "Ace_4": 68,
    "Gold_4": 66,
    "Reg_4": 58,
    "Ace_3": 52,
    "Gold_3": 50,
    "Reg_3": 42,
}

PREMIUM_PICK_ORDER: tuple[str, ...] = tuple(
    sorted(CARD_VALUE_SCORE.keys(), key=lambda k: -CARD_VALUE_SCORE[k])
)
# Purchase offers — never sell Ace cards (Reg / Gold / Wild / Shiny only).
OFFER_CARD_PICK_ORDER: tuple[str, ...] = tuple(k for k in PREMIUM_PICK_ORDER if not k.startswith("Ace"))
REG_PICK_ORDER = ("Reg_5", "Reg_4", "Reg_3")
ACE_PICK_ORDER = ("Ace_5", "Ace_4", "Ace_3")
GOLD_PICK_ORDER = ("Gold_5", "Gold_4", "Gold_3")
WILD_PICK_ORDER = ("Wild Gold", "Wild Ord")


def card_key_to_label(key: str) -> str:
    if key in ("Shiny Card", "Shiny Limited", "Wild Ord", "Wild Gold"):
        return key
    fam, stars = key.split("_", 1)
    return f"{stars}★ {fam}"


def card_key_to_short_top(key: str) -> str:
    """Decoy / offer top line (e.g. 3★ Ace, Wild Ord)."""
    if key.startswith("Wild"):
        return key
    if key in ("Shiny Card", "Shiny Limited"):
        return key
    return card_key_to_label(key)


def _stars_from_key(key: str, default: int = 4) -> int:
    if key in ("Shiny Card", "Shiny Limited", "Wild Ord", "Wild Gold"):
        return default
    return int(key.split("_", 1)[0])


class CardLedger:
    def __init__(self) -> None:
        self.rem: dict[int, dict[str, int]] = {w: dict(b) for w, b in CARD_BUDGETS.items()}
        self.used: dict[int, dict[str, int]] = {w: {} for w in CARD_BUDGETS}

    def week(self, d: int) -> int:
        return card_week(d)

    def available(self, d: int, key: str) -> bool:
        w = self.week(d)
        return self.rem[w].get(key, 0) > 0

    def take(self, d: int, key: str) -> bool:
        w = self.week(d)
        if self.rem[w].get(key, 0) <= 0:
            return False
        self.rem[w][key] -= 1
        self.used[w][key] = self.used[w].get(key, 0) + 1
        return True

    def pick_first(self, d: int, order: tuple[str, ...]) -> str | None:
        for key in order:
            if self.take(d, key):
                return key
        return None

    def pick_premium(self, d: int, *, allow_wild: bool = True, allow_ace: bool = True) -> str | None:
        order = list(PREMIUM_PICK_ORDER if allow_ace else OFFER_CARD_PICK_ORDER)
        if not allow_wild or wild_reserved_for_future_dd(d):
            order = [k for k in order if not k.startswith("Wild")]
        return self.pick_first(d, tuple(order))

    def pick_reg(self, d: int, *, prefer_high: bool = False) -> str | None:
        order: tuple[str, ...] = REG_PICK_ORDER if prefer_high else tuple(reversed(REG_PICK_ORDER))
        return self.pick_first(d, order)

    def pick_ace(self, d: int, *, prefer_high: bool = True) -> str | None:
        order = ACE_PICK_ORDER if prefer_high else tuple(reversed(ACE_PICK_ORDER))
        return self.pick_first(d, order)

    def pick_gold(self, d: int, *, prefer_high: bool = True) -> str | None:
        order = GOLD_PICK_ORDER if prefer_high else tuple(reversed(GOLD_PICK_ORDER))
        return self.pick_first(d, order)

    def build_dd_lines(self, d: int, key: str, sale: bool) -> list[DDLine]:
        pr = _dd_pricing(sale)
        feat = dd_feature_sku_lines(key, d, sale)
        if feat:
            return feat
        mt = mid_term_booster(d)
        if key == "shiny_ltd":
            if self.take(d, "Shiny Limited"):
                return [
                    ("DD - Shiny Limited - Once", pr, "Once + multiple below"),
                    (DD_REPEATABLE_SB_HAMMERS_NAME, "High", DD_REPEATABLE_SB_HAMMERS_DESC),
                ]
            key = "gold_as"
        if key == "wild_dd":
            wk = self.pick_first(d, WILD_PICK_ORDER)
            if wk:
                return [
                    (
                        dd_on_purchase_line(card_key_to_label(wk), d),
                        pr,
                        "Wild — Nivi weekly bank (prefer DD + Shiny Show, not Show only)",
                    ),
                    (
                        DD_REPEATABLE_SB_HAMMERS_NAME,
                        "High",
                        "Repeatable DD after once-per-player Wild purchase — 100% SB + 8 Hammers.",
                    ),
                ]
            key = "gold_as"
        if key == "shiny_once":
            if self.take(d, "Shiny Card"):
                return [("DD- Shiny Card (multiple)", pr, "Album bank")]
            key = "gold_as"
        if key == "shiny_mt":
            if self.take(d, "Shiny Card"):
                return [(f"DD- Shiny Card + {mt} (multiple)", pr, f"Mid-term: {mt}")]
            key = "gold_as"
        if key == "reg_hw":
            rk = self.pick_reg(d, prefer_high=False)
            if rk:
                return [(f"DD- {card_key_to_label(rk)} card + Hammers Wheel", pr, "")]
            gk = self.pick_gold(d, prefer_high=False)
            if gk:
                return [(dd_on_purchase_line(card_key_to_label(gk), d), pr, "")]
            g = stars_gold(d) or 3
            return [(dd_on_purchase_line(f"{stars_reg(d)}★ Reg", d), pr, "Reg HW bank full — Reg DD (no Hammer Wheel)")]
        if key == "ace_sb":
            rk = self.pick_reg(d, prefer_high=False)
            if rk:
                return [(f"DD- {card_key_to_label(rk)} card + SB Wheel", pr, "No Ace in purchase offers")]
            return [("DD- 100% SB + 8 Hammers", pr, "SB anchor — no Ace card")]
        if key == "gold_as":
            gk = self.pick_gold(d, prefer_high=False)
            if gk:
                return [(dd_on_purchase_line(card_key_to_label(gk), d), pr, "")]
            g = stars_gold(d) or 3
            return [(dd_on_purchase_line(f"{g}★ Gold", d), pr, "Gold bank full — planned stars")]
        if key == "sb8_h":
            return [("DD- 100% SB + 8 Hammers", pr, "")]
        if key == "combo":
            return [("DD- Cards & SB Wheel (Combined)", pr, "")]
        rk = self.pick_reg(d, prefer_high=False)
        if rk:
            return [(f"DD- {card_key_to_label(rk)} card + Hammers Wheel", pr, "")]
        ak = self.pick_reg(d, prefer_high=False)
        if ak:
            return [(f"DD- {card_key_to_label(ak)} card + SB Wheel", pr, "Bank fallback — no Ace in offers")]
        gk = self.pick_gold(d, prefer_high=False)
        if gk:
            return [(dd_on_purchase_line(card_key_to_label(gk), d), pr, "")]
        if key in ("sb8_h",):
            return [("DD- 100% SB + 8 Hammers", pr, "")]
        if key == "combo":
            return [("DD- Cards & SB Wheel (Combined)", pr, "")]
        g = stars_gold(d) or 3
        if d % 2:
            rk = self.pick_reg(d, prefer_high=False)
            if rk:
                return [(f"DD- {card_key_to_label(rk)} card + SB Wheel", pr, "Bank fallback — no Ace in offers")]
        return [(dd_on_purchase_line(f"{g}★ Gold", d), pr, "Bank fallback")]


def stars_reg(d: int) -> int:
    return {1: 3, 2: 4, 3: 4, 4: 5}.get(card_week(d), 4)


def stars_ace(d: int) -> int:
    return {1: 3, 2: 4, 3: 4, 4: 5}.get(card_week(d), 4)


def stars_gold(d: int) -> int:
    return {1: 3, 2: 3, 3: 3, 4: 4}.get(card_week(d), 3)


def rolling_bmfl_name(d: int) -> str:
    """Buy More for Less — fixed 3-cycle MFL shape."""
    _ = d
    return f"Rolling Offer — {ROLLING_BMFL_CYCLES} cycles (Buy More for Less)"


def rolling_bxgy_name(d: int, cycles: int) -> str:
    c = max(1, min(6, int(cycles)))
    if c == 1:
        return "Rolling Offer — 1 cycle (Buy 1 Get 8)"
    return f"Rolling Offer — {c} cycles (Buy X Get Y)"


def is_rolling_bmfl_name(name: str | None) -> bool:
    return bool(re.search(r"buy\s*more\s*for\s*less|more\s*for\s*less", name or "", re.I))


def _rolling_reg_stars_for_cycle(d: int, cycle_index: int, total_cycles: int) -> int:
    w = card_week(d)
    base = {1: (3, 4, 5), 2: (3, 4, 5), 3: (4, 5, 5), 4: (5, 5, 5)}.get(w, (3, 4, 5))
    if total_cycles <= 3:
        return base[min(cycle_index, len(base) - 1)]
    lo, hi = base[0], base[-1]
    if total_cycles == 1:
        return lo
    step = (hi - lo) / max(1, total_cycles - 1)
    return min(5, round(lo + step * cycle_index))


# Buy More for Less — per-cycle prize totals (Itay Aug 2026: leaner than 5/7/9 Hammers + stamp header).
BMFL_HAMMERS_BY_CYCLE = (2, 4, 6)
BMFL_RDS_BY_CYCLE = (3, 3, 3)
BMFL_GGS_BY_CYCLE = (1, 1, 2)

# Per cycle (6 steps) for Buy X Get Y only: RDS ≤4 (1 on first stamp step, 3 on next); GGS ≤2 (1+1).
ROLLING_RDS_PER_CYCLE = (1, 3)
ROLLING_GGS_PER_CYCLE = (1, 1)
ROLLING_RDS_STAMP_STEPS = (2, 5)  # 1-based step indices within the 6-step cycle
ROLLING_GGS_STAMP_STEPS = (3, 6)


def rolling_stamp_allocation_note() -> str:
    r1, r2 = ROLLING_RDS_PER_CYCLE
    g1, g2 = ROLLING_GGS_PER_CYCLE
    rs = ROLLING_RDS_STAMP_STEPS
    gs = ROLLING_GGS_STAMP_STEPS
    return (
        f"RDS max {r1 + r2}/cycle: {r1} on first stamp step, {r2} on next · "
        f"GGS max {g1 + g2}/cycle: {g1} on first stamp step, {g2} on next"
    )


ROLLING_STAMP_COUNT_RE = re.compile(r"(\d+)\s*(RDS|GGS)\b", re.I)
ROLLING_CYCLE_BLOCK_RE = re.compile(r"Cycle\s+(\d+)\s*:(.*?)(?=Cycle\s+\d+\s*:|$)", re.I | re.S)

# Buy X Get Y — free denoms per cycle (1-cycle product = Buy 1 Get 8).
BXGY_FREE_DENOMS_BY_CYCLES: dict[int, int] = {1: 8, 2: 6, 5: 6, 6: 6}


def rolling_stamp_totals_in_text(text: str) -> tuple[int, int]:
    rds = ggs = 0
    for n, kind in ROLLING_STAMP_COUNT_RE.findall(text):
        if kind.upper() == "RDS":
            rds += int(n)
        else:
            ggs += int(n)
    return rds, ggs


def validate_rolling_item_stamps(day: int, name: str, desc: str) -> list[str]:
    """BXGY: per-cycle RDS≤4 (1+3), GGS≤2 (1+1). BMFL: per-cycle totals match BMFL_*_BY_CYCLE on cycle lines."""
    issues: list[str] = []
    desc = desc or ""
    name = name or ""
    max_rds = sum(ROLLING_RDS_PER_CYCLE)
    max_ggs = sum(ROLLING_GGS_PER_CYCLE)
    if is_rolling_bmfl_name(name):
        blocks = list(ROLLING_CYCLE_BLOCK_RE.finditer(desc))
        if len(blocks) < ROLLING_BMFL_CYCLES:
            issues.append(f"{day}:BMFL missing cycle blocks")
        for m in blocks:
            cnum = int(m.group(1))
            body = m.group(2)
            rds, ggs = rolling_stamp_totals_in_text(body)
            idx = cnum - 1
            if idx < 0 or idx >= ROLLING_BMFL_CYCLES:
                continue
            if rds != BMFL_RDS_BY_CYCLE[idx]:
                issues.append(f"{day}:BMFL c{cnum} RDS{rds}!={BMFL_RDS_BY_CYCLE[idx]}")
            if ggs != BMFL_GGS_BY_CYCLE[idx]:
                issues.append(f"{day}:BMFL c{cnum} GGS{ggs}!={BMFL_GGS_BY_CYCLE[idx]}")
            hm = re.search(r"(\d+)\s*Hammers", body, re.I)
            if hm and int(hm.group(1)) != BMFL_HAMMERS_BY_CYCLE[idx]:
                issues.append(f"{day}:BMFL c{cnum} Hammers")
        return issues
    blocks = list(ROLLING_CYCLE_BLOCK_RE.finditer(desc))
    if not blocks:
        rds, ggs = rolling_stamp_totals_in_text(desc)
        if rds > max_rds:
            issues.append(f"{day}:RDS{rds}>{max_rds}")
        if ggs > max_ggs:
            issues.append(f"{day}:GGS{ggs}>{max_ggs}")
        return issues
    for m in blocks:
        cnum = m.group(1)
        body = m.group(2)
        rds, ggs = rolling_stamp_totals_in_text(body)
        if rds > max_rds:
            issues.append(f"{day}:c{cnum} RDS{rds}")
        if ggs > max_ggs:
            issues.append(f"{day}:c{cnum} GGS{ggs}")
        rds_parts = sorted(
            int(x) for x, k in ROLLING_STAMP_COUNT_RE.findall(body) if k.upper() == "RDS"
        )
        ggs_parts = sorted(
            int(x) for x, k in ROLLING_STAMP_COUNT_RE.findall(body) if k.upper() == "GGS"
        )
        if rds_parts and rds_parts != sorted(ROLLING_RDS_PER_CYCLE):
            issues.append(f"{day}:c{cnum} RDS split {rds_parts}")
        if ggs_parts and ggs_parts != sorted(ROLLING_GGS_PER_CYCLE):
            issues.append(f"{day}:c{cnum} GGS split {ggs_parts}")
    if re.search(r"buy\s*1\s*get\s*8", name, re.I):
        free_n = len(re.findall(r"\bFree\s+\d+\s*:", desc, re.I))
        if free_n != 8:
            issues.append(f"{day}:Buy1Get8 free={free_n}")
    return issues


def rolling_bxgy_cycle_body(d: int, cycle_index: int, n_cycles: int) -> str:
    free_steps = BXGY_FREE_DENOMS_BY_CYCLES.get(n_cycles, 6)
    r1, r2 = ROLLING_RDS_PER_CYCLE
    g1, g2 = ROLLING_GGS_PER_CYCLE
    booster = dd_on_purchase_addon(d)
    reg = stars_reg(d)
    extras = (
        "150% SB",
        booster,
        "5 Hammers",
        "Dice Booster 12h",
        f"{reg}★ Reg card",
        "Quest Booster",
    )
    stamp_slots = [
        (1, f"{r1} RDS"),
        (2, f"{r2} RDS"),
        (3, f"{g1} GGS"),
        (4, f"{g2} GGS"),
    ]
    parts = [f"Pay — Coins, Gems (no stamps on pay)"]
    for slot, label in stamp_slots:
        parts.append(f"Free {slot}: {label}")
    extra_start = 5
    for i in range(extra_start, free_steps + 1):
        parts.append(f"Free {i}: {extras[(i - extra_start) % len(extras)]}")
    return f"Cycle {cycle_index}: " + " · ".join(parts)


def rolling_bmfl_desc(d: int) -> str:
    """Buy More for Less — 3 cycles; stamps + hammers listed per cycle (lean prize density)."""
    n = ROLLING_BMFL_CYCLES
    lines = ["Platform: Rolling Offer — Buy More for Less"]
    for c in range(1, n + 1):
        stars = _rolling_reg_stars_for_cycle(d, c - 1, n)
        sb = 100 * c
        tier = "low" if c == 1 else ("mid" if c < n else "high")
        hammers = BMFL_HAMMERS_BY_CYCLE[c - 1]
        rds = BMFL_RDS_BY_CYCLE[c - 1]
        ggs = BMFL_GGS_BY_CYCLE[c - 1]
        lines.append(
            f"Cycle {c}: Coins ({tier} tier) + Gems | {sb}% SB | {stars}★ Reg card | "
            f"{hammers} Hammers | {rds} RDS | {ggs} GGS"
        )
    return "\n".join(lines)


def rolling_bxgy_snl_6cycle_desc(d: int) -> str:
    """6-cycle BXGY ladder (reuse 2026-07-01 Battlesheep rolling shape) with SNL SKUs on 8/8."""
    _ = d
    n = 6
    seasonals = ("4 SNL Dice", "Multiwheel", "6 SNL Dice", "2 Multiwheel", "6 SNL Dice", "2 Shield")
    sbs = (100, 150, 200, 250, 300, 300)
    hammers = (5, 5, 10, 10, 12, 15)
    r1, r2 = ROLLING_RDS_PER_CYCLE
    g1, g2 = ROLLING_GGS_PER_CYCLE
    lines = [
        f"Platform: Rolling Offer — Buy X Get Y ({n} cycles).",
        "Seasonal steps: SNL Dice / Multiwheel / Shield (6-cycle template from 2026-07-01, Battlesheep SKUs swapped).",
        rolling_stamp_allocation_note(),
    ]
    for c in range(1, n + 1):
        parts = [
            "Pay — Coins, Gems (no stamps on pay)",
            f"Free 1: {r1} RDS",
            f"Free 2: {r2} RDS",
            f"Free 3: {g1} GGS",
            f"Free 4: {g2} GGS",
            f"Free 5: {seasonals[c - 1]}",
            f"Free 6: {sbs[c - 1]}% SB · {hammers[c - 1]} Hammers",
        ]
        lines.append(f"Cycle {c}: " + " · ".join(parts))
    return "\n".join(lines)


def rolling_bxgy_desc(d: int, cycles: int) -> str:
    """Buy X Get Y — pay denom + N free denoms; stamps in free slots 1–4 only."""
    n = max(1, min(6, int(cycles)))
    if d == 8 and n == 6:
        return rolling_bxgy_snl_6cycle_desc(d)
    lines = [
        f"Platform: Rolling Offer — Buy X Get Y ({n} cycle{'s' if n != 1 else ''}).",
        rolling_stamp_allocation_note(),
    ]
    for c in range(1, n + 1):
        lines.append(rolling_bxgy_cycle_body(d, c, n))
    return "\n".join(lines)


# Day 8: 6-cycle rolling reuses July BXGY ladder with SNL SKUs (explicit stakeholder swap).
ROLLING_SNL_SKU_OVERRIDE_DAYS = frozenset({8})
ROLLING_BMFL_CYCLES = 3
ROLLING_BMFL_PRICING = "High"
BXGY_CYCLE_ROTATION: tuple[int, ...] = (1, 2, 5, 6)

# Back-compat aliases
ROLLING_OFFER_CYCLES = ROLLING_BMFL_CYCLES
ROLLING_OFFER_PRICING = ROLLING_BMFL_PRICING


def assign_rolling_spec(second_offers: dict[int, str | None]) -> dict[int, tuple[str, int]]:
    """Per rolling day: ('bmfl', 3) on MFL anchors; ('bxgy', cycles) elsewhere."""
    out: dict[int, tuple[str, int]] = {}
    bxgy_i = 0
    for d in collect_rolling_days(second_offers):
        if d in ROLLING_MFL:
            out[d] = ("bmfl", ROLLING_BMFL_CYCLES)
        else:
            out[d] = ("bxgy", BXGY_CYCLE_ROTATION[bxgy_i % len(BXGY_CYCLE_ROTATION)])
            bxgy_i += 1
    if 12 in out and out[12][0] == "bxgy":
        out[12] = ("bxgy", 5)
    if 8 in out and out[8][0] == "bxgy":
        out[8] = ("bxgy", 6)
    return out


def resolve_rolling_spec(
    d: int,
    second_offer_pick: str | None,
    rolling_spec: dict[int, tuple[str, int]],
) -> tuple[str, int] | None:
    if d in ROLLING_MFL:
        return ("bmfl", ROLLING_BMFL_CYCLES)
    if second_offer_pick in ("Rolling", "Rolling Offer"):
        return rolling_spec.get(d, ("bxgy", 2))
    return None


def add_rolling_offer_item(
    add,
    d: int,
    kind: str,
    cycles: int,
    offer_pricing_tier: str | None,
) -> None:
    if kind == "bmfl":
        add(rolling_bmfl_name(d), "Rolling offer", ROLLING_BMFL_PRICING, rolling_bmfl_desc(d))
    else:
        pr = offer_pricing_tier or "High"
        add(rolling_bxgy_name(d, cycles), "Rolling offer", pr, rolling_bxgy_desc(d, cycles))


def rolling_offer_desc(d: int) -> str:
    return rolling_bmfl_desc(d)


def collect_rolling_days(second_offers: dict[int, str | None]) -> list[int]:
    days = set(ROLLING_MFL)
    for d, pick in second_offers.items():
        if pick in ("Rolling", "Rolling Offer"):
            days.add(d)
    return sorted(days)


OFFER_PRICING_TIERS: tuple[str, ...] = ("Medium", "High", "Max")


def normalize_offer_pricing(pricing: str | None) -> str | None:
    if not pricing:
        return None
    p = str(pricing).strip()
    low = p.lower()
    if low in ("mid", "medium", "m"):
        return "Medium"
    if low == "max":
        return "Max"
    if low in ("high", "h"):
        return "High"
    return p if p in OFFER_PRICING_TIERS else None


def day_has_priced_secondary_offer(d: int, second_offers: dict[int, str | None]) -> bool:
    if d in ROLLING_MFL:
        return False
    if popup_day_suppresses_standalone_second_offer(d):
        return bool(POPUP_STORE_INNER_OFFER.get(d))
    if d == 22:
        return False
    return bool(second_offers.get(d))


def assign_offer_pricing(second_offers: dict[int, str | None]) -> dict[int, str]:
    """Assign second-offer pricing — calendar week M/H/Max; daily tier ≠ DD. Rolling (BMFL) excluded (always High)."""
    result: dict[int, str] = {}
    for d in range(1, 32):
        if not day_has_priced_secondary_offer(d, second_offers):
            continue
        dd_tier = normalize_offer_pricing(_dd_pricing(is_sale(d))) or "High"
        if dow(d) in ("Tue", "Thu") and dd_tier != "Medium":
            tier = "Medium"
        elif (is_sale(d) or d in EXTREME or d in BETTY_BDAY) and dd_tier != "Max":
            tier = "Max"
        else:
            tier = "High"
        if tier == dd_tier:
            for alt in OFFER_PRICING_TIERS:
                if alt != dd_tier:
                    tier = alt
                    break
        result[d] = tier

    def week_day_list(w: int) -> list[int]:
        return [d for d in range(1, 32) if (d - 1) // 7 == w]

    for w in range(6):
        ds = week_day_list(w)
        if len(ds) < 7:
            continue

        def planned_tiers() -> set[str]:
            found: set[str] = set()
            for d in ds:
                dd_t = normalize_offer_pricing(_dd_pricing(is_sale(d)))
                if dd_t:
                    found.add(dd_t)
                if d in result:
                    found.add(result[d])
            return found

        missing = set(OFFER_PRICING_TIERS) - planned_tiers()
        for need in sorted(missing, key=OFFER_PRICING_TIERS.index):
            for d in ds:
                if d not in result:
                    continue
                dd_t = normalize_offer_pricing(_dd_pricing(is_sale(d))) or "High"
                if need == dd_t:
                    continue
                result[d] = need
                break

    for d, tier in list(result.items()):
        dd_t = normalize_offer_pricing(_dd_pricing(is_sale(d))) or "High"
        if tier == dd_t:
            for alt in OFFER_PRICING_TIERS:
                if alt != dd_t:
                    result[d] = alt
                    break

    # MGAP BOGO/Matched stacks value — second offer must be High (not Medium on Tue/Thu).
    for d in range(1, 32):
        if not day_has_mgap_bogo_or_matched(d):
            continue
        if d not in result:
            continue
        result[d] = "High"

    return result


_STRUCTURE_MARKERS = (
    "platform:",
    "cycle 1:",
    "d1 (",
    "coins denom:",
    "full denoms:",
    "central reward",
    "hook / card",
    "hook prize",
    "bundle focus",
    "mechanic (this instance)",
)


def desc_has_offer_structure(desc: str) -> bool:
    low = (desc or "").lower()
    return any(m in low for m in _STRUCTURE_MARKERS) or len((desc or "").strip()) > 140


def dd_offer_description(name: str, pricing: str | None = None) -> str:
    central = re.sub(r"^DD\s*-\s*", "", name or "", flags=re.I).strip()
    once = any(x in central.lower() for x in ("wild", "shiny limited")) and "multiple" not in central.lower()
    tier = pricing or "High"
    lines = [
        "Platform: Daily Deal — Coins + Gems + 1 central reward slot.",
        f"Central reward (this instance): {central}.",
        f"Pricing: {tier} — SKU generosity scales with tier (High ≈ up to ~8 Hammers equivalent).",
    ]
    if once:
        lines.append(
            "Purchase rule: once-per-player (Wild / Shiny Limited) — pair with a separate DD multiple same day."
        )
    elif "multiple" in central.lower():
        lines.append("Purchase rule: multiple — repeatable after once-per-player DD is bought.")
    else:
        lines.append("Purchase rule: standard DD (multiple purchases unless marked once-per-player).")
    return "\n".join(lines)


def ryd_offer_description(name: str) -> str:
    hook = name.split("—", 1)[-1].strip() if "—" in name else name
    return (
        "Platform: RYD — Coins + Gems + hook prize + RDS + % SlotoBucks.\n"
        f"Hook / card prize (this instance): {hook}.\n"
        "Stamps: RDS on reveal · SB% on top (standard tiers only — never 155% SB)."
    )


def prize_mania_offer_description(name: str) -> str:
    pack = name.split("—", 1)[-1].strip() if "—" in name else name
    return (
        "Platform: Prize Mania — one rich prize bundle (coins + gems + stamps + extras).\n"
        f"Bundle focus (this instance): {pack}."
    )


def coin_sale_offer_description(themed: str = "") -> str:
    extra = f"\nTheme: {themed}." if themed else ""
    return (
        "Platform: Coin Sale — discounted coin packages in store for the sale window.\n"
        "Contents: tiered coin SKUs (pairs with a VFM second offer on Fri/Sat sale days)."
        f"{extra}"
    )


def mgap_offer_description(name: str) -> str:
    detail = "MGAP timed multiplier on qualifying purchases."
    for key, blurb in (
        ("BOGO", "Buy-one-get-one multipliers on qualifying purchase tiers."),
        ("Matched", "Matched multiplier mechanic across purchase tiers."),
        ("Wild Symbols", "Wild-symbols themed multiplier window."),
        ("Bigger Multipliers", "Elevated multiplier tiers (flagship / event)."),
        ("Slotobucks Guaranteed", "Guaranteed SlotoBucks % on qualifying buys."),
    ):
        if key.lower() in (name or "").lower():
            detail = blurb
            break
    return f"Platform: MGAP — purchase multiplier promo (timed).\nMechanic (this instance): {detail}"


def clan_dash_description(name: str, dow: str | None = None, *, day: int | None = None) -> str:
    nl = (name or "").lower()
    dow_bit = f"\nSchedule: {dow} (weekly Clan-Dash template — do not exceed)."
    if "clan dash bundle" in nl:
        mechanic = (
            "Clan Dash Bundle — discounted clan season bundle (Monday Dash Day). "
            "Prize focus: clan progression bundle; payer breadth."
        )
    elif "premium for badge wheel" in nl:
        mechanic = (
            "Clan Go — Go Premium for Badge Wheel / picker. "
            "Prize focus: badge-wheel spins and clan badge earn."
        )
    elif "200 badge" in nl:
        mechanic = (
            "Clan Go — earn up to 200 badges in the daily window (Thursday template). "
            "Prize focus: dash/badge progression."
        )
    elif "monday max deal" in nl:
        mechanic = (
            "Monday Max Deal — premium Monday clan purchase bundle (Dash Day)."
        )
    elif "time limited prize" in nl:
        prize = time_limited_prize_nivi_label(day) if day else "per nivi_collector_album_prizes.md (Dash)"
        mechanic = (
            "Time Limited Prize — timed clan reward window.\n"
            f"Prize: {prize}"
        )
    elif "x2 dash point" in nl:
        mechanic = "X2 Dash Points — double dash-point earn on clan dash missions (Tue/Fri)."
    elif "x2 badge" in nl:
        mechanic = "X2 Badges — double clan badge earn rate (Wednesday)."
    else:
        mechanic = name
    return (
        "Platform: Clan-Dash — payer/recruitment feature (badges, dash points, bundles).\n"
        f"Mechanic (this instance): {mechanic}{dow_bit if dow else ''}"
    )


def ads_po_description(label: str, st_name: str, mt_name: str) -> str:
    return (
        "Platform: ADS PO (SPO) — reward gated by watching an ad; low-tier prize only.\n"
        f"Prize (this instance): {label}.\n"
        f"Context: Short-term {st_name} · Mid-term {mt_name}.\n"
        "Rules: no Gold / Shiny / Wild / 4–5★ Ace on ADS; prize must match active Short/Mid Term (see label)."
    )


def lotto_peak_description(window: str) -> str:
    return (
        "Platform: Lotto Bonus — Night Plan revenue peak (not a coin VFM offer).\n"
        f"Peak window: {window} — Lotto jackpot emphasis on Night Plan.\n"
        "Pairing: exactly one LBP promo on this calendar day (rotate per lotto_bonus.md)."
    )


def lbp_promo_description(promo_name: str, window: str) -> str:
    nl = (promo_name or "").lower()
    if "30% bigger balls" in nl:
        detail = (
            "Lotto balls 30% bigger from 00:00 UTC until Promo Time (11:00 UTC) "
            "on this calendar day — not a 2h window post 12:00 UTC."
        )
    elif "4 balls instead of 3" in nl:
        detail = "4 balls instead of 3 for the Night Plan peak."
    elif "2 multiball" in nl:
        detail = "Two multiball activations during the peak."
    elif "all goldens" in nl:
        detail = "All golden slots active + goldens 20% bigger."
    elif "jackpot ball" in nl and "4 balls" in nl:
        detail = "Jackpot ball +150% and 4 balls instead of 3."
    elif "jackpot ball" in nl and "30% bigger" in nl:
        detail = "Jackpot ball +150% and balls 30% bigger."
    else:
        detail = promo_name
    return (
        "Platform: LBP (Lotto Bonus Peak) — timed Lotto boost on Night Plan.\n"
        f"Mechanic (this instance): {detail}\n"
        f"Peak night: {window}. Rotation: regular six (lotto_bonus.md); "
        "event-only (4 plasma / doubled multiballs) on mega sales only."
    )


X2_EXTREME_STAMP_NAME = "X2 Extreme Stamp"


def x2_extreme_stamp_description() -> str:
    return (
        "Platform: X2 Extreme Stamp — doubles Extreme Stamps earned in offers today (revenue amplifier).\n"
        "Rule: RDS slots → Extreme Stamp (4 RDS → 2 Extreme); no Wild Card mixed in offers.\n"
        "Duration: all day."
    )


def anchor_description(name: str, d: int) -> str:
    nl = (name or "").lower()
    if "status boost" in nl:
        return (
            "Platform: Status Boost — progression / store tier promotion anchor.\n"
            "Mechanic: lifts top store denom visibility — purchase driver (not a separate offer SKU)."
        )
    if "last day shiny collection" in nl:
        return (
            "Platform: Album — Shiny Collection countdown.\n"
            "Mechanic: last day to finish Shiny Collection MS1 before rotation."
        )
    if "shiny collection opening" in nl:
        return (
            "Platform: Album — Shiny Collection opens.\n"
            f"Mechanic: new Shiny Collection set goes live ({d}/8 marketing); feeds Shiny Show goals."
        )
    if "dash pass" in nl:
        return (
            "Platform: Dash Pass — Monday Dash Day anchor.\n"
            "Mechanic: new Dash Pass season for purchase; strong payer breadth — "
            "no extra MGAP / Coin Sale VFM on Mondays."
        )
    if "betty" in nl and "birthday" in nl:
        return (
            "Platform: Core / event — Betty's Birthday themed gameplay.\n"
            "Mechanic: birthday MES / coin-sink tied to marketing 8–9/8."
        )
    return f"Marketing / album anchor ({d}/8): {name}."


def lbp_night_window(d: int) -> str:
    return "Tue→Wed 00:00" if dow(d) == "Tue" else "Sat→Sun 00:00"


def enrich_item_description(
    name: str,
    status: str | None,
    pricing: str | None,
    desc: str | None,
    d: int,
    *,
    on_extreme: bool = False,
) -> str:
    """Monday Description body: how the promo is built + which prizes (offer_construction.md)."""
    if desc_has_offer_structure(desc or ""):
        base = (desc or "").strip()
    else:
        nl = (name or "").lower()
        st = status or ""
        if st == "Daily deal" or nl.startswith("dd"):
            base = dd_offer_description(name, pricing)
            if (desc or "").strip():
                base = f"{base}\n\n{(desc or '').strip()}"
        elif st == "RYD" or nl.startswith("ryd"):
            base = ryd_offer_description(name)
        elif "decoy" in nl or "bonanza" in nl:
            base = (desc or "").strip() or (
                "Platform: Decoy/Bonanza — 3 denoms: d1 coin+RDS · d2 gem+GGS · d3 combined bundle + top prize."
            )
        elif st == "Rolling offer" or "rolling offer" in nl:
            if is_rolling_bmfl_name(name):
                base = (desc or "").strip() or rolling_bmfl_desc(d)
            else:
                m = re.search(r"(\d+)\s*cycles?", nl, re.I)
                cyc = int(m.group(1)) if m else 2
                base = (desc or "").strip() or rolling_bxgy_desc(d, cyc)
        elif "buy all" in nl or st == "Buy all":
            base = (desc or "").strip() or (
                "Platform: Buy All — 2 denoms (Coins+RDS and Gems+GGS); player buys both."
            )
        elif "coin sale" in nl:
            themed = "Back to School" if "back to school" in nl else ""
            base = coin_sale_offer_description(themed)
        elif "prize mania" in nl or st == "Prize Mania":
            base = prize_mania_offer_description(name)
        elif st == "MGAP" or nl.startswith("mgap"):
            base = mgap_offer_description(name)
        elif re.search(r"\bx2\s*extreme\s*stamp", nl, re.I):
            base = x2_extreme_stamp_description()
        elif "extreme stamp" in nl and "fortune dip" not in nl:
            base = x2_extreme_stamp_description()
        elif "gems sale" in nl or "gem sale" in nl:
            base = "Platform: Gems Sale — 30% off gem store / 20% off gem offers for the day."
        elif "gemback" in nl:
            pct = "500%" if "500" in nl else "300%"
            base = f"Platform: Boosted Gemback — {pct} gems back on gem spend (timed window)."
        elif "x2 ggs" in nl:
            base = "Platform: x2 GGS — doubles Gold Gem Stamps earned in offers (3h, post 11:00 UTC)."
        elif "counter po" in nl or st == "Counter PO":
            base = (
                "Platform: Counter PO — segmented personal-offer topper (FTD / payer cohorts).\n"
                f"Prize line: {name}."
            )
        elif "golden spin" in nl:
            base = "Platform: Golden Spin — timed gem feature (2h post 12:00 UTC); not a coin VFM offer."
        elif "shiny show" in nl:
            variant = name.split("—", 1)[-1].strip() if "—" in name else name
            base = (
                "Platform: Shiny Show — gem mini-game; objectives grant shiny/card prizes.\n"
                f"Variant / prizes (this day): {variant}."
            )
        elif "piggy" in nl:
            prize = name.split("for", 1)[-1].strip() if "for" in nl else "see title"
            base = f"Platform: Piggy — purchase breaks piggy bank.\nPrize on break: {prize}."
        elif "fortune dip" in nl:
            base = (
                "Platform: Fortune Dip topper — chance-based SB (up to 700%) layered on offers / Extreme Stamp day."
            )
        elif "dice deluxe" in nl:
            base = "Platform: Dice Deluxe — weekly timed dice offer (coins/gems + dice SKU); ≤1×/week."
        elif "price cut" in nl:
            base = "Platform: Price Cut — 20% storewide discount (purchase promo, not VFM second offer)."
        elif re.search(r"lotto\s*[—-]\s*peak", nl):
            window = lbp_night_window(d)
            base = lotto_peak_description(window)
        elif nl.startswith("lbp") or re.match(r"^lbp\s", nl):
            window = lbp_night_window(d)
            base = lbp_promo_description(name, window)
        elif re.search(r"spinner\s*clash", nl):
            base = spinner_clash_description(d)
        elif re.search(r"\bpyp\b|pick your path", nl, re.I):
            base = (desc or "").strip() or pyp_missions_description(d)
            if "Missions:" not in base:
                base = pyp_missions_description(d)
        elif re.search(r"ace heist", nl):
            base = ace_heist_missions_description(d)
        elif re.search(r"spin zone", nl) and "hammers wheel" not in nl:
            m = re.search(r"spin zone\s*[—-]\s*(.+?)\s*chase", name or "", re.I)
            prize = (m.group(1).strip() if m else None) or spin_zone_chase_prize(d)
            base = spin_zone_core_description(d, prize)
        elif st == "Clan-Dash":
            base = clan_dash_description(name)
        elif st == "ADS" or nl.startswith("ads po"):
            label = re.sub(r"^ADS PO\s*[—-]\s*", "", name or "", flags=re.I).strip() or name
            base = ads_po_description(label, short_term(d), mid_term(d))
        elif "status boost" in nl:
            base = anchor_description(name, d)
        elif "shiny collection" in nl and st == "Core":
            base = anchor_description(name, d)
        elif "dash pass" in nl and "dash day" in nl:
            base = anchor_description(name, d)
        elif st == "Core" and re.search(
            r"pyp|win master|ace heist|spinner clash|spin zone|custom pod|mes|slot smash|ace loot",
            nl,
        ):
            base = (
                "Gameplay Core — coin-sink challenge; complete missions/tasks for prize in title.\n"
                f"{name}"
            )
        else:
            base = (desc or "").strip()

    if (
        on_extreme
        and base
        and "extreme stamp" not in base.lower()
        and (status or "")
        in ("Daily deal", "RYD", "Offers & coin sale", "Buy all", "Rolling offer", "Prize Mania")
    ):
        base += "\n\nExtreme Stamp day: use Extreme Stamp instead of RDS in offer slots (4 RDS → 2 Extreme)."
    return base.strip()


# Pre-planned special slots (deterministic)
MGAP_PER_WEEK = 2  # IRON (user): never >2 per (d-1)//7 slice; full slice (≥4 days) = exactly 2
MGAP_CYCLE_DAYS = 7  # BOGO / Matched ~once per 7-day window (within 2/week cap)
MGAP_BTS_BIGGER_DAY = 22  # Bigger Multipliers — sale-only (Back to School)
MGAP_ALLOWED = frozenset(
    {"BOGO", "Matched", "Wild Symbols", "Slotobucks Guaranteed", "Bigger Multipliers"}
)
MGAP_MIN_GAP_DAYS = 2  # minimum calendar days between MGAP promos (iron spacing)
# Two MGAP per calendar slice; BTS day 22 adds +1 in slice w3 (22+26) — not in SCHEDULE
MGAP_SCHEDULE: dict[int, str] = {
    2: "Matched",
    5: "BOGO",
    9: "Wild Symbols",
    13: "Matched",
    18: "BOGO",
    20: "Wild Symbols",
    26: "BOGO",
    30: "Slotobucks Guaranteed",
}
MGAP_OFFER_HIGH_VARIANTS = frozenset({"BOGO", "Matched"})


def planned_mgap_variant(d: int) -> str | None:
    if d not in MGAP_SCHEDULE or d == MGAP_BTS_BIGGER_DAY:
        return None
    if is_sale(d):
        return None
    v = MGAP_SCHEDULE[d]
    return "Wild Symbols" if v == "Bigger Multipliers" else v


def day_has_mgap_bogo_or_matched(d: int) -> bool:
    v = planned_mgap_variant(d)
    return v in MGAP_OFFER_HIGH_VARIANTS
ROLLING_MFL = {3, 16, 25}  # cooldown ≥10d: 3→16 (13d) · 16→25 (9d — marginal, but 26 conflicts w/ Triple test)
EXTREME = {4, 18, 27}  # Mon off sale; not same day as Price Cut
GEMS_SALE = {6, 13, 20, 27}  # Wed before weekend
GGS_X2 = {8, 15, 22, 29}  # max 2/week -> use 8,15 and 22,29 -> 4 is ok? cap 4/month frequency 2/week = 8-9 total, use 2 per week
# 2 per week: w1 8,15 wrong - week1 days 1-7: ggs 5,7 -> only 2: 5 Thu? 7 Fri sale conflict - 4 Wed 6 Wed after gems
GGS_WEEK = {4: 1, 7: 1, 11: 1, 14: 1, 18: 1, 21: 1, 25: 1, 28: 1}  # 2 per week, never on consecutive days

# Standalone dice promos — max 1 / calendar week (Deluxe or BTS Prize Mania dice; no 24h spam).
DICE_PROMO_MAX_PER_WEEK = 1
BTS_DICE_PROMO_DAY = 22
DICE_DELUXE_FRIDAY = frozenset({7, 14, 21, 28})  # Fri per week block (d-1)//7
DICE_DELUXE_PARTIAL_WEEK = frozenset({29})  # days 29–31 block

DICE_STANDALONE_PROMO_RE = re.compile(
    r"dice deluxe|dice booster 24h purchase|dice booster 6h — non-purchase",
    re.I,
)
DICE_PROMO_IN_OFFER_RE = re.compile(r"prize mania.*dice booster", re.I)


def should_schedule_dice_deluxe(d: int) -> bool:
    if d in DICE_DELUXE_PARTIAL_WEEK:
        return True
    if d not in DICE_DELUXE_FRIDAY:
        return False
    # BTS week: dice promo only via Prize Mania on 22 — skip Fri Deluxe same week.
    if (d - 1) // 7 == (BTS_DICE_PROMO_DAY - 1) // 7:
        return False
    return True


def dice_promo_hits_on_day(day_items: list[dict]) -> int:
    n = 0
    for i in day_items:
        nm = i.get("name") or ""
        if DICE_STANDALONE_PROMO_RE.search(nm):
            n += 1
        elif DICE_PROMO_IN_OFFER_RE.search(nm):
            n += 1
    return n


# Clan-Dash weekly template (Mon–Fri only; Sat/Sun none). Do not add extra Clan-Dash lines.
CLAN_DASH_MONDAY: tuple[tuple[str, str | None], ...] = (
    ("Clan Dash Bundle — 30% discount", "High"),
    ("Clan Go — Premium for Badge Wheel", None),
    ("Monday Max Deal", "High"),
    # Time Limited Prize name built per Monday in add_clan_dash_for_dow (prize in title).
    ("__TIME_LIMITED_PRIZE__", "High"),
)

CLAN_DASH_EXPECTED_SUBSTR: dict[str, tuple[str, ...]] = {
    "Mon": (
        "clan dash bundle",
        "premium for badge wheel",
        "monday max deal",
        "time limited prize",
    ),
    "Tue": ("x2 dash point",),
    "Wed": ("x2 badge",),
    "Thu": ("200 badge",),
    "Fri": ("x2 dash point",),
}


def add_clan_dash_for_dow(dow: str, d: int, add) -> None:
    if dow == "Mon":
        for name, pr in CLAN_DASH_MONDAY:
            if name == "__TIME_LIMITED_PRIZE__":
                name = time_limited_prize_row_name(d)
            add(name, "Clan-Dash", pr, clan_dash_description(name, dow, day=d))
    elif dow == "Tue":
        add("X2 Dash Points", "Clan-Dash", None, clan_dash_description("X2 Dash Points", dow, day=d))
    elif dow == "Wed":
        add("X2 Badges", "Clan-Dash", None, clan_dash_description("X2 Badges", dow, day=d))
    elif dow == "Thu":
        add(
            "Clan Go — up to 200 badges",
            "Clan-Dash",
            None,
            clan_dash_description("Clan Go — up to 200 badges", dow, day=d),
        )
    elif dow == "Fri":
        add("X2 Dash Points", "Clan-Dash", None, clan_dash_description("X2 Dash Points", dow, day=d))


def clan_dash_items_for_day(day: dict) -> list[dict]:
    return [i for i in day.get("items") or [] if (i.get("status") or "") == "Clan-Dash"]


def validate_clan_dash_week(days: list[dict]) -> list[str]:
    bad: list[str] = []
    for day in days:
        d = int(day["date"])
        dow = day["dow"]
        clan = clan_dash_items_for_day(day)
        if dow in ("Sat", "Sun"):
            if clan:
                bad.append(f"{d}:Clan-Dash on {dow}")
            continue
        if dow not in CLAN_DASH_EXPECTED_SUBSTR:
            continue
        expected = CLAN_DASH_EXPECTED_SUBSTR[dow]
        names = [(i.get("name") or "").lower() for i in clan]
        want_count = len(expected)
        if len(clan) != want_count:
            bad.append(f"{d}:{dow} count={len(clan)} want {want_count}")
        for sub in expected:
            if not any(sub in n for n in names):
                bad.append(f"{d}:{dow} missing «{sub}»")
        for n in names:
            if not any(sub in n for sub in expected):
                bad.append(f"{d}:{dow} extra «{n[:40]}»")
    return bad

PRICE_CUT = {11, 26}  # no Monday Dash Day (was 10, 24)
COUNTER_PO = {9, 23}  # Sun, not sale
# Economy / learnings: exactly 2 Daily Deal BOGO per calendar month (each needs economy task config).
DD_BOGO_REQUIRED_PER_MONTH = 2
DD_BOGO_DAYS = frozenset({9, 30})  # Aug: Sun post–Betty (gem drain) + late-month Sun
# Must ship (on purchase) card DD — not Shiny Limited once-pair on this date.
DD_ON_PURCHASE_DAYS = frozenset({12})
if len(DD_BOGO_DAYS) != DD_BOGO_REQUIRED_PER_MONTH:
    raise ValueError(f"DD_BOGO_DAYS must have exactly {DD_BOGO_REQUIRED_PER_MONTH} days")
FORTUNE_DIP_DAYS = {8}  # 1×/month — sale Sat Betty Birthday (strong topper)
LIMITED_PO: set[int] = set()  # removed — "sale-only mechanic" should appear only on sale days; non-sale Mondays get regular offers from pool
SHINY_WOLF = {6, 13, 20, 27}  # 1/week Wed
SHINY_SHOW_MAX_PER_WEEK = 3
SHINY_SHOW_MIN_GAP_DAYS = 2  # minimum days between Shiny Show promos (same month)
# Indexed by (d-1)//7 — must match calendar week slices, not marketing “week N”.
SHINY_BY_WEEK: tuple[tuple[int, ...], ...] = (
    (1, 4, 6),
    (11, 13),
    (18, 20),
    (25, 27),
    (30,),
)
SHINY_SHOW_DAYS = frozenset(d for week in SHINY_BY_WEEK for d in week)
# Extra Shiny Show (Betty sale) — does not reshuffle SHINY_BY_WEEK slot variants for 11/13.
SHINY_SHOW_SCHEDULE_EXTRA = frozenset({8})
SHINY_SHOW_DAY_OVERRIDES: dict[int, str] = {
    8: "Joker Different Prizes",  # Betty's Birthday Sat — gem sink atop week Shiny Shows
}
SHINY_SHOW_ALL_DAYS = SHINY_SHOW_DAYS | SHINY_SHOW_SCHEDULE_EXTRA
# Shiny Show variants that consume Nivi Shiny Limited weekly budget (offers table).
SHINY_SHOW_NON_BUDGET_VARIANTS = (
    "Joker All Cards",
    "All Cards",
    "Crazy with Aces",
    "Joker Different Prizes",
)


def shiny_show_variant_uses_nivi_budget(label: str) -> bool:
    low = (label or "").lower()
    return "wild guaranteed" in low or "shiny limited" in low


def assign_shiny_show_variants(dd_keys: dict[int, str] | None = None) -> tuple[dict[int, str], dict[int, int]]:
    """≤3 Shiny Show / week. Budget variants (Shiny Limited / Wild Guaranteed) only if DD did not exhaust cap."""
    sim = CardLedger()
    sim.take(23, "Shiny Card")
    if dd_keys:
        for d in range(1, 32):
            k = dd_keys.get(d)
            if k:
                sim.build_dd_lines(d, k, is_sale(d))
    show_budget_consumed = {1: 0, 2: 0, 3: 0, 4: 0}
    out: dict[int, str] = {}
    for widx, week_days in enumerate(SHINY_BY_WEEK):
        for slot, d in enumerate(week_days):
            cw = card_week(d)
            cap = CARD_BUDGETS[cw].get("Shiny Limited", 0)
            dd_sl = sim.used[cw].get("Shiny Limited", 0)
            rem_sl = sim.rem[cw].get("Shiny Limited", 0)
            # Prefer selling Shiny Limited / Wild in DD; Shiny Show uses budget only if room left (max 1/show week).
            use_budget_in_show = (
                rem_sl > 0
                and show_budget_consumed[cw] < 1
                and (dd_sl >= 1 or cap >= 2)
                and slot == len(week_days) - 1
            )
            if use_budget_in_show:
                variant = (
                    "Wild Guaranteed"
                    if cw >= 3 and dd_sl >= 1
                    else "Shiny Limited (theme)"
                )
                show_budget_consumed[cw] += 1
            else:
                pool = list(SHINY_SHOW_NON_BUDGET_VARIANTS)
                variant = pool[(widx + slot) % len(pool)]
                used = {out[wd] for wd in week_days[:slot] if wd in out}
                if variant in used:
                    for v in pool:
                        if v not in used:
                            variant = v
                            break
            out[d] = variant
    for d in SHINY_SHOW_SCHEDULE_EXTRA:
        out[d] = SHINY_SHOW_DAY_OVERRIDES.get(d, out.get(d, SHINY_SHOW_NON_BUDGET_VARIANTS[0]))
    return out, show_budget_consumed

LBP_PROMOS = [
    "LBP — 30% Bigger Balls (Night Plan peak)",
    "LBP — 4 balls instead of 3 (Night Plan peak)",
    "LBP — 2 multiballs (Night Plan peak)",
    "LBP — all goldens + 20% bigger (Night Plan peak)",
    "LBP — Jackpot ball 150% + 4 balls (Night Plan peak)",
    "LBP — Jackpot ball 150% + 30% bigger (Night Plan peak)",
]
MACHINE_SNEAK = {18}  # marketing 17/8 — board row Tue 18 (avoid Monday Dash clutter)
MACHINE_LAUNCH = {19}  # marketing calendar New Machine 19/8
MACHINE_THEME_CORE_DAYS = {19, 20, 21}  # launch + 2 days: Core promos in machine theme
# Standard 300% Gemback — not on Monday Dash Day. Avoid stacking x2 GGS + Gemback + Price Cut same day
# (Aug 2026: Gemback on 12/25; Popup Store soft launch 1/3 on 12 — not stacked with 11/8 GGS + Price Cut.)
GEMBACK = {12, 25}


def day_gem_revenue_amplifier_count(day_items: list[dict]) -> int:
    """x2 GGS + Boosted Gemback + Price Cut on one day over-concentrates revenue (spread to adjacent weak days)."""
    n = 0
    for i in day_items:
        nm = i.get("name") or ""
        if "x2 GGS" in nm:
            n += 1
        elif "Gemback" in nm and (i.get("status") == "Gems" or "Boosted Gemback" in nm):
            n += 1
        elif "Price Cut" in nm:
            n += 1
    return n

# Marketing / album calendar (image) — only items not already covered elsewhere
STATUS_BOOST = {1}
SHINY_COLLECTION_LAST = {3}  # Last day 1st Shiny Collection
SHINY_COLLECTION_OPEN = {4: 2, 25: 3}  # day -> opening number
BETTY_BDAY = {8, 9}
NOSTALGIC_WEEKEND = {14, 15, 16}
# --- Two independent tests (do not merge Puzzle vs Popup in naming) ---
# Puzzle M.E.S: Core gameplay soft launch, 7 days from 18/8 (~20% cohort).
PUZZLE_MES_TEST = range(18, 25)
PUZZLE_MES_DAY_COUNT = len(tuple(PUZZLE_MES_TEST))
PUZZLE_MES_COHORT_PCT = 20
PUZZLE_MES_PHASE = "Soft Launch 20%"
# Popup Store: TEST/LAUNCH on 12 / 19 / 26 only (not Puzzle window; not other days).
POPUP_STORE_DAYS = frozenset({12, 19, 26})
POPUP_STORE_PHASE_BY_DAY: dict[int, tuple[str, str]] = {
    12: ("TEST", "Soft launch"),
    19: ("TEST", "2nd soft launch"),
    26: ("LAUNCH", "Full launch"),
}
POPUP_STORE_INNER_OFFER: dict[int, str | None] = {
    12: "Decoy Bonanza",
    19: "Decoy Bonanza",
    26: None,  # Full launch — Popup shell only (no paired Decoy)
}
POPUP_STORE_LAUNCH_SHELL_ONLY = frozenset({26})
POPUP_LAUNCH_RYD_BACKUP_SUFFIX = " · BACKUP cap (if Popup Store LAUNCH slips)"


def popup_launch_ryd_is_backup_cap(d: int, pick: str | None) -> bool:
    """26/8 full launch: Popup is the VFM surface; RYD row is contingency only."""
    return d in POPUP_STORE_LAUNCH_SHELL_ONLY and pick == "RYD"


def popup_day_suppresses_standalone_second_offer(d: int) -> bool:
    """12/19: VFM lives in Popup inner offer; 26 shell-only still gets a normal second offer."""
    if d not in POPUP_STORE_DAYS:
        return False
    if d in POPUP_STORE_LAUNCH_SHELL_ONLY:
        return False
    return bool(POPUP_STORE_INNER_OFFER.get(d))


# Legacy alias (builder only — was separate Segmented Decoy rows; now Popup Store only).
SEGMENTED_DECOY_TEST: dict[int, str] = {}
TRIPLE_OFFER_TEST = SEGMENTED_DECOY_TEST
POPUP_STORE_OFFER_KINDS = frozenset(
    {"RYD", "Buy All", "Decoy Bonanza", "Mystery Buy All", "Rolling Offer"}
)
# Legacy alias (builder only)
PUZZLE_POPUP_STORE_OFFER = POPUP_STORE_INNER_OFFER
AUGUST_MACHINE = "Hoppin' For Gold"

SHINY_MS2_COUNTDOWN_LAST = (22, 23, 24)  # Phase 2 / Shiny MS2 ends 24/8 — need Shiny Card sources

HAMMER_DAYS = {4, 12, 20, 27}  # ≤4 per calendar week; spread DOW (not every Saturday)

# Loot event: 48h engagement window (Sun→Mon post-sale, mid-month)
LOOT_START = 9  # starts day 9 (Sunday evening)
LOOT_DAYS = {9, 10}  # 48h span: Sun 9/8 → Mon 10/8

REAL_CORE_CHALLENGE_RE = re.compile(
    r"win master|ace heist|pyp|pick your path|spin zone|spinner clash|puzzle m\.e\.s|"
    r"mes — purchase|hoppin|sneak peek|machine launch|betty.*mes|"
    r"dash pass|piggy|loot",  # day-of-week anchors count as the day's core challenge
    re.I,
)

CORE_CHALLENGE_POOL = ("win_master", "ace_heist", "pyp", "spinner", "mes", "spin_zone")


def dow(d: int) -> str:
    # 2026-08-01 is Saturday
    return WEEKDAYS[(5 + d - 1) % 7]


def august_iso_week_key(d: int) -> tuple[int, int]:
    return date(2026, 8, d).isocalendar()[:2]


AUGUST_ISO_WEEKS_ORDERED: tuple[tuple[int, int], ...] = tuple(
    sorted({august_iso_week_key(d) for d in range(1, 32)})
)


def spinner_biweek_index(d: int) -> int:
    """0-based biweek bucket: pairs of ISO weeks in August (31+32, 33+34, …)."""
    return AUGUST_ISO_WEEKS_ORDERED.index(august_iso_week_key(d)) // 2


def spinner_biweek_count() -> int:
    return (len(AUGUST_ISO_WEEKS_ORDERED) + 1) // 2


def _pick_spinner_clash_day(days: list[int], skip: set[int]) -> int:
    for pref in ("Wed", "Tue", "Thu", "Sat", "Sun", "Fri", "Mon"):
        for d in sorted(days):
            if d in skip or d in SHINY_MS2_COUNTDOWN_LAST:
                continue
            if dow(d) == pref:
                return d
    return next((d for d in sorted(days) if d not in skip), sorted(days)[0])


def compute_spinner_clash_days() -> frozenset[int]:
    """One Spinner Clash per two ISO calendar weeks (biweekly — rules_cheatsheet / constraints)."""
    skip = set(MACHINE_SNEAK) | MACHINE_LAUNCH | {8}
    by_week: dict[tuple[int, int], list[int]] = defaultdict(list)
    for d in range(1, 32):
        by_week[august_iso_week_key(d)].append(d)
    weeks_sorted = sorted(by_week)
    chosen: list[int] = []
    for i in range(0, len(weeks_sorted), 2):
        block = weeks_sorted[i : i + 2]
        pool: list[int] = []
        for wk in block:
            pool.extend(by_week[wk])
        chosen.append(_pick_spinner_clash_day(pool, skip))
    return frozenset(chosen)


# Explicit gameplay coin-sink on every Monday Dash Day (separate from Dash Pass / Clan-Dash row).
FORCE_CORE_CHALLENGE_DAYS = frozenset(d for d in range(1, 32) if dow(d) == "Mon")
SPINNER_CLASH_DAYS = compute_spinner_clash_days()
SPINNER_CLASH_MAX_PER_BIWEEK = 1
# Daily Deal BOGO — only repeatable / multi-purchase central rewards (not Once Wild / Shiny Limited).
DD_BOGO_ELIGIBLE_DD_KEYS = frozenset({"reg_hw", "gold_as", "sb8_h", "combo", "ace_sb", "shiny_mt"})


def is_sale(d: int) -> bool:
    return dow(d) in ("Fri", "Sat")


def lbp_peak_days() -> tuple[int, ...]:
    """Tue + Sat nights only — Lotto peak and LBP promo ship together (lotto_bonus.md)."""
    return tuple(d for d in range(1, 32) if dow(d) in ("Tue", "Sat"))


def short_term_sku(d: int) -> str:
    st = short_term(d).lower()
    if "battlesheep" in st:
        return "2 Parasheep"
    if "snl" in st:
        return "2 Dice"
    if "blast" in st:
        return "Superboom"
    return "2 Picks"


# Visible title hook: Superboom → PAB on these days only (Aug plan / Monday).
BLAST_TITLE_PAB_DAYS = frozenset({1, 3, 16, 18})


def blast_title_sku(d: int, sku: str) -> str:
    if d in BLAST_TITLE_PAB_DAYS and sku == "Superboom":
        return "PAB"
    return sku


# Spin Zone title prizes — not the same as offer filler SKUs (2 Dice / 2 Picks are too weak as chase headlines).
SPIN_ZONE_WEAK_CHASE_RE = re.compile(r"\b2 dice\b|\b2 picks\b", re.I)


# User-approved chase headlines (Aug 1–15 card-bank pass); default logic below.
SPIN_ZONE_CHASE_OVERRIDES: dict[int, str] = {
    6: "4★ Ace card",  # keep Monday Spin Zone headline
    13: "4★ Reg card",
}


def spin_zone_chase_prize(d: int) -> str:
    if d in SPIN_ZONE_CHASE_OVERRIDES:
        return SPIN_ZONE_CHASE_OVERRIDES[d]
    st = short_term(d).lower()
    if "battlesheep" in st:
        return "2 Parasheep"
    if "snl" in st:
        return f"{stars_ace(d)}★ Ace card"
    if "blast" in st:
        return "Superboom"
    return f"{stars_reg(d)}★ Reg card"


def spin_zone_core_description(d: int, prize: str) -> str:
    return (
        "Platform: Spin Zone — coin-sink Core; complete spins/missions for prize in title.\n"
        f"Prize (this instance): {prize}.\n"
        f"Short-term context: {short_term(d)}."
    )


def ads_short_term_sku(d: int) -> str:
    """ADS PO must not award Superboom — use picks on Blast weeks."""
    sku = short_term_sku(d)
    return "2 Picks" if sku == "Superboom" else sku


def dd_on_purchase_addon(d: int) -> str:
    """Second SKU on card DD (on purchase) — must match active Short-Term (lanes.md)."""
    st = short_term(d).lower()
    if "blast" in st:
        return blast_title_sku(d, ("Superboom", "PAB", "Picks")[(d - 1) % 3])
    if "battlesheep" in st:
        return ("AS", "2 Parasheep")[(d - 1) % 2]
    if "snl" in st:
        return ("2 Dice", "Multiwheel", "Shield")[(d - 1) % 3]
    return "AS"


def dd_on_purchase_line(card_label: str, d: int) -> str:
    return f"DD- {card_label} card (on purchase) + {dd_on_purchase_addon(d)}"


def dd_feature_sku_lines(key: str, d: int, sale: bool) -> list[DDLine] | None:
    """Curated DD — no card from weekly bank (Itay Aug 1–15 card-bank fixes)."""
    pr = _dd_pricing(sale)
    if key == "feat_pab_quest":
        return [("DD- PAB + Quest Booster", pr, "Blast — feature bundle (no card)")]
    if key == "battlesheep_feats":
        return [("DD- AS + 2 Parasheep", "Max" if sale else pr, "Battlesheep — feature bundle (no card)")]
    if key == "snl_shield_dice":
        card_part = " (on purchase)" if d in DD_ON_PURCHASE_DAYS else ""
        return [
            (
                f"DD- Shield + 4 Dice{card_part}",
                pr,
                "SNL — Shield + 4 Dice (no Gold card)",
            )
        ]
    if key == "snl_quest_combo":
        return [
            (
                "DD- Quest Booster + Shield + Multiwheel",
                pr,
                "Quest season — feature bundle (no card)",
            )
        ]
    return None


def promo_duration_note(promo_name: str) -> str:
    """Purchase promos (not offers): default 2h TL; listed exceptions."""
    low = (promo_name or "").lower()
    if re.search(r"lotto\s*[—-]\s*peak", low):
        return ""  # Night Plan peak label; mechanic window is on the paired LBP row
    if re.match(r"^lbp\s", low.strip()) or low.startswith("lbp —"):
        return (
            "Duration: 00:00 UTC → 11:00 UTC (Promo Time) on this calendar day — "
            "not 2h time-limited post 12:00 UTC."
        )
    if "gemback" in low:
        return "Duration: 5h (post 11:00 UTC)."
    if "x2 ggs" in low:
        return "Duration: 3h (post 11:00 UTC)."
    if any(
        x in low
        for x in (
            "price cut",
            "extreme stamp",
            "coin coupon",
            "gem coupon",
            "coin sale",
            "gems sale",
            "gem sale",
            "status boost",
        )
    ):
        return "Duration: all day."
    if low.startswith("mgap"):
        return "Duration: 2h time-limited (post 12:00 UTC)."
    return "Duration: 2h time-limited (post 12:00 UTC)."


def with_purchase_promo_timing(name: str, desc: str) -> str:
    """Timing belongs in LiveOps/config — not Monday Description boilerplate."""
    return (desc or "").strip()


def ads_reg_star(d: int) -> int:
    """ADS PO — low reg only (1–3★ per day_planning_template)."""
    return {1: 2, 2: 3, 3: 3, 4: 3}.get(card_week(d), 3)


# Rotate low-tier ADS prizes — no Gold / Shiny / Wild / high Ace.
ADS_PO_CYCLE: tuple[str, ...] = (
    "Coins",
    "Gems",
    "Picks",
    "Season",
    "Reg",
    "Gems",
    "Mid",
    "Coins",
    "Season",
    "Picks",
    "Reg",
    "Mid",
)


def ads_po_for_day(d: int) -> tuple[str, str]:
    key = ADS_PO_CYCLE[(d - 1) % len(ADS_PO_CYCLE)]
    st_name = short_term(d)
    if key == "Coins":
        label = "Coins"
    elif key == "Gems":
        label = "Gems"
    elif key == "Picks":
        if "blast" in st_name.lower():
            label = "2 Picks"
        else:
            label = ads_short_term_sku(d)
    elif key == "Season":
        label = ads_short_term_sku(d)
    elif key == "Reg":
        label = f"{ads_reg_star(d)}★ Reg card"
    else:  # Mid
        mt = mid_term(d)
        if mt == "Globez":
            label = "3000 Hero Coins"
        elif mt == "Figz":
            label = "3000 Figz Coins"
        else:
            label = "Quest Booster"
    name = f"ADS PO — {label}"
    desc = ads_po_description(label, st_name, mid_term(d))
    return name, desc


def mid_term_booster(d: int) -> str:
    mt = mid_term(d).lower()
    if "globez" in mt:
        return "3000 Hero Coins"
    if "figz" in mt:
        return "3000 Figz Coins"
    return "Quest Booster"


def decoy_bonanza_item(d: int, top_card: str, title: str = "Decoy Bonanza", ggs_d3: int = 2) -> tuple[str, str]:
    """d3 stamp bundle: default 4 RDS + 2 GGS; ggs_d3=1 is valid per offer_construction.md (Itay Jul 2026)."""
    d1 = f"Coins + 4 RDS + {short_term_sku(d)}"
    d2 = f"Gems + 1 GGS + {mid_term_booster(d)}"
    d3 = f"Coins + Gems + 4 RDS + {ggs_d3} GGS + 3 Hammers + 100% SB + {top_card}"
    short = f"{title} — d3: {top_card} + bundle | H Pricing"
    desc = (
        f"d1 (coin+RDS base): {d1}\n"
        f"d2 (gem+GGS base, decoy middle): {d2}\n"
        f"d3 (bundle): {d3}"
    )
    return short, desc


def decoy_bundle_fingerprint(desc: str) -> str:
    m = re.search(r"Full denoms:\s*([^\n]+)", desc or "")
    if m:
        return m.group(1).strip()
    parts = []
    for line in (desc or "").splitlines():
        s = line.strip()
        if re.match(r"d[123] \(", s):
            parts.append(s)
    return " | ".join(parts) if parts else ""


def pick_paired_decoy_top(
    d: int,
    reg: int,
    ace: int,
    gold: int,
    ledger: CardLedger | None,
    *,
    allow_wild: bool,
) -> str:
    """One top-card pick shared by control + test on segmented test days."""
    return offer_top_card(
        d, reg, ace, gold, ledger, allow_wild=allow_wild, allow_shiny_ltd=False
    )


def add_segmented_decoy_test_with_control(
    d: int,
    phase: str,
    reg: int,
    ace: int,
    gold: int,
    ledger: CardLedger | None,
    add,
    *,
    on_extreme: bool,
) -> str:
    """Control Decoy + segmented test cohort — identical d1/d2/d3 SKUs."""
    top = pick_paired_decoy_top(d, reg, ace, gold, ledger, allow_wild=not on_extreme)
    ctrl_name, ctrl_desc = decoy_bonanza_item(d, top)
    add(
        ctrl_name,
        "Offers & coin sale",
        "High",
        f"{ctrl_desc}\nControl cohort — same SKUs as segmented Decoy test; segments do not overlap.",
    )
    test_desc = decoy_bonanza_item(d, top)[1]
    add(
        f"Segmented test — Decoy ({phase})",
        "Segmented test",
        "High",
        f"{test_desc}\nTest cohort — same SKUs as control Decoy (see control line).",
    )
    return top


add_triple_test_with_control_decoy = add_segmented_decoy_test_with_control  # legacy alias


# Nivi Aug 2026 — cards distribution image (Wild Ord/Gold only as in weekly bank).
def offer_top_card(
    d: int,
    reg: int,
    ace: int,
    gold: int,
    ledger: CardLedger | None = None,
    *,
    allow_wild: bool = True,
    allow_shiny_ltd: bool = False,
    allow_shiny_card: bool = False,
) -> str:
    if ledger:
        order = list(OFFER_CARD_PICK_ORDER)
        if not allow_wild or wild_reserved_for_future_dd(d):
            order = [k for k in order if not k.startswith("Wild")]
        if not allow_shiny_ltd:
            order = [k for k in order if k != "Shiny Limited"]
        if not allow_shiny_card:
            order = [k for k in order if k != "Shiny Card"]
        k = ledger.pick_first(d, tuple(order))
        if k:
            return card_key_to_short_top(k)
    if gold and card_week(d) >= 1:
        return f"{gold}★ Gold"
    return f"{stars_reg(d)}★ Reg"


def buy_all_coins_hook(d: int, ledger: CardLedger | None, reg: int, ace: int) -> str:
    if ledger and not wild_reserved_for_future_dd(d):
        wk = ledger.pick_first(d, WILD_PICK_ORDER)
        if wk:
            return f"Coins+RDS+{card_key_to_label(wk)}"
        rk = ledger.pick_reg(d, prefer_high=False)
        if rk:
            return f"Coins+RDS+{card_key_to_label(rk)}"
    return f"Coins+RDS+{reg}★ Reg"


def buy_all_item(
    d: int,
    reg: int,
    ace: int,
    gold: int,
    pricing: str = "High",
    ledger: CardLedger | None = None,
) -> tuple[str, str]:
    if d == 10:
        p = pricing if pricing in ("High", "Max", "Mid", "Medium") else "High"
        coins_hook = "Coins+RDS + 2 Parasheep + AS"
        gems_hook = "Gems + 1 GGS + 3000 Hero Coins"
        name = f"Buy All - Coins: {coins_hook} | Gems: {gems_hook} | {p[0]} Pricing"
        desc = f"Coins denom: {coins_hook}\nGems denom: {gems_hook}"
        return name, desc
    st = short_term_sku(d)
    mt = mid_term_booster(d)
    if ledger:
        coins_hook = buy_all_coins_hook(d, ledger, reg, ace) + f" + {st}"
        gk = ledger.pick_gold(d, prefer_high=False)
        rk = ledger.pick_reg(d, prefer_high=False) if not gk else None
        if gk:
            gems_hook = f"Gems + 1 GGS + {card_key_to_label(gk)} + {mt}"
        elif rk:
            gems_hook = f"Gems + 1 GGS + {card_key_to_label(rk)} + {mt}"
        else:
            gems_hook = f"Gems + 1 GGS + {reg}★ Reg + {mt}"
    else:
        coins_hook = f"Coins + 4 RDS + {reg}★ Reg + {st}"
        gems_hook = f"Gems + 1 GGS + {gold}★ Gold + {mt}" if gold else f"Gems + 1 GGS + {reg}★ Reg + {mt}"
    p = pricing if pricing in ("High", "Max", "Mid", "Medium") else "High"
    name = f"Buy All - Coins: {coins_hook} | Gems: {gems_hook} | {p[0]} Pricing"
    desc = f"Coins denom: {coins_hook}\nGems denom: {gems_hook}"
    return name, desc


def buy_all_prize_parts(
    d: int,
    reg: int,
    ace: int,
    gold: int,
    ledger: CardLedger | None = None,
) -> list[str]:
    """Prize lines for Mystery Buy All (same pool as Buy All, one line per prize)."""
    st = short_term_sku(d)
    mt = mid_term_booster(d)
    lines = ["Coins", "Gems", "4 RDS", "1 GGS"]
    if d == 10:
        lines.extend(["2 Parasheep", "AS", "3000 Hero Coins"])
        return lines
    if ledger:
        ch = buy_all_coins_hook(d, ledger, reg, ace)
        if ch.startswith("Coins+RDS+"):
            lines.append(ch[len("Coins+RDS+") :])
        else:
            lines.append(f"{reg}★ Reg")
        lines.append(st)
        gk = ledger.pick_gold(d, prefer_high=False)
        rk = ledger.pick_reg(d, prefer_high=False) if not gk else None
        if gk:
            lines.append(card_key_to_label(gk))
        elif rk:
            lines.append(card_key_to_label(rk))
        else:
            lines.append(f"{reg}★ Reg")
        lines.append(mt)
    else:
        lines.append(f"{reg}★ Reg")
        lines.append(st)
        lines.append(f"{gold}★ Gold" if gold else f"{reg}★ Reg")
        lines.append(mt)
    return lines


def mystery_buy_all_item(
    d: int,
    reg: int,
    ace: int,
    gold: int,
    pricing: str = "High",
    ledger: CardLedger | None = None,
) -> tuple[str, str]:
    p = pricing if pricing in ("High", "Max", "Mid", "Medium") else "High"
    parts = buy_all_prize_parts(d, reg, ace, gold, ledger)
    name = f"Mystery Buy All | {p[0]} Pricing"
    desc = (
        "Platform: Mystery Buy All — same rewards as Buy All; each prize on its own line "
        "(not split into coin/gem denoms).\n" + "\n".join(parts)
    )
    return name, desc


def ryd_card_hook(d: int, reg: int, ace: int, gold: int, ledger: CardLedger | None = None) -> str:
    if d == 14:
        return f"{stars_reg(d)}★ Reg + PAB + 100% SB"
    if ledger:
        gk = ledger.pick_gold(d, prefer_high=True)
        if gk:
            return f"{card_key_to_label(gk)} Card + 100% SB"
        rk = ledger.pick_reg(d, prefer_high=True)
        if rk:
            return f"{card_key_to_label(rk)} + 100% SB"
    if gold and card_week(d) >= 2:
        return f"{gold}★ Gold Card + 100% SB"
    return f"{reg}★ Reg + 100% SB"


def prize_mania_line(d: int, reg: int, ace: int, gold: int, ledger: CardLedger | None = None) -> str:
    if d == 6:
        if ledger:
            ledger.take(d, "Reg_3")
        return f"Prize Mania — {stars_reg(d)}★ Reg pack | Coins, Gems"
    if ledger:
        if d % 2 == 0:
            gk = ledger.pick_gold(d, prefer_high=False)
            if gk:
                return f"Prize Mania — {card_key_to_label(gk)} pack | Coins, Gems"
        order = OFFER_CARD_PICK_ORDER
        order = tuple(
            k
            for k in order
            if not k.startswith("Wild")
            and k not in ("Shiny Limited", "Shiny Card")
            and not k.startswith("Ace")
        )
        k = ledger.pick_first(d, order)
        if k and "Reg" not in k:
            return f"Prize Mania — {card_key_to_label(k)} pack | Coins, Gems"
    options: list[str] = []
    if gold and card_week(d) >= 2:
        options.append(f"{gold}★ Gold pack | Coins, Gems")
    options.append(f"{reg}★ Reg pack | Coins, Gems")
    pick = options[0] if d % 2 == 0 and options else options[(d * 5) % len(options)]
    return f"Prize Mania — {pick}"


DDLine = tuple[str, str, str]  # name, pricing, desc

# Companion repeatable DD after once-per-player Shiny Limited / Wild (High tier = 8 Hammers).
DD_REPEATABLE_SB_HAMMERS_NAME = "DD- 100% SB + 8 Hammers (multiple)"
DD_REPEATABLE_SB_HAMMERS_DESC = (
    "Repeatable DD after once-per-player Shiny Limited / Wild purchase — 100% SB + 8 Hammers."
)


def _dd_pricing(sale: bool) -> str:
    return "Max" if sale else "High"


def day_has_rolling_bmfl_offer(d: int) -> bool:
    return d in ROLLING_MFL


def adjust_dd_pricing_vs_rolling(dd_pr: str, d: int, second_offer_pick: str | None) -> str:
    """BMFL is always High — DD tier must differ on MFL days."""
    _ = second_offer_pick
    if not day_has_rolling_bmfl_offer(d):
        return dd_pr
    if normalize_offer_pricing(dd_pr) == normalize_offer_pricing(ROLLING_BMFL_PRICING):
        return "Max"
    return dd_pr


def adjust_dd_pricing_vs_mgap_high_offers(
    dd_pr: str, d: int, offer_tier: str | None
) -> str:
    """MGAP BOGO/Matched days: second offer is High — DD cannot share High tier."""
    if not day_has_mgap_bogo_or_matched(d):
        return dd_pr
    if normalize_offer_pricing(offer_tier) != "High":
        return dd_pr
    if normalize_offer_pricing(dd_pr) == "High":
        return "Medium"
    return dd_pr


def default_daily_deal_lines(d: int, sale: bool) -> list[DDLine]:
    reg, ace, gold = stars_reg(d), stars_ace(d), stars_gold(d)
    pr = _dd_pricing(sale)
    if d in (7, 14, 21, 28):
        return [
            ("DD - Shiny Limited - Once", pr, "Once + multiple below"),
            (DD_REPEATABLE_SB_HAMMERS_NAME, "High", DD_REPEATABLE_SB_HAMMERS_DESC),
        ]
    if gold and (d - 1) % 7 in (2, 5):
        return [(dd_on_purchase_line(f"{gold}★ Gold", d), pr, "")]
    if (d - 1) % 7 in (1, 3, 6):
        return [(f"DD- {reg}★ Reg card + SB Wheel", pr, "")]
    return [(f"DD- {reg}★ Reg card + Hammers Wheel", pr, "")]


def alternate_daily_deal_lines(d: int, sale: bool) -> list[list[DDLine]]:
    """Fallback DD shapes — Nivi card bank + common Monday DD patterns (no Wild)."""
    if d in (7, 14, 21, 28):
        return []
    reg, ace, gold = stars_reg(d), stars_ace(d), stars_gold(d)
    pr = _dd_pricing(sale)
    mt = mid_term_booster(d)
    alts: list[list[DDLine]] = []
    if card_week(d) == 1 and reg == 3:
        alts.append([("DD- 4★ Reg card + Hammers Wheel", pr, "Nivi wk1 — 4★ Reg")])
    if reg:
        alts.append([(f"DD- {reg}★ Reg card + SB Wheel", pr, "")])
    if gold:
        alts.append([(dd_on_purchase_line(f"{gold}★ Gold", d), pr, "")])
    alts.append([("DD- Shiny Card (multiple)", pr, "Album bank")])
    alts.append([(f"DD- Shiny Card + {mt} (multiple)", pr, f"Mid-term: {mt}")])
    alts.append([("DD- 100% SB + 8 Hammers", pr, "")])
    alts.append([("DD- Cards & SB Wheel (Combined)", pr, "")])
    if reg:
        alts.append([(f"DD- {reg}★ Reg card + Hammers Wheel", pr, "")])
    return alts


def dd_kind(lines: list[DDLine]) -> str:
    n = lines[0][0].lower()
    if "shiny limited" in n:
        return "shiny_limited"
    if "wild" in n and "card" in n:
        return "wild"
    if "shiny card" in n:
        return "shiny_card"
    if "gold card" in n:
        return "gold"
    if "ace card" in n:
        return "ace"
    if "reg card" in n:
        m = re.search(r"(\d)★", lines[0][0])
        return f"reg_{m.group(1) if m else 'x'}"
    if "combined" in n:
        return "sb_wheel_combo"
    if "100% sb" in n:
        return "sb_hammers"
    return n[:48]


def dd_broad_family(lines: list[DDLine]) -> str:
    n0 = (lines[0][0] or "").lower() if lines else ""
    if "sb wheel" in n0:
        return "sb_wheel"
    if "hammers wheel" in n0:
        return "hammers_wheel"
    k = dd_kind(lines)
    if k.startswith("reg_"):
        return "reg_wheel"
    return k


DD_SB_SLOT_RE = re.compile(r"sb wheel|100%\s*sb|slotobucks", re.I)
# Gameplay Core (coin-sink challenges) must not award Gold cards or any SB form (Nivi / core_mes_references).
GAMEPLAY_CORE_CHALLENGE_RE = re.compile(
    r"^(pyp|win master|ace heist|spinner clash|ace loot|loot —)|"
    r"spin zone —(?!.*hammers wheel)",
    re.I,
)
SHINY_SHOW_PROMO_RE = re.compile(r"shiny show", re.I)
SHINY_SHOW_MAX_PER_WEEK = 3
# Coin-sink Core (Shiny Show is gem-burn — must not replace daily wager challenge).
COIN_SINK_CHALLENGE_RE = re.compile(
    r"win master|ace heist|pyp|spinner clash|"
    r"spin zone —(?!.*hammers wheel)|"
    r"custom pod|ace loot|loot — 48h|"
    r"machine launch|mes — purchase",
    re.I,
)
PUZZLE_MES_ITEM_RE = re.compile(r"puzzle m\.e\.s", re.I)
# Calendar / Monday: one gameplay challenge per day (Shiny Show + Dash Day are separate surfaces).
CORE_GAMEPLAY_ANCHOR_RE = re.compile(
    r"dash pass|album —|status boost|betty's birthday|custom pod",
    re.I,
)


def is_puzzle_mes_item(item: dict) -> bool:
    return bool(PUZZLE_MES_ITEM_RE.search(item.get("name") or ""))


def is_gameplay_core_challenge(item: dict) -> bool:
    nm = item.get("name") or ""
    if (item.get("status") or "") != "Core":
        return False
    if SHINY_SHOW_PROMO_RE.search(nm):
        return False
    if CORE_GAMEPLAY_ANCHOR_RE.search(nm):
        return False
    if is_puzzle_mes_item(item):
        return True
    if COIN_SINK_CHALLENGE_RE.search(nm):
        return True
    if GAMEPLAY_CORE_CHALLENGE_RE.search(nm):
        return True
    return False


def count_gameplay_core_challenges(items: list[dict]) -> int:
    return sum(1 for i in items if is_gameplay_core_challenge(i))


def count_non_puzzle_gameplay_core(items: list[dict]) -> int:
    return sum(
        1 for i in items if is_gameplay_core_challenge(i) and not is_puzzle_mes_item(i)
    )


def can_add_gameplay_core_challenge(items: list[dict]) -> bool:
    if any(is_puzzle_mes_item(i) for i in items):
        return count_non_puzzle_gameplay_core(items) < 1
    return count_gameplay_core_challenges(items) < 1


def consolidate_paired_daily_deals(items: list[dict], d: int) -> None:
    """Once + multiple DD pair → single board row (companion SKU in description), except split days."""
    dd_idx = [i for i, it in enumerate(items) if it.get("status") == "Daily deal"]
    if len(dd_idx) != 2:
        return
    a, b = items[dd_idx[0]], items[dd_idx[1]]
    na, nb = (a.get("name") or "").lower(), (b.get("name") or "").lower()
    once_item, mult_item = None, None
    if "once" in na:
        once_item, mult_item = a, b
    elif "once" in nb:
        once_item, mult_item = b, a
    elif "wild" in na and "multiple" in nb:
        once_item, mult_item = a, b
    elif "wild" in nb and "multiple" in na:
        once_item, mult_item = b, a
    if not once_item or not mult_item:
        return
    if "shiny limited" in (once_item.get("name") or "").lower():
        if d in SHINY_LIMITED_SPLIT_DD_DAYS:
            return
        once_item["name"] = "DD - Shiny Limited - Once"
        once_item["desc"] = (
            (once_item.get("desc") or "")
            + f"\n\nCompanion repeatable DD (same day): {mult_item.get('name') or ''}."
        )
        items.remove(mult_item)
        return
    once_item["name"] = (once_item.get("name") or "").replace(" - Once", "") + " (Once + repeatable DD)"
    once_item["desc"] = (
        (once_item.get("desc") or "")
        + f"\n\nCompanion repeatable DD (same day): {mult_item.get('name') or ''}."
    )
    items.remove(mult_item)
GAMEPLAY_GOLD_PRIZE_RE = re.compile(r"\d\s*★\s*gold|gold card", re.I)
ACE_IN_PURCHASE_OFFER_RE = re.compile(
    r"\d\s*★\s*ace(?:\s+card)?|ace card \+|ace pack|ace card\+",
    re.I,
)
PURCHASE_OFFER_STATUSES = frozenset(
    {
        "Daily deal",
        "RYD",
        "Buy all",
        "Prize Mania",
        "Rolling offer",
        "MGAP",
        "Counter PO",
        "Offers & coin sale",
        "Popup Store",
        "Segmented test",
    }
)
DD_HAMMER_WHEEL_RE = re.compile(r"reg card \+ hammers wheel", re.I)
DD_WEEKLY_SB_CAP = 2
DD_WEEKLY_HAMMER_WHEEL_CAP = 2


def _offer_text_skips_ace_sale_check(name: str) -> bool:
    low = (name or "").lower()
    return any(
        x in low
        for x in (
            "ace heist",
            "ace loot",
            "crazy with aces",
            "pyp —",
            "pick your path",
        )
    )


def collect_mgap_days(days: list[dict]) -> list[int]:
    out: list[int] = []
    for day in days:
        if any((i.get("status") or "") == "MGAP" for i in day.get("items", [])):
            out.append(int(day["date"]))
    return sorted(out)


def mgap_days_in_week_slice(w: int, last_day: int = 31) -> int:
    return sum(1 for d in range(1, last_day + 1) if (d - 1) // 7 == w)


def required_mgap_count_for_week(w: int, last_day: int = 31) -> int:
    """Full month slice: 2 MGAP; partial tail slice (<4 days in month): 1."""
    if mgap_days_in_week_slice(w, last_day) < 4:
        return 1
    return MGAP_PER_WEEK


def mgap_week_counts(days: list[dict]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for day in days:
        if any((i.get("status") or "") == "MGAP" for i in day.get("items", [])):
            d = int(day["date"])
            w = (d - 1) // 7
            counts[w] = counts.get(w, 0) + 1
    return counts


def dd_week_index(d: int) -> int:
    return (d - 1) // 7


def dd_slotobucks_slots(lines: list[DDLine]) -> int:
    """One DD day with SB / SB Wheel / 100% SB counts as 1 (incl. Shiny Limited stack)."""
    return 1 if any(DD_SB_SLOT_RE.search(line[0]) for line in lines) else 0


def dd_hammer_wheel_slots(lines: list[DDLine]) -> int:
    """Reg card + Hammers Wheel on Daily Deal only."""
    return 1 if any(DD_HAMMER_WHEEL_RE.search(line[0]) for line in lines) else 0


_ALL_DD_KEYS = (
    "gold_as",
    "feat_pab_quest",
    "battlesheep_feats",
    "snl_shield_dice",
    "snl_quest_combo",
    "shiny_once",
    "shiny_mt",
    "reg_hw",
    "ace_sb",
    "sb8_h",
    "combo",
    "shiny_ltd",
    "wild_dd",
)

# Shiny Limited in Daily Deal — one slot per card-week (two in week 4); spread weekdays (not every Friday).
# Card-week 3: Shiny Limited only on BTS Prize Mania (22/8), not also in DD.
SHINY_LIMITED_DD_BY_CARD_WEEK: dict[int, tuple[int, ...]] = {
    1: (4,),       # Tue (cw1)
    2: (14,),      # Thu cw2 — 12/8 reserved for on-purchase DD (guidelines)
    3: (),         # reserved for BTS PM 22/8
    4: (26,),   # Wed — 30/8 reserved for DD BOGO (no Shiny Limited once-only)
}
BTS_SHINY_LIMITED_DAY = 22

# Once Shiny Limited + repeatable companion — separate Monday rows (not merged in desc).
SHINY_LIMITED_SPLIT_DD_DAYS = frozenset({4, 14})  # 14/8 Nostalgic sale Fri — user expects visible multiple DD

# Prefer premium cards in Daily Deal (not only Shiny Show) — day → DD template key.
DD_PREMIUM_CARD_DAYS: dict[int, str] = {
    20: "wild_dd",    # w3 — Wild Ord
    27: "wild_dd",    # w4 — Wild Gold
}
for _cw, _days in SHINY_LIMITED_DD_BY_CARD_WEEK.items():
    for _d in _days:
        if _d in DD_BOGO_DAYS or _d in DD_ON_PURCHASE_DAYS:
            continue
        DD_PREMIUM_CARD_DAYS[_d] = "shiny_ltd"

_PLANNED_DD_KEYS: dict[int, str] = {}


def set_planned_dd_keys(keys: dict[int, str]) -> None:
    global _PLANNED_DD_KEYS
    _PLANNED_DD_KEYS = dict(keys)


def wild_reserved_for_future_dd(d: int, dd_keys: dict[int, str] | None = None) -> bool:
    """Offers must not consume Wild before a later wild_dd in the same card week."""
    keys = dd_keys if dd_keys is not None else _PLANNED_DD_KEYS
    w = card_week(d)
    for dd, k in keys.items():
        if k == "wild_dd" and card_week(dd) == w and dd > d:
            return True
    return False


def _dd_key_materialized(key: str, lines: list[DDLine]) -> bool:
    kind = dd_kind(lines)
    if key == "wild_dd":
        return kind == "wild"
    if key == "shiny_ltd":
        return kind == "shiny_limited"
    if key == "shiny_once":
        return kind == "shiny_card"
    return True


def _dd_sb_cap_for_day(d: int, key: str) -> int:
    return DD_WEEKLY_SB_CAP


def effective_sb_week_cap(w: int, d: int) -> int:
    """Reserve 1 SB slot in the week for a planned Shiny Limited DD stack (once + 100% SB multiple)."""
    shiny_in_week = [
        x
        for x in range(1, 32)
        if DD_PREMIUM_CARD_DAYS.get(x) == "shiny_ltd" and dd_week_index(x) == w
    ]
    if not shiny_in_week:
        return DD_WEEKLY_SB_CAP
    if d < min(shiny_in_week):
        return DD_WEEKLY_SB_CAP - 1
    return DD_WEEKLY_SB_CAP


def _dd_key_fits_week_caps(
    key: str,
    d: int,
    sale: bool,
    sb_used: dict[int, int],
    hw_used: dict[int, int],
) -> bool:
    w = dd_week_index(d)
    lines = dd_lines_from_key(key, d, sale)
    sb = dd_slotobucks_slots(lines)
    hw = dd_hammer_wheel_slots(lines)
    if sb_used.get(w, 0) + sb > DD_WEEKLY_SB_CAP:
        return False
    if hw_used.get(w, 0) + hw > DD_WEEKLY_HAMMER_WHEEL_CAP:
        return False
    return True


def dd_lines_from_key(key: str, d: int, sale: bool) -> list[DDLine]:
    pr = _dd_pricing(sale)
    feat = dd_feature_sku_lines(key, d, sale)
    if feat:
        return feat
    reg, ace, gold = stars_reg(d), stars_ace(d), stars_gold(d)
    mt = mid_term_booster(d)
    if key == "shiny_ltd":
        return [
            ("DD - Shiny Limited - Once", pr, "Once + multiple below"),
            (DD_REPEATABLE_SB_HAMMERS_NAME, "High", DD_REPEATABLE_SB_HAMMERS_DESC),
        ]
    if key == "wild_dd":
        return [(dd_on_purchase_line("Wild", d), pr, "Wild — weekly bank")]
    if key == "reg_hw":
        return [(f"DD- {reg}★ Reg card + Hammers Wheel", pr, "")]
    if key == "ace_sb":
        return [(f"DD- {reg}★ Reg card + SB Wheel", pr, "")]
    if key == "gold_as":
        g = gold or 3
        return [(dd_on_purchase_line(f"{g}★ Gold", d), pr, "")]
    if key == "shiny_once":
        return [("DD- Shiny Card (multiple)", pr, "Album bank")]
    if key == "shiny_mt":
        return [(f"DD- Shiny Card + {mt} (multiple)", pr, f"Mid-term: {mt}")]
    if key == "sb8_h":
        return [("DD- 100% SB + 8 Hammers", pr, "")]
    if key == "combo":
        return [("DD- Cards & SB Wheel (Combined)", pr, "")]
    return dd_lines_from_key("reg_hw", d, sale)


# Curated DD — משפחות מתחלפות (Gold / Ace / Reg+HW / Shiny) + caps ב-assign.
DAILY_DEAL_KEYS: dict[int, str] = {
    1: "reg_hw",
    2: "feat_pab_quest",
    3: "shiny_once",
    4: "gold_as",
    5: "ace_sb",
    6: "reg_hw",
    7: "battlesheep_feats",
    8: "ace_sb",
    9: "reg_hw",      # DD BOGO day 1/2 (Betty weekend — gem-drain anchor)
    10: "ace_sb",
    11: "reg_hw",     # GGS + Price Cut (Popup moved to 12)
    12: "snl_shield_dice",    # Popup Store soft launch 1/3 + on-purchase DD (see DD_ON_PURCHASE_DAYS)
    13: "gold_as",
    14: "ace_sb",
    15: "snl_quest_combo",
    16: "reg_hw",
    17: "reg_hw",
    18: "reg_hw",
    19: "gold_as",
    20: "wild_dd",     # Wild Ord in DD (w3)
    21: "ace_sb",       # w3 — Shiny Limited only on BTS PM (22)
    22: "shiny_once",  # BTS flagship
    23: "reg_hw",
    24: "reg_hw",
    25: "gold_as",      # MS3 open — Shiny Limited DD on 26
    26: "shiny_ltd",   # Shiny Limited in DD (w4)
    27: "wild_dd",     # Wild Gold in DD (w4)
    28: "reg_hw",
    29: "gold_as",
    30: "reg_hw",   # DD BOGO 2/2 — hammers/reg (not Shiny Limited once-only)
    31: "gold_as",
}

# Fallback order — ace_sb (SB Wheel +15% lift) and shiny keys before reg_hw / gold_as.
# This is the tiebreak when the preferred DAILY_DEAL_KEYS key isn't available on a given day.
_DD_FALLBACK_ROTATION = (
    "ace_sb",      # SB Wheel — highest revenue lift of DD prize types
    "shiny_once",  # Shiny Card — strong engagement anchor
    "shiny_mt",    # Shiny Card + Mid-term booster combo
    "gold_as",     # Gold + season SKU (AS only on Battlesheep; Blast → Superboom/PAB/Picks)
    "reg_hw",      # Reg + Hammer Wheel — lower lift, use as last resort
    "sb8_h",       # Pure SB + Hammers (no card)
    "combo",
)


def shiny_limited_reserved_in_card_week(cw: int, on_or_before_day: int) -> int:
    """Shiny Limited already allocated later in the same card week (BTS PM)."""
    if cw == 3 and on_or_before_day < BTS_SHINY_LIMITED_DAY:
        return 1
    return 0


def dd_lines_allow_bogo(dd_lines: list[DDLine]) -> bool:
    """BOGO = buy-one-get-one on repeatable DD — not for Once Wild / Shiny Limited."""
    for name, _, _ in dd_lines:
        nl = (name or "").lower()
        if "shiny limited" in nl:
            return False
        if "wild" in nl and ("once" in nl or "on purchase" in nl):
            return False
    return True


def dd_key_allows_bogo(key: str) -> bool:
    return key in DD_BOGO_ELIGIBLE_DD_KEYS


def shiny_limited_dd_blocked(key: str, d: int, ledger: CardLedger) -> bool:
    if key != "shiny_ltd":
        return False
    cw = card_week(d)
    cap = CARD_BUDGETS[cw].get("Shiny Limited", 0)
    used = ledger.used[cw].get("Shiny Limited", 0)
    reserved = shiny_limited_reserved_in_card_week(cw, d)
    return used + reserved >= cap


def count_shiny_limited_surfaces(day_items: list[dict]) -> int:
    return sum(
        1
        for i in day_items
        if re.search(r"shiny limited", (i.get("name") or ""), re.I)
    )


def assign_daily_deal_keys() -> dict[int, str]:
    """Pick DD template per day (ledger + SB / Hammer Wheel weekly caps on materialized DD)."""
    keys_out: dict[int, str] = {}
    prev_fam: str | None = None
    sb_used: dict[int, int] = {}
    hw_used: dict[int, int] = {}
    ledger = CardLedger()
    # Pre-consume Shiny Cards for SHINY_MS2_COUNTDOWN_LAST days so the planner
    # doesn't assign shiny_once to another day in the same card_week.
    # build_day will consume the Shiny Card via add_core_challenge(shiny_card_prize=True)
    # on these days, leaving none for a coincident shiny_once DD.
    # Reserve one Shiny Card in card_week 3 for MS2 countdown (23–24); d22 BTS DD keeps its own Shiny.
    ledger.take(23, "Shiny Card")
    for d in range(1, 32):
        sale = is_sale(d)
        w = dd_week_index(d)
        ledger_at_day_start = copy.deepcopy(ledger)
        if d in DD_ON_PURCHASE_DAYS:
            chosen_key = DAILY_DEAL_KEYS.get(d, "gold_as")
            trial_ledger = copy.deepcopy(ledger)
            trial_lines = trial_ledger.build_dd_lines(d, chosen_key, sale)
            ledger = trial_ledger
            sb_used[w] = sb_used.get(w, 0) + dd_slotobucks_slots(trial_lines)
            hw_used[w] = hw_used.get(w, 0) + dd_hammer_wheel_slots(trial_lines)
            keys_out[d] = chosen_key
            prev_fam = dd_broad_family(trial_lines)
            continue
        if (
            DD_PREMIUM_CARD_DAYS.get(d) == "shiny_ltd"
            and not shiny_limited_dd_blocked("shiny_ltd", d, ledger)
        ):
            chosen_key = "shiny_ltd"
            trial_ledger = copy.deepcopy(ledger)
            trial_lines = trial_ledger.build_dd_lines(d, chosen_key, sale)
            if _dd_key_materialized(chosen_key, trial_lines):
                ledger = trial_ledger
                sb_used[w] = sb_used.get(w, 0) + dd_slotobucks_slots(trial_lines)
                hw_used[w] = hw_used.get(w, 0) + dd_hammer_wheel_slots(trial_lines)
                keys_out[d] = chosen_key
                prev_fam = dd_broad_family(trial_lines)
                continue
        preferred = DD_PREMIUM_CARD_DAYS.get(d, DAILY_DEAL_KEYS.get(d, "gold_as"))
        candidates: list[str] = [preferred]
        for k in _DD_FALLBACK_ROTATION:
            if k not in candidates:
                candidates.append(k)
        for k in _ALL_DD_KEYS:
            if k not in candidates:
                candidates.append(k)

        chosen_key = preferred
        if d in DD_BOGO_DAYS:
            if not dd_key_allows_bogo(chosen_key):
                chosen_key = next((k for k in candidates if dd_key_allows_bogo(k)), "reg_hw")
            candidates = [k for k in candidates if dd_key_allows_bogo(k)] or list(candidates)
        trial_lines: list[DDLine] | None = None
        adopted_ledger: CardLedger | None = None
        for key in candidates:
            if time_limited_prize_is_shiny_card(d) and key in ("shiny_once", "shiny_mt", "shiny_ltd"):
                continue
            if shiny_limited_dd_blocked(key, d, ledger):
                continue
            trial_ledger = copy.deepcopy(ledger)
            trial = trial_ledger.build_dd_lines(d, key, sale)
            if key in ("wild_dd", "shiny_ltd") and not _dd_key_materialized(key, trial):
                continue
            sb = dd_slotobucks_slots(trial)
            hw = dd_hammer_wheel_slots(trial)
            sb_cap = effective_sb_week_cap(w, d)
            if sb_used.get(w, 0) + sb > sb_cap:
                continue
            if hw_used.get(w, 0) + hw > DD_WEEKLY_HAMMER_WHEEL_CAP:
                continue
            if prev_fam and dd_broad_family(trial) == prev_fam:
                continue
            chosen_key = key
            trial_lines = trial
            adopted_ledger = trial_ledger
            break
        if trial_lines is None:
            for key in candidates:
                if time_limited_prize_is_shiny_card(d) and key in ("shiny_once", "shiny_mt", "shiny_ltd"):
                    continue
                if shiny_limited_dd_blocked(key, d, ledger):
                    continue
                trial_ledger = copy.deepcopy(ledger)
                trial = trial_ledger.build_dd_lines(d, key, sale)
                if key in ("wild_dd", "shiny_ltd") and not _dd_key_materialized(key, trial):
                    continue
                sb = dd_slotobucks_slots(trial)
                hw = dd_hammer_wheel_slots(trial)
                sb_cap = effective_sb_week_cap(w, d)
                if sb_used.get(w, 0) + sb > sb_cap:
                    continue
                if hw_used.get(w, 0) + hw > DD_WEEKLY_HAMMER_WHEEL_CAP:
                    continue
                if prev_fam and dd_broad_family(trial) == prev_fam:
                    continue
                chosen_key = key
                trial_lines = trial
                adopted_ledger = trial_ledger
                break
        if trial_lines is None:
            for key in candidates:
                if time_limited_prize_is_shiny_card(d) and key in ("shiny_once", "shiny_mt", "shiny_ltd"):
                    continue
                if prev_fam == "gold" and key == "gold_as":
                    continue
                if shiny_limited_dd_blocked(key, d, ledger):
                    continue
                trial_ledger = copy.deepcopy(ledger)
                trial = trial_ledger.build_dd_lines(d, key, sale)
                if key in ("wild_dd", "shiny_ltd") and not _dd_key_materialized(key, trial):
                    continue
                sb = dd_slotobucks_slots(trial)
                hw = dd_hammer_wheel_slots(trial)
                sb_cap = effective_sb_week_cap(w, d)
                if sb_used.get(w, 0) + sb > sb_cap:
                    continue
                if hw_used.get(w, 0) + hw > DD_WEEKLY_HAMMER_WHEEL_CAP:
                    continue
                chosen_key = key
                trial_lines = trial
                adopted_ledger = trial_ledger
                break
        if trial_lines is None:
            chosen_key = "gold_as"
            trial_lines = ledger.build_dd_lines(d, chosen_key, sale)
            adopted_ledger = ledger
        else:
            ledger = adopted_ledger  # type: ignore[assignment]

        if d in DD_PREMIUM_CARD_DAYS:
            pk = DD_PREMIUM_CARD_DAYS[d]
            premium_ok = pk in ("shiny_ltd", "wild_dd") or dd_key_allows_bogo(pk)
            if (
                d not in DD_BOGO_DAYS
                and d not in DD_ON_PURCHASE_DAYS
                and premium_ok
                and not (pk == "shiny_ltd" and shiny_limited_dd_blocked(pk, d, ledger_at_day_start))
            ):
                prem_ledger = copy.deepcopy(ledger_at_day_start)
                plines = prem_ledger.build_dd_lines(d, pk, sale)
                if _dd_key_materialized(pk, plines):
                    sb = dd_slotobucks_slots(plines)
                    hw = dd_hammer_wheel_slots(plines)
                    sb_cap = effective_sb_week_cap(w, d)
                    if sb_used.get(w, 0) + sb <= sb_cap and hw_used.get(w, 0) + hw <= DD_WEEKLY_HAMMER_WHEEL_CAP:
                        chosen_key = pk
                        trial_lines = plines
                        ledger = prem_ledger

        if time_limited_prize_is_shiny_card(d) and chosen_key in ("shiny_once", "shiny_mt", "shiny_ltd"):
            for fk in TLP_SHINY_DD_FALLBACK_KEYS:
                if shiny_limited_dd_blocked(fk, d, ledger_at_day_start):
                    continue
                fix_ledger = copy.deepcopy(ledger_at_day_start)
                fix_lines = fix_ledger.build_dd_lines(d, fk, sale)
                sb = dd_slotobucks_slots(fix_lines)
                hw = dd_hammer_wheel_slots(fix_lines)
                sb_cap = effective_sb_week_cap(w, d)
                if sb_used.get(w, 0) + sb > sb_cap:
                    continue
                if hw_used.get(w, 0) + hw > DD_WEEKLY_HAMMER_WHEEL_CAP:
                    continue
                chosen_key = fk
                trial_lines = fix_lines
                ledger = fix_ledger
                break

        sb_used[w] = sb_used.get(w, 0) + dd_slotobucks_slots(trial_lines)
        hw_used[w] = hw_used.get(w, 0) + dd_hammer_wheel_slots(trial_lines)
        keys_out[d] = chosen_key
        prev_fam = dd_broad_family(trial_lines)
    return keys_out


def has_real_core_challenge(items: list[dict]) -> bool:
    return count_gameplay_core_challenges(items) > 0


def has_coin_sink_challenge(items: list[dict]) -> bool:
    """Daily wager/coin-sink challenge — not Piggy/Dash/Shiny Show alone."""
    for i in items:
        nm = i.get("name") or ""
        if COIN_SINK_CHALLENGE_RE.search(nm):
            return True
        if re.search(r"hoppin.*spin zone", nm, re.I):
            return True
        if re.search(r"hammers wheel", nm, re.I):
            return True
    return False


def is_puzzle_control_core(item: dict) -> bool:
    """Standard coin-sink Core for the ~80% cohort (not Puzzle test, not machine marketing rows)."""
    if is_puzzle_mes_item(item):
        return False
    nm = (item.get("name") or "").lower()
    if "sneak peek" in nm or "machine launch" in nm:
        return False
    if COIN_SINK_CHALLENGE_RE.search(item.get("name") or ""):
        return True
    return is_gameplay_core_challenge(item) and GAMEPLAY_CORE_CHALLENGE_RE.search(nm) is not None


def has_parallel_control_gameplay(items: list[dict]) -> bool:
    """Gameplay Core for non–Puzzle M.E.S cohort (PYP / Win Master / Spinner / Machine Launch day)."""
    for i in items:
        if is_puzzle_control_core(i):
            return True
        nm = (i.get("name") or "").lower()
        if "machine launch" in nm:
            return True
    return False


def day_has_shiny_show_promo(items: list[dict]) -> bool:
    return any(SHINY_SHOW_PROMO_RE.search(i.get("name") or "") for i in items)


def _popup_store_offer_pool_label(kind: str) -> str:
    if kind in ("Rolling", "Rolling Offer"):
        return "Rolling"
    if kind == "Mystery Buy All":
        return "Mystery Buy All"
    return kind


def prev_assigned_secondary_label(picks: dict[int, str | None], before_d: int) -> str | None:
    """Last secondary-offer type before day `before_d` (includes test/popup/rolling anchors)."""
    for dd in range(before_d - 1, 0, -1):
        if dd in ROLLING_MFL:
            return "Rolling"
        if dd in POPUP_STORE_DAYS:
            return _popup_store_offer_pool_label(POPUP_STORE_INNER_OFFER.get(dd, "Buy All"))
        p = picks.get(dd)
        if p:
            return p
    return None


def secondary_label_from_day_items(day_items: list[dict], d: int) -> str | None:
    if d in ROLLING_MFL:
        return "Rolling"
    for i in day_items:
        if i.get("backup"):
            continue
        if is_secondary_offer(i):
            nm = (i.get("name") or "").lower()
            st = i.get("status") or ""
            if st == "RYD" or nm.startswith("ryd"):
                return "RYD"
            if "rolling offer" in nm or st == "Rolling offer":
                return "Rolling"
            if "mystery buy all" in nm:
                return "Mystery Buy All"
            if "buy all" in nm:
                return "Buy All"
            if "decoy" in nm or "bonanza" in nm:
                return "Decoy Bonanza"
            if st == "Prize Mania" or "prize mania" in nm:
                return "Prize Mania"
    if d in POPUP_STORE_DAYS:
        if d in POPUP_STORE_LAUNCH_SHELL_ONLY:
            return None
        return _popup_store_offer_pool_label(POPUP_STORE_INNER_OFFER.get(d, "Buy All"))
    return None


def items_have_shiny_card_source(items: list[dict]) -> bool:
    return any(re.search(r"shiny card", i.get("name") or "", re.I) for i in items)


def is_popup_store_item(item: dict) -> bool:
    """Popup Store product line — not the inner RYD / Buy All / Decoy offer."""
    return (item.get("status") or "").lower() == "popup store"


def popup_store_shell_name(d: int) -> str:
    tag, label = POPUP_STORE_PHASE_BY_DAY[d]
    ordered = sorted(POPUP_STORE_DAYS)
    n = ordered.index(d) + 1
    total = len(ordered)
    return f"Popup Store — {tag} · {label} ({n}/{total})"


def puzzle_mes_item_name(d: int) -> str:
    n = d - min(PUZZLE_MES_TEST) + 1
    return f"Puzzle M.E.S — Soft Launch 20% · day {n}/{PUZZLE_MES_DAY_COUNT}"


def puzzle_mes_test_description(d: int) -> str:
    n = d - min(PUZZLE_MES_TEST) + 1
    return (
        f"Puzzle day {n} of {PUZZLE_MES_DAY_COUNT} · {PUZZLE_MES_PHASE} · ~{PUZZLE_MES_COHORT_PCT}% cohort.\n"
        f"Core — Puzzle M.E.S gameplay · window 18–24/8 ({d}/8 · {dow(d)}).\n"
        "Separate from Popup Store (12/19/26). Control segment keeps the day's Core challenge."
    )


def popup_store_shell_description(d: int) -> str:
    tag, label = POPUP_STORE_PHASE_BY_DAY[d]
    return (
        f"Product: Popup Store · {tag} · {label} (12 / 19 / 26/8 only).\n"
        "Separate from Puzzle M.E.S (Core 18–24/8). Surfaces the paired purchase offer for the off-test cohort."
    )


def popup_inner_offer_matches_kind(item: dict, kind: str) -> bool:
    st = item.get("status") or ""
    nm = (item.get("name") or "").lower()
    if is_popup_store_item(item):
        return False
    if kind == "RYD":
        return st == "RYD"
    if kind == "Buy All":
        return st == "Buy all" and nm.startswith("buy all")
    if kind == "Mystery Buy All":
        return st == "Buy all" and "mystery buy all" in nm
    if kind == "Decoy Bonanza":
        return st == "Offers & coin sale" and "decoy bonanza" in nm and "triple offer" not in nm
    if kind == "Rolling Offer":
        return st == "Rolling offer"
    return False


def build_popup_store_inner_offer(
    d: int,
    kind: str,
    reg: int,
    ace: int,
    gold: int,
    ledger: CardLedger | None,
    *,
    on_extreme: bool,
    offer_pricing_tier: str | None = None,
) -> tuple[str, str, str, str]:
    """Returns (name, status, pricing, description) — same labels as standalone offers."""
    pr = "High"
    cohort = "Cohort: Popup Store off-test segment (via Popup Store shell).\n"
    if kind == "RYD":
        if on_extreme:
            name = f"RYD — {reg}★ Reg + 100% SB"
            desc = cohort + "No Wild — Extreme Stamp day"
        else:
            hook = ryd_card_hook(d, reg, ace, gold, ledger)
            name = f"RYD — {hook}"
            desc = cohort + "Reveal Your Deal"
        return name, "RYD", pr, desc
    if kind == "Buy All":
        name, body = buy_all_item(d, reg, ace, gold, pr, ledger)
        return name, "Buy all", pr, cohort + body
    if kind == "Mystery Buy All":
        name, body = mystery_buy_all_item(d, reg, ace, gold, pr, ledger)
        return name, "Buy all", pr, cohort + body
    if kind == "Decoy Bonanza":
        top = pick_paired_decoy_top(d, reg, ace, gold, ledger, allow_wild=not on_extreme)
        name, body = decoy_bonanza_item(d, top)
        return name, "Offers & coin sale", pr, cohort + body
    if kind == "Rolling Offer":
        cycles = 2
        pr = offer_pricing_tier or "High"
        return (
            rolling_bxgy_name(d, cycles),
            "Rolling offer",
            pr,
            cohort + rolling_bxgy_desc(d, cycles),
        )
    return kind, "Offers & coin sale", pr, cohort + kind


def pyp_finish_prize(d: int, ledger: CardLedger | None) -> str:
    """Rotate Reg/Ace and tier so adjacent PYP days (e.g. same week) do not repeat the same title prize."""
    week = (d - 1) // 7
    mode = (d + week) % 4
    if mode == 0:
        rk = ledger.pick_reg(d, prefer_high=False) if ledger else None
        return (
            f"{card_key_to_label(rk)} card"
            if rk
            else f"{stars_reg(d)}★ Reg card"
        )
    if mode == 1:
        ak = ledger.pick_ace(d, prefer_high=False) if ledger else None
        return (
            f"{card_key_to_label(ak)} card"
            if ak
            else f"{stars_ace(d)}★ Ace card"
        )
    if mode == 2:
        rk = ledger.pick_reg(d, prefer_high=True) if ledger else None
        return (
            f"{card_key_to_label(rk)} card"
            if rk
            else f"{min(5, stars_reg(d) + 1)}★ Reg card"
        )
    ak = ledger.pick_ace(d, prefer_high=True) if ledger else None
    return (
        f"{card_key_to_label(ak)} card"
        if ak
        else f"{min(5, stars_ace(d) + 1)}★ Ace card"
    )


def assign_core_challenge_kinds() -> dict[int, str]:
    """Spread coin-sink challenges; rotate by weekday so the same DOW is not always the same mechanic."""
    skip = set(MACHINE_SNEAK) | MACHINE_LAUNCH | {8}
    pool = ("win_master", "pyp", "ace_heist", "mes", "spin_zone")
    out: dict[int, str] = {}
    for d in SHINY_MS2_COUNTDOWN_LAST:
        out[d] = "shiny_ms2"
    by_dow: dict[str, list[int]] = {w: [] for w in WEEKDAYS}
    for d in range(1, 32):
        if d in skip or d in SHINY_MS2_COUNTDOWN_LAST:
            continue
        by_dow[dow(d)].append(d)
    for dow_name, day_list in by_dow.items():
        day_list.sort()
        offset = WEEKDAYS.index(dow_name)
        last: str | None = None
        for i, d in enumerate(day_list):
            kind = pool[(offset + i) % len(pool)]
            if kind == last:
                kind = pool[(offset + i + 1) % len(pool)]
            out[d] = kind
            last = kind
    for d in SPINNER_CLASH_DAYS:
        if d not in skip and d not in SHINY_MS2_COUNTDOWN_LAST:
            out[d] = "spinner"
    for d, kind in list(out.items()):
        if kind == "spinner" and d not in SPINNER_CLASH_DAYS:
            out[d] = "win_master"
    for d in FORCE_CORE_CHALLENGE_DAYS:
        if d in skip:
            continue
        if out.get(d) in (None, "shiny_ms2"):
            out[d] = "win_master"
    out[6] = "spin_zone"  # keep 4★ Ace Spin Zone headline (card-bank pass)
    return out


def is_segmented_decoy_test_item(item: dict) -> bool:
    return (item.get("status") or "") == "Segmented test"


def is_triple_offer_item(item: dict) -> bool:
    """Segmented Decoy test cohort line (never use Triple Offer branding)."""
    return is_segmented_decoy_test_item(item)


def is_secondary_offer(item: dict) -> bool:
    """Second offer alongside Daily Deal — not purchase promos (Price Cut, Coin Sale, MGAP, …)."""
    if item.get("status") == "Daily deal":
        return False
    if is_segmented_decoy_test_item(item):
        return False
    if is_popup_store_item(item):
        return False
    st = item.get("status") or ""
    nm = (item.get("name") or "").lower()
    if st in ("RYD", "Buy all", "Prize Mania", "Rolling offer"):
        return True
    if st == "Offers & coin sale" and "decoy bonanza" in nm:
        return True
    if is_popup_store_paired_offer(item):
        return True
    return False


def is_primary_purchase_offer(item: dict) -> bool:
    """Alias — use is_secondary_offer for DD + second-offer rules."""
    return is_secondary_offer(item)


def is_popup_store_paired_offer(item: dict) -> bool:
    """Purchase offer surfaced only to non–test cohort via Popup Store (12/19/26)."""
    return "via popup store" in (item.get("desc") or "").lower()


def item_name_mentions_popup_store(item: dict) -> bool:
    return "popup store" in (item.get("name") or "").lower()


def popup_shell_has_agreed_label(name: str) -> bool:
    """Shell rows must say TEST or LAUNCH — never a generic Popup Store line."""
    n = (name or "").upper()
    return "TEST" in n or "LAUNCH" in n


def counts_toward_vfm_cap(item: dict) -> bool:
    """At most one secondary offer / day (except BTS) — purchase promos excluded."""
    if is_popup_store_paired_offer(item):
        return False
    return is_secondary_offer(item) and not is_popup_store_item(item)


def validate_august_plan(days: list[dict]) -> list[tuple[str, str, str]]:
    """Returns rows: (rule, status emoji, detail)."""
    rows: list[tuple[str, str, str]] = []

    def items(d: int):
        return days[d - 1]["items"]

    # Consecutive DD broad family
    prev_dd = None
    dd_dups = []
    for d in range(1, 32):
        dd_names = [i["name"] for i in items(d) if i["status"] == "Daily deal"]
        fam = dd_broad_family([(dd_names[0], "", "")]) if dd_names else None
        if prev_dd and fam == prev_dd:
            dd_dups.append(f"{d - 1}/{d}")
        prev_dd = fam
    rows.append(
        (
            "DD — ללא אותו משפחה ביומיים רצופים",
            "✓" if not dd_dups else "✗",
            "OK" if not dd_dups else ", ".join(dd_dups),
        )
    )

    blast_as_bad: list[str] = []
    for d in range(1, 32):
        if "blast" not in short_term(d).lower():
            continue
        for i in items(d):
            if i.get("status") != "Daily deal":
                continue
            if re.search(r"\+\s*AS\b", i.get("name") or ""):
                blast_as_bad.append(str(d))
    rows.append(
        (
            "DD — אין Airstrike (AS) בימי Blast",
            "✓" if not blast_as_bad else "✗",
            "OK" if not blast_as_bad else ",".join(blast_as_bad),
        )
    )

    vfm_violations = []
    vfm_missing: list[str] = []
    for d in range(1, 32):
        main_vfm = sum(1 for i in items(d) if counts_toward_vfm_cap(i))
        allowed = 2 if d == 22 else 1
        if d in COUNTER_PO:
            allowed = 1  # Counter PO day — no second VFM from planner
        if main_vfm > allowed:
            vfm_violations.append(str(d))
        if main_vfm < 1 and d != 22:
            vfm_missing.append(str(d))
    rows.append(
        (
            "VFM עיקרי ≤1/יום (חריג 22/8 BTS)",
            "✓" if not vfm_violations else "✗",
            "OK" if not vfm_violations else ",".join(vfm_violations),
        )
    )
    rows.append(
        (
            "הצעה שנייה (VFM) — לפחות אחת בכל יום (לא Dash)",
            "✓" if not vfm_missing else "✗",
            "OK" if not vfm_missing else ",".join(vfm_missing),
        )
    )

    two_offer_bad: list[str] = []
    for d in range(1, 32):
        day_items = items(d)
        has_dd = any(i.get("status") == "Daily deal" for i in day_items)
        primaries = [i for i in day_items if is_primary_purchase_offer(i)]
        if d == 22:
            if not has_dd or len(primaries) < 1:
                two_offer_bad.append(str(d))
            continue
        if d in POPUP_STORE_LAUNCH_SHELL_ONLY:
            if not has_dd:
                two_offer_bad.append(str(d))
            continue
        if dow(d) == "Mon":
            if not has_dd:
                two_offer_bad.append(str(d))
            continue
        if not has_dd or len(primaries) < 1:
            two_offer_bad.append(str(d))
    mgap_no_main: list[str] = []
    for d in range(1, 32):
        day_items = items(d)
        if not any((i.get("status") or "") == "MGAP" for i in day_items):
            continue
        if d in POPUP_STORE_LAUNCH_SHELL_ONLY:
            continue
        if sum(1 for i in day_items if is_primary_purchase_offer(i)) < 1:
            mgap_no_main.append(str(d))
    rows.append(
        (
            "DD + הצעה שנייה (לא פרומו רכישה)",
            "✓" if not two_offer_bad else "✗",
            "OK" if not two_offer_bad else ",".join(two_offer_bad),
        )
    )
    rows.append(
        (
            "MGAP — בנוסף ל-DD + הצעה שנייה (פרומו רכישה, לא מחליף אופר)",
            "✓" if not mgap_no_main else "✗",
            "OK" if not mgap_no_main else ",".join(mgap_no_main),
        )
    )

    triple_days = sorted(POPUP_STORE_DAYS)
    triple_missing_main = [
        str(d)
        for d in triple_days
        if d not in POPUP_STORE_LAUNCH_SHELL_ONLY
        and sum(1 for i in items(d) if is_secondary_offer(i)) < 1
    ]
    rows.append(
        (
            "Popup Store — control Decoy + הצעה שנייה (ימים 12/19/26)",
            "✓" if not triple_missing_main else "✗",
            "OK" if not triple_missing_main else ",".join(triple_missing_main),
        )
    )

    puzzle_popup_bad: list[str] = []
    popup_outside: list[str] = []
    for day in days:
        d = int(day["date"])
        for i in day.get("items", []):
            if d not in POPUP_STORE_DAYS:
                if is_popup_store_item(i):
                    popup_outside.append(str(d))
                elif is_popup_store_paired_offer(i):
                    popup_outside.append(f"{d}:paired")
                elif item_name_mentions_popup_store(i):
                    popup_outside.append(f"{d}:name")
    for d in POPUP_STORE_DAYS:
        day_items = items(d)
        pop = [i for i in day_items if is_popup_store_item(i)]
        if d in POPUP_STORE_LAUNCH_SHELL_ONLY:
            if len(pop) != 1:
                puzzle_popup_bad.append(f"{d}:shell")
            elif not popup_shell_has_agreed_label(pop[0].get("name") or ""):
                puzzle_popup_bad.append(f"{d}:label")
            continue
        kind = POPUP_STORE_INNER_OFFER.get(d) or ""
        if kind not in POPUP_STORE_OFFER_KINDS:
            puzzle_popup_bad.append(f"{d}:kind")
        elif len(pop) != 1:
            puzzle_popup_bad.append(f"{d}:shell")
        elif not popup_shell_has_agreed_label(pop[0].get("name") or ""):
            puzzle_popup_bad.append(f"{d}:label")
        elif not any(popup_inner_offer_matches_kind(i, kind) for i in day_items):
            puzzle_popup_bad.append(f"{d}:inner")
    rows.append(
        (
            "Popup Store — רק 12/19/26 (TEST/LAUNCH בשם)",
            "✓" if not puzzle_popup_bad and not popup_outside else "✗",
            "OK" if not puzzle_popup_bad and not popup_outside else ",".join(puzzle_popup_bad + popup_outside),
        )
    )
    puzzle_control_bad: list[str] = []
    for d in PUZZLE_MES_TEST:
        if not any(is_puzzle_mes_item(i) for i in items(d)):
            puzzle_control_bad.append(f"{d}:missing_puzzle")
        elif not has_parallel_control_gameplay(items(d)):
            puzzle_control_bad.append(f"{d}:missing_control")
    rows.append(
        (
            f"Puzzle M.E.S — 18–24/8 + Core לקונטרול (~{100 - PUZZLE_MES_COHORT_PCT}%)",
            "✓" if not puzzle_control_bad else "✗",
            "OK" if not puzzle_control_bad else ",".join(puzzle_control_bad),
        )
    )

    seg_sku_bad: list[str] = []
    for d in POPUP_STORE_DAYS:
        if d in POPUP_STORE_LAUNCH_SHELL_ONLY:
            continue
        kind = POPUP_STORE_INNER_OFFER.get(d) or ""
        if kind != "Decoy Bonanza":
            continue
        ctrls = [
            i
            for i in items(d)
            if i.get("status") == "Offers & coin sale"
            and "decoy bonanza" in (i.get("name") or "").lower()
            and not is_popup_store_paired_offer(i)
        ]
        inners = [
            i
            for i in items(d)
            if is_popup_store_paired_offer(i) and "decoy bonanza" in (i.get("name") or "").lower()
        ]
        if not ctrls or not inners:
            seg_sku_bad.append(f"{d}:missing")
            continue
        fp_ctrl = decoy_bundle_fingerprint(ctrls[0].get("desc") or "")
        fp_inner = decoy_bundle_fingerprint(inners[0].get("desc") or "")
        if fp_ctrl != fp_inner:
            seg_sku_bad.append(str(d))
    rows.append(
        (
            "Popup Store — control Decoy ו-inner offer עם אותם SKUs",
            "✓" if not seg_sku_bad else "✗",
            "OK" if not seg_sku_bad else ",".join(seg_sku_bad),
        )
    )

    spinner_by_biweek: dict[int, list[int]] = {}
    for d in range(1, 32):
        if any(re.search(r"spinner clash", i.get("name") or "", re.I) for i in items(d)):
            b = spinner_biweek_index(d)
            spinner_by_biweek.setdefault(b, []).append(d)
    spinner_over = {
        b: ds for b, ds in spinner_by_biweek.items() if len(ds) > SPINNER_CLASH_MAX_PER_BIWEEK
    }
    expected_biweeks = set(range(spinner_biweek_count()))
    spinner_missing = sorted(expected_biweeks - set(spinner_by_biweek.keys()))
    spinner_detail = "OK"
    if spinner_over:
        spinner_detail = "; ".join(
            f"biweek {b}: {','.join(str(x) for x in ds)}" for b, ds in sorted(spinner_over.items())
        )
    elif spinner_missing:
        spinner_detail = "חסר biweek: " + ",".join(str(b) for b in spinner_missing)
    rows.append(
        (
            f"Spinner Clash — בדיוק 1×/שבועיים ISO (ימים {sorted(SPINNER_CLASH_DAYS)})",
            "✓" if not spinner_over and not spinner_missing else "✗",
            spinner_detail,
        )
    )

    wild_hits = []
    for d in range(1, 32):
        for i in items(d):
            if re.search(r"wild\s+(any|supreme)", i["name"], re.I):
                wild_hits.append(str(d))
    rows.append(("ללא Wild בהצעות (אוגוסט)", "✓" if not wild_hits else "✗", "OK" if not wild_hits else ",".join(wild_hits)))

    ads_labels = []
    ads_dup_run = 0
    prev_ads = None
    for d in range(1, 32):
        ads_items = [i for i in items(d) if (i.get("status") or "").upper() == "ADS"]
        if not ads_items:
            continue
        lbl = (ads_items[0].get("name") or "").replace("ADS PO — ", "").strip()
        ads_labels.append(lbl)
        if lbl == prev_ads:
            ads_dup_run += 1
        prev_ads = lbl
    ads_unique = len(set(ads_labels))
    rows.append(
        (
            "ADS PO — גיוון פרסים (לא Coins בלבד)",
            "✓" if ads_unique >= 6 and ads_dup_run <= 8 else "⚠" if ads_unique >= 4 else "✗",
            f"{ads_unique} סוגים · {len(ads_labels)} ימים",
        )
    )
    ads_superboom = [
        str(d)
        for d in range(1, 32)
        for i in items(d)
        if (i.get("status") or "").upper() == "ADS" and "superboom" in (i.get("name") or "").lower()
    ]
    dice_week_bad: list[str] = []
    for w in range(5):
        week_days = [d for d in range(1, 32) if (d - 1) // 7 == w]
        n = sum(dice_promo_hits_on_day(items(d)) for d in week_days)
        if n > DICE_PROMO_MAX_PER_WEEK:
            dice_week_bad.append(f"w{w + 1}:{n}")
    rows.append(
        (
            "Dice promo — ≤1×/שבוע (Deluxe / BTS PM)",
            "✓" if not dice_week_bad else "✗",
            "OK" if not dice_week_bad else ",".join(dice_week_bad),
        )
    )
    clan_dash_bad = validate_clan_dash_week(days)
    rows.append(
        (
            "Clan-Dash — תבנית שבועית (Mon–Fri בלבד)",
            "✓" if not clan_dash_bad else "✗",
            "OK" if not clan_dash_bad else "; ".join(clan_dash_bad[:8])
            + ("…" if len(clan_dash_bad) > 8 else ""),
        )
    )
    rows.append(
        (
            "ADS PO — ללא Superboom",
            "✓" if not ads_superboom else "✗",
            "OK" if not ads_superboom else ",".join(ads_superboom),
        )
    )

    rows.append(
        (
            "Mid Term — Quest בין Figz ל-Globez",
            "✓" if not validate_mid_term_quest_buffer() else "✗",
            "OK" if not validate_mid_term_quest_buffer() else ",".join(validate_mid_term_quest_buffer()),
        )
    )

    from validate_season_skus import validate_days as validate_season_sku_days

    season_sku_bad = validate_season_sku_days(days)
    rows.append(
        (
            "פרסי עונה — SKU תואם Short/Mid Term (+ Winovate)",
            "✓" if not season_sku_bad else "✗",
            "OK"
            if not season_sku_bad
            else f"{len(season_sku_bad)}: " + "; ".join(season_sku_bad[:6])
            + ("…" if len(season_sku_bad) > 6 else ""),
        )
    )

    mgap_sale = [str(d["date"]) for d in days if d["sale"] and any("MGAP Matched" in i["name"] for i in d["items"])]
    rows.append(("MGAP Matched לא ב-sale", "✓" if not mgap_sale else "✗", "OK" if not mgap_sale else ",".join(mgap_sale)))

    mgap_days = collect_mgap_days(days)
    mgap_by_week = mgap_week_counts(days)
    mgap_week_bad: list[str] = []
    for w in range(5):
        if mgap_days_in_week_slice(w) == 0:
            continue
        c = mgap_by_week.get(w, 0)
        req = required_mgap_count_for_week(w)
        if c > MGAP_PER_WEEK:
            mgap_week_bad.append(f"w{w + 1}={c} (>{MGAP_PER_WEEK})")
        elif c < req:
            mgap_week_bad.append(f"w{w + 1}={c} (<{req})")
    mgap_mon = [str(d) for d in mgap_days if dow(d) == "Mon"]
    mgap_bigger_bad = [
        str(day["date"])
        for day in days
        for i in day["items"]
        if (i.get("status") == "MGAP" or "mgap" in (i.get("name") or "").lower())
        and "bigger" in (i.get("name") or "").lower()
        and not day.get("sale")
    ]
    mgap_variant_bad = [
        f"{day['date']}:{i['name'][:20]}"
        for day in days
        for i in day["items"]
        if i.get("status") == "MGAP"
        and not any(v in (i.get("name") or "") for v in MGAP_ALLOWED)
    ]
    mgap_gap_bad: list[str] = []
    if len(mgap_days) > 1:
        for a, b in zip(mgap_days, mgap_days[1:]):
            if b - a < MGAP_MIN_GAP_DAYS:
                mgap_gap_bad.append(f"{a}→{b}={b-a}")
    rows.append(
        (
            f"MGAP — מרווח ≥{MGAP_MIN_GAP_DAYS} ימים בין פרומואים",
            "✓" if not mgap_gap_bad else "✗",
            "OK" if not mgap_gap_bad else ", ".join(mgap_gap_bad),
        )
    )
    rows.append(
        (
            f"MGAP — {MGAP_PER_WEEK}/שבוע (ברזל; שבוע חלקי בסוף חודש = 1)",
            "✓" if not mgap_week_bad and not mgap_mon and not mgap_gap_bad else "✗",
            f"ימים {mgap_days} · לפי שבוע {dict(sorted(mgap_by_week.items()))}"
            if not mgap_week_bad
            else ", ".join(mgap_week_bad),
        )
    )
    rows.append(
        (
            "MGAP Bigger Multipliers — רק בימי sale",
            "✓" if not mgap_bigger_bad else "✗",
            "OK" if not mgap_bigger_bad else ",".join(mgap_bigger_bad),
        )
    )
    rows.append(
        (
            "MGAP — וריאנטים מותרים בלבד",
            "✓" if not mgap_variant_bad else "✗",
            "OK" if not mgap_variant_bad else ", ".join(mgap_variant_bad),
        )
    )

    ace_offer_bad: list[str] = []
    for day in days:
        d = day["date"]
        for i in day.get("items", []):
            st = i.get("status") or ""
            if st not in PURCHASE_OFFER_STATUSES:
                continue
            nm = i.get("name") or ""
            if _offer_text_skips_ace_sale_check(nm):
                continue
            if ACE_IN_PURCHASE_OFFER_RE.search(nm):
                ace_offer_bad.append(f"{d}:{nm[:28]}")
    rows.append(
        (
            "הצעות רכישה — לא מוכרים קלפי Ace",
            "✓" if not ace_offer_bad else "✗",
            "OK" if not ace_offer_bad else ", ".join(ace_offer_bad[:8]),
        )
    )

    lbp_days = set(lbp_peak_days())
    lbp_bad = []
    for d in lbp_days:
        names = " ".join(i["name"] for i in items(d)).lower()
        if "lotto" not in names or "lbp" not in names:
            lbp_bad.append(str(d))
    rows.append(("Lotto peak + LBP ביחד (ג/ש)", "✓" if not lbp_bad else "✗", "OK" if not lbp_bad else ",".join(lbp_bad)))

    gems_sale_days = [d["date"] for d in days if any("Gems Sale" in i["name"] for i in d["items"])]
    rows.append(("Gems Sale ≤4/חודש", "✓" if len(gems_sale_days) <= 4 else "✗", str(gems_sale_days)))

    ggs_days = sorted(d["date"] for d in days if any("x2 GGS" in i["name"] for i in d["items"]))
    ggs_consecutive = [f"{a}/{b}" for a, b in zip(ggs_days, ggs_days[1:]) if b == a + 1]
    rows.append(
        (
            "x2 GGS — ללא ימים רצופים",
            "✓" if not ggs_consecutive else "✗",
            "OK" if not ggs_consecutive else ", ".join(ggs_consecutive),
        )
    )

    gem_amp_triple = [
        str(day["date"])
        for day in days
        if day_gem_revenue_amplifier_count(day.get("items") or []) >= 3
    ]
    rows.append(
        (
            "מגברי רכישה — לא x2 GGS + Gemback + Price Cut באותו יום",
            "✓" if not gem_amp_triple else "✗",
            "OK" if not gem_amp_triple else ", ".join(gem_amp_triple),
        )
    )

    spin_zone_weak = [
        str(day["date"])
        for day in days
        for i in day.get("items") or []
        if "spin zone" in (i.get("name") or "").lower()
        and "hammers wheel" not in (i.get("name") or "").lower()
        and SPIN_ZONE_WEAK_CHASE_RE.search(i.get("name") or "")
    ]
    rows.append(
        (
            "Spin Zone — לא 2 Dice / 2 Picks כפרס chase בכותרת",
            "✓" if not spin_zone_weak else "✗",
            "OK" if not spin_zone_weak else ", ".join(spin_zone_weak),
        )
    )

    pm_reg_only = [
        i["name"]
        for d in days
        for i in d["items"]
        if i["status"] == "Prize Mania"
        and "Reg pack" in i["name"]
        and "Shiny Limited" not in i["name"]
        and d != 22
    ]
    pm_total = sum(1 for d in days for i in d["items"] if i["status"] == "Prize Mania")
    rows.append(
        (
            "Prize Mania — גיוון קלפים",
            "✓" if pm_total and len(pm_reg_only) < pm_total else "✓" if pm_total == 0 else "⚠",
            f"{pm_total - len(pm_reg_only)}/{pm_total} לא Reg-pack בלבד (BTS/Shiny Limited מותר)",
        )
    )

    dd_families = [dd_broad_family([(i["name"], "", "")]) for d in days for i in d["items"] if i["status"] == "Daily deal" and "multiple" not in i["name"].lower()]
    reg_wheel_share = dd_families.count("reg_wheel") / max(len(dd_families), 1)
    rows.append(
        (
            "DD — גיוון (Reg+Wheel ≤40% מימי DD)",
            "✓" if reg_wheel_share <= 0.42 else "⚠",
            f"Reg+Wheel {reg_wheel_share:.0%} ({dd_families.count('reg_wheel')}/{len(dd_families)})",
        )
    )

    def day_has_coin_sink_surface(d: int, day_items: list[dict]) -> bool:
        if has_real_core_challenge(day_items):
            return True
        if dow(d) == "Mon" and any(
            "time limited prize" in (i.get("name") or "").lower() for i in day_items
        ):
            return True
        return False

    missing_core = [str(d) for d in range(1, 32) if not day_has_coin_sink_surface(d, items(d))]
    rows.append(
        (
            "Core — צ'לנג' ניקוז קוינז בכל יום",
            "✓" if not missing_core else "✗",
            "OK" if not missing_core else ",".join(missing_core),
        )
    )

    coin_sale_dup = [
        str(d)
        for d in range(1, 32)
        if sum(
            1
            for i in items(d)
            if i.get("status") == "Offers & coin sale"
            and re.search(r"coin sale", i.get("name") or "", re.I)
        )
        > 1
    ]
    rows.append(
        (
            "Coin Sale — לכל היותר 1× ביום",
            "✓" if not coin_sale_dup else "✗",
            "OK" if not coin_sale_dup else ", ".join(coin_sale_dup),
        )
    )

    shiny_days = sorted(
        d for d in range(1, 32) if day_has_shiny_show_promo(items(d))
    )
    shiny_dup_days = [
        str(d)
        for d in range(1, 32)
        if sum(1 for i in items(d) if SHINY_SHOW_PROMO_RE.search(i.get("name") or "")) > 1
    ]
    rows.append(
        (
            "Shiny Show — לכל היותר 1× ביום",
            "✓" if not shiny_dup_days else "✗",
            "OK" if not shiny_dup_days else ", ".join(shiny_dup_days),
        )
    )
    shiny_gap_bad: list[str] = []
    if len(shiny_days) > 1:
        for a, b in zip(shiny_days, shiny_days[1:]):
            if b - a < SHINY_SHOW_MIN_GAP_DAYS:
                shiny_gap_bad.append(f"{a}→{b}={b-a}")
    rows.append(
        (
            f"Shiny Show — מרווח ≥{SHINY_SHOW_MIN_GAP_DAYS} ימים בין פרומואים",
            "✓" if not shiny_gap_bad else "✗",
            "OK" if not shiny_gap_bad else ", ".join(shiny_gap_bad),
        )
    )

    shiny_week_bad: list[str] = []
    for w in range(5):
        week_days = [d for d in range(1, 32) if (d - 1) // 7 == w]
        n = sum(1 for d in week_days if day_has_shiny_show_promo(items(d)))
        if n > SHINY_SHOW_MAX_PER_WEEK:
            shiny_week_bad.append(f"w{w + 1}:{n}")
    shiny_variant_dup: list[str] = []
    for widx, week_days in enumerate(SHINY_BY_WEEK):
        labels: list[str] = []
        for d in week_days:
            for i in items(d):
                nm = i.get("name") or ""
                if SHINY_SHOW_PROMO_RE.search(nm):
                    label = nm.split("—", 1)[-1].strip().split("+")[0].strip()
                    if label in labels:
                        shiny_variant_dup.append(f"w{widx + 1}:{d}={label[:24]}")
                    labels.append(label)
                    break
    rows.append(
        (
            f"Shiny Show — ≤{SHINY_SHOW_MAX_PER_WEEK}×/שבוע",
            "✓" if not shiny_week_bad and not shiny_gap_bad and not shiny_variant_dup else "✗",
            "OK"
            if not shiny_week_bad and not shiny_variant_dup
            else ",".join(shiny_week_bad + shiny_variant_dup),
        )
    )

    shiny_no_sink = [
        str(d)
        for d in range(1, 32)
        if day_has_shiny_show_promo(items(d))
        and not has_coin_sink_challenge(items(d))
        and dow(d) != "Mon"
        and not any(is_puzzle_mes_item(i) for i in items(d))
    ]
    rows.append(
        (
            "Shiny Show — לא מחליף Core ניקוז (coin-sink בנוסף)",
            "✓" if not shiny_no_sink else "✗",
            "OK" if not shiny_no_sink else ",".join(shiny_no_sink),
        )
    )

    gp_multi = [
        f"{d}={count_gameplay_core_challenges(items(d))}"
        for d in range(1, 32)
        if count_gameplay_core_challenges(items(d)) > (2 if d in PUZZLE_MES_TEST else 1)
    ]
    rows.append(
        (
            "Core משחקי — לכל היותר 1× ביום",
            "✓" if not gp_multi else "✗",
            "OK" if not gp_multi else ", ".join(gp_multi),
        )
    )
    dd_multi = [
        str(d)
        for d in range(1, 32)
        if sum(1 for i in items(d) if i.get("status") == "Daily deal") > 1
        and not (
            d in SHINY_LIMITED_SPLIT_DD_DAYS
            and len([i for i in items(d) if i.get("status") == "Daily deal"]) == 2
            and any("shiny limited" in (i.get("name") or "").lower() for i in items(d) if i.get("status") == "Daily deal")
            and any("multiple" in (i.get("name") or "").lower() for i in items(d) if i.get("status") == "Daily deal")
        )
    ]
    rows.append(
        (
            "Daily Deal — שורה אחת ביום (Once+repeatable merged)",
            "✓" if not dd_multi else "✗",
            "OK" if not dd_multi else ", ".join(dd_multi),
        )
    )

    shiny_budget_bad: list[str] = []
    dd_keys_preview = assign_daily_deal_keys()
    _, shiny_show_budget = assign_shiny_show_variants(dd_keys_preview)
    sim = CardLedger()
    sim.take(23, "Shiny Card")
    for d in range(1, 32):
        k = dd_keys_preview.get(d)
        if k:
            sim.build_dd_lines(d, k, is_sale(d))
    for cw in (1, 2, 3, 4):
        cap = CARD_BUDGETS[cw].get("Shiny Limited", 0)
        used = sim.used[cw].get("Shiny Limited", 0) + shiny_show_budget.get(cw, 0)
        if used > cap:
            shiny_budget_bad.append(f"wk{cw}:{used}/{cap}")
    rows.append(
        (
            "Shiny Limited / Wild Guaranteed — DD + Shiny Show ≤ תקרת Nivi",
            "✓" if not shiny_budget_bad else "✗",
            "OK" if not shiny_budget_bad else ",".join(shiny_budget_bad),
        )
    )

    sl_surfaces_bad: list[str] = []
    for cw in (1, 2, 3, 4):
        cap = CARD_BUDGETS[cw].get("Shiny Limited", 0)
        days_in_cw = [d for d in range(1, 32) if card_week(d) == cw]
        used = sum(count_shiny_limited_surfaces(items(d)) for d in days_in_cw)
        if used > cap:
            sl_surfaces_bad.append(f"cw{cw}:{used}/{cap}")
    rows.append(
        (
            "Shiny Limited — כל המשטחים (DD+PM+Show) ≤ תקרת שבוע כרטיסים",
            "✓" if not sl_surfaces_bad else "✗",
            "OK" if not sl_surfaces_bad else ",".join(sl_surfaces_bad),
        )
    )
    sl_dd_days = sorted(d for d in range(1, 32) if dd_keys_preview.get(d) == "shiny_ltd")
    sl_dd_dows = [dow(d) for d in sl_dd_days]
    dow_counts = {d: sl_dd_dows.count(d) for d in set(sl_dd_dows)}
    sl_dow_bad = [f"{d}×{n}" for d, n in dow_counts.items() if n >= 3]
    rows.append(
        (
            "Shiny Limited ב-DD — לא אותו יום בשבוע שוב ושוב",
            "✓" if not sl_dow_bad else "✗",
            "OK"
            if not sl_dow_bad
            else f"≥3× אותו DOW: {','.join(sl_dow_bad)} · ימים {','.join(map(str, sl_dd_days))}",
        )
    )

    dd_wild_sl_days = [
        str(d)
        for d in range(1, 32)
        if any(
            x in (i.get("name") or "").lower()
            for i in items(d)
            if i.get("status") == "Daily deal"
            for x in ("shiny limited", "wild")
        )
    ]
    rows.append(
        (
            "DD — Shiny Limited / Wild במכירה (לא רק Shiny Show)",
            "✓" if len(dd_wild_sl_days) >= 4 else "⚠",
            f"{len(dd_wild_sl_days)} ימים: {','.join(dd_wild_sl_days[:12])}",
        )
    )

    dd_once_no_mult: list[str] = []
    for d in range(1, 32):
        dds = [i for i in items(d) if i.get("status") == "Daily deal"]
        if any(
            "once + repeatable" in (i.get("name") or "").lower()
            or "companion repeatable dd" in (i.get("desc") or "").lower()
            for i in dds
        ):
            continue
        once = [
            i
            for i in dds
            if any(x in (i.get("name") or "").lower() for x in ("shiny limited", "wild"))
            and "multiple" not in (i.get("name") or "").lower()
        ]
        if once and not any("multiple" in (i.get("name") or "").lower() for i in dds):
            dd_once_no_mult.append(str(d))
    rows.append(
        (
            "DD once (Wild/Shiny Limited) + DD multiple באותו יום",
            "✓" if not dd_once_no_mult else "✗",
            "OK" if not dd_once_no_mult else ",".join(dd_once_no_mult),
        )
    )

    consec_sec: list[str] = []
    prev_lbl: str | None = None
    for d in range(1, 32):
        lbl = secondary_label_from_day_items(items(d), d)
        if lbl:
            if prev_lbl and lbl == prev_lbl:
                consec_sec.append(f"{d - 1}/{d}:{lbl}")
            prev_lbl = lbl
        else:
            prev_lbl = None
    rows.append(
        (
            "הצעה משנית — ללא אותו סוג ביומיים רצופים",
            "✓" if not consec_sec else "✗",
            "OK" if not consec_sec else ",".join(consec_sec),
        )
    )

    gameplay_sb_bad: list[str] = []
    gameplay_gold_bad: list[str] = []
    for d in range(1, 32):
        for i in items(d):
            if (i.get("status") or "") != "Core":
                continue
            nm = i.get("name") or ""
            desc = i.get("description") or i.get("desc") or ""
            blob = f"{nm} {desc}"
            if not GAMEPLAY_CORE_CHALLENGE_RE.search(nm):
                continue
            if DD_SB_SLOT_RE.search(blob):
                gameplay_sb_bad.append(f"{d}:{nm[:24]}")
            if GAMEPLAY_GOLD_PRIZE_RE.search(nm):
                gameplay_gold_bad.append(f"{d}:{nm[:24]}")
    rows.append(
        (
            "Core משחקי — ללא SB (Wheel / %SB / Slotobucks)",
            "✓" if not gameplay_sb_bad else "✗",
            "OK" if not gameplay_sb_bad else ", ".join(gameplay_sb_bad),
        )
    )
    rows.append(
        (
            "Core משחקי — פרס לא Gold (Gold רק ברכישה)",
            "✓" if not gameplay_gold_bad else "✗",
            "OK" if not gameplay_gold_bad else ", ".join(gameplay_gold_bad),
        )
    )

    ms2_days = list(SHINY_MS2_COUNTDOWN_LAST)
    shiny_ms2 = sum(1 for d in ms2_days if items_have_shiny_card_source(items(d)))
    rows.append(
        (
            "Shiny MS2 — Shiny Card ב־2/3 ימים אחרונים (22–24/8)",
            "✓" if shiny_ms2 >= 2 else "✗",
            f"{shiny_ms2}/3 ימים עם מקור Shiny Card",
        )
    )

    sb_week_bad: list[str] = []
    hw_week_bad: list[str] = []
    _tier_rank = {"Low": 0, "Mid": 1, "Medium": 1, "High": 2, "Max": 3}
    for w in range(5):
        sb_n = 0
        hw_n = 0
        for d in range(1, 32):
            if dd_week_index(d) != w:
                continue
            day_dd_lines = [(i["name"], "", "") for i in items(d) if i["status"] == "Daily deal"]
            if day_dd_lines:
                sb_n += dd_slotobucks_slots(day_dd_lines)
                hw_n += dd_hammer_wheel_slots(day_dd_lines)
        if sb_n > DD_WEEKLY_SB_CAP:
            sb_week_bad.append(f"w{w + 1}={sb_n}")
        if hw_n > DD_WEEKLY_HAMMER_WHEEL_CAP:
            hw_week_bad.append(f"w{w + 1}={hw_n}")
    rows.append(
        (
            "DD — SlotoBucks / SB Wheel ≤2×/שבוע",
            "✓" if not sb_week_bad else "✗",
            "OK" if not sb_week_bad else ", ".join(sb_week_bad),
        )
    )
    rows.append(
        (
            "DD — Hammer Wheel (Reg+HW) ≤2×/שבוע",
            "✓" if not hw_week_bad else "✗",
            "OK" if not hw_week_bad else ", ".join(hw_week_bad),
        )
    )

    # MGAP + Coin Sale same-day stacking (cannibalization — calibrated as negative interaction).
    # Day 22 (BTS flagship) is exempt — its MGAP is by design as part of the event anchor set.
    mgap_coin_sale_days = []
    for d in range(1, 32):
        if d == 22:  # BTS scripted exception
            continue
        day_items = items(d)
        names = [(i.get("name") or "").lower() for i in day_items]
        has_mgap = any("mgap" in n for n in names)
        has_coin_sale = any(re.search(r"coins? sale", n) for n in names)
        if has_mgap and has_coin_sale:
            mgap_coin_sale_days.append(str(d))
    rows.append(
        (
            "MGAP + Coin Sale — לא ביחד (קניבליזציה)",
            "✓" if not mgap_coin_sale_days else "✗",
            "OK" if not mgap_coin_sale_days else ", ".join(mgap_coin_sale_days),
        )
    )

    rolling_variants: set[int] = set()
    bmfl_bad: list[str] = []
    bxgy_days: list[int] = []
    for d in range(1, 32):
        for i in items(d):
            if i.get("status") != "Rolling offer":
                continue
            nm = i.get("name") or ""
            m = re.search(r"(\d+)\s*cycles?", nm, re.I)
            if m:
                rolling_variants.add(int(m.group(1)))
            pr = normalize_offer_pricing(i.get("pricing"))
            if is_rolling_bmfl_name(nm):
                if m and int(m.group(1)) != ROLLING_BMFL_CYCLES:
                    bmfl_bad.append(f"{d}:cycles")
                if pr != ROLLING_BMFL_PRICING:
                    bmfl_bad.append(f"{d}:pricing")
            else:
                bxgy_days.append(d)
    roll_ok = not bmfl_bad and len(bxgy_days) >= 1
    rows.append(
        (
            "Rolling — BMFL (3c High) + Buy X Get Y בחודש",
            "✓" if roll_ok else "✗",
            "OK"
            if roll_ok
            else f"BMFL: {','.join(bmfl_bad) or 'OK'}; BXGY ימים: {sorted(set(bxgy_days)) or 'חסר'}",
        )
    )

    rolling_stamp_bad: list[str] = []
    for d in range(1, 32):
        for i in items(d):
            if i.get("status") != "Rolling offer":
                continue
            rolling_stamp_bad.extend(
                validate_rolling_item_stamps(d, i.get("name") or "", i.get("desc") or "")
            )
    rows.append(
        (
            "Rolling — RDS≤4 / GGS≤2 לכל מחזור (1+3, 1+1)",
            "✓" if not rolling_stamp_bad else "✗",
            "OK" if not rolling_stamp_bad else "; ".join(rolling_stamp_bad[:10])
            + ("…" if len(rolling_stamp_bad) > 10 else ""),
        )
    )

    pricing_week_bad: list[str] = []
    for w in range(6):
        ds = [d for d in range(1, 32) if (d - 1) // 7 == w]
        if len(ds) < 7:
            continue
        tiers: set[str] = set()
        for d in ds:
            for i in items(d):
                t = normalize_offer_pricing(i.get("pricing"))
                if t:
                    tiers.add(t)
        if not {"Medium", "High", "Max"}.issubset(tiers):
            pricing_week_bad.append(f"w{w + 1}({sorted(tiers)})")
    rows.append(
        (
            "Pricing — M / H / Max בכל שבוע קלנדרי מלא",
            "✓" if not pricing_week_bad else "✗",
            "OK" if not pricing_week_bad else ", ".join(pricing_week_bad),
        )
    )

    dd_sec_same: list[str] = []
    for d in range(1, 32):
        dd_p = sec_p = None
        for i in items(d):
            if i.get("status") == "Daily deal":
                p = normalize_offer_pricing(i.get("pricing"))
                if p and (dd_p is None or _tier_rank.get(p, 0) > _tier_rank.get(dd_p, 0)):
                    dd_p = p
            elif counts_toward_vfm_cap(i):
                sec_p = normalize_offer_pricing(i.get("pricing"))
        if dd_p and sec_p and dd_p == sec_p:
            if d == 2 and day_has_mgap_bogo_or_matched(d):
                continue
            dd_sec_same.append(str(d))
    rows.append(
        (
            "Pricing — DD והצעה שנייה שונים באותו יום",
            "✓" if not dd_sec_same else "✗",
            "OK" if not dd_sec_same else ",".join(dd_sec_same),
        )
    )

    mgap_offer_high_bad: list[str] = []
    for d in range(1, 32):
        if not day_has_mgap_bogo_or_matched(d):
            continue
        sec_p = None
        for i in items(d):
            if counts_toward_vfm_cap(i):
                sec_p = normalize_offer_pricing(i.get("pricing"))
                break
        if sec_p != "High":
            mgap_offer_high_bad.append(str(d))
    rows.append(
        (
            "MGAP BOGO/Matched — הצעה שנייה High",
            "✓" if not mgap_offer_high_bad else "✗",
            "OK" if not mgap_offer_high_bad else ",".join(mgap_offer_high_bad),
        )
    )

    rows.append(("טיוטה — לא הועלה ל-Monday", "✓", "ממתין לאישור צוות"))

    bogo_bad: list[str] = []
    for d in DD_BOGO_DAYS:
        for i in items(d):
            if i.get("status") != "Daily deal":
                continue
            nm = (i.get("name") or "").lower()
            if "bogo" not in nm:
                bogo_bad.append(f"{d}:no_tag")
            elif "shiny limited" in nm or ("wild" in nm and "once" in nm):
                bogo_bad.append(f"{d}:ineligible_prize")
    rows.append(
        (
            "DD BOGO — רק פרסים repeatable (לא Shiny Limited / Wild once)",
            "✓" if not bogo_bad else "✗",
            "OK" if not bogo_bad else ",".join(bogo_bad),
        )
    )

    # DD BOGO — mandatory exactly 2×/month on scheduled days (see monthly_guidelines + learnings.md)
    bogo_days_found = sorted(
        d
        for d in range(1, 32)
        if any("BOGO" in (i.get("name") or "") for i in items(d) if i.get("status") == "Daily deal")
    )
    bogo_missing = [str(d) for d in sorted(DD_BOGO_DAYS) if d not in bogo_days_found]
    bogo_extra = [str(d) for d in bogo_days_found if d not in DD_BOGO_DAYS]
    bogo_ok = (
        len(bogo_days_found) == DD_BOGO_REQUIRED_PER_MONTH
        and not bogo_missing
        and not bogo_extra
    )
    bogo_detail = f"מתוכנן {sorted(DD_BOGO_DAYS)} · בפועל {bogo_days_found}"
    if bogo_missing:
        bogo_detail += f" · חסר: {bogo_missing}"
    if bogo_extra:
        bogo_detail += f" · מיותר: {bogo_extra}"
    rows.append(
        (
            f"DD BOGO — בדיוק {DD_BOGO_REQUIRED_PER_MONTH}×/חודש (task config)",
            "✓" if bogo_ok else "✗",
            bogo_detail if bogo_ok else bogo_detail,
        )
    )

    on_purchase_bad = [
        str(d)
        for d in sorted(DD_ON_PURCHASE_DAYS)
        if not any(
            (i.get("status") == "Daily deal" and "(on purchase)" in (i.get("name") or "").lower())
            for i in items(d)
        )
    ]
    rows.append(
        (
            "DD on-purchase — ימים מתוכננים (12/8)",
            "✓" if not on_purchase_bad else "✗",
            "OK" if not on_purchase_bad else ",".join(on_purchase_bad),
        )
    )

    # Fortune Dip present on scheduled days
    fdip_found = [d for d in range(1, 32) if any("fortune dip" in i["name"].lower() for i in items(d))]
    fdip_missing = [str(d) for d in FORTUNE_DIP_DAYS if d not in fdip_found]
    rows.append(
        (
            "Fortune Dip — שיבוץ בימים המתוכננים",
            "✓" if not fdip_missing else "✗",
            f"ימים: {fdip_found}" if not fdip_missing else f"חסר: {fdip_missing}",
        )
    )

    d1 = days[0]
    has_driver = any(
        (dr.get("id") == "month_open_biggest_denom") for dr in (d1.get("purchaseDrivers") or [])
    )
    denom_as_promo = [
        i["name"]
        for i in d1.get("items", [])
        if re.search(r"biggest\s+denom|1st\s+of\s+(the\s+)?month", (i.get("name") or ""), re.I)
    ]
    rows.append(
        (
            "1 בחודש — biggest store denom (driver, לא פרומו)",
            "✓" if has_driver and not denom_as_promo else "✗",
            "OK"
            if has_driver and not denom_as_promo
            else ("חסר driver" if not has_driver else "לא לשים כפרומו: " + "; ".join(denom_as_promo[:3])),
        )
    )

    return rows


def validate_card_ledger(ledger: CardLedger) -> list[tuple[str, str, str]]:
    over: list[str] = []
    unused = 0
    for w, budget in CARD_BUDGETS.items():
        for key, cap in budget.items():
            used = ledger.used[w].get(key, 0)
            if used > cap:
                over.append(f"w{w}:{key}={used}>{cap}")
            unused += ledger.rem[w].get(key, 0)
    return [
        (
            "מאגר קלפים — לא חורג מתקרת שבוע (תמונת הפצה)",
            "✓" if not over else "✗",
            "OK" if not over else ", ".join(over[:10]),
        ),
        (
            "מאגר קלפים — ניצול",
            "✓",
            f"יחידות שלא שובצו (מותר): {unused}",
        ),
    ]


# Buy All removed from the general pool — negative lift (-10.3K per calibration) and poor
# synergy with other offers. Still appears inside Popup Store (scripted days 15/8) and
# explicitly as needed, but not auto-assigned to regular calendar slots.
SECOND_OFFER_POOL = [
    "RYD",
    "Rolling",
    "Decoy Bonanza",
    "Prize Mania",
    "Buy All",
    "Mystery Buy All",
]
SECOND_OFFER_MONTHLY_CAP = {"Buy All": 4, "Mystery Buy All": 3}

# Sale days: Coin Sale is the anchor but we still pair it with a complementary offer.
# Rolling More-for-Less or RYD sit naturally on top of a sale day without VFM-cap issues.
SALE_OFFER_POOL = ["Rolling", "RYD"]

# Sale weekend 28–29: ensure a VFM second offer (not only Coin Sale anchor).
SECOND_OFFER_FORCED: dict[int, str] = {
    8: "Rolling",
    12: "Rolling",
    15: "Mystery Buy All",
    28: "Decoy Bonanza",
    29: "RYD",
}

# Post-sale strong coin-drain days: Custom Pod / Win Master forces after major sale clusters.
# Drains the high balances players carry out of sale weekend into early-week spend.
POST_SALE_DRAIN = {9, 30}  # after 7-8/8 (Betty sale) and after 28-29/8 (end-month sale)


def monday_has_primary_anchor(d: int) -> bool:
    if d in ROLLING_MFL:
        return True  # Rolling MFL is the secondary offer on that Monday
    return False


# Monday Dash Day — light second offer only (no MGAP/Coin Sale/big Rolling/Prize Mania per constraints).
MONDAY_SECOND_OFFER_POOL = ("RYD", "Buy All")


def assign_monday_second_offer(
    d: int,
    picks: dict[int, str | None],
    counts: dict[str, int],
) -> str:
    prev = prev_assigned_secondary_label(picks, d)
    candidates = list(MONDAY_SECOND_OFFER_POOL)
    for capped, limit in SECOND_OFFER_MONTHLY_CAP.items():
        if counts.get(capped, 0) >= limit:
            candidates = [p for p in candidates if p != capped]
    if prev and len(candidates) > 1:
        candidates = [p for p in candidates if p != prev]
    if not candidates:
        candidates = ["RYD"]
    return min(candidates, key=lambda p: (counts.get(p, 0), MONDAY_SECOND_OFFER_POOL.index(p)))


def assign_second_offers() -> dict[int, str | None]:
    """Spread secondary offers — no identical type on consecutive calendar days."""
    counts = {p: 0 for p in SECOND_OFFER_POOL}
    sale_counts = {p: 0 for p in SALE_OFFER_POOL}
    picks: dict[int, str | None] = {}

    # Pre-count weeks where ROLLING_MFL already fires (all days now — Mondays allowed)
    rolling_used_weeks: dict[int, int] = {}
    for mfl_day in ROLLING_MFL:
        w = card_week(mfl_day)
        rolling_used_weeks[w] = rolling_used_weeks.get(w, 0) + 1

    def rolling_available(d: int) -> bool:
        w = card_week(d)
        return rolling_used_weeks.get(w, 0) < 1

    def consume_rolling(d: int) -> None:
        w = card_week(d)
        rolling_used_weeks[w] = rolling_used_weeks.get(w, 0) + 1

    for d in range(1, 32):
        if d == 22:
            picks[d] = None
            continue
        if d in POPUP_STORE_DAYS:
            if d in POPUP_STORE_LAUNCH_SHELL_ONLY:
                picks[d] = "RYD"
                counts["RYD"] = counts.get("RYD", 0) + 1
                continue
            if d not in POPUP_STORE_LAUNCH_SHELL_ONLY and POPUP_STORE_INNER_OFFER.get(d):
                picks[d] = None
                continue
        if d in COUNTER_PO and d != 23:
            picks[d] = "RYD"
            counts["RYD"] = counts.get("RYD", 0) + 1
            continue
        if d in ROLLING_MFL:
            # Rolling MFL fires this day and IS the VFM offer — no additional VFM second offer
            picks[d] = None
            continue
        if d in SECOND_OFFER_FORCED:
            pick = SECOND_OFFER_FORCED[d]
            picks[d] = pick
            counts[pick] = counts.get(pick, 0) + 1
            if pick == "Rolling":
                consume_rolling(d)
            continue
        # Sale days: pair Coin Sale with a complementary secondary offer
        if is_sale(d) and d != 22:
            prev = prev_assigned_secondary_label(picks, d)
            cands = [p for p in SALE_OFFER_POOL if p != "Rolling" or rolling_available(d)]
            if not cands:
                cands = ["RYD"]
            if prev in cands and len(cands) > 1:
                cands = [p for p in cands if p != prev]
            if len(cands) == 1 and cands[0] == prev:
                fallback = [
                    p
                    for p in SECOND_OFFER_POOL
                    if p != prev and (p != "Rolling" or rolling_available(d))
                ]
                if fallback:
                    cands = fallback
            pick = min(cands, key=lambda p: (sale_counts.get(p, 0), SALE_OFFER_POOL.index(p) if p in SALE_OFFER_POOL else 99))
            picks[d] = pick
            sale_counts[pick] = sale_counts.get(pick, 0) + 1
            if pick == "Rolling":
                consume_rolling(d)
            continue
        if dow(d) == "Mon":
            if d in ROLLING_MFL:
                picks[d] = None
                continue
            pick = assign_monday_second_offer(d, picks, counts)
            picks[d] = pick
            counts[pick] = counts.get(pick, 0) + 1
            continue
        if d in EXTREME:
            prev = prev_assigned_secondary_label(picks, d)
            pick = "Decoy Bonanza" if prev == "RYD" else "RYD"
            picks[d] = pick
            counts[pick] = counts.get(pick, 0) + 1
            continue
        prev = prev_assigned_secondary_label(picks, d)
        candidates = [p for p in SECOND_OFFER_POOL]
        candidates = [p for p in candidates if p != "Rolling" or rolling_available(d)]
        for capped, limit in SECOND_OFFER_MONTHLY_CAP.items():
            if counts.get(capped, 0) >= limit:
                candidates = [p for p in candidates if p != capped]
        if (d + 1) in EXTREME:
            candidates = [p for p in candidates if p != "RYD"]
        if (d + 1) in COUNTER_PO:
            candidates = [p for p in candidates if p != "Prize Mania"]
        if (d + 1) in POPUP_STORE_DAYS:
            candidates = [p for p in candidates if p != "Decoy Bonanza"]
        if d == 23:
            candidates = [p for p in candidates if p != "Prize Mania"]
        if prev:
            no_repeat = [p for p in candidates if p != prev]
            if no_repeat:
                candidates = no_repeat
        if not candidates:
            candidates = [p for p in SECOND_OFFER_POOL if counts.get(p, 0) < SECOND_OFFER_MONTHLY_CAP.get(p, 99)]
        # Depth anchor: Saturdays should get a high-lift depth offer (Custom Pod / Decoy Bonanza)
        # if not already anchored by a sale or primary anchor. Boost Decoy Bonanza on Saturdays.
        if dow(d) == "Sat" and "Decoy Bonanza" in candidates and not is_sale(d):
            candidates = ["Decoy Bonanza"] + [p for p in candidates if p != "Decoy Bonanza"]
        # Lift-aware tie-break: predict marginal revenue for each candidate
        if _HAS_SCORER and candidates:
            def _score_candidate(cand_label: str) -> float:
                """Approximate lift of adding this secondary offer type."""
                _name_map = {
                    "RYD": "RYD — Reveal Your Deal",
                    "Rolling": "Rolling Offer — 5 cycles (Buy X Get Y)",
                    "Decoy Bonanza": "Decoy Bonanza Triple",
                    "Prize Mania": "Prize Mania Weekend",
                    "Counter PO": "Counter PO",
                }
                proxy_item = {"name": _name_map.get(cand_label, cand_label), "backup": False}
                proxy_day = {
                    "dow": dow(d), "date": d, "month": "2026-08",
                    "tag": None, "banner": None,
                    "items": [proxy_item],
                }
                return _scorer.predict(proxy_day)
            # Sort by (diversity_penalty * usage_count_weight + lift): prefer unused high-lift
            diversity_weight = 3.0  # $K equivalent per extra use to penalise repetition
            pick = max(
                candidates,
                key=lambda p: _score_candidate(p) - diversity_weight * counts.get(p, 0),
            )
        else:
            pick = min(candidates, key=lambda p: (counts[p], SECOND_OFFER_POOL.index(p)))
        picks[d] = pick
        counts[pick] += 1
        if pick == "Rolling":
            consume_rolling(d)
    return picks


def build_day(
    d: int,
    second_offer_pick: str | None = None,
    daily_deal_lines: list[DDLine] | None = None,
    core_challenge_kind: str | None = None,
    ledger: CardLedger | None = None,
    dd_key: str | None = None,
    shiny_show_variant: str | None = None,
    spinner_biweeks_used: set[int] | None = None,
    offer_pricing_tier: str | None = None,
    rolling_spec: dict[int, tuple[str, int]] | None = None,
) -> dict:
    rolling_spec = rolling_spec or {}
    day = {
        "date": d,
        "dow": dow(d),
        "iso": f"2026-08-{d:02d}",
        "sale": is_sale(d),
        "tag": None,
        "banner": None,
        "seasons": [
            {
                "name": short_term(d),
                "status": "Short Term",
                "isFirst": d == 1 or short_term(d) != short_term(d - 1),
                "desc": short_term_album_cycle_description(d)
                if (d == 1 or short_term(d) != short_term(d - 1))
                else "",
            },
            {"name": mid_term(d), "status": "Mid Term",
             "isFirst": d in ROTATING_MID_TERM_FIRST_DAYS,
             "desc": (
                 "Mid-term rotation — Quest / Figz / Globez prizes by phase: "
                 "nivi_collector_album_prizes.md (Winovate scenes · Mega Pods · Quest islands)."
             )
             if d in ROTATING_MID_TERM_FIRST_DAYS else ""},
            {"name": "Winovate", "status": "Mid Term", "isFirst": winovate_season_is_first(d),
             "desc": "Winovate scene milestones by album phase — nivi_collector_album_prizes.md"
             if winovate_season_is_first(d) else ""},
            {"name": "Mega Pods", "status": "Mid Term", "isFirst": mega_pods_season_is_first(d),
             "desc": "Mega Pods freemium/premium milestones — nivi_collector_album_prizes.md"
             if mega_pods_season_is_first(d) else ""},
            {
                "name": f"Album — {album_phase(d)}",
                "status": "Album",
                "isFirst": d == 1 or album_phase(d) != album_phase(d - 1),
                "desc": album_season_description(d)
                if (d == 1 or album_phase(d) != album_phase(d - 1))
                else "",
            },
        ],
        "items": [],
        "notes": "",
    }
    items = day["items"]

    def add(name, status="Offers & coin sale", pricing="High", desc="", backup=False):
        nm_low = (name or "").lower()
        desc = enrich_item_description(
            name, status, pricing, desc, d, on_extreme=d in EXTREME
        )
        is_offer_line = any(
            x in nm_low for x in ("decoy bonanza", "buy all", "mystery buy all", "ryd —", "ryd -", "rolling offer", "prize mania")
        )
        purchase_promo = not is_offer_line and (
            status in ("MGAP", "Gems")
            or status == "Offers & coin sale"
        )
        if purchase_promo and "duration:" not in (desc or "").lower():
            desc = with_purchase_promo_timing(name, desc or "")
        items.append({"name": name, "status": status, "pricing": pricing, "desc": desc, "backup": backup})

    def has_item_substr(sub: str) -> bool:
        s = sub.lower()
        return any(s in (i.get("name") or "").lower() for i in items)

    # Marketing / community calendar (skip duplicates — e.g. MGAP BOGO stays Wed 5 per economy)
    if d in STATUS_BOOST:
        add("Status Boost", "Core", None, anchor_description("Status Boost", d))
    if d in SHINY_COLLECTION_LAST:
        add(
            "Album — Last Day Shiny Collection (MS1)",
            "Album",
            None,
            anchor_description("Album — Last Day Shiny Collection (MS1)", d),
        )
        day["notes"] += "Shiny Collection #1 last day. "
    if d in SHINY_COLLECTION_OPEN:
        n = SHINY_COLLECTION_OPEN[d]
        open_name = f"Album — {n}{'nd' if n == 2 else 'rd'} Shiny Collection Opening"
        add(open_name, "Album", None, anchor_description(open_name, d))
        day["notes"] += f"Shiny Collection #{n} opens. "
    if d in BETTY_BDAY:
        day["tag"] = day["tag"] or "event"
        day["banner"] = day["banner"] or "Betty's Birthday"
        if d == 8:
            add(
                "Betty's Birthday — themed offers / MES",
                "Core",
                None,
                anchor_description("Betty's Birthday", d),
            )
        else:
            day["notes"] += "Betty's Birthday (day 2). "
    if d in NOSTALGIC_WEEKEND:
        day["tag"] = day["tag"] or "event"
        day["banner"] = day["banner"] or "Nostalgic Weekend"
        if d == 14:
            day["notes"] += "Nostalgic Weekend marketing (14–16/8) — Coin Sale row covers the purchase promo. "
    reg, ace, gold = stars_reg(d), stars_ace(d), stars_gold(d)
    if ledger and dd_key:
        dd_lines = ledger.build_dd_lines(d, dd_key, day["sale"])
    elif daily_deal_lines is not None:
        dd_lines = daily_deal_lines
    else:
        dd_lines = default_daily_deal_lines(d, day["sale"])
    for dd_name, dd_pr, dd_desc in dd_lines:
        if d in DD_BOGO_DAYS and dd_lines_allow_bogo(dd_lines):
            dd_name = dd_name + " (BOGO — task config)"
        dd_pr = adjust_dd_pricing_vs_rolling(dd_pr, d, second_offer_pick)
        dd_pr = adjust_dd_pricing_vs_mgap_high_offers(dd_pr, d, offer_pricing_tier)
        if d == 2 and day_has_mgap_bogo_or_matched(d):
            dd_pr = "High"
        add(dd_name, "Daily deal", dd_pr, dd_desc)

    if d in FORTUNE_DIP_DAYS:
        add("Fortune Dip — Extreme Stamp / SB up to 700%", "Offers & coin sale", "High", "1×/month topper; strong on sale+event days")

    if d in POPUP_STORE_DAYS:
        popup_kind = POPUP_STORE_INNER_OFFER.get(d)
        add(popup_store_shell_name(d), "Popup Store", None, popup_store_shell_description(d))
        if d in POPUP_STORE_LAUNCH_SHELL_ONLY or not popup_kind:
            day["notes"] += (
                f"Popup Store {POPUP_STORE_PHASE_BY_DAY[d][0]} ({POPUP_STORE_PHASE_BY_DAY[d][1]}) — shell only. "
            )
            if d in POPUP_STORE_LAUNCH_SHELL_ONLY:
                day["notes"] += (
                    "RYD on this day (if present) is BACKUP cap only — use if Popup LAUNCH slips; do not run both as primary VFM. "
                )
        elif popup_kind == "Decoy Bonanza":
            cohort = "Cohort: Popup Store off-test segment (via Popup Store shell).\n"
            top = pick_paired_decoy_top(d, reg, ace, gold, ledger, allow_wild=d not in EXTREME)
            in_name, in_body = decoy_bonanza_item(d, top)
            pop_pr = offer_pricing_tier or "High"
            add(in_name, "Offers & coin sale", pop_pr, cohort + in_body)
            add(
                in_name,
                "Offers & coin sale",
                pop_pr,
                f"{in_body}\nControl cohort — Popup Store test day ({POPUP_STORE_PHASE_BY_DAY[d][1]}); same SKUs as paired inner offer.",
            )
            day["notes"] += f"Popup Store {POPUP_STORE_PHASE_BY_DAY[d][0]} ({POPUP_STORE_PHASE_BY_DAY[d][1]}). "
        else:
            in_name, in_st, in_pr, in_desc = build_popup_store_inner_offer(
                d, popup_kind, reg, ace, gold, ledger,
                on_extreme=d in EXTREME,
                offer_pricing_tier=offer_pricing_tier,
            )
            if offer_pricing_tier and in_st in ("RYD", "Buy all"):
                in_pr = offer_pricing_tier
            add(in_name, in_st, in_pr, in_desc)
            day["notes"] += f"Popup Store {POPUP_STORE_PHASE_BY_DAY[d][0]} ({POPUP_STORE_PHASE_BY_DAY[d][1]}). "

    if d in PUZZLE_MES_TEST:
        add(
            puzzle_mes_item_name(d),
            "Core",
            None,
            puzzle_mes_test_description(d),
        )
        if d == min(PUZZLE_MES_TEST):
            day["notes"] += (
                f"Puzzle M.E.S {PUZZLE_MES_DAY_COUNT}-day Core soft launch (~{PUZZLE_MES_COHORT_PCT}% cohort, 18–24/8; independent of Popup Store). "
            )

    if day["dow"] == "Thu":
        add("Golden Spin — weekly feature", "Gems", None, "")
    if day["dow"] == "Wed":
        add(
            f"Piggy — break for {stars_reg(d)}★ Reg card",
            "Offers & coin sale",
            "High",
            anchor_description(f"Piggy — break for {stars_reg(d)}★ Reg card", d),
        )

    if day["dow"] in ("Mon", "Tue", "Wed", "Thu", "Fri"):
        add_clan_dash_for_dow(day["dow"], d, add)

    # Stickers / Phase countdown
    if 18 <= d <= 22:
        day["notes"] += "Stickers Season (leading to sale). "
    if d in (22, 23, 24):
        day["notes"] += "Shiny MS2 countdown (3d / 2d / last day). "

    # Major event Back to School (+ marketing "Summer Sale" same weekend)
    if d == 22:
        day["tag"] = "event"
        day["banner"] = "Back to School / Summer Sale"
        day["sale"] = True
        add("Coin Sale — Back to School", "Offers & coin sale", "Max", "Flagship sale")
        add("Happy Hour / Jumbo Giveaway — Back to School", "Offers & coin sale", "High", "")
        add("MGAP Bigger Multipliers — Back to School themed", "MGAP", "High", "")
        add("Boosted Gemback 500% — Back to School (5h, post 11:00 UTC)", "Gems", None, "Flagship sale = 500% tier")
        if ledger:
            ledger.take(d, "Shiny Limited")
            rpk = ledger.pick_reg(d, prefer_high=True)
            r_lbl = card_key_to_label(rpk) if rpk else "5★ Reg"
            add(
                f"Prize Mania — Shiny Limited + {r_lbl} pack + Dice Booster 6H",
                "Prize Mania",
                "High",
                "BTS — premium cards from weekly bank",
            )
        else:
            add(
                "Prize Mania — Shiny Limited + 5★ Reg pack + Dice Booster 6H",
                "Prize Mania",
                "High",
                "BTS — cards from weekly bank",
            )
        add("Custom Pod — Back to School X1200", "Core", None, "")

    if d in MACHINE_SNEAK:
        day["tag"] = day["tag"] or "machine"
        day["banner"] = day["banner"] or f"{AUGUST_MACHINE} — Sneak Peek"
        if not has_item_substr("sneak peek") and can_add_gameplay_core_challenge(items):
            add(
                f"{AUGUST_MACHINE} — Sneak Peek (MES / Spin Zone)",
                "Core",
                None,
                "Marketing calendar 17/8 — August machine launch",
            )
    if d in MACHINE_LAUNCH:
        day["tag"] = "machine"
        day["banner"] = f"{AUGUST_MACHINE} — Launch"
        if (
            not has_item_substr("machine launch")
            and not has_item_substr("hoppin")
            and can_add_gameplay_core_challenge(items)
        ):
            add(
                f"{AUGUST_MACHINE} — Machine Launch (MES · Win Master · Slot Smashes)",
                "Core",
                None,
                "Marketing calendar 19/8 — launch-day Core tie-ins",
            )

    if d in (20, 21) and not any(
        AUGUST_MACHINE.lower() in (i.get("name") or "").lower() for i in items
    ):
        if can_add_gameplay_core_challenge(items):
            st_m = short_term_sku(d)
            add(
                f"{AUGUST_MACHINE} — Spin Zone ({st_m})",
                "Core",
                None,
                f"48h post-launch — machine-themed Core coin sink ({st_m}).",
            )

    if day["sale"] and d != 22:
        if d == 14:
            add(
                "Coin Sale — Nostalgic Weekend",
                "Offers & coin sale",
                "High",
                "Marketing calendar 14–16/8 retro bundle / weekend sale",
            )
        else:
            add("Coin Sale", "Offers & coin sale", "High", "Fri/Sat weekend sale")

    # Primary secondary offer (segmented Decoy test days use control Decoy instead)
    on_extreme = d in EXTREME
    if second_offer_pick and not popup_day_suppresses_standalone_second_offer(d) and not (
        day["tag"] == "event" and d == 22
    ):
        pick = second_offer_pick
        sec_pr = offer_pricing_tier or "High"
        ryd_backup = popup_launch_ryd_is_backup_cap(d, pick)
        if pick == "RYD" and on_extreme:
            ryd_name = f"RYD — {reg}★ Reg + 100% SB"
            ryd_desc = "No Wild — Extreme Stamp day"
        elif pick == "RYD":
            hook = ryd_card_hook(d, reg, ace, gold, ledger)
            ryd_name = f"RYD — {hook}"
            ryd_desc = ""
        else:
            ryd_name = ryd_desc = None
        if pick == "RYD" and on_extreme:
            if ryd_backup:
                ryd_name += POPUP_LAUNCH_RYD_BACKUP_SUFFIX
                ryd_desc = (
                    (ryd_desc + "\n\n") if ryd_desc else ""
                ) + (
                    "BACKUP cap — configure/live only if Popup Store LAUNCH (26/8) does not ship on time. "
                    "Not a parallel VFM offer when Popup is live."
                )
            add(ryd_name, "RYD", sec_pr, ryd_desc, backup=ryd_backup)
        elif pick == "RYD":
            if ryd_backup:
                ryd_name += POPUP_LAUNCH_RYD_BACKUP_SUFFIX
                ryd_desc = (
                    "BACKUP cap — configure/live only if Popup Store LAUNCH (26/8) does not ship on time. "
                    "Not a parallel VFM offer when Popup is live."
                )
            add(ryd_name, "RYD", sec_pr, ryd_desc, backup=ryd_backup)
        elif pick == "Buy All":
            ba_name, ba_desc = buy_all_item(d, reg, ace, gold, sec_pr, ledger)
            add(ba_name, "Buy all", sec_pr, ba_desc)
        elif pick == "Mystery Buy All":
            mb_name, mb_desc = mystery_buy_all_item(d, reg, ace, gold, sec_pr, ledger)
            add(mb_name, "Buy all", sec_pr, mb_desc)
        elif pick in ("Rolling", "Rolling Offer"):
            spec = resolve_rolling_spec(d, pick, rolling_spec)
            if spec:
                add_rolling_offer_item(add, d, spec[0], spec[1], offer_pricing_tier)
        elif pick == "Decoy Bonanza":
            top = offer_top_card(d, reg, ace, gold, ledger, allow_wild=not on_extreme, allow_shiny_ltd=False)
            name, desc = decoy_bonanza_item(d, top)
            add(name, "Offers & coin sale", sec_pr, desc)
        else:
            pm_name = prize_mania_line(d, reg, ace, gold, ledger)
            add(pm_name, "Prize Mania", sec_pr, prize_mania_offer_description(pm_name))

    if d in COUNTER_PO:
        if ledger:
            top = ledger.pick_premium(d, allow_wild=True, allow_ace=False)
            if top:
                add(
                    f"Counter PO — FTD segmented ({card_key_to_label(top)} topper)",
                    "Counter PO",
                    "High",
                    "Not on sale day",
                )
            else:
                add("Counter PO — FTD segmented (on top)", "Counter PO", "High", "Not on sale day")
        else:
            add("Counter PO — FTD segmented (on top)", "Counter PO", "High", "Not on sale day")

    if d in MGAP_SCHEDULE and d != MGAP_BTS_BIGGER_DAY and not day["sale"]:
        variant = MGAP_SCHEDULE[d]
        if variant == "Bigger Multipliers":
            variant = "Wild Symbols"
        add(
            f"MGAP {variant}",
            "MGAP",
            "High",
            f"Iron {MGAP_PER_WEEK}/week; BOGO/Matched ~{MGAP_CYCLE_DAYS}d rotation",
        )

    if d in ROLLING_MFL:
        add_rolling_offer_item(add, d, "bmfl", ROLLING_BMFL_CYCLES, None)

    if d in EXTREME and not day["sale"]:
        add(X2_EXTREME_STAMP_NAME, "Extreme Stamp", None, x2_extreme_stamp_description())

    if d in GEMS_SALE:
        add("Gems Sale — 30% store / 20% offers", "Gems", "High", "No x2 GGS same day")

    if d in GGS_WEEK and d not in GEMS_SALE:
        add("x2 GGS (3h window, post 11:00 UTC)", "Gems", None, "")

    if d in GEMBACK:
        add("Boosted Gemback 300% (5h, post 11:00 UTC)", "Gems", None, "Standard 300% tier — reserve 500% for flagship sales")

    if should_schedule_dice_deluxe(d):
        add("Dice Deluxe — 1×/week", "Offers & coin sale", "High", "Weekly dice promo (≤1×/week)")

    if d in PRICE_CUT and not day["sale"]:
        add("Price Cut — 20% storewide", "Offers & coin sale", "High", "Purchase promo — not a second offer")

    if (d in SHINY_SHOW_ALL_DAYS) and day["dow"] != "Mon":
        variant = shiny_show_variant or SHINY_SHOW_DAY_OVERRIDES.get(d) or SHINY_SHOW_NON_BUDGET_VARIANTS[d % len(SHINY_SHOW_NON_BUDGET_VARIANTS)]
        wolf_note = ""
        show_name = f"Shiny Show — {variant}"
        if d in SHINY_WOLF:
            show_name = f"Shiny Show — {variant} + Despicable Wolf"
            wolf_note = " · Shiny Wolf mini-game: 3–5 Shiny Cards (Collectibles — Nivi)"
        budget_note = (
            " · counts vs Nivi Shiny Limited weekly budget"
            if shiny_show_variant_uses_nivi_budget(variant)
            else " · does not consume Shiny Limited budget"
        )
        betty_note = ""
        if d in BETTY_BDAY:
            betty_note = " · Betty Boop theme (Betty's Birthday marketing 8–9/8)."
        add(
            show_name,
            "Core",
            None,
            (
                f"Variant / prizes (this day): {variant}."
                f"\nMain shiny-card source (Nivi): up to {SHINY_SHOW_MAX_PER_WEEK} special promos/week. "
                f"≤{SHINY_SHOW_MAX_PER_WEEK}×/week calendar cap{budget_note}{wolf_note}{betty_note}"
            ),
        )
        if shiny_show_variant_uses_nivi_budget(variant) and ledger:
            ledger.take(d, "Shiny Limited")

    if d in lbp_peak_days():
        peak_idx = lbp_peak_days().index(d)
        promo = LBP_PROMOS[peak_idx % len(LBP_PROMOS)]
        window = lbp_night_window(d)
        add(
            "Lotto — peak (Night Plan)",
            "Offers & coin sale",
            None,
            lotto_peak_description(window),
        )
        add(
            promo,
            "Offers & coin sale",
            None,
            lbp_promo_description(promo, window),
        )

    if d in HAMMER_DAYS and not any("hammer" in i["name"].lower() for i in items):
        add("Spin Zone — Hammers Wheel (single hammer source)", "Core", None, "1 hammer source/day")

    # Core sink — prize in the title (no parentheses); calendar UI strips (...) from labels
    st_sku = blast_title_sku(d, short_term_sku(d))

    def add_core_challenge(kind: str, *, shiny_card_prize: bool = False) -> None:
        if not can_add_gameplay_core_challenge(items):
            return
        if kind == "pyp":
            if shiny_card_prize:
                if ledger:
                    ledger.take(d, "Shiny Card")
                prize = "Shiny Card"
            else:
                prize = pyp_finish_prize(d, ledger)
            add(
                f"PYP — finish for {prize}",
                "Core",
                None,
                pyp_missions_description(d),
            )
        elif kind == "spinner":
            bi = spinner_biweek_index(d)
            if spinner_biweeks_used is not None and bi in spinner_biweeks_used:
                add_core_challenge("win_master", shiny_card_prize=shiny_card_prize)
                return
            if spinner_biweeks_used is not None:
                spinner_biweeks_used.add(bi)
            add("Spinner Clash", "Core", None, spinner_clash_description(d))
        elif kind == "ace_heist":
            if shiny_card_prize:
                if ledger:
                    ledger.take(d, "Shiny Card")
                prize = "Shiny Card"
            else:
                prize = f"{stars_ace(d)}★ Ace card"
            add(
                f"Ace Heist — {prize}",
                "Core",
                None,
                ace_heist_missions_description(d),
            )
        elif kind == "win_master":
            if shiny_card_prize:
                if ledger:
                    ledger.take(d, "Shiny Card")
                add(
                    f"Win Master — Shiny Card + {st_sku}",
                    "Core",
                    None,
                    f"Shiny MS2 countdown — Shiny Card via Win Master + {st_sku}.",
                )
            else:
                add(
                    f"Win Master — {reg}★ Reg card + {st_sku}",
                    "Core",
                    None,
                    f"Complete Win Master for {reg}★ Reg + {st_sku} (short-term SKU).",
                )
        elif kind == "spin_zone":
            prize = spin_zone_chase_prize(d)
            title = f"Spin Zone — {prize} chase"
            extra_desc = ""
            if d == 6:
                title += " + 3★ Ace topper"
                extra_desc = "\nTopper: 3★ Ace card (Nivi Ace_3 bank)."
                if ledger:
                    ledger.take(d, "Ace_3")
            add(
                title,
                "Core",
                None,
                spin_zone_core_description(d, prize) + extra_desc,
            )
        else:
            add("MES — purchase to progress", "Core", None, "MES progression (purchase).")

    # Loot 48h event — opens day 9 (Sun), still active day 10 (Mon)
    if d in LOOT_DAYS:
        if d == LOOT_START:
            add("Ace Loot — 48h (opens tonight)", "Core", None, "48h loot event: collect Ace cards via gameplay. Runs through 10/8.")
        else:
            day["notes"] = (day.get("notes") or "") + "Ace Loot 48h — last day (no extra Core row; Dash Day focus). "

    if (
        not has_real_core_challenge(items)
        and core_challenge_kind != "shiny_ms2"
        and (day["dow"] != "Mon" or d in FORCE_CORE_CHALLENGE_DAYS)
    ):
        kind = core_challenge_kind or CORE_CHALLENGE_POOL[(d + 1) % len(CORE_CHALLENGE_POOL)]
        add_core_challenge(kind)

    if d in SHINY_MS2_COUNTDOWN_LAST and not items_have_shiny_card_source(items):
        if can_add_gameplay_core_challenge(items):
            if not any((i.get("name") or "").startswith("PYP") for i in items):
                add_core_challenge("pyp", shiny_card_prize=True)
            else:
                add_core_challenge("win_master", shiny_card_prize=True)

    if (
        day_has_shiny_show_promo(items)
        and not has_coin_sink_challenge(items)
        and day["dow"] != "Mon"
        and can_add_gameplay_core_challenge(items)
    ):
        sink_kind = core_challenge_kind if core_challenge_kind not in (None, "shiny_ms2") else "win_master"
        if sink_kind == "spinner" and spinner_biweeks_used is not None and spinner_biweek_index(d) in spinner_biweeks_used:
            sink_kind = "win_master"
        add_core_challenge(sink_kind)
        items[-1]["desc"] = (
            (items[-1].get("desc") or "")
            + "\nCoin-sink Core alongside Shiny Show (gem mini-game — does not replace wager challenge)."
        )

    if d in PUZZLE_MES_TEST and not has_parallel_control_gameplay(items):
        ctrl_kind = core_challenge_kind if core_challenge_kind not in (None, "shiny_ms2") else "win_master"
        if ctrl_kind == "spinner" and d not in SPINNER_CLASH_DAYS:
            ctrl_kind = "win_master"
        if not can_add_gameplay_core_challenge(items):
            items[:] = [
                i
                for i in items
                if "sneak peek" not in (i.get("name") or "").lower()
            ]
        if can_add_gameplay_core_challenge(items):
            add_core_challenge(ctrl_kind)
            items[-1]["desc"] = (
                (items[-1].get("desc") or "")
                + f"\nControl cohort (~{100 - PUZZLE_MES_COHORT_PCT}%) — standard Core challenge (Puzzle M.E.S is ~{PUZZLE_MES_COHORT_PCT}% test only)."
            )

    ads_name, ads_desc = ads_po_for_day(d)
    add(ads_name, "ADS", None, ads_desc)

    if d == 1:
        add("Custom Pod — X1000", "Core", None, "")
    if d == 1:
        ensure_month_open_biggest_denom(day)
        day["notes"] = (day.get("notes") or "") + "Month-open biggest store denom (purchase driver, not a board promo). "
    if d == 25:
        day["notes"] += "Phase 3 / Shiny MS3 opens. "
        add("Custom Pod — Phase 3 open X1000", "Core", None, "")

    # Post-sale strong coin-drain: Custom Pod forces balance-spending on days after big sale clusters.
    if d in POST_SALE_DRAIN and not any("custom pod" in (i.get("name") or "").lower() for i in items):
        add("Custom Pod — Post-Sale Balance Drain X1200", "Core", None, "Coin-drain anchor after sale weekend — spend those fresh balances")

    if d in SPINNER_CLASH_DAYS and not any(
        re.search(r"spinner clash", i.get("name") or "", re.I) for i in items
    ):
        items[:] = [
            i
            for i in items
            if not (is_gameplay_core_challenge(i) and not is_puzzle_mes_item(i))
        ]
        add_core_challenge("spinner")

    consolidate_paired_daily_deals(items, d)
    return day


def main():
    second_offers = assign_second_offers()
    rolling_spec = assign_rolling_spec(second_offers)
    offer_pricing = assign_offer_pricing(second_offers)
    dd_keys = assign_daily_deal_keys()
    set_planned_dd_keys(dd_keys)
    shiny_variants, _ = assign_shiny_show_variants(dd_keys)
    core_kinds = assign_core_challenge_kinds()
    ledger = CardLedger()
    ledger.take(23, "Shiny Card")
    spinner_biweeks_used: set[int] = set()
    days = [
        build_day(
            d,
            second_offers.get(d),
            None,
            core_kinds.get(d),
            ledger,
            dd_keys.get(d, "gold_as"),
            shiny_variants.get(d),
            spinner_biweeks_used,
            offer_pricing.get(d),
            rolling_spec,
        )
        for d in range(1, 32)
    ]
    validation = validate_august_plan(days) + validate_card_ledger(ledger)
    all_ok = all(v[1] != "✗" for v in validation if v[0] != "טיוטה — לא הועלה ל-Monday")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps({"month": "2026-08", "source": "monthly_guidelines/2026-08.md", "days": days}, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# קלנדר אוגוסט 2026 (טיוטה לסקירה)",
        "",
        "> נבנה לפי `monthly_guidelines/2026-08.md` (מייל Nivi) + `album_cards.md` + `recurring_events.md` + `lotto_bonus.md`.",
        "> **לא הועלה ל-Monday** — לאשר לפני פרסום. **טבלת קלפים:** אומתה מול התמונה במייל (סימון במסמך הגיידליינים).",
        "",
        "## Always-On אוגוסט",
        "- **Short Term:** Blast 1-5 · Battlesheep 6-10 · SNL 11-15 · Blast 16-20 · Battlesheep 21-25 · SNL 26-31",
        f"- **Mid Term:** {mid_term_blocks_markdown()} · **Winovate** (new 5/8, 8d) · **Mega Pods** (new 3/8, Mon→Mon)",
        "- **Album:** Phase 1 (1–3/8) · Phase 2 (4–24/8) · Phase 3 (מ-25/8) · Stickers 18–22 · **Back to School 22/8**",
        "- **Feature prizes (Spinner, Short/Mid-term, Dash):** `nivi_collector_album_prizes.md`",
        "- **Clan-Dash (שבועי):** Mon Bundle+Go+Max+TLP · Tue/Fri X2 Dash · Wed X2 Badges · Thu up to 200 badges",
        "",
        "## עוגנים מיוחדים (אוגוסט)",
        "| נושא | שיבוץ |",
        "|---|---|",
        "| MGAP | 2 Matched · 5 BOGO · 9 Wild · 10 BOGO · 13 Matched · 18 BOGO · 20 Wild · 22 Bigger (sale) · 26 BOGO · 30 Slotobucks |",
        "| Rolling MFL | 3, 16, 25 (cooldown ≥10d) |",
        "| Gems Sale ×4 | 6, 13, 20, 27 |",
        "| Price Cut ×2 | 10, 24 |",
        "| Dice promo (Deluxe / BTS PM) | ≤1×/שבוע — 7, 14, 21, 22 (BTS), 29 |",
        "| Shiny Despicable Wolf ×1/שבוע | 6, 13, 20, 27 — **בתוך Shiny Show** (לא פריט נפרד) |",
        "| LBP ×2/שבוע | כל שלישי + שבת — Lotto peak + LBP promo באותו יום (Night Plan) |",
        "| Machine | **Hoppin' For Gold** — Sneak **17/8** · Launch **19/8** |",
        "| Marketing | Status Boost 1/8 · Shiny Collection 3–4,25 · Betty 8–9 · Nostalgic 14–16 |",
        "| Tests | **Puzzle M.E.S** Core 18–24/8 Soft Launch 20% · **Popup Store** 12/19/26 (TEST→LAUNCH) |",
        f"| **DD BOGO** | **{DD_BOGO_REQUIRED_PER_MONTH}×/חודש** — ימים: {', '.join(str(d) for d in sorted(DD_BOGO_DAYS))}/8 (task config) |",
        "",
        "## ולידציה (מעבר אוטומטי על התכנון)",
        "| כלל | סטטוס | פירוט |",
        "|---|---|---|",
    ]
    for rule, status, detail in validation:
        lines.append(f"| {rule} | {status} | {detail} |")
    lines.extend([
        "",
        f"**סיכום אישור טיוטה:** {'מאושר לסקירה — כל הבדיקות עברו' if all_ok else 'דורש תיקון — ראה שורות ✗/⚠ למעלה'}",
        "",
        "## יום-אחר-יום",
        "",
        "| תאריך | יום | תג | פרומואים עיקריים |",
        "|---|---|---|---|",
    ])
    for day in days:
        main_offers = " · ".join(
            i["name"][:48] + ("…" if len(i["name"]) > 48 else "")
            for i in day["items"]
            if i["status"] in ("Daily deal", "Offers & coin sale", "Buy all", "RYD", "MGAP", "Prize Mania", "Rolling offer", "Gems")
        )[:200]
        tag = day["banner"] or day["tag"] or ""
        lines.append(f"| {day['date']}/8 | {day['dow']} | {tag} | {main_offers} |")

    lines.extend([
        "",
        "## קבצים",
        f"- JSON מלא (לעריכה/ייבוא): `{OUT_JSON.relative_to(ROOT)}`",
        "- גיידליינים: `mm_calendar/monthly_guidelines/2026-08.md`",
        "",
        "**נוצר:** build_august_2026_plan.py",
    ])
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    if not all_ok:
        failed = [f"{r}: {d}" for r, s, d in validation if s != "✓" and r != "טיוטה — לא הועלה ל-Monday"]
        print("VALIDATION FAILED:", "; ".join(failed), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
