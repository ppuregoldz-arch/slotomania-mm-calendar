#!/usr/bin/env python3
"""Build canonical promo instances, variant docs, and coverage reports.

Inputs are treated as immutable. This script writes derived artifacts only.
"""
from __future__ import annotations

import collections
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MM = ROOT / "mm_calendar"
DATA = MM / "data"
INSTANCE_PATH = MM / "performance" / "instances" / "promo_instances.jsonl"
PERF_ROOT = MM / "performance"
CALC_DATE = dt.date.today().isoformat()
SCHEMA_VERSION = "1.0"

FAMILY_NAMES = {
    "daily-deal": "Daily Deal",
    "rolling-offer": "Rolling Offer",
    "mgap": "MGAP",
    "buy-all": "Buy All",
    "decoy-bonanza": "Decoy / Bonanza",
    "ryd": "Reveal Your Deal",
    "coin-sale": "Coin Sale",
    "prize-mania": "Prize Mania",
    "counter-po": "Counter PO",
    "payment-offer": "Payment Offer",
    "gems-sale": "Gems Sale",
    "boosted-gemback": "Boosted Gemback",
    "ggs": "GGS",
    "extreme-stamp": "Extreme Stamp",
    "happy-hour": "Happy Hour / Jumbo",
    "golden-spin": "Golden Spin",
    "core": "Core",
    "clan-dash": "Clan-Dash",
    "shiny-show": "Shiny Show",
    "winovate": "Winovate",
    "short-term-season": "Short-Term Season",
    "mid-term-season": "Mid-Term Season",
    "album": "Album",
    "lotto-lbp": "Lotto / LBP",
    "ads": "ADS",
    "event": "Event",
    "slotobucks": "SlotoBucks",
    "other": "Other",
    "unclassified": "Unclassified",
}

FAMILY_KPI = {
    "daily-deal": "revenue",
    "rolling-offer": "revenue",
    "mgap": "revenue",
    "buy-all": "revenue",
    "decoy-bonanza": "revenue",
    "ryd": "revenue",
    "coin-sale": "revenue",
    "prize-mania": "paying_users",
    "counter-po": "revenue",
    "payment-offer": "revenue",
    "gems-sale": "revenue",
    "boosted-gemback": "gem_usage",
    "ggs": "gem_usage",
    "extreme-stamp": "revenue",
    "happy-hour": "revenue",
    "golden-spin": "revenue",
    "core": "wager",
    "clan-dash": "paying_users",
    "shiny-show": "gem_usage",
    "winovate": "gem_usage",
}

KNOWN_VARIANT_EVIDENCE = {
    "shiny-show--joker-different-prizes": ("gem_usage", 89.0, 4, "shiny_show_performance.md", "Shiny mini-game usage versus Play-X baseline"),
    "shiny-show--wild-guaranteed": ("gem_usage", 71.0, 1, "shiny_show_performance.md", "Shiny mini-game usage versus Play-X baseline"),
    "shiny-show--all-cards-joker": ("gem_usage", 57.0, 5, "shiny_show_performance.md", "Shiny mini-game usage versus Play-X baseline"),
    "shiny-show--all-cards": ("gem_usage", 54.0, 5, "shiny_show_performance.md", "Shiny mini-game usage versus Play-X baseline"),
    "shiny-show--different-prizes": ("gem_usage", 38.0, 7, "shiny_show_performance.md", "Shiny mini-game usage versus Play-X baseline"),
    "shiny-show--crazy-with-aces": ("gem_usage", -2.0, 5, "shiny_show_performance.md", "Shiny mini-game usage versus Play-X baseline"),
    "core--spin-zone": ("wager", 4.1, 5, "core_wager_analysis.md", "June all-user median wager uplift; day-level correlation"),
    "core--pyp": ("wager", 3.0, 5, "core_wager_analysis.md", "June all-user median wager uplift; day-level correlation"),
    "core--win-master": ("wager", -6.7, 4, "core_wager_analysis.md", "June all-user median wager uplift; day-level correlation"),
    "core--mes": ("wager", -8.8, 3, "core_wager_analysis.md", "June all-user median wager uplift; heavily timing-confounded"),
    "rolling-offer--buy-more-for-less": ("revenue", None, 4, "promo_revenue_analysis.md", "Product revenue proxy ~$131.7K/day on solo days; not lift"),
    "rolling-offer--supersized": ("revenue", None, 2, "promo_revenue_analysis.md", "Product revenue proxy ~$73.7K/day on solo days; not lift"),
    "daily-deal--hammers": ("revenue", None, 21, "promo_revenue_analysis.md", "Sticky Bundle proxy ~$132.5K/day on solo days; not total DD lift"),
    "mgap--bigger": ("revenue", None, 3, "promo_revenue_analysis.md", "Product revenue proxy ~$235.4K/day; conflicts with clean standalone family lift"),
}

