# Operational task construction guidelines

**Last updated:** July 2026  
**Board:** `Operation - Monetization` (`2109172490`)  
**Schema:** `ops_board_schema.md`

## Purpose and authority

Turn an approved MM calendar row into an execution-ready Ops subitem under the correct day. This is a handoff transformation, not a second calendar planner.

Authority order:

1. Itay's live instruction.
2. Approved live MM calendar row (Name is authoritative when it conflicts with Description).
3. Current plan JSON and monthly guidelines.
4. Same-promo historical Ops execution from the **latest 3 months only**, newest relevant task first.
5. Generic template.

Never infer a missing business rule, parameter, segment, reward, ID, owner, file, or status. A draft may contain `TBD - owner required`; an executable task may not.

## Historical-reference freshness

- Search only the 3 calendar months immediately before the target task date. For 1 August 2026, valid references start on 1 May 2026.
- Within that window, use the newest task matching the same promo, variant, pricing, audience, and intended behavior.
- A newer exact-variant task overrides an older generic template.
- Do not combine mechanics, parameters, files, or journeys from several old tasks into a synthetic task.
- If no relevant task exists in the 3-month window, write `No recent Ops precedent found (3-month window)` and keep unsupported fields as TBD.
- A task marked `Reuse` must state the exact source task date, item ID/link, what is reused, and what changes in the current instance.
- Never describe a task as Reuse solely because the MM Creative Label says `Reuse`; verify a recent matching Ops execution.

## Placement model

All dated production tasks are **subitems of the matching `YYYY-MM-DD` day parent** in `Monday days` (`group_mm0t6mxh`). Offer-type groups are template/reference sources, not production destinations.

| Calendar Product / pattern | Historical template group | Production placement |
|---|---|---|
| Daily deal | Daily Deal | Subitem under day |
| Rolling offer | Rolling Offer | Subitem under day |
| RYD | RYD | Subitem under day |
| Buy all | Buy All | Subitem under day |
| Decoy / Bonanza | Triple Offer- Decoy | Subitem under day |
| Equal triple offer | Triple Offer- Equal offers | Subitem under day |
| Limited PO | Limited PO | Subitem under day |
| MGAP | MGAP | Subitem under day |
| ADS | PO ADS | Subitem under day |
| Mid Term / Short Term opening | Mid Term | Subitem under start day |
| Album handover/opening | Album handover | Subitem under start day |
| Core / gameplay / sale / other config | No single template group | Subitem under day; use recent same-promo history |

## Decide whether an Ops task exists

Create a task when Ops must configure, open, schedule, rotate, award, target, publish, QA, or close something.

Do not create a task for a calendar-only communication/amplifier row that explicitly requires no Ops config. Default exclusions:

- Status Boost
- Shiny Collection calendar communications
- X2 GGS
- Clan-Dash calendar rows

**X2 Extreme Stamp:** create a separate Ops task when the MM calendar row is present. Description is **`Segment:`** plus a **`don't forget UI`** line (no Variant). Stamp-slot pairing with Rolling belongs in the Rolling task text, not here.

**MGAP promotions:** after `Segment` / `Variant`, include a UI reminder in Description — use **`Make sure to set UI for both Extreme + Epic`** when the mechanic applies to both tiers; otherwise **`don't forget UI`** (same voice as historical MGAP UI subitems).

**X2 GGS:** default calendar-only exclusion (no Ops task). Composer supports UI lines if a task is ever generated.

If unsure, generate a review spec with `requires_review: true`; do not silently skip a row Monetization expects on the Ops board.

Season rows create work only on `isFirst`. Daily promos create work on their scheduled day. Backup items are excluded.

When a calendar day contains both Lotto peak and LBP for Night Plan, create **two separate Ops tasks** under that calendar day's parent: one for Lotto peak and one for the LBP mechanic. Their production window is on the following date from `00:00 UTC` through `11:00 UTC`, and both use M&M Status `Night Plan`. Example: tasks under parent `2026-08-01` run on `2026-08-02` from 00:00 to 11:00.

## Required fields

Before a task is ready for Ops, confirm:

- Correct parent day.
- `MM calendar` relation connected to the exact approved source row, not merely mentioned in Description.
- Exact name/mechanic.
- Production Start and End in UTC.
- Audience and exclusions, or `All eligible players`.
- Exact mechanic/config behavior.
- Exact prizes/SKUs and pricing where relevant.
- Once vs Multiple.
- Trigger, conditions, actions, surfaces, CTA, reset/removal behavior where relevant.
- Dependencies: config, art, MCP, economy task, BA list, payment task, test groups.

