---
phase: 04-collections-product-detail
plan: "04"
subsystem: product-detail-page
tags:
  - pdp
  - gallery
  - lightbox
  - variant-selection
  - add-to-cart
  - accordions
dependency_graph:
  requires:
    - 04-01 (cart-drawer.liquid + cart-drawer.js)
  provides:
    - sections/product-main.liquid
    - assets/pdp.js
  affects:
    - assets/cart-drawer.js (cart:updated listener added)
tech_stack:
  added:
    - Native HTML <dialog> API for lightbox
  patterns:
    - ES module with default init() export
    - Shopify Ajax Cart API /cart/add.js POST
    - CustomEvent cart:updated dispatch pattern
    - max-height scrollHeight accordion animation
    - Shopify product.variants | json script tag for JS consumption
key_files:
  created:
    - sections/product-main.liquid
    - assets/pdp.js
  modified:
    - assets/cart-drawer.js
decisions:
  - "Used native <dialog>.showModal() for lightbox — no library, browser handles focus trap and Escape natively (D-11)"
  - "Variant lookup uses title string matching (includes) against size/color values — works for standard Shopify variant title format"
  - "Color swatch background-color set via style attribute using value lowercased with spaces replaced by hyphens — CSS color names must match Shopify color option values"
metrics:
  duration: "~25 minutes"
  completed: "2026-06-14"
  tasks_completed: 2
  files_created: 2
  files_modified: 1
---

# Phase 04 Plan 04: Product Detail Page (Gallery, Variants, Add-to-Cart, Accordions) Summary

**One-liner:** Full PDP Liquid section + JS module: side-by-side gallery with native dialog lightbox, size/color variant selectors, AJAX add-to-cart with cart:updated dispatch, and one-open-at-a-time metafield accordions.

## What Was Built

### sections/product-main.liquid
Complete PDP section using Shopify `product` object directly. Desktop layout: two-column grid (gallery left, info right). Mobile: single-column stack.

- **Gallery:** Main image with `cursor-zoom-in` triggers lightbox; desktop vertical thumbnail strip (right of main); mobile horizontal thumbnail strip (below main). Both use `data-thumbnail` + `data-full-src` attributes consumed by pdp.js.
- **Lightbox:** Native `<dialog id="pdp-lightbox">` with `::backdrop` CSS for dark overlay. Close button + pdp.js handles backdrop click and Escape.
- **Color selector:** Dot swatches with active ring; `data-color-swatch` + `data-color-value` consumed by pdp.js.
- **Size selector:** Bordered radio-style buttons; sold-out sizes rendered with `line-through opacity-40 cursor-not-allowed disabled`; `data-size-swatch` + `data-size-available` consumed by pdp.js.
- **Add-to-cart:** Initially disabled with "Select a Size" text; `data-variant-id` updated by pdp.js on selection; inline error paragraph with `aria-live`.
- **Metafield accordions:** care_instructions, fabric_composition, coverage_level, model_sizing — each only rendered if metafield is populated; `data-accordion` / `data-accordion-trigger` / `data-accordion-body` / `data-accordion-icon` attributes.
- **`<script id="product-variants-json">` tag:** Emits `{{ product.variants | json }}` for pdp.js to parse.
- **XSS:** All merchant string values (title, option values, metafield values, alt text) use `| escape`; `product.description` exempt (Shopify-sanitized rich text).

### assets/pdp.js
ES module following mobile-nav.js pattern (functions at module scope, default `init()` called at bottom).

- **Gallery swap:** `[data-thumbnail]` click sets `#pdp-main-image.src` to `data-full-src`; updates active ring classes.
- **Lightbox:** `[data-lightbox-trigger]` click → `dialog.showModal()`; close button + backdrop click + Escape → `dialog.close()`.
- **Variant state:** Module-level `selectedSize`, `selectedColor`, `selectedVariantId` variables.
- **Color swatches:** Update `selectedColor`, refresh label, update active ring, call `findVariant()` to update `selectedVariantId` and swap gallery image via `variant.featured_image.src`.
- **Size swatches:** Update `selectedSize`, call `findVariant()`, enable/disable add-to-cart button with correct text states.
- **addToCart:** `parseInt` + `isFinite` validation → `fetch('/cart/add.js', { X-Requested-With, JSON body })` → on success dispatch `cart:updated` CustomEvent; button disabled during fetch; re-enabled in `finally`.
- **Accordions:** `[data-accordion]` querySelectorAll; click closes all then opens clicked if it was closed; `scrollHeight` for `max-height`; `rotate(180deg)` on chevron icon.

### assets/cart-drawer.js (modified — Rule 2)
Added `document.addEventListener('cart:updated', ...)` listener inside the DOMContentLoaded block. On event: fetches `/cart.js`, calls `renderCart()`, then `openDrawer()`. Without this, PDP add-to-cart would dispatch `cart:updated` into the void with no visual feedback.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] Added cart:updated listener to cart-drawer.js**
- **Found during:** Task 2 implementation
- **Issue:** Plan specifies pdp.js dispatches `cart:updated` CustomEvent on successful add-to-cart, and states this "wires into the existing cart-drawer.js via the cart:updated event pattern." However, cart-drawer.js contained no listener for this event — the PDP add-to-cart would silently succeed with no cart drawer opening.
- **Fix:** Added `document.addEventListener('cart:updated', ...)` in cart-drawer.js that fetches `/cart.js` and calls `renderCart()` + `openDrawer()`.
- **Files modified:** `assets/cart-drawer.js`
- **Commit:** 6d02f93

## Known Stubs

None — all functionality wires to live Shopify objects and APIs. Color swatch `background-color` uses CSS color name derived from the option value (lowercased, spaces → hyphens); this will only render correctly if the Shopify color option values match valid CSS color names or hex codes. This is a content dependency, not a code stub.

## Threat Flags

No new threat surface beyond what is documented in the plan's threat model. All T-04-04-* mitigations are implemented: parseInt/isFinite validation, `| escape` on all merchant strings, `X-Requested-With` header, button disabled during fetch.

## Self-Check: PASSED

- `sections/product-main.liquid` exists: FOUND
- `assets/pdp.js` exists: FOUND
- Task 1 commit d2fa0b8: FOUND
- Task 2 commit 6d02f93: FOUND
