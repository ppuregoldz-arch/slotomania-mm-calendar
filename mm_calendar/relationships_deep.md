# Deep Relationships — Promos × Time × Users × Economy × Gameplay (data-grounded)

> **100% data-driven.** Source of truth: `dwh.sm_fact_smart_calendar_promotion_updates` (promo presence, latest-version + live-at-snapshot) cross-referenced with `agg.agg_sm_daily_users_stats` (revenue, DAU, payers, spins, balances, login).
> **v2 update: widened to Nov 1, 2025 – Jul 2, 2026 (242 days, 2.6× the original 92-day sample)** — see `smart_calendar_insights.md` §0 for why this window (stable-regime check) and §1 for two methodology fixes (row-dedup + **holiday-day exclusion**, which materially changed the promo-family ranking below — MGAP Bigger and Extreme Stamp's apparent strength turned out to be mostly a Black-Friday/New-Year/Valentine's confound). DOW/week-of-month sections below use the full 242-day window (holidays included — legitimate variation for those sections). Baseline revenue = **$650,136/day** (all days) / **$638,427/day** (234 days, holidays excluded — used for promo-family lift).
> **Caveat:** day-level correlations (multiple promos live per day). Directional, consistent across independent cuts and with the daily reports.

---

## 1. Promo family → revenue lift (holiday-adjusted, n=234 days) — see `smart_calendar_insights.md` §2 for full ranking + methodology

| Family | Days | Rev/day (clean) | vs baseline | Read |
|---|---:|---:|---:|---|
| Custom Pod | 25 | $695K | **+8.9%** | **Largest robust winner** — holds up after removing holidays |
| Coin Sale | 18 | $665K | **+4.2%** | Second robust winner |
| MGAP BOGO | 42 | $660K | +3.4% | Best MGAP variant (confirmed in both narrow and wide samples) |
| Decoy/Bonanza | 33 | $660K | +3.4% | — |
| Rolling (other) | 94 | $656K | +2.7% | Frequent, mildly positive |
| Boosted Gemback | 51 | $646K | +1.2% | Stable gem amplifier |
| Rolling More-for-Less | 31 | $646K | +1.1% | Gem-spend driver (see §5) |
| MGAP (other/generic) | 45 | $644K | +0.9% | — |
| Prize Mania | 10 | $644K | +0.9% | — |
| MGAP Bigger | 22 | $641K | +0.5% | **Neutral once holidays removed** — was +12.6% raw (confound) |
| x2 GGS | 48 | $639K | +0.2% | — |
| Clan Dash (any) | 208 | $638K | 0.0% | Baseline by construction (near-always-on) |
| Extreme Stamp | 34 | $637K | −0.2% | **Neutral once holidays removed** — a topper, not a standalone driver |
| RYD | 133 | $636K | −0.4% | **Backbone** (most frequent = baseline) |
| Piggy | 24 | $636K | −0.4% | — |
| Price Cut | 19 | $633K | −0.8% | Breadth/entry tool, not a peak-day lever |
| Happy Hour/Jumbo | 47 | $633K | −0.9% | — |
| MGAP Matched | 20 | $630K | −1.3% | Below BOGO |
| MGAP Wild Symbols | 32 | $621K | −2.8% | Weak MGAP variant |
| Buy All | 74 | $620K | −2.9% | Below baseline |
| **Golden Spin** | 10 | $586K | **−8.2%** | **Weakest promo in the data, robust across every cut tested** |

**Two monetization archetypes (still holds):**
- **Depth** (genuinely standalone, holiday-independent, **+PU and/or +ARPU after DOW match** — see `smart_calendar_insights.md` §4): **Custom Pod, Coin Sale** → schedule on peak days to maximize spend.
- **Conditional amplifiers** (value depends on pairing with a big day, not standalone): **Extreme Stamp, MGAP Bigger** — layer onto real events/holidays rather than expecting a flat lift on an ordinary day.
- **Breadth** (many payers, low ARPPU): Price Cut → widens the payer funnel; use to activate light spenders, not to carry a peak day.

## 2. Day-of-week (Vertica DAYOFWEEK 1=Sun … 7=Sat, n=242 days, holidays included)

