---
phase: 05
slug: content-pages
status: approved
shadcn_initialized: false
preset: none
created: 2026-06-14
---

# Phase 5 — UI Design Contract

> Visual and interaction contract for Phase 5: Content Pages.
> Covers: About, Models, Payment Info, Size Guide, Affiliates, Social UGC, Contact, FAQ, Policy pages.
> Locked by orchestrator (gsd-ui-researcher agent unavailable; synthesized from Phase 4 established patterns + design tokens).

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — Tailwind utility classes only |
| Preset | not applicable |
| Component library | none |
| Icon library | Inline SVG (heroicons shapes, hand-coded) |
| Fonts | Cormorant Garamond (display), Barlow Condensed (body) — self-hosted, preloaded |

**Rules:**
- No `@apply` or custom CSS classes. All styling via Tailwind utility classes inline in Liquid.
- No external component library. Reuse patterns from Phase 3 (sections) and Phase 4 (accordions, forms).
- All Liquid pages are Shopify `page.*` JSON templates routing to a named section.

---

## Spacing Scale

Multiples of 4px — consistent with established Phase 3/4 patterns:

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px (p-1) | Icon gaps, badge padding |
| sm | 8px (p-2) | Compact inline padding |
| md | 16px (p-4) | Default element spacing |
| lg | 24px (p-6) | Card/section internal padding |
| xl | 32px (p-8) | Layout gaps, wide padding |
| 2xl | 48px (py-12) | Section vertical rhythm |
| 3xl | 64px (py-16) | Page-level section breaks |

Page content container: `max-w-screen-xl mx-auto px-4 lg:px-8 py-12 lg:py-16` (matches PDP pattern).
Prose pages (policy, about text blocks): `max-w-3xl mx-auto px-4 py-16`.

Exceptions: none.

---

## Typography

Inheriting roles established in Phase 3/4:

| Role | Class | Usage |
|------|-------|-------|
| Page display heading | `font-display text-5xl lg:text-7xl font-normal leading-tight` | Hero H1 on About, Models, etc. |
| Section heading | `font-display text-3xl font-normal leading-tight text-deep` | Section H2 |
| Sub-heading | `font-display text-2xl font-normal text-deep` | Card names, accordion headers |
| Body copy | `font-body text-sm text-mid leading-relaxed` | Paragraphs, captions |
| Label / eyebrow | `font-body text-xs uppercase tracking-widest text-deep` | Labels, tags, eyebrow text |
| CTA / button | `font-body text-xs tracking-widest uppercase` | All button text |

---

## Color

60/30/10 contract — matches site-wide palette:

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `cream` `#faf6f0` | Page backgrounds, card fills |
| Secondary (30%) | `deep` `#0d0a08` | Text, nav, hero backgrounds, button fills |
| Accent (10%) | `coral` `#e85d3a` | Primary CTAs, commission % figures, result highlights, error states |
| Tertiary surface | `sand` `#f5ede0` | Tier cards, sidebar surfaces, input focus rings |
| Muted text | `mid` `#8a7060` | Secondary text, captions, sub-labels |
| Gold | `c9a84c` | Reserved for VIP tier badge and "Gold" commission tier label only |

Accent (coral) reserved for: primary CTAs, fit recommender result, commission % display, contact form success/error highlights.
Gold reserved for: "Gold" affiliate tier badge only.

---

## Page-Specific Interaction Contracts

