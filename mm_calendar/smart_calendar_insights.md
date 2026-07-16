# Smart Calendar × Revenue — Promo Value Insights v2 (Wide Sample, Holiday-Adjusted)

> **Source of truth:** `dwh.sm_fact_smart_calendar_promotion_updates` (latest version per `promo_id`, live-at-snapshot @ 11:00, excludes cancelled/operational rows), cross-referenced with daily total net revenue from `agg.agg_sm_daily_users_stats`.
> **Window: Nov 1, 2025 – Jul 2, 2026 (242 days)** — widened from the original 92-day pass (Apr–Jul 2026) after confirming this is a **stable regime** (see §0). **2.6× the sample size** of v1.
> **Two methodology fixes vs v1** (see §1): (a) fixed a **row-duplication bug** for segmented promos, (b) **removed 8 holiday days** that were confounding the promo-lift numbers. Both are important — read §1 before trusting any number below.

## 0. Why Nov 1, 2025 and not further back — regime-stability check

The game went through a **major decline phase** before stabilizing:

| Period | DAU | Daily revenue |
|---|---:|---:|
| Jul 2024 | 733K | $1.23M |
| Oct 2025 (trough) | 460K | $601K |
| Nov 2025 – Jun 2026 | 410–454K (slow ~1-3%/mo decline) | $605–674K (stable band) |

