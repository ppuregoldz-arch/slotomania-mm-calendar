# Itay's MM Calendar Guidelines — Highest Standing Authority

**Last updated:** July 2026  
**Scope:** Slotomania monetization-calendar planning, promo construction, measurement, performance interpretation, and recommendations.

## Authority order

1. A new explicit instruction from Itay in the current conversation overrides every file.
2. This file contains Itay's standing rules.
3. `monthly_guidelines/YYYY-MM.md` supplies month-specific economy ceilings and card banks.
4. `constraints.md` and `rules_cheatsheet.md` supply operational HARD/SOFT constraints.
5. `learnings.md` and `daily_mm_reports.md` supply observed operating lessons.
6. Canonical performance documents and their cited analyses supply measured evidence.
7. `patterns_derived.md` supplies historical patterns when higher authorities are silent.

If two sources conflict, do not silently choose. Follow the higher authority and register the conflict in `measurement/UNRESOLVED_CONFLICTS.md`.

## Policy versus economy ceilings

- Itay's instructions determine planning policy.
- Month-specific economy ceilings and weekly card banks remain HARD unless Itay explicitly approves an exception to that exact ceiling or bank.
- Never invent a missing cap, reward allocation, card type, frequency, or numeric target.

## Standing construction and scheduling rules

- **MGAP:** exactly 2 placements per week. The older `<=3/week` wording is superseded.
- **Hammers:** one product source per day. A Rolling product may distribute Hammers across its own cycles, but no second product may also grant Hammers that day.
- **BMFL:** Buy More for Less is distinct from BXGY; 3 cycles, High pricing only, with approximately 10 days minimum cooldown.
- **Rolling BXGY 5/6 cycles:** follow `rolling_offer.md`; do not use the old builder helper's Free1/Free2 stamp model.
- **Daily VFM:** every day needs at least one real second offer beyond Daily Deal. Clan-Dash and Dash Pass do not count.
- **Pricing separation:** when Daily Deal and the second offer are both priced, they must use different pricing levels.
- **Monday:** use a light second offer except on approved MFL anchors; do not rely on a large revenue stack.
- **Board density:** no more than one Core gameplay item and one Shiny Show item per day; no Shiny Show on Monday; merge paired Daily Deal once/repeatable rows for board presentation.
- **Coin sink versus gem sink:** Core/MES/Spin Zone/PYP/Custom Pod drive machine play and coin wager. Shiny Show and Winovate drive gem usage. Do not group them under one sink KPI.
- **Cards:** card rewards must come from the current weekly bank. Gold is purchase-only; Core rewards are Reg/Ace/Shiny/Wild as allowed by the bank.
- **Monday safety:** never create, change, delete, or synchronize Monday rows without explicit approval.
- **August 2026 (days 1–15):** live Monday board rows are committed planning truth for UI/forecasts (`monday_board_live_by_date.json`, `august_2026_monday_days_1-15.json`). Do not overwrite via builder or sync without Itay’s explicit approval for that date range.
- **Monday title vs Description:** when they disagree, the **row title (Name)** is correct. Update **Description** (and **Pricing** when the title states High/Mid/Max) to match the title; do not “fix” the title from builder JSON or plan text unless Itay asks.

## Evidence and measurement rules

- Raw sources are immutable. Never delete or overwrite them.
- Never silently infer a missing business rule or numeric result.
- Every numeric KPI result must include its source, baseline method, calculation date, confidence, and validation status.
- Main KPI is a family-level default only. A variant or instance may override it when its intended player action differs; every override must record the reason and source.
- Distinguish observed result, measured lift, attributed lift, correlation, and causal evidence.
- Concurrent promotions, holidays/events, album phase, LBP/Lotto peak, Dash Day, segment mix, placement, pricing, and missing controls prevent causal language unless explicitly controlled.
- Low-confidence evidence is directional or insufficient evidence, never a confirmed learning.
- Compare performance against a documented baseline, normally a same-day-of-week trailing window of at least 20 complete days. Never use a single adjacent day as a lift baseline.

## Required planning output

Every recommendation must state:

- expected KPI;
- expected direction and range;
- applicable segment and calendar context;
- supporting historical instances;
- confidence and evidence label;
- risks and confounders;
- an alternative recommendation.

If those fields cannot be supported, return **insufficient evidence** rather than inventing an answer.
