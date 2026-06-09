# Phase 2: Global Shell — UI Design Contract

**Generated:** 2026-06-09
**Phase:** 02-global-shell
**Source:** discuss-phase decisions (02-CONTEXT.md D-01–D-16)
**Status:** Ready for planning

---

## Design Token Reference

All components use these tokens exclusively — no hardcoded colors:

| Token | Value | Usage |
|-------|-------|-------|
| `--deep` | `#0d0a08` | Nav bg, mobile drawer bg, CCPA banner bg |
| `--cream` | `#faf6f0` | Text on dark, page background |
| `--coral` | `#e85d3a` | CTAs, active states, cart count badge |
| `--gold` | `#c9a84c` | Accent, hover underlines |
| `--sand` | `#f5ede0` | Subtle backgrounds |
| `--mid` | `#8a7060` | Muted text, borders |

Typography: `font-display` = Cormorant Garamond · `font-body` = Barlow Condensed

---

## Component 1: Sticky Navigation

### Layout — Desktop (≥1024px)

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo / Shop Name]   New In  Bikinis  Lingerie  Sale   🔍 👤 🛍  │  ← bg-deep, h-16
└─────────────────────────────────────────────────────────────────┘
```

- Full-width, `position: fixed; top: 0; z-index: 50`
- Height: `h-16` (64px) — constant, never shrinks
- Background: `bg-deep` always — no transparency, no scroll transition
- Text: `text-cream`, `font-body tracking-widest uppercase text-sm`
- Logo: left-aligned. If logo image uploaded via theme settings → `<img>` max-height `h-8`. Fallback → `shop.name` in `font-display text-xl text-cream`
- Nav links: centered between logo and icons. Links: New In · Bikinis · Lingerie · Sale
  - Hover state: `--gold` underline, `text-gold` transition
  - Active/current page: `--coral` underline, persistent
- Right icons: search (🔍) · account (👤) · bag (🛍) — `text-cream`, 20px
- Bag icon: shows count badge when cart non-empty — `bg-coral text-cream text-xs rounded-full w-4 h-4` positioned top-right of icon
- Body offset: `<body>` gets `pt-16` (or equivalent) so content sits below sticky nav

### Layout — Tablet (768px–1023px)

- Same as desktop but nav links collapse; show hamburger (☰) on left + icons on right
- Logo centered

### Layout — Mobile (<768px)

```
┌─────────────────────────────────────────────────────────────────┐
│  ☰   [Logo / Shop Name]                             🔍 👤 🛍    │  ← bg-deep, h-14
└─────────────────────────────────────────────────────────────────┘
```

- Height: `h-14` (56px)
- Hamburger left, logo centered, icons right
- No nav links visible — in mobile drawer

### Search — Inline Expand State

Triggered by clicking the 🔍 icon. Replaces the nav links area in-place:

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo]   [_________________________search input___________] ✕  │
└─────────────────────────────────────────────────────────────────┘
```

- Nav links fade out (`opacity-0`) → search input fades in (`opacity-100`), `transition-opacity duration-200`
- Input: `bg-transparent border-b border-cream text-cream placeholder-mid font-body`
- Placeholder text: "Search…"
- ✕ close button right — restores nav links, clears input
- `autofocus` on input when expanded
- Submit: `Enter` key → navigates to `/search?q={query}`
- Escape key → collapses search, restores links

### States Summary

| State | Description |
|-------|-------------|
| Default | bg-deep, cream text, nav links visible |
| Search expanded | Nav links hidden, inline search input visible |
| Cart has items | Bag icon shows coral count badge |
| Current page link | Coral underline on matching nav link |

---

## Component 2: Mobile Nav Drawer

### Structure

Slide-in panel from the LEFT side. Overlay covers rest of screen.

```
┌──────────────────────┬────────────────────────────────┐
│  ✕                   │                                │
│                      │   [dimmed overlay, bg-deep/50] │
│  New In              │                                │
│                      │                                │
│  Bikinis             │                                │
│                      │                                │
│  Lingerie            │                                │
│                      │                                │
│  Sale                │                                │
│                      │                                │
│                      │                                │
└──────────────────────┴────────────────────────────────┘
  [drawer ~280px wide]        [overlay]
```

- Drawer width: `w-70` (280px) or `w-4/5` max, whichever is smaller
- Background: `bg-deep`
- Text: `text-cream font-display text-3xl` for nav links — large, editorial
- ✕ close button: top-right of drawer, `text-cream`
- Overlay: `bg-deep/50 backdrop-blur-sm` — clicking overlay closes drawer
- Animation: `transform translate-x-[-100%]` → `translate-x-0`, `transition-transform duration-300 ease-in-out`
- When open: body scroll locked (`overflow-hidden` on `<body>`)
- Focus trap: Tab cycles through ✕ button and nav links only while drawer is open
- Escape key closes drawer

