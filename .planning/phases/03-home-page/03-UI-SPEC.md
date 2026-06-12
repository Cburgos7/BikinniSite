---
phase: 3
slug: home-page
status: approved
shadcn_initialized: false
preset: none
created: 2026-06-11
---

# Phase 3 — UI Design Contract

> Visual and interaction contract for the Soleil Noir home page. All decisions in §Design Tokens, §Color, and §Locked Decisions are pre-approved from discuss-phase (D-01–D-10). Downstream agents must not re-ask these.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | None — Tailwind utility classes in Shopify Liquid |
| Preset | Not applicable |
| Component library | None |
| Icon library | Inline SVG only |
| Heading font | Cormorant Garamond → `font-display` |
| Body / UI font | Barlow Condensed → `font-body` |

---

## Design Tokens

| Token | Hex | Role |
|-------|-----|------|
| `--sand` | `#f5ede0` | Warm off-white — light section backgrounds |
| `--deep` | `#0d0a08` | Near-black — dark panels, nav, text on light |
| `--coral` | `#e85d3a` | Brand accent — CTAs, highlights |
| `--gold` | `#c9a84c` | Accent secondary — borders, hover states, badge text |
| `--cream` | `#faf6f0` | Page background, card surfaces |
| `--mid` | `#8a7060` | Muted body text, captions, tertiary UI |

Tailwind class mapping:
- `bg-deep` = `background-color: var(--deep)`
- `bg-sand` = `background-color: var(--sand)`
- `bg-coral` = `background-color: var(--coral)`
- `bg-cream` = `background-color: var(--cream)`
- `text-deep` = `color: var(--deep)`
- `text-cream` = `color: var(--cream)`
- `text-coral` = `color: var(--coral)`
- `text-gold` = `color: var(--gold)`
- `text-mid` = `color: var(--mid)`

---

## Color Assignments (60/30/10 rule)

| Role | Token | Hex | Usage |
|------|-------|-----|-------|
| Dominant (60%) | `--cream` | `#faf6f0` | Page background, card surfaces, light section fills |
| Secondary (30%) | `--deep` | `#0d0a08` | Dark panels (hero right half, brand promise strip, footer), nav |
| Accent (10%) | `--coral` | `#e85d3a` | Primary CTA buttons, active states, highlights only |
| Supporting | `--sand` | `#f5ede0` | Hero fallback background, alternate light sections |
| Decorative | `--gold` | `#c9a84c` | Section dividers, hover border on product cards, testimonial quote marks |
| Muted | `--mid` | `#8a7060` | Captions, meta text, placeholder text, sizing pill borders |

**Accent (`--coral`) reserved for:** primary CTA buttons, hover underlines on nav, carousel active dot. Never use for body text or decorative borders.

---

## Spacing Scale

Tailwind-based (4px base unit):

| Token | Tailwind | px | Usage |
|-------|----------|----|-------|
| xs | `gap-1` / `p-1` | 4px | Icon gaps, tight inline |
| sm | `gap-2` / `p-2` | 8px | Badge padding, compact elements |
| md | `gap-4` / `p-4` | 16px | Card internal padding, button padding |
| lg | `gap-6` / `p-6` | 24px | Section internal padding (mobile) |
| xl | `gap-8` / `p-8` | 32px | Section internal padding (tablet) |
| 2xl | `gap-12` / `p-12` | 48px | Section vertical padding (desktop) |
| 3xl | `gap-16` / `p-16` | 64px | Hero vertical padding, major section breaks |

Section vertical rhythm: `py-12 md:py-16 lg:py-20` as default. Hero: `py-0` (full-bleed).

---

## Typography Scale

