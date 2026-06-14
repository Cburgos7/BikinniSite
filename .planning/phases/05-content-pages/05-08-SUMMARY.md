---
phase: 05-content-pages
plan: "08"
subsystem: templates
tags: [templates, routing, json, shopify]
dependency_graph:
  requires: [05-01, 05-02, 05-03, 05-04, 05-05, 05-06, 05-07]
  provides: [all-content-page-routes]
  affects: []
tech_stack:
  added: []
  patterns: [shopify-json-template]
key_files:
  created:
    - templates/page.about.json
    - templates/page.models.json
    - templates/page.payment.json
    - templates/page.sizeguide.json
    - templates/page.affiliates.json
    - templates/page.social.json
    - templates/page.contact.json
    - templates/page.faq.json
    - templates/page.shipping-returns.json
    - templates/page.privacy-policy.json
    - templates/page.terms-of-service.json
    - templates/page.care-instructions.json
  modified: []
decisions: []
metrics:
  duration: "5m"
  completed: "2026-06-14"
  tasks_completed: 2
  files_created: 12
---

# Phase 05 Plan 08: Wire All 12 JSON Page Templates Summary

**One-liner:** 12 Shopify JSON page templates wired to route each content page URL to its dedicated Wave 1 Liquid section.

## What Was Built

Two batches of JSON page templates created in `templates/`:

- **8 unique content templates** — each routes to its own dedicated section (page-about, page-models, page-payment, page-sizeguide, page-affiliates, page-social, page-contact, page-faq)
- **4 shared policy templates** — all route to the single `page-content` section; merchant assigns content per-page in Shopify admin

All 12 templates follow the standard Shopify JSON template schema with a single `"main"` section entry and `"order": ["main"]`.

## Task Commits

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Create 8 unique content page templates | 503de8b | templates/page.about.json, page.models.json, page.payment.json, page.sizeguide.json, page.affiliates.json, page.social.json, page.contact.json, page.faq.json |
| 2 | Create 4 policy page templates | 9fd2324 | templates/page.shipping-returns.json, page.privacy-policy.json, page.terms-of-service.json, page.care-instructions.json |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None. All templates are complete wire-ups to existing sections. Policy page content is merchant-provided via Shopify admin (by design).

## Threat Flags

None. All section type values are hardcoded strings pointing to known section files; no user input involved.

## Self-Check: PASSED

All 12 template files confirmed created. Both commits verified in git log.