The plan-driven builder can draft only what exists in the source plan. Missing execution fields stay visible as TBDs.

## Time rules

- August 2026 Promo Time is **11:00 UTC**.
- A standard calendar-day task runs from `YYYY-MM-DD 11:00 UTC` to the following day at `11:00 UTC`.
- An inclusive calendar range ends at 11:00 UTC on the day after its final listed date.
- Night Plan uses `00:00–11:00 UTC` on the date following its calendar-day parent.
- Never copy the historical March `12:00 UTC` convention into August.
- Write scheduling dates and exact clock times only into `date_mm0f8tdb` and `date_mm0fr8sp`.
- Do not repeat production dates, start/end times, reset times, or date ranges in Description.
- The Ops board renders API date-times at UTC+3. Compensate the API payload by 3 hours so the visible Start/End values equal the intended UTC schedule (for example, write `08:00` so the board shows `11:00`; write the previous day at `21:00` so the board shows `00:00`).
- Standard promo window: 11:00 UTC to 11:00 UTC the next day. Time-limited and Night Plan tasks use their exact approved hours.
- When MM confirms a **time-limited** promo but **does not** state exact start/end clocks, assign start from a **stable** pick (hash of parent day + MM item id) among **14:00, 16:00, 17:00, or 21:00 UTC**. Infer duration from MM text (`for 1 hour`, `5 hours`, etc.); if still unknown, default **1 hour** and record a warning in the spec/worklog.
- Prefix or embed that UTC start in the Ops subitem **title** (for example `14:00 UTC - HH - Coins & Gems sale on DD purchase`). Do **not** repeat start/end in Description.
- Do **not** override rows that already carry an explicit title prefix (`HH:MM UTC - …`) or parseable UTC clocks in the MM Description.

## Naming

Because the parent already names the date, use a concise operational subitem name:

```text
Daily Deal - 3* Reg Card + Hammers Wheel - Max Price
Rolling Offer - Buy More for Less - High Price
Win Master - 3* Reg Card + PAB
Blast - New Season
```

Normalize symbols only for readability (`★` may remain `★`). Do not prepend the date to subitem names. Keep segment/test qualifiers that change execution.

## How to write the Description

Do not explain the product and do not mention Reuse, Prize Change, source tasks, or current deltas in Description. Those belong in M&M Status/reference metadata.

**No internal repo references in Description** — omit paths (`mm_calendar/…`), Nivi prize-table filenames, “Full tables: …”, “Collector's Album phase …” boilerplate, “Configure ranks in LiveOps per …”, and similar agent/calendar notes. Ops only needs segment, prizes, pricing, triggers, and execution fields the team configures in LiveOps.

**Field order is fixed.** Do not repeat pricing inside prize text (no `Central reward`, no `(High Pricing)` in prizes).

### Standard offers (Daily Deal, RYD, Buy All, Decoy, Limited PO, Prize Mania, Counter PO)

```text
Reset at 00:00 UTC   ← main offers only; not Daily Deal, RLAP, or ADS

Segment: …
Prizes: …
Pricing: …
```

Daily Deal uses the same **Prizes / Pricing** shape but **no** reset line and defaults to **Multiple** in Times per player.

### ADS Personal Offer

```text
Segment: ADS Segment
Prizes: <exact ad grant — no Pricing line>
```

### Store / Gem / Coin sales

**Sale** (store vs offers split — name or MM text mentions store/offers):

```text
Currency: Gems | Coins
Segment: PU
Amount: <store%> store | <offers%> offers
Segment: PRAS
Amount: <PU+bonus> (<PU>+<bonus>) store | <PU+bonus> (<PU>+<bonus>) offers
```

Regular segmented **sales**: **+20** on each PU component for **Gems** PRAS; **+25** on each PU component for **Coins** PRAS (unless MM calendar overrides).

**Coupon** (task name contains *coupon* — single PU and PRAS amounts, no store/offers split, no PRAS bonus math):

```text
Currency: Gems | Coins
Segment: PU
Amount: <PU%>
Segment: PRAS
Amount: <PRAS%>
```

Example: `Gems coupon 20%/40%` → PU **20%**, PRAS **40%** (not store 20% / offers 40%).

### RLAP / Stash Booster

```text
Segment: All Users
Trigger: Eligible offers: <Daily Deal + main offer names from MM>
Prize:
<segmented CZ reward lines from MM — no Pricing>
```

**Times per player:** leave blank for **Short Term / Mid Term / Season** rows (and other seasonals). Do not set Once/Multiple on those tasks.

### Rolling Offer

