---
phase: 05-content-pages
plan: "02"
subsystem: sections
tags: [models, metaobject, grid, liquid]
dependency_graph:
  requires: []
  provides: [sections/page-models.liquid]
  affects: []
tech_stack:
  added: []
  patterns: [metaobject-iteration, page-hero-D10, portrait-grid-D01]
key_files:
  created:
    - sections/page-models.liquid
  modified: []
decisions:
  - "All metaobject field outputs escaped with | escape; instagram_handle additionally strips @ with | remove: '@' before href and display rendering"
metrics:
  duration: "5m"
  completed: "2026-06-14"
---

# Phase 05 Plan 02: Models Grid Section Summary

**One-liner:** Responsive 3-column portrait grid powered by `shop.metaobjects.model.values` with hover scale, bio, Instagram link, and merchant-configurable D-10 hero.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Build page-models.liquid | aacb080 | sections/page-models.liquid |

## What Was Built

`sections/page-models.liquid` implements:
- **D-10 hero** — `bg-deep text-cream py-16 lg:py-24` banner with schema-configurable heading (default "The Faces of Soleil Noir") and optional subtitle
- **D-01 portrait grid** — `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8` iterating `shop.metaobjects.model.values` with `limit: 10`
- Each model card: `bg-cream group`, `aspect-[2/3] overflow-hidden` portrait with `group-hover:scale-105 transition-transform duration-500`, name, height + size worn, `line-clamp-3` bio, optional Instagram link
- **Empty state** — "New faces coming soon." / "Check back after our next drop."
- `{% schema %}` with heading and subtitle settings and a "Models Page" preset

## Security

- T-05-02-01 mitigated: all `model.name`, `model.bio`, `model.height`, `model.size_worn` outputs use `| escape`
- T-05-02-02 mitigated: `instagram_handle` uses `| remove: '@' | escape` before href interpolation and display
- T-05-02-03 accepted: Instagram link uses `rel="noopener noreferrer" target="_blank"`

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — all threat register mitigations applied.

## Self-Check: PASSED

- [x] `sections/page-models.liquid` exists and is non-empty
- [x] `{% schema %}` present
- [x] `shop.metaobjects.model.values` present
- [x] `limit: 10` present
- [x] `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8` present
- [x] `aspect-[2/3]` present
- [x] `group-hover:scale-105` present
- [x] `line-clamp-3` present
- [x] instagram present
- [x] "New faces coming soon." present
- [x] Commit aacb080 exists