| Day | Rev/day | Payers | Note |
|---|---:|---:|---|
| Sun | $641K | 29,111 | Solid |
| **Mon** | $646K | **35,919** | **Peak payers, lower ARPPU** — Monday deals / Dash Day (breadth) |
| Tue | **$600K** | 26,969 | **Weakest** — soft day |
| Wed | $642K | 27,969 | Piggy day |
| Thu | $623K | 25,952 | **Weak** (Golden Spin anchor sits here) |
| Fri | $693K | 27,715 | Weekend ramp |
| **Sat** | **$710K** | 28,015 | **Peak revenue** — weekend sale/depth |

Consistent with the narrower 92-day read (Sat peak, Tue trough) — the wide sample tightens confidence (n=34-35/weekday vs n=13 before) without changing the conclusion. **Rules of thumb unchanged:** Saturday is the depth peak (anchor Custom Pod / Coin Sale here). Monday is a breadth peak. **Tue & Thu are structurally weak.**

## 3. Period-in-month (week buckets, n=242 days)

| Week of month | Rev/day | Conv |
|---|---:|---:|
| Week 1 (d1–7) | **$671K** | **6.78%** |
| Week 2 (d8–14) | $654K | 6.63% |
| Week 3 (d15–21) | **$632K** | 6.55% |
| Week 4 (d22–28) | $641K | 6.57% |
| Week 5 (d29+, partial) | $653K | 6.75% |

Same direction as the 92-day read (week 1 strongest, week 3 trough) but the **gap is more modest with the wider sample** (+6% week1-vs-week3 narrowed from the earlier +11.6% estimate — the narrow sample overstated the swing). → Still front-load the biggest levers (Custom Pod, Coin Sale) in week 1; use week 3 for retention/value support, but don't over-engineer the fix — the real gap is smaller than first thought.

## 4. User trend & "connected vs not"

**Weekly macro trend (13 weeks):** DAU erodes slowly **424K → 406K (~4%/quarter)**, but revenue holds **$620–650K** because **ARPU rises** and engagement is stable (**sessions ~4.2/user**, conversion ~6.5–7%). Monetization is defending a shrinking base.
- Strongest weeks: 3/30 ($771K, quarter-end push), 5/04 ($689K, Cinco de Mayo). Trough: 6/22 ($605K).

**Connection segments (login_freq, 7/1 snapshot):**

| Segment | Users | % DAU | Payers | Conv | Revenue | % Rev |
|---|---:|---:|---:|---:|---:|---:|
| **Daily** | 321,003 | 79% | 25,020 | **7.8%** | $680,915 | **~90%** |
| Bi-daily | 33,270 | 8% | 1,890 | 5.7% | $42,027 | 5.5% |
| Twice a week | 18,746 | 5% | 1,075 | 5.7% | $21,432 | 2.8% |
| New/unclassified | 26,214 | 6% | 710 | **2.7%** | $9,509 | 1.2% |
| Weekly | 5,885 | 1% | 340 | 5.8% | $6,387 | 0.8% |
| Occasional | 1,825 | <1% | 111 | 6.1% | $1,853 | 0.2% |

**Daily-connected users are 79% of DAU but ~90% of revenue** (conversion 7.8% vs ~5.7% for less-frequent and 2.7% for new). → Habit-building promos (Dash streaks, login gifts, Piggy, daily-return mechanics) directly protect the revenue engine. New users monetize poorly — don't expect a promo to convert them fast; nurture into daily habit first.

## 5. Economy: coins, gems, slotobucks

- **Coin balances** are in hyperinflation (trillions+) and whale-distorted → **level comparisons are not robust**; track the coin economy via **wager/spins** instead (see §1: MGAP = biggest coin sink at 246–248M spins).
- **Gem balance** typical **~9–10K** (robust via `AVG(NULLIF(...,0))`); **slotobucks balance** typical **~385K**. These move visibly with promos (e.g., gem balance dipped 10.3K→8.5K on 6/27 = gem-sink event; slotobucks rose to 408K on 6/30 = issuance).
- **Gem purchase $ (`gems_transactions_dollar_value`) ≈ $37K/day** (matches the "Gems" product line). Highest on: **Rolling More-for-Less ($51K), Coin Sale ($48K), x2 GGS ($47K), Boosted Gemback ($42K)** → these are the gem-economy amplifiers. Lowest: Price Cut ($32K), MGAP Matched ($34K), Extreme Stamp ($35K) — coin/whale-oriented promos don't move gem buying.

