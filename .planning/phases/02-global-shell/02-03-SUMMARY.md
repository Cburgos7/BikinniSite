---
phase: 02-global-shell
plan: 03
subsystem: navigation
tags: [header, nav, mobile-drawer, inline-search, liquid, js]
dependency_graph:
  requires: [02-01]
  provides: [sticky-nav, mobile-drawer, inline-search, cart-badge]
  affects: [layout/theme.liquid, sections/header.liquid, sections/announcement-bar.liquid, assets/mobile-nav.js, assets/inline-search.js]
tech_stack:
  added: []
  patterns: [ES module with export default + immediate init, Liquid schema image_picker, Tailwind responsive classes]
key_files:
  created:
    - assets/mobile-nav.js
    - assets/inline-search.js
  modified:
    - layout/theme.liquid
    - sections/header.liquid
    - sections/announcement-bar.liquid
decisions:
  - encodeURIComponent used on search query (T-02-03 mitigation)
  - Announcement bar text field left blank triggers auto free-shipping message
metrics:
  duration: ~15min
  completed: 2026-06-11
---

# Phase 2 Plan 03: Sticky Navigation Summary

**One-liner:** Full sticky nav with desktop links, mobile left-drawer, inline search expand, and cart badge — all in Liquid + Tailwind + vanilla JS ES modules.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Update theme.liquid + build header.liquid | 44216c2 | layout/theme.liquid, sections/header.liquid |
| 2 | Create mobile-nav.js and inline-search.js | e5e7fe3 | assets/mobile-nav.js, assets/inline-search.js |
| 3 | Update announcement-bar free shipping threshold | df0de2a | sections/announcement-bar.liquid |

## What Was Built

- `layout/theme.liquid`: body gets `pt-16`; announcement bar and header sections inserted above `<main>`
- `sections/header.liquid`: full sticky nav — fixed `h-14 lg:h-16`, responsive layout, inline search div, mobile drawer with overlay, cart count badge, schema with logo + threshold
- `assets/mobile-nav.js`: hamburger/close/overlay click handlers, Escape key, focus trap (Tab cycling), scroll lock (`document.body.style.overflow`)
- `assets/inline-search.js`: toggle open/close, autofocus, Enter navigation to `/search?q=encodeURIComponent(query)`, Escape collapse
- `sections/announcement-bar.liquid`: additive `free_shipping_threshold` number setting; blank text field auto-renders threshold dynamically

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Security] encodeURIComponent on search query**
- **Found during:** Task 2 (threat model T-02-03 explicitly called out)
- **Issue:** Raw `input.value` appended to URL would allow `&` param injection or `#` fragment spoofing
- **Fix:** `encodeURIComponent(input.value.trim())` used in `window.location.href` construction
- **Files modified:** assets/inline-search.js
- **Commit:** e5e7fe3

## Known Stubs

None — nav links are hardcoded to real collection URLs; cart badge renders from live `cart.item_count`.

## Threat Flags

None beyond T-02-03 (mitigated above).

## Self-Check: PASSED

- layout/theme.liquid contains `{% section 'header' %}` — confirmed
- sections/header.liquid contains `fixed top-0` — confirmed
- sections/header.liquid contains `mobile-nav-drawer` — confirmed
- assets/mobile-nav.js contains `export default` — confirmed
- assets/inline-search.js contains `export default` — confirmed
- All 3 commits exist in git log
