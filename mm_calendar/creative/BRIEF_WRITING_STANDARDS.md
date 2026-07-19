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

### Trigger and prize (labeling)

**Prize Change** applies when the **player trigger is the same** but the **visible reward differs** — break piggy, finish quest island, complete Shiny Show, claim milestone, etc. Structure, theme, and entry flow stay; only art-visible prizes, counts, or currency types change.

**New theme for promo** is same trigger + same prizes with a different visual theme. **Reuse** is same trigger, same prizes, same theme. Do not label a prize-only delta as theme change unless Itay explicitly treats it as theme work.

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

When no product-specific schema exists and the label is **not** Prize Change or New theme for promo: `Task` · `Keep` · optional `Theme / Art Guidelines` · optional `Numbers / Prizes / Amounts` · `Reference` · `Reference Link`.

### MGAP UI

Every real MGAP promotion has a separate `MGAP UI - <variant>` parent in addition to the regular promo brief/Reuse row. Keep only UI-related subitems. The UI table is: `Task` · `Keep` · `Mechanic` · optional `Reference` · `Reference Link`. Apply this to embedded MGAP mechanics such as a Rolling MGAP ladder; do not apply it to RLAP/Stash Booster.

## Row rules

- **Main Messages:** one-sentence takeaway for this asset, not literal headline copy.
- **What to change:** only the **delta** — plain language, one line per change. Do not list what stays the same (no “keep layout unchanged…”). Multiple prizes → **one table row per prize** (repeat Reference / Reference Link on each row).
- **Reference:** **short ref name only** (date + execution + asset, e.g. `2026-07-06 Spinner Clash — Main Inapp`). Optional embedded preview in this cell only. **No** match-tier essay, MM description dump, or “see attached in Monday” filler.
- **Reference Link:** CRM3 **folder** path for Prize Change and New theme for promo (never a Monday `protected_static` PNG URL in this row).
- **Timer:** include `Timer | yes` only when explicitly required by the mechanic/source.
- **FP:** use only when the asset/template requires it; never infer.

`5*reg` means one 5-star Regular card; the number is the star rating, not quantity.

## Denom rules

- Labels are exactly `Denom 1`, `Denom 2`, `Denom 3`; do not put price, package name, or role in the label.
- Values contain prizes only.
- Match row count to actual denom count.
- If tier roles are operationally necessary, put one concise row in the table; do not append prose outside it.

## CRM3 reference ladder (agent / MM — not in Reference row)

When picking a CRM3 folder, search in this order:

1. **Same trigger + same prize** — reuse or strongest ref.
2. **Same trigger + different prize** — preferred for Prize Change.
3. **Same feature, weaker match** — only if nothing closer; optional **one short note in parent Change** if the gap matters to design.

Do **not** paste ladder prose into the subitem **Reference** cell. Designer sees ref name + folder link only.

Preview PNGs may embed in **Reference** when uploaded; **Reference Link** stays a **folder** path.

## Inapp types (designer-facing)

| Type | Role | Typical content |
|---|---|---|
| **Main inapp** | Entry / hub | Prize strip, CTA into the promo, core mechanic framing |
| **Journey inapp** | Mid-event frames | Progress, rank, mission track, interim prizes |
| **Winner inapp** | End / results | Podium, claim, summary of what the player won |

Banner, PP Banner, BG, denoms, and widgets follow `PRODUCT_PLAYBOOK.md` per product. When scope is unclear, mirror the latest comparable execution’s inapp split (Main vs Journey vs Winner), not the duplicated template alone.

### Winner inapp requirement

Use **Winners Inapp** only where the product playbook or a prior shipped brief includes it (e.g. Piggy break payout, Battlesheep, Custom Pod, PYP journey/winners).

**No Winners Inapp** for:

- **Store / pre-purchase offers** (Daily Deal store cell, RYD denoms, Rolling, Decoy, etc.) — the inapp is **before** purchase, not a post-win claim.
- **Spinner Clash** — **Main Inapp**, **Journey Inapp**, **Banner** only (mirror prior Spinner briefs).