| Role | Tailwind classes | Breakpoint variants |
|------|-----------------|---------------------|
| Hero headline | `font-display text-4xl font-normal leading-tight` | `md:text-5xl lg:text-6xl` |
| Hero subheadline | `font-body text-lg font-normal tracking-wide` | `md:text-xl` |
| Section heading | `font-display text-3xl font-normal` | `md:text-4xl` |
| Product card title | `font-body text-base font-semibold tracking-wide uppercase` | — |
| Product card price | `font-body text-sm font-normal` | — |
| Body / caption | `font-body text-sm font-normal` | — |
| CTA button | `font-body text-sm font-semibold tracking-widest uppercase` | — |
| Ticker text | `font-body text-sm font-semibold tracking-widest uppercase` | — |
| Testimonial quote | `font-display text-2xl font-normal italic leading-relaxed` | `md:text-3xl` |
| Testimonial author | `font-body text-xs font-semibold tracking-widest uppercase` | — |
| Sizing pill | `font-body text-xs font-semibold tracking-wide` | — |
| Nav link | `font-body text-sm font-semibold tracking-widest uppercase` | — |

---

## Section-by-Section Specs

### HOME-01 — Hero

- **Layout:** Split — image left (55% desktop, full-width stacked mobile), text right (45%)
- **Background:** Image side: no bg. Text side: `bg-deep`
- **Text colors:** `text-cream` for headline + subheadline; CTA: `bg-coral text-cream`
- **Padding:** Text panel: `px-8 py-16 md:px-12 md:py-20 lg:px-16`
- **Fallback:** If no image set, left panel uses `bg-sand`
- **Mobile:** Stack vertically — image on top (aspect-ratio 4/3), text below with `bg-deep`
- **CTA hover:** `bg-coral/90` (10% opacity reduction), `transition-colors duration-200`

### HOME-02 — Ticker / Marquee

- **Background:** `bg-deep`
- **Text:** `text-cream` ticker text + `text-gold` separator dots
- **Padding:** `py-3`
- **Animation:** CSS `@keyframes marquee` — `animation: marquee 30s linear infinite`; pause on `hover:animation-play-state: paused`
- **Default copy:** "Dare to Bare · Inclusive Sizing XXS–3XL · New Drops Weekly · US-Based · Free Shipping Over $75"
- **Separator:** ` · ` in `text-gold`
- **Reuse:** Extend existing `sections/announcement-bar.liquid` marquee CSS animation

### HOME-03 — Category Grid

- **Background:** `bg-cream`
- **Padding:** `py-12 md:py-16`
- **Grid:** 2 columns mobile → 4 columns desktop (`grid grid-cols-2 lg:grid-cols-4 gap-4`)
- **Cards:** Square aspect ratio (aspect-square), image fill, overlay on hover
- **Overlay:** `bg-deep/40 → bg-deep/60 on hover`, label centered in `text-cream font-body text-sm font-semibold tracking-widest uppercase`
- **Default categories:** Bikinis, Lingerie, New In, Sale
- **Card transition:** `transition-all duration-300`

### HOME-04 — Featured Products ("Best Sellers")

- **Background:** `bg-sand`
- **Padding:** `py-12 md:py-16`
- **Grid:** 2 cols mobile → 4 cols desktop (`grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6`)
- **Section heading:** Centered, `font-display text-3xl md:text-4xl text-deep`
- **Product card:** White card (`bg-cream`), image top (aspect-[3/4]), title + price below, quick-add on hover
- **Quick-add:** Appears as bottom overlay `bg-deep text-cream py-3 text-xs tracking-widest uppercase` on card hover; `translate-y-full → translate-y-0 transition-transform duration-200`

### HOME-05 — Social Feed Strip

- **Background:** `bg-cream`
- **Padding:** `py-12 md:py-16`
- **Layout:** Horizontal scroll row — `flex gap-4 overflow-x-auto snap-x snap-mandatory pb-4`
- **Cards:** Square (`w-64 h-64 flex-shrink-0 snap-start`), image fill with `object-cover`
- **Hover overlay:** `bg-deep/70 opacity-0 group-hover:opacity-100 transition-opacity duration-300` — centered "Shop [Product Name] →" in `text-cream font-body text-xs tracking-widest uppercase`
- **Arrow:** `→` in `text-coral`
- **Graceful degradation:** No overlay if `social_post.product` is null (D-08)
- **Scrollbar:** Hidden on mobile (`scrollbar-hide` utility)

