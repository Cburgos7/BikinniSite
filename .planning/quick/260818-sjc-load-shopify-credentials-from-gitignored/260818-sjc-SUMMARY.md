---
id: 260818-sjc
status: complete
date: 2026-08-19
commits: 84d1615
---

# Quick Task 260818-sjc — Summary

Wired credential loading and fixed three defects the **first live run against the
Shopify Admin API** exposed. Follows [260818-s63](../260818-s63-prepare-elegant-moments-images-and-build/).

## Live verification

One product (`em-2472`) was created in `velvet-tide-2.myshopify.com`, inspected,
and deleted. Confirmed working end to end:

- Client-credentials token minting
- Product creation: title, vendor, product type, tags, description HTML
- Variants: SKU, price `$7.95`, barcode, weight 34 g
- **Image upload** — both JPEGs on Shopify's CDN at 1200×1800 with attribution alt

Scope probe results: `products` OK, `files` OK, `publications` OK, `shop` OK,
**`locations` DENIED**.

Note: the earlier concern that `write_files` might be missing was wrong — file
access is already granted, so image upload needed no scope change.

## Fixes

**1. Credentials from `.env`.** Loaded from a gitignored file beside the script so
the client secret never enters a shell history or a transcript. Real environment
variables take precedence. `--env` overrides the path.

The user's file had values pasted with no `=` separator
(`SHOPIFY_CLIENT_ID<value>`); repaired in place rather than asking them to redo it.

**2. Degrade without `read_locations`.** Setting stock needs a location ID. Rather
than abort, products are created without quantities and the gap is reported — a
draft with no stock is recoverable, a failed run is lost work. Added
`--inventory-only` to backfill quantities onto existing products via
`inventorySetQuantities`, matching variants by SKU, once the scope is granted.

**3. Front image first.** The workbook's `Image 1` column holds the *back* shot for
8 styles, which would have made a back view the collection-tile thumbnail. Ordering
now follows the reliable `_f`/`_b` filename convention. 313 of 317 products lead
with a front view; the remaining 4 have no front image in the supplier ZIP.

## Next

Owner is adding `read_locations` + `write_inventory`, then the full 330-product
push runs in a single pass with accurate stock.
