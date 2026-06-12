---
phase: 03-home-page
plan: "05"
subsystem: testimonials-section
tags: [liquid, vanilla-js, carousel, social-proof, home-page]
dependency_graph:
  requires: [03-01, 03-02]
  provides: [testimonials-section, testimonial-carousel-js]
  affects: [home-page-layout]
tech_stack:
  added: []
  patterns: [liquid-block-schema, json-data-handoff, es-module-named-export, intersection-observer]
key_files:
  created:
    - sections/testimonials.liquid
    - assets/testimonial-carousel.js
  modified: []
decisions:
  - Used `export function init` named export (not default export) per plan spec, despite mobile-nav.js using a default export
  - JSON data handoff via script#testimonial-data — Liquid json filter escapes all block settings before embedding (T-03-14)
  - textContent used exclusively for DOM writes in JS — no innerHTML (T-03-15)
  - IntersectionObserver with threshold 0 gates the setInterval — timer never runs off-screen (T-03-16)
  - startTimer guard (timer !== null check) prevents duplicate intervals on rapid viewport re-entries
metrics:
  duration: "~10 minutes"
  completed: "2026-06-12"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 0
---

# Phase 03 Plan 05: Testimonials Carousel Section Summary

**One-liner:** Block-based testimonials carousel with Vanilla JS ES module — auto-rotating quotes, IntersectionObserver timer gating, hover-pause, and opacity-fade dot sync.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Build Testimonials Liquid section (HOME-07) | 45bdd74 | sections/testimonials.liquid |
| 2 | Build testimonial-carousel.js ES module (HOME-07 JS) | 61459a5 | assets/testimonial-carousel.js |

## What Was Built

### sections/testimonials.liquid

- Outer section `id="testimonial-section"` with `bg-sand py-16 md:py-20`
- Heading with `section.settings.heading` (default: "What She Said")
- Blockquote `id="testimonial-quote"` with font-display italic styling and opacity transition
- Author `id="testimonial-author"` with optional location span (only rendered when `!= blank`)
- Decorative `&ldquo;` / `&rdquo;` gold quote marks (`text-gold font-display text-6xl`)
- Dot container `id="testimonial-dots"` with `data-count="{{ section.blocks.size }}"` (JS builds buttons)
- JSON data block `id="testimonial-data"` — all block settings piped through Liquid `json` filter (XSS safe)
- Schema: name "Testimonials", max_blocks 6, block type "testimonial" with textarea quote, text author, text location
- ES module loading: standalone `<script type="module">` import + `init()` call pattern

### assets/testimonial-carousel.js

- Named export `init()` — no default export
- Reads and parses JSON from `#testimonial-data`; exits early if fewer than 2 quotes
- Builds dot buttons dynamically (aria-label, active/inactive classes)
- `showQuote(index)`: opacity-0 fade-out → 500ms setTimeout → textContent update → opacity-0 removal
- Author rendering: `document.createTextNode` + optional `<span>` for location (pure textContent, no innerHTML)
- Auto-rotate: `setInterval(next, 5000)` with duplicate-interval guard
- `IntersectionObserver` on sectionEl: `startTimer()` on enter, `stopTimer()` on exit
- Hover: mouseenter → stopTimer, mouseleave → startTimer
- Touch: touchstart → stopTimer (passive), touchend → startTimer (passive)

## Deviations from Plan

None — plan executed exactly as written.

The plan noted the mobile-nav.js pattern as "named exports only"; the actual file uses `export default`. For testimonial-carousel.js, the plan spec (`export function init`) was followed as written — the named export is the correct pattern per plan requirement.

## Threat Model Compliance

| Threat ID | Mitigation Applied |
|-----------|--------------------|
| T-03-14 | All block settings emitted via Liquid `json` filter in script#testimonial-data |
| T-03-15 | JS uses `textContent` and `createTextNode` exclusively — no innerHTML anywhere |
| T-03-16 | `IntersectionObserver` gates setInterval; `stopTimer` called on mouseleave and touchstart |
| T-03-17 | No package installs; pure Liquid + Vanilla JS |

## Known Stubs

None — section renders first block's quote/author/location as server-side default; JS takes over for rotation.

## Threat Flags

None — no new network endpoints, auth paths, or trust boundaries introduced.

## Self-Check

- [x] sections/testimonials.liquid exists and contains `{% schema %}`
- [x] assets/testimonial-carousel.js exists and contains `export function init`
- [x] Commits 45bdd74 and 61459a5 exist in git log
- [x] No innerHTML usage in JS
- [x] No external imports in JS
