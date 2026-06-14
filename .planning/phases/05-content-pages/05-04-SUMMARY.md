---
phase: 05-content-pages
plan: "04"
subsystem: affiliates
tags: [liquid, affiliates, tier-cards, upromote, iframe]
dependency_graph:
  requires: []
  provides: [sections/page-affiliates.liquid]
  affects: []
tech_stack:
  added: []
  patterns: [D-10 hero, D-03 tier cards, iframe embed with fallback]
key_files:
  created:
    - sections/page-affiliates.liquid
  modified: []
decisions:
  - "Tier card content hardcoded per copywriting contract — no merchant-editable perk lists needed at launch"
  - "upromote_url rendered with | escape on both iframe src and fallback href (T-05-04-01, T-05-04-02)"
metrics:
  duration: "~5 minutes"
  completed: "2026-06-14"
---

# Phase 05 Plan 04: Affiliates Page Summary

**One-liner:** Affiliates page with D-10 hero, three D-03 commission tier cards (Standard 10% / Silver 12% / Gold 15% inverted), and UpPromote iframe embed with apply-button fallback.

## What Was Built

`sections/page-affiliates.liquid` — single file implementing the full affiliates page layout:

- **D-10 Hero:** `bg-deep text-cream py-16 lg:py-24`, H1 in Cormorant Garamond, conditional subtitle in `text-cream/60`
- **Tier cards grid:** `grid-cols-1 md:grid-cols-3 gap-6` with three hardcoded cards per D-03 spec
  - Standard (10%): `bg-sand border border-deep/10 p-6`
  - Silver (12%): `bg-sand border border-deep/20 p-6 ring-1 ring-mid`
  - Gold (15%): `bg-deep text-cream p-6` (inverted), perks in `text-cream/80`
  - Commission % on all cards: `font-display text-5xl font-normal text-coral`
- **UpPromote embed:** `<iframe ... min-h-[600px] loading="lazy">` when `upromote_url` is set; fallback `<a>` apply button when blank
- **Schema:** `heading`, `subtitle`, `upromote_url` settings; preset "Affiliates Page"
- **Security:** `| escape` applied to `upromote_url` on both iframe src and fallback href

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Build page-affiliates.liquid | 9923a67 | sections/page-affiliates.liquid |

## Deviations from Plan

None — plan executed exactly as written.

## Threat Surface Scan

No new trust boundaries beyond those documented in the plan threat model (T-05-04-01 through T-05-04-03). All mitigations applied.

## Self-Check: PASSED

- `sections/page-affiliates.liquid` exists: FOUND
- Commit 9923a67 exists: FOUND
- `{% schema %}`: 1 match
- `bg-deep text-cream py-16 lg:py-24`: 1 match
- `grid-cols-1 md:grid-cols-3 gap-6`: 1 match
- `text-5xl font-normal text-coral`: 3 matches (one per tier)
- `bg-deep text-cream p-6`: 1 match (Gold inverted)
- `upromote_url`: 4 matches
- `min-h-[600px]`: 1 match
- `| escape`: 4 matches
