---
plan: 06-03
phase: 06-integrations
subsystem: analytics
tags: [ga4, ecommerce, tracking, influencer]
dependency_graph:
  requires: []
  provides: [ga4-events, ref-capture, influencer-dimension]
  affects: [pdp, cart-drawer, theme-head]
tech_stack:
  added: []
  patterns: [ES modules with named exports, JSON data island, event delegation, leading-comma JSON pattern]
key_files:
  created:
    - assets/ref-capture.js
    - assets/ga4.js
  modified:
    - layout/theme.liquid
    - assets/pdp.js
    - assets/cart-drawer.js
decisions:
  - Use leading-comma pattern for ga4-page-data JSON island to guarantee valid JSON on any page type
  - Store last cart data in module-level _lastCartData in cart-drawer.js to provide accurate begin_checkout payload without extra fetch
  - Event delegation on drawer element for checkout button to survive innerHTML re-renders
  - safeGtag wrapper guards all gtag calls against ad blockers and disabled GA4 setting
  - purchase event intentionally excluded from theme files; documented in ga4.js comment for Shopify Additional Scripts
metrics:
  duration: ~20 min
  completed: 2026-06-17
  tasks_completed: 3
  tasks_total: 3
  files_created: 2
  files_modified: 3
---

# Phase 06 Plan 03: GA4 Enhanced E-Commerce Events + Influencer Code Dimension Summary

## One-liner

GA4 enhanced e-commerce with gtag.js in head, six event types across product/collection/cart flows, and influencer_code custom dimension via shared ref-capture.js utility.

## What Was Built

### Task 1 — ref-capture.js + theme.liquid gtag injection (commit 70cf874)

Created `assets/ref-capture.js` as the single source of truth for the `?ref=` referral param. Runs at ES module evaluation time (before DOMContentLoaded) to capture the param into sessionStorage under key `upromote_ref`. Exports `getInfluencerCode()` which returns the stored value or falls back to `utm_campaign`.

In `layout/theme.liquid`:
- Added `gtag.js` async script + inline `gtag('config', ...)` block, gated on `settings.ga4_measurement_id`
- Added `<script id="ga4-page-data" type="application/json">` data island using the leading-comma pattern — base object is always valid JSON; `product` and `collection` objects are prepended with a comma when present
- Added `data-ga4-id` attribute to `<body>` for measurement ID access from JS
- Added module script loads for `ref-capture.js` and `ga4.js` before `</body>`, gated on GA4 setting

### Task 2 — ga4.js event module (commit 8a5f9b9)

Created `assets/ga4.js` with full enhanced e-commerce event suite:
- `setInfluencerDimension()` — calls `getInfluencerCode()` from ref-capture.js, sets `gtag('set', { influencer_code })` so the dimension propagates on every subsequent hit
- `fireViewItem()` — fires `view_item` on product pages from ga4-page-data island
- `fireViewItemList()` — fires `view_item_list` on collection pages with up to 50 products
- `initSelectItem()` — event delegation on `document` for `[data-product-card]` clicks → `select_item` event; handles AJAX-loaded cards
- Exported `trackAddToCart(cartItem)` — called by pdp.js with /cart/add.js response
- Exported `trackBeginCheckout(cartData)` — called by cart-drawer.js with /cart.js response

All gtag calls wrapped in `safeGtag()` to guard against ad blockers. Purchase event documented in a code comment referencing Shopify Additional Scripts (order status page only).

### Task 3 — pdp.js + cart-drawer.js wiring (commit 94df5cc)

`assets/pdp.js`:
- Added `import { trackAddToCart } from './ga4.js'`
- Calls `trackAddToCart(cartItem)` immediately after the Klaviyo `trackAddedToCart` call on successful cart add

`assets/cart-drawer.js`:
- Added `import { trackBeginCheckout } from './ga4.js'`
- Added module-level `_lastCartData` variable updated on every `renderCart()` call
- Added event delegation listener on the drawer element for `[data-action="checkout"]` and `a[href="/checkout"]` → calls `trackBeginCheckout(_lastCartData)`

## Verification Results

All 8 verification checks passed:
1. `ga4_measurement_id` appears 5 times in theme.liquid (>=2 required)
2. `assets/ref-capture.js` exists
3. `getInfluencerCode` appears 2 times in ref-capture.js (>=1 required)
4. `assets/ga4.js` exists
5. `view_item` appears 6 times in ga4.js (>=1 required)
6. `trackAddToCart` appears 2 times in pdp.js (>=1 required)
7. `trackBeginCheckout` appears 2 times in cart-drawer.js (>=1 required)
8. `ga4-page-data` appears 1 time in theme.liquid (>=1 required)

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written with one minor enhancement:

**[Rule 2 - Missing Critical Functionality] Cart data snapshot for begin_checkout**
- **Found during:** Task 3
- **Issue:** cart-drawer.js has no checkout button click handler and no cached cart state variable — `trackBeginCheckout` needs accurate cart data at the moment of checkout click, but there is no extra fetch budget on a navigation event
- **Fix:** Added module-level `_lastCartData` updated in `renderCart()` on every cart update; added event delegation on drawer for checkout button clicks
- **Files modified:** `assets/cart-drawer.js`
- **Commit:** 94df5cc

## Known Stubs

None — all six required GA4 events are fully implemented. The purchase event is intentionally excluded from theme files and documented for Shopify Additional Scripts configuration.

## Threat Flags

No new security-relevant surface introduced beyond what the plan's threat model covers.

## Self-Check: PASSED

- assets/ref-capture.js: FOUND
- assets/ga4.js: FOUND
- layout/theme.liquid (modified): verified ga4_measurement_id, ga4-page-data, data-ga4-id
- assets/pdp.js (modified): trackAddToCart call confirmed
- assets/cart-drawer.js (modified): trackBeginCheckout import and call confirmed
- Commits: 70cf874, 8a5f9b9, 94df5cc — all present in git log
