---
phase: 02-global-shell
reviewed: 2026-06-11T00:00:00Z
depth: standard
files_reviewed: 17
files_reviewed_list:
  - assets/cart-drawer.js
  - assets/cookie-consent.js
  - assets/inline-search.js
  - assets/mobile-nav.js
  - layout/theme.liquid
  - sections/announcement-bar.liquid
  - sections/cart-drawer.liquid
  - sections/cookie-consent.liquid
  - sections/footer.liquid
  - sections/header.liquid
  - sections/not-found.liquid
  - templates/404.json
  - templates/customers/account.liquid
  - templates/customers/addresses.liquid
  - templates/customers/login.liquid
  - templates/customers/order.liquid
  - templates/customers/register.liquid
findings:
  critical: 5
  warning: 7
  info: 4
  total: 16
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-06-11T00:00:00Z
**Depth:** standard
**Files Reviewed:** 17
**Status:** issues_found

## Summary

Reviewed the complete global shell implementation for Phase 02 — layout, header/footer, cart drawer, mobile nav, inline search, cookie consent, 404, and customer account templates. The implementation is broadly functional but carries five critical defects: two XSS injection paths in the cart drawer's JS renderer, a double-init pattern that fires every module twice, a threshold data mismatch between the section that owns the setting and the element the JS reads from, and an unescaped output in the announcement bar. Seven warnings cover logic bugs, a checkout URL construction error, a missing ARIA state, and several reliability gaps. Four informational items cover dead code and minor quality issues.

---

## Critical Issues

### CR-01: XSS — `item.variant_title` injected unescaped into innerHTML

**File:** `assets/cart-drawer.js:45-46`
**Issue:** `buildItemHTML` inserts `item.variant_title` directly into the HTML string without escaping. An attacker who can control product variant title content (possible via wholesale/partner integrations or a compromised Shopify partner account) can inject arbitrary HTML/script into every visitor's cart drawer. `item.title` is correctly escaped via `escapeHtml()` on lines 53 and 76, but `item.variant_title` is not.
**Fix:**
```js
const variantTitle =
  item.variant_title && item.variant_title !== 'Default Title'
    ? `<p class="text-mid text-xs mt-0.5">${escapeHtml(item.variant_title)}</p>`
    : '';
```

---

### CR-02: XSS — `item.image` URL injected unescaped into `src`

**File:** `assets/cart-drawer.js:42,51`
**Issue:** `imgSrc = item.image || ''` is placed directly into the `src` attribute of an `<img>` tag inside a template literal on line 51. A value such as `" onerror="alert(1)` or a `javascript:` URI would execute. The Shopify cart API returns image URLs from Shopify's CDN under normal operation, but the value is never sanitised before injection. All other user-visible strings use `escapeHtml()`; this one does not.
**Fix:**
```js
const imgSrc = escapeHtml(item.image || '');
// then in the template:
<img src="${imgSrc}" ...>
```

---

### CR-03: Double initialisation — every module calls `init()` twice

**File:** `assets/cart-drawer.js:97-303`, `assets/cookie-consent.js:13-48`, `assets/inline-search.js:24-54`, `assets/mobile-nav.js:54-78`
**Issue:** Each file both `export default function init()` and then immediately calls `init()` at module scope (e.g. `cart-drawer.js` line 303, `cookie-consent.js` line 48, `inline-search.js` line 54, `mobile-nav.js` line 78). Because all four scripts are loaded as `type="module"` via Shopify's asset pipeline, the module is evaluated once, which means `init()` runs once at import time and then — if an external caller ever invokes the export — a second time. More concretely, the self-call at module scope registers a `DOMContentLoaded` listener unconditionally. If the document is already loaded when the module evaluates (e.g. deferred execution), `DOMContentLoaded` may never fire and the feature silently fails. Replacing the bare call with a `readyState` guard is the correct fix. The double-call pattern also means any future consumer who calls the export will bind duplicate event listeners.
**Fix:** Replace the bare `init()` call at the bottom of each file with:
```js
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
```
And remove the inner `document.addEventListener('DOMContentLoaded', ...)` wrapper inside `init()` itself, since the guard above already handles timing.

---

### CR-04: Free-shipping threshold mismatch — JS reads from wrong element

**File:** `assets/cart-drawer.js:114-117` vs `sections/cart-drawer.liquid:34`
**Issue:** The JS reads `data-threshold` from `document.querySelector('[data-threshold]')`. That attribute is set on the `<div class="px-6 py-3 bg-sand">` wrapper inside the cart drawer panel. However, `sections/header.liquid` also defines a `free_shipping_threshold` schema setting (line 169) that is never rendered into any DOM attribute — it is completely disconnected. The announcement bar (`sections/announcement-bar.liquid`) uses its own separate schema setting. This means three separate places store the threshold value with no single source of truth. If a merchant sets a different value in the Header section than in the Cart Drawer section (which is the only one that actually emits `data-threshold`), the announcement bar text and the cart bar will disagree. Additionally, the `header.liquid` setting is dead — it is defined but never referenced in the template output.
**Fix:** Remove the `free_shipping_threshold` setting from `sections/header.liquid` entirely. Ensure the announcement bar reads its threshold from `sections/announcement-bar.liquid`'s own setting (it currently does). Document that the Cart Drawer section setting is the canonical source for the JS progress bar. Consider using a global theme setting instead of per-section duplication.