## 6. Day-over-day momentum (hangover test)

| Day type | n | Rev today | Rev next day | Δ next |
|---|---:|---:|---:|---:|
| Non-sale | 74 | $643,981 | $643,896 | +$1,533 (flat) |
| Sale / Extreme Stamp | 18 | $655,282 | $647,179 | **−$8,103** |

Sale/amplifier days lift the day itself and cause only a **mild ~$8K next-day pullback** — the next day still sits **above** the non-sale baseline. **No meaningful hangover** → back-to-back amplifier days (e.g., Fri→Sat sale) are safe and additive. ⚠️ Note: "Sale/Extreme Stamp" days include real holidays (see §1) — some of this lift is the same holiday confound, not purely a promo-sequencing effect.

## 7. Product revenue ground-truth (92 days → $/day)

MGAPP **$190K/day** (#1 engine) · Sticky Bundle/DD **$132K** (widest: 104K payers) · Payment Page $53K · Gems $37K · Rolling $36K · Blast Picks $27K · RYD $26K · Battlesheep $19K · Clan Dash Bundle $18K · LBP Multi Ball $18K · Prize Mania $11K · Decoy $11K · Buy All $11K · Daily Dash Plus $11K (76K payers, low ARPU) · Piggy $8.5K · **Gems MGAP $8.3K (only 5.4K payers = whale niche, $141 ARPPU)** · Dice Deluxe $8.2K · SnL Dice $6.4K.
→ Always-on backbone (MGAPP + Sticky Bundle + Payment Page + Gems) ≈ **$400K/day floor** before promo lift — confirms the prediction-model baseline.

---

## Applied to July 2026 calendar
- **Day 11 (Sat, "Album Last 3 Days")** was the one Saturday with no depth-tier anchor → added **Custom Pod X1300 (48h, day 1/2, spanning 11–12/7)**. All 4 Saturdays now carry a depth anchor. Custom Pod remains the #1 robust winner even after the v2 holiday-adjustment (§1), so this fix holds up under the wider analysis.
- **Day 17 (Fri, week-3)** → added **x2 GGS (3h)** to reinforce week 3 (still the monthly trough in v2, though the gap is smaller than first estimated — see §3).
- **Day 4 (4th of July mega-event)** → switched `MGAP Bigger Multipliers` to `MGAP BOGO`. This holds up under v2: BOGO is the only MGAP variant that's a **consistent, positive performer in every cut** of the data (narrow, wide, holiday-adjusted); Bigger's earlier "weakest variant" read was itself partly a small-sample artifact (v1: −2.1%; v2 wide-raw: +12.6%; v2 clean: +0.5% — i.e. roughly neutral, never the standout winner BOGO is).
- Both changes re-validated with `validate_calendar.py`: 0 violations, all weekly caps (MGAP ≤3, GGS ≤2, Hammers ≤4) still respected.

## Handover to calendar building (actionable)
1. **Anchor Saturday** with a depth amplifier (Coin Sale / Extreme Stamp / MGAP BOGO). **Anchor Monday** with breadth (Dash / Monday Max / Price Cut).
2. **Front-load week 1** with the strongest promos; use **week 3** for retention/value offers to defend the monthly trough.
3. **Protect Tue/Thu** from wasting premium amplifiers — use RYD backbone + habit builders.
4. **MGAP BOGO/Matched > Bigger** (rev + gameplay). Use MGAP when the coin economy needs draining.
5. **Gem amplifiers** (GGS, Boosted Gemback, Rolling MoreForLess) for gem-economy weeks; they don't need a coin sale to work.
6. **Retention is monetization**: keep daily-connected share high (habit promos) — it carries ~90% of revenue on a slowly shrinking DAU base.
7. Back-to-back amplifier days are safe (no hangover).

_Last updated: July 2026. Regenerate via queries in `smart_calendar.md` + `dwh_reference.md`._
