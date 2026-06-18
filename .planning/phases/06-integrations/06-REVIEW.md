---
phase: 06-integrations
review_depth: standard
reviewed_at: 2026-06-17
files_reviewed: 10
files_reviewed_list:
  - assets/ref-capture.js
  - assets/klaviyo.js
  - assets/klaviyo-flows.js
  - assets/ga4.js
  - assets/upromote.js
  - snippets/cloudinary-img.liquid
  - sections/klaviyo-forms.liquid
  - layout/theme.liquid
  - assets/pdp.js
  - assets/cart-drawer.js
findings:
  critical: 2
  warning: 5
  info: 2
  total: 9
status: PASS
---

# Phase 6: Code Review

**Reviewed:** 2026-06-17
**Depth:** standard
**Files Reviewed:** 10
**Status:** PASS — 2 Criticals + 5 Warnings fixed in commit `b76adcb`; 2 Info non-blocking.

---

## Summary

Ten Phase 6 source files were reviewed: five JavaScript ES modules (ref-capture, klaviyo, klaviyo-flows, ga4, upromote), two Liquid files (cloudinary-img snippet, klaviyo-forms section), theme.liquid (script-injection blocks), and two modified JS files (pdp.js, cart-drawer.js). The integration architecture is sound — ref-capture.js is correctly the single URLSearchParams reader, ga4.js and upromote.js import from it without re-reading location.search, and all API IDs flow from theme settings rather than being hardcoded.

Two Critical XSS vulnerabilities exist: unescaped variant_title HTML injection in the cart drawer's innerHTML builder, and an unescaped form_id in the Klaviyo forms section that is rendered into a CSS class attribute. Both involve merchant- or Shopify-supplied strings entering the DOM via innerHTML or unescaped attribute output.

---

## Critical Issues

### CR-01: `item.variant_title` injected into innerHTML without escaping

**File:** `assets/cart-drawer.js:59-69`

**Issue:** `buildItemHTML` constructs an HTML string that inserts `variant_title` into a `<p>` tag via a template literal. The `escapeHtml` helper is present in the file and applied to `item.title` elsewhere, but `variantTitle` is built with raw interpolation:

```js
const variantTitle =
  item.variant_title && item.variant_title !== 'Default Title'
    ? `<p class="text-mid text-xs mt-0.5">${item.variant_title}</p>`  // NOT escaped
    : '';
```

`variant_title` is a Shopify-supplied string that a merchant constructs from option values (e.g. "Red / XL"). A store owner naming a variant option value `<img src=x onerror=alert(1)>` would execute arbitrary JavaScript in every buyer's browser when the cart drawer renders. This is a stored-XSS vector.

**Fix:**
```js
const variantTitle =
  item.variant_title && item.variant_title !== 'Default Title'
    ? `<p class="text-mid text-xs mt-0.5">${escapeHtml(item.variant_title)}</p>`
    : '';
```

---

### CR-02: Unescaped `form_id` written into HTML attribute in `klaviyo-forms.liquid`

**File:** `sections/klaviyo-forms.liquid:17`

**Issue:** The Klaviyo form ID from theme settings is interpolated directly into a CSS class without the `| escape` filter:

```liquid
<div class="klaviyo-form-{{ section.settings.form_id }}"></div>
```

A merchant (or a compromised Shopify account) setting `form_id` to `x"><script>evil()</script><div class="` would break out of the attribute and inject executable HTML. Theme settings are merchant-controlled input and must be escaped on output.

**Fix:**
```liquid
<div class="klaviyo-form-{{ section.settings.form_id | escape }}"></div>
```

---

## Warnings

### WR-01: `settings.upromote_merchant_id` output unescaped into HTML attribute

**File:** `layout/theme.liquid:91`

**Issue:** The UpPromote merchant ID is written into a `data-merchant-id` attribute without `| escape`:

```liquid
data-merchant-id="{{ settings.upromote_merchant_id }}">
```

A value containing `"` would break out of the attribute. Compare to `data-klaviyo-company-id` on `<body>` (line 100) which correctly uses `| escape`.

**Fix:**
```liquid
data-merchant-id="{{ settings.upromote_merchant_id | escape }}">
```

---

### WR-02: `settings.cloudinary_cloud_name` unescaped in URL construction; `class` attribute unescaped

**File:** `snippets/cloudinary-img.liquid:27-32, 41`

**Issue (a):** `settings.cloudinary_cloud_name` is appended directly into a URL string without `| url_encode` or `| escape`. A cloud name containing `/` or `?` would corrupt the Cloudinary fetch URL path (e.g. shifting transforms after the path component). While Cloudinary cloud names are restricted to lowercase alphanumeric + hyphens, the theme should not rely on that external constraint.

**Issue (b):** The `class` parameter is output without escaping at line 41:
```liquid
{%- if class != blank %} class="{{ class }}"{% endif %}
```
`class` is a snippet parameter supplied by callers in Liquid. If a caller passes a value with `"`, it breaks the attribute.

**Fix (a):**
```liquid
{%- assign src = 'https://res.cloudinary.com/'
  | append: settings.cloudinary_cloud_name
  ...
```
Add `| url_encode` to `settings.cloudinary_cloud_name` before appending, or add `| escape` as a minimum guard.

**Fix (b):**
```liquid
{%- if class != blank %} class="{{ class | escape }}"{% endif %}
```

---

### WR-03: `item.image` URL inserted into `src` attribute without validation

**File:** `assets/cart-drawer.js:58, 66`