### HOME-06 — Brand Promise Strip

- **Background:** `bg-deep`
- **Text:** `text-cream`
- **Padding:** `py-10 md:py-12`
- **Layout:** 4-column grid on desktop (`grid grid-cols-2 md:grid-cols-4 gap-8`), centered items
- **Each promise:** Icon (inline SVG, 24×24, `text-gold`) + heading (`font-body text-sm font-semibold tracking-widest uppercase text-cream`) + short descriptor (`font-body text-xs text-mid`)
- **Promises:** "Premium Fabrics" / "Sizes XXS–3XL" / "New Drops Weekly" / "US-Based & Proud"

### HOME-07 — Testimonials

- **Background:** `bg-sand`
- **Padding:** `py-16 md:py-20`
- **Layout:** Single centered quote, max-width `max-w-2xl mx-auto text-center`
- **Quote marks:** `text-gold font-display text-6xl leading-none` decorative opening/closing
- **Auto-rotate:** 5s interval, Vanilla JS ES module (`assets/testimonial-carousel.js`), pause on hover (D-10)
- **Dot indicators:** `w-2 h-2 rounded-full bg-mid` → active: `bg-coral w-4 transition-all duration-300`
- **Transition:** `opacity-0 → opacity-100 transition-opacity duration-500` between quotes
- **Max blocks:** 6 (D-09)

### HOME-08 — New Arrivals

- **Background:** `bg-cream`
- **Padding:** `py-12 md:py-16`
- **Grid:** Same as HOME-04 (2→4 cols, same card spec)
- **Count:** 4 products (owner-configurable up to 8 via theme editor)
- **Source:** Newest products by `published_at` or a pinned "New Arrivals" collection
- **Section heading:** `font-display text-3xl md:text-4xl text-deep` centered
- **CTA link:** "View All New Arrivals →" below grid — `font-body text-sm font-semibold tracking-widest uppercase text-coral hover:text-deep transition-colors`

### HOME-09 — Sizing Banner

- **Background:** `bg-deep`
- **Text:** `text-cream`
- **Padding:** `py-10 md:py-12`
- **Layout:** Centered — heading + size pill row + CTA link
- **Heading:** `font-display text-2xl md:text-3xl text-cream`
- **Heading copy:** "Find Your Perfect Fit"
- **Pills:** `<span>` elements — `border border-cream/30 px-3 py-1 font-body text-xs tracking-wide text-cream/80 hover:border-coral hover:text-coral transition-colors cursor-pointer`
- **Size order:** XXS · XS · S · M · L · XL · 1X · 2X · 3X
- **CTA:** "View Full Size Guide →" → `/pages/size-guide` — `text-coral hover:text-gold transition-colors font-body text-sm font-semibold tracking-widest uppercase`

---

## Copywriting Contract

