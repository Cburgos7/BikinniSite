---
phase: 05-content-pages
plan: "06"
subsystem: content-pages
tags: [contact-form, faq, accordion, liquid, vanilla-js]
dependency_graph:
  requires: []
  provides: [sections/page-contact.liquid, sections/page-faq.liquid, assets/faq.js]
  affects: []
tech_stack:
  added: []
  patterns: [shopify-contact-form, data-accordion, es-module]
key_files:
  created:
    - sections/page-contact.liquid
    - sections/page-faq.liquid
    - assets/faq.js
  modified: []
decisions:
  - "richtext FAQ answers rendered without | escape — Shopify richtext schema type is sanitized by platform (same trust boundary as product.description)"
  - "faq.js is a standalone ES module — does not import from pdp.js to avoid coupling"
metrics:
  duration: "5 minutes"
  completed: "2026-06-14"
  tasks_completed: 2
  tasks_total: 2
  files_created: 3
  files_modified: 0
---

# Phase 5 Plan 06: Contact Form + FAQ Accordion Summary

**One-liner:** Shopify native contact form with XSS-safe field repopulation and a merchant-configurable FAQ accordion using the data-accordion/scrollHeight pattern from pdp.js.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Build page-contact.liquid | 8810f2f | sections/page-contact.liquid |
| 2 | Build page-faq.liquid and faq.js | 1382234 | sections/page-faq.liquid, assets/faq.js |

## What Was Built

### page-contact.liquid
- D-10 page hero section (bg-deep, Cormorant Garamond H1, optional subtitle)
- D-05 Shopify native contact form using `{%- form 'contact' -%}` tag
- Success state: `form.posted_successfully` renders coral confirmation message
- Error state: `form.errors | default_errors` renders coral error list
- Three fields: name (text), email (email), message (textarea rows=5) with correct `contact[*]` names
- All form value repopulation (`form.name`, `form.email`, `form.body`) use `| escape`
- CSRF token included automatically by Shopify `form` tag
- Schema: heading and subtitle settings, "Contact" preset

### page-faq.liquid
- D-10 page hero with configurable heading
- D-06 FAQ accordion container with `divide-y divide-deep/10 border-t border-deep/10`
- Merchant-configurable `faq_item` blocks (limit 20): question (text), answer (richtext)
- Each item: `data-accordion` container, `data-accordion-trigger` button with chevron SVG, `data-accordion-body` div with inline max-height:0 and transition style
- `aria-expanded="false"` initial state; faq.js manages open/close
- Empty state message when no blocks added
- `<script type="module" src="{{ 'faq.js' | asset_url }}">` at end of section
- Schema: heading setting, faq_item block type, "FAQ" preset

### faq.js
- Standalone ES module — no imports from pdp.js
- `initFaqAccordions()` mirrors `initAccordions()` from pdp.js exactly
- `closeAll()` resets all accordions: aria-expanded=false, maxHeight=0, icon rotate(0deg)
- Click handler: closeAll() then open selected via scrollHeight if was closed (toggle behavior)
- `document.addEventListener('DOMContentLoaded', initFaqAccordions)` entry point
- No fetch, no XMLHttpRequest, no innerHTML writes

## Security Review (Threat Model)

| Threat | Disposition | Implementation |
|--------|-------------|----------------|
| T-05-06-01: form field repopulation XSS | mitigate | form.name, form.email, form.body all use \| escape |
| T-05-06-02: CSRF on contact form | mitigate | Shopify form tag includes CSRF token automatically |
| T-05-06-03: richtext answer injection | accept | Shopify richtext schema type sanitized by platform |
| T-05-06-04: faq.js DOM manipulation | accept | Only sets style.maxHeight and aria-expanded — no innerHTML |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — both sections are fully wired. Contact form submits to Shopify. FAQ blocks are merchant-configurable in theme editor.

## Threat Flags

None — no new security surface beyond what the plan's threat model already covers.

## Self-Check: PASSED

- [x] sections/page-contact.liquid exists
- [x] sections/page-faq.liquid exists
- [x] assets/faq.js exists
- [x] Commit 8810f2f exists (page-contact.liquid)
- [x] Commit 1382234 exists (page-faq.liquid + faq.js)
