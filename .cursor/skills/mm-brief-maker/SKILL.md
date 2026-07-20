---
name: mm-brief-maker
description: Creates, reviews, or repairs Slotomania Monetization-Art briefs from approved MM calendar rows using Creative labels, product playbooks, and verified CRM3 references. Use when the user asks for Creative briefs, asset subitems, references, or Monetization-Art Monday work.
---

# MM Brief Maker

## Read first

1. `DEPARTMENT_TOOL_CONTRACTS.md`
2. `mm_calendar/00_GUIDELINES_ITAY.md`
3. `mm_calendar/creative/LEARNINGS_BRIEFS.md`
4. `mm_calendar/creative/CREATIVE_LABEL_RULES.md`
5. `mm_calendar/creative/PROMOTION_GLOSSARY.md`
6. `mm_calendar/creative/overrides.yaml`
7. `mm_calendar/creative/BRIEF_WRITING_STANDARDS.md`
8. `mm_calendar/creative/CRM3_REFERENCE_MAP.md`
9. `mm_calendar/creative/PRODUCT_PLAYBOOK.md`
10. `.cursor/rules/slotomania_monetization_art.mdc`

## Workflow

1. Confirm exact dates, approved MM rows, and dry-run versus live-write intent.
2. Classify each row before composing any brief.
3. Derive parent and subitems only from the product playbook and explicit MM content.
4. Use verified designer assets and exact CRM3 evidence; never invent a theme or reference.
5. Consolidate Reuse exactly as documented.
6. Run a dry-run and inspect every proposed parent, subitem, people mapping, status, and reference.

Current writer:

```bash
python3 scripts/apply_selected_august_creative_briefs.py --date YYYY-MM-DD
```

Live writes require an explicit request:

```bash
python3 scripts/apply_selected_august_creative_briefs.py --date YYYY-MM-DD --commit
```

## Safety

- Stop on an in-flight `Status MM` unless explicit override permission is given.
- `--rebuild` is destructive and requires exact approval.
- Never add Creative pricing prose.
- Never create Decoy multi-denom art briefs.
- Do not use historical examples as authority over current standards.

## Output

Return the exact date, source MM rows, classification, parent/subitems, reference evidence, validation result, external-write status, and pulse IDs for approved writes.
