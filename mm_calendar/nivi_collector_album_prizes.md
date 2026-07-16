# Collector's Album — phase structure & feature prizes (Nivi)

> **Source:** Nivi Manor, economy mail ahead of Collector's Album launch **14/07/2026**.  
> **Use for:** LiveOps prize config + **Monday `Description`** text on calendar rows.  
> **Monetization card bank** for purchase offers remains `monthly_guidelines/YYYY-MM.md` (shared separately in planning).

## Album timeline (promo-time boundaries)

| Phase | Shiny Series | Weeks | Window |
|-------|--------------|-------|--------|
| **1** | Shiny Series 1 | 1–3 | **14/07/2026** after promo → **04/08/2026** before promo |
| **2** | Shiny Series 2 | 4–6 | **04/08/2026** after promo → **25/08/2026** before promo |
| **3** | Shiny Series 3 | 7–10 | **25/08/2026** after promo → **22/09/2026** before promo |

**August 2026 mapping (calendar days):**

| Days | Phase | Shiny Series |
|------|-------|--------------|
| 1–3 Aug | 1 | MS1 |
| 4–24 Aug | 2 | MS2 |
| 25–31 Aug | 3 | MS3 |

Album active **14/07/26 – 22/09/26** (`album_cards.md`).

---

## Short-term features (Blast, Battlesheep, S&L)

~**5 days** average per season for **Blast / Battlesheep**. **Snakes & Ladders (SNL): 3–4 days** (Jul 2026). Board completion cycle prizes by album **phase**:

| Cycle | Phase 1 | Phase 2 | Phase 3 |
|-------|---------|---------|---------|
| 1 | Wild Ordinary | Wild Gold | Wild Any |
| 2 | 5★ Regular Pack | 5★ Regular Pack | 5★ Regular Pack |
| 3 | 4★ Regular Pack | 4★ Regular Pack | 4★ Regular Pack |

---

## Mid-term — Winovate (scene milestones)

| Scene | Phase 1 | Phase 2 | Phase 3 |
|-------|---------|---------|---------|
| 1st | 1★ regular | 2★ regular | 2★ regular |
| 4th | 3★ regular | 4★ regular | 4★ regular |
| 5th | 4★ regular | 5★ regular | 5★ regular |

Special promotions per album progression (calendar TBD with economy).

---

## Mid-term — Mega Pods

| Milestone | Freemium | Premium |
|-----------|----------|---------|
| 4 | 1★ regular | One of 3/4/5 regular **or** 3/4/5 gold |
| 8 | 3★ regular | — |
| 14 | — | One of 3/4/5 ace **or** 3/4/5 gold |
| 19 | — | Wild Any |

---

## Mid-term — Quest (islands)

| Island | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| 1st | 3★ Ace | 3★ Ace | 3★ Ace |
| 2nd | 4★ Ace | 4★ Ace | 4★ Ace |
| 3rd | 5★ Ace | 5★ Ace | Wild Ace |

---

## Collectibles

| Feature | Reward |
|---------|--------|
| **Ace Machine** | 1–5 Regular Packs, 3–5 Gold Cards |
| **Wheel of Stars** | 1st wheel: 1–5 regular small packs (×3) · 2nd: same + Ace packs · 3rd: same + Ace + Gold + **Wild Any** |
| **Shiny Wolf** | **3–5 Shiny Cards** |
| **Shiny Show** | Main shiny source; **up to 3 special promos/week** |

---

## Spinner Clash (rank prizes — Core)

| Rank | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| **1st** | 4★ Ace Card | 5★ Ace Pack | Wild Ace |
| **2nd** | 3★ Ace Card | 4★ Ace Pack | 5★ Ace Pack |
| **3rd** | 3★ Regular Card | 3★ Ace Card | 3★ Ace Pack |

**Cadence on MM calendar:** ≤1× per **two** ISO weeks (`build_august_2026_plan.py`).

---

## Dash

| Milestone | Freemium | Premium |
|-----------|----------|---------|
| 4 | — | 4★ Regular |
| 7 | 1★ Ace | — |
| 9 | — | Shiny Card |
| 10 | 2★ Ace | — |
| 11 | — | 3★ Gold |
| 12 | 2★ Ace | — |
| 14 | — | 5★ Regular |
| 17 | — | 5★ Gold |
| 19 | 3★ regular | Dash wheel: Wild Gold or Rare Pack (Hammers, Clan points, cards) |
| 20 | 5★ Ace | Wild Any |
| Swap Shop 900 DP | — | 4★ Ace |

---

## Clan Go

| Milestone | Freemium P1 | Freemium P2 | Freemium P3 | Premium |
|-----------|-------------|-------------|-------------|---------|
| 1 | 2★ Reg | 3★ Reg | 4★ Reg | — |
| 8 | — | — | — | Shiny Card |
| 11 | — | — | — | 3★ Gold |
| 17 | 3★ Ace | 4★ Ace | 5★ Ace | Wild Gold |

---

## Clan Chests

| Chest | Prize |
|-------|--------|
| 1st | 3★ Regular |
| 2nd | 3★ Ace |
| 3rd | 4★ Ace Pack |
| 4th | 4★ Ace Pack / 4★ Card |
| 5th | 4★ Ace Pack |
| 6th | 5★ Regular |
| 7th | 5★ Ace |
| 8th | 5★ Regular |

---

## Smash Market & Level Up

No change (per Nivi).

---

## MM calendar implementation

| Surface | Where prizes appear |
|---------|---------------------|
| **Spinner Clash** rows | `Description` — full 1st/2nd/3rd ladder for active phase |
| **Short Term** season open (day 1 / rotation) | Season `desc` on plan JSON + Monday context |
| **Album** phase row | Phase label + pointer to this doc |
| **Shiny Show** | Description notes main shiny source + ≤3/week |
| **Clan-Dash / Dash** | Economist configures in feature; cite this doc in tasks |
| **Time Limited Prize** (Monday) | **Prize in row title** (`Time Limited Prize — …`) and in Description — Nivi **Dash** premium milestones (rotate per Monday; `time_limited_prize_row_name()` / `time_limited_prize_nivi_label()` in builder). **No separate Dash Pass — Dash Day row** on the MM calendar. |

**Last updated:** July 2026
