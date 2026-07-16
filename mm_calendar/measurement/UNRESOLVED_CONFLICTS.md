# Unresolved Conflicts

**Last updated:** July 10, 2026  
**Rule:** Preserve both readings, their methods, and their intended use. Do not silently select a number.

| ID | Affected promo/method | Source A | Source B | Conflict and impact | Required action | Status |
|---|---|---|---|---|---|---|
| CF-001 | MGAP Bigger | `promo_revenue_analysis.md`: ~$235K/day product revenue, n=3 solo days, strongest MGAP variant | `smart_calendar_insights.md`: +0.5% wider clean family lift; selective Apr–Jul DWH cut: +3.82% whole-day DOW correlation, n=12 | Product revenue depth and standalone whole-day lift answer different questions; window/context changes the reading | Keep KPI/scope separate; selectively validate product revenue with approved payments | open |
| CF-002 | Extreme Stamp | Raw/event analyses and selective Apr–Jul DWH cut report positive correlation (+7.70%, n=23) | `smart_calendar_insights.md`: −0.2% wider clean standalone family lift | Conditional/event placement and window selection materially change the result | Treat as conditional/correlation; validate interaction terms before numeric recommendation | open |
| CF-003 | Golden Spin | `smart_calendar_insights.md`: −8.2% clean, −6.1% DOW matched, n=10; selective DWH: −5.32%, n=11 | Operational schedule treats it as a recurring Thursday anchor | Performance direction is consistently negative but sample is recent/thin and scheduling obligation may be independent | Preserve anchor rule; do not claim causal harm; gather additional occurrences | open |
| CF-004 | DD Hammers | `promo_revenue_analysis.md`: ~$133K product proxy, n=21, stable | Selective DWH whole-day DOW correlation: +0.27% revenue and −0.09% PU, n=38 | Product proxy is useful but does not establish total-day incremental lift | Query offer/product source for clean variant-level revenue | open |
| CF-005 | Holiday exclusions | `smart_calendar_insights.md` says 8 excluded dates | `calibrate_model.py` defines 10 dates including Memorial Day and July 4 | Baseline and backtest samples differ | Adopt one dated anomaly register after backtest sensitivity analysis | open |
| CF-006 | Clan Pack | Historical DD/Shiny analyses report performance | `00_GUIDELINES_ITAY.md` prohibits Clan Pack in future planning | Historical evidence is valid but recommendation eligibility differs | Mark historical-only; never recommend | resolved-policy |
| CF-007 | MGAP weekly count | Older cheatsheet/rule text allowed up to 3 | Itay standing rule is exactly 2/week | Could produce invalid calendars | `00_GUIDELINES_ITAY.md` supersedes older wording; sync routing/rules in Phase 5 | resolved-policy |
| CF-008 | Rolling BXGY structure | Old `rolling_bxgy_cycle_body` helper uses outdated stamp/free-step model | `rolling_offer.md` and live Monday examples use six-denom canonical cycle | Generated descriptions may be structurally wrong | Keep builder logic untouched unless separately requested; canonical docs win | resolved-policy |
| CF-009 | Main KPI by family | Older plan maps one KPI per family | Itay requires variant/instance overrides when player action differs | Forced family KPI can misclassify evidence | Use inheritance + documented override model in `DATA_MODEL.md` | resolved-policy |
| CF-010 | August MGAP plan | Itay rule: exactly 2/week, no Monday MGAP, spacing ≥2 days | Current August human audit reports `w2=3`, 9→10 spacing=1, and MGAP BOGO on Monday 10/8 | August draft is not compliant with standing policy | Fix through the August builder/plan workflow only after explicit plan-change approval; rerun builder and audit | open |
| CF-011 | August validation path | August source of truth is `august_2026_plan.json` plus `audit_august_2026_plan.py` | `validate_calendar.py` and dashboard audit still depend on a July canvas | Generic validation can report against the wrong calendar | Refactor validator/dashboard audit to read the August plan or clearly scope the legacy validator | open |
| CF-012 | Monday versus Smart Calendar | Monday/`real_months` provides planning copy and row structure | Smart Calendar live-at-snapshot classifications disagree on 63/122 Apr–Jul days; 27 Monday-only and 5 Smart-only | Instance identity and actual-live attribution can diverge | Preserve both sources; validate high-impact mismatches before attribution | open |

## Resolution standard

`resolved-data` requires a reproducible calculation with complete provenance.  
`resolved-policy` records a planning decision but does not erase historical evidence.  
Open conflicts lower confidence and block confirmed-learning language where material.
