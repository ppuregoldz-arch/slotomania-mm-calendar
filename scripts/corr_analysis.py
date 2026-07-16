#!/usr/bin/env python3
"""קורלציה בין wager uplift יומי לגורמים (Core + confounds) ליוני 2026."""
from __future__ import annotations

import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = Path("/Users/itayg/Downloads/Daily Wager (W_O Migrated Users).csv")
CTX = ROOT / "mm_calendar" / "data" / "june_context_2026.tsv"
MECHS = ["Spin Zone", "Win Master", "PYP", "Ace/Card Loot", "Spinner Clash",
         "Custom Pod", "Jackpots MES", "Mega Winner", "Dash Challenge", "MES themed/cards"]


def read_text(p: Path) -> str:
    raw = p.read_bytes()
    for enc in ("utf-16", "utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "replace")


def num(s):
    s = (s or "").strip().replace(",", "").replace("%", "")
    try:
        return float(s)
    except ValueError:
        return None


def load_wager():
    text = read_text(CSV).replace("\x00", "")
    out = {}
    for line in text.splitlines()[1:]:
        c = line.split("\t")
        if len(c) < 3 or not c[0].strip():
            continue
        m, d, y = c[0].split("/")
        out[f"{y}-{int(m):02d}-{int(d):02d}"] = {"wager": num(c[2]), "spins": num(c[1])}
    base_w = st.mean(v["wager"] for v in out.values())
    base_s = st.mean(v["spins"] for v in out.values())
    for v in out.values():
        v["w_up"] = v["wager"] / base_w - 1
        v["s_up"] = v["spins"] / base_s - 1
    return out


def load_ctx():
    out = {}
    for line in CTX.read_text(encoding="utf-8").splitlines()[1:]:
        c = line.split("\t")
        if len(c) < 9:
            continue
        out[c[0]] = {"weekend": int(c[2]), "sale": int(c[3]), "event": int(c[4]),
                     "mgap": int(c[5]), "gems": int(c[6]), "n_items": int(c[7]),
                     "cores": set(filter(None, c[8].split("|")))}
    return out


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = st.mean(xs), st.mean(ys)
    num_ = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    return num_ / (dx * dy) if dx and dy else None


def main():
    w = load_wager()
    ctx = load_ctx()
    days = sorted(set(w) & set(ctx))
    up = [w[d]["w_up"] for d in days]
    print(f"ימים משותפים: {len(days)} ({days[0]}→{days[-1]})\n")

    print("=== קורלציה (Pearson r) בין wager uplift לגורם ===")
    factors = ["weekend", "sale", "event", "mgap", "gems"]
    rows = []
    for f in factors:
        xs = [ctx[d][f] for d in days]
        rows.append((f, pearson(xs, up), sum(xs)))
    # n_items רציף
    rows.append(("n_items", pearson([ctx[d]["n_items"] for d in days], up), None))
    # Core כללי
    rows.append(("any_core", pearson([1 if ctx[d]["cores"] else 0 for d in days], up),
                 sum(1 for d in days if ctx[d]["cores"])))
    for name, r, cnt in sorted(rows, key=lambda x: -(x[1] or -9)):
        c = f" (ימים={cnt})" if cnt is not None else ""
        print(f"  {name:<12} r={r:+.2f}{c}" if r is not None else f"  {name:<12} r=NA")

    print("\n=== קורלציה של כל מכניקת Core (dummy) עם wager uplift ===")
    mrows = []
    for m in MECHS:
        xs = [1 if m in ctx[d]["cores"] else 0 for d in days]
        cnt = sum(xs)
        if cnt == 0:
            continue
        mrows.append((m, pearson(xs, up), cnt, st.mean([up[i] for i, d in enumerate(days) if xs[i]])))
    for m, r, cnt, avg in sorted(mrows, key=lambda x: -(x[1] or -9)):
        print(f"  {m:<20} r={r:+.2f}  ימים={cnt}  avg_uplift={avg*100:+.1f}%")

    print("\n=== בידוד confounds: avg wager uplift לפי חתך ===")
    for f in ["sale", "event", "weekend", "mgap", "gems"]:
        on = [w[d]["w_up"] for d in days if ctx[d][f]]
        off = [w[d]["w_up"] for d in days if not ctx[d][f]]
        on_m = f"{st.mean(on)*100:+.1f}% (n={len(on)})" if on else "—"
        off_m = f"{st.mean(off)*100:+.1f}% (n={len(off)})" if off else "—"
        print(f"  {f:<10} עם: {on_m:<18} בלי: {off_m}")


if __name__ == "__main__":
    main()
