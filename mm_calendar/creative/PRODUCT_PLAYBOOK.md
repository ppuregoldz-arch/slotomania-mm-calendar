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
| Daily Deal, standard | `DD (in store)` / `store denom` | Pre-purchase offer — **no Winners Inapp**. Add Inapp/Banner only when explicitly big. |
| Spinner Clash | `Main Inapp`, `Journey Inapp`, `Banner` | **No Winners Inapp.** Match prior Spinner briefs. |
| Daily Deal, BOGO / big | `Store Denom`, `Inapp`, `Winners Inapp` | BOGO is big by default. |
| Rolling Offer | `Background`, `Banner` | Drop Denom Buy/Free unless requested. |
| RYD | `Background`, `Banner`, `Denom On`, `Denom Off` | Each denom state needs its own reference. |
| MGAP | `Main Inapp`, `Banner`, `PP Banner`, `UI` | Add Winners Inapp when relevant. |
| Gem Machine | `Banner` | Drop dynamic Inapp/Winners/push unless requested. |
| Spin Zone, light | `Banner` | Distinct from MES-linear. |
| MES SB Challenge | `Banner` | Win Master exception below. |
| Shiny Show | `Inapp`, `Banner`, `PJMS`, `Intro`, `Tooltip` | Drop Externals, Comufy, iOS Push. |
| Battlesheep Challenge | `Main Inapp`, `Theme/BO`, `Banner`, `Winners Inapp` | Drop other template assets. |
| Custom Pod | `Main Inapp`, `Winners Inapp`, `Banner` | Drop Externals and Comufy. |
| Decoy Bonanza | `Background`, `Banner`, `Denoms` | Three denoms; Big Denom is best value. |
| Gatcha / Cocktail Bonus / SB Picker | `Inapp`, `BG`, `Banner`, `PP Banner`, `UI`, `Logo Entrance`, `Header` | Pick screen needs BG/UI/Logo/Header. |
| PYP | `Inapp`, `Journey/Winners Inapp`, `Banner`, `Widget` | Main Inapp must be a true Inapp. |

## Canonical order

Creative works top-to-bottom:

`Inapp / Main Inapp` → `Background / BG / Theme/BO` → `DF` → `Denom slot` → `Banner` → `PP Banner` → remaining assets in template order.

The Denom slot includes DD store cells, Denoms, Big Denom, Denom On/Off, Store Denom, and Denom Buy/Free. Monday has no reorder mutation; ordering may require snapshotting bodies, recreating subitems in order, clearing their gate fields, then deleting originals. Treat this as a guarded mutation.

## Product rules

### Reveal Your Deal

- Put the full ordered wheel-slot list in the Background subitem.
- Repeat the exact mechanic/prize phrasing supplied by Itay across all four asset tables.
- Denom On and Denom Off use different active/muted references.
- Avoid themed or mechanic-variant RYD references unless that is the requested variant.

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

- Decoy Bonanza has three denoms; Big Denom is the best-value choice.
- Triple PO extends Double PO to three denoms. Use Double PO for layout and a separate theme cue only when needed.
- Mystery Box / any-purchase promos get one Winners subitem per prize variant.

### Reuse-source adaptation

Reuse itself is consolidated and gets no asset subitems. If an actionable label requires adapting a past execution, each affected subitem points to the exact source date/folder and states only the visible delta.

### Timers and time-limited mechanics

If the chosen source or requested mechanic is explicitly ALERT, Happy Hour, Limited Time, or otherwise countdown-based, include `Timer | yes` immediately before Reference. Never infer a timer from a family name alone.

### MES and Win Master

- A request for one explanatory MES brief becomes one comprehensive `Promo Info` or `Main Inapp` subitem; the parent remains the two-row hybrid summary.
- **Win Master exception:** when delivered through Mission Event System, open the complete MES asset set every time. Do not reduce to Banner-only from recent history.

### MGAP

MGAP price-cut means the multiplier-upgrade cost is reduced by the specified percentage; it does not mean the Gem pack is discounted.

### Gatcha / Cocktail Bonus / SB Picker

- Each purchase lets the player pick a tier, producing an escalating sale bonus.
- Cocktail Bonus Inapp/Banner/PP come from the Cocktail Bonus tree; pick-screen BG/UI/Logo/Header come from the matching Gatcha tree.
- SB Picker uses matching Gatcha Inapp/Banner/PP/UI assets.

### Pick Your Path

PYP is a complete-N-missions-to-win mechanic. Use true Inapp, journey/winners, Banner, and Widget assets; do not substitute a Banner for Main Inapp.
