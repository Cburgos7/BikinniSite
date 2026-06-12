---
phase: 03-home-page
plan: "01"
subsystem: sections
tags: [hero, ticker, marquee, liquid, tailwind]
dependency_graph:
  requires: []
  provides: [sections/hero.liquid, sections/ticker.liquid]
  affects: [templates/index.json]
tech_stack:
  added: []
  patterns: [shopify-liquid-section, tailwind-utility-classes, css-keyframe-animation]
key_files:
  created:
    - sections/hero.liquid
    - sections/ticker.liquid
  modified: []
decisions:
  - "Image fallback uses an inner div with bg-sand class (not applied to the panel wrapper) to ensure the fallback fills the full left panel height"
  - "Ticker duplicates content spans in Liquid (not JS) for seamless CSS loop — translateX(-50%) on doubled content = one full pass"
metrics:
  duration: "~10 minutes"
  completed: "2026-06-12"
requirements_fulfilled:
  - HOME-01
  - HOME-02
---

# Phase 03 Plan 01: Hero + Ticker Sections Summary

Hero section (split layout, image/text, coral CTA) and CSS marquee ticker section with pause-on-hover — both owner-editable via Shopify theme editor.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Build Hero section (HOME-01) | 6ac3e1d | sections/hero.liquid |
| 2 | Build Ticker/Marquee section (HOME-02) | f7e2951 | sections/ticker.liquid |

## What Was Built

**Hero section (`sections/hero.liquid`):**
- Flex split layout: image panel 55% left (aspect-[4/3] mobile, auto desktop), text panel 45% right (bg-deep)
- Image rendered via `image_url: width: 1200 | image_tag` with `loading: eager`
- Graceful fallback: left panel shows `bg-sand` inner div when no image is set
- Text panel: Cormorant Garamond h1 (font-display), Barlow Condensed subheadline and CTA (font-body)
- CTA anchor: coral background with hover/focus/active states, focus ring for accessibility
- Schema: 5 settings — image (image_picker), heading (text), subheading (text), cta_label (text), cta_url (url)

**Ticker section (`sections/ticker.liquid`):**
- CSS `@keyframes marquee` animates `translateX(0)` to `translateX(-50%)` over 30s linear infinite
- Content duplicated in Liquid (two identical spans) so -50% of total track width = one seamless loop
- Hover pause via CSS rule: `#ticker-section:hover #ticker-track { animation-play-state: paused; }`
- Default copy: "Dare to Bare · Inclusive Sizing XXS–3XL · New Drops Weekly · US-Based · Free Shipping Over $75"
- Gold separators (`text-gold`) between phrases; full font-body tracking-widest uppercase styling
- Schema: 1 setting — ticker_text (text, leave blank for defaults)

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

| Stub | File | Reason |
|------|------|--------|
| Heading default "[PLACEHOLDER — owner provides]" | sections/hero.liquid | Brand copy is owner-provided; intentional per PROJECT.md constraints |
| Subheading default "[PLACEHOLDER — owner provides]" | sections/hero.liquid | Brand copy is owner-provided; intentional per PROJECT.md constraints |

Both stubs are intentional — the sections are fully functional and owner-editable. Content is provided by the store owner, not the build.

## Threat Surface Scan

No new threat surface beyond what the plan's threat model covers. Liquid text settings are auto-escaped; `cta_url` uses type `"url"` schema setting (Shopify validates/sanitizes).

## Self-Check: PASSED

- sections/hero.liquid exists: FOUND
- sections/ticker.liquid exists: FOUND
- Commit 6ac3e1d exists: FOUND
- Commit f7e2951 exists: FOUND
