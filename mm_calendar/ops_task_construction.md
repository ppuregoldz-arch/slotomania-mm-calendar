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
- Lotto peak and LBP rotation rows
- Shiny Collection calendar communications
- X2 Extreme Stamp
- X2 GGS
- Clan-Dash calendar rows

If unsure, generate a review spec with `requires_review: true`; do not silently create a live task.

Season rows create work only on `isFirst`. Daily promos create work on their scheduled day. Backup items are excluded.

## Required fields

Before a task is ready for Ops, confirm:

- Correct parent day.
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
- Night Plan uses `00:00 UTC` only when the source explicitly says Night Plan.
- Never copy the historical March `12:00 UTC` convention into August.
- Write the same dates into `date_mm0f8tdb` and `date_mm0fr8sp`; the Description carries exact UTC times.

## Naming

Because the parent already names the date, use a concise operational subitem name:

```text
Daily Deal - 3* Reg Card + Hammers Wheel - Max Price
Rolling Offer - Buy More for Less - High Price
Win Master - 3* Reg Card + PAB
Blast - New Season
```

Normalize symbols only for readability (`★` may remain `★`). Do not prepend the date to subitem names. Keep segment/test qualifiers that change execution.

## Description skeleton

```text
Production
Start: <YYYY-MM-DD HH:MM UTC>
End: <YYYY-MM-DD HH:MM UTC>

Audience: <confirmed audience or All eligible players>
Mechanic: <execution instruction>
Pricing: <High / Max / Mid / Low, if applicable>
Prize / contents: <exact source text>
Times per player: <Once / Multiple / TBD>

Journey / flow:
Trigger: <confirmed trigger or TBD>
Condition: <confirmed condition or n/a>
Action 1: <confirmed action or TBD>
Action 2: <confirmed action or n/a>

Surfaces / CTA:
<confirmed surfaces and CTA, or TBD>

Dependencies:
- Config: <attached / reuse from date / TBD>
- Art: <attached / PM task / reuse from date / not required / TBD>
- MCP / Economy / BA list / Payment: <IDs or TBD>

Source: MM calendar <date> - <source row name>
Recent Ops reference: <date + item ID/link, or no recent precedent>
Reuse: <Yes/No> - <exact reused scope and current changes>
```

For simple offer tasks, omit journey blocks that are genuinely unnecessary. Do not add generic triggers or CTA behavior merely to fill the template.

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
Times per player: Multiple.
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

## Status defaults

For generated review specs:

| Condition | Operation Status |
|---|---|
| Complete draft, not started | `To Do` |
| Required config absent | `Missing Config` |
| Required art absent | `Missing art` |
| Both absent | `Missing Art+config` |
| Card/reward MCP absent | `Missing MCP` |
| Audience/parameter/reward unclear | `More Info required` |

The builder does not mark `Scheduled`, `QA Done`, `Done`, or `M&M Completed` as an operational fact. Those are human/automation lifecycle outcomes.

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
- Do not create a missing day parent unless `--create-day` is explicitly supplied with `--commit`.
- Creating/updating a task does not authorize comments, assignees, links, files, or statuses beyond the reviewed spec.
- Show warnings for every TBD and unsupported calendar row.
