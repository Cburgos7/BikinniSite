---
phase: 05-content-pages
plan: "07"
subsystem: content-pages
tags: [liquid, policy, page-content, sections]
dependency_graph:
  requires: []
  provides: [sections/page-content.liquid]
  affects: [policy page templates]
tech_stack:
  added: []
  patterns: [Shopify page object, Liquid section schema, Tailwind prose wrapper]
key_files:
  created:
    - sections/page-content.liquid
  modified: []
decisions:
  - "page.content rendered without | escape — Shopify pre-sanitizes rich text (same trust boundary as product.description)"
  - "page.title uses | escape — plain text string, not sanitized HTML"
  - "No settings in schema — all content from page.* object; merchant edits in Shopify page editor"
metrics:
  duration: "< 5 minutes"
  completed: "2026-06-14"
  tasks_completed: 1
  tasks_total: 1
  files_changed: 1
---

# Phase 05 Plan 07: Shared Policy Section — page-content.liquid Summary

Single shared Liquid section rendering `page.title` as H1 and `page.content` as pre-sanitized rich text inside a `max-w-3xl` prose wrapper, per D-07 spec.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Build page-content.liquid | ced8808 | sections/page-content.liquid |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- sections/page-content.liquid: FOUND
- commit ced8808: FOUND
