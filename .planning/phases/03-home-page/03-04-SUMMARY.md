---
phase: 03-home-page
plan: "04"
subsystem: sections
tags: [social-feed, category-grid, metaobjects, liquid, tailwind, home-page]
dependency_graph:
  requires: [03-01]
  provides: [sections/social-feed.liquid, sections/category-grid.liquid]
  affects: [templates/index.json]
tech_stack:
  added: []
  patterns:
    - Shopify metaobject iteration via shop.metaobjects.<type>.values
    - Block-based section schema with collection picker per block
    - Tailwind group-hover overlay pattern for interactive cards
    - CSS scrollbar-hide via custom class + ::-webkit-scrollbar rule
key_files:
  created:
    - sections/social-feed.liquid
    - sections/category-grid.liquid
  modified: []
decisions:
  - Overlay div always rendered in social feed; shop link gated on post.product != blank (D-08 graceful degradation — decorative dark overlay on hover even when product is null)
  - Arrow character rendered as HTML entity &rarr; inside text-coral span to satisfy Liquid escaping
  - Category grid preset blocks ship with label strings only (no collection assigned); collections are store-specific and must be set by owner in theme editor
metrics:
  duration_seconds: 66
  completed_date: "2026-06-12"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 0
---

# Phase 03 Plan 04: Social Feed Strip and Category Grid Summary

Horizontal-scroll shoppable social feed from social_post metaobjects and a 2x4 category grid with hover overlays, both wired to Tailwind utility classes and owner-configurable via the Shopify theme editor.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Build Social Feed strip section (HOME-05) | 185a6ea | sections/social-feed.liquid |
| 2 | Build Category Grid section (HOME-03) | fe9a0d3 | sections/category-grid.liquid |

## What Was Built

### sections/social-feed.liquid
- Outer section: `bg-cream py-12 md:py-16`
- Heading h2 with configurable text (default: "As Seen On") using `font-display text-3xl md:text-4xl text-deep text-center mb-8`
- Scroll container: `social-feed-scroll flex gap-4 overflow-x-auto snap-x snap-mandatory pb-4` with CSS scrollbar-hide rule targeting `.social-feed-scroll::-webkit-scrollbar`
- Iterates `shop.metaobjects.social_post.values`; each card `w-64 h-64 flex-shrink-0 snap-start overflow-hidden`
- Card image: `image_url: width: 400 | image_tag` with `bg-sand` placeholder
- Hover overlay: `absolute inset-0 bg-deep/70 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center`
- Shop link wrapped in `{% if post.product != blank %}` — shows "Shop [title]" with `text-coral` arrow; overlay is purely decorative when product is null (D-08)
- Empty state paragraph when no metaobjects exist
- Schema: one setting (heading), preset "Social Feed Strip"

### sections/category-grid.liquid
- Outer section: `bg-cream py-12 md:py-16`
- Grid: `grid grid-cols-2 lg:grid-cols-4 gap-4`
- Iterates `section.blocks`; each card is `<a>` with `relative group block aspect-square overflow-hidden`
- `block.shopify_attributes` included on anchor for theme editor targeting
- Image: `collection.featured_image | image_url: width: 600 | image_tag` with `bg-sand` placeholder
- Overlay: `absolute inset-0 bg-deep/40 group-hover:bg-deep/60 transition-colors duration-300 flex items-center justify-center`
- Label span: `text-cream font-body text-sm font-semibold tracking-widest uppercase` — `block.settings.label | default: block.settings.collection.title`
- Schema: blocks type `category_card` with `collection` (collection picker) and `label` (text override); `max_blocks: 4`
- Preset: 4 blocks with labels Bikinis, Lingerie, New In, Sale

## Deviations from Plan

None — plan executed exactly as written.

## Threat Surface Scan

No new trust boundaries introduced beyond those in the plan's threat model. Both files use Liquid's default escaping on all metaobject text output (`post.caption.value`, product title). No `raw` filter used. URLs sourced from internal Shopify product/collection objects (auto-escaped in href attributes).

## Known Stubs

- Category grid preset blocks have no `collection` value assigned — owners must select collections in the theme editor. Labels ("Bikinis", "Lingerie", "New In", "Sale") are placeholders until collections are assigned. This is intentional per plan instructions (collections are store-specific).
- Social feed renders the empty-state paragraph until the owner creates Social Post metaobjects in Shopify admin. This is expected behavior, not a build stub.

## Self-Check: PASSED

- sections/social-feed.liquid: exists, contains schema, iterates social_post.values, overlay gated on product != blank
- sections/category-grid.liquid: exists, contains schema, iterates section.blocks, max_blocks: 4, preset has 4 labeled blocks
- Commits 185a6ea and fe9a0d3 verified in git log
