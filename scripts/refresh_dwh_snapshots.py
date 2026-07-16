#!/usr/bin/env python3
"""Refresh local DWH snapshots used by the MM dashboard.

This script is intentionally standalone so launchd can run the daily dashboard
pipeline without relying on Cursor/MCP tool calls. It reads the existing MCP DB
configuration, pulls DWH data up to yesterday (or the latest date available in
the tables), and rewrites the JSON caches consumed by pull_real_months.py and
calibrate_model.py.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import warnings
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MCP_CONFIG = ROOT / ".cursor" / "mcp.json"
DATA = ROOT / "mm_calendar" / "data"

WIDE_REVENUE_PU = DATA / "wide_revenue_pu.json"
WIDE_PROMO_KEYS = DATA / "wide_promo_keys.json"
PU_BALANCE = DATA / "pu_balance_raw.json"
SINK_KEYS = DATA / "sink_mechanic_keys.json"

WIDE_START = dt.date(2025, 11, 1)
ECON_START = dt.date(2026, 4, 1)

PROMO_PATTERNS = {
    "customPod": r"custom pod",
    "coinSale": r"coins? sale",
    "decoyBonanza": r"decoy|bonanza",
    "mgapBogo": r"mgap.*bogo|bogo.*mgap",
    "mgapMatched": r"mgap.*matched",
    "mgapWildSymbols": r"mgap.*wild symbol",
    "mgapBigger": r"mgap.*bigger",
    "gemback": r"gemback",
    "rollingMoreForLess": r"more.?for.?less|buy.?more",
    "rolling": r"rolling",
    "prizeMania": r"prize mania",
    "priceCut": r"price cut",
    "buyAll": r"buy all|mystery buy all",
    "goldenSpin": r"golden spin",
    "counterPo": r"counter po|limited po",
    "snl": r"\bsnl\b",
    "happyHour": r"happy hour|jumbo giveaway|jumbo|prize picker|eyes on|fortune dip",
    "extremeStamp": r"extreme stamp",
    "fortuneDip": r"fortune dip",
    "ryd": r"\bryd\b|reveal your deal",
}

SINK_PATTERNS = {
    "pyp": r"\bpyp\b|pick your path",
    "mesTokens": r"\bm\.?e\.?s\b|mes tokens?|mes steps?",
    "spinnerClash": r"spinner clash",
    "aceCardLoot": r"ace.*loot|card.*loot|loot.*ace|loot.*card",
    "customPod": r"custom pod",
    "clanPoints": r"clan points?|badges?",
    "dashChallenge": r"daily dash|superdash|dash challenge|complete .*dash",
    "machine": r"machine launch|new machine|full launch|trigger free spin|free spins",
    "winMaster": r"win master",
    "spinZone": r"spin zone",
    "jackpot": r"jackpot|\bjp\b",
    "megaWinner": r"mega winner",
    "shinyShow": r"shiny show|growing shiny|shiny wolf",
    "sneakPeek": r"sneak peek",
}


def load_db_url() -> str:
    cfg = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    servers = cfg.get("mcpServers", {})
    for server in servers.values():
        env = server.get("env", {})
        db_url = env.get("DB_URL", "")
        if db_url.startswith("vertica+vertica_python://") and "playtika_dwh" in db_url:
            return db_url
    raise RuntimeError(f"No Vertica DB_URL found in {MCP_CONFIG}")


def engine_from_config():
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SAWarning
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing Python DB dependencies. Install once with: "
            "python3 -m pip install --user sqlalchemy vertica-python"
        ) from exc

    cfg = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    db_url = load_db_url()
    warnings.filterwarnings("ignore", category=SAWarning, message="Dialect vertica:vertica_python.*")
    engine_options = {}
    for server in cfg.get("mcpServers", {}).values():
        env = server.get("env", {})
        if env.get("DB_URL") == db_url and env.get("DB_ENGINE_OPTIONS"):
            engine_options = json.loads(env["DB_ENGINE_OPTIONS"])
            break
    engine_options.setdefault("pool_reset_on_return", None)
    return create_engine(db_url, **engine_options), text


def rows(conn, text, query: str, params: dict):
    result = conn.execute(text(query), params)
    return [dict(row._mapping) for row in result]


def iso_date(value) -> str:
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    return str(value)[:10]


def daterange(start: dt.date, end: dt.date):
    cur = start
    while cur <= end:
        yield cur
        cur += dt.timedelta(days=1)


def classify_keys(name: str, patterns: dict[str, str]) -> set[str]:
    s = (name or "").lower()
    keys = set()
    mgap_seen = "mgap" in s
    for key, pattern in patterns.items():
        if key.startswith("mgap"):
            continue
        if re.search(pattern, s):
            keys.add(key)
    if mgap_seen and "mgapBogo" in patterns:
        if re.search(patterns["mgapBogo"], s):
            keys.add("mgapBogo")
        elif re.search(patterns["mgapMatched"], s):
            keys.add("mgapMatched")
        elif re.search(patterns["mgapWildSymbols"], s):
            keys.add("mgapWildSymbols")
        elif re.search(patterns["mgapBigger"], s):
            keys.add("mgapBigger")
        else:
            keys.add("mgapOther")
    return keys


def normalize_ts(value) -> dt.datetime:
    if isinstance(value, dt.datetime):
        return value.replace(tzinfo=None)
    s = str(value).replace("T", " ").split(".")[0]
    return dt.datetime.fromisoformat(s)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")
    print(f"Wrote {path}")


def refresh_wide_revenue_pu(conn, text, pulled_at: str):
    q = """
    SELECT
      calc_date,
      ROUND(SUM(daily_Net_revenue), 0) AS rev,
      COUNT(DISTINCT CASE WHEN daily_payments > 0 THEN user_id END) AS pu
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date >= :start_date
      AND calc_date < CURRENT_DATE
      AND user_id > 0
    GROUP BY calc_date
    ORDER BY calc_date
    """
    data = {}
    for r in rows(conn, text, q, {"start_date": WIDE_START.isoformat()}):
        data[iso_date(r["calc_date"])] = {"rev": int(round(float(r["rev"] or 0))), "pu": int(r["pu"] or 0)}
    if not data:
        raise RuntimeError("wide_revenue_pu query returned no rows")
    write_json(WIDE_REVENUE_PU, {
        "_source": "agg.agg_sm_daily_users_stats — SUM(daily_Net_revenue), COUNT(DISTINCT user_id WHERE daily_payments>0). Auto-refreshed by scripts/refresh_dwh_snapshots.py.",
        "_pulled_at": pulled_at,
        "_range": [min(data), max(data)],
        "days": data,
    })


def latest_promos(conn, text, start: dt.date, end: dt.date):
    q = """
    SELECT promo_id, promo_name, promo_desc, start_date, end_date, status, is_main, category_id
    FROM (
      SELECT
        promo_id,
        promo_name,
        promo_desc,
        start_date,
        end_date,
        status,
        is_main,
        category_id,
        ROW_NUMBER() OVER (PARTITION BY promo_id ORDER BY update_ts DESC, insert_id DESC) AS rn
      FROM dwh.sm_fact_smart_calendar_promotion_updates
      WHERE end_date >= :start_date
        AND start_date < :end_date
    ) t
    WHERE rn = 1
      AND status NOT ILIKE '%cancel%'
      AND promo_name NOT ILIKE '%cancel%'
      AND promo_name NOT ILIKE '%Operation - Daily View%'
    """
    return rows(conn, text, q, {"start_date": (start - dt.timedelta(days=10)).isoformat(), "end_date": (end + dt.timedelta(days=3)).isoformat()})


def refresh_key_file(conn, text, path: Path, start: dt.date, end: dt.date, patterns: dict[str, str], source: str, extra: dict | None = None):
    promos = latest_promos(conn, text, start, end)
    day_keys: dict[str, str] = {}
    for day in daterange(start, end):
        snapshot = dt.datetime.combine(day, dt.time(11, 0))
        keys = set()
        for p in promos:
            if normalize_ts(p["start_date"]) <= snapshot < normalize_ts(p["end_date"]):
                keys.update(classify_keys(p["promo_name"], patterns))
        if keys:
            day_keys[day.isoformat()] = ",".join(sorted(keys))
    payload = {
        "_source": source,
        "_pulled_at": dt.date.today().isoformat(),
        "_range": [start.isoformat(), end.isoformat()],
        "days": day_keys,
    }
    if extra:
        payload.update(extra)
    write_json(path, payload)


def refresh_pu_balance(conn, text, pulled_at: str):
    q = """
    SELECT DISTINCT
      COUNT(*) OVER () AS n_pu,
      MEDIAN(coins_start_day_balance) OVER () AS coin_s,
      MEDIAN(coins_end_day_balance) OVER () AS coin_e,
      MEDIAN(gems_start_day_balance) OVER () AS gem_s,
      MEDIAN(gems_end_day_balance) OVER () AS gem_e
    FROM agg.agg_sm_daily_user_currency_balance
    WHERE calc_date = :calc_date
      AND pu_segment = 'Active PU'
      AND is_playtika_user = 0
    """
    data = {}
    yesterday = dt.date.today() - dt.timedelta(days=1)
    for day in daterange(ECON_START, yesterday):
        day_rows = rows(conn, text, q, {"calc_date": day.isoformat()})
        if not day_rows:
            continue
        r = day_rows[0]
        data[day.isoformat()] = {
            "n_pu": int(r["n_pu"] or 0),
            "coin_s": float(r["coin_s"]) if r["coin_s"] is not None else None,
            "coin_e": float(r["coin_e"]) if r["coin_e"] is not None else None,
            "gem_s": float(r["gem_s"]) if r["gem_s"] is not None else None,
            "gem_e": float(r["gem_e"]) if r["gem_e"] is not None else None,
        }
    if not data:
        raise RuntimeError("pu_balance query returned no rows")
    write_json(PU_BALANCE, {
        "_source": "agg.agg_sm_daily_user_currency_balance filtered to pu_segment='Active PU' and is_playtika_user=0. Auto-refreshed by scripts/refresh_dwh_snapshots.py.",
        "_pulled_at": pulled_at,
        "_range": [min(data), max(data)],
        "days": data,
    })


def main() -> None:
    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    pulled_at = today.isoformat()
    engine, text = engine_from_config()

    def with_connection(fn, *args):
        conn = engine.connect()
        try:
            return fn(conn, text, *args)
        finally:
            try:
                conn.close()
            except Exception as exc:
                print(f"WARNING: Vertica connection close failed after {fn.__name__}: {exc}")

    with_connection(refresh_wide_revenue_pu, pulled_at)
    with_connection(
        refresh_key_file, WIDE_PROMO_KEYS, WIDE_START, yesterday, PROMO_PATTERNS,
        "dwh.sm_fact_smart_calendar_promotion_updates — latest version per promo_id, live-at-snapshot @ 11:00 UTC, classified in Python to match calibrate_model.py PROMO_PATTERNS. Auto-refreshed by scripts/refresh_dwh_snapshots.py.",
        {"_note": "Dates with revenue but no key list had no promo matching the tracked families at the 11:00 UTC snapshot."},
    )
    try:
        with_connection(
            refresh_key_file, SINK_KEYS, ECON_START, yesterday, SINK_PATTERNS,
            "dwh.sm_fact_smart_calendar_promotion_updates — latest version per promo_id, live-at-snapshot @ 11:00 UTC, classified into coin/gem sink mechanics. Auto-refreshed by scripts/refresh_dwh_snapshots.py.",
            {"_families": {
                "coin_sink": ["pyp", "mesTokens", "spinnerClash", "aceCardLoot", "customPod", "clanPoints", "dashChallenge", "machine", "winMaster", "spinZone", "jackpot", "megaWinner"],
                "gem_sink": ["shinyShow", "sneakPeek"],
            }},
        )
    except Exception as exc:
        if SINK_KEYS.exists():
            print(f"WARNING: sink_mechanic_keys refresh failed; keeping last good {SINK_KEYS}: {exc}")
        else:
            raise
    try:
        with_connection(refresh_pu_balance, pulled_at)
    except Exception as exc:
        if PU_BALANCE.exists():
            print(f"WARNING: pu_balance refresh failed; keeping last good {PU_BALANCE}: {exc}")
        else:
            raise


if __name__ == "__main__":
    main()
