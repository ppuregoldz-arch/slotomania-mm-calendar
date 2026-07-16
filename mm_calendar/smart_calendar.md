# Smart Calendar — `dwh.sm_fact_smart_calendar_promotion_updates` (Source of Truth)

> The **authoritative record** of what promos were scheduled/live. Query live via MCP `user-mcp-alchemy-sm`. This is a **timeline of edits, not one clean sheet** — multiple versions per `promo_id`.

## Key columns
`promo_id` (identity) · `promo_name` · `promo_desc` · `start_date`/`end_date` (timestamp) · `status` · `is_main` · `category_id` · `feature_id` · `population_id` · `promo_kpi` · `update_ts`/`insert_ts`/`insert_id` (versioning) · `event_date` · `color_code` · `created_by`/`updated_by`.

## How to read correctly
1. **Latest version per promo** first: `ROW_NUMBER() OVER (PARTITION BY promo_id ORDER BY update_ts DESC, insert_id DESC) = 1`.
2. **Two day-views**:
   - **Starts today**: `start_date::date = day` → what shows in that day's calendar column.
   - **Live at snapshot**: `start_date <= snapshot AND snapshot < end_date` → what's actually live operationally. **`end` is exclusive**.
3. **Snapshot = 14:00 Israel local** → **11:00 UTC (summer/DST)** · **12:00 UTC (winter)**.
4. **Framing order when reading a day**: (a) Short-Term seasonal (Blast/BattleSheep/SNL/Holy Moley) — which is active? → (b) Mid-Term always-on (**Mega Pods + Winovate** both live?) → (c) Mid-Term rotating (**Quest/Globez/Figz** — which one?) → (d) Daily offers (Buy All/DD/RYD/MGAP…) → (e) Mission layer (Dash/Clan) separately.
5. **Month-boundary rule (critical)**: never read only current-month rows — include **carryover history from prior days** (e.g., Mega Pods started 6/29 but live on 7/1), or season handovers look wrong.

## What to ignore
- Anything marked **cancelled/canceled** — ⚠️ appears in **`promo_name`** (e.g., "… - CANCELLED"), not only `status`. Filter **both**.
- **"Operation - Daily View"** wrappers (ops notes, not offers).
- Internal/config-only noise.
- **Parallel test/control duplicates** that are variants of one live family.
- **Known one-to-many**: two Monday **MGAP BOGO** variants map to one Smart row concept ("MGAP - BOGO" ≈ "MGAP BOGO"); same for "DD - 6 Hammers BOGO" ≈ "DD BOGO - 6 Hammers".

## Naming equivalences
- **M.E.S Tokens Offer ≈ M.E.S Steps Offer**
- **Counter PO ≈ Limited PO** (esp. backup context)
- **Boosted Gemback** variants (punctuation/spacing) = same concept.

## Canonical query — "live at snapshot" for a given day
```sql
SELECT promo_name, is_main, start_date, end_date, category_id
FROM (
  SELECT promo_name, is_main, start_date, end_date, category_id, status,
         ROW_NUMBER() OVER (PARTITION BY promo_id ORDER BY update_ts DESC, insert_id DESC) rn
  FROM dwh.sm_fact_smart_calendar_promotion_updates
  WHERE end_date >= DATE '{day}' - 10   -- carryover window (month-boundary rule)
    AND start_date <= DATE '{day}' + 3
) t
WHERE rn = 1
  AND start_date <= TIMESTAMP '{day} 11:00:00'   -- summer 11:00 UTC · winter 12:00
  AND end_date   >  TIMESTAMP '{day} 11:00:00'   -- end exclusive
  AND status     NOT ILIKE '%cancel%'
  AND promo_name NOT ILIKE '%cancel%'            -- cancelled often in the NAME
  AND promo_name NOT ILIKE '%Operation - Daily View%'
ORDER BY is_main DESC, promo_name;
```
- **"Starts today"** view: replace the snapshot lines with `start_date::date = DATE '{day}'`.

## Daily summary sentence (output format)
> "At 14:00 IL (11:00/12:00 UTC), active seasonal is **X**, rotating mid-term is **Y**, always-on are **Mega Pods + Winovate**, and key offers are **…**."

## Verified example — 2026-07-01 (live @ 11:00 UTC)
- **Seasonal**: BLAST (Cozy — Blast Cozy Wild Any handover from 6/29).
- **Mid-Term rotating**: Globez. **Always-on**: Mega Pods (Winovate to verify per day).
- **Core**: M.E.S Two Weeks Album (+ M.E.S Tokens Offer, up to 2×/day).
- **Offers**: DD BOGO 6 Hammers (no gems, Max) · MGAP BOGO · Rolling Offer 6 cycles (M) · Piggy (5H / 5★ Reg) · Boosted Gemback 300% (01:00-06:00).
- **Missions**: Collect X Clan Points / Hammers · Complete Superdash / 4 Daily Dashes · Pick X in Blast · Win X Coins.
- **Events**: 4th of July Stickers (Wild Gold) + Special 4th of July dash season.
- ✅ matches the evening reports (6/29 launched Cozy Blast + 2-Weeks-Album MES; 7/1 night MGAP BOGO + Rolling more-for-less).

---
**Updated:** Jul 2026 · live via `user-mcp-alchemy-sm`. This replaces assumptions about what ran — read it directly.
