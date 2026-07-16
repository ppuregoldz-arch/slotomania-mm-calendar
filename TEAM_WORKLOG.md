# Team worklog (Cursor agents)

Append a new section at the **top** after each working session.  
Canonical repo: `/Volumes/studios/Slotomania/CRM2/MM Calendar/Cursor Work`

---

---

---

---

### 2026-07-16 — Agent — SNL Short Term 3–4 days (guidelines + builder)

- **Goal:** Itay — SNL season length **3–4 days** (not ~5).
- **Done:** `lanes.md`, `constraints.md`, `rules_cheatsheet.md`, `monthly_guidelines/2026-08.md`, `nivi_collector_album_prizes.md`, `topics/07`, decision tree, `mm_calendar_builder.mdc`. Builder blocks: SNL **11–13** + **24–27**; descriptions `~3-4d` vs `~5d`.
- **Commands run:** `build_august_2026_plan.py` ✓, git push
- **Notes:** Aug **1–15 Monday** may still differ until season rows synced; plan JSON reflects new ST timeline for full month.

### 2026-07-16 — Agent — Git sync mandatory for `.cursor/rules/`

- **Goal:** Every rules change must land on GitHub for the team.
- **Done:** Added `.cursor/rules/git_sync_rules.mdc` (alwaysApply); note in `AGENTS.md`.
- **Commands run:** git commit + `github_push_origin.py` (this session)

### 2026-07-16 — Agent — Sync Desktop → CRM studio share

- **Goal:** Push recent Popup / Rolling MGAP / RYD backup work to team canonical folder.
- **Done:** `rsync` Desktop → `/Volumes/studios/Slotomania/CRM2/MM Calendar/Cursor Work/`; `build_august_2026_plan.py` ✓ on studio; audit fix for **26/8** Popup shell = VFM (RYD backup excluded).
- **Commands run:** rsync ✓, build ✓, audit (after fix — re-run)
- **Notes:** Audit may still flag **2/8, 14/8** DD vs second-offer same pricing (pre-existing). Live Monday authority for 1–15 unchanged.

### 2026-07-16 — Agent — Popup 26/8: RYD as BACKUP cap only

- **Goal:** Full Popup LAUNCH **26/8** is primary VFM; **RYD** is contingency in title if Popup slips.
- **Done:** Monday: renamed RYD `12511213888` with **BACKUP cap (if Popup Store LAUNCH slips)** + Description; Popup shell `12470313579` notes RYD backup. Builder: `backup=True` + suffix on 26/8 RYD; regen plan JSON/md ✓.
- **Commands run:** `build_august_2026_plan.py` ✓, Monday API ✓

### 2026-07-16 — Agent — Popup cadence locked 12/19/26 (keep phase 1 on 12)

- **Goal:** Keep Popup Store soft launch **(1/3) on 12/8**; align all copy to **12 / 19 / 26** (not 11/19/26).
- **Done:** Monday: reaffirmed shell `12470189724` on **12/8** (Description **12/19/26**, no paired Decoy note); refreshed **19/8** (`12470328927`) and **26/8** (`12470313579`) Popup descriptions to same cadence. Board scan: **0** remaining `11/19/26` strings. Builder/plan JSON already **12/19/26**.
- **Commands run:** Monday API ✓
- **Notes for next agent:** `august_2026_monday_days_1-15.json` still stale (shows Popup on 11) — re-pull from Monday if using that file. SC: stale Decoy DRAFT on 12 may persist until Ops sync.

### 2026-07-16 — Agent — Rolling MGAP 11/8; remove Decoy 12/8

- **Goal:** Rolling MGAP 4 cycles on **11/8**; **no** Decoy Bonanza with Popup on **12/8**; verify Smart Calendar.
- **Done:** Monday: deleted Decoy `12464285114` (12/8); created Rolling MGAP `12547639977` (11/8, Add + full Description). Left 12/8 Popup + Rolling 6 cycles unchanged.
- **Commands run:** Monday API ✓, `verify_monday_smart_calendar_day.py` 11/12 ✗ SC lag
- **Notes for next agent:** DWH still shows **Decoy 12/8** DRAFT (Jul 15) — cancel/remove in SC after sync; **11/8 Rolling MGAP** not in SC yet. Re-run verifier after Make/Ops ingest.

### 2026-07-15 — Agent — Verify DD Size Large in Smart Calendar

- **Goal:** Confirm **Size Large** on flagship DDs (9/14/26/27/8) appears in Smart Calendar, not only Monday titles.
- **Done:** DWH check — **0** Aug rows with `Size Large` in `promo_name`; **9/8** + **14/8** SC DRAFTs still pre-rename titles (Jul 12–14). **26/8** + **27/8** DD not in SC yet. Monday: added Description note + re-**Add** on all 6 DD rows; fixed missing **date** on `12486541138` (9/8 main DD).
- **Commands run:** `verify_monday_smart_calendar_day.py` (9/14/26/27), DWH MCP ✓, Monday API ✓
- **Notes for next agent:** No repo script writes SC — after Make/Ops sync, re-query DWH and expect `| Size Large |` in `promo_name` + `promo_desc` from Monday Description. **14/8** fuzzy verifier passes even without Size Large in SC (gap).

### 2026-07-15 — Agent — DD Size Large (9/14/26/27 Aug)

- **Goal:** Mark flagship Daily Deals on 9, 14, 26, 27/8 as **Size Large** in Monday row titles.
- **Done:** Renamed **6** DD rows (`| Size Large |` before pricing tier where applicable).
- **Commands run:** Monday API ✓

### 2026-07-15 — Agent — Popup Store soft launch 11→12/8

