---
phase: 04-collections-product-detail
plan: "02"
subsystem: collection-browsing
tags: [collection, filter, ajax, liquid, vanilla-js]
dependency_graph:
  requires: []
  provides:
    - sections/collection-grid.liquid
    - assets/collection-filter.js
  affects:
    - templates/collection.json
    - snippets/product-card.liquid
tech_stack:
  added: []
  patterns:
    - Shopify section rendering API (section_id param) for AJAX partial HTML swap
    - ES module with default init() export (mobile-nav.js pattern)
    - DOMParser for safe HTML parsing of fetched section HTML
    - history.pushState for clean URL updates without reload
    - CSS.escape() for safe querySelector with user-controlled attribute values
key_files:
  created:
    - sections/collection-grid.liquid
    - assets/collection-filter.js
  modified: []
decisions:
  - "Sticky sidebar uses top-20 self-start on the aside element; flex gap-8 row provides natural gutter"
  - "Filter groups rendered once via Liquid capture block, output in both sidebar and drawer to avoid duplication"
  - "Drawer focus trap attached/detached on open/close (not persistent) to avoid keydown conflicts with global Escape handler"
  - "Price inputs use divided_by 100.0 to convert Shopify money integers to display dollars server-side"
  - "applyFilters() reads only from desktop sidebar inputs; drawer mirrors same markup so mobile users apply via Show Results button"
metrics:
  duration_minutes: 25
  completed_date: "2026-06-14"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 0
---

# Phase 04 Plan 02: Collection Grid + AJAX Filter Summary

**One-liner:** Shopify collection browsing section with sticky desktop filter sidebar, mobile slide-in filter drawer, AJAX grid swap via section_id, URL pushState, and removable active filter chips.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Build sections/collection-grid.liquid | 314697c | sections/collection-grid.liquid |
| 2 | Build assets/collection-filter.js | 16e8e5e | assets/collection-filter.js |

## What Was Built

### sections/collection-grid.liquid

Full collection browsing UI as a single Shopify section (no schema settings — all content from the collection object):

- **Hero banner:** `bg-deep text-cream py-24` with optional `collection.image` as a 30%-opacity background. `hero_subtitle` from `custom.hero_subtitle` metafield rendered below the h1.
- **Filter groups:** Rendered once via `{%- capture filter_groups_html -%}` and output in both the desktop sidebar and mobile drawer, eliminating duplication. Supports `filter.type == 'list'` (checkboxes with `data-filter-input`) and `filter.type == 'price_range'` (two number inputs with `data-filter-price-min` / `data-filter-price-max`).
- **Desktop sidebar:** `aside#filter-sidebar` — `hidden lg:block w-60 sticky top-20 self-start`. Clear All button (`#filter-clear-all`).
- **Mobile drawer:** `div#filter-drawer` — `fixed inset-y-0 left-0 -translate-x-full transition-transform duration-300`. Show Results button (`#filter-drawer-apply`). Drawer overlay (`#filter-drawer-overlay`).
- **Toolbar:** Mobile Filter button (`#filter-drawer-open`), active chips container (`#active-filter-chips`), sort dropdown (`#sort-by`), product count (`#product-count`).
- **Product grid:** `#product-grid-inner grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4` — renders `snippets/product-card.liquid` with `paginate by 24`.
- **Empty state:** Server-side "Nothing here yet" / "New drops land every week" copy when `collection.products_count == 0`.
- **XSS safety:** 8 uses of `| escape` covering all merchant-controlled string outputs.

### assets/collection-filter.js

ES module following `mobile-nav.js` pattern (named functions + `export default init()` + `init()` call at bottom):

- **`escapeHtml(str)`** — Same implementation as `cart-drawer.js` (`& < > " '` replacements). Used for chip label injection and chip `data-*` attribute values.
- **`openFilterDrawer()` / `closeFilterDrawer()`** — Toggle `-translate-x-full`/`translate-x-0` on `#filter-drawer`, toggle `hidden` on `#filter-drawer-overlay`, lock/unlock `body.style.overflow`, attach/detach focus trap listener. Return focus to `#filter-drawer-open` on close.
- **`buildActiveChips(searchParams)`** — Iterates params starting with `filter.`, builds escaped chip HTML with per-chip `×` remove button using `data-remove-param` / `data-remove-value` attributes.
- **`fetchFilteredGrid(url)`** — `fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})`, parses response via `DOMParser`, swaps `#product-grid-inner` innerHTML. Injects JS no-match message when returned grid is empty. Updates `#product-count` text.
- **`getFilterParams()`** — Reads all `[data-filter-input]:checked` checkboxes and price inputs; returns `URLSearchParams`.
- **`applyFilters()`** — Builds params, appends `section_id=collection-grid` for fetch URL only, pushes clean URL via `history.pushState`, calls `buildActiveChips` and `fetchFilteredGrid`.
- **`init()`** — Wires all event listeners; hydrates chips and sort-by select from existing URL params on page load.

## Threat Model Compliance

| Threat ID | Mitigation Applied |
|-----------|-------------------|
| T-04-02-01 | `| escape` applied to all Liquid string outputs (8 occurrences) |
| T-04-02-02 | `escapeHtml()` used for chip label text and `data-*` attribute values in innerHTML |
| T-04-02-03 | `X-Requested-With: XMLHttpRequest` header on all fetch calls |
| T-04-02-04 | `CSS.escape()` used when building `querySelector` string from `data-remove-param` / `data-remove-value` |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — both files are fully implemented. `snippets/product-card.liquid` is referenced by the collection grid but is created in plan 04-01 (or another plan); that dependency is external to this plan.

## Self-Check: PASSED

- sections/collection-grid.liquid: FOUND (commit 314697c)
- assets/collection-filter.js: FOUND (commit 16e8e5e)
