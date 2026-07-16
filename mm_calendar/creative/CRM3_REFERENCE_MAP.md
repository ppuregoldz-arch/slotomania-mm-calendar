# CRM3 Reference Map for Creative Briefs

**Last updated:** July 2026  
**Scope:** Reference selection for actionable, non-Reuse Monetization-Art briefs.

Use this after Creative Label classification. Monday history determines the correct source execution; this map finds the matching CRM3 asset. A Reuse item remains consolidated under `REUSE - No Creative Action`.

## Selection order

1. Ignore canceled tasks.
2. Prefer an older exact mechanic + theme + visible-prize match over a newer family-level match.
3. Within that execution, use the newest delivered Creative attachment for the same asset type.
4. Match the subitem asset type exactly.
5. Use one reference per subitem by default. Use two only when the asset genuinely combines two mechanics; label them `Layout` and `Theme cue`.
6. If no valid match exists, omit the preview and state that the reference is missing. Never attach misleading art.

## Asset-type matching

| Subitem | Valid reference | Reject |
|---|---|---|
| Background | True BG under `BG`, `Store_Assets/BG`, or `_mat` | Banner, preloader |
| Banner | Banner under the same mechanic's `Banner` folder | Different mechanic |
| PP Banner | `PP` or `PP_Banner` payment-page asset | Regular Banner |
| UI / Denoms | Rendered `UI/Store_Offer_Medium_*.png` tier cards | Inapp, blank `*_Template.png` |
| DD (in store) | Real DD store cell such as `DD_<prize>.png` | Inapp |
| Inapp | True Inapp screen for that mechanic | Banner or widget |
| Widget | Matching widget state(s) | Inapp or banner |

## Mechanic roots

| Mechanic | CRM3 root | Selection notes |
|---|---|---|
| Shiny Show | `Features/SlotoCards/X_SlotoCard_FEATURES/The_Shiny_Show/<year>/` | Do not use legacy `Features/PJMS/Shiny_Show`. For Joker, check sibling `Joker Promotions` first. |
| RYD | `Features/Reveal_Your_Deal/<year>/` | Prefer generic, non-themed, non-variant art. Clean examples: `2026_04_28_RYD_100SB_5GoldCard`; off denom: `2026_03_19_RYD_100%SB_Cheeky_Wins/BG/denom_OFF.png`. |
| Daily Deal | `Features/Daily_Deal/<year>/` | Prefer generic. Verify the folder contains a real image, not only `Thumbs.db`. Search the year index when the obvious folder lacks a DD store cell. |
| MGAP | `Features/MGAP/<year>/<date>_MGAP_*/` | Typical folders: `Inapp`, `Banner`, `PP`, sometimes `UI`. |
| Gem Machine | `New Games/Winning_Spins_Gems/<year>/<date>_<mechanic>/` | Not MGAP. Usually time-windowed Inapp/Banner. |
| Spin Zone | `Features/Spin_Zone/<year>/<date>_<prize>/` | Light four-subitem mechanic; distinct from MES-linear Spin Zone. |
| MES linear | `Features/MES/<date>_<mechanic>/` | No year subfolder. |
| Rolling Offer | `Features/Rolling_PO/<year>/` and `Features/Rolling_Offer/<year>/` | Search both. Avoid Reach/Get More for Less, SuperBoom, or Supersized unless requested. Generic examples: `2026_03_30_RO_Generic/Banner/RO_Banner.jpg`; `2026_03_04_RollingOffer_8FreePrizes/BG/`. |
| DD BOGO | `Features/Daily_Deal/<year>/<date>_DD_BOGO/DD/<date>_DD/` | Extra nested DD folder. Do not add Gems/Stamps unless present in the mechanic. |
| PJMS / DPU / NPU | `Features/PJMS/<year>/` | Search folder names for `DPU`, `NPU`, or `DPU_NPU`. |
| Decoy / Decoy Bonanza | `Features/DecoyOffer/<year>/` | Prefer generic art. Generic BG example: `2026_05_14_Decoy_Bonanza_Offer/BG/Decoy_Offer_Bonanaza_BG.jpg`; denoms: `2026_07_20_Decoy_Bonanza/Denom/Store_Offer_Medium_{1,2,3}.png`. Avoid themed folders unless requested. |
| Gatcha / Cocktail Bonus / SB Picker | `Features/Gatcha/<year>/` and `Features/Cocktail Bonus/<year>/` | Cocktail Bonus provides Inapp/Banner/PP; matching Gatcha provides pick-screen BG/UI/Logo/Header. SB Picker assets live under matching Gatcha folders. |
| PYP generic | `Generic Promotions/Pick_Your_Path/<year>/` | Use for non-Album PYP. |
| PYP Album | `Features/SlotoCards/X_SlotoCard_FEATURES/PickYourPath-Album_challenge/<year>/` | Use only for Album-based PYP. |

## Reference presentation

- `Reference` contains only the embedded image uploaded to Monday.
- `Reference Link` contains only the exact Windows path: `Q:\Slotomania\CRM3\...\filename.png`.
- Keep `/Volumes/CRM3/...` only for local upload code; never show it to the artist.
- When multiple required variants are delivered together, embed all required variants in one reference-cell thumbnail grid.
- If CRM3 is unavailable, keep the exact Windows path and leave the preview empty for later backfill. Never fabricate an image URL.