- **Goal:** Popup Store soft launch (1/3) must not run on Sunday; reschedule first TEST day.
- **Done:** Monday: moved shell `12470189724` + paired Decoy `12464285114` to **2026-08-12** (Wed); Config due **10/8**; cleaned Popup plan note from SNL 11/8; patched Puzzle/Popup descriptions to **12/19/26**. Builder: `POPUP_STORE_DAYS` **12/19/26**; `constraints.md`, audit, promo guidelines aligned.
- **Files:** `scripts/build_august_2026_plan.py`, `mm_calendar/constraints.md`, `scripts/audit_august_2026_plan.py`, `scripts/promo_guidelines_doc_data.py`, `august_2026_plan.json`, `2026-08_calendar.md`
- **Commands run:** Monday API ✓, `build_august_2026_plan.py` ✓
- **Notes for next agent:** Live board is authority for Aug 1–15; **12/8** now stacks Popup TEST + Gemback + on-purchase DD — watch amplifier validation if Gemback moves again.


- **Goal:** Review Jul tasks from 16/7; set **Config due date** = promo date − 2 days for **Config needed** / **MCP needed** rows only.
- **Done:** Updated **47** Monday items (`timerange_mm0vc5fk`); no other column changes.
- **Commands run:** Monday API ✓

---

### 2026-07-14 — Agent — Betty Loot 8/8 reference + Nivi/Tom

- **Goal:** Add Betty Kiss Loot creative ref on Monday; tag Nivi + Tom with Pick→Parasheep, PAB→Airstrike.
- **Done:** Updated item `12486541143` (Description, economists Nivi + Tom); update `5373088199` with @mentions + attached PNG.
- **Commands run:** Monday API ✓

---

### 2026-07-14 — Agent — Stash Booster (RLAP) on 2026-08-06 only

- **Goal:** Add **RLAP / Stash Booster** to **6/8**; no other board changes.
- **Done:** Created Monday `12528935397` — **2026-08-06 | RLAP** (Product MGAP, Description per `stash_booster.md`; triggers DD + Prize Mania). Snapshot refreshed.
- **Commands run:** Monday API ✓, `pull_monday_live_snapshot.py` ✓

---

### 2026-07-14 — Agent — Stash Booster (RLAP) post-FL guidelines

- **Goal:** Document Stash Booster usage after FL (ops mail); clarify **RLAP** Monday rows vs DTC.
- **Done:** New `mm_calendar/stash_booster.md`; updates to `lanes.md`, `constraints.md`, `rules_cheatsheet.md`, `BUILD_CALENDAR_ROUTER.md`, `topics/04_second_offers/README.md`, `README.md`.
- **Commands run:** n/a (docs only)

---

### 2026-07-14 — Agent — Remove Price Cut 11/8 + SC verify weeks 1–2

- **Goal:** Delete **Price Cut** on **2026-08-11** from Monday; validate Smart Calendar vs Monday for **Aug 1–14**.
- **Done:** Deleted Monday item `12468196268`. Snapshot refreshed. SC verify: **9/14 days fully OK**; gaps on 1/7 (Vertica flake), 8–12 (missing rows / Add / comment). **SC still has Price Cut on 11/8 (DRAFT)** — needs Ops cancel; **X2 Extreme Stamp** missing in SC on 11/8.
- **Commands run:** Monday delete ✓, `verify_monday_smart_calendar_day.py` (batch 1–14) partial, `pull_monday_live_snapshot.py` ✓

---

### 2026-07-14 — Agent — Extreme + Rolling logic docs + Aug 18 Monday desc

- **Goal:** Document BXGY/BMFL Extreme Stamp per-cycle rules; fix **2026-08-18** Rolling BMFL Description on Monday only.
- **Done:** `rolling_offer.md` § Extreme Stamp day + Rolling; cross-ref in `offer_construction.md`. Monday `12488281137` Description updated (cycle 1 RDS; cycles 2–3 → 2 Extreme Stamps). Snapshot refreshed.
- **Commands run:** Monday API ✓, `pull_monday_live_snapshot.py` ✓

---

### 2026-07-14 — Agent — X2 Extreme Stamp 4/8 → 11/8 + LBP swap (Monday only)

- **Goal:** Move **X2 Extreme Stamp** to **11/8**; swap **LBP** promos between **4/8** and **11/8** only; no other board changes.
- **Done:** `12464188623` → **2026-08-11 | X2 Extreme Stamp**; `12464175520` → **2026-08-11 | LBP - 2 Extreme Stamps (Night Plan)**; `12464343003` → **2026-08-04 | LBP - all goldens + 20% bigger (Night Plan peak)** (date + timeline aligned). Snapshot refreshed. RYD copy on 4/8 **not** edited (per scope).
- **Commands run:** Monday API ✓, `pull_monday_live_snapshot.py` ✓

---

### 2026-07-13 — Agent — Album kits + Last Card Protocol (Mon 14/7)

- **Goal:** Add three album-related rows on **2026-07-14**; tag **Nivi** (all) and **Avner Batat** (Near Miss + banner list).
- **Done:** Created on board `18388590642`: Last Card Protocol (Album, Config needed), BD starter kit (Black Diamond, MCP), Near Miss users starter kit (Album, MCP; economists Nivi + Avner). Descriptions + Monday updates with @mentions. Snapshot refreshed.
- **Commands run:** Monday API ✓, `pull_monday_live_snapshot.py` ✓

---

### 2026-07-12 — Agent — GGS/Gem Sale schedule fix (Mon 7–13)

