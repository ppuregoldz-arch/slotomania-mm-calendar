# Monthly Knowledge and Performance Refresh SOP

**Last updated:** July 2026  
**Goal:** add a new month without rebuilding the knowledge system.

## 1. Import sources

1. Create dated copies/snapshots from Monday and DWH through approved pull scripts.
2. Preserve all incoming raw CSV/TSV files unchanged.
3. Record source window, pull date, owner/origin, and extraction command in `SOURCE_INVENTORY.md`.
4. Never replace an older raw snapshot as part of migration.

## 2. Validate schema and vocabulary

- Confirm required source fields exist.
- Parse every JSON/JSONL file.
- Validate dates and controlled vocabulary against `DATA_MODEL.md`.
- Record unknown names as `unclassified`; do not invent mappings.
- Register schema drift and unknown vocabulary.

## 3. Detect duplicates

- Apply Smart Calendar latest-version and cancellation rules.
- Prefer stable Monday/Smart IDs.
- Use canonical fallback hash only when no stable ID exists.
- Detect duplicate `instance_id` values.
- Link segmented audience rows with `logical_promo_group_id`; do not collapse them.
- Deduplicate family/day before attaching one daily KPI to family analysis.

## 4. Add promo instances

- Append one independently valid record per line to `performance/instances/promo_instances.jsonl`.
- Preserve chronological sorting in generated output.
- Add exact source references.
- Leave unavailable fields null/empty and register missing required evidence.

## 5. Refresh variant summaries

- Group instances by `variant_id`.
- Recalculate coverage, context distribution, and evidence counts.
- Never overwrite an existing result without retaining its prior source/baseline context.
- Update Main KPI overrides only when explicit evidence supports the intended player action.

## 6. Run selective Vertica validation

Query only:

- missing/conflicting high-impact results;
- non-reproducible numbers;
- critical recommendation evidence;
- backtesting inputs that could alter model eligibility.

Record query metadata and update both registers.

## 7. Recalculate confidence

- Apply `MEASUREMENT_METHODOLOGY.md`.
- Downgrade small-sample or confounded results.
- Never promote a correlation to causal evidence without a valid design.
- Low confidence cannot become a confirmed learning.

## 8. Update prediction evidence

- Add the new month to the historical holdout/backtest schedule.
- Recompute observed forecast errors before changing formulas.
- Revise expected ranges, confidence thresholds, eligibility, and insufficient-evidence rules only from documented error evidence.
- Mark the prediction guide draft whenever new evidence is not yet backtested.

## 9. Coverage and link checks

Report coverage by:

- month;
- KPI;
- family;
- variant.

Validate all internal links and source references. Report rather than hide unavailable external CSV paths.

## 10. Acceptance criteria

- 100% of instances have date, family, variant, and source.
- 100% of numeric KPI results have traceable provenance.
- Zero silently inferred values.
- Zero duplicate instance IDs.
- Zero broken internal links.
- All controlled vocabulary values are valid.
- All unresolved conflicts are registered.
- Coverage rates are reported by month, KPI, family, and variant.
- Backtesting results and failure cases are documented.

## Recommended commands

Run from the workspace root:

```bash
python3 scripts/build_promo_knowledge_base.py
python3 scripts/validate_promo_knowledge_base.py
```

For existing calendar artifacts after any plan change:

```bash
python3 scripts/build_august_2026_plan.py
python3 scripts/audit_august_2026_plan.py
```

Monday synchronization is never part of this SOP without separate explicit approval.
