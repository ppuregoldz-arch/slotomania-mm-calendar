# Stash Booster — calendar & ops guidelines (post–Full Launch)

> **Status:** Product live (FL). **Until further notice:** always **2 configs + 2 comms** (CZ segments).  
> **Monday board alias:** rows may appear as **RLAP** / **RLAP - Full Launch** — treat as **Stash Booster** tasks unless explicitly another product.  
> **Updated:** July 2026 (ops mail post-FL)

**Router:** `BUILD_CALENDAR_ROUTER.md` · **Conflicts:** `constraints.md` §6 · **Visual shell:** same background/denoms as **Rolling Offer** (`rolling_offer.md`)

---

## What it is

**Stash Booster** is a **purchase-side coin multiplier** layered on selected offers when the player buys through the **full cycle** of those offers. It is **not** MGAP: eligible MGAP purchases elsewhere must **still trigger MGAP** unchanged.

**Trigger offers (exactly 2 per Stash day):**

1. **Daily Deal** (that day’s DD)
2. **Main offer of the day** — typically the **second VFM offer** (not Clan-Dash / Dash Pass)

---

## When to use (recommended)

| Pairing | Notes |
|---------|--------|
| **RYD / Decoy Bonanza** | **Recommended** default |
| **Buy All / Mystery Buy All** | Allowed |

**Economy context (HARD for planning):**

- Same day **and the following days** must include **balance-draining** promotions (coin sinks / consumption — Core challenges, spins, etc.). Do not run Stash Booster into a “soft” drain window.

**Cadence:** **≤ once per week** (recommended).

---

## When NOT to use (HARD)

| Do not combine Stash Booster day with | Reason |
|---------------------------------------|--------|
| **Rolling Offer** (any BXGY / BMFL / Supersized) | Product rule post-FL |
| **MGAP promotion row that day** | **Stash Booster replaces MGAP for that calendar day** — do not also schedule BOGO / Matched / Wild / Bigger / etc. |

### Stash day ↔ MGAP (planning rule — Itay)

**On days Stash Booster is live, it replaces MGAP** in the calendar slot: you run **Stash**, not a separate **MGAP promo** for that day.

- **Other MGAP-eligible purchases** (offers not wired to Stash) must **still trigger MGAP** in LiveOps — Stash does not remove MGAP from the whole game, only **replaces the daily MGAP calendar promo**.
- Do **not** stack a Monday **MGAP** row and **Stash/RLAP** on the same date.

See also `constraints.md` §6.

---

## Segments & value (HARD until further notice)

Always **two configurations** and **two communication sets**:

| CZ deluxe | Message (cycle purchase) | Notes |
|-----------|--------------------------|--------|
| **0–159.99** | Receive **UP TO ×24 Coins** when purchasing the **entire cycle** | Default FL value |
| **160+** | Receive **UP TO ×36 Coins** when purchasing the **entire cycle** | Default FL value |

- Theming allowed (art/copy), **values stay segment-specific**.
- **Special events:** room to **increase** both segment caps together (document in Monday Description when used).

---

## Creative & Promo Manager

- **Art:** Promo Manager → **Purchase Tools** (Stash Booster / purchase-tools coins resource).  
  Back-office resource id (reference): `af440312-a739-453d-8fc3-1aa0e78c356a` (purchaseToolsCoins).
- **Per day, pull assets (×2 segments each):**
  - Banner  
  - In-App  
  - Pop-up Banner  
  - The offer itself  

**Duplicate task:** use the **example Monday task** on the MM calendar board as template when scheduling Stash days (do not invent config from scratch).

---

## QA / preview (HARD)

On promo preview, verify **both** trigger offers:

1. **Daily Deal** purchase button shows **Stash Booster** (not **Extreme MGAP** or generic MGAP label).
2. **Main offer** purchase button shows **Stash Booster** (same check).

**Other purchases:** any purchase still eligible for **MGAP** must **continue to trigger MGAP** — Stash only replaces/indicates on the **two configured offers**, not globally.

---

## Monday Description template (copy-ready)

```
Stash Booster — live (2 configs + 2 comms)
Triggers: Daily Deal + [main offer name: RYD / Decoy / Buy All / Mystery Buy All]
CZ 0–159.99: UP TO x24 Coins (full cycle purchase)
CZ 160+: UP TO x36 Coins (full cycle purchase)
Assets: Banner, In-App, Pop-up Banner, Offer (both segments) — Promo Manager Purchase Tools
QA: DD + main offer buttons show Stash Booster (not Extreme MGAP); other MGAP-eligible purchases unchanged
Drain: this day + following days include balance-draining promos
Do not combine: Rolling Offer same day. MGAP calendar promo: Stash replaces MGAP (no MGAP row same day).
```

---

## Related (different product)

**Stash Bundle / Surprise Box** — one-time surprise box (`offer_construction.md` §Stash Bundle). **Not** Stash Booster.

**DTC** — separate; not Stash Booster. Do not conflate with RLAP/Stash rows on old board entries.

---

## Links

| File | Role |
|------|------|
| `topics/04_second_offers/README.md` | Main-offer pairings (RYD, Decoy, Buy All) |
| `topics/03_rolling_offer/README.md` | Exclusion: no Rolling same day |
| `topics/05_mgap_gems_amplifiers/README.md` | Exclusion: no MGAP promo same day |
| `topics/06_core_coin_sink/README.md` | Balance drain context |