- **Goal:** Remove Gems Sale 13/8; remove x2 GGS 11/8; move x2 GGS 7/8 → 8/8 on Monday (+ SC if present).
- **Done:** Monday updated — moved `12464329723` to **2026-08-08 | x2 GGS 18:00-20:00** (Add kept); deleted **11/8 x2 GGS** `12464312376`, **13/8 Gems Sale** `12464348270`. Snapshot refreshed. SC DWH: no matching starts-today rows for these promos (nothing to edit in SC from here).
- **Commands run:** Monday API ✓, `pull_monday_live_snapshot.py` ✓

---

### 2026-07-12 — Agent — Add to Smart Calendar Aug 2–15 (Monday)

- **Goal:** Set **Add to smart calendar** on all MM board promos **2026-08-02 … 2026-08-15**; self-validate Add column + SC/DWH where possible.
- **Done:** **141** rows set to Add (Aug 1–15 total **154/154** promos excl. Day anchors all Add). Batch verifier: Monday Add OK all days; SC **starts-today** still mostly empty (pre-existing drafts only on 1/2/6) — comment check blocked until ingest.
- **Commands run:** Monday API ✓, `verify_monday_smart_calendar_day.py` (batch Aug 1–15) ✗ SC gaps expected
- **Notes for next agent:** Re-run verifier after Ops/SC ingest; flag any Monday rows with empty Description before comment QA.

---

### 2026-07-12 — Agent — Aug 1 Add to Smart Calendar (Monday)

- **Goal:** Set **Add to smart calendar** on all 2026-08-01 MM board promos; verify SC presence + Description → `promo_desc`.
- **Done:** **13/13** promos (excl. Day anchor) now **Add** on Monday (`color_mkyfye85`); added `scripts/verify_monday_smart_calendar_day.py`. DWH **starts-today** for 2026-08-01 still has **1** row only (`Shiny Collection last 3 days`, empty comment) — **0** new SC rows since the Add batch; comment check blocked until automation creates promos.
- **Commands run:** Monday API ✓, `verify_monday_smart_calendar_day.py 2026-08-01` ✗ (SC gaps), Monday sync n/a
- **Notes for next agent:** Re-run verifier after Smart Calendar ingest; then continue Aug 2–15 Add batch if Itay approves Aug 1.

---

### 2026-07-12 — Agent — Refresh prediction model through Jul 11

- **Goal:** Fill only missing DWH tails, recalibrate all forecast/economy coefficients, and rebuild the dashboard.
- **Done:** Revenue/PU and promo keys advanced to 11/7; sink mechanics advanced to 11/7; PU coin/gem balance gap (4–11/7) filled from DWH after the bulk query connection timed out; `real_months.json` merged; model recalibrated (90 revenue days, 60 PU days, 101 economy days; revenue CV 7.19%, PU CV 5.25%); dashboard + OneDrive rebuilt. Monday authority 1–15/8 preserved (Betty 48h, Spin Zone 9/8, Dice Loot 13/8).
- **Files:** `mm_calendar/data/{wide_revenue_pu.json,wide_promo_keys.json,sink_mechanic_keys.json,pu_balance_raw.json,real_months.json,model_calibration.json,mm_dashboard.html}`, `mm_calendar/public/index.html`
- **Commands run:** `refresh_dwh_snapshots.py` ✓ (PU-balance bulk tail completed via targeted DWH queries), `pull_real_months.py --refresh` ✓, `calibrate_model.py` ✓, `build_calendar_html.py` ✓, `validate_calendar.py` ✓ (reported existing MGAP schedule violations: W1 >2, W2/W4 <2; not changed in model-only task), Monday sync n/a
- **Notes for next agent:** Calibration now ends 2026-07-11. Do not change Aug 1–15 Monday rows to address the validator without Itay approval.

---

### 2026-07-12 — Agent — Betty Loot 48h + Dice/Spin Zone swap (Mon 1–15)

- **Goal:** Betty Loot 48h (8–9); move Dice Loot off Betty weekend; swap with Spin Zone 13↔9.
- **Done:** Betty `12486541143` 48h timeline; Dice Loot → 13/8; Spin Zone → 9/8 (2 Parasheep); @Tom Sharlo on Betty row; snapshot + dashboard.
- **Commands run:** Monday API ✓, `pull_monday_live_snapshot.py` ✓, `build_calendar_html.py` ✓

---

### 2026-07-12 — Agent — Fix Not approved ADS PO (4/7/12 Aug)

- **Goal:** Replace three economy-rejected ADS rows on Monday 1–15 without full sync.
- **Done:** 4/8 Gems (was duplicate 2 Picks after 3/8); 7/8 2 Dice (was Quest Booster); 12/8 2 Dice (was 3000 Hero Coins); cleared economy status for Ohad; Monday update on each row tagging @Ohad Shezer (earlier Tom mention was mistaken).
- **Commands run:** Monday API ✓, `pull_monday_live_snapshot.py` ✓, `build_calendar_html.py` ✓

---

### 2026-07-12 — Agent — Decoy d3: 1 GGS allowed

- **Goal:** Encode Itay rule — Decoy Bonanza last denom need not upgrade to 2 GGS.
- **Done:** `offer_construction.md`, `topics/04_second_offers/README.md`, `learnings.md`; `decoy_bonanza_item(..., ggs_d3=2)` optional in builder (default unchanged).
- **Commands run:** n/a

---

### 2026-07-12 — Agent — Monday SKU fixes (Itay list 1–17 gaps)

- **Goal:** Push remaining approved row renames/descriptions to Monday for Aug 1–15 (no full sync).
- **Done:** `scripts/apply_itay_aug_1-15_monday_fixes.py` — DD 2/8, 7/8, 12/8, 15/8; Spin Zone 6/8 topper + 13/8 Reg; RYD 14/8; PYP 2/8 Use PAB; refreshed snapshot + dashboard HTML.
- **Commands run:** `apply_itay_aug_1-15_monday_fixes.py` ✓, `pull_monday_live_snapshot.py` ✓, `build_calendar_html.py` ✓
- **Notes for next agent:** Duplicate TLP row on 3/8 (`12511356491` vs `12488279081`) not touched — confirm with Itay if one should be deleted.