**Issue:** `item.image` from Shopify's `/cart.js` response is placed verbatim into the `src` attribute of an `<img>` tag built via innerHTML:

```js
const imgSrc = item.image || '';
// ...
<img src="${imgSrc}" alt="${escapeHtml(item.title)}" ...>
```

`item.image` is Shopify-provided so `javascript:` URIs are not a realistic Shopify-origin concern, but the value is unescaped — a `"` in the URL (theoretically possible in a relative path) breaks out of the attribute and can inject additional attributes. At minimum it should be escaped.

**Fix:**
```js
const imgSrc = item.image ? escapeHtml(item.image) : '';
```

---

### WR-04: Weak email validation before Klaviyo BIS API call

**File:** `assets/klaviyo-flows.js:121`

**Issue:** Email validation is `!email.includes('@')`. Strings like `a@`, `@`, or `@@` pass this check and are sent to the Klaviyo API. Klaviyo will reject them server-side, but users receive a confusing generic error rather than the "valid email" message shown for locally-detected invalids. The check also passes clearly malformed inputs to the network, which is unnecessary.

**Fix:** Use a minimal but meaningful regex:
```js
const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!email || !emailRe.test(email)) {
```

---

### WR-05: `variantsData` JSON.parse runs at module top-level with no DOM-ready guard

**File:** `assets/pdp.js:20-22`

**Issue:** `variantsData` is parsed at module evaluation time before DOMContentLoaded:
```js
const variantsData = JSON.parse(
  document.getElementById('product-variants-json')?.textContent || '[]'
);
```
If the script tag is loaded in `<head>` (or via a future loader change), `getElementById` returns `null` and the optional-chain falls through to `'[]'` silently — all variant lookups return `undefined` and add-to-cart silently fails. The fallback hides the failure entirely; there is no warning.

**Fix:** Move the parse inside `init()` / `DOMContentLoaded`, or add an explicit warning:
```js
const variantsData = (() => {
  const el = document.getElementById('product-variants-json');
  if (!el) { console.warn('[pdp] product-variants-json not found'); return []; }
  try { return JSON.parse(el.textContent); }
  catch (e) { console.warn('[pdp] invalid product-variants-json', e); return []; }
})();
```

---

## Info

### IN-01: Shadowed `variant` variable in `initSizeSwatches` — dead code

**File:** `assets/pdp.js:207-215`

**Issue:** Inside the `else` (sold-out) branch where `variant` is already known to be falsy or unavailable, there is a second `const variant = findVariant(selectedSize, selectedColor)` declaration that shadows the outer `variant`. This second call returns the same value (falsy or unavailable), so the `if (variant)` block at line 208 never executes. The BIS form show logic inside it is dead code.

```js
// outer branch
} else {
  selectedVariantId = null;
  // ...
  // Redundant second call — 'variant' is already in scope and already falsy/unavailable
  const variant = findVariant(selectedSize, selectedColor);  // line 207
  if (variant) {  // always false if we got here via unavailable path
    ...
  }
}
```

**Fix:** Remove the second `findVariant` call. Use the outer `variant` variable and check `!variant.available` specifically:
```js
if (variant) {
  // Show BIS form for this (unavailable) variant
  document.querySelectorAll('[data-bis-variant]').forEach((el) => el.classList.add('hidden'));
  const bisEl = document.getElementById(`bis-${variant.id}`);
  if (bisEl) bisEl.classList.remove('hidden');
}
```

---

### IN-02: `ref-capture.js` stores raw URL param to sessionStorage without length guard

**File:** `assets/ref-capture.js:17-20`

**Issue:** The `?ref=` value is written to sessionStorage without any length limit or character validation. An attacker crafting a link like `?ref=<64KB string>` could saturate sessionStorage (total ~5MB across origins), potentially causing `setItem` to throw a `QuotaExceededError` that is silently uncaught. This is not a security vulnerability but a robustness gap.

**Fix:**
```js
const _ref = new URLSearchParams(location.search).get('ref') || '';
if (_ref && _ref.length <= 200) {
  try {
    sessionStorage.setItem('upromote_ref', _ref);
  } catch (_) {
    // sessionStorage full — silently skip
  }
}
```

---

## File Notes

| File | Result | Notes |
|---|---|---|
| `assets/ref-capture.js` | WARNING | IN-02 (no length guard on sessionStorage write) |
| `assets/klaviyo.js` | PASS | Clean. Async Klaviyo retry pattern is correct. |
| `assets/klaviyo-flows.js` | WARNING | WR-04 (weak email regex before BIS API call) |
| `assets/ga4.js` | PASS | Correctly imports from ref-capture.js; no direct URLSearchParams reads. |
| `assets/upromote.js` | PASS | Correctly imports from ref-capture.js; applyDiscountToHref logic is sound. |
| `snippets/cloudinary-img.liquid` | WARNING | WR-02 (unescaped cloudinary_cloud_name in URL; unescaped class param) |
| `sections/klaviyo-forms.liquid` | CRITICAL | CR-02 (unescaped form_id in class attribute) |
| `layout/theme.liquid` | WARNING | WR-01 (unescaped upromote_merchant_id in data attribute) |
| `assets/pdp.js` | WARNING + INFO | WR-05 (top-level JSON.parse); IN-01 (dead code / shadowed variable) |
| `assets/cart-drawer.js` | CRITICAL + WARNING | CR-01 (variant_title XSS via innerHTML); WR-03 (item.image unescaped in src) |

---

_Reviewed: 2026-06-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