### D-01 — Models Grid Layout
- Grid: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8`
- Model card: `bg-cream group` with portrait `aspect-[2/3] overflow-hidden` and `object-cover scale-100 group-hover:scale-105 transition-transform duration-500`
- Below image: `p-4`, name `font-display text-2xl font-normal text-deep`, height + size worn `font-body text-xs uppercase tracking-widest text-mid mt-1`
- Bio: `font-body text-sm text-mid leading-relaxed mt-2 line-clamp-3`
- Instagram link (if present): coral `font-body text-xs uppercase tracking-widest text-coral hover:text-deep transition-colors`
- No pagination — render all up to 10 entries (hard cap in requirements)

### D-02 — Size Guide Fit Recommender
- Input form: 3 number inputs (Bust, Waist, Hips) in a row `flex gap-4 flex-wrap`
- Input style: `w-full border border-deep/30 bg-cream px-4 py-3 font-body text-sm focus:outline-none focus:border-deep transition-colors`
- Unit label: `font-body text-xs text-mid mt-1` below each input ("inches")
- CTA: `bg-deep text-cream font-body text-xs tracking-widest uppercase py-4 px-8 hover:opacity-90 transition-opacity cursor-pointer`
- Logic: Vanilla JS, inline in section JS module. Size thresholds derived from a hardcoded lookup table (XXS–3XL with bust/waist/hip ranges in inches). First matching row wins (bust takes priority if all three don't match one row).
- Result display: Hidden by default, `hidden` class toggled. Result element: `inline-block bg-coral text-cream font-body text-sm tracking-widest uppercase py-2 px-6 mt-4`
- Reset: Clearing any input hides the result div
- No server round-trip — pure JS math on the client

### D-03 — Affiliates Tier Cards
- 3-column grid: `grid grid-cols-1 md:grid-cols-3 gap-6 mt-8`
- Standard tier (10%): `bg-sand border border-deep/10 p-6`
- Silver tier (12%): `bg-sand border border-deep/20 p-6` with `ring-1 ring-mid` to distinguish
- Gold tier (15%): `bg-deep text-cream p-6` (inverted card — highest tier, most emphasis)
- Commission %: `font-display text-5xl font-normal text-coral` (white on Gold card: `text-coral` stays coral for contrast)
- Tier name: `font-body text-xs uppercase tracking-widest text-mid mt-1` (on Gold card: `text-cream/60`)
- Perks list: `mt-4 space-y-2 font-body text-sm text-mid` with `— ` prefix on each item (on Gold card: `text-cream/80`)
- UpPromote embed: `<iframe src="{upromote_url}" class="w-full min-h-[600px] border-0 mt-12" loading="lazy" title="Affiliate Registration"></iframe>`. URL is a merchant-configurable schema setting.
- Fallback if no iframe URL: link button `bg-deep text-cream font-body text-xs tracking-widest uppercase py-4 px-8` → UpPromote URL setting

### D-04 — Social UGC Gallery
- Grid: `grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4` (matches collection grid)
- Post card: `relative group aspect-square overflow-hidden bg-sand`
- Image: `w-full h-full object-cover scale-100 group-hover:scale-105 transition-transform duration-500`
- Hover overlay: `absolute inset-0 bg-deep/60 flex flex-col items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300`
- Caption: `font-body text-xs text-cream text-center px-4 line-clamp-2` inside overlay
- If `product` tagged on post: Show "Shop This Look" link inside overlay: `font-body text-xs uppercase tracking-widest text-cream border border-cream/50 px-4 py-2 hover:bg-cream hover:text-deep transition-colors`
- Empty state: `py-24 text-center` — heading "Nothing to see yet." body "Tag us @soleilnoir to be featured here."

### D-05 — Contact Form
- Fields: Name (text), Email (email), Message (textarea, `rows="5"`)
- Input style: `w-full border border-deep/30 bg-cream px-4 py-3 font-body text-sm focus:outline-none focus:border-deep transition-colors`
- Label style: `font-body text-xs uppercase tracking-widest text-deep mb-1 block`
- Field gap: `space-y-4`
- Submit: `w-full bg-deep text-cream font-body text-xs tracking-widest uppercase py-4 cursor-pointer hover:opacity-90 transition-opacity`
- Uses Shopify native `contact[name]`, `contact[email]`, `contact[body]` form fields with `action="/contact"` and `method="post"` — no JS fetch, standard Shopify form handling
- Success state (`form.posted_successfully`): inline `<p class="font-body text-sm text-coral">` with success copy
- Error state: Shopify renders form errors inline — style `<ul class="font-body text-xs text-coral space-y-1 mt-2">`

### D-06 — FAQ Accordion
- Same pattern as PDP metafield accordions (Phase 4): `data-accordion`, `data-accordion-trigger`, `data-accordion-body`
- Container: `divide-y divide-deep/10 border-t border-deep/10`
- Trigger: `w-full flex items-center justify-between py-4 font-body text-lg font-normal text-deep text-left`
- Body: `overflow-hidden font-body text-sm text-mid leading-relaxed pb-4` with `style="max-height: 0; transition: max-height 300ms ease;"`
- Chevron icon: `w-4 h-4 transition-transform data-accordion-icon` — rotates `180deg` on open
- One-open-at-a-time: same `closeAll()` → `open selected` logic from `pdp.js`. Reuse the same JS pattern in a `faq.js` module.

### D-07 — Policy Pages
- Simple prose layout. Merchant adds copy in Shopify page editor (rich text).
- Wrapper: `max-w-3xl mx-auto px-4 py-16`
- Heading: `font-display text-4xl font-normal text-deep mb-8`
- Body (Shopify `page.content` rich text): `font-body text-sm text-mid leading-relaxed prose-headings:font-display prose-headings:font-normal prose-headings:text-deep`
- Note: `{{ page.content }}` renders Shopify sanitized rich text — no `| escape` needed (same trust boundary as `product.description`)
- 4 policy template JSON files: `page.shipping-returns.json`, `page.privacy-policy.json`, `page.terms-of-service.json`, `page.care-instructions.json` — all route to the same `page-content.liquid` section

### D-08 — About Page
- Hero: `bg-deep text-cream py-24 text-center`, H1 `font-display text-6xl font-normal leading-tight`, subhead `font-body text-sm uppercase tracking-widest text-cream/60 mt-4`
- Story section: `max-w-3xl mx-auto px-4 py-16`, copy in `font-body text-sm text-mid leading-relaxed` with section breaks
- Founder/team strip (optional, placeholder-ready): `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8` — same card shape as Models grid but without metaobject logic; content from merchant-configured schema blocks

### D-09 — Payment Info Page
- Single-column content: `max-w-2xl mx-auto px-4 py-16`
- Payment method icons: inline SVG or merchant-uploaded images in a `flex flex-wrap gap-6 items-center mt-6`
- Trust badge strip: `font-body text-xs uppercase tracking-widest text-mid flex flex-wrap gap-8 items-center mt-6` (SSL, PCI-DSS, US-based)
- Body copy: `font-body text-sm text-mid leading-relaxed` — content from schema text blocks (merchant-editable)

### D-10 — Page Hero Pattern (shared)
All content pages (except policy pages) open with:
- `bg-deep text-cream py-16 lg:py-24` banner
- `h1 class="font-display text-4xl lg:text-6xl font-normal leading-tight text-center"`
- Optional subtitle: `font-body text-xs uppercase tracking-widest text-cream/60 mt-4 text-center`
- Configurable as schema settings: `heading` (text), `subtitle` (text)

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| About hero H1 | "Our Story" |
| About hero subtitle | "Built in the US. Designed for every body." |
| About primary CTA | "Meet Our Models" |
| Models page H1 | "The Faces of Soleil Noir" |
| Models empty heading | "New faces coming soon." |
| Models empty body | "Check back after our next drop." |
| Size guide H1 | "Find Your Fit" |
| Size guide subtitle | "Measure in inches — we'll do the math." |
| Fit recommender CTA | "Find My Size" |
| Fit recommender prompt | "Enter your bust, waist, and hip measurements" |
| Fit recommender result prefix | "We recommend" |
| Fit recommender no-match | "We suggest sizing up — or contact us for help." |
| Affiliates H1 | "Partner With Us" |
| Affiliates subtitle | "Earn commissions sharing styles you love." |
| Affiliates apply CTA | "Apply Now" |
| Affiliates section label | "Join Our Creator Community" |
| Social H1 | "As Seen On You" |
| Social subtitle | "Real bodies. Real styles. All Soleil Noir." |
| Social empty heading | "Nothing to see yet." |
| Social empty body | "Tag us @soleilnoir to be featured here." |
| Social post CTA | "Shop This Look" |
| Contact H1 | "Get in Touch" |
| Contact subtitle | "We'd love to hear from you." |
| Contact submit CTA | "Send Message" |
| Contact success | "Your message is on its way. We'll get back to you within 24 hours." |
| Contact error | "Something went wrong. Please try again or email us directly." |
| FAQ H1 | "Frequently Asked Questions" |
| Shipping policy page heading | "Shipping & Returns" |
| Privacy policy heading | "Privacy Policy" |
| Terms heading | "Terms of Service" |
| Care instructions heading | "Care Instructions" |
| Payment info H1 | "Payment & Security" |
| Payment info subtitle | "Safe, simple, US checkout — always." |

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn | None | not applicable |
| External libraries | None | not applicable |

No third-party UI dependencies. All components are Tailwind utility + Vanilla JS inline in Liquid.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS — all CTAs, empty states, error states, headings specified with exact copy
- [x] Dimension 2 Visuals: PASS — page hero, grid layouts, card shapes, overlay interactions all specified
- [x] Dimension 3 Color: PASS — 60/30/10 contract maintained; coral accent enumerated; gold scoped to Gold tier only
- [x] Dimension 4 Typography: PASS — 6 roles defined with exact Tailwind classes; display/body font pairing consistent with site
- [x] Dimension 5 Spacing: PASS — spacing scale declared, all multiples of 4px, page container and prose widths specified
- [x] Dimension 6 Registry Safety: PASS — no external component or icon libraries; no shadcn; pure Tailwind

**Approval:** approved 2026-06-14
