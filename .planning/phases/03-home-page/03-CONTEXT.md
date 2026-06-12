# Phase 3: Home Page - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the complete home page — all 9 content sections from hero to sizing banner — as Shopify Liquid sections wired into `templates/index.json`. Every section must be editable in the Shopify theme editor without touching code. Sections must render correctly at 375px, 768px, and 1280px.

This phase does NOT include: collection pages, PDP, content pages (about, models, etc.), or any integrations. Those are Phases 4–6.

</domain>

<decisions>
## Implementation Decisions

### Hero Section (HOME-01)
- **D-01:** Split layout — image on the left (50–60% width), headline + subheadline + CTA on the right. Image is a theme-editor upload (no placeholder required — section renders gracefully with a `--sand` background if no image set).
- **D-02:** Text area: headline (Cormorant Garamond, large), subheadline (Barlow Condensed, smaller), single CTA button.
- **D-03:** CTA button style: solid coral fill (`bg-coral text-cream`). High contrast, conversion-focused.
- **D-04:** Hero image and all text (headline, subheadline, CTA label, CTA URL) are owner-editable via theme editor settings.

### Section Order (HOME-01 through HOME-09)
- **D-05:** Confirmed order in `templates/index.json`:
  1. Hero (HOME-01)
  2. Ticker / marquee (HOME-02)
  3. Category grid (HOME-03)
  4. Featured products — "Best Sellers" collection (HOME-04)
  5. Social feed strip (HOME-05)
  6. Brand promise strip (HOME-06)
  7. Testimonials (HOME-07)
  8. New arrivals (HOME-08)
  9. Sizing banner (HOME-09)

### Social Feed Strip (HOME-05)
- **D-06:** Horizontal scroll strip — 4–6 square cards in a row, scrollable on mobile. Pulls from `social_post` metaobjects defined in Phase 2.
- **D-07:** Shoppable card interaction: image at rest, on hover a dark overlay appears with a "Shop [Product Name] →" link. The link goes to the product variant from the `social_post.product` metafield (Product variant reference).
- **D-08:** If `social_post.product` is null, the card still displays without a shop overlay (graceful degradation).

### Testimonials (HOME-07)
- **D-09:** Owner-editable via theme editor blocks — each quote is a block with `quote`, `author`, and optional `location` fields. Maximum 6 blocks.
- **D-10:** Auto-rotating carousel — one quote visible at a time, cycles every 5 seconds. Vanilla JS ES module (same pattern as mobile-nav.js). Pause on hover.

### Claude's Discretion
- Ticker/marquee animation speed and content (default brand promises: "Dare to Bare · Inclusive Sizing XXS–3XL · New Drops Weekly · US-Based · Free Shipping Over $75")
- Category grid layout (how many columns, which collections to feature — likely Bikinis, Lingerie, New In, Sale)
- Brand promise strip icon/copy choices
- New arrivals section — pull from newest products or a specific collection; number to show (suggest 4 or 8)
- Sizing banner layout — size pills (XXS S M L XL 1X 2X 3X) with link to `/pages/size-guide`
- Exact breakpoint behavior for each section

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — brand context, constraints, US compliance, tech stack decisions
- `.planning/REQUIREMENTS.md` — HOME-01–09 (Phase 3 requirements)

### Design & Patterns
- `buildSpec.md` §1 — design token values and tech stack spec
- `.planning/phases/01-theme-foundation/01-CONTEXT.md` — Phase 1 locked decisions (Tailwind utility classes, Vanilla JS only, self-hosted fonts, section/block JSON schemas)
- `.planning/phases/02-global-shell/02-CONTEXT.md` — Phase 2 patterns (dark nav aesthetic, ES module pattern, section schema pattern)

### Existing Theme Files (read before implementing)
- `layout/theme.liquid` — page shell; home page sections go into `templates/index.json`, rendered via `{{ content_for_layout }}`
- `sections/announcement-bar.liquid` — reference for section + schema pattern
- `sections/header.liquid` — reference for ES module loading pattern
- `sections/cart-drawer.liquid` — reference for JS module + Liquid data handoff pattern

### Metaobject Schema (Phase 2 output)
- `social_post` metaobject has fields: `image`, `caption`, `link`, `product` (Product variant reference)
- Access in Liquid: `{% for post in shop.metaobjects.social_post.values %}`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `assets/mobile-nav.js` — ES module pattern with `init()` export; follow for carousel JS
- `assets/cart-drawer.js` — Ajax + DOM update pattern; reference for any async section behavior
- `sections/announcement-bar.liquid` — horizontal marquee/ticker already implemented; reuse or extend for HOME-02

### Established Patterns
- Tailwind utility classes used directly in Liquid markup (no CSS component classes)
- `bg-deep text-cream` / `bg-cream text-deep` for dark/light panels
- `font-display` = Cormorant Garamond (headings), `font-body` = Barlow Condensed (body/UI)
- Each JS feature = one ES module in `assets/`, loaded via `<script type="module" src="...">` at section level
- `{% schema %}` JSON block on every section for theme editor editability
- Theme editor image uploads use `{{ section.settings.image | image_url: width: N | image_tag }}`

### Integration Points
- `templates/index.json` — home page template; each section added to `sections` map and `order` array
- `social_post` metaobjects from Phase 2 admin setup feed the social strip section
- "Best Sellers" Shopify collection (created in Phase 2 placeholder setup) feeds featured products

</code_context>

<specifics>
## Specific Ideas

- Hero: if no image uploaded, `--sand` background keeps the split layout from breaking
- Ticker: reuse or extend `announcement-bar.liquid` marquee approach — same CSS animation, different content
- Social strip hover overlay: `group` Tailwind class on card, `group-hover:opacity-100` on overlay
- Testimonial carousel: IntersectionObserver to start/stop animation when section is in view (battery-friendly)
- Sizing banner: size pills as `<span>` elements styled with `border border-deep/20 px-3 py-1 font-body text-sm`

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-home-page*
*Context gathered: 2026-06-11*
