# Creative Brief Writing Standards

**Last updated:** July 2026  
**Authority:** Combined reviewer feedback and Itay's Creative Label workflow.

## Content contract

### Parent update: hybrid summary

The non-Reuse parent contains exactly one HTML table with two rows:

| Row | Content |
|---|---|
| Creative Label | `Prize Change`, `New theme for promo`, or `New promo` |
| Change | Exact `source → required` delta |

No parent Reference, Reference Link, Assets, Skeleton, mechanic prose, or art direction. Reuse is the exception: one consolidated day-level summary with no subitems.

### Subitem updates

- Body is only `<table>...</table>`; no leading or trailing prose.
- Use the shortest unambiguous sentence in each cell.
- Theme name appears as a name only, once per asset table when its schema includes Theme.
- Include only theme name, prizes/amounts, mechanic facts, required format constraints, CTA destination, and reference.
- Never prescribe palette, colors, decorative motifs, mood, atmosphere, composition, typography, headline/button copy, or quoted copy.
- Never repeat promo date, due dates, priority, category, status, or internal pricing tier.

## Asset table schemas

Mirror the relevant source template where it is more specific. Otherwise use:

### Background

`Main Messages` · `Theme / Art Guidelines` · `Numbers / Prizes / Amounts` · optional mechanic rows · `Reference` · `Reference Link` · `FP`

### Banner

`Main Messages` · `Numbers / Prizes / Amounts to be shown` · optional mechanic rows · `Reference` · `Reference Link` · `CTA`

### PP Banner

Same as Banner, but omit CTA because the payment page has no click destination.

### Denoms

One row per actual denom (`Denom 1`, `Denom 2`, `Denom 3`) · `Reference` · `Reference Link`

Do not add an `N/A` row for a denom that does not exist.

### Generic actionable asset

When no product-specific schema exists: `Task` · `Keep` · optional `Theme / Art Guidelines` · optional `Numbers / Prizes / Amounts` · `Reference` · `Reference Link`.

### MGAP UI

Every real MGAP promotion has a separate `MGAP UI - <variant>` parent in addition to the regular promo brief/Reuse row. Keep only UI-related subitems. The UI table is: `Task` · `Keep` · `Mechanic` · optional `Reference` · `Reference Link`. Apply this to embedded MGAP mechanics such as a Rolling MGAP ladder; do not apply it to RLAP/Stash Booster.

## Row rules

- **Main Messages:** one-sentence takeaway for this asset, not literal headline copy.
- **Task:** point to the parent's exact Change and name this asset.
- **Keep:** what must remain structurally unchanged from the reference; no visual direction.
- **Theme / Art Guidelines:** theme name only, such as `Generic.` or `Cozy.`
- **Numbers / Prizes / Amounts:** prize data only. If Itay omitted a required quantity, use `TBD — awaiting MM prizes`; do not invent it.
- **CTA:** destination, not button text: offer/inapp screen or checkout.
- **Reference:** embedded matching image only.
- **Reference Link:** exact Windows file path or direct attached-image URL only.
- **Timer:** include `Timer | yes` only when explicitly required by the mechanic/source.
- **FP:** use only when the asset/template requires it; never infer.

`5*reg` means one 5-star Regular card; the number is the star rating, not quantity.

## Denom rules

- Labels are exactly `Denom 1`, `Denom 2`, `Denom 3`; do not put price, package name, or role in the label.
- Values contain prizes only.
- Match row count to actual denom count.
- If tier roles are operationally necessary, put one concise row in the table; do not append prose outside it.

## Reference embedding

1. Remove existing editable updates from the subitem.
2. Create a placeholder update.
3. Upload local CRM3 image(s) through Monday `/v2/file`.
4. Build the table with the returned protected-static URLs inside the Reference cell.
5. Edit the placeholder into the final table.
6. If no valid file exists, omit the preview and preserve the exact Reference Link for backfill.

One reference per asset is the default. Multiple images belong in one thumbnail grid only when they are required variants or a genuine layout + theme-cue combination.

## Technical safeguards

1. Duplicate templates with `with_updates=False`; target exactly one editable update per subitem.
2. Board automation can create parent placeholders and late stray subitems. Wait for it to settle, then remove only unwanted subitems and re-verify.
3. Date and people writes can silently drop after duplication. Verify all date/team columns and retry idempotently.
4. Apply custom team overrides after finalization; finalization may overwrite them.
5. Retry `edit_update` on transient internal errors without re-uploading assets.
6. If automation deletes the placeholder during upload, create a fresh update using the already-uploaded URLs.
7. Body builders must accept `urls: list[str]` and tolerate an empty list.
8. Use GraphQL variables instead of interpolating braces where possible.
9. Preserve spaces and unusual Unicode in CRM3 names; quote paths in shell use.
10. Reordering subitems means recreate + delete. Preserve bodies, clear gate fields on recreated subitems, and require Status-MM approval first.

## Status and edit safety

- Before any mutation to an existing brief, query Status MM (`color_mkwes65f`).
- Non-blank means in flight: stop and ask Itay. Use an override only after explicit approval.
- After writing/recreating each subitem, blank Copy Status (`status`), Art Status (`color_mkwerpn6`), TL Approval (`color_mkwe6hz`), and Subject Line (`long_text_mkwyvrm1`).
- Never set Copy/Art Done merely because the brief was written.

## Completion checklist

- Correct date group, clean title, and valid Product label or blank.
- Promo, Art Due, Brief Due, and assigned team verified.
- Art folder link blank.
- Parent contains exactly Creative Label + Change.
- Subitem set and order match `PRODUCT_PLAYBOOK.md`.
- Every subitem is table-only, concise, and free of creative direction.
- Every available preview matches its asset type and mechanic; Reference Link is exact.
- All four subitem gate/copy fields are blank.
- Post-automation stray cleanup and final verification completed.
