---
phase: 06-integrations
plan: 06-06
title: Integration verification + env vars + purchase event docs
subsystem: integrations
tags: [klaviyo, ga4, cloudinary, upromote, verification, docs]
dependency_graph:
  requires: [06-01, 06-02, 06-03, 06-04, 06-05]
  provides: [integration-settings-inventory, human-checkpoint-checklist]
  affects: [config/settings_data.json]
tech_stack:
  added: []
  patterns: [placeholder-grep-go-live-check]
key_files:
  created:
    - .planning/phases/06-integrations/06-INTEGRATION-SETTINGS.md
    - .planning/phases/06-integrations/06-HUMAN-CHECKPOINT.md
  modified:
    - config/settings_data.json
decisions:
  - settings_data.json uses PLACEHOLDER strings so owner can grep before go-live
  - GA4 purchase snippet guarded by first_time_accessed to prevent double-counting (T-06-15)
  - 06-CONTEXT.md already contained all required content from prior plan run; no edit needed
metrics:
  duration: 10m
  completed: 2026-06-17
---

# Phase 06 Plan 06: Integration verification + env vars + purchase event docs Summary

**One-liner:** Placeholder integration settings committed to settings_data.json; integration settings inventory and browser verification checklist written for merchant go-live.

## Tasks Completed

| Task | Description | Commit | Status |
|------|-------------|--------|--------|
| 1 | Populate settings_data.json with 4 integration placeholder values | ec66195 | Done |
| 2 | Human checkpoint checklist (browser verification) | c9c11bd | Documented |
| 3 | Update 06-CONTEXT.md with GA4 purchase snippet | — | Already present; no edit needed |

## Verification Results

- `grep -c "PLACEHOLDER" config/settings_data.json` = 3 (>= 3 required) — PASS
- `grep -c "purchase" .planning/phases/06-integrations/06-CONTEXT.md` = 4 (>= 1 required) — PASS

## Deviations from Plan

**1. [Rule 1 - Pre-existing content] Task 3 skipped as already complete**
- Found during: Task 3
- Issue: 06-CONTEXT.md already contained the GA4 purchase snippet, Klaviyo flow documentation, and all content required by Task 3 — added by an earlier plan run.
- Fix: No edit performed; verified with grep.
- Files modified: None

## Human Checkpoint (INT-02 requires real credentials)

Task 2 is a `checkpoint:human-verify`. The 06-HUMAN-CHECKPOINT.md checklist has been written and committed. The owner must:
1. Replace all PLACEHOLDER values with real credentials
2. Run `shopify theme dev`
3. Complete each checkbox in `.planning/phases/06-integrations/06-HUMAN-CHECKPOINT.md`

UpPromote end-to-end (discount code pass-through to Shopify checkout) requires a real UpPromote merchant account and a real Bogus Gateway test order.

## Known Stubs

- `config/settings_data.json` contains 3 intentional PLACEHOLDER strings that must be replaced before go-live. This is by design (threat T-06-14: accepted).

## Self-Check: PASSED

- `F:\CODING\BikinniSite\config\settings_data.json` — FOUND
- `F:\CODING\BikinniSite\.planning\phases\06-integrations\06-INTEGRATION-SETTINGS.md` — FOUND
- `F:\CODING\BikinniSite\.planning\phases\06-integrations\06-HUMAN-CHECKPOINT.md` — FOUND
- Commit ec66195 — FOUND
- Commit c9c11bd — FOUND
