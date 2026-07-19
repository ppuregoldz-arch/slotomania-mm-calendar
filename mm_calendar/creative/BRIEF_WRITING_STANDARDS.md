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

No other parent Reference, Reference Link, Assets, Skeleton, mechanic prose, or art direction. Reuse is the exception: one consolidated day-level summary with no subitems.

### Trigger and prize (labeling)

**Prize Change** applies when the **player trigger is the same** but the **visible reward differs** — break piggy, finish quest island, complete Shiny Show, claim milestone, etc. Structure, theme, and entry flow stay; only art-visible prizes, counts, or currency types change.

**New theme for promo** is same trigger + same prizes with a different visual theme. **Reuse** is same trigger, same prizes, same theme. Do not label a prize-only delta as theme change unless Itay explicitly treats it as theme work.

### Subitem updates

- Body is only `<table>...</table>`; no leading or trailing prose.
- **Layout:** vertical field table — each label is a **left column row**, content in the **right column**, read top to bottom (`What to change` → optional **`Theme`** → optional **`Hook`** → optional **`SKU`** → `Reference` → `Reference Link`). Match live briefs such as [Battlesheep (vertical table)](https://playtika.monday.com/boards/18112190666/pulses/12393938324); never use a horizontal header row with three field names as columns.
- **`SKU` row:** Battlesheep / Blast **only** when MM **Description** defines a **season challenge** and names the reward SKU — omit otherwise.
- Use the shortest unambiguous sentence in each cell.
- **`Theme` row:** include when MM name/description states a named theme or explicit `Generic` / `Generic theme`. Value is the theme name only (`Betty Boop`, `Cozy`, `4th of July`, `Generic`). Do **not** invent a theme when the calendar row is variant-only with no theme token.
- Include only theme name, prizes/amounts, mechanic facts, required format constraints, CTA destination, and reference.
- Never prescribe palette, colors, decorative motifs, mood, atmosphere, composition, typography, headline/button copy, or quoted copy.
- Never repeat promo date, due dates, priority, category, status, or internal **pricing tier** (H/M/Max pricing, `| H Pricing` suffixes, etc.).

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
- **What to change:** only the **delta** — plain language, one line per change. Do not list what stays the same (no “keep layout unchanged…”). No internal jargon (e.g. “count badge”) — describe what the player sees. Multiple prizes → **extra rows** labeled `What to change` (stacked top-to-bottom), then one `Reference` row, then one `Reference Link` row — **not** a sideways 3-column grid.
- **Reference:** **embedded preview only** when a matching asset exists — **no wording** in this cell (no ref name, match tier, or “see Monday”). Empty cell if no preview yet.
- **Reference Link:** CRM3 **folder** path only (never a Monday `protected_static` PNG URL in this row).
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
4. **Non-themed execution** — when the calendar day is **generic** (Winovate, Blast, standard DD/SB+hammers, etc.) or label is **Prize Change**, pick CRM3 folders from **regular Features paths**, not `Holidays & Events` or holiday skins (4th of July, Easter, Thanksgiving, XmasInJuly, …). Use themed folders **only** when label is **New theme for promo** **and** MM names that same theme.

### Gems coupon (generic default)

- **Creative source:** Monetization-Art **`11415353948`** (`2026-03-14` Gems Coupon). MM row override **`12511095622`** → same source (not Pre-Easter **`11621408835`**).
- **Scope:** **`Inapp` only**. Do not create `store denom`.
- **Reference (preview):** Embed the actual designer PNG uploaded on pulse [11415353948](https://playtika.monday.com/boards/18112190666/pulses/11415353948), including attachments in the parent Update (for example `Gems_Coupon_Superbowl_Inapp_IC_145.png`). The designer attachment outranks old path prose.
- **Reference Link:** `Q:\Slotomania\CRM3\Features\Gems\2026\2026_03_14_Gem_Coupon\Inapp`.

### Prize Mania

- Pricing (`H/M/L/Max price` or Pricing column) is configuration only: remove it from the Creative title, Change, What to change, and Hook.
- The **visible prize list from the MM Description is the hook**. Put those prizes in `Change`, the asset delta, and `Hook` on Banner/Inapp.

### MGAP UI

- A request for **basic UI** creates exactly one subitem named **`MGAP UI`**.
- Never call it `Full theme UI` and do not request a full-theme package unless MM explicitly asks for one.

Do **not** paste ladder prose or ref labels into the subitem **Reference** cell. Designers use **Reference Link** (folder) + preview image.

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

- **Store / pre-purchase offers** (Daily Deal store cell, RYD denoms, Rolling, etc.) — the inapp is **before** purchase, not a post-win claim.
- **Decoy Bonanza / multi-denom decoy:** no Monetization-Art brief — calendar treats these as **single** offers; do not brief three-denom decoy structures.
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
3. Date and people writes can silently drop after duplication. **Always** clear then set Artist (`multiple_person_mkwetsg8`) and Copywriter (`multiple_person_mkwev9a5`) from Creative Traffic on every apply — duplicated templates often copy both owners onto Artist only. Verify all date/team columns and retry idempotently.
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
| **New promo** | BG · Main Message · Benefits · Reference · Reference Link · **CTA** |

Reuse has no asset subitems (day-level summary only).

**Reuse Reference Link rules (Jul 2026):**

- **Product match:** ADS PO reuse must cite **Rewarded Video / PJMS ADS** CRM3 roots — never paid Personal Offer, ROOC, or generic PO sale folders from legacy template text.
- **Rolling Supersized (non-themed MM rows):** default reuse folder is generic **`Supersize_Wins\…\2025_04_06_Supersized_Wins_X_RO`** — not Easter/Halloween/Thanksgiving skin folders unless the MM row is explicitly themed.
- Reuse **Reference Link** cells use CRM3 **folder** paths (not Monday `protected_static` PNG URLs).

### Bad vs Good — Prize / Theme Change subitems (Itay Jul 2026)

**Bad (parent Change dump):** paste MM Description / Name into Change or What to change — e.g. `Theme/layout delta: Rolling Offer - 4th of July → Rolling Offer - 4 cycles (Buy X Get Y) · MGAP ladder… — Platform: … · Short Term: SNL… · Same day: X2 Extreme Stamp…` (season stack, Ops config, same-day promos).

**Bad (themed DD ref on generic day):** Reference Link `…\Holidays & Events\…` or `…XmasInJuly…` when the DD row is generic Shiny+hammers (Prize Change).

**Good (Rolling + MGAP parent Change):** `Theme: 4th of July → Generic; Add MGAP denom 3 (cycles 2–4) on Rolling ladder; 4 cycles Buy X Get Y`

**Good (DD Reference Link):** `Q:\Slotomania\CRM3\Features\Daily_Deal\2026\2026_07_09_DD_Hammer_Wheel` (generic hammer/wheel structure — not holiday DD skin).

**Bad (do not ship):** `Task` · `Keep` tables — e.g. Task “Apply the parent Change to Background.” and Keep “Match the reference for everything else.” Never ship **Keep**; never use pointer Task rows on actionable assets.

**Bad (Rolling):** briefing **Denom Buy** / buy-free denom slots by default; vague denom line with no MGAP/denom name.

**Good:** vertical **`What to change` → `Theme` (when MM states one) → `Reference` (image only) → `Reference Link` (folder)**. **What to change** = plain creative action (theme hook, prize delta, or named denom work).

**Good (Rolling + MGAP ladder):** Background — `Make the MGAP ladder the main visual hook of this Rolling offer.` · MGAP denom subitem — `Build MGAP denom 3 (cycles 2–4; new for this Rolling promo).`

**Good (Background / theme):** `Reskin this Background to the Betty Boop theme.` — not “Apply the parent Change to Background.”

Parent hybrid: exactly **Creative Label** + **Change** one-liner. Theme and Hook rows belong only in applicable asset subitems.

- **`Hook` row:** only on **Banner** and **Inapp** subitems (not Background, denom, MGAP denom, Theme/BO, etc.). Examples: Golden Spin **`30% Bigger Wedges`**; MGAP **`BOGO`**; Rolling **`MGAP denom 3 ladder`** on banner/inapp only.

Example Golden Spin subitem stack (HTML):

```html
<tr><td><p>What to change</p></td><td><p>Reskin this Banner to the Betty Boop theme.</p></td></tr>
<tr><td><p>Theme</p></td><td><p>Betty Boop</p></td></tr>
<tr><td><p>Hook</p></td><td><p>30% Bigger Wedges</p></td></tr>
<tr><td><p>Reference</p></td><td><p></p></td></tr>
<tr><td><p>Reference Link</p></td><td><p>…CRM3 folder…</p></td></tr>
```

Example Rolling MGAP denom **What to change** row:

```html
<tr><td><p>What to change</p></td><td><p>Build MGAP denom 3 (cycles 2–4; new for this Rolling promo).</p></td></tr>
```

**New promo** skeletons use **`BG` or `Main Message` · `Benefits` · `Reference` · `Reference Link` · `CTA`** (vertical) — not Task/Keep and not the Prize Change `What to change` stack.

### Stickers Sources (Lucy's Hunt season)

- **Layout reference:** Monetization-Art **`12093956694`** (*4th of July Stickers* / Lucy's BBQ Hunt) — duplicate that brief's structure, not the generic RE-USE template.
- **Per day:** Match subitem **`Day N - Source`** (day 1 = **`Day 1 - Source (first)`**) for **Reference** image from the layout brief; **Reference Link** = `Q:\Slotomania\CRM3\Features\Lucy's_Hunt\2026_07_04_Lucy's_BBQ_Hunt\Inapp\Inapp_How_To` (reskin layout; art folder unchanged until MM ships new hunt skin).
- **Copy:** MM Calendar **Description** numbered list = sticker source tiles for that day → **Benefits** on the **Inapp** subitem; parent **Change** = `Day N/5 sticker sources: …`.
- **Status MM:** **`Waiting for MM`** when the MM source list is present (not an empty New-promo skeleton). Season header row (*Stickers - Lucy's Hunt - 5 Days*) is **not** a separate Art brief.

## Status and edit safety

- Before any mutation to an existing brief, query **Status MM** (`color_mkwes65f`).
- Non-blank Status MM means in flight: stop and ask Itay. Use an override only after explicit approval.
- When the agent finishes a **complete** active brief (Prize Change, New theme for promo, or finished New promo), set **Status MM** = **`Waiting for MM`** — MM reviews and sets **`Ready for Brief`** when ready for Creative. Leave **Status Creative** (`status`) empty unless Creative/copy has started.
- **New promo** skeleton still in progress: Status MM = **`MM work in progress`**.
- Consolidated **Reuse** parent: Status Creative = `done`, Status MM = **`Ready - no action needed`** (unchanged).
- After writing/recreating each subitem, blank Copy Status (`status` on subitem board), Art Status, TL Approval, and Subject Line on subitems.
- Never set Copy/Art Done merely because the brief was written.

## Completion checklist

- Correct date group, clean title, and valid Product label or blank.
- Promo, Art Due, Brief Due, and assigned team verified.
- Art folder link blank.
- Parent contains exactly Creative Label + Change.
- Subitem set and order match `PRODUCT_PLAYBOOK.md` (Main / Journey / Winner inapps where required).
- Non–card-only rewards include Winner inapp **only when playbook/prior brief does** (not DD store offers, not Spinner Clash). **DD with SB + hammers:** `store denom` + `Inapp`; still no Winners.
- Reference row is **preview only** (no prose).
- What to change lists **deltas only** (plain language).
- Every subitem is table-only, concise, and free of creative direction.
- Every available preview matches its asset type and mechanic; Reference Link is exact.
- All four subitem gate/copy fields are blank.
- Post-automation stray cleanup and final verification completed.