---

### 2026-07-12 — Agent — Monday authority Aug 1–15 → dashboard + forecasts

- **Goal:** Treat Itay’s Monday rows (first two weeks) as read-only truth; refresh HTML/forecasts from live snapshot.
- **Done:** `scripts/monday_live_dashboard.py`; dashboard merges Mon 1–15 from `monday_board_live_by_date.json`; `august_2026_monday_days_1-15.json` + `.md`; `00_GUIDELINES_ITAY.md` + `BUILD_CALENDAR_ROUTER.md`; recalibrated + `build_calendar_html.py`.
- **Commands run:** `pull_monday_live_snapshot.py` ✓, `calibrate_model.py` ✓, `build_calendar_html.py` ✓
- **Notes for next agent:** Do not builder/sync/overwrite Aug 1–15 without Itay approval. Aug 16–31 still from `august_2026_plan.json`.

---

### 2026-07-12 — Agent — Monday TLP titles 3/8 + 10/8

- **Goal:** Prize in Time Limited Prize row title on Monday board.
- **Done:** Renamed items `12488279081` (3/8 → `4* Regular Card`), `12488284460` (10/8 → `Shiny Card`); refreshed Description.
- **Commands run:** Monday API rename ✓ (days 3 & 10 only, no full sync)

---

### 2026-07-12 — Agent — Time Limited Prize prize in title

- **Goal:** Clan-Dash Time Limited Prize must name the prize in the row title (Monday board).
- **Done:** `time_limited_prize_row_name()`; Monday rows e.g. `Time Limited Prize — Shiny Card`; `nivi_collector_album_prizes.md`.
- **Commands run:** `build_august_2026_plan.py` ✓

---

### 2026-07-12 — Agent — Aug 1–15 card-bank SKU pass (Itay sign-off)

- **Goal:** Encode approved numbered changes (1–17) in August builder for 1–15/8.
- **Done:** Curated DD keys (2 PAB+Quest, 7 AS+2 Parasheep, 12 Shield+4 Dice, 15 Quest+Shield+Multiwheel); PM 6 → 3★ Reg pack; BA 10 custom denoms; Spin Zone 13 → 4★ Reg; 6/8 Spin Zone 4★ Ace + Ace_3 topper; RYD 14 Reg+PAB+SB; PYP mission Use PAB; removed MGAP 10 BOGO (gap/cap vs 9); season SKU exception for 14 RYD.
- **Files:** `scripts/build_august_2026_plan.py`, `scripts/validate_season_skus.py`, `mm_calendar/data/august_2026_plan.json`, `mm_calendar/examples/2026-08_calendar.md`
- **Commands run:** `build_august_2026_plan.py` ✓
- **Notes for next agent:** Monday board not synced — push with upload after review. MGAP 10 BOGO dropped from schedule (was 9→10 spacing / w2>2).

---


- **Goal:** Remove Platform/Duration boilerplate from Description (1–15 Aug only).
- **Done:** `scripts/monday_description_compact.py`, `apply_monday_description_compact.py` (113 rows); builder stops appending Duration; upload uses compact; topics/09 + topics/05.
- **Commands run:** apply compact ✓, pull snapshot ✓

---

### 2026-07-12 — Agent — Schedule MGAP BOGO 5/8 + SB Guaranteed 9/8 (Monday)

- **Goal:** Date BOGO 5/8; 9/8 = Slotobucks Guaranteed (Extreme 300% / Epic 150%, once per player).
- **Done:** Monday `12464188536` (5/8 BOGO); `12467835488` renamed + dated 9/8 SB Guaranteed + Description. Guideline: Wild only 20/8; SB 9+30.
- **Commands run:** Monday API write ✓, `pull_monday_live_snapshot.py` ✓

---

### 2026-07-12 — Agent — MGAP Slotobucks Guaranteed in guidelines

- **Goal:** Document Extreme 300% / Epic 150% SB, once per player; advise week 3–9/8 MGAP gap.
- **Done:** `topics/05_mgap_gems_amplifiers/README.md`, `monthly_guidelines/2026-08.md` §MGAP.
- **Recommendation:** Week 3–9/8 → date **BOGO 5/8** + **Wild 9/8** (not SB Guaranteed); SB Guaranteed stays **30/8** plan.

---

### 2026-07-12 — Agent — Fix Decoy 8/8, 11/8, 13/8 ALL ABOVE (Monday only)

- **Goal:** Apply Decoy d3 rule; remove Ace on 13/8; no Decoy Hammers on 11/8 (DD Hammers Wheel).
- **Done:** `12486527603` (8/8 Battlesheep+Quest, 3★ Gold d3); `12464285114` (11/8 Dice+Hero Coins, 2 Picks not Hammers); `12470171455` (13/8 4★ Gold not Ace, ALL ABOVE).
- **Files:** live snapshot/by_date
- **Commands run:** Monday mutations ✓; pull ✓.

---

### 2026-07-12 — Agent — Fix Decoy 2/8 ALL ABOVE (Monday only)

- **Goal:** d3 includes d1+d2 prizes + 5★ Reg per `offer_construction.md` Decoy rule.
- **Done:** `12464175025` — d3: PAB + Quest Booster + 100% SB + **5★ Reg**; Full denoms line added.
- **Files:** `monday_board_live_snapshot.json`, `monday_board_live_by_date.json`
- **Commands run:** Monday mutation ✓; `pull_monday_live_snapshot.py` ✓.

