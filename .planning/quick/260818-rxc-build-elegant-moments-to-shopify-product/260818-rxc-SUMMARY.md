---
id: 260818-rxc
status: complete
date: 2026-08-19
commits: 00ba32c, ce7c92a, bc69740
---

# Quick Task 260818-rxc — Summary

Built a re-runnable pipeline turning Elegant Moments' B2B wholesale exports into a
Shopify product import CSV.

## What was built

| File | Purpose |
|---|---|
| `data/suppliers/elegant-moments/build_import.py` | Join + transform + emit Shopify CSV |
| `data/suppliers/elegant-moments/README.md` | Licence constraints, refresh procedure, known gaps |
| `.gitignore` | Excludes `data/suppliers/*/source/` and `*/out/` |

## Result

396 products / 1,004 variants from 1,539 sellable inventory rows.

- 2,572 inventory rows → 1,539 sellable (dropped 875 discontinued, 251 zero-stock)
- 448 of 460 description styles matched inventory on `STYLE`
- 420 sellable styles skipped for lack of copy — need the Holiday, Hosiery and
  Vivace description workbooks

Validated: all prices end in `.95`, no blank handles or SKUs, no duplicate SKUs,
no duplicate option combinations within a product, `Option2` presence consistent
per product, sizes ordered wearably (S, M, L, 2X, 3X) rather than alphabetically.

## Decisions applied

- Retail = wholesale × 2.5 rounded to nearest `.95` (user choice)
- Shipping free over $75 else $7.95 — configured in Shopify, not in this CSV
- Products emit as `draft` so nothing publishes unreviewed
- `Vendor` = Elegant Moments and a `Brand:` line in every body, as the supplier
  licence requires attribution in advertising content

## Deviations from plan

None functionally. One thing the plan did not anticipate: the repo is **public**
(github.com/Cburgos7/BikinniSite), so gitignoring the supplier data moved from a
tidiness concern to a licence-compliance requirement.

## Blockers

1. **No images.** The descriptions workbook holds bare filenames, not URLs. Needs
   the *Catalog Images – Download Links* file from the B2B portal. Products should
   not be published until images are attached — hence `draft` status.
2. **Regular/plus split across products.** 67 of 396 products are the plus twin of
   another (`11022` / `11022X`), so the same garment lists twice. Merging is a
   product-structure decision, deliberately left to the owner.
3. **Size range is S–4X**, no XXS or XS exists in the feed. The XXS–3XL brand
   claim in PROJECT.md is not supportable on this supplier.
4. **Manual fulfilment** — no supplier API; every order is re-keyed by email.