**Card-only** payouts: no Winner inapp; note `card-only — no winner inapp` in scope if needed.

**MGAP UI** already shipped for the day: do **not** open a standalone MGAP UI brief (`skip_brief` in overrides / script).

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

## Creative Traffic → Monetization-Art people

Source board `18041947639` (`Creative Owner` = column `people3`). Target board `18112190666`:

| Traffic column | Monetization-Art column | Column id |
|---|---|---|
| Brief Date | Brief Due Date | `date_mkwj8wwp` |
| Creative Owner — **1st person** | **Artist** | `multiple_person_mkwetsg8` |
| Creative Owner — **2nd person** (if any) | **Copywriter** | `multiple_person_mkwev9a5` |
| Monetization | MM | `person` |
| MM TL | MM TL | `multiple_person_mkwetd0y` |
| TL Owner | Creative TL | `multiple_person_mkwez377` |

Putting both Traffic owners on Artist only is wrong (copywriter ends up invisible to Copy Status workflows).

## Per-label subitem tables (training / Description HTML)

Parent row stays the hybrid **`Creative Label` + `Change`** summary. Subitem bodies are table-only. For agent training, use these row sets (CRM3 **folder** paths in **Reference Link** unless Itay asks for a direct PNG path; embed matching PNGs in **Reference** when uploading):

| Label | Subitem rows |
|---|---|
| **New theme for promo** | What to change · Reference · Reference Link |
| **Prize Change** | What to change · Reference · Reference Link |
| **New promo** | BG · Main Message · Ref · Ref Link |

Reuse has no asset subitems (day-level summary only).

**Reuse Reference Link rules (Jul 2026):**

- **Product match:** ADS PO reuse must cite **Rewarded Video / PJMS ADS** CRM3 roots — never paid Personal Offer, ROOC, or generic PO sale folders from legacy template text.
- **Rolling Supersized (non-themed MM rows):** default reuse folder is generic **`Supersize_Wins\…\2025_04_06_Supersized_Wins_X_RO`** — not Easter/Halloween/Thanksgiving skin folders unless the MM row is explicitly themed.
- Reuse **Reference Link** cells use CRM3 **folder** paths (not Monday `protected_static` PNG URLs).

### Bad vs Good — Prize / Theme Change subitems (Itay Jul 2026)

**Bad (do not ship):** four-row `Task` · `Keep` · `Reference` · `Reference Link` tables where Task says “Apply the parent Change to Main Inapp.”, Keep says “Match the reference for everything else.”, and Reference Link is a `monday.com/protected_static/...png` URL.

**Good:** multi-row **`What to change` · `Reference` · `Reference Link`** when several prizes change. Each **What to change** cell states **only the delta** in simple English. **Reference** is a short label (optional preview in that cell). **Reference Link** is a CRM3 **folder** path.

Parent stays hybrid: **Creative Label** + **Change** one-liner (e.g. `Break prize: 5 Hammers → 2 PAB`).

**Generic actionable asset** (`Task` · `Keep` · …) remains for **New promo** skeletons and products without a Prize/Theme schema — not for Prize Change or New theme for promo.

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
- Subitem set and order match `PRODUCT_PLAYBOOK.md` (Main / Journey / Winner inapps where required).
- Non–card-only rewards include Winner inapp **only when playbook/prior brief does** (not DD offers, not Spinner Clash).
- Reference row is **short ref name** only (no CRM3 ladder prose).
- What to change lists **deltas only** (plain language).
- Each **Reference** row states match tier (trigger/prize alignment or weaker feature match).
- Every subitem is table-only, concise, and free of creative direction.
- Every available preview matches its asset type and mechanic; Reference Link is exact.
- All four subitem gate/copy fields are blank.
- Post-automation stray cleanup and final verification completed.