```text
Reset at 00:00 UTC

Segment: <segment>
Pricing: <High / Mid / Max / Low>
Denoms:
Cycle 1:
<denom#> Pay: <contents>
<denom#> Free: <contents>

Cycle 2:
…
```

Leave a **blank line** between each `Cycle N:` block in Description for readability.

### Machine full launch (new slot)

Follow prior Ops launch tasks (e.g. Sweet Ambrosia / Wild Goddesses / Rich's Riches playbook):

```text
Segment: All Users
Action:
Open the new machine to all players:
1. Widget — open Main Inapp (Reg / Scrolldown / UV per approved creative)
2. Add the machine to Figz and Winovate playlist
3. New Machines DF — Big (Day 1+2) and Small (Day 3)
4. CTA Reg → machine · UV → app store / Google Play
```

Art references stay in Monetization-Art / PM — not repo paths in Description.

### Spinner Clash

Match historical Ops (e.g. 2026-05-27): **4 × 6hr tournaments** in 24h, config in economy task, rank **Prize:** lines from MM Name/Description. **Times per player:** **Multiple** (same as recent Ops builds).

### Variant promos (MGAP, Shiny Show, Golden Spin, Dice, LBP / Lotto)

```text
Segment: <segment>
Variant: <mechanic variant from MM calendar — not the promo title alone>
```

### All other promos (Core, MES, Piggy, season rows, etc.)

**M.E.S / MES** — use the dated template voice. **Sub title** comes **only** from an explicit `Sub title - …` line in MM Description (never from the row Name). If MM has no Sub title (Win Master, Spin Zone, and other types reuse prior art as-is), **omit** the Sub title block and set **M&M Status** to **Missing art** (or **Missing Art+Config** when Config is also needed). Do not copy the MES timeframe/duration into Description; scheduling belongs only in Start/End columns. When MM supplies milestones, preserve its mission and prize text and format each one as a semantic pair:

```text
Segment: <segment>
banner - open M.E.S

Sub title - <only when MM Description includes it>

Milestone 1:
Mission: <mission / trigger from MM Description>
Prize: <prize from MM Description>

Milestone 2:
Mission: …
Prize: …
```

```text
Segment: <confirmed segment; if none, All Users>
Trigger: <what the player must do — omit the whole line if unknown>
Prize: <single reward or prize bundle — not the promo title>
```

For tournament / rank features (Spinner Clash, Battlesheep, SNL, Blast, Winovate, etc.), list rank rewards from MM calendar / economy guidelines under **Prize:** (one rank per line when applicable).

Start/End date **and time** live only in the Start date / End date columns (UTC in API; Monday may display local). **Ops subitem titles:** use promo name only — no `YYYY-MM-DD` prefix (clock prefix like `00:00 UTC - RLAP` is OK). **Night Plan / 00:00 UTC:** production starts **calendar day + 1** at **00:00 UTC** through **11:00 UTC** that day; Monday Start column shows that date at **12:00 AM** (no display offset shift). **Times per player:** **main offers** (Rolling, RYD, Buy All, Decoy, Limited PO, Prize Mania, Counter PO — **not** Daily Deal) and **Piggy** default to **Once**; **Win Master** → **Once**; **Daily Deal** and other promos default to **Multiple** unless MM calendar text says otherwise; **machine full launch** and **Short/Mid Term / Season** → leave **blank**. **Spinner Clash** follows recent Ops precedent (**Multiple**). Main-offer descriptions start with **`Reset at 00:00 UTC`** (then a blank line, then Segment…). Do not repeat dates or Once/Multiple inside Description.

## Duplicate-from source map

“Duplicate” means duplicate the closest verified task structure, then change the instance-specific fields. It never means copy an entire old description unchanged.

| Promo family | Preferred source | Safe to carry forward | Must be checked or changed |
|---|---|---|---|
| Daily Deal | Newest exact reward + pricing task; fallback group `Daily Deal` (`group_mkv1971m`) | DD shell and standard Coins/Gems structure | Central rewards, pricing, MCP, Once/Multiple |
| Rolling Offer | Newest exact variant/cycle task; fallback `Rolling Offer` (`group_mkv1b6ky`) | Variant flow, verified triggers, timer, close/removal behavior | Cycles, rewards, pricing, MGAP tie-in, audience |
| RYD | Newest exact SB/reward/pricing task; fallback `RYD` (`group_mkv1q8yw`) | Reveal flow and verified shell | Hook reward, SB %, pricing, segment, reset/trigger |
| Buy All | Newest matching denom layout; fallback `Buy All` (`group_mkv12864`) | Multi-denom structure | Coins/Gems denoms, rewards, pricing, reset |
| Decoy / Bonanza | Same test structure; fallback `Triple Offer- Decoy` (`group_mkzvt95x`) | Three-offer layout and test framework | Each denom, decoy position, rewards, test groups |
| Equal triple offer | Same structure; fallback `Triple Offer- Equal offers` (`group_mm0928d4`) | Equal-offer layout only | Denoms, rewards, segment allocation |
| Limited Personal Offer | Same offer type; fallback `Limited PO` (`group_mm4h2685`) | Verified limited-offer shell | Reward, price, eligibility, cap/timer |
| MGAP | Newest exact mechanic (Matched/BOGO/Bigger/etc.); fallback `MGAP` (`group_mkv1vqxx`) | Only the same mechanic's flow | Eligible tiers, mapping, UI, reward, frequency |
| ADS Personal Offer | Same prize type; fallback `PO ADS` (`group_mm15y5em`) | Ad-watch grant flow | Prize, eligibility, frequency, season context |
| RLAP / Stash Booster | Newest exact RLAP task | Stash Booster configuration and verified purchase flow | Reward pool, price/segment, art/config version |
| Sticker Sources | Previous source-list day only when the inapp structure matches | Inapp layout and source-list structure | Exact daily sources, order, art, album phase |
| M.E.S | Newest exact M.E.S mechanic from a dated day task | Banner→M.E.S entry and only verified completion behavior | Mission, parameters, reward, audience, full config/asset set |
| Clan Dash | Newest task for the same Clan Dash component | Only the same bar/wheel/pass component | Reward SKU, bar placement, segment, attached economy config |
| Core / gameplay | Newest exact feature and variant | Feature-specific triggers/actions only | Machines, exclusions, effort, min bet, rewards, winner flow |
| Shiny Show | Newest exact Shiny mechanic/reward setup | Floor/config structure only when identical | Reward pool, floors, Joker/special rules, art/UI |
| Season / Blast | Same season mechanic; fallback `Mid Term` (`group_mky2tww7`) | Journey SKU behavior only when identical | Theme, cycle rewards, SKU grants, winner messages |
| Album opening/handover | `Album handover` (`group_mkx57gcq`) | Verified opening/handover checklist | Album name, audience, rewards, exact opening state |
| LBP / Lotto | Newest exact LBP variant or Lotto Peak task | Exact config type and segment UI mapping | Percentage/ball count, segments, UI; keep Lotto and LBP separate |
| Sales / store | Newest same sale/store mechanic | Store surfaces and verified exclusions | Percent by segment, denoms, Coins/Gems values, payment-page scope |

If no exact task exists in the valid three-month window, point to the template group and leave unsupported execution details as `TBD - owner required`. Do not present a generic template as a verified reuse.

## Product-specific minimums

### Daily Deal

- Start/end, exact central reward and base contents from source.
- Pricing tier.
- Once/Multiple.
- If Wild or Shiny Limited is once-per-player, describe replacement DD behavior only when the source confirms it.
- MCP dependency for card delivery must be linked or marked TBD.

```text
Daily Deal: Coins + Gems + <central reward>.
Pricing: High.
```

### Rolling Offer

- Variant: BXGY, BMFL, Supersized, etc.
- Number of cycles and exact per-cycle structure from `rolling_offer.md`/source.
- Pricing, timer/reset behavior, Once/Multiple.
- Banner removal and CTA only when historical/source evidence supports them.

BMFL is exactly 3 cycles and High pricing. Never substitute the deprecated Free1/Free2 stamp model.

### RYD

- Hook prize, SB percentage, pricing.
- RDS/Extreme conversion where applicable.
- Reveal/animated-frame journey only when included in the approved instance.
- Never use 155% SB.

### Buy All

- Separate Coins and Gems denoms.
- List exact rewards per denom and pricing.
- State reset and Once/Multiple only when confirmed.

### Decoy / triple offer

- Write denom 1, denom 2, denom 3 separately.
- Preserve test-group/segment allocation.
- State which denom is the decoy and all on-top rewards.

### MGAP

- Exact mechanic: BOGO, Matched, Bigger, Wild Symbols, Guaranteed, etc.
- A BOGO task must explicitly say the BOGO config must be opened.
- Include eligible tiers, multiplier/reward mapping, UI/config dependencies, Once/Multiple when known.
- Description must include the UI reminder line(s) above — do not rely on a separate UI-only subitem unless Ops asks for one.

### Core / challenge

- Eligible machines and exclusions.
- Requirement parameter and minimum-bet parameter when known.
- Exact prize and MCP.
- Once/Multiple; free-spin/re-spin exclusions.
- Full progression: triggers, actions, widget states, winner inapp, banner/news-feed behavior, CTA parameter.
- Unknown parameters stay TBD; do not invent them from a different Core mechanic.

### Ace Heist / PYP mission source

- Ace Heist uses a linear three-mission flow: each completion advances the progress/winner inapp and widget; final completion grants the prize and closes the active journey surfaces.
- The flow is reusable, but the mission content and values are not. For both Ace Heist and PYP, read the exact current missions from the approved Monday row (or approved plan Description when the live row is title-only).
- Ops Description template:

```text
Segment: All Users
Missions:
1. <mission 1>
2. <mission 2>
3. <mission 3>
Flow: Linear three-mission Ace Heist — after each mission show winner inapp and update widget; after mission 3 grant the final prize and close banner / NF / journey surfaces
Prize: <final card/reward from row title>
```

- Put those current missions in numbered **Missions** lines (not a single Trigger line). Never copy historical values such as Spin 30/50/100 or Open 5/8 Pods as defaults unless they appear on the approved row.

### Golden Spin

- Golden Spin is a coin-value feature, not a Gems feature.
- Keep that classification internal; Description uses the non-offer schema: Segment, Trigger (if confirmed), Prize.

### ADS PO

- Exact low-tier prize and active season context.
- Ad-watch eligibility and Once/Multiple if known.
- ADS is a separate product, not Daily Deal.

### Season opening / handover

- Internal window only when explicitly scheduled.
- Production start/end.
- Open-to audience.
- Config source, playlist, theme/reuse date.
- Exact season rewards from approved monthly guidelines.

### Sales and store configuration

- Exact percentage by segment and surface (store/offers/payment page).
- Explicit exclusions (for example SlotoBucks denoms).
- Communication/store-asset scope.
- Do not infer percentages from a generic `Coin Sale` calendar row; mark them TBD.

## Status ownership

- **Never write Operation Status** (`dup__of_m_m_status1`). Leave it blank; Ops owns this lifecycle.
- The agent owns `M&M Status` and may set it according to handoff completeness.
- Use **`Waiting for MM Approval`** when Monetization handoff is execution-ready on the **config/MCP** side (calendar `Config`/`MCP` done or not required, Description complete). This replaces **`M&M Completed`** for newly built tasks — Ops still owns Operation Status.
- Use the most specific current blocker status when one exists: `Missing MCP`, `Missing art`, `Missing Art+Config`, `Missing Config`, `Missing List`, `Missing Test Groups`, `Waiting for economy`, or `More Info required`.
- **`More Info required`** only when the composed Ops Description still lacks execution-critical fields **and** the MM **Name** cannot supply them (empty Description alone is not enough to block). Use **`Waiting for MM Approval`** when `Config` is Done (or not required) and handoff is sufficient from **Name + Description**, including: **Daily Deal** prizes parsed from the title; **Win Master** prize/trigger from the title (`mes` family); **machine full launch** launch checklist template; **Spinner Clash** rank prizes / tournament copy from Name or Description.
- Use `Night Plan` for a task explicitly scheduled in the Night Plan window.
- Use `MM Work in Progress` only when Monetization is actively drafting and no more specific blocker label applies.
- Never use M&M Status to claim that Ops configured, scheduled, QA'd, or completed the promo.
- Put `Once` / `Multiple` only in the dedicated `Times per player` column. Do not repeat it in Description.

## Comments and QA

Post comments only when explicitly requested.

Change comment:

```text
Correction for <task>:
1. <old -> new>
2. <old -> new>
Effective from <timestamp UTC>.
The previous file remains for history; use <new file/version>.
```

QA comment:

```text
QA completed for <promo/date>.
Checked: <sample and method>.
Expected: <requirements>.
Result: <pass/fail and evidence>.
Open issues: <none/list>.
```

Never pre-write a success claim or fake a spot-check count.

## Builder and writer safety

- Build only after Itay explicitly asks for a day.
- Dry-run is the default.
- One day at a time.
- Add/update only; never delete or archive.
- Match within the parent day by normalized task name.
- Write and verify `board_relation_mkzvrve9` against the task's `source_mm_item_id`; query `BoardRelationValue.linked_items` for verification because the generic column `text` and `value` fields can be null even when the relation is connected.
- Do not create a missing day parent unless `--create-day` is explicitly supplied with `--commit`.
- Creating/updating a task does not authorize comments, assignees, links, files, or statuses beyond the reviewed spec.
- Show warnings for every TBD and unsupported calendar row.
- For an approved description-only repair of existing tasks, use `upload_ops_task_monday.py --commit --update-existing --description-only`; this updates only `long_text` and refuses missing tasks.
