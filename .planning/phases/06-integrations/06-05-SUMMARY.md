---
plan: 06-05
phase: 06-integrations
subsystem: image-optimization
tags: [cloudinary, liquid, images, performance]
dependency_graph:
  requires: []
  provides: [cloudinary-img-snippet]
  affects: [snippets/product-card.liquid, sections/product-main.liquid]
tech_stack:
  added: []
  patterns: [cloudinary-fetch-url, liquid-snippet-render]
key_files:
  created:
    - snippets/cloudinary-img.liquid
  modified:
    - snippets/product-card.liquid
    - sections/product-main.liquid
    - assets/pdp.js
decisions:
  - Wrap Cloudinary snippet in div wrapper on PDP main image to preserve JS id/data targets
  - Use span wrappers for thumbnail elements to preserve data-thumbnail JS selector
metrics:
  duration: ~15min
  completed: 2026-06-17
---

# Phase 06 Plan 05: Cloudinary Image Optimization Summary

**One-liner:** Reusable `cloudinary-img.liquid` snippet routes product card and PDP gallery images through Cloudinary fetch-URL with f_auto,q_auto,w_ transforms, falling back to raw Shopify CDN when cloud name is unset.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Create snippets/cloudinary-img.liquid | 6c9d84a | snippets/cloudinary-img.liquid |
| 2 | Apply cloudinary-img to product cards and PDP gallery | 6c9d84a | snippets/product-card.liquid, sections/product-main.liquid |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed pdp.js DOM targeting after img-to-wrapper refactor**

- **Found during:** Task 2
- **Issue:** The PDP main image was previously a bare `<img id="pdp-main-image">`. Wrapping it in a `<div>` for the cloudinary-img snippet broke `pdp.js` which called `.src` and `.alt` directly on the element returned by `getElementById('pdp-main-image')`. Also `data-lightbox-trigger` was on the old `<img>` and needed to move to the wrapper div.
- **Fix:** Updated `pdp.js` `initGallery`, `initLightbox`, and `initColorSwatches` to use `mainImageWrap.querySelector('img')` when reading/writing `.src`/`.alt`. Moved `data-lightbox-trigger` to the wrapper `<div>`. Thumbnail `<img>` elements were replaced with `<span>` wrappers preserving `data-thumbnail` and `data-full-src` attributes — JS already read these via `dataset`, so no change needed there.
- **Files modified:** assets/pdp.js
- **Commit:** 6c9d84a

## Verification Results

All 5 verification checks passed:
1. `snippets/cloudinary-img.liquid` exists
2. `res.cloudinary.com` present in snippet (count: 1)
3. `cloudinary_cloud_name` present in snippet (count: 4)
4. `cloudinary-img` render call in `product-card.liquid` (count: 1)
5. `cloudinary-img` render calls in `product-main.liquid` (count: 3 — main + desktop thumbnails + mobile thumbnails)

## Known Stubs

None.

## Threat Flags

None. No new network endpoints, auth paths, or trust-boundary changes introduced. Cloudinary fetch-URL pattern uses only public Shopify CDN URLs.

## Self-Check: PASSED

- snippets/cloudinary-img.liquid: FOUND
- commit 6c9d84a: FOUND
