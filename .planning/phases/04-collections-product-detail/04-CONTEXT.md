# Phase 4: Collections & Product Detail - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the core shopping flow: Bikinis collection, Lingerie collection, all-products catalog, and the product detail page. One shared collection template drives all three collection pages. The PDP includes image gallery, variant selectors, add-to-cart, and metafield accordions. Product cards get a shared snippet with color swatches and wishlist toggle.

This phase does NOT include: content pages (about, models, affiliates), integrations (Klaviyo, GA4), or any checkout customization.

</domain>

<decisions>
## Implementation Decisions

### Collection Page Structure
- **D-01:** Single shared `templates/collection.json` for Bikinis, Lingerie, and All-Products. All three collections use one template — simpler to maintain.
- **D-02:** Each collection page has a hero banner at the top, pulling from `collection.image`, `collection.description`, and the `hero_subtitle` metafield (defined in Phase 2). Owner edits image and copy in Shopify admin.

### Filtering & Sorting
- **D-03:** Filters live in a sticky left sidebar on desktop; slide-in drawer on mobile.
- **D-04:** Filtering uses Shopify native URL params (`/collections/X?filter.p.tag=Y`). Requires Shopify Search & Discovery app for faceted filters. Filter axes: style, color, size, price.
- **D-05:** Sort options: all Shopify defaults (Featured, Best selling, A-Z, Z-A, Price low-high, Price high-low, Newest).
- **D-06:** Filters update results instantly via AJAX — no full page reload when a filter is ticked. JS fetches updated collection URL and swaps the product grid in the DOM.

### Product Card (Shared Snippet)
- **D-07:** Extract product card into `snippets/product-card.liquid` — one snippet used by collection pages AND Phase 3 home page sections (featured-products, new-arrivals). Phase 3 sections updated to use the snippet.
- **D-08:** Color swatches: colored dots below the product image (12–16px circles). Clicking a dot swaps the card's main image to that color variant's featured image.
- **D-09:** Wishlist toggle: heart icon, requires customer account login. Saves to customer account wishlist via Shopify's customer object. Shows filled heart if already wishlisted.
- **D-10:** Quick-add slide-up on hover (same pattern as Phase 3) — preserved in the shared snippet.

### Product Detail Page (PDP)
- **D-11:** Image gallery: large main image on the left + scrollable thumbnail strip (below or beside). Clicking a thumbnail swaps the main image. Clicking the main image opens a fullscreen lightbox.
- **D-12:** Size and color selectors: Shopify native variant selectors (standard `<select>` or radio buttons tied to variant IDs). Styled to match brand but wired via Shopify's built-in variant selection.
- **D-13:** Metafield accordions (care_instructions, fabric_composition, coverage_level, model_sizing): one open at a time — clicking an accordion closes any currently open one.
- **D-14:** Add-to-cart uses Shopify Ajax Cart API (same as cart-drawer.js pattern from Phase 2) — no page reload on add.

### Claude's Discretion
- Product grid column count and gap at each breakpoint
- Thumbnail strip orientation (below vs side) and max thumbnail count
- Lightbox implementation approach (native dialog or custom overlay)
- Filter sidebar width and animation for mobile drawer
- Accordion animation (height transition vs display toggle)
- Empty collection state copy and CTA

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — brand context, constraints, tech stack
- `.planning/REQUIREMENTS.md` — COLL-01–04, PDP-01–05 (Phase 4 requirements)

### Design & Patterns
- `.planning/phases/01-theme-foundation/01-CONTEXT.md` — locked decisions: Tailwind utilities, Vanilla JS only, section/block schemas
- `.planning/phases/03-home-page/03-CONTEXT.md` — product card patterns, quick-add hover pattern, Tailwind color palette

### Existing Theme Files (read before implementing)
- `sections/featured-products.liquid` — existing product card pattern to extract into snippet
- `sections/new-arrivals.liquid` — second card instance to migrate to shared snippet
- `sections/cart-drawer.liquid` — Ajax Cart API pattern (reuse for PDP add-to-cart)
- `assets/cart-drawer.js` — Ajax fetch + DOM update pattern
- `layout/theme.liquid` — page shell; collection and product templates render via `{{ content_for_layout }}`

### Shopify APIs
- Shopify Search & Discovery app — required for native URL-based faceted filtering (filter.p.tag, filter.v.price, filter.v.option.*)
- Shopify Ajax Cart API (`/cart/add.js`, `/cart/change.js`) — for add-to-cart without reload
- Shopify variant selection — `product.variants`, `variant.id`, `variant.available`

### Metafields (Phase 2 definitions)
- Product metafields: `care_instructions`, `fabric_composition`, `coverage_level`, `model_sizing`
- Collection metafield: `hero_subtitle`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `snippets/product-card.liquid` (to be created) — will be used by collection pages + Phase 3 home sections
- `assets/cart-drawer.js` — Ajax cart pattern; reuse or extend for PDP add-to-cart
- `assets/mobile-nav.js` — ES module pattern with `init()` export; follow for filter drawer JS

### Established Patterns
- Tailwind utility classes directly in Liquid (no separate CSS component classes)
- `bg-deep text-cream` / `bg-sand` / `bg-cream text-deep` for section backgrounds
- `font-display` = Cormorant Garamond (headings), `font-body` = Barlow Condensed (body/UI)
- Each JS feature = one ES module in `assets/`, loaded via `<script type="module">` at section level
- `{% schema %}` block on every section for theme editor editability
- Quick-add: `translate-y-full group-hover:translate-y-0 transition-transform` slide-up pattern

### Integration Points
- `templates/collection.json` — new file; collection sections wire in here
- `templates/product.json` — new file; PDP sections wire in here
- `snippets/product-card.liquid` — referenced from collection section AND Phase 3 home sections
- Phase 2 metafields (`custom.care_instructions` etc.) surface in PDP accordions

</code_context>

<specifics>
## Specific Ideas

- Filter AJAX: fetch `/collections/X?filter.p.tag=Y&section_id=collection-grid` and swap inner HTML of the grid container
- Color swatch dot click: update `data-variant-id` on the card's quick-add button + swap `src` on the card image
- Wishlist heart: check `customer.metafields.wishlist` or use Shopify customer tags as a lightweight store; show filled state on page load if product ID is in wishlist
- Lightbox: native `<dialog>` element with `showModal()` — no library needed, keyboard accessible, backdrop handled by browser
- Accordion: `max-height` transition (0 → auto via JS-set pixel value) for smooth open/close

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-collections-product-detail*
*Context gathered: 2026-06-14*
