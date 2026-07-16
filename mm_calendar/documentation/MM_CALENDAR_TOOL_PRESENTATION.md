# MM Calendar Tool — 5-Slide Deck (English)

Copy each slide into Google Slides / PowerPoint. **Minimal text by design.**

---

## Slide 1 — What we built

**MM Calendar Intelligence Stack**

One pipeline for Slotomania monetization planning:

**Plan → Monday → Smart Calendar**

- **Knowledge + rules** in the repo  
- **Python builder** encodes scheduling logic  
- **Monday board** = team handoff  
- **Smart Calendar (DWH)** = what LiveOps actually configured  

---

## Slide 2 — Why it matters

| Gap | Fix |
|-----|-----|
| Rules scattered | Single KB + monthly caps & card bank |
| Easy to break limits | Builder + audit (must pass before ship) |
| Monday ≠ LiveOps | Automated **Monday ↔ SC** check per day |

**August scheduling:** live **Monday board** is source of truth for *what’s on the calendar*; builder JSON supports validation & dashboard.

---

## Slide 3 — Planning layer

**In:** `monthly_guidelines` · topic docs · product constraints  

**Out:** `august_2026_plan.json` + human calendar + HTML dashboard  

**Builder assigns each day:** DD → second offer (VFM) → amplifiers → sinks → ADS  

**Gate:**

`build_august_2026_plan.py` · `audit_august_2026_plan.py` · season SKU check  

---

## Slide 4 — Monday layer

**Board:** MM calendar (promo rows by date)

Each row: **Product · Pricing · Description · Economist · Add to SC**

- **Description** = prizes, SKUs, hooks (not timing noise)  
- **Snapshot** (read-only): `pull_monday_live_snapshot.py`  
- **Upload to Monday** = explicit approval only (can overwrite board)

---

## Slide 5 — Smart Calendar & loop

**Source:** `dwh.sm_fact_smart_calendar_promotion_updates`  
(latest version per promo · promo-time ~ **11:00 UTC** summer)

**Verify one day:**

`verify_monday_smart_calendar_day.py YYYY-MM-DD`

- Monday promo → matching SC name  
- Description text → SC comment  

**Loop:** plan/validate → Monday finalize → LiveOps config → verify → fix gaps  

**Agents (Cursor):** router + rules + optional DWH — handoff in `TEAM_WORKLOG.md`

---

### Optional visual (paste on Slide 2 or 3)

```
monthly guidelines + KB
        ↓
   build + audit  →  plan.json / dashboard
        ↓
   Monday rows (Description, Add to SC)
        ↓
   Smart Calendar (DWH)
        ↓
   verify script (per day)
```