Monthly DAU decline rate dropped from **−4% to −7%/month** (pre-Nov 2025) to **−1% to −3%/month** (post-Nov 2025) — a clear regime break. Using data from before Nov 2025 would blend in a fundamentally different user base and inflate/bias baselines. **Nov 1, 2025 is the correct cutoff**: it maximizes sample size (242 days vs 92) while staying inside the current stable regime. Baseline over this window: **$650,136/day** (vs $646,192 over the narrower 92-day window — only 0.6% apart, confirming the original window wasn't biased, just thin).

## 1. Two methodology corrections (read this first)

### (a) Row-duplication bug (fixed)
Segmented promos (e.g. Coin Sale split into PU/IC/DPU/NPU rows, or multi-audience variants) create **multiple Smart Calendar rows for the same promo on the same day**. A naive join × average double/triple-counts that day's revenue. Fixed by deduplicating on `(day, family)` before averaging. **Effect: small** (most family averages shifted <1%) — the original v1 numbers weren't badly wrong, just slightly noisy.

### (b) Holiday confound (this one mattered a lot)
The top revenue days in the window are almost all **calendar holidays**, not promo effects: Black Friday (11/28, $1.30M), New Year (1/1–1/2, ~$1.0M), Valentine's Day (2/14, $1.04M), Cinco de Mayo (5/5, $917K), St. Patrick's (3/17, $828K). Certain promo families (**MGAP Bigger, Extreme Stamp**) are disproportionately scheduled on these flagship days — inflating their *apparent* standalone lift when in fact the lift belongs to the holiday, not the promo.

**Test:** recomputed every family's average after excluding 8 clear holiday dates (11/28, 11/29, 1/1, 1/2, 2/14, 5/5, 4/4, 3/17). Clean baseline over the remaining 234 days: **$638,427/day**.

| Family | Raw avg (holidays included) | Clean avg (holidays excluded) | Holiday-confound size |
|---|---:|---:|---:|
| MGAP Bigger | $731,902 (**+12.6%**) | $641,439 (+0.5%) | **−12.1pp — almost entirely a holiday artifact** |
| Extreme Stamp | $687,414 (+5.7%) | $637,069 (−0.2%) | **−5.9pp — mostly a holiday artifact** |
| Custom Pod | $745,869 (+14.7%) | $695,256 (+8.9%) | −5.8pp, but still strongly positive after cleaning |
| Coin Sale | $730,814 (+12.4%) | $665,359 (+4.2%) | −8.2pp, still positive after cleaning |
| Golden Spin | $586,225 (−9.8%) | $586,225 (−8.2%) | **0 — not holiday-related, genuinely weak** |

**Conclusion: always use the holiday-adjusted ("clean") numbers below for promo-level decisions.** Extreme Stamp and MGAP Bigger's real standalone value is much smaller than raw correlation suggests — their apparent strength was "this promo happens to run on Black Friday," not "this promo drives incremental revenue on a normal day." This actually sharpens their correct use: they're genuinely most valuable specifically *layered onto* big event/holiday days (captured separately by the model's event-day bonus), not as an everyday revenue lever.

## 2. Clean promo value ranking (holiday-excluded, deduplicated, n=234 days)

| Rank | Promo family | Live days | Rev/day (clean) | vs clean baseline ($638,427) |
|---|---|---:|---:|---:|
| 1 | Custom Pod | 25 | $695,256 | **+8.9%** |
| 2 | Coin Sale | 18 | $665,359 | **+4.2%** |
| 3 | MGAP BOGO | 42 | $660,099 | **+3.4%** |
| 4 | Decoy/Bonanza | 33 | $660,005 | +3.4% |
| 5 | Rolling (other) | 94 | $655,812 | +2.7% |
| 6 | Boosted Gemback | 51 | $645,825 | +1.2% |
| 7 | Rolling More-for-Less | 31 | $645,657 | +1.1% |
| 8 | MGAP (other/generic) | 45 | $644,288 | +0.9% |
| 9 | Prize Mania | 10 | $643,903 | +0.9% |
| 10 | MGAP Bigger | 22 | $641,439 | +0.5% |
| 11 | x2 GGS | 48 | $639,408 | +0.2% |
| 12 | Clan Dash (any) | 208 | $638,202 | 0.0% (baseline) |
| 13 | Extreme Stamp | 34 | $637,069 | −0.2% |
| 14 | RYD | 133 | $636,033 | −0.4% (workhorse, most frequent) |
| 15 | Piggy | 24 | $635,643 | −0.4% |
| 16 | Price Cut | 19 | $633,495 | −0.8% |
| 17 | Happy Hour/Jumbo | 47 | $632,708 | −0.9% |
| 18 | MGAP Matched | 20 | $630,150 | −1.3% |
| 19 | MGAP Wild Symbols | 32 | $620,691 | −2.8% |
| 20 | Buy All | 74 | $620,179 | −2.9% |
| 21 | **Golden Spin** | 10 | $586,225 | **−8.2%** |

**⚠️ Golden Spin caveat:** n=10, and all 10 occurrences fall within the last ~3 months (it's a newer promo type) — "wide sample" doesn't apply to this specific family the way it does to the others. The direction is consistent with the original 92-day finding (identical numbers — no new occurrences existed outside that window), so treat it as consistent-but-still-thin evidence, not yet statistically mature.

## 3. Key insights (revised)

1. **Custom Pod and Coin Sale are the only two "robust, large, standalone" winners** — they hold up strongly (+8.9%, +4.2%) even after removing every major holiday from the sample. These are genuine everyday revenue levers, not holiday artifacts.
2. **MGAP BOGO is confirmed (again) as the best MGAP variant** — +3.4% clean, consistent across both the narrow and wide samples. **MGAP Matched (−1.3%) and Wild Symbols (−2.8%) underperform**; **MGAP Bigger is now roughly neutral (+0.5%)** — not the winner OR the loser it looked like in different cuts, just average. Prefer BOGO when choosing a variant.
3. **Extreme Stamp is genuinely a "topper," not a standalone driver** — once holiday-confound is removed it's flat (−0.2%). Its documented "amplifier" role should be understood as "amplifies whatever else is happening that day" rather than "adds X% on its own." Don't expect it to rescue a quiet day.
4. **Golden Spin is the one unambiguously weak promo across every cut of the data** (−8.2% to −9.8%, holiday-adjusted or not) — the only finding that's robust in both magnitude and direction regardless of methodology.
5. **RYD remains the pure workhorse** — most frequent (133 days), sits almost exactly at baseline by construction (it's the always-on default).
6. **Buy All (−2.9%) and MGAP Wild Symbols (−2.8%)** are the clearest "avoid on peak days" picks among the moderately-frequent families.

## 4. DAU & paying-user (PU) normalization — v2.1

Absolute **$/day** lift mixes three levers: **audience size (DAU)**, **payer count (PU / conversion)**, and **spend intensity (ARPU / ARPPU)**. In the stable window, DAU fell ~**454K → 410K** (~−10%) and PU ~**30.4K → 27.1K** (~−11%) while headline revenue stayed ~**$620–650K** because **ARPU rose ~+7%** (fewer users, heavier payers).

### Macro reference (clean days, no holidays)

| Metric | Regime mean (234 clean days) |
|---|---:|
| DAU | **433,900** |
| PU (payers) | **28,629** |
| Net revenue | **$638,427** |
| ARPU | **$1.47** |
| Conv (PU/DAU) | **6.60%** |
| ARPPU | **~$22.3** |

**July 2026 planning anchor** (21-day trail through Jul 1): DAU **~407K**, PU **~27.8K**, daily rev **~$615K** — structurally lower absolute $ than the 242-day mean even when promos are “average,” unless ARPPU keeps compensating.

### Three lenses for promo lift (same families, holiday-excluded, deduped)

| Lens | What it controls | Use for |
|---|---|---|
| **A. Clean $ vs $638K baseline** | Holidays only | Conservative calendar ranking (§2) |
| **B. DOW-matched residual** | Same weekday expected rev in-window | **Primary model deltas (v5)** — removes Sat-vs-Tue placement bias |
| **C. Residual after DAU+PU regression** | Daily DAU & payer count | “Incremental $ beyond audience that day” — can **inflate** toppers on low-PU days (Extreme Stamp) |

**DOW-matched residual** (avg rev on live days minus avg rev on same weekday across clean days):

| Family | n | $ residual | Rev lift | ΔPU | ΔARPU |
|---|---:|---:|---:|---:|---:|
| Custom Pod | 25 | **+$37K** | +5.6% | +1.8% | +5.5% |
| Coin Sale | 18 | +$17K | +2.6% | +1.6% | +1.6% |
| MGAP BOGO | 42 | +$15K | +2.3% | +1.0% | +1.8% |
| Buy All | 75 | −$13K | −2.0% | −0.2% | −3.0% |
| Golden Spin | 10 | **−$38K** | −6.1% | **−4.6%** | −2.3% |

**Interpretation:** **Custom Pod** wins on **both** breadth (PU) and depth (ARPU). **Golden Spin** is weak on **all three** — not just “fewer users that day.” **Coin Sale** adds payers *and* ARPU (consistent with segmented PU/IC/DPU offers). After full DAU+PU regression, ranks stay the same at the top/bottom; mid-tier **Extreme Stamp / MGAP Bigger** can look slightly positive in lens C while still **neutral in lens A** — they often run when PU is already depressed, so regression credits them; keep them as **event toppers**, not weekday anchors.

**Calendar / `predict()` v5:** promo $ deltas = **0.8 × DOW-matched residual**; plus a **crowd term** for July 2026 vs regime (~407K DAU, ~27.8K PU) so month-level forecasts are not blind to the shrinking base.

## Handover to calendar building
- Anchor peak days (weekends, real events/holidays) with **Custom Pod / Coin Sale**, and layer **Extreme Stamp** on top of those days specifically (its value is conditional on the day already being big, not a standalone lever).
- Prefer **MGAP BOGO** over Matched/Wild Symbols/Bigger when choosing a variant — small but consistent edge.
- Keep **RYD** as the daily backbone.
- Avoid relying on **Golden Spin** to carry any day — it is structurally the weakest promo in the data, in every cut tested.

_Last updated: July 2026 (v2.1 — §4 DAU/PU normalization + v5 prediction). Regenerate via SC × revenue queries in `smart_calendar.md`; re-check regime window (§0) and trailing DAU/PU monthly._
