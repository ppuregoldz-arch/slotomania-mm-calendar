#!/usr/bin/env python3
"""Rolling-origin backtest for the evidence-disciplined promo forecast.

This intentionally uses only data available before each test day.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MM = ROOT / "mm_calendar"
DATA = MM / "data"
OUT_JSON = MM / "prediction" / "backtest_results.json"
OUT_MD = MM / "prediction" / "BACKTEST_RESULTS.md"

HOLIDAYS = {
    "2025-11-28", "2025-11-29", "2026-01-01", "2026-01-02", "2026-02-14",
    "2026-03-17", "2026-04-04", "2026-05-05", "2026-05-25", "2026-07-04",
}
TEST_START = "2026-04-01"
TEST_END = "2026-07-05"
MIN_TRAIN_DAYS = 90
SHRINKAGE_N = 10
REV_PROMO_CAP = 100_000.0
PU_PROMO_CAP = 5_000.0


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def direction(value: float, tolerance: float) -> int:
    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def load_rows() -> list[dict]:
    outcomes = json.loads((DATA / "wide_revenue_pu.json").read_text())["days"]
    keys = json.loads((DATA / "wide_promo_keys.json").read_text())["days"]
    rows = []
    for iso, outcome in outcomes.items():
        if iso in HOLIDAYS:
            continue
        rows.append({
            "date": iso,
            "dow": dt.date.fromisoformat(iso).strftime("%a"),
            "revenue": float(outcome["rev"]),
            "paying_users": float(outcome["pu"]),
            "families": set(filter(None, (keys.get(iso) or "").split(","))),
        })
    return sorted(rows, key=lambda r: r["date"])


def fit(train: list[dict], metric: str) -> dict:
    by_dow = collections.defaultdict(list)
    for row in train:
        by_dow[row["dow"]].append(row[metric])
    base = {dow: statistics.mean(values) for dow, values in by_dow.items()}
    residuals = []
    family_residuals = collections.defaultdict(list)
    for row in train:
        residual = row[metric] - base[row["dow"]]
        residuals.append(residual)
        for family in row["families"]:
            family_residuals[family].append(residual)
    effects = {}
    for family, values in family_residuals.items():
        raw = statistics.mean(values)
        effects[family] = {
            "n": len(values),
            "raw": raw,
            "shrunk": raw * len(values) / (len(values) + SHRINKAGE_N),
            "p20": percentile(values, 0.2),
            "p80": percentile(values, 0.8),
        }
    return {
        "base": base,
        "effects": effects,
        "error_p80": percentile([abs(x) for x in residuals], 0.8),
    }


def evaluate_metric(rows: list[dict], metric: str, cap: float, tolerance: float) -> tuple[dict, list[dict]]:
    predictions = []
    family_eval = collections.defaultdict(lambda: {"n": 0, "correct": 0, "actual": [], "predicted": []})
    for i, test in enumerate(rows):
        if not (TEST_START <= test["date"] <= TEST_END):
            continue
        train = rows[:i]
        if len(train) < MIN_TRAIN_DAYS:
            continue
        model = fit(train, metric)
        base = model["base"].get(test["dow"])
        if base is None:
            continue
        contributions = {family: model["effects"].get(family, {}).get("shrunk", 0.0) for family in test["families"]}
        combined = max(-cap, min(cap, sum(contributions.values())))
        predicted = base + combined
        actual = test[metric]
        actual_residual = actual - base
        pred_residual = predicted - base
        low, high = predicted - model["error_p80"], predicted + model["error_p80"]
        predictions.append({
            "date": test["date"], "actual": actual, "base": base, "predicted": predicted,
            "error": predicted - actual, "abs_pct_error": abs(predicted - actual) / actual * 100 if actual else None,
            "actual_direction": direction(actual_residual, tolerance),
            "predicted_direction": direction(pred_residual, tolerance),
            "range_low": low, "range_high": high, "in_range": low <= actual <= high,
            "families": sorted(test["families"]),
        })
        for family in test["families"]:
            effect = contributions[family]
            stats = family_eval[family]
            stats["n"] += 1
            stats["actual"].append(actual_residual)
            stats["predicted"].append(effect)
            if direction(effect, tolerance) == direction(actual_residual, tolerance):
                stats["correct"] += 1
    errors = [p["error"] for p in predictions]
    apes = [p["abs_pct_error"] for p in predictions if p["abs_pct_error"] is not None]
    comparable = [p for p in predictions if p["actual_direction"] != 0 or p["predicted_direction"] != 0]
    result = {
        "n_days": len(predictions),
        "mae": statistics.mean(abs(e) for e in errors),
        "mape": statistics.mean(apes),
        "bias": statistics.mean(errors),
        "direction_accuracy": sum(p["actual_direction"] == p["predicted_direction"] for p in comparable) / len(comparable) if comparable else None,
        "range_coverage": sum(p["in_range"] for p in predictions) / len(predictions) if predictions else None,
        "families": {},
    }
    for family, stats in sorted(family_eval.items()):
        result["families"][family] = {
            "n_test_days": stats["n"],
            "direction_accuracy": stats["correct"] / stats["n"] if stats["n"] else None,
            "avg_actual_dow_residual": statistics.mean(stats["actual"]),
            "avg_predicted_effect": statistics.mean(stats["predicted"]),
        }
    return result, predictions


def main() -> None:
    rows = load_rows()
    revenue, revenue_days = evaluate_metric(rows, "revenue", REV_PROMO_CAP, 5_000.0)
    pu, pu_days = evaluate_metric(rows, "paying_users", PU_PROMO_CAP, 250.0)
    payload = {
        "generated_at": dt.date.today().isoformat(),
        "method": {
            "type": "rolling-origin",
            "test_window": [TEST_START, TEST_END],
            "minimum_prior_days": MIN_TRAIN_DAYS,
            "holiday_dates_excluded": sorted(HOLIDAYS),
            "family_effect": f"same-weekday residual mean shrunk by n/(n+{SHRINKAGE_N})",
            "revenue_family_sum_cap": REV_PROMO_CAP,
            "pu_family_sum_cap": PU_PROMO_CAP,
            "interval": "prediction +/- 80th percentile absolute training residual",
        },
        "revenue": revenue,
        "paying_users": pu,
        "wager": {"status": "insufficient-evidence", "reason": "No comparable daily wager series across the backtest window."},
        "gem_usage": {"status": "insufficient-evidence", "reason": "No comparable game-wide/variant gem-usage series across the backtest window."},
        "segment": {"status": "insufficient-evidence", "reason": "Daily outcome snapshots do not include canonical segment-level outcomes."},
        "day_predictions": {"revenue": revenue_days, "paying_users": pu_days},
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Historical Prediction Backtest",
        "",
        f"**Generated:** {payload['generated_at']}",
        f"**Design:** rolling-origin; every test day uses only prior data; test window {TEST_START}–{TEST_END}.",
        "",
        "## Overall results",
        "",
        "| KPI | Test days | MAE | MAPE | Bias | Direction accuracy | 80%-residual range coverage |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Revenue | {revenue['n_days']} | ${revenue['mae']:,.0f} | {revenue['mape']:.1f}% | ${revenue['bias']:+,.0f} | {revenue['direction_accuracy']:.1%} | {revenue['range_coverage']:.1%} |",
        f"| Paying users | {pu['n_days']} | {pu['mae']:,.0f} | {pu['mape']:.1f}% | {pu['bias']:+,.0f} | {pu['direction_accuracy']:.1%} | {pu['range_coverage']:.1%} |",
        "| Wager | — | — | — | — | insufficient evidence | insufficient evidence |",
        "| Gem usage | — | — | — | — | insufficient evidence | insufficient evidence |",
        "",
        "## Method",
        "",
        "- Same-weekday mean is fitted from prior non-holiday days.",
        f"- Family effects are prior same-weekday residual means shrunk by `n/(n+{SHRINKAGE_N})`.",
        f"- Concurrent family effects are summed and capped at ±${REV_PROMO_CAP/1000:.0f}K revenue / ±{PU_PROMO_CAP:,.0f} PU.",
        "- Expected range is prediction ± the prior 80th percentile absolute residual.",
        "- This tests family/day association, not causal attribution.",
        "",
        "## Family-level out-of-sample direction",
        "",
        "| Family key | Revenue n | Revenue direction | PU n | PU direction |",
        "|---|---:|---:|---:|---:|",
    ]
    families = sorted(set(revenue["families"]) | set(pu["families"]))
    for family in families:
        r = revenue["families"].get(family, {})
        p = pu["families"].get(family, {})
        lines.append(
            f"| {family} | {r.get('n_test_days','—')} | "
            f"{r.get('direction_accuracy',0):.1%} | {p.get('n_test_days','—')} | {p.get('direction_accuracy',0):.1%} |"
        )
    lines.extend([
        "",
        "## Failure cases and limits",
        "",
        "- Concurrent family effects are correlated; additive summation can double-count a large day.",
        "- Holiday/event behavior is excluded rather than modeled; this framework cannot predict flagship-event peaks.",
        "- Pricing, duration, exact segment, album phase, LBP peak, and audience size are incomplete in the wide source.",
        "- Wager, gem usage, and segment-level validation return **insufficient evidence**.",
        "- Family-level direction can be unstable where occurrences are sparse or systematically placed on one weekday/context.",
        "",
        "## Calibration implication",
        "",
        "Eligibility and expected ranges in `PREDICTION_AND_OPTIMIZATION.md` must use these observed errors. "
        "A recommendation cannot claim precision tighter than the demonstrated out-of-sample error/range.",
        "",
        f"Machine-readable results: `backtest_results.json`.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