SELECTIVE_DWH_EVIDENCE = {
    "daily-deal--hammers": (38, 646142, 644379, 0.27, 27576, 27601, -0.09),
    "extreme-stamp--standard": (23, 673185, 625061, 7.70, 26574, 26242, 1.26),
    "golden-spin--standard": (11, 588900, 621998, -5.32, 25400, 25932, -2.05),
    "mgap--bigger": (12, 684444, 659252, 3.82, 28281, 27790, 1.77),
}

HOLIDAY_DATES_USED = {"2026-04-04", "2026-05-05", "2026-05-25", "2026-07-04"}


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def slug(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"\b20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}\b", " ", value)
    value = re.sub(r"\b\d{1,2}[-/.]\d{1,2}\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def norm(value: str) -> str:
    value = value.lower()
    value = re.sub(r"\b20\d{2}-\d{2}-\d{2}\b", "", value)
    return re.sub(r"\s+", " ", value).strip()


def contains(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.I))


def classify_family(status: str, name: str) -> str:
    s, n = status.lower().strip(), name.lower()
    if contains(n, r"\bdaily deal\b|\bdd\b.*bogo|dpu promo.*daily deal"):
        return "daily-deal"
    if "shiny show" in n or "growing shiny" in n or "shiny wolf" in n:
        return "shiny-show"
    if "winovate" in n:
        return "winovate"
    if "golden spin" in n:
        return "golden-spin"
    if "coin sale" in n or "coins sale" in n:
        return "coin-sale"
    if "boosted gemback" in n or ("gemback" in n and s == "gems"):
        return "boosted-gemback"
    if contains(n, r"\bx2\s*ggs\b|gold gem stamp") or (s == "gems" and "ggs" in n):
        return "ggs"
    if "extreme stamp" in n or s == "extreme stamp":
        return "extreme-stamp"
    if contains(n, r"happy hour|jumbo|prize picker|fortune dip"):
        return "happy-hour"
    if contains(n, r"lotto|\blbp\b|l\.b\.p"):
        return "lotto-lbp"
    if contains(n, r"decoy|bonanza|triple offer"):
        return "decoy-bonanza"
    if contains(n, r"custom pod|spin zone|pick your path|\bpyp\b|win master|spinner clash|ace.*loot|card.*loot|\bm\.?e\.?s\b|mega winner|jackpot"):
        return "core"
    if contains(n, r"dpu po|make any purchase|payment page"):
        return "payment-offer"
    by_status = {
        "daily deal": "daily-deal",
        "rolling offer": "rolling-offer",
        "mgap": "mgap",
        "buy all": "buy-all",
        "ryd": "ryd",
        "prize mania": "prize-mania",
        "counter po": "counter-po",
        "gems": "gems-sale",
        "core": "core",
        "clan-dash": "clan-dash",
        "short term": "short-term-season",
        "mid term": "mid-term-season",
        "album": "album",
        "ads": "ads",
        "event": "event",
        "slotobucks": "slotobucks",
        "offers & coin sale": "other",
        "black diamond": "event",
    }
    return by_status.get(s, "unclassified")