---

### CR-05: Unescaped output in announcement bar — stored XSS risk

**File:** `sections/announcement-bar.liquid:3`
**Issue:** `{{ section.settings.text }}` is rendered without the `| escape` filter. A merchant (or anyone with theme editor access) who enters malicious content in the "Announcement text" field will have it injected raw into the page for all visitors. Shopify's admin does not sanitise rich-text or plain-text setting values before storing them. The `| escape` filter should be applied to all merchant-controlled text that is rendered as HTML content.
**Fix:**
```liquid
{{ section.settings.text | escape }}
```

---

## Warnings

### WR-01: Checkout URL construction is non-standard

**File:** `sections/cart-drawer.liquid:136`
**Issue:** The checkout link is `href="{{ routes.cart_url }}/checkout"`. `routes.cart_url` resolves to `/cart`, so this produces `/cart/checkout`. The correct Shopify checkout URL is `{{ routes.checkout_url }}` (which resolves to `/checkout`). The constructed path `/cart/checkout` does not exist and will 404 in a standard Shopify storefront.
**Fix:**
```liquid
<a href="{{ routes.checkout_url }}" ...>PROCEED TO CHECKOUT</a>
```

---

### WR-02: `bindCartItemEvents` cloneNode approach silently breaks on re-render

**File:** `assets/cart-drawer.js:173-199`
**Issue:** `bindCartItemEvents` removes the listener by cloning the node (`cloneNode(true)`) and replacing it in the DOM. It then re-queries `#cart-items` by ID to get the new node. However, `renderCart` calls `bindCartItemEvents` at line 295 after it has already set `currentCartItems.innerHTML` — meaning the `cartItems` variable captured in the outer `DOMContentLoaded` closure now points to the old (replaced) node, not the live one. Subsequent renders pass stale references. The fix is to always query by ID inside `renderCart`/`bindCartItemEvents` rather than closing over the initial reference — which the function partially does (`document.getElementById('cart-items')` on line 179) but this creates unnecessary churn. The real issue is that cloning and re-querying on every cart update is fragile; a single delegated listener attached once to a stable parent container (e.g. the drawer itself) would be more reliable.
**Fix:** Attach one delegated listener to `#cart-drawer` (the stable outer element) instead of re-attaching to `#cart-items` on every render. Remove `bindCartItemEvents` entirely.

---

### WR-03: `decrease` action allows quantity 1 → 1 with no feedback

**File:** `assets/cart-drawer.js:193`
**Issue:** When quantity is 1 and the decrease button is clicked, `Math.max(1, qty - 1)` evaluates to 1, so an API call `POST /cart/change.js` is made with `quantity: 1` — the same value already in the cart. This is a wasted network request and gives the user no feedback that the minimum has been reached. The decrease button is visually disabled (`disabled` attribute and `opacity-50`) in the initial Liquid render, but after `renderCart` rebuilds the HTML via `buildItemHTML`, the disable state is only set via the CSS class string in `disabledAttrs` (line 48) — the actual `disabled` HTML attribute is only added if `item.quantity <= 1` via the ternary, which looks correct. However, if a user rapidly clicks before the API response returns, the button can be re-enabled momentarily. The guard `Math.max(1, qty - 1)` prevents going below 1 but still fires the request.
**Fix:** Add an early return before the fetch when the action is `decrease` and `qty <= 1`:
```js
if (action === 'decrease' && qty <= 1) return;
```

---

### WR-04: `cookie-consent.js` — already-consented users see banner flash

**File:** `assets/cookie-consent.js:19-25`
**Issue:** When consent is already stored in `localStorage`, the code adds `translate-y-full` and then hides the banner after a 300 ms timeout. But the banner's initial CSS class in `sections/cookie-consent.liquid` is `translate-y-0` (visible), so for returning visitors the banner is rendered fully visible in the HTML, then hidden by JS after DOMContentLoaded. On slow devices or connections this produces a visible flash of the cookie banner before it slides out. The banner should start hidden (or the CSS should default to `translate-y-full`) and only be made visible when consent is absent.
**Fix:** Change the initial class on `#cookie-consent-banner` to `translate-y-full` (hidden by default) and remove it in JS when consent is absent:
```liquid
class="fixed bottom-0 ... transform translate-y-full transition-transform duration-300"
```
Then in JS, when no consent is stored, slide in with:
```js
requestAnimationFrame(() => banner.classList.remove('translate-y-full'));
```

