---
phase: 04-collections-product-detail
plan: "01"
subsystem: product-card
tags: [snippet, product-card, swatches, wishlist, quick-add, shopify-liquid]
dependency_graph:
  requires: []
  provides: [snippets/product-card.liquid]
  affects: [sections/featured-products.liquid, sections/new-arrivals.liquid]
tech_stack:
  added: []
  patterns: [shared-snippet, render-tag]
key_files:
  created:
    - snippets/product-card.liquid
  modified:
    - sections/featured-products.liquid
    - sections/new-arrivals.liquid
decisions:
  - "Color swatch deduplication uses seen_colors string with | contains check — no arrays needed in Liquid"
  - "Wishlist uses <a> for guests (return_url param) and <button data-wishlist-toggle> for logged-in customers"
  - "Quick-add slide-up uses translate-y-full / group-hover:translate-y-0 matching existing section pattern"
metrics:
  duration: "15m"
  completed_date: "2026-06-14"
  tasks_completed: 2
  files_changed: 3
---

# Phase 04 Plan 01: Product Card Snippet Summary

**One-liner:** Shared product-card snippet with color swatches, login-gated wishlist toggle, quick-add slide-up, sale/new badges, and full XSS escaping — home page sections migrated to render via snippet.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create snippets/product-card.liquid | 12f5117 | snippets/product-card.liquid |
| 2 | Migrate featured-products and new-arrivals to snippet | c2cbee4 | sections/featured-products.liquid, sections/new-arrivals.liquid |

## What Was Built

`snippets/product-card.liquid` is a self-contained product card receiving a single `product` variable. It renders:

- Portrait 3:4 image with `id="card-img-{{ product.id }}"` for JS swatch swap targeting
- Sale (coral) and New (deep) badges from `compare_at_price` and tags
- Wishlist toggle: `<button data-wishlist-toggle>` for logged-in customers, `<a href="/account/login?return_url=...">` for guests
- Quick-add slide-up form using `first_available_variant`; "Sold Out" span when none available
- Color swatch dots — unique colors extracted via `seen_colors` string deduplication
- Card body with escaped title and price + compare-at strikethrough

Both `sections/featured-products.liquid` and `sections/new-arrivals.liquid` had their inline `<article>` card markup replaced with `{%- render 'product-card', product: product -%}`. Grid wrappers, headings, schema blocks, and the new-arrivals "View All" link are unchanged.

## Threat Mitigations Applied

| Threat | Mitigation |
|--------|-----------|
| T-04-01-01 Tampering via product.title | `| escape` applied to product.title, option names (aria-label), and swatch aria-labels |
| T-04-01-02 Wishlist info disclosure | `customer != blank` gates the `data-wishlist-toggle` button; guests get login link only |
| T-04-01-03 Quick-add variant ID | Accepted — variant ID is server-side rendered from Shopify product object |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — snippet renders live product data from Shopify object. Swatch JS wiring (`data-card-id` image swap) deferred to Plan 02 per plan spec.

## Self-Check: PASSED

- snippets/product-card.liquid: FOUND
- sections/featured-products.liquid: FOUND (contains render 'product-card', no inline article)
- sections/new-arrivals.liquid: FOUND (contains render 'product-card', no inline article)
- Commit 12f5117: FOUND
- Commit c2cbee4: FOUND
