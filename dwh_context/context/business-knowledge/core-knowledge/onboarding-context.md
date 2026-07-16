# Slotomania — Analytics Onboarding & Context (for Cursor)
_Last updated: 2025-09-28T09:28:49.716517_

> This file distills the Slotomania BA onboarding document into an actionable, search-friendly knowledge base you can keep open in Cursor while you work. It’s optimized for discoverability (clear headers, code blocks, checklists) and safety (sensitive credentials redacted).

---

## Table of Contents
- [0. Quickstart (Day 1–7)](#0-quickstart-day-1–7)
- [1. Studio Overview & Responsibilities](#1-studio-overview--responsibilities)
- [2. Game Primer — Slotomania Core](#2-game-primer--slotomania-core)
  - [2.1 Lobby & Navigation](#21-lobby--navigation)
  - [2.2 Currencies & Economy](#22-currencies--economy)
  - [2.3 Bonuses & Premiums](#23-bonuses--premiums)
  - [2.4 Social & Meta Features](#24-social--meta-features)
  - [2.5 Cards, Albums & Shiny](#25-cards-albums--shiny)
  - [2.6 Daily Dash & Progression](#26-daily-dash--progression)
  - [2.7 Machines, MFE, Jackpots & Manias](#27-machines-mfe-jackpots--manias)
  - [2.8 Seasonal Features (5–7 days)](#28-seasonal-features-5–7-days)
  - [2.9 Mid‑Term Features](#29-midterm-features)
  - [2.10 VIP Platforms (PRAS, .com)](#210-vip-platforms-pras-com)
- [3. Monetization, Store & SKUs](#3-monetization-store--skus)
- [4. Analytics Toolbox](#4-analytics-toolbox)
  - [4.1 Tableau](#41-tableau)
  - [4.2 DataGrip (Vertica SQL)](#42-datagrip-vertica-sql)
  - [4.3 Jira & Lists Runbook](#43-jira--lists-runbook)
- [5. Data Foundations](#5-data-foundations)
  - [5.1 Schemas, Facts & Dims](#51-schemas-facts--dims)
  - [5.2 Promo‑Date & Timezone Canon](#52-promo-date--timezone-canon)
  - [5.3 Core Dimensions (Platform, Level, Tier, Segments)](#53-core-dimensions-platform-level-tier-segments)
  - [5.4 NPU/PU/FTD Identification](#54-npupuftd-identification)
  - [5.5 High‑Value Tables (Cheat Sheet)](#55-high-value-tables-cheat-sheet)
- [6. Query Patterns & Snippets](#6-query-patterns--snippets)
  - [6.1 Required Filters (Payments Safety)](#61-required-filters-payments-safety)
  - [6.2 Grouping & Window Functions](#62-grouping--window-functions)
  - [6.3 “Turn Measures into Dims” Pattern](#63-turn-measures-into-dims-pattern)
  - [6.4 “Promo Date Everywhere” Pattern](#64-promo-date-everywhere-pattern)
  - [6.5 Common KPIs](#65-common-kpis)
  - [6.6 Examples from Onboarding](#66-examples-from-onboarding)
- [7. A/B Testing in Slotomania](#7-ab-testing-in-slotomania)
- [8. Gatekeeping Playbooks](#8-gatekeeping-playbooks)
- [9. Daily BA Workflow](#9-daily-ba-workflow)
- [10. KPIs & Targets](#10-kpis--targets)
- [11. Glossary](#11-glossary)
- [12. Useful Links (internal)](#12-useful-links-internal)
- [13. Open Questions & TODOs](#13-open-questions--todos)
- [Appendix A — Level Ranges & Tier Mapping](#appendix-a--level-ranges--tier-mapping)
- [Appendix B — Redacted Sensitive Details](#appendix-b--redacted-sensitive-details)

---

## 0. Quickstart (Day 1–7)
**Your first week, condensed:**
1. **Install & access**: Tableau, DataGrip, Jira/Monday/Teams, Monetization calendar, Q, Lenses. _(Request DB access via Infra.)_
2. **Play the game**: Experience lobby, bonuses, store (PP), Daily Dash, a few machines. Take notes.
3. **Know the canon time**: Analytics “day” = **promo date** starting **12:00 UTC / 14:00 IL** (subject to DST shifts). Anchor every query to this.
4. **Spin up notebooks/dashboards**:
   - Payments, PUs, ARPPU/ARPU time series.
   - Daily spins/wager per tier & platform.
   - Cards/Album progress, Daily Dash, key seasonal feature of the week.
5. **Learn the “must‑join” dims**:
   - **Platform, Level Range, Tier, Product (SKU)**, Promo Date logic. Keep snippets handy.
6. **Run a safe query**: Use payments **required filters** (approved, non‑test, non‑sandbox).
7. **Shadow a lists extraction**: Follow the **Monetization Lists Runbook** (Section 4.3) & do QA in Teem.
8. **A/B baseline**: Identify your test IDs, validate control/test allocation, and bookmark the A/B results Tableau workbook.
9. **Gatekeep tonight’s change**: Use relevant dashboard checks 2 hours after go‑live.

---

## 1. Studio Overview & Responsibilities
**Vision**: Lead data‑driven decision making and continuously support & improve business choices across the studio.  
**Responsibilities** include: KPI definition/monitoring, **gatekeeping** (data QA) for operations & features, deep analysis for departments, dashboards, challenging offers, A/B tests & insights, voice‑of‑player reflection, surveys, validation of new features, and brand equity research. source: internal onboarding doc; see citation in chat.

**Collaboration cadence**: Daily standup (yesterday’s KPIs + today’s promos), monthly business‑oriented meetings per TF, TF weekly syncs per feature with cross‑functional stakeholders (Product, Monetization, AM, Economy, Art, R&D).

---

## 2. Game Primer — Slotomania Core
Slotomania is a social slots game with **frequent new content**, liveops, and a deep metagame (cards, clans, progression). Players encounter new experiences daily.

### 2.1 Lobby & Navigation
- **Pre‑loader** with brand slogan (“What will today spin?”). 
- **News Feed**: Central surface for live promos; red dot = unread.
- **Static & rotating banners** in lobby for daily promos/challenges.
- **Playlists**: Curated machine collections for discovery & traffic shaping.
- **Static icons** (clockwise from BUY/SlotoStore): Payment Page (PP), Personal Offer (PO), **Gems**, Level bar (XP), **Piggy**, Menu (ID, Support), **Special Bonus**, **Mega Bonus** → **Golden Spin**, **Daily Bonus**, **Clans**, **Smash It**, **Slotoclub**, **Sloto Cards**, **Daily Dash**, Avatar, **Gifts/GCP**, **Stash**, Seasonal feature slot, **Lotto Bonus (+Premium)**, **Level Rush Rally**, **Eye on the Prize**, **Ballinko**, **Cocktail Bonus**, **Store Bonus**, **Stamp Hit**, **Grab ’em**, **Buddy Guard**, **Badge Book/Medals**. 

### 2.2 Currencies & Economy
- **Coins** (primary soft currency / wager).
- **Gems** (premium in‑app currency; spend in various sinks; purchasable).
- **Slotobucks** (used in PP; logged separately).
- **XP** (progression to level unlocks).  
- **Status Points (SP)** (tiering; benefits by Tier).  
- **Club Points** (Slotoclub access; temporary pass).

### 2.3 Bonuses & Premiums
- **Special Bonus**: Collect every 3h; **1h Power** after purchase for 7 days; **Turbo** variants adjust cadence.
- **Mega Bonus**: Every 3 Special Bonuses; wedge multipliers; **Golden Spin** is a **premium** upsell after Mega.
- **Daily Bonus**: 1/day spin.
- **Lotto Bonus** (LBP): After 3 consecutive Special Bonus collections; **Lotto Bonus Premium** upsell with higher multipliers.

### 2.4 Social & Meta Features
- **Clans**: Social group with communal challenges, **Clan Points**, **Chest rewards**, trading, chat; **Clan Badges** → “Clan Go” bar.
- **Smash It**: Loyalty hub with seasonal missions (28 days), **Slot Smashes**, **Smash N’ Grab** minigame; token economy; personal % benefits by tier/level.
- **Buddy Guard**: Time‑boxed “protect the safe” wager‑accumulation to keep a large coin buffer.
- **Medals**: Replaces Badges per machine (Bronze/Silver/Gold) → spins on Medal Machine.

### 2.5 Cards, Albums & Shiny
- **Sloto Cards**: Always‑on collectible album (70‑day seasons). Rewards for sets & album completion; **Wild Cards** are universal fillers via challenges/promos; **Gold** (non‑tradable), **Ace** cards (from special channels).  
- **Fusion Cards**: 1 Fusion = 4 regular (1 + 3 dupes); better set rewards; helps dupe pressure.  
- **Shiny Cards**: Only from **Shiny Show** minigame.  
- **Ace Spin Machine**: Free spins based on Ace card stars; rewards include gems/coins/cards/club points.  
- **Shiny Show**: Pick‑one risk minigame with mole fail state; gems can save; Shiny card jackpots on acts 5/10/15.

### 2.6 Daily Dash & Progression
- **Daily Dash**: 4 daily challenges; bar with prizes (coins/cards); resets **daily 14:00 IL**; weekly bar resets every **2 weeks**. High retention driver.  
- **Super Dash**: Extra 24h missions; can skip with gems.  
- **Daily Dash Max** (premium): Bi‑weekly purchase that unlocks more rewards; end reward can be **Wild Card**.

### 2.7 Machines, MFE, Jackpots & Manias
- **Machines**: Many slots; new on the left of lobby; older to the right. Some are locked by level.  
- **Jackpots**: Multi‑stage (Minor/Major/Grand) with points meter & wheel progression via keys; **Jackpot Stages** progression bar with stage‑up rewards.  
- **MFE (Machine Feature Engine)**: Each machine can host bonus minigames (e.g., Roulette Nights’ Roulette Bonus), sometimes granted directly to **GCP**.
- **Game Manias**: Time‑boxed machine‑specific payouts/fun injections (e.g., higher payout), granted via promos/mini‑games.
- **Shiny Loot**: Watermark mechanism granting shiny wands/cards.

### 2.8 Seasonal Features (5–7 days)
Rotating surprise features themed by month/album; most require filling a meter (bet or win based) to enter. Some have direct‑revenue products (e.g., extra picks). Examples:
- **Blast** (Owner: Aviv): Uncover **blast** to advance; **extra pick** upsell drives revenue.
- **Battle Sheep** (Owner: Aviv): Uncover clouds (empty/ship/jackpot/wolf); **parasheeps** from purchase/spinning to progress.

### 2.9 Mid‑Term Features
- **Figs** (Owner: Avner): Collect figure coins via spinning; buy figures; complete sets → free spins rewards.
- **Winovate** (Owner: Avner): Spend **hammers** to renovate items across scenes; **Hammer Strike** minigame; hammers from designated games.
- **Globez** (Owner: Avner): Collect snow globes (USA/AUS/JPN/FRA sets) via designated games; complete sets → coin grabs.
- **Stash or Splash** (Owner: Avner): Race across missions against others for pooled **grand prize**; prize splits on multiple winners.
- **Mega Pods** (Owner: Avner): Earn pods from **Mega wins**; timers by rarity; open instantly with gems; max 4 stored, 1 active.

### 2.10 VIP Platforms (PRAS, .com)
- **VIP Premium app (PRAS)** & **Slotomania.com** reduce third‑party store fees and unlock extra benefits (coupons, higher multipliers, extra dash points, boosted bonuses, status/XP multipliers, permanent manias, safety nets, sneak peeks, etc.). Strategic conversion target.

---

## 3. Monetization, Store & SKUs
- **Denominations**: Price points map to increasing value (**VFM/V4M** improves with higher denoms & tier/level).  
- **Products** in PP: Coin packages (+ card packs, stamp card progress, club points, SP, 1h power, gift card), **Gems**, and **Boosters** (e.g., **Mega Bonanza**, **Level Boom**, **Star Dice**) typically for **3 or 7 days**.
- **PO (Personal Offer)**: Time‑limited personalized upsell triggered by exits/low balance/login events; urgency mechanics.
- **Stamp Hit**: Purchase‑only stamps; fill a 4‑stamp card (expires 30 days) to play a minigame; special stamps (Diamond/Red Diamond) boost value.
- **Cocktail Bonus** (post‑purchase multiplier), **Store Bonus** (free every ~8–9h), **Grab ’em** (purchase tools).  
- **Piggy Bank**: Save a portion of wager; can break for a fee (monetized).  
- **Slotoclub**: Temporary pass (7 days per 10k club points). Benefits: XP boost, cashback, better bonuses/discounts, exclusive machines, boosted store.

> **SKU Identity**: Each product is represented by **(sku_id, transaction_source_type_id)** → Product Name mapping (see `sm_draft.SM_DIM_Products`).

---

## 4. Analytics Toolbox

### 4.1 Tableau
- Keep server version parity; obtain license key (via owner).  
- Prefer **Extract** over Live for performance; use Live only for dynamic dashboards.  
- Marks: Color by group (A/B), Label for values.  
- Calculated fields (typical):
  ```text
  Daily Revenue = SUM([net_revenue]) / COUNTD([promo_date])
  Daily PU      = SUM([PU]) / COUNTD([promo_date])
  ARPPU         = SUM([net_revenue]) / SUM([PU])
  ARPU          = SUM([net_revenue]) / SUM([users])
  ```
- Publishing: Overwrite carefully; set schedule & sheet selection.

### 4.2 DataGrip (Vertica SQL)
- Request Vertica access via Infra; install DataGrip (license auto‑recognized).  
- Add Playtika DWH; schemas commonly used: `dwh`, `agg`, `sm_draft`, `users`.  
- Introspect schemas; use templates later (start manual first to learn tables).  
- Performance tips: Query **top 500** when exploring; aggregate before exporting; customize shortcuts.

### 4.3 Jira & Lists Runbook
**Why care**: Many promos are manual ⇒ error‑prone lists. Good QA prevents bad player experiences.

**Cadence**
- Monetization posts **list JIRAs** by **Thu** for the **week +1** (≥10 days ahead).  
- Weekly sync: Monetization × BA approve.

**BA steps**
1. Confirm inputs in Jira (start/end time, inapp asset, rules).
2. Write/validate SQL (reuse with caution; re‑QA conditions).
3. Extract to CSV/Excel & attach to Jira.
4. **QA in Teem** via checklist (edge cases; caps; dupes; sample UIDs).
5. Add to Jira comments:
   - Final SQL,
   - # winners,
   - # extreme wins (e.g., >100T coins),
   - # multi‑completes,
   - Cap hits.
6. Flip Jira to **Complete** and ping Operations.

---

## 5. Data Foundations

### 5.1 Schemas, Facts & Dims
- **DWH**: Raw, high‑granularity (per user/spin/session/payment).  
- **AGG**: Aggregated convenience tables (daily, hourly, etc.).  
- Naming: `fact_*` = events/measures; `dim_*` = reference mappings.

### 5.2 Promo‑Date & Timezone Canon
- **Promo Date** ≈ analytics day boundary aligned to **12:00 UTC / 14:00 IL** (DST may shift the offset).  
- Convert timestamps to promo date in SQL to ensure day‑aligned joins for promos & dashboards.

### 5.3 Core Dimensions (Platform, Level, Tier, Segments)
- **Platform**: Map `platform_id` → human names (Web/iOS/Android/.com/PRAS/Amazon/Win8/Win10/Other).  
- **Level Range**: Bucket `user_level` (see Appendix A).  
- **Tier**: `tier_id` → Bronze, Silver, Gold, Platinum, Diamond, Royal Diamond, Black Diamond.  
- **Smart Segments** (from `dwh.sm_user_profile_datamining`): `avg_bet`, `median_bet`, `n_spins_per_day`, `sq_wager`, `dp_habit`, `CZ_*`, `mgap_comfort_zone`, etc.

### 5.4 NPU/PU/FTD Identification
- **FTD**: first ever approved real‑money purchase (see `dwh.v_fact_currency_transactions` with `game_tran_order_count = 1, environment_id = 1`).  
- **is_paying** flag exists in `dwh.sm_user_profile` (lifetime).

### 5.5 High‑Value Tables (Cheat Sheet)
- **Payments**: `dwh.sm_fact_payments` (apply required filters!).  
- **Spins**: `dwh.fact_sm_spin_history_kafka`.  
- **Sessions**: `dwh.fact_sm_sessions_kafka`.  
- **User Profile**: `dwh.sm_user_profile`.  
- **Bonuses**: `dwh.fact_sm_bonus_history` + `dwh.dim_sm_bonus_type`.  
- **Cards**: `dwh.sm_fact_collectibles_cards`.  
- **AGG Daily**: `agg.agg_sm_daily_users_stats`, `agg.agg_sm_daily_users_spins`, `agg.agg_sm_daily_promotion_stats`.  
- **Products DIM**: `sm_draft.SM_DIM_Products`.

---

## 6. Query Patterns & Snippets

### 6.1 Required Filters (Payments Safety)
Always include these in payments work:
```sql
WHERE user_id > 0
  AND tran_status_id = 2         -- approved
  AND artificial_ind = 0         -- real, not sandbox
  AND is_test = 0                -- not test transactions
```

### 6.2 Grouping & Window Functions
- Prefer **`GROUP BY 1,2,...`** for speed & brevity.  
- Windows for medians/percentiles across cohorts:
```sql
SELECT
  calc_date,
  MEDIAN(spins)          OVER (PARTITION BY calc_date) AS med_spins,
  MEDIAN(balance_end_day)OVER (PARTITION BY calc_date) AS med_balance,
  MEDIAN(bet_coins)      OVER (PARTITION BY calc_date) AS med_wager
FROM agg.agg_sm_daily_users_stats
WHERE calc_date >= CURRENT_DATE - 3;
```

### 6.3 “Turn Measures into Dims” Pattern
Count events per user, then wrap & group:
```sql
-- How many users finished N daily‑dash challenges yesterday, by N?
SELECT challenges_finish, promo_date, COUNT(DISTINCT user_id) AS users
FROM (
  SELECT user_id,
         DATE( CASE
                 WHEN DATEDIFF('hh', event_ts AT TIME ZONE 'Asia/Jerusalem', event_ts AT TIME ZONE 'UTC') = 2
                 THEN event_ts - INTERVAL '12 hour' ELSE event_ts - INTERVAL '11 hour' END
         ) AS promo_date,
         COUNT(*) AS challenges_finish
  FROM dwh.sm_fact_daily_dash_challenges
  WHERE status = 'finished' AND event_ts >= CURRENT_DATE - 30
  GROUP BY 1,2
) a
GROUP BY 1,2;
```

### 6.4 “Promo Date Everywhere” Pattern
```sql
-- Canonical promo date from UTC
DATE(tran_ts::timestamp AT TIME ZONE 'UTC'
     AT TIME ZONE 'Asia/Jerusalem' - INTERVAL '14 hours') AS promo_date
```

### 6.5 Common KPIs
```sql
-- Daily revenue
SUM(net_amount)/COUNTD(promo_date)

-- ARPPU
SUM(net_amount)/SUM(PU)

-- ARPU
SUM(net_amount)/SUM(users)
```

### 6.6 Examples from Onboarding
**Spins & Wager for ‘Crazy Train’ — last 7 days**
```sql
SELECT b.machine_type_name,
       COUNT(*)          AS spin_count,
       SUM(a.bet_amount) AS wager
FROM dwh.fact_sm_spin_history_kafka a
LEFT JOIN dwh.dim_sm_machine_type b
  ON a.machine_type_id = b.machine_type_id
WHERE b.machine_type_name ILIKE 'Crazy Train'
  AND a.spin_date >= CURRENT_DATE - 7
GROUP BY 1;
```

**Daily spins & wager by Tier**
```sql
SELECT spin_date,
       CASE
         WHEN tier_id=1 THEN 'Bronze'
         WHEN tier_id=2 THEN 'Silver'
         WHEN tier_id=3 THEN 'Gold'
         WHEN tier_id=4 THEN 'Platinum'
         WHEN tier_id=5 THEN 'Diamond'
         WHEN tier_id=6 THEN 'Royal Diamond'
         WHEN tier_id=7 THEN 'Black Diamond'
         ELSE 'Other' END AS tier_name,
       COUNT(*)          AS spin_count,
       SUM(bet_amount)   AS total_wager
FROM dwh.fact_sm_spin_history_kafka
WHERE spin_date BETWEEN CURRENT_DATE-8 AND CURRENT_DATE-1
GROUP BY 1,2
ORDER BY 1,2;
```

**Map (sku_id, source) → product name**
```sql
SELECT a.user_id, a.tran_date, a.net_amount, b.product_name
FROM dwh.sm_fact_payments a
JOIN sm_draft.SM_DIM_Products b
  ON a.sku_id = b.sku_id
 AND a.transaction_source_type_id = b.transaction_source_type_id
WHERE a.tran_date >= CURRENT_DATE - 7
  AND a.user_id > 0 AND a.tran_status_id = 2 AND a.artificial_ind = 0 AND a.is_test = 0;
```

More examples (FTD detection, DAU/PU joins, repurchase rate for Piggy, etc.) are embedded throughout the source doc; port them as needed and validate column names in your environment.

---

## 7. A/B Testing in Slotomania
- Allocation historically based on **digits** (e.g., `test_id_3`); transitioning to **smart allocation**.  
- Typical control/test split isn’t always 50/50 → **use within‑group deltas** vs. prior, then compare to control deltas.  
- Example grouping in SQL:
```sql
CASE
  WHEN test_id_3 IN (2,3,4,5,6,7,8,9) THEN 'Control'
  WHEN test_id_3 IN (0,1)             THEN 'Test'
END AS t_group
```
- **Results reading**: Prefer normalized lifts vs. control, not absolute totals.  
- **Dashboard**: Dedicated A/B results workbook (paste test groups → see auto results).

---

## 8. Gatekeeping Playbooks
**When**: New economy configs (PP, PO, Dash, Clans, Ballinko), tests, features, seasonal openings.  
**Windows**: Immediately at “war room” opening, **+2h** update, **+24h** email/Teams update, **+1 week** follow‑up.

**Checklist**
- Config applied? (values, eligibility, caps, triggers)
- Exposure & segmentation correct? (platform, tier, level ranges)
- Event fire rate sane? (spikes, drop‑offs)
- Monetization funnels (views → clicks → purchases)
- Rewards delivery & balances (coins/gems/cards/clan points)
- Error audits (timeouts, exceptions)
- Player feedback (AM, SSG/FB group)
- Create/refresh easy dashboards; keep ad‑hoc SQL at hand.

---

## 9. Daily BA Workflow
1. **Morning**: Open management KPI report; scan yesterday vs. targets; note anomalies.  
2. **Promos**: Review today’s calendar; identify manual lists; align with Monetization.  
3. **Gatekeep**: Track live ops/toggles; run +2h checks.  
4. **Analysis**: TF priorities; iterate with lead → GM sign‑off → studio blast.  
5. **Comms**: Share insights to _SM|Data Analysis_ distro with clear **Bottom Lines** & **Recommendations** template.

**Analysis template**  
```
Name
Background
Results table / visual
Bottom lines
Recommendations
```

---

## 10. KPIs & Targets
- **Unique PU (Monthly)** — studio‑wide goal (example: 285k).  
- **Daily Revenue** — e.g., 1.33M target (varies over time).  
- **Retention D30** — e.g., 5% target.  
Monitor with the **SM Quarterly Performance Tracking** and **SM Management KPI** reports.

---

## 11. Glossary
A non‑exhaustive subset (see source doc for full list):
- **ARPU** — Avg Revenue per User  
- **ARPPU** — Avg Revenue per Paying User  
- **DAU/MAU** — Daily/Monthly Active Users  
- **FTD/STD** — First/Second Time Depositor  
- **GCP** — Gift Collection Popup  
- **PO** — Personal Offer (also “Product Owner” in other contexts; disambiguate)  
- **PP** — Payment Page  
- **PU** — Paying Users  
- **SP** — Status Points  
- **VFM/V4M** — Value for Money  
- **MFE** — Machine Feature Engine  
- **GS** — Golden Spin  
- **CZ** — Comfort Zone (pricing affinity)  
- **SQ** — Sloto Quest  
- **GUID** — Unique Spin ID  
- **CTR/CTA** — Click‑through / Call‑to‑Action  
- **HO** — Hidden Objects  
- **PRAS** — Playtika Rewards App/Platform (VIP premium)  
- **TRS** — Total Rewards Social

(Keep this section updated as new team jargon appears.)

---

## 12. Useful Links (internal)
- Slotomania Wiki Home  
- Sloto Cards wiki  
- Daily Dash 2.0 wiki  
- Level Rush Rally – BA Events wiki  
- Game Design decks (Intro to Slots; A–Z)  
- A/B Testing Results Tableau  
- Jira board for lists (Monetization/BA)  
- SM SQL Templates (Promo Date, Platform, Level Ranges, Product map)

> Note: Internal links omitted here for external sharing. Keep a local copy with links if you have access.

---

## 13. Open Questions & TODOs
- **Credentials**: Replace redacted placeholders with secure secrets manager references.  
- **Calendar edge cases**: Re‑confirm DST offset logic for promo date each switch.  
- **A/B allocation**: Confirm current split rules in smart allocator and update SQL macros.  
- **Product DIM**: Ensure latest `SM_DIM_Products` is synced & documented (versioned).  
- **VIP perks list**: Periodically refresh; benefits change over time.  
- **Seasonal roster**: Keep live list of seasonals + owners + revenue hooks + entry meters.  
- **KPIs**: Validate current targets and dashboards ownership.

---

## Appendix A — Level Ranges & Tier Mapping

**Tier Map**
```
1 Bronze
2 Silver
3 Gold
4 Platinum
5 Diamond
6 Royal Diamond
7 Black Diamond
```

**Example Level Ranges** (align to team standard; adjust as needed):
```
  1–99, 100–199, 200–299, 300–399, 400–499,
500–999, 1000–1499, 1500–1999, 2000–2999, 3000–3999,
4000–4999, 5000–5999, 6000–7999, 8000–9999,
10000–11999, 12000–13999, 14000–14999, 15000–15999,
16000–17999, 18000–19999, 20000–23999, 24000–24999,
25000–25999, 26000–27999, 28000–29999, 30000–34999, 35000-40000, 40000-50000, 50000-100000
```

---

## Appendix B — Redacted Sensitive Details
Where the source onboarding text included direct credentials (e.g., Tableau server username/password), this file **redacts** them. Retrieve secrets only through approved internal channels and avoid committing secrets to repos or sharing externally.

---

**Source**: Consolidated from the Slotomania BA onboarding document and team notes (see chat for citation).
