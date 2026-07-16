# Canonical Promotion Identity

**Version:** 1.0  
**Last updated:** July 2026  
**Applies to:** `performance/instances/promo_instances.jsonl`, canonical variant documents, measurement registers, and prediction evidence.

## Three identity levels

### Promo family

The durable product or mechanic lane used for planning and aggregation, such as `daily-deal`, `rolling-offer`, `mgap`, `shiny-show`, or `core`.

A family answers: **which product/mechanic owns this promotion?**

### Promo variant

A repeatable design within a family whose core player action, mechanic, or offer topology is materially distinct and can be compared across occurrences. Examples:

- `daily-deal / hammers`
- `rolling-offer / buy-more-for-less`
- `mgap / bogo`
- `shiny-show / joker-different-prizes`
- `core / spin-zone`

A variant answers: **which repeatable treatment was used?**

### Promo instance

One scheduled occurrence of one variant for a defined time window and audience. It preserves the exact Monday/Smart Calendar row, date, duration, pricing, segment, rewards, placement, and concurrent context.

An instance answers: **what ran, when, where, and for whom?**

## Variant versus instance decision rules

Use this order. Stop at the first rule that applies.

| Change | Identity result | Reason |
|---|---|---|
| Family/product lane changes | New family and variant | Different operating product |
| Core mechanic or required player action changes | New variant | Measures a different behavior |
| Offer topology changes materially | New variant | Examples: BMFL vs BXGY; 1-cycle vs 5/6-cycle only when the cycle count is a managed repeatable design |
| Named, repeatable treatment changes | New variant | Examples: MGAP BOGO vs Matched; Shiny Joker vs All Cards |
| Main KPI/intended player action changes | New variant, or documented variant-level KPI override if the treatment is otherwise identical | Prevents unlike outcomes being pooled |
| Reward family changes and is the named treatment | New variant | Example: DD Hammers vs DD SB Wheel |
| Reward quantity/star level changes only | New instance | Configuration strength, not a new mechanic |
| Price tier/price point changes only | New instance | Store as instance attributes; compare as a pricing slice |
| Segment/audience changes only | New instance | Store audience on the occurrence; do not duplicate the design |
| Duration/timing changes only | New instance | Store exact window and placement |
| Promo Time/Night Plan/board placement changes only | New instance | Placement is a confounder/context field |
| Theme, art, event skin, copy, or seasonal SKU substitution only | New instance | Unless it changes the mechanic/player action |
| Minor punctuation, spacing, date suffix, or operational wording changes | Same variant; separate instance | Normalize for deduplication |

When evidence does not establish whether a named treatment is repeatable, assign the conservative family variant `other` or `unclassified`; log the ambiguity instead of inventing a variant.

## Canonical names

- IDs use lowercase ASCII kebab-case.
- Family IDs use the product/mechanic name: `daily-deal`, `rolling-offer`, `mgap`.
- Variant IDs use `<family-id>--<variant-slug>`.
- Human names preserve standard product capitalization.
- Legacy equivalents are aliases, not duplicate identities:
  - `Reveal Your Deal` = `RYD`
  - `M.E.S Steps Offer` = `M.E.S Tokens Offer`
  - `Counter PO` = `Limited PO` only when the source context confirms the same treatment
  - punctuation/spacing variants of `Boosted Gemback` share one identity

## Instance IDs

Preferred:

```text
<variant-id>--<start-date>--<source-system>-<source-row-id>
```

Example:

```text
rolling-offer--buy-more-for-less--2026-05-10--monday-123456789
```

If no stable source row ID exists:

```text
<variant-id>--<start-date>--<segment-slug>--<short-content-hash>
```

The hash is derived from normalized family, variant, start/end, segment, pricing, name, and description. It is a technical identity aid, not a business attribute.

## Deduplication

1. Prefer exact stable source ID (`promo_id` or Monday item ID).
2. Apply latest-version logic to Smart Calendar: latest `update_ts`, then `insert_id`, per `promo_id`.
3. Remove cancelled/canceled rows and `Operation - Daily View` wrappers.
4. Do not collapse distinct audience rows into one instance. Link them through `logical_promo_group_id`.
5. When measuring family/day outcomes, deduplicate by `(date, family_id)` so segmented rows do not multiply the same daily KPI.
6. For exact duplicate rows without stable IDs, compare the normalized identity tuple used by the fallback hash.
7. Keep both source references when Monday and Smart Calendar represent the same occurrence; select one canonical instance and record the other under `source_refs`.

## Main KPI inheritance

1. Start with the family default in `DATA_MODEL.md`.
2. Apply a variant override when that repeatable treatment targets a different player action.
3. Apply an instance override only when the source explicitly identifies a different objective for that occurrence.
4. Every override requires `main_kpi_override.reason` and `main_kpi_override.source`.
5. Missing intent does not justify an override.

## Examples

| Source rows | Canonical identity |
|---|---|
| DD Hammers, High, May 1 and DD Hammers, Max, May 3 | Same `daily-deal--hammers` variant; two instances |
| DD Hammers and DD SB Wheel | Two variants in `daily-deal` |
| Rolling BMFL and Rolling BXGY 6 cycles | Two variants in `rolling-offer` |
| Shiny Show All Cards and All Cards Joker | Separate variants if Monday names/mechanics preserve those treatments |
| Coin Sale split into PU/DPU/NPU rows | Separate audience instances linked by one logical group |

## Non-inference rule

No parser may derive a reward, segment, duration, KPI, or mechanic not present in a source or an approved mapping. Unknown values remain null and are registered in `MISSING_DATA_REGISTER.md`.
