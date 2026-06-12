---
phase: 02-global-shell
plan: 05
subsystem: global-shell
tags: [ccpa, cookie-consent, 404, compliance, liquid, vanilla-js]
dependency_graph:
  requires: [02-03, 02-04]
  provides: [cookie-consent-banner, 404-page]
  affects: [layout/theme.liquid]
tech_stack:
  added: []
  patterns: [localStorage persistence, slide-out CSS transition, Shopify JSON template]
key_files:
  created:
    - sections/cookie-consent.liquid
    - assets/cookie-consent.js
    - sections/not-found.liquid
  modified:
    - templates/404.json
    - layout/theme.liquid
decisions:
  - CCPA banner starts visible (translate-y-0) on first visit; JS adds translate-y-full to animate dismiss
  - Banner hides on DOMContentLoaded if localStorage key already set — no flash on returning visits
  - 404 uses Shopify JSON template format pointing to not-found section type
  - Decorative 404 numeral uses aria-hidden="true"; semantic meaning carried by h1
metrics:
  duration: ~10 minutes
  completed: 2026-06-11
  tasks_completed: 2
  tasks_total: 2
---

# Phase 2 Plan 05: Cookie Consent Banner and 404 Page Summary

**One-liner:** CCPA cookie consent banner with localStorage persistence and animated dismiss, plus branded 404 page with "took a swim" copy and two CTAs inside the full theme shell.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | CCPA cookie consent banner — section + JS module | b16f9ae | sections/cookie-consent.liquid, assets/cookie-consent.js, layout/theme.liquid |
| 2 | Build 404 template and not-found section | 24c7358 | templates/404.json, sections/not-found.liquid |

## What Was Built

### Task 1: CCPA Cookie Consent Banner

`sections/cookie-consent.liquid` — fixed bottom bar (`z-[100]`) with `role="complementary"` and `aria-label="Cookie consent"`. Accept button has `bg-coral` styling; Decline button uses `border border-cream` ghost style. Loads `cookie-consent.js` as ES module.

`assets/cookie-consent.js` — on DOMContentLoaded: checks `localStorage.getItem('soleil_noir_cookie_consent')`; if set, immediately animates banner off-screen. Accept handler stores `'accepted'`, Decline stores `'declined'`, both call `dismissBanner()` which adds `translate-y-full` class and after 300ms sets `display: none`. Exports `init` as default.

`layout/theme.liquid` — `{% section 'cookie-consent' %}` added before `</body>`.

### Task 2: 404 Page

`templates/404.json` — Shopify JSON template with `"type": "not-found"` section.

`sections/not-found.liquid` — centered full-screen layout on `bg-cream`. Decorative `404` numeral (`font-display text-[12rem] text-sand aria-hidden`), `<h1>Page Not Found</h1>`, brand copy "Looks like this page took a swim.", two CTA links: "BACK TO SHOP" (`bg-coral`) → `/` and "VIEW COLLECTIONS" (`border border-deep`) → `/collections/all`.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — both sections are fully wired. The 404 CTAs link to live Shopify routes (`/` and `/collections/all`).

## Threat Flags

None — no new network endpoints or trust boundaries introduced. localStorage stores only the strings "accepted" or "declined" (no PII).

## Self-Check: PASSED

- sections/cookie-consent.liquid: exists, contains `id="cookie-consent-banner"`, Accept/Decline buttons, role/aria attributes, schema
- assets/cookie-consent.js: exists, contains `export default`, localStorage get/set, translate-y-full animation
- layout/theme.liquid: contains `{% section 'cookie-consent' %}`
- templates/404.json: exists, contains `"type": "not-found"`
- sections/not-found.liquid: exists, contains "took a swim", font-display, aria-hidden, schema
- Commits b16f9ae and 24c7358 verified in git log
