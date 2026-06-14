---
phase: 04-collections-product-detail
review_depth: standard
reviewed_at: 2026-06-14
files_reviewed: 8
status: PASS
---

# Phase 4 Code Review

## Summary

All 8 Phase 4 files were reviewed at standard depth. Four critical findings were identified; three were fixed immediately (CR-04-02, CR-04-03, CR-04-04 — committed as `e29f416`). CR-04-01 (`product.description` raw output) is accepted as a documented trust boundary — Shopify sanitizes rich text descriptions server-side and stripping HTML would break merchant-authored formatting. Five warnings and three info findings remain as non-blocking notes.

## Findings

### Critical

**CR-04-01** — `sections/product-main.liquid:69`
**Issue:** `{{ product.description }}` outputs raw HTML without `| escape`.
**Disposition:** ACCEPTED — Shopify processes product descriptions through its rich text editor and sanitizes all output before storing. Raw output is required to preserve bold, links, and paragraph formatting that merchants use. Stripping HTML (`| strip_html | escape`) would degrade UX. This is an explicit merchant trust boundary: if the merchant account is compromised, description XSS is possible, but that is the same risk as a compromised theme file.
**Fix applied:** None — documented as accepted trust boundary.

**CR-04-02** — `assets/cart-drawer.js` (declaration order)
**Issue:** `escapeHtml` declared after `buildItemHTML` which references it.
**Note:** Safe at runtime (function called post-DOMContentLoaded, after all const declarations initialize), but declaration order was a false-positive risk and bad practice.
**Fix applied:** `escapeHtml` moved above `buildItemHTML`. Commit `e29f416`.

**CR-04-03** — `assets/cart-drawer.js:156` (`updateQuantity`)
**Issue:** `/cart/change.js` POST missing `X-Requested-With: XMLHttpRequest` header. Inconsistent with project CSRF convention applied to all other Ajax Cart API calls.
**Fix applied:** Header added to `updateQuantity` fetch. Commit `e29f416`.

**CR-04-04** — `assets/pdp.js:28-33` (`findVariant`)
**Issue:** Variant lookup used `v.title.toLowerCase().includes(size/color)` — partial string matching causes wrong variant on multi-option products (e.g., color "Red" matches "ExtraRed"; selecting size before color could add wrong variant to cart).
**Fix applied:** Replaced with `v.options.some((o) => o === size/color)` exact equality matching against the Shopify variant options array. Commit `e29f416`.

### Warning

**CW-04-01** — `assets/collection-filter.js` (`fetchFilteredGrid`)
**Issue:** On fetch error, the product grid silently shows stale content. No user-visible error state.
**Recommendation:** Add a visible error banner on failed filter fetches ("Couldn't load products — please try again.").

**CW-04-02** — `assets/pdp.js` (`initSizeSwatches`)
**Issue:** `selectedSize + ' is sold out'` writes the size value to `unavailableMsg.textContent`. Safe (textContent, not innerHTML), and value is server-rendered via `| escape`. Noted for completeness.

**CW-04-03** — `snippets/product-card.liquid` (color swatch background-color)
**Issue:** `style="background-color: {{ value | downcase | replace: ' ', '-' }}"` — produces CSS identifiers from option names, not CSS color values. "Navy Blue" → `background-color: navy-blue` (invalid CSS color).
**Recommendation:** Document in merchant onboarding that Color option values must be valid CSS color keywords or hex codes.

**CW-04-04** — `assets/cart-drawer.js` (`bindCartItemEvents`)
**Issue:** Node replacement strategy (`cloneNode + replaceChild`) to remove stale listeners is unconventional. Safe for current markup but brittle if DOM structure inside `#cart-items` changes.

**CW-04-05** — `sections/product-main.liquid` (variant JSON)
**Issue:** `{{ product.variants | json }}` exposes full variant data (including inventory quantities) publicly on the PDP. Accepted as standard Shopify practice.

### Info

**CI-04-01** — `assets/pdp.js` (`findVariant` post-fix)
**Issue:** If two options share the same value (e.g., a color named the same as a size), `opts.some()` will match ambiguously. Extremely unlikely with this catalog.

**CI-04-02** — `sections/collection-grid.liquid` (price range inputs)
**Issue:** Price range inputs have no `min="0"` attribute. Shopify ignores invalid ranges gracefully, but defensive HTML validation would be an improvement.

**CI-04-03** — `assets/collection-filter.js` (`buildActiveChips`)
**Issue:** Price filter chip labels display raw cent values from URL params (e.g., "500" instead of "$5.00"). A price formatter would improve readability.

## File Notes

| File | Status | Notes |
|------|--------|-------|
| `snippets/product-card.liquid` | Pass | All outputs escaped; wishlist auth gate present; quick-add, swatches, badges correct. CW-04-03. |
| `sections/collection-grid.liquid` | Pass | Filter sidebar + drawer correct; AJAX section swap correct. CI-04-02. |
| `sections/featured-products.liquid` | Pass | Migrated to snippet render; schema intact. |
| `sections/new-arrivals.liquid` | Pass | Migrated to snippet render; schema intact. |
| `sections/product-main.liquid` | Pass | CR-04-01 accepted; all other outputs escaped; variant JSON safe. |
| `assets/collection-filter.js` | Pass | escapeHtml on all innerHTML writes; CSS.escape for querySelector; pushState correct. CW-04-01. |
| `assets/pdp.js` | Pass (fixed) | CR-04-04 fixed; CSRF header present; integer validation; double-submit guard. |
| `assets/cart-drawer.js` | Pass (fixed) | CR-04-02 fixed; CR-04-03 fixed; cart:updated listener correct. |
