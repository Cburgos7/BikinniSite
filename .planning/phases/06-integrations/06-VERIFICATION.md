---
phase: 06-integrations
verified_at: 2026-06-17
status: PASS
---
# Phase 6 Verification

## Phase Goal

Wire all third-party services — Klaviyo flows, UpPromote affiliate tracking, GA4 enhanced e-commerce, and Cloudinary image transforms — and verify end-to-end data flow.

## Success Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| INT-01 Klaviyo | PASS | `assets/klaviyo.js` exists; reads `body.dataset.customerEmail` and calls `window.klaviyo.identify()` for logged-in customers. `assets/klaviyo-flows.js` exists; exports `trackAddedToCart` (fires klaviyo.track 'Added to Cart' with full item payload) and `subscribeBackInStock` (POSTs to Klaviyo client BIS API). `sections/klaviyo-forms.liquid` exists; form ID rendered as `klaviyo-form-{{ section.settings.form_id \| escape }}` — escaped. Klaviyo CDN snippet in `layout/theme.liquid` (lines 36–40) gated on `settings.klaviyo_company_id != blank`; `klaviyo.js` module also gated on same setting (lines 124–126). |
| INT-02 UpPromote | PASS-PENDING-HUMAN | `assets/upromote.js` exists; imports `getInfluencerCode` from `./ref-capture.js`; appends `?discount=CODE` (or `&discount=CODE`) to all `a[href*="/checkout"]` links on DOMContentLoaded; dispatches `upromote:ref-captured` event. UpPromote tracking pixel in `layout/theme.liquid` (lines 88–93) gated on `upromote_merchant_id != blank`. `sections/cart-drawer.liquid` line 136 renders the checkout button with `id="cart-checkout-btn"`; `assets/cart-drawer.js` line 330 listens for `upromote:ref-captured` and patches that button's `href` with the discount code. `06-HUMAN-CHECKPOINT.md` exists with full end-to-end checkout test steps. Code is correctly wired; end-to-end confirmation requires merchant to supply real UpPromote credentials and complete a test checkout per `06-HUMAN-CHECKPOINT.md`. |
| INT-03 GA4 | PASS | `assets/ref-capture.js` exists; exports `getInfluencerCode()` (sessionStorage `upromote_ref` with `utm_campaign` fallback). `assets/ga4.js` exists; imports `getInfluencerCode`; fires `view_item` (line 90), exports `trackAddToCart` for `add_to_cart` (line 170) and `trackBeginCheckout` for `begin_checkout` (line 196). gtag.js snippet in `layout/theme.liquid` (lines 42–86) gated on `ga4_measurement_id != blank`; includes inline `gtag('config', ...)` push and `ga4-page-data` JSON island. GA4 `purchase` event is documented in `06-INTEGRATION-SETTINGS.md` (lines 79–113) with a complete Liquid snippet for Shopify Admin → Checkout → Additional scripts — correctly excluded from theme files per criterion. |
| INT-04 Cloudinary | PASS | `snippets/cloudinary-img.liquid` exists; constructs Cloudinary fetch-URL `https://res.cloudinary.com/{cloud}/image/fetch/f_auto,q_auto,w_{width}/{shopify_url}` when `settings.cloudinary_cloud_name != blank`; falls back to raw Shopify CDN URL when blank (graceful degradation confirmed). Applied in `snippets/product-card.liquid` (line 14, main product image). Applied in `sections/product-main.liquid` (line 11 main image; lines 31 and 53 desktop and mobile thumbnail strips). |
| All IDs are PLACEHOLDER | PASS | `config/settings_data.json` contains only placeholder values: `klaviyo_company_id` = `KLAVIYO_COMPANY_ID_PLACEHOLDER`, `ga4_measurement_id` = `G-XXXXXXXXXX`, `cloudinary_cloud_name` = `CLOUDINARY_CLOUD_NAME_PLACEHOLDER`, `upromote_merchant_id` = `UPROMOTE_MERCHANT_ID_PLACEHOLDER`. No real credentials present. Merchant must supply real values before go-live. |

## Summary

All five success criteria are met. The four integrations are correctly wired in theme files:

- Klaviyo identify and behavioral flows are fully implemented with TCPA-compliant SMS handling delegated to the Klaviyo dashboard.
- UpPromote affiliate discount code flows from `?ref=` URL param through sessionStorage into the cart drawer checkout button href via a custom event handshake between `upromote.js` and `cart-drawer.js`. The `cart-checkout-btn` id required by the criterion is confirmed present in `sections/cart-drawer.liquid`.
- GA4 enhanced e-commerce fires `view_item`, `add_to_cart`, and `begin_checkout` from theme JS; the `purchase` event is documented as an Additional Scripts snippet in `06-INTEGRATION-SETTINGS.md`, which satisfies the criterion that it must not appear in theme files (order status page only).
- Cloudinary image transforms are applied to product card and product detail images with documented graceful fallback.
- All four integration IDs hold placeholder values in `config/settings_data.json`; no real credentials are committed.

INT-02 is marked PASS-PENDING-HUMAN because confirming that a discount code auto-applies on Shopify's hosted checkout page requires a live UpPromote merchant account and a real affiliate code. The theme-side code is correctly implemented. Complete the steps in `06-HUMAN-CHECKPOINT.md` after supplying real credentials to sign off fully.
