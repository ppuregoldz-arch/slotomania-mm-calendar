# Creative Label Rules

**Last updated:** July 2026
**Authority:** Explicit definitions supplied by Itay. These rules classify required Creative work, not merely calendar configuration changes.

## Labels

| Label | Use when | Required evidence |
|---|---|---|
| **Reuse** | The same mechanic, visual theme, visible prizes/mission, and required asset variants already exist; Creative changes nothing. Dynamic configuration that is not embedded in art may change. | A previous non-canceled matching execution. Missing art does not change the label; mark the reference as missing. |
| **Prize Change** | Same **player trigger** and Creative structure/theme; only a visible prize, mission, quantity, percentage, multiplier, currency, or value changes (break piggy, finish island, Shiny Show completion, etc.). | A previous **same-trigger** execution plus the exact `source → required` delta. Prefer a ref with same trigger and different prize over a loose same-feature ref. |
| **New theme for promo** | The mechanic/structure exists, but Creative must apply a different event, machine, season, or visual theme. | A previous matching structure and the exact old/new themes. If theme and prize both change, this label wins. |
| **New promo** | The mechanic or Creative structure has never existed. | No valid prior matching execution. Create a skeleton for Itay; do not invent mechanics or art direction. |

## Decision order

1. Ignore canceled tasks as historical evidence.
2. Determine whether the mechanic and Creative structure existed before.
3. If not, use **New promo**.
4. If the visual theme changes, use **New theme for promo**.
5. If any art-visible prize/mission/value changes, use **Prize Change**.
6. Otherwise use **Reuse**.
7. Audience/segment changes alone are **Reuse**.
8. A missing reference never converts an otherwise exact reuse into a new promo.

## Reference selection

**Trigger + prize ladder** (agent-internal; do not paste into subitem **Reference**): (1) same trigger + same prize → best reuse/ref; (2) same trigger + different prize → **Prize Change** ref; (3) same feature only → weaker; optional one line in parent **Change** if the gap matters.

1. Prefer an older exact promo match over a newer same-family task with different prizes or theme.
2. Within the selected exact task, use the newest matching Creative attachment, even if the task is not yet Approved.
3. Match asset type exactly: Inapp→Inapp, Banner→Banner, Widget→Widget, etc.
4. For Reuse, verify that the final image visibly matches the current prize and theme.
5. Do not use canceled tasks as evidence or as references.
6. If no matching asset exists, keep the correct label and explicitly mark **Reference missing**.
7. A confirmed matching promo/variant that previously went live on the Operation - Monetization board is valid Reuse evidence. If no exact Creative reference exists, link the Ops task and record the date it went live.
8. A same-family but different visible prize, theme, mechanic, or variant is not sufficient live evidence.

## Brief behavior

- **Reuse:** create exactly one day-level Monday item named `REUSE - No Creative Action`. List every Reuse promotion in that item with its promotion title, reuse-from date, Monday source pulse, and CRM3 reference path. Do not create separate per-promo Reuse items or asset subitems. Set the summary item to Completed.
- **Prize Change** and **New theme for promo:** use the delta subitem table (`What to change` → optional `Theme` / `Hook` / `SKU` → `Reference` → `Reference Link`). Any other actionable MM label (including explicit **New promo** or legacy/blank variants normalized by the applier) → **New promo** template.
- **New promo:** vertical subitem table **`BG` or `Main Message` · `Benefits` · `Reference` · `Reference Link` · `CTA`** (skeleton rows for Itay — do not invent mechanics or copy). Parent **Change** states the promo is a new skeleton.
- **Pricing:** never mention MM **pricing tiers** (H/M/Max pricing, `| H Pricing` in titles, etc.) in parent **Change** or subitem prose — pricing stays in MM/Ops columns only.
- **MGAP UI:** every real MGAP promotion also gets a separate parent task named `MGAP UI - <variant>` in the same day group, in addition to its regular promo brief or Reuse-summary row. The separate task keeps only MGAP UI subitems. This includes MGAP embedded in another offer (for example a Rolling MGAP ladder), but excludes RLAP/Stash Booster because it replaces the MGAP promo.
- Theme change takes precedence over simultaneous prize change.
- Active art-only work leaves both Copy Status and Art Status empty.
- Brief Due Date and people ownership come from `Creative Traffic` board `18041947639`: `Brief Date`, `Creative Owner`, `Monetization`, `MM TL`, and `TL Owner`. Map `Brief Date` → `Brief Due Date`; `Monetization` → `MM`; `MM TL` → `MM TL`; `TL Owner` → `Creative TL`. Split `Creative Owner` on Monetization-Art: first person → **Artist** (`multiple_person_mkwetsg8`), second person (when present) → **Copywriter** (`multiple_person_mkwev9a5`); a lone `Creative Owner` → Artist only. Do not assign both Traffic owners to Artist.
- Leave Status Creative empty for every non-Reuse brief until Creative starts. Monetization owns **Status MM** (`color_mkwes65f`): **`Ready for Brief`** when the agent finished a complete brief (handoff to Creative); **`MM work in progress`** for an incomplete New promo skeleton; **`Ready - no action needed`** for the Reuse summary. Reuse sets Status Creative to `done`.
- Art Due Date is at least 48 hours before launch. Move Friday/Saturday due dates back to Thursday.
- Keep briefs short. Subitem layout and row rules: `BRIEF_WRITING_STANDARDS.md` (vertical tables, **What to change** deltas only, **Reference** = preview only, **Reference Link** = CRM3 folder). Do not use Task/Keep rows for Prize Change or New theme for promo.

## Known exceptions

- **ADS Personal Offer:** reward quantities are dynamic; changing Coins quantity alone is Reuse.
- **Win Master through M.E.S:** open the complete Mission Event System asset set for Creative every time. Do not reduce scope to Banner-only based on a recent task.
- **Lotto Peak:** operational timing row only; no standalone Creative brief.
- Promo-specific definitions and exceptions are in `PROMOTION_GLOSSARY.md` and `overrides.yaml`.
