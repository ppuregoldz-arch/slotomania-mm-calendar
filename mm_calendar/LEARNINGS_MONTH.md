# Month-planning learnings

**Last updated:** July 2026  
**Purpose:** Start-here index for planning an MM calendar month. Detailed rules, evidence, and month-specific limits remain in their canonical files.

## Authority and reading order

1. [00_GUIDELINES_ITAY.md](00_GUIDELINES_ITAY.md) — highest standing authority after Itay's live instruction.
2. [BUILD_CALENDAR_ROUTER.md](BUILD_CALENDAR_ROUTER.md) — route each planning question to the correct topic.
3. `monthly_guidelines/YYYY-MM.md` — HARD economy ceilings and weekly card bank for the target month.
4. [documentation/MONTH_BUILD_DECISION_TREE_COLORED_HE.md](documentation/MONTH_BUILD_DECISION_TREE_COLORED_HE.md) — end-to-end month flow.
5. [rules_cheatsheet.md](rules_cheatsheet.md), [constraints.md](constraints.md), and [PRIZE_PRIORITY_AND_MONTH_BUILD.md](PRIZE_PRIORITY_AND_MONTH_BUILD.md) — construction and validation.
6. [learnings.md](learnings.md) — detailed operating learnings; [daily_mm_reports.md](daily_mm_reports.md) — observed daily evidence.
7. Agent workflow is enforced by [mm_calendar_builder.mdc](../.cursor/rules/mm_calendar_builder.mdc).

## Confirmed HARD learnings

- **Never infer missing rules or numbers.** Ask for missing month guidelines, reward allocations, caps, card banks, or business decisions.
- **Month ceilings and card banks stay HARD** unless Itay explicitly approves an exception to that exact constraint.
- **Build order:** seasons/album phase → anchors → Daily Deal → real second offer + pricing → Core/gem sinks/clan → amplifiers → ADS last.
- **ADS is separate from Daily Deal.** It is its own low-tier product and is planned only after the rest of the day.
- **Daily VFM:** Every day needs a real second offer beyond Daily Deal; Clan-Dash / Dash Pass do not count.
- **Pricing separation:** Daily Deal and the priced second offer use different pricing tiers.
- **MGAP:** Exactly two placements per full week; apply the documented partial-week exception only where specified.
- **BMFL:** Distinct from BXGY; three cycles, High pricing only, with approximately ten days minimum cooldown.
- **Hammers:** One product source per day.
- **Cards:** Every card reward must come from that week's month-specific bank. Gold is purchase-only.
- **Board density:** At most one gameplay Core and one Shiny Show per day; no Shiny Show on Monday; paired Daily Deals are merged into one board row.
- **Monday safety:** Never sync or mutate Monday without explicit approval and an exact day scope. Live August 1–15 rows remain planning authority unless Itay approves replacement.
- **Title authority:** When Monday Name conflicts with Description/Pricing, correct the latter to match Name.
- **Measurement:** A numeric KPI needs source, baseline, calculation date, confidence, and validation status. Use a documented trailing baseline of at least 20 complete days, not adjacent-day lift.
- **Evidence:** Low-confidence or confounded evidence is directional, never a confirmed learning.
- **Validation:** Build, audit, and season-SKU validation must pass before handoff. Do not hand-edit generated JSON to hide a builder failure.

## Month workflow

1. Confirm month type, target month, approved economy guidelines, live seasons, events, and business goals.
2. Build the month in the canonical order above while maintaining a reward/card ledger.
3. Resolve conflicts by authority; register unresolved evidence conflicts rather than silently choosing.
4. Validate HARD constraints and review board density.
5. Present for approval.
6. Sync only explicitly approved days to Monday.

## Maintenance rule

`learnings.md` remains the detailed month best-practices file. `TEAM_WORKLOG.md` records changes but is not a rule source. New confirmed planning rules must be added to the appropriate canonical document and summarized here.
