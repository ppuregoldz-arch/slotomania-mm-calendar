# Creative Brief Product Playbook

**Last updated:** July 2026  
**Scope:** Default asset scope and product-specific rules for non-Reuse briefs.

Explicit instructions from Itay override these defaults. Reuse promotions do not use this playbook: consolidate them into the day-level `REUSE - No Creative Action` item.

## Inapp types

- **Main inapp** — entry/hub and prize strip.
- **Journey inapp** — mid-event progress, rank, or interim prize frames.
- **Winner inapp** — end state: results, podium, claim, visible payout.

**Winner inapp rule:** Include **Winners Inapp** only when this playbook or a prior brief lists it (Piggy break, Battlesheep, Custom Pod, PYP, etc.). **Do not** add Winners Inapp for **Daily Deal** store offers (pre-purchase), **Spinner Clash** (Main + Journey + Banner only), or other store/denom-first offers unless Itay asks. **Card-only** payouts: omit Winner inapp.

## Default actionable subitems

| Product | Keep by default | Notes |
|---|---|---|
| Daily Deal, standard | `DD (in store)` / `store denom` | Pre-purchase — **no Winners Inapp**. Store denom only unless the offer mixes **SB + hammers** (see next row). |
| Daily Deal, SB + hammers | `store denom`, `Inapp` | Same visible reward on store card and inapp hub; **no Winners Inapp** (pre-purchase). Match prior DD+SB briefs (`Inapp` subitem name). |
| Spinner Clash | `Main Inapp`, `Journey Inapp`, `Banner` | **No Winners Inapp.** Match prior Spinner briefs. |
| Daily Deal, BOGO / big | `Store Denom`, `Inapp`, `Winners Inapp` | BOGO is big by default. |
| Rolling Offer | `Background`, `Banner` | Drop **Denom Buy**, **Denom Free**, and generic buy/free denom slots unless Itay explicitly requests them. When MM embeds an **MGAP ladder** (name/description mentions MGAP + ladder/denom), add **`MGAP denom`** subitem only — brief it with a named line (e.g. `Build MGAP denom 3 (cycles 2–4; new for this Rolling promo).`). |
| RYD | `Background`, `Banner`, `Denom On`, `Denom Off` | Each denom state needs its own reference. |
| MGAP | `Main Inapp`, `Banner`, `PP Banner`, `UI` | Add Winners Inapp when relevant. |
| Gem Machine | `Banner` | Drop dynamic Inapp/Winners/push unless requested. |
| Spin Zone, light | `Banner` | Distinct from MES-linear. |
| MES SB Challenge | `Banner` | Win Master exception below. |
| Shiny Show | `Inapp`, `Banner`, `PJMS`, `Intro`, `Tooltip` | Drop Externals, Comufy, iOS Push. |
| Battlesheep / Blast (default) | `Main Inapp`, `Banner`, `Winners Inapp` | Strip **Challenge** from brief titles unless MM **description** defines a season challenge. No Theme/BO, Journey, Wheel UI, or Wedges subitems. |
| Battlesheep / Blast (season challenge) | `Main Inapp`, `Theme/BO`, `Journey Inapps`, `Banner`, `Winners Inapp` | Subitem table may include **`SKU`** row when MM defines the challenge reward SKU. |
| Golden Spin | Template defaults (Main Inapp, Banner, arena assets) | **Coin-value Mega Bonus wheel** — not Gem Machine / timed Gems ALERT. Use **Theme** when MM names a skin; **Hook** when MM states the variant (e.g. **`30% Bigger Wedges`**). Never label “timed gem feature” in brief text. |
| Gems Coupon | `Inapp` | Use the designer-uploaded Inapp preview on source pulse `11415353948`; no `store denom`. |
| Prize Mania | Template asset set (usually `Banner`) | The visible prize list is the Hook. Pricing is never Creative copy or a Hook. |
| Custom Pod | `Main Inapp`, `Winners Inapp`, `Banner` | Drop Externals and Comufy. |
| Gatcha / Cocktail Bonus / SB Picker | `Inapp`, `BG`, `Banner`, `PP Banner`, `UI`, `Logo Entrance`, `Header` | Pick screen needs BG/UI/Logo/Header. |
| PYP | `Inapp`, `Journey/Winners Inapp`, `Banner`, `Widget` | Main Inapp must be a true Inapp. |

## Canonical order

Creative works top-to-bottom:

`Inapp / Main Inapp` → `Background / BG / Theme/BO` → `DF` → `Denom slot` → `Banner` → `PP Banner` → remaining assets in template order.

The Denom slot includes DD store cells, Denoms, Big Denom, Denom On/Off, Store Denom, and Denom Buy/Free. Monday has no reorder mutation; ordering may require snapshotting bodies, recreating subitems in order, clearing their gate fields, then deleting originals. Treat this as a guarded mutation.

