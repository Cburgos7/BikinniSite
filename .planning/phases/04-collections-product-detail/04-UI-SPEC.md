---
phase: 4
slug: collections-product-detail
status: draft
shadcn_initialized: false
preset: none
created: 2026-06-14
---

# Phase 4 — UI Design Contract

> Visual and interaction contract for Collections & Product Detail. Generated from discuss-phase decisions, Tailwind design tokens, and existing theme patterns.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none (Shopify Liquid + Tailwind utility classes) |
| Preset | not applicable |
| Component library | none (Vanilla JS, no framework) |
| Icon library | Inline SVG only — no icon library dependency |
| Font (display) | Cormorant Garamond, Georgia, serif — `font-display` |
| Font (body/UI) | Barlow Condensed, Arial, sans-serif — `font-body` |

---

## Spacing Scale

Declared values (multiples of 4, mapped to Tailwind spacing):

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| xs | 4px | p-1 / gap-1 | Icon gaps, swatch ring offset, inline micro-spacing |
| sm | 8px | p-2 / gap-2 | Compact element padding, swatch gap, badge padding |
| md | 16px | p-4 / gap-4 | Card internal padding, form field spacing |
| lg | 24px | p-6 / gap-6 | Section horizontal padding (mobile), filter group gap |
| xl | 32px | p-8 / gap-8 | Section horizontal padding (desktop), card grid gap |
| 2xl | 48px | p-12 / gap-12 | Section vertical padding, PDP content block gap |
| 3xl | 64px | p-16 / gap-16 | Page-level top/bottom padding, hero section padding |

Exceptions: collection hero banner uses `py-24` (96px) to provide breathing room around collection name and subtitle.

---

## Typography

All sizes are Tailwind utility classes. Cormorant Garamond is editorial/display only; Barlow Condensed handles all UI, body, and label text.

| Role | Size | Tailwind | Weight | Line Height | Font | Usage |
|------|------|----------|--------|-------------|------|-------|
| Body | 14px | text-sm | 400 | 1.5 | font-body | Product descriptions, accordion content, filter labels |
| Label | 12px | text-xs | 500 | 1.2 | font-body | Color swatch label, size option text, badge text, price |
| UI / Button | 13px | text-xs tracking-widest uppercase | 600 | 1 | font-body | "ADD TO CART", "QUICK ADD", filter drawer header |
| Subheading | 18px | text-lg | 400 | 1.2 | font-body | Accordion header, product card title, filter section label |
| Heading | 28px | text-3xl | 400 | 1.1 | font-display | PDP product name, collection page H1 |
| Display | 48px | text-5xl | 300 | 1.0 | font-display | Collection hero banner headline |

Typography exceptions:
- Price: `text-sm font-body font-semibold tracking-wide` (14px, 600 weight)
- Compare-at price (strikethrough): `text-xs font-body text-mid line-through`
- Metafield accordion body: `text-sm font-body leading-relaxed text-mid`

---

## Color

| Role | Token | Hex | Usage |
|------|-------|-----|-------|
| Dominant (60%) | cream | #faf6f0 | Page background, product card background, PDP main area |
| Secondary (30%) | deep | #0d0a08 | All body text, nav bar, footer, borders, primary button background |
| Surface | sand | #f5ede0 | Filter sidebar background, accordion background, active filter chip background |
| Mid | mid | #8a7060 | Secondary text (meta, sold-out labels, accordion body text) |
| Accent primary | coral | #e85d3a | Active filter dot indicator, sale badge, wishlist filled heart, "New" badge |
| Accent secondary | gold | #c9a84c | Star rating icons, price highlight on hover (optional, non-blocking) |
| Destructive | deep | #0d0a08 | Destructive actions use deep background with cream text (no separate red — brand consistency) |

Accent reserved for: active filter state indicator, sale/new product badges, wishlisted heart fill, sold-out strikethrough accent. Never used for body text or decorative backgrounds.

Color usage rules:
- Primary CTA "Add to Cart": `bg-deep text-cream` — deep background, cream text, no coral (brand hierarchy)
- Secondary / ghost button: `border border-deep text-deep` — outlined
- Filter checkbox checked: `accent-coral` or custom SVG checkmark in coral
- Sold-out size option: `text-mid line-through opacity-50`
- Collection hero: `bg-deep text-cream` overlay on collection image

---

## Copywriting Contract

### Collection Page

| Element | Copy |
|---------|------|
| Collection hero headline | Use `collection.title` (owner-set in Shopify admin) |
| Collection hero subtitle | Use `collection.metafields.custom.hero_subtitle` |
| Empty collection heading | "Nothing here yet" |
| Empty collection body | "New drops land every week — check back soon." |
| Filter panel heading | "Filter" |
| Filter clear all | "Clear all" |
| Filter apply (mobile drawer) | "Show Results" |
| Active filter close | "×" (aria-label: "Remove [filter name] filter") |
| Sort label | "Sort by" |
| Product count | "{N} products" / "1 product" |

### Product Card

| Element | Copy |
|---------|------|
| Quick-add button | "Quick Add" |
| Sold-out badge | "Sold Out" |
| Sale badge | "Sale" |
| New badge | "New" |
| Wishlist add (aria-label) | "Add [product title] to wishlist" |
| Wishlist remove (aria-label) | "Remove [product title] from wishlist" |
| Color swatch (aria-label) | "[color name]" |

### Product Detail Page (PDP)