### Nav Link Styles

```
New In          ← font-display, text-3xl, tracking-wide, text-cream
Bikinis         ← same
Lingerie        ← same
Sale            ← same, text-coral (sale gets accent color)
```

- Hover: `text-gold`, no underline
- Padding: `py-4 px-8` per link — generous touch targets

---

## Component 3: Cart Drawer

### Trigger

- Bag icon click only — does NOT auto-open on add-to-cart
- Cart count badge on bag icon updates via Shopify Ajax Cart API without page reload

### Structure — Slide from RIGHT

```
                    ┌──────────────────────────────────┐
                    │  Your Cart               ✕       │  ← header
                    ├──────────────────────────────────┤
                    │ ████████████░░░ $52 of $75       │  ← free shipping bar
                    │ "You're $23 away from free ship" │
                    ├──────────────────────────────────┤
                    │ [Product image] Product name     │  ← item row
                    │                Variant: S / Red  │
                    │                [−] [2] [+]  $48  │
                    │                           🗑     │
                    ├──────────────────────────────────┤
                    │ [Product image] Product name     │  ← item row 2
                    │                ...               │
                    ├──────────────────────────────────┤
                    │         Subtotal: $96.00         │  ← footer
                    │    [  PROCEED TO CHECKOUT  ]     │  ← coral CTA button
                    └──────────────────────────────────┘
```

- Drawer width: `w-96` (384px) desktop · full-width on mobile
- Background: `bg-cream`
- Header: `bg-deep text-cream`, "Your Cart" in `font-display`, ✕ close right
- Animation: `translate-x-[100%]` → `translate-x-0`, `transition-transform duration-300`
- Overlay: `bg-deep/40` behind drawer; clicking overlay closes drawer
- Body scroll locked when open; focus trap active

### Free Shipping Progress Bar

```
████████████░░░░░░   $52 / $75
"You're $23 away from free shipping!"
```

- Threshold: `$75` (configurable via theme setting — synced with announcement bar)
- Progress: `width: {(cart_total / 75) * 100}%`, capped at 100%
- Bar colors: filled = `bg-coral`, track = `bg-sand`
- Text: `font-body text-sm text-deep`
- At $75+: bar full coral, text changes to "🎉 You've unlocked free shipping!"
- Updates live when quantity changes

### Item Row

- Product thumbnail: `w-16 h-20 object-cover` (portrait crop)
- Product name: `font-body text-sm text-deep`
- Variant: `text-mid text-xs`
- Quantity controls: `[−]` · count number · `[+]` — each `w-8 h-8 border border-mid`
  - `−` disabled (visually muted) at quantity 1 — does NOT remove item
  - `+` / `−` calls Shopify Ajax Cart API (`/cart/change.js`), subtotal updates without reload
- Price: `font-body text-sm text-deep` right-aligned
- Remove icon 🗑: `text-mid`, hover `text-coral`; calls `/cart/change.js` with quantity 0

### Empty Cart State

When cart has 0 items:

```
                    │  Your Cart               ✕       │
                    │                                  │
                    │         [bag icon, large]        │
                    │                                  │
                    │       Your cart is empty         │  ← font-display
                    │  Start browsing our collections  │  ← font-body, text-mid
                    │                                  │
                    │       [  SHOP NOW  ]             │  ← coral button → /collections/all
                    │                                  │
```

### Footer

- Subtotal line: `font-body text-deep`, subtotal value right-aligned
- Note: "Shipping & taxes calculated at checkout" — `text-mid text-xs`
- CTA: full-width button `bg-coral text-cream font-body tracking-widest uppercase py-4` → Shopify checkout URL

---

## Component 4: CCPA Cookie Banner

### Structure — Slim Bottom Bar

```
┌─────────────────────────────────────────────────────────────────┐
│  We use cookies to improve your experience.  [Accept] [Decline] │  ← fixed bottom, bg-deep
└─────────────────────────────────────────────────────────────────┘
```