def classify_variant(family: str, name: str, desc: str) -> tuple[str, str]:
    text = f"{name} {desc}".lower()
    key = "other"
    if family == "daily-deal":
        checks = [
            ("bogo", r"\bbogo\b|buy\s*1\s*get\s*1"),
            ("hammers", r"hammer"),
            ("sb-wheel", r"sb wheel|bucks wheel|100%\s*sb"),
            ("wild-supreme", r"wild supreme"),
            ("wild-any", r"wild any"),
            ("clan-pack", r"clan pack"),
            ("superboom", r"super\s*boom|superboom"),
            ("parasheep-airstrike", r"parasheep|air\s*strike|\bairstrike\b"),
            ("cards", r"\b[3-5]\s*\*|\b[3-5]★|card|wild|gold|ace|shiny"),
        ]
    elif family == "rolling-offer":
        checks = [
            ("buy-more-for-less", r"more.?for.?less|buy more"),
            ("supersized", r"supersiz"),
            ("buy-1-get-8", r"buy\s*1\s*get\s*8"),
            ("bxgy-6-cycles", r"6\s*cycles?"),
            ("bxgy-5-cycles", r"5\s*cycles?"),
            ("bxgy-other", r"rolling|buy.*get"),
        ]
    elif family == "mgap":
        checks = [
            ("bogo", r"\bbogo\b|buy\s*one|buy\s*1"),
            ("bigger", r"bigger"),
            ("matched", r"match"),
            ("wild-symbols", r"wild symbol"),
        ]
    elif family == "shiny-show":
        checks = [
            ("all-cards-joker", r"all cards.*joker|joker.*all cards"),
            ("joker-different-prizes", r"joker.*different prizes|different prizes.*joker"),
            ("wild-guaranteed", r"wild.*guaranteed|win a wild"),
            ("all-cards", r"all cards"),
            ("crazy-with-aces", r"crazy.*aces"),
            ("different-prizes", r"different prizes"),
            ("growing", r"growing"),
            ("find-the-flower", r"find the flower|betty"),
            ("finish-sticker", r"finish sticker"),
        ]
    elif family == "core":
        checks = [
            ("spin-zone", r"spin zone"),
            ("pyp", r"pick your path|\bpyp\b"),
            ("win-master", r"win master"),
            ("spinner-clash", r"spinner clash"),
            ("custom-pod", r"custom pod"),
            ("ace-card-loot", r"ace.*loot|card.*loot"),
            ("mega-winner", r"mega winner"),
            ("jackpot", r"jackpot|\bjp\b"),
            ("mes", r"\bm\.?e\.?s\b|\bmes\b"),
        ]
    elif family == "ryd":
        checks = [("wild-gold", r"wild gold"), ("100-sb", r"100%\s*sb"), ("150-sb", r"15[05]%\s*sb")]
    elif family == "buy-all":
        checks = [("wild", r"wild"), ("coins", r"coin"), ("mystery", r"mystery")]
    elif family == "gems-sale":
        checks = [("sale", r"sale|%"), ("machine", r"machine")]
    else:
        checks = []
    for candidate, pattern in checks:
        if contains(text, pattern):
            key = candidate
            break
    if key == "other" and family in {
        "coin-sale", "prize-mania", "counter-po", "payment-offer", "boosted-gemback",
        "ggs", "extreme-stamp", "happy-hour", "golden-spin", "clan-dash", "winovate",
        "album", "ads", "event", "slotobucks", "short-term-season", "mid-term-season",
    }:
        key = "standard"
    return f"{family}--{key}", key.replace("-", " ").title()


def segment_from(text: str) -> str:
    t = text.lower()
    found = []
    for token, out in [
        ("black diamond", "black-diamond"), ("dormant", "dormant"), ("finish", "finishers"),
        ("dpu", "dpu"), ("npu", "npu"), ("active pu", "pu"), (" pu ", "pu"), (" ic ", "ic"),
    ]:
        if token in f" {t} ":
            found.append(out)
    return found[0] if len(set(found)) == 1 else ("mixed" if found else "unknown")


def pricing_from(value: str) -> str:
    s = value.strip().lower()
    return {"m": "medium", "mid": "medium", "medium": "medium", "h": "high", "high": "high", "max": "max", "maximum": "max", "low": "low", "": "none"}.get(s, "unknown")


def explicit_rewards(text: str) -> list[dict]:
    patterns = {
        "hammers": r"\b\d+\s*hammers?\b|\bhammers?\b",
        "rds": r"\b\d+\s*rds\b|\brds\b",
        "ggs": r"\b\d+\s*ggs\b|\bggs\b",
        "slotobucks": r"\b\d+%\s*(?:sb|slotobucks)\b",
        "card": r"\b[1-5]\s*(?:\*|★)\s*(?:reg|gold|ace)\b|wild (?:any|gold|ordinary|supreme)|shiny (?:card|limited)",
        "gems": r"\bgems?\b",
        "coins": r"\bcoins?\b",
        "picks": r"\b\d+\s*picks?\b",
        "parasheep": r"\b\d*\s*parasheep\b",
        "airstrike": r"\bair\s*strike\b|\bairstrike\b",
        "superboom": r"\bsuper\s*boom\b|\bsuperboom\b",
        "dice": r"\b\d*\s*(?:snl )?dice\b",
    }
    out = []
    for kind, pattern in patterns.items():
        matches = [m.group(0).strip() for m in re.finditer(pattern, text, re.I)]
        if matches:
            out.append({"type": kind, "source_text": matches[:10]})
    return out