| Element | Copy |
|---------|------|
| Primary CTA | "Add to Cart" |
| CTA (sold out) | "Sold Out" |
| CTA (select size prompt) | "Select a Size" (disabled state until size chosen) |
| Size guide link | "Size Guide" |
| Variant unavailable | "[Size] is sold out" (inline below size selector) |
| Lightbox close (aria-label) | "Close image" |
| Thumbnail (aria-label) | "View image [N] of [total]" |
| Metafield accordion — care | "Care Instructions" |
| Metafield accordion — fabric | "Fabric Composition" |
| Metafield accordion — coverage | "Coverage Level" |
| Metafield accordion — model sizing | "Model Sizing" |
| Accordion expand (aria-label) | "Expand [section name]" |
| Accordion collapse (aria-label) | "Collapse [section name]" |

### Error States

| Element | Copy |
|---------|------|
| No filters match | "No products match these filters. Try adjusting or clearing your filters." |
| Add to cart error | "Something went wrong. Please try again." |
| Wishlist error (not logged in) | "Log in to save items to your wishlist." |

---

## Interaction Contracts

### Product Grid & Filtering (D-03, D-04, D-05, D-06)

- **Grid columns:** 2col mobile (`grid-cols-2`), 3col at lg (`lg:grid-cols-3`), 4col at xl (`xl:grid-cols-4`); gap: `gap-4 lg:gap-6`
- **Filter sidebar (desktop ≥ 1024px):** 240px wide (`w-60`), sticky (`sticky top-20`), `bg-sand`; separator: `border-r border-deep/10`
- **Filter drawer (mobile < 1024px):** full-height slide-in from left, `max-w-[80vw] w-72 bg-sand`, overlay `bg-deep/40`; open/close: `translate-x-0` / `-translate-x-full transition-transform duration-300`
- **AJAX filter swap:** fetch `/collections/[handle]?[params]&section_id=collection-grid`, extract `#shopify-section-collection-grid` innerHTML, swap into `#collection-grid` container; push URL state with `history.pushState`
- **URL param format:** `?filter.p.tag=[style]&filter.v.option.Color=[color]&filter.v.option.Size=[size]&filter.v.price.gte=[min]&filter.v.price.lte=[max]`
- **Active filter chips:** displayed in a flex row below filter button on mobile; each chip shows filter label + "×" to remove

### Product Card (D-07, D-08, D-09, D-10)

- **Card structure:** `relative group overflow-hidden` wrapper; `aspect-[3/4]` image (portrait crop); content below image
- **Quick-add:** `absolute bottom-0 left-0 right-0 translate-y-full group-hover:translate-y-0 transition-transform duration-300 bg-deep text-cream text-center py-3`
- **Color swatches:** `flex gap-1 mt-2`; each dot: `w-3.5 h-3.5 rounded-full border border-deep/20 cursor-pointer`; active state: `ring-2 ring-offset-1 ring-deep`; clicking updates card `<img>` src to color variant's featured image AND updates quick-add `data-variant-id`
- **Wishlist toggle:** `absolute top-3 right-3`; heart SVG 20×20px; default: `text-deep/40`; wishlisted: `text-coral fill-coral`; requires customer login — redirect to `/account/login` if not logged in with return URL

### Product Detail Page (D-11, D-12, D-13, D-14)

- **Image gallery layout (desktop):** `lg:grid lg:grid-cols-[1fr_auto]` — main image left, thumbnail strip right (vertical, `w-16`, scrollable); main image: `aspect-[3/4]`; thumbnails: `w-14 h-14 object-cover cursor-pointer ring-0 hover:ring-2 ring-deep`; active thumbnail: `ring-2 ring-deep`
- **Image gallery layout (mobile):** single scrollable horizontal strip below main image; thumbnails `w-14 h-14 inline-block`
- **Lightbox:** native `<dialog>` element; `showModal()` on main image click; `max-w-[90vw] max-h-[90vh]` image inside; close on backdrop click and Escape key; `::backdrop { background: rgba(13,10,8,0.85) }`
- **Size selector:** radio buttons styled as bordered boxes; `border border-deep/30 px-3 py-2 text-xs font-body uppercase cursor-pointer`; selected: `border-deep bg-deep text-cream`; sold-out: `opacity-40 line-through cursor-not-allowed` + strikethrough
- **Color selector:** same swatch dot pattern as product card; 16×16px dots; clicking a color updates selected `variant_id` and main gallery images
- **Add-to-cart:** `POST /cart/add.js` with JSON body `{id: variantId, quantity: 1}`; on success: dispatch custom event `cart:updated` to trigger cart drawer open (reusing Phase 2 cart-drawer.js pattern); on error: show inline error message
- **Metafield accordions:** `<details>`/`<summary>` elements (or JS-controlled); one open at a time enforced via JS — opening one closes others; expand animation: `max-height: 0 → max-height: {computed}px` with `transition: max-height 300ms ease`; header: `flex justify-between items-center py-4 border-b border-deep/10`

### Breakpoints

| Breakpoint | Width | Key Changes |
|------------|-------|-------------|
| Mobile | 375px–767px | 2-col grid, filter drawer, single-col PDP, horizontal thumbnail strip |
| Tablet | 768px–1023px | 2–3 col grid, filter drawer still, PDP stacks vertically |
| Desktop | 1024px+ | 3–4 col grid, sticky filter sidebar visible, PDP side-by-side layout |

---

## Registry Safety

| Registry | Components Used | Safety Gate |
|----------|----------------|-------------|
| None — Tailwind utility classes only | n/a | n/a |

No third-party component registries. All UI built from Tailwind utilities in Liquid templates. No npm UI packages beyond Tailwind/PostCSS (already installed).

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Flags (non-blocking):**
- Gold hover accent on price is optional — confirm with owner if desired before execution
- Wishlist heart initial hydration (filled state on page load) not fully specified — executor should read `customer.metafields.wishlist` or customer tags on `DOMContentLoaded` and fill hearts for matching product IDs

**Approval:** approved 2026-06-14