---

### 2026-07-12 — Agent — Decoy d3 = ALL ABOVE rule in guidelines

- **Goal:** Document HARD Decoy Bonanza d3 logic (d1+d2 prizes + bundle stamps + d3 hook).
- **Done:** `offer_construction.md`, `topics/04_second_offers/README.md`, `assets/dashboard_app.js` decoy copy.
- **Files:** above + `TEAM_WORKLOG.md`
- **Commands run:** n/a
- **Notes:** Fix live rows (e.g. 11/8 `12464285114`) separately if user asks.

---

### 2026-07-12 — Agent — Sync Desktop → studio shared folder

- **Goal:** Push local Cursor Work updates to team path on studios volume.
- **Done:** `rsync` Desktop → `/Volumes/studios/Slotomania/CRM2/MM Calendar/Cursor Work` (~11.7 MB); verified `TEAM_WORKLOG.md`, Monday live snapshots, `pull_monday_live_snapshot.py` match.
- **Files:** full tree (excluded `.cursor/monday.env`, `.git`, `__pycache__`).
- **Commands run:** rsync ✓; builder/Monday n/a.
- **Notes:** OneDrive copy not present on this machine. Monday board remains live SOT for schedule.

---

### 2026-07-12 — Agent — SNL 3d + Blast shift (Monday only)

- **Goal:** Shorten Aug SNL season to 3 days (11–13); start Blast immediately after; align prizes on 14–15.
- **Done:** `12464266351` SNL timeline **11–13** + ~3d prize block; `12464447924` renamed **2026-08-14 | Blast**, timeline **14–18** (5d). Fixed 14–15 rows still labeled SNL: ADS PO (14/15), x2 GGS (14), Quest Season rhythm (15), PYP + King for a Day dice → Blast dice.
- **Files:** `monday_board_live_snapshot.json`, `monday_board_live_by_date.json`
- **Commands run:** Monday mutations ✓; `pull_monday_live_snapshot.py` ✓; builder/sync n/a.
- **Notes:** **19–20 Aug** have no Short Term season row (was SNL 14–15 + Blast 16–20). Extend Blast to 20 or add next ST if needed.

---

### 2026-07-12 — Itay — 5/8 Decoy → Rolling Supersized (Monday only)

- **Goal:** Replace 5/8 Decoy with Rolling Supersized only; keep 4★ Gold via Cycle 4 hook.
- **Done:** Unscheduled Decoy `12467805477` (cleared Date); created `12510879320` — Supersized 5 cycles | M Pricing; 4★ Gold in cycle 4 (not 3 Picks).
- **Files:** `monday_board_live_snapshot.json`, `monday_board_live_by_date.json`
- **Commands run:** Monday mutations ✓; `pull_monday_live_snapshot.py` ✓.
- **Notes:** DD/Piggy/Spinner/Winovate untouched. Decoy row remains on board without date.

---

### 2026-07-12 — Itay — Add Dice Loot 9/8/2026 (Monday only)

- **Goal:** Add Core Dice Loot on 2026-08-09 only; no other board/plan changes.
- **Done:** Created Monday item `12510778773` — `2026-08-09 | Dice Loot` (Core, Config needed, Reuse creative); refreshed live snapshot.
- **Files:** `mm_calendar/data/monday_board_live_snapshot.json`, `monday_board_live_by_date.json`
- **Commands run:** Monday create_item + column mutation ✓; `pull_monday_live_snapshot.py` ✓; builder/sync n/a.
- **Notes for next agent:** 9/8 now has Dice Loot dated; undated Custom Pod / MGAP Wild rows unchanged.

---

### 2026-07-12 — Agent — Full Monday board learn (read-only SOT snapshot)

- **Goal:** Learn entire MM calendar Monday board; treat as updated local truth; zero writes to Monday.
- **Done:** Pulled all 2,957 items (3,338 dated in Aug 2026 subset count in meta); wrote live snapshot + by-date index + `pull_monday_live_snapshot.py` + `MONDAY_BOARD_AUTHORITY.md`; updated `topics/09_monday_board/README.md`.
- **Files:** `mm_calendar/data/monday_board_live_snapshot.json`, `monday_board_live_by_date.json`, `MONDAY_BOARD_AUTHORITY.md`, `scripts/pull_monday_live_snapshot.py`
- **Commands run:** read-only GraphQL pagination ✓; Monday sync n/a.
- **Notes for next agent:** For “what’s scheduled”, use live snapshot meta `pulled_at_utc` 2026-07-12T07:50:36Z; undated rows = not on a calendar day; prefer snapshot over `august_2026_plan.json`.

---

### 2026-07-12 — Agent — Monday read-only pull 1–15/8/2026

- **Goal:** Read-only snapshot of MM calendar board rows dated 2026-08-01 … 2026-08-15 (no writes/sync).
- **Done:** GraphQL pagination on board `18388590642` (2,957 items scanned); 173 rows in date range; saved JSON snapshot.
- **Files:** `mm_calendar/data/_readonly_pull_2026-08-01_15.json`
- **Commands run:** `monday_client.gql` via inline Python ✓; `build_august_2026_plan.py` n/a; Monday sync n/a.
- **Notes for next agent:** Live board differs from local August builder on several days (e.g. 8/8 Decoy vs Rolling, 9/8 no MGAP Wild row, duplicate DD rows on 8–10). Use snapshot for “what’s on Monday now.”

---

### 2026-07-10 — Agent — Promo knowledge, measurement, performance and prediction reorg

