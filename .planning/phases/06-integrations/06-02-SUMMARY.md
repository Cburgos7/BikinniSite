---
phase: 06-integrations
plan: 06-02
title: Klaviyo abandoned cart, back-in-stock, and email flow wiring
subsystem: integrations
tags: [klaviyo, tracking, back-in-stock, abandoned-cart]
requirements: [INT-01]
dependency_graph:
  requires: [06-01]
  provides: [klaviyo-flows, bis-form]
  affects: [pdp, cart]
tech_stack:
  added: []
  patterns: [ES module side-effect import, Klaviyo client API v2023-12-15, data-attribute-driven form wiring]
key_files:
  created:
    - assets/klaviyo-flows.js
  modified:
    - assets/pdp.js
    - sections/product-main.liquid
    - layout/theme.liquid
decisions:
  - "BIS forms rendered server-side for all OOS variants; JS shows/hides based on size selection to avoid re-renders"
  - "klaviyo-flows.js is standalone (no import from klaviyo.js) to keep coupling low; accesses window.klaviyo directly"
  - "Company ID passed via data-klaviyo-company-id on <body> — public identifier, not secret key (T-06-04 accept)"
metrics:
  duration: ~15m
  completed: 2026-06-17
  tasks_completed: 2
  tasks_total: 2
  files_changed: 4
---

# Phase 06 Plan 02: Klaviyo Abandoned Cart and Back-in-Stock Wiring Summary

**One-liner:** Standalone `klaviyo-flows.js` module wires Klaviyo "Added to Cart" tracking and client-API back-in-stock subscriptions into the existing PDP JS without coupling to the base klaviyo.js module.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Create assets/klaviyo-flows.js — track helpers | 64db74c | assets/klaviyo-flows.js |
| 2 | Wire pdp.js + add BIS form to PDP section | 64db74c | assets/pdp.js, sections/product-main.liquid, layout/theme.liquid |

## What Was Built

**`assets/klaviyo-flows.js`**
- `trackAddedToCart(cartItem)` — maps Shopify `/cart/add.js` response to Klaviyo "Added to Cart" event properties (ProductName, ProductID, SKU, Categories, ImageURL, URL, Brand, Price, CompareAtPrice, Quantity). Price converted from Shopify cents to dollars.
- `subscribeBackInStock(email, variantId)` — POSTs to `https://a.klaviyo.com/client/back-in-stock-subscriptions/` with Klaviyo API revision `2023-12-15`. Reads company ID from `document.body.dataset.klaviyoCompanyId`. Basic email validation before POST (T-06-05 mitigate).
- `initBackInStockForms()` — wires submit listeners on all `[data-bis-form]` elements at DOMContentLoaded, shows inline success/error messaging via `[data-bis-msg]`.

**`assets/pdp.js`**
- Imports `trackAddedToCart` from `./klaviyo-flows.js`.
- Calls `trackAddedToCart(cartItem)` after successful `/cart/add.js` response (was previously discarding the parsed JSON).
- Shows/hides BIS forms in size swatch selection: reveals `#bis-{variantId}` when a sold-out variant is selected, hides all BIS forms when an available variant is selected.

**`sections/product-main.liquid`**
- Loops `product.variants`, renders a `[data-bis-form][data-bis-variant]` form for each unavailable variant (hidden by default, shown by JS).
- Each form contains an email input `[data-bis-email]`, submit button `[data-bis-submit]`, and feedback paragraph `[data-bis-msg]`.
- Loads `klaviyo-flows.js` as a `type="module"` script.

**`layout/theme.liquid`**
- Added `data-klaviyo-company-id="{{ settings.klaviyo_company_id | escape }}"` to `<body>` for BIS API auth.

## Deviations from Plan

### Auto-added functionality (Rule 2)

**1. [Rule 2 - Missing functionality] BIS form show/hide wired in pdp.js size selection**
- The plan specified the BIS form should render for OOS variants but did not specify the show/hide trigger.
- Added JS in `initSizeSwatches` to reveal the correct BIS form when a sold-out size is selected and hide all BIS forms when an available size is selected. Without this the forms would always be hidden (initial `class="hidden"` in template).
- Files modified: assets/pdp.js
- Commit: 64db74c

**2. [Rule 2 - Missing functionality] Added data-klaviyo-company-id to layout/theme.liquid**
- Plan specified the BIS function reads `document.body.dataset.klaviyoCompanyId` but did not call out the Liquid change required to emit that attribute.
- Added the data attribute output to `<body>` in theme.liquid. Without this the BIS API call would silently skip with a console warning.
- Files modified: layout/theme.liquid
- Commit: 64db74c

## Verification

All four plan verification checks pass:

| Check | Result |
|-------|--------|
| `test -f assets/klaviyo-flows.js` | FOUND |
| `grep -c "trackAddedToCart" assets/pdp.js` | 2 |
| `grep -c "data-bis-variant" sections/product-main.liquid` | 2 |
| `grep -c "subscribeBackInStock" assets/klaviyo-flows.js` | 3 |

## Known Stubs

None. The klaviyo company ID is read from `settings.klaviyo_company_id` (owner-provided Shopify setting) — not hardcoded. All API endpoints are real Klaviyo production URLs.

## Threat Flags

No new security surface beyond what is documented in the plan's threat model. Company ID on `<body>` is a public identifier (T-06-04 accept). Email input validated client-side before POST; Klaviyo validates server-side (T-06-05 mitigate).

## Self-Check: PASSED

- `assets/klaviyo-flows.js` exists
- `assets/pdp.js` contains `trackAddedToCart` import and call
- `sections/product-main.liquid` contains `data-bis-variant`
- `layout/theme.liquid` contains `data-klaviyo-company-id`
- Commit 64db74c exists on main
