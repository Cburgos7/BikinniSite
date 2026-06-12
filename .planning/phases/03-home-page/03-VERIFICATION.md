---
status: gaps_found
phase: 03-home-page
verified: 2026-06-12
must_haves_checked: 22
must_haves_passed: 20
requirements_covered: [HOME-01, HOME-02, HOME-03, HOME-04, HOME-05, HOME-06, HOME-07, HOME-08, HOME-09]
requirements_missing: []
---

# Verification Report — Phase 03: Home Page

## Must-Haves

| # | Truth | Artifact | Key Link | Result |
|---|-------|----------|----------|--------|
| 1 | Hero section renders a split layout: image left, dark text panel right | sections/hero.liquid | `flex flex-col md:flex-row`, left `md:w-[55%]`, right `bg-deep md:w-[45%]` | PASS |
| 2 | Hero image, headline, subheadline, CTA label, and CTA URL are all editable in theme editor | sections/hero.liquid schema | Settings: image_picker, text×3, url — all 5 settings present | PASS |
| 3 | Hero left panel falls back to bg-sand when no image is uploaded | sections/hero.liquid line 8 | `<div class="w-full h-full bg-sand"></div>` in else branch | PASS |
| 4 | Ticker section displays scrolling brand promise text on a dark background | sections/ticker.liquid | `bg-deep py-3`, `animation: marquee 30s linear infinite`, "Dare to Bare ..." copy | PASS |
| 5 | Ticker animation pauses on mouse hover | sections/ticker.liquid lines 6–8 | CSS rule `#ticker-section:hover #ticker-track { animation-play-state: paused; }` | PASS |
| 6 | Brand promise strip renders 4 promise cards on a dark background | sections/brand-promise.liquid | `bg-deep`, `grid grid-cols-2 md:grid-cols-4 gap-8`, 4-block preset | PASS |
| 7 | Each promise card has an inline SVG icon, heading, and descriptor | sections/brand-promise.liquid lines 7–15 | SVG star in `text-gold`, heading in `font-body ... text-cream`, descriptor in `font-body text-xs text-mid` | PASS |
| 8 | Brand promise cards are owner-editable via theme editor blocks | sections/brand-promise.liquid schema | Block type "promise" with heading+descriptor settings, max_blocks: 4 | PASS |
| 9 | Sizing banner renders size pills XXS through 3X on a dark background | sections/sizing-banner.liquid | `bg-deep`, sizes split/loop, pill spans with correct classes | PARTIAL FAIL — size list default is `"XXS,XS,S,M,L,XL,2X,3X"` (missing `1X`); plan specified `XXS,XS,S,M,L,XL,1X,2X,3X` |
| 10 | Sizing banner links to /pages/size-guide | sections/sizing-banner.liquid line 15 | `href="{{ section.settings.cta_url \| default: '/pages/size-guide' }}"` | PASS |
| 11 | Size pills have correct hover state (border-coral text-coral) | sections/sizing-banner.liquid line 9 | `hover:border-coral hover:text-coral transition-colors cursor-pointer` | PASS |
| 12 | Featured products section pulls from a theme-editor-selected 'Best Sellers' collection | sections/featured-products.liquid | Schema type "collection"; Liquid iterates `section.settings.collection.products` | PASS |
| 13 | Product cards show image (3/4 aspect), title, and price | sections/featured-products.liquid | `aspect-[3/4]`, `product.title`, `product.price \| money` | PASS |
| 14 | Quick-add button slides up from bottom of card on hover | sections/featured-products.liquid lines 26–27 | `translate-y-full group-hover:translate-y-0 transition-transform duration-200` | PASS |
| 15 | New arrivals section pulls from a theme-editor-selected collection (newest products) | sections/new-arrivals.liquid | Schema type "collection"; Liquid iterates `section.settings.collection.products` | PASS |
| 16 | New arrivals has a 'View All New Arrivals →' CTA link below the grid | sections/new-arrivals.liquid lines 46–50 | `view_all_label` setting (default "View All New Arrivals →"), link to `collection.url` | PASS |
| 17 | Both grids are 2 columns on mobile, 4 columns on desktop | sections/featured-products.liquid + new-arrivals.liquid | `grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6` in both | PASS |
| 18 | Social feed renders 4–6 square cards from social_post metaobjects in a horizontal scroll row | sections/social-feed.liquid | Iterates `shop.metaobjects.social_post.values`; cards `w-64 h-64 flex-shrink-0 snap-start`; `overflow-x-auto snap-x snap-mandatory` | PARTIAL FAIL — product URL/title accessed as `post.product.url` / `post.product.title` instead of `post.product.value.product.url` / `post.product.value.product.title` as spec required; may fail at runtime depending on Shopify metaobject reference resolution |
| 19 | Social feed cards show a dark overlay with 'Shop [Product Title] →' on hover when product is linked | sections/social-feed.liquid lines 25–31 | `bg-deep/70 opacity-0 group-hover:opacity-100`; shop link gated on `post.product != blank`; arrow in `text-coral` span | PASS (subject to gap noted in #18) |
| 20 | Social feed cards display without a shop overlay when social_post.product is null | sections/social-feed.liquid | Overlay div always rendered; link inside guarded with `{% if post.product != blank %}` | PASS |
| 21 | Category grid renders 4 collection cards in a 2-to-4 column grid | sections/category-grid.liquid | `grid grid-cols-2 lg:grid-cols-4 gap-4`; 4-block preset with Bikinis/Lingerie/New In/Sale labels | PASS |
| 22 | Category grid cards show a dark overlay with the collection title on hover | sections/category-grid.liquid | `bg-deep/40 group-hover:bg-deep/60 transition-colors duration-300`; label from `block.settings.label \| default: block.settings.collection.title` | PASS |
| 23 | Category cards are owner-configurable (collection picker per card) | sections/category-grid.liquid schema | Block type "category_card" with collection (type: collection) and label (text); max_blocks: 4 | PASS |
| 24 | Testimonials section renders one centered quote at a time on a sand background | sections/testimonials.liquid | `bg-sand py-16 md:py-20`; blockquote `id="testimonial-quote"` with first block's quote as default | PASS |
| 25 | Quotes auto-rotate every 5 seconds | assets/testimonial-carousel.js line 13 + 110 | `INTERVAL_MS = 5000`; `setInterval(next, INTERVAL_MS)` | PASS |
| 26 | Auto-rotation pauses when the user hovers the section | assets/testimonial-carousel.js lines 134–135 | `mouseenter → stopTimer`, `mouseleave → startTimer` | PASS |
| 27 | Dot indicators show which quote is active (coral wide pill) vs inactive (mid small circle) | assets/testimonial-carousel.js lines 10–11 | `ACTIVE_DOT_CLASSES = ['w-4','h-2','bg-coral',...]`, `INACTIVE_DOT_CLASSES = ['w-2','h-2','bg-mid',...]` | PASS |
| 28 | Each testimonial block has quote, author, and optional location fields editable in theme editor | sections/testimonials.liquid schema | Block type "testimonial" with textarea quote, text author, text location | PASS |
| 29 | Maximum 6 testimonial blocks | sections/testimonials.liquid schema | `"max_blocks": 6` | PASS |
| 30 | Carousel uses a Vanilla JS ES module with an exported init() function | assets/testimonial-carousel.js line 25 | `export function init()` — named export; no default export | PASS |
| 31 | templates/index.json order array contains all 9 section keys in the correct order (D-05) | templates/index.json | order: hero, ticker, category-grid, featured-products, social-feed, brand-promise, testimonials, new-arrivals, sizing-banner | PASS |
| 32 | templates/index.json sections map contains a valid entry for each of the 9 sections | templates/index.json | All 9 keys present with correct type values; blocks/block_order present on brand-promise, testimonials, category-grid | PASS |

## Requirements Traceability

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| HOME-01 | Hero section: split layout, headline, sub-headline, primary CTA | COVERED | sections/hero.liquid — split flex layout, 5 schema settings, coral CTA |
| HOME-02 | Ticker / marquee with rotating brand promises | COVERED | sections/ticker.liquid — CSS @keyframes marquee, hover-pause, gold separators |
| HOME-03 | Category grid linking to collection pages | COVERED | sections/category-grid.liquid — 4 block-based collection cards, 2→4 column grid |
| HOME-04 | Featured products section pulling from "Best Sellers" collection | COVERED | sections/featured-products.liquid — collection picker, quick-add card grid |
| HOME-05 | Social media feed block: curated social_post metaobjects as shoppable strip | COVERED (with minor gap) | sections/social-feed.liquid — metaobject iteration, horizontal scroll, product link gating; see gap #2 below |
| HOME-06 | Brand promise strip (fabric quality, sizing, weekly drops, US-based) | COVERED | sections/brand-promise.liquid — 4-block grid, gold SVG icons, dark panel |
| HOME-07 | Editorial / testimonial section | COVERED | sections/testimonials.liquid + assets/testimonial-carousel.js — block-based quotes, auto-rotate, IntersectionObserver |
| HOME-08 | New arrivals section | COVERED | sections/new-arrivals.liquid — collection picker, quick-add grid, view-all CTA |
| HOME-09 | Sizing banner with size pills and link to sizing page | COVERED (with minor gap) | sections/sizing-banner.liquid — pill row, /pages/size-guide CTA; see gap #1 below |

Note: REQUIREMENTS.md still shows HOME-01 through HOME-09 as unchecked (`[ ]`). These should be marked as `[x]` after human verification of the live Shopify preview confirms the phase goal is achieved.

## Gaps

### Gap 1 — Missing size `1X` in sizing-banner default (MINOR)
- **File:** sections/sizing-banner.liquid, line 6
- **Plan spec:** `"XXS,XS,S,M,L,XL,1X,2X,3X"` (9 sizes, per UI-SPEC §HOME-09)
- **Actual default:** `"XXS,XS,S,M,L,XL,2X,3X"` (8 sizes — `1X` omitted)
- **Impact:** Low. The `size_list` is now an owner-editable schema setting, so the owner can correct this in the theme editor without a code change. However the out-of-box default does not match the spec.
- **Recommended fix:** Change the schema default from `"XXS,XS,S,M,L,XL,2X,3X"` to `"XXS,XS,S,M,L,XL,1X,2X,3X"` in `sections/sizing-banner.liquid` line 37.

### Gap 2 — Social feed product link uses simplified metaobject access (UNCERTAIN)
- **File:** sections/social-feed.liquid, lines 27–29
- **Plan spec:** Access product via `post.product.value.product.url` and `post.product.value.product.title`
- **Actual:** `post.product.url` and `post.product.title`
- **Impact:** Uncertain. If `social_post.product` is a product variant reference metafield, Shopify may or may not resolve `.url` and `.title` directly without `.value.product.` traversal. This cannot be verified without a live store with social_post metaobjects populated. If the link renders as blank or throws a nil error, the fix is to restore the `.value.product.` traversal path.
- **Recommended action:** Flag for human verification in the live theme editor once social_post metaobjects are configured (see Human Verification Items below).

### Gap 3 — product_count range schema differs from plan spec (INTENTIONAL DEVIATION)
- **Files:** sections/featured-products.liquid (line 70–76), sections/new-arrivals.liquid (line 72–78)
- **Plan spec:** `min: 4, max: 8, step: 4` (2 stops: 4 and 8)
- **Actual:** `min: 2, max: 8, step: 2` (4 stops: 2, 4, 6, 8)
- **Reason:** Commit `7d5778e` message states "Shopify requires 3+ steps" on a range slider. The plan's `step: 4` would produce only 2 stops (4 and 8), which Shopify rejects. The deviation is intentional and correct.
- **Impact:** None — behavior is functionally equivalent and more flexible.

### Gap 4 — REQUIREMENTS.md checkboxes not updated
- **File:** .planning/REQUIREMENTS.md lines 22–30
- **Status:** HOME-01 through HOME-09 are still marked `[ ]` (unchecked)
- **Impact:** Tracking only. Requirements should be marked `[x]` after human sign-off on the live store.

## Human Verification Items

The following items require a running Shopify store and cannot be verified from source files alone:

| Item | How to Verify |
|------|---------------|
| All 9 sections render in the Shopify theme editor sidebar | Open Customize → confirm all 9 sections are listed and their settings are editable |
| Hero image upload and fallback | In theme editor, set and clear hero image — confirm sand fallback appears correctly |
| Ticker pause on hover | Open home page in browser — hover ticker strip — confirm scrolling stops |
| Featured products / New arrivals product pull | Assign collections in theme editor — confirm products render with correct card layout |
| Social feed product link resolution | Create a `social_post` metaobject with a product variant linked — confirm "Shop [title] →" appears on hover and link navigates correctly (validates Gap 2 above) |
| Social feed empty state | Verify empty-state message appears before any social_post metaobjects are created |
| Testimonials auto-rotation | Add 2+ testimonial blocks in theme editor — confirm 5-second auto-rotation, dot sync, and hover pause |
| Home page responsive layout | Verify at 375px (mobile), 768px (tablet), 1280px (desktop) — hero stacks vertically on mobile, grids collapse to 2 columns |
| Size guide CTA link | Click "View Full Size Guide →" — confirm it routes to /pages/size-guide (or owner-configured URL) |
| Category grid collection assignment | Assign collections to category card blocks in theme editor — confirm images and hover overlays render |
| Quick-add form | Add a product to cart via Quick Add button — confirm Shopify cart updates |

Note: The 03-06-SUMMARY.md records that the human checkpoint for Plan 06 was completed and APPROVED — the owner reviewed the home page on mobile via Shopify preview and confirmed all 9 sections rendered correctly. The items above are listed for completeness and to flag Gap 2 (social feed product link) for targeted re-verification once social_post metaobjects are populated.
