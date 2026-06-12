---
phase: 03-home-page
reviewed: 2026-06-12T00:00:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - assets/testimonial-carousel.js
  - sections/brand-promise.liquid
  - sections/category-grid.liquid
  - sections/featured-products.liquid
  - sections/hero.liquid
  - sections/new-arrivals.liquid
  - sections/sizing-banner.liquid
  - sections/social-feed.liquid
  - sections/testimonials.liquid
  - sections/ticker.liquid
  - templates/index.json
findings:
  critical: 4
  warning: 6
  info: 4
  total: 14
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-06-12T00:00:00Z
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

This review covers the full home-page section set for the Soleil Noir Shopify theme: hero, ticker, category grid, featured products, new arrivals, social feed, brand promise, testimonials carousel, sizing banner, and the index template. The sections are generally well-structured and the testimonial carousel has good security discipline (textContent, JSON filter handoff). However, four critical defects were found that either break functionality for real visitors or represent correctness failures — most notably a broken ES module import pattern in testimonials, a cart-add form that silently drops out-of-stock products, and an unescaped Liquid output in two product-card sections. Six warnings cover reliability and editor-experience issues.

---

## Critical Issues

### CR-01: Broken ES module import — `init()` is never called in practice

**File:** `sections/testimonials.liquid:62-65`

**Issue:** The section loads `testimonial-carousel.js` twice. The first `<script type="module" src="...">` tag silently executes the module (which exports `init` but calls nothing at top level — correct). The second inline module does `import { init } from <url>` and then calls `init()` inside `DOMContentLoaded`. The problem is that browsers treat `type="module"` scripts as deferred automatically — `DOMContentLoaded` will already have fired by the time an inline module that depends on the external module resolves, particularly in Shopify's asset pipeline where the URL may be cache-busted. More critically: **the first `<script src>` tag is redundant and causes a double module evaluation**. In practice on some browsers, the inline module's `import` will resolve to a separate module instance (two fetches, two instances), meaning the `init` registered in one instance never sees the DOM state set up by the other. The carousel silently does nothing when there is only one module instance evaluating the export.

The correct pattern is a single inline module that imports and calls `init()`:

```html
<!-- Remove the external src tag entirely -->
<script type="module">
  import { init } from {{ 'testimonial-carousel.js' | asset_url | json }};
  init(); // modules are already deferred — DOMContentLoaded wrapper is unnecessary
</script>
```

---

### CR-02: Quick Add submits `id = ""` for sold-out / variant-less products — cart error surfaces to customer

**File:** `sections/featured-products.liquid:23` and `sections/new-arrivals.liquid:23`

**Issue:** Both product cards render:

```liquid
<input type="hidden" name="id" value="{{ product.first_available_variant.id }}">
```

`first_available_variant` returns `nil` when every variant is sold out. Shopify Liquid renders `nil` as an empty string, so `value=""`. When a customer clicks "Quick Add" on a sold-out product, a POST is sent to `/cart/add` with `id=` (blank), which returns a 422 JSON error. Because the form has no JS error handler and no `novalidate`, the page reloads to the raw cart error page — a broken UX that exposes Shopify's default error response to the shopper.

Fix: guard the button and input when no variant is available.

```liquid
{%- assign first_variant = product.first_available_variant -%}
<form action="/cart/add" method="post" class="absolute bottom-0 left-0 right-0">
  {%- if first_variant -%}
    <input type="hidden" name="id" value="{{ first_variant.id }}">
    <button type="submit" class="...">Quick Add</button>
  {%- else -%}
    <span class="w-full bg-mid text-cream py-3 font-body text-xs tracking-widest uppercase flex items-center justify-center translate-y-full group-hover:translate-y-0 transition-transform duration-200">
      Sold Out
    </span>
  {%- endif -%}
</form>
```

---

### CR-03: Unescaped Liquid output in product title and price — XSS if Shopify ever returns malicious data

**File:** `sections/featured-products.liquid:31-32` and `sections/new-arrivals.liquid:31-32`

**Issue:** Product title and price are output without the `escape` filter:

```liquid
<p ...>{{ product.title }}</p>
<p ...>{{ product.price | money }}</p>
```

Shopify sanitizes product titles server-side today, but Shopify's own documentation recommends applying `escape` to any user-controlled string rendered into HTML. If a merchant sets a product title containing `<script>` or `">` (e.g. via the API or a bulk import), the raw string is injected into the DOM. `| money` is safe (numeric), but `product.title` is not.

Fix:

```liquid
<p ...>{{ product.title | escape }}</p>
```

Apply consistently to every `{{ product.title }}` and `{{ block.settings.* }}` rendered inside HTML (not inside attributes, where Shopify's `image_tag` helper already encodes).

---

### CR-04: `social-feed` section accesses metaobject fields with `.value` — incorrect API usage that silently renders nothing

**File:** `sections/social-feed.liquid:20,27`

**Issue:** The section uses:

```liquid
post.image.value | image_url: width: 400
post.product.value.product.url
post.product.value.product.title
```

In Shopify's Liquid metaobject API, `shop.metaobjects.<type>.values` returns a collection of metaobject entries. Each entry's fields are accessed directly as `post.<field_key>` — not `post.<field_key>.value`. The `.value` accessor does not exist in this context and resolves to `nil`, so `post.image.value` is always blank, the image placeholder is always shown, and `post.product.value.product.url` is always nil (the shop link is never rendered). The entire social feed silently shows placeholder boxes.

Fix — use the correct field accessor syntax:

```liquid
{%- if post.image != blank -%}
  {{ post.image | image_url: width: 400 | image_tag: ... }}
{%- endif -%}

{%- if post.product != blank -%}
  <a href="{{ post.product.url }}">Shop {{ post.product.title }}</a>
{%- endif -%}
```

Note: the exact accessor path depends on the metaobject field type (file reference vs. product reference). Verify in the Shopify admin metaobject definition and adjust accordingly. The current `.value.product` chain is doubly wrong for a product reference field.

---

## Warnings

### WR-01: Ticker only duplicates content when text is blank — custom text has broken seamless loop

**File:** `sections/ticker.liquid:15-21`

**Issue:** When `section.settings.ticker_text` is set by the merchant, only one `<span>` is rendered. The CSS marquee animates to `-50%` expecting two identical copies to create a seamless loop. With one copy, the ticker reaches the end of the text and snaps back, creating a visible jump on every cycle.

Fix: always render two copies:

```liquid
{%- assign ticker_content = section.settings.ticker_text | default: 'Dare to Bare ...' -%}
<span ...>{{ ticker_content }}</span>
<span aria-hidden="true" ...>{{ ticker_content }}</span>
```

---

### WR-02: Hero CTA renders a broken `href` when no URL is configured

**File:** `sections/hero.liquid:21`

**Issue:** `{{ section.settings.cta_url }}` outputs an empty string when the merchant has not set a URL. The `<a>` tag becomes `href=""`, which resolves to the current page — the button clicks but navigates to the page itself, silently doing nothing rather than being visually disabled. There is no `default` fallback and no conditional guard.

Fix:

```liquid
{%- if section.settings.cta_url != blank -%}
  <a href="{{ section.settings.cta_url }}" class="...">{{ section.settings.cta_label }}</a>
{%- else -%}
  <span class="...">{{ section.settings.cta_label }}</span>
{%- endif -%}
```

---

### WR-03: Testimonials carousel `showQuote` advances `currentIndex` inside a `setTimeout` — race condition with rapid dot clicks

**File:** `assets/testimonial-carousel.js:95`

**Issue:** `currentIndex = index` is set inside `setTimeout(..., FADE_DURATION)` (500 ms). If a user clicks a dot twice quickly within 500 ms, the first `setTimeout` hasn't updated `currentIndex` yet when `next()` is called by the auto-timer or second click. The auto-rotation then advances from the stale `currentIndex`, skipping the intended target. The dot UI updates correctly (it uses `index`) but the next auto-advance uses the wrong baseline.

Fix: update `currentIndex` immediately in `showQuote` before the `setTimeout`, not inside it.

```js
function showQuote(index) {
  currentIndex = index; // update immediately
  quoteEl.classList.add('opacity-0');
  authorEl.classList.add('opacity-0');
  setTimeout(() => {
    // ... render content, sync dots (no currentIndex = index here)
  }, FADE_DURATION);
}
```

---

### WR-04: Category grid `<a>` has no accessible label when both collection and label are blank

**File:** `sections/category-grid.liquid:5,14-16`

**Issue:** The card anchor's visible text is `{{ block.settings.label | default: block.settings.collection.title }}`. If a merchant adds a card without selecting a collection and leaves label blank, both values are empty and the anchor renders as a clickable element with no visible text and no `aria-label`. Screen readers announce it as an unlabeled link.

Fix: provide a fallback or suppress the card entirely:

```liquid
{%- assign card_label = block.settings.label | default: block.settings.collection.title | default: 'Shop' -%}
```

---

### WR-05: `brand-promise.liquid` renders the section with no blocks — empty `<section>` visible on page

**File:** `sections/brand-promise.liquid:4`

**Issue:** There is no guard around the `{%- for block in section.blocks -%}` loop. When a merchant adds the section but has not yet added any blocks (or removes all blocks), the section renders an empty `<div class="grid ...">` inside a visible padded `<section>`. The `bg-deep py-10` creates a dark stripe with no content — visible layout gap.

Fix: wrap the section body in `{%- if section.blocks.size > 0 -%}`.

---

### WR-06: `sizing-banner.liquid` hardcodes the size list in Liquid — merchant cannot customize it from theme editor

**File:** `sections/sizing-banner.liquid:6`

**Issue:** `{%- assign sizes = "XXS,XS,S,M,L,XL,1X,2X,3X" | split: "," -%}` is a hard-coded string. If the store's actual range changes (e.g. adds 4X or removes XXS for a category), the merchant cannot update it without a developer code change. The schema has no `sizes` setting.

Fix: add a `text` schema setting (comma-separated) with the current string as default, then use `section.settings.sizes | split: ","` in the Liquid.

---

## Info

### IN-01: Hero section uses `<div>` as the root element instead of `<section>` or `<header>`

**File:** `sections/hero.liquid:1`

**Issue:** The root element is `<div class="flex ...">`. Every other section uses `<section>`. This is inconsistent and slightly worse for semantics / landmark navigation. Minor, but a `<header>` or `<section>` would be more appropriate for the page's primary hero.

---

### IN-02: Placeholder copy committed in schema defaults

**File:** `sections/hero.liquid:44,49`

**Issue:** `"default": "[PLACEHOLDER — owner provides]"` is a development note embedded in the deployed schema. In the Shopify theme editor, new instances of the Hero section will pre-populate with `[PLACEHOLDER — owner provides]` as visible text. This should be replaced with real copy or left as an empty string.

---

### IN-03: `new-arrivals` section is placed after `testimonials` in `index.json` order

**File:** `templates/index.json:47-56`

**Issue:** The section order is: hero → ticker → category-grid → featured-products → social-feed → brand-promise → testimonials → **new-arrivals** → sizing-banner. Placing New Arrivals after Testimonials buries the freshest product content below social proof. This is a merchandising concern, not a code defect, but worth flagging for the owner to review before launch.

---

### IN-04: No `prefers-reduced-motion` guard on ticker CSS animation or testimonials carousel timer

**File:** `sections/ticker.liquid:2-4`, `assets/testimonial-carousel.js:108`

**Issue:** The marquee animation runs unconditionally. Users who have enabled "Reduce Motion" in their OS get the full animated ticker and auto-rotating carousel regardless. WCAG 2.1 SC 2.3.3 (AAA) recommends respecting this preference; for a fashion site with continuous motion it is a quality concern.

Fix for ticker:

```css
@media (prefers-reduced-motion: reduce) {
  #ticker-track { animation: none; }
}
```

Fix for carousel: check `window.matchMedia('(prefers-reduced-motion: reduce)').matches` and skip `startTimer()` if true.

---

_Reviewed: 2026-06-12T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