---

### WR-05: Missing `aria-expanded` on search toggle button

**File:** `sections/header.liquid:77-84`
**Issue:** The `#nav-search-toggle` button opens/closes the inline search bar but has no `aria-expanded` attribute. Screen reader users get no indication of whether the search bar is currently open. The mobile nav hamburger correctly uses `aria-expanded` (line 9), but the search toggle does not.
**Fix:**
```html
<button id="nav-search-toggle" aria-expanded="false" aria-controls="nav-search-bar" ...>
```
In `inline-search.js`, update `aria-expanded` on open/close:
```js
toggle.setAttribute('aria-expanded', 'true');  // in openSearch
toggle.setAttribute('aria-expanded', 'false'); // in closeSearch
```

---

### WR-06: Address form accepts free-text country — no validation

**File:** `templates/customers/addresses.liquid:75-81`
**Issue:** The country field is a plain `<input type="text">` pre-filled with "United States". A user can type any arbitrary string. Shopify's customer address API will reject invalid country values at the server, but there is no client-side feedback and the form does not use `<select>` or Shopify's address autocomplete helper. This causes silent failures for international users and is likely to frustrate US users who mistype. Given the project is US-only at launch, at minimum the field should be `readonly` or replaced with a hidden input; a `<select>` with Shopify's `CountryProvinceSelector` is the conventional pattern.
**Fix:** Replace with a hidden input for US-only launch:
```html
<input type="hidden" name="address[country]" value="United States">
```
Or use Shopify's address selector helper for future-proofing.

---

### WR-07: `announcement-bar.liquid` — `remaining` can display as decimal with unexpected precision via `money_without_currency`

**File:** `sections/cart-drawer.liquid:49-50`
**Issue:** `remaining = threshold | minus: cart_total_dollars` can produce values like `24.5699999...` due to floating-point arithmetic on Liquid's division (`cart.total_price | divided_by: 100.0`). The `money_without_currency` filter will format this correctly for display, but the Liquid-rendered initial text and the JS-rendered text use different formatting paths: Liquid uses `money_without_currency`, while the JS (line 251 of `cart-drawer.js`) uses `.toFixed(2)`. These will agree numerically but may differ in locale formatting (e.g. thousands separators) for larger carts. This is a latent inconsistency that becomes visible for orders over $1,000.
**Fix:** In the JS, use the `formatPrice` helper consistently, or compute `remaining` in cents and format it with `formatPrice`:
```js
const remainingCents = threshold * 100 - cart.total_price;
shippingText.textContent = `You're ${formatPrice(remainingCents)} away from free shipping!`;
```

---

## Info

### IN-01: Dead variable `nav_links` in header

**File:** `sections/header.liquid:33`
**Issue:** `nav_links` is assigned via `| split: '|'` but never used. `nav_items` (line 34) is the variable actually iterated. The `nav_links` assignment is dead code.
**Fix:** Remove line 33.

---

### IN-02: `escapeHtml` is defined after it is first used

**File:** `assets/cart-drawer.js:41-95`
**Issue:** `buildItemHTML` (line 41) calls `escapeHtml` (defined at line 88). In non-strict mode JS this works due to hoisting of function declarations, but `escapeHtml` is defined as a `const` arrow function, which is NOT hoisted. This code executes correctly only because `buildItemHTML` itself is not called until after `escapeHtml` is defined (the call happens inside the `DOMContentLoaded` callback). However, the ordering is misleading and fragile — if someone calls `buildItemHTML` at module evaluation time it will throw `ReferenceError: Cannot access 'escapeHtml' before initialization`.
**Fix:** Move the `escapeHtml` definition to before `buildItemHTML` (i.e., before line 41).

---

### IN-03: `autofocus` attribute on search input always fires

**File:** `sections/header.liquid:59`
**Issue:** The search `<input>` has `autofocus` attribute. Because the search bar is hidden (`hidden opacity-0`) on load, most browsers will not actually focus the input — but the attribute is misleading and may cause unexpected focus behaviour on some browsers or assistive technologies. The JS already correctly calls `input.focus()` when the search is opened (line 9 of `inline-search.js`).
**Fix:** Remove the `autofocus` attribute from the input element. The JS-controlled focus is sufficient.

---

### IN-04: `cookie-consent.js` exported as `export default init` but also called via named export path

**File:** `assets/cookie-consent.js:46-48`
**Issue:** The file uses `export default init` then immediately calls `init()`. The pattern is inconsistent with `cart-drawer.js` which uses `export default function init()`. Minor inconsistency — `cookie-consent.js` declares `function init()` (hoisted function declaration) while the others use `export default function`. No runtime impact but the pattern should be uniform across the module files.
**Fix:** Standardise to `export default function init() { ... }` across all four JS modules.

---

_Reviewed: 2026-06-11T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