def timeline_end(monday: dict | None, start: str) -> str:
    if not monday:
        return start
    candidates = re.findall(r"\d{4}-\d{2}-\d{2}", monday.get("timeline") or "")
    return candidates[-1] if candidates else monday.get("iso_end") or start


def build_records() -> list[dict]:
    months = load("real_months.json")
    monday_raw = load("monday_pull_last_3mo.json")
    outcomes_raw = load("wide_revenue_pu.json")
    outcome_days = outcomes_raw.get("days", {})

    monday_by_key: dict[tuple[str, str, str], collections.deque] = collections.defaultdict(collections.deque)
    for row in monday_raw.get("items", []):
        key = (row.get("iso") or row.get("date") or "", norm(row.get("name") or ""), (row.get("product") or "").lower())
        monday_by_key[key].append(row)

    staged = []
    for month, days in months.items():
        for day in days:
            for source_group, entries in (("season", day.get("seasons", [])), ("item", day.get("items", []))):
                for ordinal, entry in enumerate(entries):
                    if entry.get("backup"):
                        continue
                    staged.append((month, day, source_group, ordinal, entry))

    skeletons = []
    family_variant_by_day: dict[str, set[str]] = collections.defaultdict(set)
    for month, day, source_group, ordinal, entry in staged:
        name = (entry.get("name") or "").strip()
        status = (entry.get("status") or "").strip()
        desc = (entry.get("desc") or "").strip()
        iso = day["iso"]
        family = classify_family(status, name)
        variant_id, variant_name = classify_variant(family, name, desc)
        monday_key = (iso, norm(name), status.lower())
        monday = monday_by_key[monday_key].popleft() if monday_by_key[monday_key] else None
        stable = f"monday-{monday['id']}" if monday and monday.get("id") else None
        if not stable:
            seed = json.dumps([family, variant_id, iso, status, name, desc, ordinal], ensure_ascii=False)
            stable = "derived-" + hashlib.sha256(seed.encode()).hexdigest()[:12]
        instance_id = f"{variant_id}--{iso}--{stable}"
        skeletons.append((instance_id, family, variant_id, variant_name, day, entry, monday, source_group))
        family_variant_by_day[iso].add(variant_id)

    records = []
    for instance_id, family, variant_id, variant_name, day, entry, monday, source_group in skeletons:
        iso = day["iso"]
        name, desc, status = entry.get("name") or "", entry.get("desc") or "", entry.get("status") or ""
        end_date = timeline_end(monday, iso)
        text = f"{name} {desc}"
        day_type = []
        if day.get("sale"):
            day_type.append("sale")
        if day.get("tag") == "event":
            day_type.extend(["event", "holiday"])
        if day.get("tag") == "machine":
            day_type.append("machine-launch")
        if day.get("dow") == "Mon":
            day_type.append("dash-day")
        if int(iso[-2:]) <= 7:
            day_type.append("month-start")
        if int(iso[-2:]) >= 25:
            day_type.append("month-end")
        if "album" in text.lower() and contains(text, r"last|end|finish"):
            day_type.append("album-end")
        if not day_type:
            day_type = ["normal"]
        placement = "night-plan" if "night plan" in text.lower() else ("multi-day" if end_date != iso else "unknown")
        outcome = outcome_days.get(iso, {})
        actual = {}
        source_refs = [{
            "source_type": "derived-calendar",
            "path_or_table": "mm_calendar/data/real_months.json",
            "source_id": None,
            "pulled_at": None,
            "fields_used": ["name", "status", "pricing", "description", "date", "day context"],
        }]
        if monday:
            source_refs.append({
                "source_type": "monday-export",
                "path_or_table": "mm_calendar/data/monday_pull_last_3mo.json",
                "source_id": monday.get("id"),
                "pulled_at": monday_raw.get("pulled"),
                "fields_used": ["name", "product", "date", "timeline", "description", "pricing"],
            })
        if outcome.get("rev") is not None:
            actual["revenue"] = {
                "value": outcome["rev"], "unit": "usd_per_day", "scope": "whole_day",
                "attribution": "not_attributed", "source": "mm_calendar/data/wide_revenue_pu.json",
                "source_date": outcomes_raw.get("_pulled_at"), "calculation_date": None,
                "baseline_method": None, "validation_status": "dwh-snapshot",
                "confidence": "high", "evidence_type": "observed-result",
            }
        if outcome.get("pu") is not None:
            actual["paying_users"] = {
                "value": outcome["pu"], "unit": "users_per_day", "scope": "whole_day",
                "attribution": "not_attributed", "source": "mm_calendar/data/wide_revenue_pu.json",
                "source_date": outcomes_raw.get("_pulled_at"), "calculation_date": None,
                "baseline_method": None, "validation_status": "dwh-snapshot",
                "confidence": "high", "evidence_type": "observed-result",
            }
        if actual:
            source_refs.append({
                "source_type": "dwh-snapshot",
                "path_or_table": "mm_calendar/data/wide_revenue_pu.json",
                "source_id": iso,
                "pulled_at": outcomes_raw.get("_pulled_at"),
                "fields_used": sorted(actual),
            })
        concurrent = sorted(family_variant_by_day[iso] - {variant_id})
        confounders = []
        if concurrent:
            confounders.append("concurrent-promotions")
        if "holiday" in day_type or "event" in day_type:
            confounders.append("holiday-event")
        if "album-end" in day_type:
            confounders.append("album-timing")
        if "dash-day" in day_type:
            confounders.append("dash-day")
        confounders.extend(["weekday-placement", "missing-control"])
        check = day.get("smartCalendarCheck") or {}
        if check.get("status") == "mismatch":
            confounders.append("source-mismatch")
        if not actual:
            confounders.append("future-or-incomplete-day")
        kpi = FAMILY_KPI.get(family)
        result_confidence = "high" if actual else "insufficient"
        validation = "dwh-snapshot" if actual else "source-only"
        records.append({
            "schema_version": SCHEMA_VERSION,
            "instance_id": instance_id,
            "logical_promo_group_id": None,
            "family_id": family,
            "family_name": FAMILY_NAMES[family],
            "variant_id": variant_id,
            "variant_name": variant_name,
            "promo_name": name,
            "start_date": iso,
            "end_date": end_date,
            "duration_hours": None,
            "target_audience": [],
            "segment": segment_from(text),
            "day_type": sorted(set(day_type)),
            "placement": placement,
            "pricing": pricing_from(entry.get("pricing") or (monday or {}).get("pricing") or ""),
            "mechanic": None,
            "rewards": explicit_rewards(text),
            "main_kpi": kpi,
            "main_kpi_level": "family-default" if kpi else "unassigned",
            "main_kpi_override": None,
            "secondary_kpis": [],
            "actual_results": actual,
            "baseline": None,
            "lift_vs_baseline": None,
            "nominal_volume": {},
            "concurrent_promotions": concurrent,
            "known_confounders": sorted(set(confounders)),
            "result_confidence": result_confidence,
            "evidence_type": "observed-result" if actual else "insufficient-evidence",
            "validation_status": validation,
            "what_worked": [],
            "what_did_not_work": [],
            "reuse_recommendation": "insufficient-evidence",
            "best_timing": [],
            "source_refs": source_refs,
            "calculation_date": None,
            "notes": [f"Source group: {source_group}", "Whole-day outcomes are not attributed to this promo."],
        })
    records.sort(key=lambda r: (r["start_date"], r["family_id"], r["variant_id"], r["instance_id"]))
    return records


