# Creative Label Rules

**Last updated:** July 2026
**Authority:** Explicit definitions supplied by Itay. These rules classify required Creative work, not merely calendar configuration changes.

## Labels

| Label | Use when | Required evidence |
|---|---|---|
| **Reuse** | The same mechanic, visual theme, visible prizes/mission, and required asset variants already exist; Creative changes nothing. Dynamic configuration that is not embedded in art may change. | A previous non-canceled matching execution. Missing art does not change the label; mark the reference as missing. |
| **Prize Change** | The structure and theme already exist, but a visible prize, mission, quantity, percentage, multiplier, currency, or value changes. | A previous matching structure plus the exact `source → required` delta. |
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

1. Prefer an older exact promo match over a newer same-family task with different prizes or theme.
2. Within the selected exact task, use the newest matching Creative attachment, even if the task is not yet Approved.
3. Match asset type exactly: Inapp→Inapp, Banner→Banner, Widget→Widget, etc.
4. For Reuse, verify that the final image visibly matches the current prize and theme.
5. Do not use canceled tasks as evidence or as references.
6. If no matching asset exists, keep the correct label and explicitly mark **Reference missing**.

## Brief behavior

- **Reuse:** title includes `| Reuse from YYYY-MM-DD`; parent and no-action assets are Completed.
- **Prize Change:** state the exact visible delta for every affected asset.
- **New theme for promo:** state the exact theme delta and what remains unchanged.
- **New promo:** leave mechanics and direction for Itay; attach only clearly relevant inspiration.
- Theme change takes precedence over simultaneous prize change.
- Active art-only work leaves both Copy Status and Art Status empty.
- Brief Due Date is at least seven days before launch; Art Due Date is at least 48 hours before launch. Move Friday/Saturday due dates back to Thursday.
- Keep briefs short. Links contain only links/paths; PNG rows contain only real matching images.

## Known exceptions

- **ADS Personal Offer:** reward quantities are dynamic; changing Coins quantity alone is Reuse.
- **Win Master through M.E.S:** open the complete Mission Event System asset set for Creative every time. Do not reduce scope to Banner-only based on a recent task.
- **Lotto Peak:** operational timing row only; no standalone Creative brief.
- Promo-specific definitions and exceptions are in `PROMOTION_GLOSSARY.md` and `overrides.yaml`.