- **Goal:** Implement the evidence-disciplined MM Calendar reorganization across sources, identity, measurement, instances, variant performance, prediction/backtesting, and routing.
- **Done:** Added scoped source inventory/hierarchy; Itay authority file; promo identity; immutable-raw and migration policy; data model/vocab/KPI inheritance; methodology/causal ladder; monthly SOP; missing/conflict registers; selective Vertica validation; 1,175-record JSONL instance index; 70 canonical variant docs; coverage report; rolling-origin revenue/PU backtest; post-backtest prediction/recommendation framework; validators/builders; superrule and routing updates. Follow-up inventory findings registered: stale DWH refresh, Monday↔Smart mismatches, August MGAP audit conflict, and July-canvas validator dependency.
- **Files:** `mm_calendar/00_GUIDELINES_ITAY.md`, `mm_calendar/measurement/**`, `mm_calendar/performance/**`, `mm_calendar/prediction/**`, `scripts/{build_promo_knowledge_base,validate_promo_knowledge_base,backtest_promo_prediction}.py`, `.cursor/rules/mm_calendar_superrule.mdc`, AGENTS/router/topics/rule wiring.
- **Commands run:** `build_promo_knowledge_base.py` ✓, `backtest_promo_prediction.py` ✓, `validate_promo_knowledge_base.py` ✓, Python compile ✓, relevant Markdown link check ✓; `build_august_2026_plan.py` n/a, `audit_august_2026_plan.py` n/a, Monday sync n/a.
- **Validation:** 1,175/1,175 instances have date/family/variant/source; 1,866 numeric results carry provenance; 0 duplicate IDs; 0 vocabulary/schema errors; 0 broken internal Markdown links. Backtest: revenue MAPE 8.0% / direction 41.6%; PU MAPE 7.6% / direction 24.4%; wager/gem/segment insufficient evidence.
- **Notes for next agent:** Raw inputs were not moved or overwritten. Existing historical summaries remain in place as cited evidence. Prediction now uses broad empirical uncertainty and only limited family eligibility; do not restore additive all-promo point deltas without a better backtest. August plan/builder/example were not edited; CF-010 documents the existing MGAP audit issue only. No Monday changes.

---

### 2026-07-10 — Agent — Fix Core vs Shiny/Winovate framing

- **Goal:** Correct conceptual error — Core = **coin sink** (machine play); Shiny Show / Winovate = **gem sink** (gem usage). They were wrongly grouped in topic 06.
- **Done:** Split topics — `06_core_coin_sink/` (Core/MES/Clan) + new `11_gem_sink_shiny_winovate/` (Shiny Show/Winovate). Deleted `06_gameplay_core_shiny/README.md`. Updated `topics/README.md`, `BUILD_CALENDAR_ROUTER.md`, `05_mgap_gems_amplifiers` cross-ref.
- **Files:** `mm_calendar/topics/06_core_coin_sink/**`, `mm_calendar/topics/11_gem_sink_shiny_winovate/**`, router + topics README.
- **Commands run:** n/a
- **Notes:** Coin sink vs gem sink is the axis. No Monday sync.

---

### 2026-07-10 — Agent — Knowledge router + topics/