## Product rules

### Rolling Offer

- Default actionable scope: **Background** + **Banner** only.
- **Never** auto-create **Buy denom**, **Denom Buy**, **Denom Free**, or combined buy/free denom subitems.
- When the calendar row includes an **MGAP ladder** (MGAP + ladder/denom in name or Description), add one **`MGAP denom`** subitem. **What to change** must name the denom (e.g. **MGAP denom 3**) and cycles when MM specifies them — not generic “apply parent Change” text.
- **Background** theme work: plain hook lines (e.g. “Make the MGAP ladder the main visual hook of this Rolling offer.”), not Task/Keep pointer rows.

### Reveal Your Deal

- Put the full ordered wheel-slot list in the Background subitem.
- Repeat the exact mechanic/prize phrasing supplied by Itay across all four asset tables.
- Denom On and Denom Off use different active/muted references.
- Avoid themed or mechanic-variant RYD references unless that is the requested variant.

### Battlesheep / Blast

- Default brief scope: **Main Inapp**, **Banner**, **Winners Inapp** — prize/theme from MM name (e.g. `Wild Gold · Betty theme`), not challenge template assets.
- **Season challenge** (ships, journey progress, wheel UI, etc.) applies only when MM **Description** states that mechanic — not when the MM product name says “Challenge”.
- **`SKU`** table row: only on challenge weeks, populated from the visible reward SKU in MM.

### Buy All

- Background prize row: non-currency prizes only, joined with ` · `.
- Banner prize row: top four prize names only, joined with ` · `.
- Coins/Gems splits belong only in the Denoms subitem.

### Coin / Mixed / Gem Sale

- Coin and Mixed start from the Coin Sale structure.
- Single-day Coin/Mixed default set: `Main Inapp`, `Coupon Inapp`, `Preloader`, `DF`, `ROOC`, `Banner`, `PP Banner`, `Store Assets`; remove copied duplicates.
- Main Inapp, PP Banner, and DF use a four-version grid: `PU`, `IC`, `DPU`, `NPU`.
- Preserve intentional wording: PU/IC may say `up to N%`; DPU/NPU flat values remain flat.
- `ROOC` means Run-Out-Of-Coins PO; `ROOG` means Run-Out-Of-Gems PO.
- Mixed Sale DF uses both Coin and Gem DF references when no native mixed DF exists.
- Store Assets includes the complete CTA/cell-skin folder and denomination icons.

### Decoy, Triple PO, and Mystery Box

- **Decoy Bonanza / multi-denom decoy:** do **not** create Monetization-Art briefs — offers are **single** in calendar scope; no Background + three-denom brief structure.
- Triple PO extends Double PO to three denoms. Use Double PO for layout and a separate theme cue only when needed.
- Mystery Box / any-purchase promos get one Winners subitem per prize variant.

### Reuse-source adaptation

Reuse itself is consolidated and gets no asset subitems. If an actionable label requires adapting a past execution, each affected subitem points to the exact source date/folder and states only the visible delta.

### Timers and time-limited mechanics

If the chosen source or requested mechanic is explicitly ALERT, Happy Hour, Limited Time, or otherwise countdown-based, include `Timer | yes` immediately before Reference. Never infer a timer from a family name alone.

**Golden Spin** is not in this bucket — it is not Gem Machine and not a Gems timed ALERT; do not add `Timer | yes` or “timed gem” language for Golden Spin unless MM explicitly requests a countdown on a specific asset.

### MES and Win Master

- A request for one explanatory MES brief becomes one comprehensive `Promo Info` or `Main Inapp` subitem; the parent remains the two-row hybrid summary.
- **Win Master exception:** when delivered through Mission Event System, open the complete MES asset set every time. Do not reduce to Banner-only from recent history.

### MGAP

MGAP price-cut means the multiplier-upgrade cost is reduced by the specified percentage; it does not mean the Gem pack is discounted.

Standalone MGAP **basic UI** work uses exactly one subitem named `MGAP UI`. Do not label or scope it as `Full theme UI` unless MM explicitly requests a full-theme execution.

### Gatcha / Cocktail Bonus / SB Picker

- Each purchase lets the player pick a tier, producing an escalating sale bonus.
- Cocktail Bonus Inapp/Banner/PP come from the Cocktail Bonus tree; pick-screen BG/UI/Logo/Header come from the matching Gatcha tree.
- SB Picker uses matching Gatcha Inapp/Banner/PP/UI assets.

### Pick Your Path

PYP is a complete-N-missions-to-win mechanic. Use true Inapp, journey/winners, Banner, and Widget assets; do not substitute a Banner for Main Inapp.
