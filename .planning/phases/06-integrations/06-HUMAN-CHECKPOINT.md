# Phase 06 — Integration Human Verification Checklist

Complete these steps after replacing all `PLACEHOLDER` values in `config/settings_data.json`
with real credentials. Run `shopify theme dev` and open the preview URL in a browser with
DevTools available.

Run `grep -r "PLACEHOLDER" config/settings_data.json` first — it should return no results
before proceeding.

---

## INT-01 — Klaviyo

- [ ] Set `klaviyo_company_id` in Shopify theme settings (Customize → Theme settings → Integrations)
- [ ] Add a `klaviyo-forms` section to a page template and enter your Klaviyo form ID
- [ ] Open that page in a browser — confirm the Klaviyo signup form renders correctly
- [ ] Confirm the SMS opt-in checkbox is present and is NOT pre-checked by default
- [ ] DevTools → Network → filter "klaviyo" — confirm `klaviyo.js?company_id=YOUR_ID` loads in `<head>`
- [ ] Add a product to cart — open DevTools Console and confirm a `klaviyo.track` call fires with event name `'Added to Cart'`
- [ ] (Alternative) In Klaviyo → Analytics → Metrics, confirm the "Added to Cart" metric receives an event within 5 minutes of the add-to-cart action
- [ ] Navigate to `/account` while logged in as a test customer — run `window.klaviyo?.identify` in Console, confirm no error is thrown
- [ ] On an out-of-stock product variant, confirm the `data-bis-variant` attribute is present on the back-in-stock subscription form

---

## INT-03 — GA4

- [ ] Set `ga4_measurement_id` in theme settings (format: `G-XXXXXXXXXX`)
- [ ] DevTools → Network → filter "gtag" — confirm `gtag.js?id=G-XXXXXXXXXX` script loads in `<head>`
- [ ] In Console, run `window.dataLayer` — confirm it is an array with at least one config push entry
- [ ] Open a product page — confirm `gtag('event', 'view_item', ...)` call fires (check Console or dataLayer)
- [ ] Add a product to cart — run `window.dataLayer` in Console — confirm an `add_to_cart` event entry is present
- [ ] Open the cart drawer and click Checkout — confirm `begin_checkout` event appears in `window.dataLayer`
- [ ] Navigate to a collection page — confirm `view_item_list` event appears in `window.dataLayer`
- [ ] Paste the GA4 purchase snippet (from `06-INTEGRATION-SETTINGS.md`) into Shopify Admin → Settings → Checkout → Additional scripts
- [ ] Complete a test order using the Bogus Gateway — confirm the `purchase` event appears in GA4 Real-Time reports within 60 seconds

---

## INT-02 — UpPromote

- [ ] Set `upromote_merchant_id` in theme settings
- [ ] In a new browser tab, visit `/?ref=TESTCODE` (replace TESTCODE with a real affiliate code from UpPromote dashboard)
- [ ] DevTools → Application → Storage → Session Storage → confirm `upromote_ref` = `TESTCODE`
- [ ] Add any product to the cart
- [ ] Open the cart drawer — inspect the Checkout button's `href` in DevTools Elements — confirm it contains `?discount=TESTCODE` or `&discount=TESTCODE`
- [ ] Click Checkout — on the Shopify-hosted checkout page, confirm the discount code `TESTCODE` appears in the order summary (even if the code is invalid, Shopify should acknowledge it was passed)
- [ ] Obtain a real UpPromote test discount code from the UpPromote dashboard (Affiliates → select test affiliate → copy referral/discount code)
- [ ] Repeat the flow with the real discount code — confirm it auto-applies on the checkout page with a monetary discount line item
- [ ] Complete a Bogus Gateway test order — confirm the completed order appears in UpPromote dashboard with affiliate attribution

---

## INT-04 — Cloudinary

- [ ] Set `cloudinary_cloud_name` in theme settings
- [ ] Allowlist your Shopify CDN domain in Cloudinary → Settings → Security → Allowed fetch domains (add `cdn.shopify.com`)
- [ ] Open any collection page — right-click a product card image → Copy image address
- [ ] Confirm the URL contains `res.cloudinary.com/{your-cloud-name}/image/fetch/f_auto,q_auto`
- [ ] DevTools → Network tab — confirm the Cloudinary image request returns HTTP 200 (not 404)
- [ ] Temporarily clear the `cloudinary_cloud_name` setting and reload — confirm product card images still load (via Shopify CDN), confirming graceful degradation
- [ ] Restore `cloudinary_cloud_name` setting

---

## Sign-off

Once all checkboxes above are checked, the Phase 06 integrations are verified for go-live.

Record the date and verifier name here:

**Verified by:** ___________________________
**Date:** ___________________________
**Theme version / commit:** ___________________________
