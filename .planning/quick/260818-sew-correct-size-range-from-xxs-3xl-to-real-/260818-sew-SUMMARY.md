---
id: 260818-sew
status: complete
date: 2026-08-19
commits: 3997a4e, 4a35492
---

# Quick Task 260818-sew — Summary

Corrected the advertised size range from **XXS–3XL** to **S–4X**, the range the
supplier actually stocks, and replaced the size guide's invented measurements with
the manufacturer's published chart.

## Why

The Elegant Moments inventory feed contains no XXS and no XS — not a single row.
Advertising sizes that cannot be bought drives returns and erodes trust. The
supplier's chart documents XS but they never stock it.

## Changes

| File | Change |
|---|---|
| `sections/sizing-banner.liquid` | Size pills `XXS,XS,S,M,L,XL,2X,3X` → `S,M,L,XL,1X,2X,3X,4X` (schema default and fallback both) |
| `sections/ticker.liquid` | "Inclusive Sizing XXS–3XL" → "S–4X" (both marquee copies) |
| `sections/brand-promise.liquid` | Promise heading "Sizes XXS–3XL" → "Sizes S–4X" |
| `sections/page-sizeguide.liquid` | Real chart + Cup and Dress Size columns; new One Size table |
| `assets/size-guide.js` | `SIZE_TABLE` replaced with manufacturer measurements |
| `scripts/reference-product.json` | Test product sizes aligned |
| `CLAUDE.md`, `buildSpec.md`, `PROJECT.md`, `REQUIREMENTS.md` | Stated range corrected |

## Notes

- The banner's fallback default previously disagreed with its own schema default
  (`2X,3X` vs `1X,2X,3X`) — a live bug flagged in 03-VERIFICATION.md. Both now
  read `S,M,L,XL,1X,2X,3X,4X`.
- Added a **One Size** table (O/S, Q/S). O/S is roughly 37% of sellable rows;
  "one size" is meaningless to a shopper without the range behind it. Includes the
  hosiery height/weight ranges.
- XS is omitted from the recommender despite appearing on the supplier chart,
  since it is never stocked.
- Historical planning docs under `.planning/phases/` were left as-is — they record
  what was decided at the time.
- Verified: all three touched section schemas parse as valid JSON, and
  `reference-product.json` is valid. Relevant because Shopify's GitHub sync
  silently drops files that fail validation.
- No stored overrides in `config/settings_data.json`, so the new defaults apply.

## Not done

Size range is corrected everywhere it is stated, but no product data ships an
`XS`; nothing further is required for the current catalogue. If a future supplier
carries XS or XXS, the banner is merchant-editable from the theme editor.
