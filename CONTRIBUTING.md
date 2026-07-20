# Contributing to the MM Department Cursor Tools

The goal is to improve shared knowledge without silently changing approved business logic.

## Start with feedback

Use the GitHub **Tool improvement** issue form when:

- an output is wrong or unclear;
- a rule is missing or contradictory;
- a new approved example should be learned;
- a workflow is too slow or difficult.

Include the tool, exact input, current output, expected output, source evidence, and whether Monday/DWH was involved.

## Make changes through a Pull Request

1. Create a feature branch from current `main`.
2. Change the canonical source. Do not duplicate a business rule inside multiple Skills.
3. Update the relevant Skill only when its workflow or entry point changed.
4. Add or update a golden regression when behavior changes.
5. Run:

```bash
python3 scripts/validate_department_tooling.py
python3 scripts/validate_ops_task_spec_rules.py
python3 scripts/validate_promo_knowledge_base.py
```

6. Complete the Pull Request checklist and request the required owner review.

## Protected areas

Changes in these areas require owner review and passing checks:

- `.cursor/rules/` and `.cursor/skills/`;
- `mm_calendar/00_GUIDELINES_ITAY.md`;
- month guidelines, constraints, reward banks, and canonical learnings;
- planning, forecasting, Creative, Ops, Monday, DWH, and GitHub scripts;
- generated plan and Ops specifications;
- GitHub workflows and ownership files.

No contributor may bypass review by editing `main` directly.

## Never commit

- `.cursor/mcp.json`;
- `.cursor/monday.env`;
- `.cursor/github.env`;
- credentials, tokens, secret URLs, or exported private data.

## External systems

A Pull Request does not authorize Monday, DWH, CRM3, or GitHub-setting mutations. External writes require the explicit scope and approvals documented by the relevant Skill.

## Evidence standard

- A live instruction from Itay is highest authority.
- Low-confidence or confounded evidence is not a confirmed learning.
- Numeric KPI claims require source, baseline, calculation date, confidence, and validation.
- If sources conflict, register the conflict instead of silently selecting one.
