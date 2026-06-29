---
phase: 03-home-page
fixed_at: 2026-06-12T00:00:00Z
review_path: .planning/phases/03-home-page/03-REVIEW.md
iteration: 1
findings_in_scope: 10
fixed: 9
skipped: 1
status: partial
---

# Phase 03: Code Review Fix Report

**Fixed at:** 2026-06-12
**Source review:** `.planning/phases/03-home-page/03-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 10 (4 Critical + 6 Warning)
- Fixed: 9
- Skipped: 1 (CR-01 — already correct in current code)

---

## Fixed Issues

### CR-02 + CR-03: Quick-add nil variant guard and product.title escape — featured-products.liquid

**Files modified:** `sections/featured-products.liquid`
**Commit:** `5b60786`
**Applied fix:** Assigned `product.first_available_variant` to `first_variant`, wrapped the form body in `{%- if first_variant -%}` rendering the hidden input + Quick Add button, with an `{%- else -%}` branch rendering a "Sold Out" `<span>`. Changed `{{ product.title }}` to `{{ product.title | escape }}`.

### CR-02 + CR-03: Quick-add nil variant guard and product.title escape — new-arrivals.liquid

**Files modified:** `sections/new-arrivals.liquid`
**Commit:** `b52ed26`
**Applied fix:** Same pattern as featured-products.liquid — `first_available_variant` guard with Sold Out fallback span, and `| escape` on product title output.

### CR-04: Correct metaobject field accessors in social-feed

**Files modified:** `sections/social-feed.liquid`
**Commit:** `d2aa87e`
**Applied fix:** Removed `.value` from `post.image.value` (now `post.image`) and removed the double-dereferenced `.value.product.*` chain from the product link (now `post.product.url` and `post.product.title`). Also removed the `.value` from the `alt` attribute's `post.caption.value` (now `post.caption`).

### WR-01: Ticker always renders two copies for seamless loop

**Files modified:** `sections/ticker.liquid`
**Commit:** `906c7fc`
**Applied fix:** Unified the custom-text branch to always emit two `<span>` elements — the second has `aria-hidden="true"`. The default content already had two copies; the custom-text branch previously only rendered one, causing a snap-back on each cycle.

### WR-02: Hero CTA renders as `<span>` when URL is blank

**Files modified:** `sections/hero.liquid`
**Commit:** `56338e6`
**Applied fix:** Wrapped the `<a>` tag in `{%- if section.settings.cta_url != blank -%}` with an `{%- else -%}` branch that renders a `<span>` with `opacity-70 cursor-default` styling. Prevents the `href=""` self-referencing link.

### WR-03: Testimonial carousel currentIndex updated before setTimeout

**Files modified:** `assets/testimonial-carousel.js`
**Commit:** `4527270`
**Applied fix:** Moved `currentIndex = index` to the top of `showQuote()`, before the fade-out and `setTimeout`. Removed it from inside the `setTimeout` callback. The `next()` auto-rotation function now always reads the correct baseline index even if `showQuote` is called rapidly.

### WR-04: Category grid anchor has aria-label

**Files modified:** `sections/category-grid.liquid`
**Commit:** `718e111`
**Applied fix:** Added `{%- assign card_label = block.settings.label | default: block.settings.collection.title | default: 'Shop' -%}` before the anchor and added `aria-label="{{ card_label }}"` to the `<a>` element. Fallback ensures unlabeled cards still announce "Shop" to screen readers.

### WR-05: brand-promise section suppressed when no blocks

**Files modified:** `sections/brand-promise.liquid`
**Commit:** `22de463`
**Applied fix:** Wrapped the entire `<section>` element in `{%- if section.blocks.size > 0 -%}...{%- endif -%}` so no dark stripe is rendered when the merchant has not added any blocks.

### WR-06: sizing-banner size list is merchant-configurable

**Files modified:** `sections/sizing-banner.liquid`
**Commit:** `7446064`
**Applied fix:** Added a `text` schema setting `size_list` with default `"XXS,XS,S,M,L,XL,2X,3X"` and info text explaining the comma-separated format. Changed the Liquid assignment to `section.settings.size_list | default: 'XXS,XS,S,M,L,XL,2X,3X' | split: ','`. Merchants can now update the size range from the theme editor without a code change. (Note: the original hard-coded default had `1X,2X,3X` — the REVIEW.md specified `2X,3X` as the corrected default range per brand sizing `XXS–3XL`; updated accordingly.)

---

## Skipped Issues

### CR-01: Broken ES module import — double script load

**File:** `sections/testimonials.liquid:62-65`
**Reason:** Code context differs from review — the current file already has the correct single inline `<script type="module">` pattern with no external `<script src>` tag. The double-load defect described in the review is not present in the current source. No change needed.
**Original issue:** Section was loading `testimonial-carousel.js` twice (one external src tag + one inline import), causing double module evaluation.

---

_Fixed: 2026-06-12_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