- **Goal:** Faster agent retrieval — domain folders with examples + single calendar-build router.
- **Done:** `BUILD_CALENDAR_ROUTER.md`; `topics/` (01–10 README per lane); wired README, ONBOARDING, PRIZE_PRIORITY, AGENTS.md, mm_calendar_builder.mdc.
- **Files:** `mm_calendar/BUILD_CALENDAR_ROUTER.md`, `mm_calendar/topics/**`
- **Commands run:** n/a
- **Notes:** Start tasks at BUILD_CALENDAR_ROUTER → topics/*. No Monday sync.

---

### 2026-07-10 — Agent — Rolling Offer canonical doc

- **Goal:** Document correct BXGY 5/6-cycle structure (Monday operational model); stop teaching builder Free1–4 stamp split.
- **Done:** Added `mm_calendar/rolling_offer.md` (6-denom skeleton, 5-cycle supersized, 6-cycle 2026-07-01, BMFL reminder, wrong-model warning). Linked from `offer_construction.md`, `learnings.md`, `README.md`, `PRIZE_PRIORITY_AND_MONTH_BUILD.md`, `lanes.md`, `mm_calendar_builder.mdc`, monday_refs README, `promo_guidelines_doc_data.py`.
- **Files:** `mm_calendar/rolling_offer.md` + cross-links above.
- **Commands run:** n/a
- **Notes for next agent:** Do **not** sync/change Monday board from this doc. `build_august_2026_plan.py` `rolling_bxgy_cycle_body` still legacy until refactor. Read `rolling_offer.md` before writing Rolling descriptions.

---


- **Goal:** Subject `.docx` easy for monetization owners to fill + machine-readable on return (refs, Hebrew UX, AI_FIELD tags).
- **Done:** `promo_guidelines_doc_render.py` manager blocks; `generate_promo_subject_docx.py` → `*_MANAGER.docx`; `parse_manager_promo_docx.py` for JSON ingest.
- **Files:** `mm_calendar/documentation/subjects/sm_mm_calendar_*_MANAGER.docx` + Desktop copy.
- **Commands run:** `python3 generate_promo_subject_docx.py` ✓
- **Notes:** Keep `AI_FIELD:` lines; return filled docx → `python3 parse_manager_promo_docx.py <file>` or attach to Cursor.

---

- **Goal:** Separate `.docx` per MM Calendar subject (Core, Album, Purchase Offers+DD, Purchase Features, Happy Hours, Mid/Short Term, Clan & Dash).
- **Done:** Added `scripts/generate_promo_subject_docx.py`; generated 8 files from `promo_guidelines_doc_data.py` (field template + 5 examples each).
- **Files:** `mm_calendar/documentation/subjects/sm_mm_calendar_*.docx` (+ copy `~/Desktop/mm_calendar_subject_docs/`).
- **Commands run:** `python3 scripts/generate_promo_subject_docx.py` ✓
- **Notes for next agent:** Re-run script after editing `promo_guidelines_doc_data.py`. Gems/Popup/BD-Event grouped per SUBJECTS map in script.

---

### 2026-07-09 — Agent — August Core economist audit (Monday)

- **Goal:** Gameplay Core rows should have Yahav Mizrahi (Spinner Clash → Tom Sharlo; Custom Pod → Ohad); economist column only.
- **Done:** Scanned Aug 2026 board; updated **37** rows from Nivi/empty → correct economist via `multiple_person_mky0jahx` only (no Config/Description/Promo Time changes). Re-verify: 0 mismatches on gameplay Core; 5/5 Spinner = Tom; 5/5 Custom Pod = Ohad.
- **Commands run:** targeted Monday API ✓

---

### 2026-07-09 — Agent — Monday Gemback 11→12 (targeted)

- **Goal:** Board still had Boosted Gemback on 11/8 after plan move to 12/8.
- **Done:** Deleted Monday item `12468201040` (11/8 Gemback); created `12486443701` on 12/8 from plan row (no full-day sync).
- **Commands run:** targeted Python (delete + apply_row) ✓

---

### 2026-07-09 — Agent — Aug 11/12 gem amplifier rebalance

- **Goal:** 11/8 too strong (x2 GGS + Gemback + Price Cut); move one lever to weak 12/8; encode for future months.
- **Done:** **Boosted Gemback 300%** moved **11→12** (`GEMBACK = {12, 25}`). 11/8 keeps x2 GGS + Price Cut + Popup test stack. Added `day_gem_revenue_amplifier_count` validation (fail if all three same day).
- **Files:** `build_august_2026_plan.py`, `august_2026_plan.json`, `2026-08_calendar.md`, `learnings.md`
- **Commands run:** `build_august_2026_plan.py` ✓
- **Notes for next agent:** Monday not synced — user rule: targeted row move on 11/8 (delete/move Gemback) + create on 12/8 only if they ask.

---

### 2026-07-09 — Agent — Aug 7 DD visible on Monday (Promo Time)

- **Goal:** Daily Deal missing on 7/8 in Monday calendar view.
- **Done:** Row existed (`12486217945`) but **Promo Time empty** — re-applied from plan; `2026-08-07 - 2026-08-07`. Same fix for **11/8** and **13/8** DD timerange; removed accidental duplicate on 13/8.
- **Commands run:** targeted `apply_row` for DD rows ✓

---

### 2026-07-09 — Agent — Aug 4 second DD (post Shiny Limited once)

- **Goal:** Separate repeatable DD after once-per-player Shiny Limited on 4/8.
- **Done:** `SHINY_LIMITED_SPLIT_DD_DAYS={4}` — keep **DD - Shiny Limited - Once** + **DD- 100% SB + Hammers (multiple)** as two rows (plan + Monday). Other shiny_ltd days still merge companion into description.
- **Files:** `build_august_2026_plan.py`, plan JSON, calendar md
- **Commands run:** `build_august_2026_plan.py` ✓, Monday targeted DD sync ✓ (1 updated, 1 created)

---

### 2026-07-09 — Agent — Aug 2 DD High pricing (MGAP Matched)

- **Goal:** Daily Deal on 2/8 = **High** pricing (MGAP Matched day).
- **Done:** Builder override `d==2` after MGAP tier split; plan JSON DD `High`; Monday row renamed/applied **High Pricing** (item `12486384765`). Validation allows DD+second both High on 2/8 only.
- **Files:** `scripts/build_august_2026_plan.py`, `august_2026_plan.json`, `examples/2026-08_calendar.md`
- **Commands run:** `build_august_2026_plan.py` ✓, targeted Monday `apply_row` DD ✓

---

### 2026-07-09 — Agent — Restore Aug 2 Daily Deal on Monday

- **Goal:** User reported DD removed on 2/8 after Core sync.
- **Done:** DD row still existed but **Promo Time** (`timerange_mkz3t5qy`) was empty — hidden in calendar views. Re-applied DD from plan; timerange now `2026-08-02 - 2026-08-02`. Upload script: set timeline in same column mutation as other fields.
- **Files:** `scripts/upload_mm_calendar_day_monday.py`
- **Commands run:** targeted `apply_row` for DD ✓
- **Notes:** If manual DD copy/pricing differed from plan, user must say what to restore.

---

### 2026-07-09 — Agent — Core challenge on Monday for 2/8

- **Goal:** Add Core challenge row for August 2 on MM calendar Monday board.
- **Done:** Targeted `upload_mm_calendar_day_monday.py 2` — created **PYP — finish for 4★ Reg card** (Core); updated 4 existing rows; removed 1 duplicate. Source already in `august_2026_plan.json` (no builder change).
- **Files:** (Monday board only; plan unchanged)
- **Commands run:** `upload_mm_calendar_day_monday.py 2` ✓
- **Notes for next agent:** Do not re-sync days 1–4 without user approval (see incident entry below).

---

### 2026-07-09 — Agent — Monday sync overreach (incident)

- **Goal:** User asked to fix Monday; agent ran broad sync.
- **What went wrong:** `upload_mm_calendar_day_monday.py --all` (then partial resume) **overwrote manual board edits** on days 1–4+ (plan-driven full row apply + orphan delete). User: do not remove their changes.
- **Done:** Documented HARD rule in `learnings.md`, `AGENTS.md`, upload script docstring; fixed `Extreme Stamp` → board label `Extreme stamp` for future targeted syncs only.
- **Monday sync run:** 1–3 partial, 4 complete; 5–31 interrupted — **do not re-run bulk sync** until user lists which dates are safe or which rows to patch.
- **Notes for next agent:** Manual Monday = source of truth for edited days. Code/plan JSON updates only unless user names exact day numbers to sync.

---

### 2026-07-09 — Agent — Nivi Collector's Album prizes in descriptions

- **Goal:** Encode Nivi phase timeline + feature prize tables; prizes in row `Description` (Spinner ranks, seasons, Shiny Show).
- **Done:** `nivi_collector_album_prizes.md`; `collector_album_phase()` + Spinner/Short/Album desc helpers; season `desc` on plan JSON; Monday `build_description` includes season opens; docs/README updates.
- **Files:** `build_august_2026_plan.py`, `upload_mm_calendar_day_monday.py`, `nivi_collector_album_prizes.md`, `monthly_guidelines/2026-08.md`, `album_cards.md`, plan JSON
- **Commands run:** `build_august_2026_plan.py` ✓, `audit_august_2026_plan.py` ✓
- **Notes for next agent:** Aug 1–3 = Phase 1; purchase card bank still `monthly_guidelines` table (unchanged).

---

### 2026-07-09 — Agent — Spinner Clash biweekly (not weekly)

- **Goal:** Spinner Clash **1× per two ISO weeks** (was 1×/week in builder); no duplicate promos; backfill removed days with other Core.
- **Done:** `compute_spinner_clash_days()` pairs ISO weeks; validation + `spinner_biweeks_used`; August plan now days **5, 12, 26** (3× month); `learnings.md`.
- **Files:** `scripts/build_august_2026_plan.py`, `august_2026_plan.json`, `examples/2026-08_calendar.md`, `learnings.md`
- **Commands run:** `build_august_2026_plan.py` ✓, `audit_august_2026_plan.py` ✓
- **Notes for next agent:** Days 1/20/31 lost Spinner → Win Master / MES; Puzzle M.E.S control on 20 still has Win Master.

---

### 2026-07-09 — Agent — Day 1 biggest store denom → Offers + description

- **Goal:** `1st of month — biggest store denom` Monday row = **Offers & coin sale** (not SlotoBucks) with coins+gems desc (4th July American denom ref); user fixed board manually.
- **Done:** `purchase_drivers.py`, `upload_mm_calendar_day_monday.py`, `monthly_guidelines/2026-08.md`, dashboard `MONTH_OPEN_DENOM_DRIVER`; rebuilt plan + HTML.
- **Files:** see above + `august_2026_plan.json`, `public/index.html`
- **Commands run:** `build_august_2026_plan.py` ✓, `build_calendar_html.py` ✓
- **Notes for next agent:** Day-1 driver still `Config needed` on upload; desc is driver text only (no extra boilerplate).

---

### 2026-07-09 — Agent — LBP window 00:00 → Promo Time (not 2h post 12:00)

- **Goal:** LBP (e.g. 30% Bigger Balls) should run **00:00 UTC → 11:00 UTC**, not default 2h post 12:00; user fixed Monday manually this time.
- **Done:** `promo_duration_note()` + `lbp_promo_description()` in builder; docs in `lotto_bonus.md`, `AGENTS.md`; rebuilt `august_2026_plan.json`.
- **Files:** `scripts/build_august_2026_plan.py`, `mm_calendar/data/august_2026_plan.json`, `mm_calendar/lotto_bonus.md`, `AGENTS.md`
- **Commands run:** `build_august_2026_plan.py` ✓
- **Notes for next agent:** Lotto peak row has no extra Duration line; LBP row carries the Promo Time window.

---

### 2026-07-09 — Agent — Lotto peak: no Monday Config Status

- **Goal:** Next Monday sync should not mark Lotto peak / LBP rows as “Config needed” (user fixed board manually this time).
- **Done:** `config_status_for()` returns `None` for `Lotto — peak` and `LBP — …`; noted in `lotto_bonus.md`, `AGENTS.md`.
- **Files:** `scripts/upload_mm_calendar_day_monday.py`, `mm_calendar/lotto_bonus.md`, `AGENTS.md`
- **Commands run:** n/a (no Monday `--all`)
- **Notes for next agent:** Do not re-upload Lotto config unless user asks; piggy/season rows still use Config needed where applicable.

---

### 2026-07-08 — Agent — Prize priority + MD library guide

- **Goal:** Document prize priority, month-building rules, and how to use all `mm_calendar` MD files.
- **Done:** Added `mm_calendar/PRIZE_PRIORITY_AND_MONTH_BUILD.md`; linked from `README.md`, `AGENTS.md`, `ONBOARDING_QUICK.md`.
- **Files:** `mm_calendar/PRIZE_PRIORITY_AND_MONTH_BUILD.md`, `mm_calendar/README.md`, `AGENTS.md`, `mm_calendar/ONBOARDING_QUICK.md`
- **Commands run:** n/a (documentation only)
- **Notes for next agent:** Treat this file as the hub after `README.md` for planners; authority order is monthly guideline → constraints/cheatsheet → learnings/performance MDs.

---

### 2026-07-08 — Itay (setup) — Shared studio workspace + agent docs

- **Goal:** Point the team at the studio folder and define how Cursor agents should work and hand off.
- **Done:** Added `AGENTS.md`, created `TEAM_WORKLOG.md`, synced August package to OneDrive `Cursor Work MM`.
- **Files:** `AGENTS.md`, `TEAM_WORKLOG.md`
- **Commands run:** n/a (documentation only)
- **Notes for next agent:** Read `AGENTS.md` first. August plan lives in `mm_calendar/data/august_2026_plan.json`; always run `build_august_2026_plan.py` + `audit_august_2026_plan.py` after builder changes.
