# Phase 4: Collections & Product Detail - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-14
**Phase:** 04-collections-product-detail
**Areas discussed:** Filtering & sorting, Product card design, PDP layout & gallery, Collection page structure

---

## Filtering & Sorting

| Option | Description | Selected |
|--------|-------------|----------|
| Left sidebar (desktop) | Sticky left column on desktop, slide-in drawer on mobile | ✓ |
| Top filter bar | Horizontal row of dropdowns above the grid | |
| You decide | Claude picks based on brand aesthetic | |

| Option | Description | Selected |
|--------|-------------|----------|
| Shopify native URL filters | Uses /collections/X?filter.p.tag=Y params | ✓ |
| JS-only client-side filter | Hide/show cards with Vanilla JS | |
| You decide | Claude picks most practical approach | |

| Option | Description | Selected |
|--------|-------------|----------|
| Shopify defaults | Featured, Best selling, A-Z, Z-A, Price low-high, Price high-low, Newest | ✓ |
| Curated subset | Just: Featured, Newest, Price low-high, Price high-low | |
| You decide | Claude picks for fashion store | |

| Option | Description | Selected |
|--------|-------------|----------|
| Instant (AJAX) | Results update without page reload | ✓ |
| On apply / page reload | Shopify reloads page with new URL params | |

**Notes:** Shopify Search & Discovery app required for native faceted filtering.

---

## Product Card Design

| Option | Description | Selected |
|--------|-------------|----------|
| Colored dots below the image | Clicking swaps card image to that color's variant | ✓ |
| Dots only — no image swap | Visual indicators only | |
| No swatches on cards | Color selection on PDP only | |

| Option | Description | Selected |
|--------|-------------|----------|
| Heart icon — visual only | Saves to localStorage | |
| Heart icon — requires account | Saves to customer Shopify account wishlist | ✓ |
| Skip wishlist for now | Defer to v2 | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — create a shared snippet | snippets/product-card.liquid used everywhere | ✓ |
| No — collection cards only | Home page cards stay minimal | |

**Notes:** Phase 3 home page sections (featured-products, new-arrivals) will be updated to use the shared snippet.

---

## PDP Layout & Gallery

| Option | Description | Selected |
|--------|-------------|----------|
| Main image + thumbnail strip | Large main + scrollable thumbnails, click to swap, click main for lightbox | ✓ |
| Swipe-only carousel | Single image, swipe left/right | |
| Main image + lightbox only | No thumbnails | |

| Option | Description | Selected |
|--------|-------------|----------|
| Shopify native variant selectors | Standard select/radio tied to variant IDs | ✓ |
| Custom styled buttons | Pill buttons + circles with custom JS | |

| Option | Description | Selected |
|--------|-------------|----------|
| One open at a time | Clicking closes any open accordion | ✓ |
| Multiple can be open | Each toggles independently | |

---

## Collection Page Structure

| Option | Description | Selected |
|--------|-------------|----------|
| One shared template | Single templates/collection.json for all collections | ✓ |
| Separate templates | Separate files per collection | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — editable per collection | Hero pulling from collection.image + hero_subtitle metafield | ✓ |
| No — straight to grid | Skip hero, start at filters | |

---

## Claude's Discretion

- Product grid column count and gap at each breakpoint
- Thumbnail strip orientation (below vs side) and max thumbnail count
- Lightbox implementation (native dialog recommended)
- Filter sidebar width and mobile drawer animation
- Accordion animation approach
- Empty collection state copy and CTA

## Deferred Ideas

None — discussion stayed within phase scope.