| Section | Element | Placeholder / Default Copy |
|---------|---------|---------------------------|
| HOME-01 Hero | Headline | `[PLACEHOLDER — owner provides]` |
| HOME-01 Hero | Subheadline | `[PLACEHOLDER — owner provides]` |
| HOME-01 Hero | CTA label | "Shop Now" (owner-editable) |
| HOME-02 Ticker | Default content | "Dare to Bare · Inclusive Sizing XXS–3XL · New Drops Weekly · US-Based · Free Shipping Over $75" |
| HOME-03 Category | Card labels | "Bikinis" / "Lingerie" / "New In" / "Sale" (collection names, owner-configurable) |
| HOME-04 Featured | Section heading | "Best Sellers" |
| HOME-04 Featured | Quick-add button | "Quick Add" |
| HOME-05 Social | Section heading | "As Seen On" |
| HOME-05 Social | Card CTA | "Shop [product title] →" (dynamic from metaobject) |
| HOME-06 Brand | Promise 1 | "Premium Fabrics" |
| HOME-06 Brand | Promise 2 | "Sizes XXS–3XL" |
| HOME-06 Brand | Promise 3 | "New Drops Weekly" |
| HOME-06 Brand | Promise 4 | "US-Based & Proud" |
| HOME-07 Testimonials | Section heading | "What She Said" |
| HOME-07 Testimonials | Default quote | `[PLACEHOLDER — owner provides testimonials via theme editor blocks]` |
| HOME-08 New Arrivals | Section heading | "New Arrivals" |
| HOME-08 New Arrivals | View all link | "View All New Arrivals →" |
| HOME-09 Sizing | Heading | "Find Your Perfect Fit" |
| HOME-09 Sizing | CTA | "View Full Size Guide →" |
| Empty cart state | (Global — Phase 2) | n/a |
| 404 state | (Global — Phase 2) | n/a |

---

## Interactive States

### Buttons (CTA)
- Default: `bg-coral text-cream`
- Hover: `bg-coral/90 transition-colors duration-200`
- Focus: `ring-2 ring-coral ring-offset-2 outline-none`
- Active: `bg-coral/80 scale-[0.98] transition-transform duration-100`

### Product Cards (HOME-04, HOME-08)
- Default: shadow-none
- Hover: `shadow-md transition-shadow duration-200` + quick-add overlay slides up
- Image: `scale-100 → scale-105 transition-transform duration-500 group-hover:scale-105`

### Social Feed Cards (HOME-05)
- Default: overlay hidden (`opacity-0`)
- Hover: `opacity-100 transition-opacity duration-300`

### Category Grid Cards (HOME-03)
- Default: overlay `bg-deep/40`
- Hover: overlay `bg-deep/60 transition-colors duration-300`

### Nav Links (Global — inherited from Phase 2)
- Hover: underline in `--coral`

### Sizing Pills (HOME-09)
- Default: `border-cream/30 text-cream/80`
- Hover: `border-coral text-coral transition-colors duration-200`

### Testimonial Dots (HOME-07)
- Inactive: `w-2 h-2 bg-mid rounded-full`
- Active: `w-4 h-2 bg-coral rounded-full transition-all duration-300`

---

## Animation Contracts

| Element | Type | Duration | Easing | Notes |
|---------|------|----------|--------|-------|
| Ticker / marquee | CSS `@keyframes marquee` | 30s | `linear` | `animation-play-state: paused` on hover |
| Testimonial swap | Opacity fade | 500ms | `ease-in-out` | JS `setTimeout` 5000ms between swaps |
| Product card image zoom | CSS transform scale | 500ms | `ease-out` | `group-hover:scale-105` |
| Quick-add slide up | CSS transform translateY | 200ms | `ease-out` | `translate-y-full → translate-y-0` |
| Social card overlay | Opacity | 300ms | `ease-in-out` | `opacity-0 → opacity-100` |
| CTA button | Background color | 200ms | `ease` | `transition-colors` |
| Sizing pills | Border + color | 200ms | `ease` | `transition-colors` |

All transitions use Tailwind's `transition-*` utilities. No GSAP or external animation libraries.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS — all 9 sections have placeholder/default copy specified
- [x] Dimension 2 Visuals: PASS — section layouts, card specs, responsive breakpoints defined
- [x] Dimension 3 Color: PASS — 60/30/10 assignments, accent reserved for CTAs only
- [x] Dimension 4 Typography: PASS — all roles mapped to Tailwind classes with breakpoints
- [x] Dimension 5 Spacing: PASS — Tailwind scale documented, section padding specified
- [x] Dimension 6 Registry Safety: PASS — no third-party registries; Tailwind utilities only

**Approval:** approved 2026-06-11