def dow_baselines(outcomes: dict[str, dict]) -> dict[str, dict[str, float]]:
    grouped = collections.defaultdict(lambda: collections.defaultdict(list))
    for iso, row in outcomes.items():
        if not iso.startswith("2026-") or not ("2026-04-01" <= iso <= "2026-07-05") or iso in HOLIDAY_DATES_USED:
            continue
        dow = dt.date.fromisoformat(iso).strftime("%a")
        for k in ("rev", "pu"):
            if row.get(k) is not None:
                grouped[dow][k].append(float(row[k]))
    return {dow: {k: sum(v) / len(v) for k, v in cols.items()} for dow, cols in grouped.items()}


def write_variant_docs(records: list[dict]) -> None:
    outcomes = load("wide_revenue_pu.json").get("days", {})
    baselines = dow_baselines(outcomes)
    by_variant = collections.defaultdict(list)
    for row in records:
        by_variant[row["variant_id"]].append(row)
    index_rows = []
    for variant_id, rows in sorted(by_variant.items()):
        family = rows[0]["family_id"]
        kpi = rows[0]["main_kpi"] or "unassigned"
        dates = sorted({r["start_date"] for r in rows})
        completed = [d for d in dates if d in outcomes]
        rev_actual, rev_expected, pu_actual, pu_expected = [], [], [], []
        for iso in completed:
            dow = dt.date.fromisoformat(iso).strftime("%a")
            if outcomes[iso].get("rev") is not None and baselines.get(dow, {}).get("rev"):
                rev_actual.append(float(outcomes[iso]["rev"]))
                rev_expected.append(baselines[dow]["rev"])
            if outcomes[iso].get("pu") is not None and baselines.get(dow, {}).get("pu"):
                pu_actual.append(float(outcomes[iso]["pu"]))
                pu_expected.append(baselines[dow]["pu"])
        def impact(actual, expected):
            if not actual:
                return None
            a, b = sum(actual) / len(actual), sum(expected) / len(expected)
            return {"n": len(actual), "actual": a, "baseline": b, "delta": a - b, "pct": (a / b - 1) * 100 if b else None}
        rev, pu = impact(rev_actual, rev_expected), impact(pu_actual, pu_expected)
        out_dir = PERF_ROOT / "by_kpi" / kpi
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{variant_id}.md"
        source_links = sorted({ref["path_or_table"] for r in rows for ref in r["source_refs"]})
        lines = [
            f"# {rows[0]['family_name']} — {rows[0]['variant_name']}",
            "",
            f"- **Variant ID:** `{variant_id}`",
            f"- **Family:** `{family}`",
            f"- **Default Main KPI:** `{rows[0]['main_kpi'] or 'unassigned'}`",
            f"- **Instances:** {len(rows)} rows across {len(dates)} dates ({dates[0]} to {dates[-1]})",
            f"- **Completed dates with daily outcomes:** {len(completed)}",
            "",
            "## Measured daily context",
            "",
            "The values below are whole-day, same-weekday comparisons. They are correlations with all concurrent promotions, not attributed promo lift.",
            "",
            "| KPI | n dates | Mean observed | DOW-matched baseline | Nominal difference | Difference | Evidence | Confidence |",
            "|---|---:|---:|---:|---:|---:|---|---|",
        ]
        if rev:
            lines.append(f"| Revenue | {rev['n']} | ${rev['actual']:,.0f} | ${rev['baseline']:,.0f} | ${rev['delta']:+,.0f} | {rev['pct']:+.1f}% | correlation | low |")
        else:
            lines.append("| Revenue | 0 | — | — | — | — | insufficient evidence | insufficient |")
        if pu:
            lines.append(f"| Paying users | {pu['n']} | {pu['actual']:,.0f} | {pu['baseline']:,.0f} | {pu['delta']:+,.0f} | {pu['pct']:+.1f}% | correlation | low |")
        else:
            lines.append("| Paying users | 0 | — | — | — | — | insufficient evidence | insufficient |")
        known = KNOWN_VARIANT_EVIDENCE.get(variant_id)
        lines.extend(["", "## KPI-specific historical evidence", ""])
        if known:
            kkpi, pct, n, source, note = known
            result = f"{pct:+.1f}% vs documented baseline" if pct is not None else "Nominal product proxy only; see source"
            lines.extend([
                f"- **KPI:** `{kkpi}`",
                f"- **Result:** {result}",
                f"- **Sample:** n={n}",
                f"- **Source:** `{source}`",
                f"- **Interpretation:** {note}.",
                "- **Evidence label:** correlation",
                "- **Confidence:** low unless the source explicitly documents stronger controls.",
            ])
        else:
            lines.append("No reproducible variant-specific KPI result is available. This is registered as missing evidence; do not infer one.")
        selective = SELECTIVE_DWH_EVIDENCE.get(variant_id)
        if selective:
            n, rev_avg, rev_base, rev_pct, pu_avg, pu_base, pu_pct = selective
            lines.extend([
                "",
                "## Selective DWH validation",
                "",
                f"- **Window:** 2026-04-01–2026-07-05; n={n} distinct Smart Calendar start dates.",
                f"- **Revenue:** ${rev_avg:,.0f} vs ${rev_base:,.0f} same-weekday baseline ({rev_pct:+.2f}%).",
                f"- **Paying users:** {pu_avg:,.0f} vs {pu_base:,.0f} same-weekday baseline ({pu_pct:+.2f}%).",
                "- **Evidence:** whole-day correlation; low confidence; not attributed lift.",
                "- **Source:** `measurement/SELECTIVE_DWH_VALIDATION_2026-07-10.md`.",
            ])
        lines.extend([
            "",
            "## Context and confounders",
            "",
            f"- Concurrent promotion present on {sum(bool(r['concurrent_promotions']) for r in rows)}/{len(rows)} instance rows.",
            f"- Segments observed: {', '.join(sorted({r['segment'] for r in rows}))}.",
            f"- Pricing observed: {', '.join(sorted({r['pricing'] for r in rows}))}.",
            "- Holiday set used for the local DOW comparison: 2026-04-04, 2026-05-05, 2026-05-25, 2026-07-04.",
            "- The holiday-list conflict remains registered; changing it may change the comparison.",
            "",
            "## Reuse recommendation",
            "",
            "**Insufficient evidence for a confirmed recommendation.** Use only with the family rules and current monthly constraints; consult the prediction framework for eligibility.",
            "",
            "## Provenance",
            "",
        ])
        lines.extend(f"- `{src}`" for src in source_links)
        lines.extend([
            f"- Calculation date: {CALC_DATE}",
            "- Baseline method: mean daily outcome for the same weekday in Apr 1–Jul 5, excluding the four dates listed above.",
            "",
            "## Instance dates",
            "",
            ", ".join(dates),
            "",
        ])
        path.write_text("\n".join(lines), encoding="utf-8")
        index_rows.append((kpi, rows[0]["family_name"], rows[0]["variant_name"], variant_id, len(rows), len(completed), path.relative_to(PERF_ROOT).as_posix()))

    lines = [
        "# Promotion Performance Index",
        "",
        f"**Generated:** {CALC_DATE}",
        "",
        "Canonical instance data: `instances/promo_instances.jsonl`.",
        "All local DOW comparisons are observational and low confidence; variant-specific evidence retains its original source limitations.",
        "",
        "| Main KPI | Family | Variant | Instances | Completed dates | Document |",
        "|---|---|---|---:|---:|---|",
    ]
    for kpi, family, variant, vid, count, completed, rel in index_rows:
        lines.append(f"| {kpi} | {family} | {variant} | {count} | {completed} | [{vid}]({rel}) |")
    (PERF_ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_coverage(records: list[dict]) -> None:
    by_month = collections.Counter(r["start_date"][:7] for r in records)
    by_kpi = collections.Counter(r["main_kpi"] or "unassigned" for r in records)
    by_family = collections.Counter(r["family_id"] for r in records)
    by_variant = collections.Counter(r["variant_id"] for r in records)
    completed = sum(bool(r["actual_results"]) for r in records)
    monday = sum(any(s["source_type"] == "monday-export" for s in r["source_refs"]) for r in records)
    lines = [
        "# Promotion Knowledge Coverage",
        "",
        f"**Generated:** {CALC_DATE}",
        "",
        f"- Total instance rows: {len(records)}",
        f"- Rows with at least one complete daily outcome: {completed} ({completed/len(records):.1%})",
        f"- Rows matched to stable Monday export IDs: {monday} ({monday/len(records):.1%})",
        f"- Unique families: {len(by_family)}",
        f"- Unique variants: {len(by_variant)}",
        "",
        "## By month",
        "",
        "| Month | Instances |",
        "|---|---:|",
    ]
    lines.extend(f"| {k} | {v} |" for k, v in sorted(by_month.items()))
    lines.extend(["", "## By Main KPI", "", "| KPI | Instances |", "|---|---:|"])
    lines.extend(f"| {k} | {v} |" for k, v in sorted(by_kpi.items()))
    lines.extend(["", "## By family", "", "| Family | Instances |", "|---|---:|"])
    lines.extend(f"| {k} | {v} |" for k, v in sorted(by_family.items()))
    lines.extend(["", "## By variant", "", "| Variant | Instances |", "|---|---:|"])
    lines.extend(f"| {k} | {v} |" for k, v in sorted(by_variant.items()))
    (PERF_ROOT / "COVERAGE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    records = build_records()
    INSTANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INSTANCE_PATH.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    write_variant_docs(records)
    write_coverage(records)
    print(f"Wrote {len(records)} instances to {INSTANCE_PATH}")


if __name__ == "__main__":
    main()
