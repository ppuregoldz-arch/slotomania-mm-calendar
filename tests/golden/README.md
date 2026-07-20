# Trained behavior baseline

`department_tools.json` is the versioned regression baseline for behavior that must survive department contributions.

Version 1 protects:

- discovery and canonical routing for all four Cursor Skills;
- conservative forecast capability boundaries;
- MES, 24-hour, midnight, Night Plan, Promo Time, and Monday-offset timing behavior.

Do not update an expected value merely to make a failing check pass. A baseline change requires:

1. explicit approved authority or validated evidence;
2. a canonical rule/document update;
3. a Pull Request explaining current versus new behavior;
4. CODEOWNER approval.

Generated or live Monday exports are evidence, not automatically golden truth.
