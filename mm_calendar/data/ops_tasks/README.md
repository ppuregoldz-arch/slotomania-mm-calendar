# Generated Ops task specs

Review-only JSON specs from `scripts/build_ops_tasks_from_plan.py` are written here.

Example:

```bash
python3 scripts/build_ops_tasks_from_plan.py --day 1
python3 scripts/upload_ops_task_monday.py mm_calendar/data/ops_tasks/2026-08-01.json
```

The second command is a dry run. It does not write to Monday. Review every warning and replace all `TBD - owner required` values before any live write.

Live writing requires explicit approval and `--commit`. A missing day parent remains a blocker unless creation was separately authorized with `--create-day`.
