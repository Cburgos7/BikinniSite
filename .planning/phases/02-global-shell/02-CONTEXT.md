# Phase 2: Global Shell - Context

**Gathered:** 2026-06-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Build everything that wraps every page: sticky nav, mobile nav drawer, cart drawer, metaobject/metafield schema definitions, Shopify customer accounts, CCPA cookie banner, 404 page, and empty cart state. Later phases inherit this complete page frame.

Also includes developer environment setup: Shopify Partner account creation, dev store provisioning, and Shopify CLI local preview (`shopify theme dev`) — so the owner can see a live preview of all Phase 2 work before it ships.

</domain>

<decisions>
## Implementation Decisions

### Sticky Nav
- **D-01:** Nav is always visible — no shrink or hide-on-scroll. Fixed to top, same size and style throughout the full page scroll.
- **D-02:** Nav background is solid `--deep` (#0d0a08) at all times. No transparency-over-hero effect.
- **D-03:** Logo uses image-with-text-fallback pattern — theme setting for logo image upload; if not set, falls back to `shop.name` rendered in Cormorant Garamond.
- **D-04:** Search icon expands an inline search bar within the nav row (replaces the nav links area briefly). No overlay, no page navigation.

### Mobile Nav
- **D-05:** Hamburger opens a slide-in drawer from the left side.
- **D-06:** Mobile drawer contains nav links only: New In, Bikinis, Lingerie, Sale. Account and search icons remain in the top bar.
- **D-07:** Mobile drawer background is `--deep` with `--cream` text — matches the nav bar for a cohesive, dramatic brand feel.

### Cart Drawer
- **D-08:** Cart drawer slides in from the right. Triggered only by bag icon click — does NOT auto-open on add-to-cart.
- **D-09:** Free shipping progress bar is included — shows progress toward the $75 free shipping threshold (e.g., "You're $23 away from free shipping!"). Consistent with the announcement bar message.
- **D-10:** Quantity controls are `−` / `+` buttons with live subtotal price update (no page reload). Separate remove button for deletion — minus does not remove on zero.

### CCPA Cookie Banner
- **D-11:** Slim fixed bottom bar — appears immediately on first visit (no delay).
- **D-12:** Two buttons only: Accept and Decline. No manage-preferences panel.
- **D-13:** Consent stored in `localStorage` — once a choice is made the banner never reappears (until localStorage is cleared by the user).

### Dev Environment Setup
- **D-14:** Owner does not yet have a Shopify Partner account or dev store. Phase 2 must include a setup task with step-by-step instructions: create Partner account at partners.shopify.com → create Development store → install Shopify CLI → authenticate CLI → run `shopify theme dev --store=<dev-store>.myshopify.com`.
- **D-15:** Dev store needs placeholder content (2–3 products with variants, a "Best Sellers" collection, at least one each of Bikinis and Lingerie collection) so nav links and cart work realistically during local preview.
- **D-16:** `shopify.theme.toml` already scaffolded in Phase 1; verify it is configured with the dev store environment so `shopify theme dev` works without extra flags.

### Claude's Discretion
- Footer layout and link structure (links will be stubbed — actual policy pages built in Phase 5)
- Metafield definition approach in Shopify admin (type, validation, namespace)
- Shopify account page template styling (standard Shopify native accounts, AUTH-01)
- 404 and empty cart visual design (must use brand tokens and carry brand copy feel)
- Exact HTML/Aria patterns for drawer open/close (focus trap, scroll lock)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — brand context, constraints, US compliance notes, tech stack decisions
- `.planning/REQUIREMENTS.md` — NAV-01–05, META-01–04, AUTH-01 (Phase 2 requirements)

### Design Tokens & Conventions
- `buildSpec.md` §1 — design token values (`--deep`, `--coral`, `--cream`, `--sand`, `--gold`, `--mid`) and tech stack spec
- `.planning/phases/01-theme-foundation/01-CONTEXT.md` — Phase 1 locked decisions (Tailwind utility classes throughout, Vanilla JS only, self-hosted fonts, section/block JSON schemas)

### Existing Theme Files (read before implementing)
- `layout/theme.liquid` — current page shell; nav and footer sections must be added here
- `sections/announcement-bar.liquid` — already implemented; reference its schema pattern
- `sections/header.liquid` — current stub; Phase 2 replaces this

No external specs — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `assets/custom-cursor.js` — Vanilla JS ES module pattern to follow for cart-drawer.js, mobile-nav.js, cookie-consent.js, inline-search.js
- `sections/announcement-bar.liquid` — working section with Tailwind classes and `{% schema %}` block; reference for new section structure

### Established Patterns
- Tailwind utility classes used directly in Liquid markup (no CSS component classes)
- `bg-deep text-cream` / `bg-cream text-deep` are the established dark/light panel pattern
- `font-body` = Barlow Condensed, `font-display` = Cormorant Garamond (from font-faces snippet)
- Each JS feature = one ES module in `assets/`, loaded via `<script type="module">` at section level
- `{% schema %}` JSON blocks on every section for theme editor editability

### Integration Points
- `layout/theme.liquid` — `{{ content_for_layout }}` is inside `<main id="main-content">`; announcement bar + header sections must render above `<main>`, footer below
- Shopify's `cart` object and Ajax Cart API for cart drawer item management
- Shopify customer account routes: `/account`, `/account/login`, `/account/register`, `/account/orders`

</code_context>

<specifics>
## Specific Ideas

- Dev environment: Partner account at partners.shopify.com (free) → Development store (free, unlimited) → `npm install -g @shopify/cli` → `shopify auth login` → `shopify theme dev --store=<store>.myshopify.com`. Preview URL is shareable so owner can review work before it goes live.
- Free shipping threshold of $75 matches announcement bar copy — keep them in sync via a single theme setting
- Mobile drawer close on outside-click and on `Escape` key
- Cart bag icon should show item count badge (number bubble) when cart is non-empty
- CCPA banner: cream text on deep background to match nav; coral accent on Accept button; ghost/outline style for Decline

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-global-shell*
*Context gathered: 2026-06-09*