- `position: fixed; bottom: 0; left: 0; right: 0; z-index: 100`
- Background: `bg-deep`
- Text: `text-cream font-body text-sm` — "We use cookies to improve your experience and for analytics."
- **Accept** button: `bg-coral text-cream px-4 py-2 text-xs font-body uppercase tracking-wider`
- **Decline** button: `border border-cream text-cream px-4 py-2 text-xs` (ghost/outline style)
- Appears immediately on first visit (no delay)
- On either choice: banner slides down off screen (`translate-y-full`), `transition-transform duration-300`
- Choice stored in `localStorage` key `soleil_noir_cookie_consent` → value `"accepted"` or `"declined"`
- On page load: if key exists → banner never renders (display: none from server or hidden immediately)
- Responsive: stacks text above buttons on mobile

---

## Component 5: 404 Page (`templates/404.json`)

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [Nav]                                                          │
│                                                                 │
│                        404                                      │  ← font-display, text-9xl, text-sand
│                  Page Not Found                                 │  ← font-display, text-2xl
│         Looks like this page took a swim.                      │  ← font-body, text-mid
│                                                                 │
│              [  BACK TO SHOP  ]   [  VIEW COLLECTIONS  ]       │  ← coral + outline buttons
│                                                                 │
│  [Footer]                                                       │
└─────────────────────────────────────────────────────────────────┘
```

- Large `404` numeral: `font-display text-[12rem] text-sand leading-none` — decorative
- Brand copy: "Looks like this page took a swim." — on-brand, playful
- Two CTAs: primary coral button → `/` · secondary outline → `/collections/all`

---

## Component 6: Metafield & Metaobject Definitions

No UI — these are Shopify admin configuration entries. Document the definitions for the executor:

### Product Metafields (namespace: `custom`)

| Key | Type | Validation | Used in |
|-----|------|------------|---------|
| `care_instructions` | `multi_line_text_field` | — | PDP accordion (Phase 4) |
| `model_sizing` | `single_line_text_field` | — | PDP model note (Phase 4) |
| `fabric_composition` | `single_line_text_field` | — | PDP accordion (Phase 4) |
| `coverage_level` | `single_line_text_field` | — | PDP accordion (Phase 4) |

### Collection Metafields (namespace: `custom`)

| Key | Type | Used in |
|-----|------|---------|
| `hero_subtitle` | `single_line_text_field` | Collection hero (Phase 4) |

### Metaobject: `model`

| Field | Type | Required |
|-------|------|----------|
| `name` | `single_line_text_field` | ✓ |
| `photo` | `file_reference` (image) | ✓ |
| `bio` | `multi_line_text_field` | ✓ |
| `height` | `single_line_text_field` | ✓ |
| `size_worn` | `single_line_text_field` | ✓ |
| `instagram_handle` | `single_line_text_field` | — |
| `featured_products` | `list.product_reference` | — |

### Metaobject: `social_post`

| Field | Type | Required |
|-------|------|----------|
| `image` | `file_reference` (image) | ✓ |
| `caption` | `single_line_text_field` | ✓ |
| `link` | `url` | ✓ |
| `product_tag` | `product_reference` | — |

---

## Component 7: Dev Environment Setup

No UI — setup task. Steps for plan executor:

1. Create Shopify Partner account at `partners.shopify.com` (free)
2. Create Development store inside Partner dashboard (free, unlimited)
3. `npm install -g @shopify/cli @shopify/theme`
4. `shopify auth login --store=<dev-store>.myshopify.com`
5. Verify `shopify.theme.toml` has `[environments.development]` with correct store URL
6. Add placeholder content in Shopify admin:
   - 3 products with size variants (XS/S/M/L/XL) — assign to "Best Sellers" collection
   - Create "Bikinis" collection + "Lingerie" collection — assign products
7. `shopify theme dev --store=<dev-store>.myshopify.com` — confirm live preview URL loads

---

## Responsive Breakpoints

| Breakpoint | Tailwind | Behavior |
|-----------|----------|---------|
| Mobile | default (<768px) | Hamburger nav, full-width cart drawer |
| Tablet | `md:` (768px) | Hamburger nav, nav icons visible |
| Desktop | `lg:` (1024px) | Full nav links visible, no hamburger |

---

## Accessibility Requirements

- All drawers: focus trap active when open, focus returns to trigger on close
- All drawers: `role="dialog"` `aria-modal="true"` `aria-label="[name]"`
- Overlay: `aria-hidden="true"`
- Hamburger: `aria-expanded` toggles `true`/`false`
- Cart count badge: `aria-label="Cart, {N} items"`
- CCPA: `role="banner"` or `role="complementary"`, buttons with clear labels
- Escape key closes any open drawer/overlay

---

*UI-SPEC generated from 02-CONTEXT.md decisions D-01 through D-16*
*Consumed by: gsd-planner for Phase 2 task breakdown*
