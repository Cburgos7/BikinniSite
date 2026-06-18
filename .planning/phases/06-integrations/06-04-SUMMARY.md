---
phase: 06-integrations
plan: 06-04
title: UpPromote affiliate tracking + referral capture
subsystem: integrations/affiliate
tags: [upromote, affiliate, referral, tracking, checkout]
requirements: [INT-02]
dependency_graph:
  requires: [06-03]
  provides: [upromote-pixel, referral-discount-wiring]
  affects: [layout/theme.liquid, assets/cart-drawer.js]
tech_stack:
  added: []
  patterns: [ES module custom event communication, sessionStorage referral state]
key_files:
  created:
    - assets/upromote.js
  modified:
    - layout/theme.liquid
    - assets/cart-drawer.js
    - sections/cart-drawer.liquid
decisions:
  - "upromote.js module script included conditionally under a separate upromote_merchant_id gate; ref-capture.js deduplicated via browser ES module caching so no double-load when GA4 is also enabled"
  - "Conditional ref-capture.js tag added under upromote gate to support sites where GA4 is disabled but upromote is enabled"
  - "cart-checkout-btn id added to sections/cart-drawer.liquid checkout anchor to allow targeted href mutation by upromote.js event handler"
metrics:
  duration: "~12 minutes"
  completed_date: "2026-06-17"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 4
---

# Phase 06 Plan 04: UpPromote Affiliate Tracking + Referral Capture Summary

**One-liner:** UpPromote tracking pixel injected in theme head; referral code from `?ref=` piped through `ref-capture.js` shared state into checkout URL discount param via `upromote.js` ES module and `upromote:ref-captured` custom event.

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Inject UpPromote tracking pixel + module scripts in theme.liquid; add cart-checkout-btn id | 6fc0a67 |
| 2 | Create assets/upromote.js; wire upromote:ref-captured listener in cart-drawer.js | 4bc3759 |

## What Was Built

**`assets/upromote.js`** — ES module that:
- Imports `getInfluencerCode()` exclusively from `./ref-capture.js` (no direct URL param reads)
- On `DOMContentLoaded`: reads active referral code, stores as `discount_code` in sessionStorage
- Appends `?discount=CODE` (or `&discount=CODE`) to all `a[href*="/checkout"]` links on the page
- Dispatches `upromote:ref-captured` custom event for cart drawer late-binding

**`layout/theme.liquid`** changes:
- UpPromote CDN tracking pixel (`cdn.upromote.me/js/affiliate.min.js`) injected in `<head>`, gated on `settings.upromote_merchant_id != blank`
- `upromote.js` module script added before `</body>` under same gate
- Conditional `ref-capture.js` tag added under upromote gate for sites without GA4

**`sections/cart-drawer.liquid`** — added `id="cart-checkout-btn"` to checkout anchor for targeted href mutation.

**`assets/cart-drawer.js`** — added `upromote:ref-captured` event listener that appends discount code to `#cart-checkout-btn` href, covering the case where upromote.js fires before or after the drawer renders.

## Verification Results

```
upromote_merchant_id references in theme.liquid : 3  (>= 1) PASS
upromote.js references in theme.liquid          : 1  (>= 1) PASS
getInfluencerCode references in upromote.js     : 3  (>= 1) PASS
upromote:ref-captured refs in cart-drawer.js    : 2  (>= 1) PASS
assets/upromote.js exists                       : YES        PASS
```

## Deviations from Plan

**1. [Rule 2 - Missing feature] Conditional ref-capture.js for upromote-only sites**
- **Found during:** Task 1
- **Issue:** Plan instructs not to add a second `ref-capture.js` tag if GA4 already emits one, but does not address the case where GA4 is disabled and upromote is enabled — upromote.js would fail to import from ref-capture.js if the module was never loaded.
- **Fix:** Added `{%- unless settings.ga4_measurement_id != blank -%}` conditional inside the upromote gate to emit `ref-capture.js` only when GA4 is not emitting it. Browser ES module deduplication handles the overlap case cleanly.
- **Files modified:** `layout/theme.liquid`
- **Commit:** 6fc0a67

**2. [Rule 2 - Missing feature] Added cart-checkout-btn id to liquid anchor**
- **Found during:** Task 1 (pre-requisite for Task 2 event handler)
- **Issue:** Checkout anchor in `sections/cart-drawer.liquid` had no `id`, so the `upromote:ref-captured` handler in cart-drawer.js could not target it via `document.getElementById('cart-checkout-btn')`.
- **Fix:** Added `id="cart-checkout-btn"` to the checkout `<a>` tag.
- **Files modified:** `sections/cart-drawer.liquid`
- **Commit:** 6fc0a67

## Dashboard Configuration Required

The following UpPromote settings must be configured by the merchant in the UpPromote dashboard — no theme code required:

- **Commission tiers:** Standard 10% / Silver 12% / Gold 15%
- **Ambassador program:** configure separately in UpPromote
- **Customer Referral:** 5% commission
- **Fraud Detection — Self-referral block:** enabled in Settings → Fraud Detection
- **IP clustering threshold:** 3 conversions per IP per 24h
- **Conversion hold period:** 14 days

## Known Stubs

None — no placeholder data flows to UI rendering. Merchant ID uses PLACEHOLDER string in settings which gates all pixel and script injection off until a real ID is set.

## Threat Surface Scan

No new network endpoints, auth paths, or schema changes introduced beyond what is documented in the plan threat model (T-06-09 through T-06-11, T-06-SC). The UpPromote CDN script is loaded from `cdn.upromote.me` — a first-party UpPromote domain; the merchant ID is rendered via Liquid server-side and is a non-secret identifier.

## Self-Check

- [x] `assets/upromote.js` exists at correct path
- [x] `layout/theme.liquid` contains `upromote_merchant_id` gate (3 references)
- [x] `assets/cart-drawer.js` contains `upromote:ref-captured` listener
- [x] Commits 6fc0a67 and 4bc3759 exist in git log

## Self-Check: PASSED
