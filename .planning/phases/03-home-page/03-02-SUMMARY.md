---
phase: 03-home-page
plan: "02"
subsystem: sections
tags: [liquid, brand-promise, sizing-banner, home-page, dark-panel]
dependency_graph:
  requires: []
  provides:
    - sections/brand-promise.liquid
    - sections/sizing-banner.liquid
  affects:
    - templates/index.json (wired in Plan 05)
tech_stack:
  added: []
  patterns:
    - Shopify Liquid block schema with presets
    - Tailwind utility classes via design token aliases (bg-deep, text-gold, text-coral)
key_files:
  created:
    - sections/brand-promise.liquid
    - sections/sizing-banner.liquid
  modified: []
decisions:
  - Hardcoded decorative diamond SVG in each promise block (not a schema field) — icons are purely decorative; owner can request icon variants post-launch
  - Size pills rendered via Liquid assign/split trick on a fixed comma-delimited string — avoids schema complexity for a static, brand-defined size range
metrics:
  duration_minutes: 5
  completed_date: "2026-06-12"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 0
requirements_addressed:
  - HOME-06
  - HOME-09
---

# Phase 03 Plan 02: Brand Promise Strip and Sizing Banner Summary

**One-liner:** Two dark-panel Liquid sections — 4-column brand promise grid with block-based editing and a fixed size pill row (XXS–3X) with owner-editable heading and CTA.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Build Brand Promise strip section (HOME-06) | 26c9063 | sections/brand-promise.liquid |
| 2 | Build Sizing Banner section (HOME-09) | bcfe273 | sections/sizing-banner.liquid |

## Implementation Details

### Brand Promise Strip (sections/brand-promise.liquid)

- Outer section uses `bg-deep py-10 md:py-12`
- 2-column mobile, 4-column desktop grid (`grid grid-cols-2 md:grid-cols-4 gap-8`)
- Each block renders a decorative diamond SVG in `text-gold`, a heading in `font-body text-sm font-semibold tracking-widest uppercase text-cream`, and a descriptor in `font-body text-xs text-mid`
- Schema: `type: "promise"`, `max_blocks: 4`, preset with 4 blocks (Premium Fabrics, Sizes XXS–3XL, New Drops Weekly, US-Based & Proud)
- `{{ block.shopify_attributes }}` applied for theme editor targeting

### Sizing Banner (sections/sizing-banner.liquid)

- Outer section uses `bg-deep py-10 md:py-12`, inner `max-w-2xl mx-auto px-4 text-center`
- Heading in `font-display text-2xl md:text-3xl text-cream`, owner-editable, default: "Find Your Perfect Fit"
- Size pills rendered via `{% assign sizes = "XXS,XS,S,M,L,XL,1X,2X,3X" | split: "," %}` loop
- Each pill: `border border-cream/30 px-3 py-1 font-body text-xs tracking-wide text-cream/80 hover:border-coral hover:text-coral transition-colors cursor-pointer`
- CTA: `text-coral hover:text-gold transition-colors`, owner-editable label and URL, default href `/pages/size-guide`
- Schema: settings for `heading` (text), `cta_label` (text), `cta_url` (url)

## Deviations from Plan

None — plan executed exactly as written.

## Threat Surface Scan

No new trust boundaries or security-relevant surface beyond what was documented in the plan's threat model. Liquid auto-escapes `section.settings.heading`; `cta_url` uses `type: "url"` schema setting enforcing Shopify URL validation.

## Known Stubs

None — both sections are complete and self-contained. Wiring into `templates/index.json` is intentionally deferred to Plan 05.

## Self-Check: PASSED

- sections/brand-promise.liquid exists: FOUND
- sections/sizing-banner.liquid exists: FOUND
- Commit 26c9063 exists: FOUND
- Commit bcfe273 exists: FOUND
