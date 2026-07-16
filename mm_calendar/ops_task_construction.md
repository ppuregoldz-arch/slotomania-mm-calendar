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

Do not create a task for a calendar-only communication/amplifier row that explicitly requires no Ops config. Current exclusions inherited from the calendar uploader:

- Status Boost
- Shiny Collection calendar communications
- X2 Extreme Stamp
- X2 GGS
- Clan-Dash calendar rows

If unsure, generate a review spec with `requires_review: true`; do not silently create a live task.

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

Descriptions must read like a direct handoff from Monetization to Ops, not like a database export.

1. Open with one plain sentence saying what Ops must set up.
2. Add only the promo facts that change execution: contents, reward, price, audience, cycles, trigger, or feature behavior.
3. For a verified reuse, say **Duplicate from** and name the exact dated task/link. Follow with **Change** and **Keep** only when useful.
4. Add flow steps only for a journey, challenge, grant, or UI transition. A simple offer does not need empty Trigger/Action headings.
5. End with concrete dependencies only: config, art, MCP, economy task, list, or attached file.
6. Do not repeat the calendar source ID in prose; the `MM calendar` relation is the source connection.
7. Do not write `Production`, `Reuse: YES/NO`, generic ownership disclaimers, or filler such as “apply the current mechanic.”

### Natural description patterns

#### Daily Deal / simple purchase offer

```text
Set up a High-price Daily Deal with Coins, Gems, a 3★ Regular Card and a Hammers Wheel.

Duplicate from: Daily Deal - 8 Hammers, 2026-05-25 (item 11967559266).
Change: replace the 8 Hammers reward with the 3★ Regular Card + Hammers Wheel.

MCP required for the card.
```

#### Rolling / RYD / Buy All / Decoy

```text
Set up a 6-cycle Mid-price Rolling Offer.

Duplicate from: Rolling Offer 6 Cycles - M Price, 2026-05-31 (item 12104594749).
Keep: 12-hour timer, login + banner triggers, X button and banner removal after purchase.
Change: use the current six-cycle config and approved rewards.

Config is attached; art is in PM.
```

#### M.E.S / gameplay challenge

```text
Set up Win Master in M.E.S for all eligible players.
Players complete the configured win requirement to receive a 3★ Regular Card + Pick a Boom.

Banner opens M.E.S. Remove it after the challenge is completed and show the winner inapp.
Duplicate the full latest matching Win Master M.E.S task; update the mission and reward across the complete asset/config set.

MCP required for the card.
```

#### Grant / segmented benefit

```text
Give 10 Parasheep Tokens directly to the balance of eligible Black Diamond players.

Trigger: player logs in.
Condition: Black Diamond segment.
Action: grant 10 tokens and show the attached winner inapp.
```

#### LBP / Night Plan

```text
Open Lotto Bonus Premium with every ball value increased by 30%.

Duplicate from: LBP - all balls 40% bigger, 2026-05-09 (item 11936779021).
Change: 40% → 30%.
Keep: the existing Bigger Balls config and matching UI by segment.
```

For more real examples, start at `documentation/ops_task_refs/README.md`. These examples preserve the team's writing voice; old dates/times shown in source examples must not be copied into new Descriptions.

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

### Core / challenge

- Eligible machines and exclusions.
- Requirement parameter and minimum-bet parameter when known.
- Exact prize and MCP.
- Once/Multiple; free-spin/re-spin exclusions.
- Full progression: triggers, actions, widget states, winner inapp, banner/news-feed behavior, CTA parameter.
- Unknown parameters stay TBD; do not invent them from a different Core mechanic.

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
- Use `M&M Completed` only when Monetization supplied an execution-ready definition.
- Use the most specific current blocker status when one exists: `Missing MCP`, `Missing art`, `Missing Art+Config`, `Missing Config`, `Missing List`, `Missing Test Groups`, `Waiting for economy`, or `More Info required`.
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
