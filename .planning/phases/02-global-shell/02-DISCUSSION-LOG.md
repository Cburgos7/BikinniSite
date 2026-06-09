# Phase 2: Global Shell - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-09
**Phase:** 02-global-shell
**Areas discussed:** Sticky nav behavior, Mobile nav pattern, Cart drawer, CCPA cookie banner

---

## Sticky Nav Behavior

### Scroll behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Always visible, no change | Fixed to top, same size and style the entire scroll | ✓ |
| Shrink on scroll | Full-height nav shrinks once user scrolls past ~80px | |
| Hide on scroll down, reappear on scroll up | Hides when scrolling down, snaps back on scroll up | |

**User's choice:** Always visible, no change

---

### Nav background

| Option | Description | Selected |
|--------|-------------|----------|
| Solid dark (--deep) | Always opaque deep background | ✓ |
| Transparent over hero, solid on scroll | Transparent on hero, transitions to solid on scroll | |
| Solid cream (--cream) | Light background, dark text | |

**User's choice:** Solid dark (--deep)

---

### Logo treatment

| Option | Description | Selected |
|--------|-------------|----------|
| Image logo (SVG or PNG) | Logo image file via theme settings | |
| Text logo (shop name) | shop.name in Cormorant Garamond, no image | |
| Support both — image if uploaded, text fallback | Theme setting for logo; falls back to shop name text | ✓ |

**User's choice:** Image with text fallback

---

### Search icon behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Expand an inline search bar in the nav | Input expands within the nav row | ✓ |
| Open a full search overlay/drawer | Full-width overlay with larger input | |
| Navigate to /search page | Simple link to Shopify built-in search | |

**User's choice:** Expand inline search bar in nav

---

## Mobile Nav Pattern

### Drawer type

| Option | Description | Selected |
|--------|-------------|----------|
| Full-screen overlay | Nav links fill entire screen, large typography | |
| Slide-in drawer from left | Panel slides from left, partial overlay | ✓ |
| Slide-in drawer from right | Same but from right side | |

**User's choice:** Slide-in drawer from left

---

### Drawer contents

| Option | Description | Selected |
|--------|-------------|----------|
| Nav links only (New In, Bikinis, Lingerie, Sale) | Clean and minimal | ✓ |
| Nav links + account + search | All nav functionality in drawer | |
| Nav links + account + search + social links | Full utility drawer with social icons | |

**User's choice:** Nav links only

---

### Drawer background

| Option | Description | Selected |
|--------|-------------|----------|
| Dark (--deep) with cream text | Matches nav bar, dramatic | ✓ |
| Cream (--cream) with dark text | Lighter, more approachable | |
| Sand (--sand) with dark text | Warm neutral | |

**User's choice:** Dark (--deep) with cream text

---

## Cart Drawer

### Trigger & position

| Option | Description | Selected |
|--------|-------------|----------|
| Slides from right, bag icon click only | Standard; bag icon is the only trigger | ✓ |
| Slides from right, bag icon + auto-open on add-to-cart | Also opens when product added to cart | |
| Slides from right, auto-open + stay-open toast option | Opens on add-to-cart with toast notification option | |

**User's choice:** Slides from right, bag icon click only

---

### Free shipping progress bar

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — show progress toward $75 free shipping threshold | "You're $X away from free shipping!" | ✓ |
| No — keep it clean | Item list + checkout CTA only | |

**User's choice:** Yes — free shipping progress bar

---

### Quantity controls

| Option | Description | Selected |
|--------|-------------|----------|
| − / + buttons with live price update | Tap to adjust, subtotal updates instantly | ✓ |
| Editable number input | Tappable number field | |
| − / + with remove on zero | Minus on qty 1 removes item | |

**User's choice:** − / + buttons with live price update (separate remove button)

---

## CCPA Cookie Banner

### Appearance

| Option | Description | Selected |
|--------|-------------|----------|
| Bottom bar — slim fixed strip | Non-intrusive, appears immediately | ✓ |
| Bottom bar — appears after 3-second delay | Same but delayed | |
| Modal / centered overlay | Blocks interaction until choice is made | |

**User's choice:** Bottom bar, immediate

---

### Choices offered

| Option | Description | Selected |
|--------|-------------|----------|
| Accept / Decline only | Two buttons, simple | ✓ |
| Accept / Manage Preferences | Accept + preferences panel | |

**User's choice:** Accept / Decline only

---

### Storage mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| localStorage — remember choice, never show again | Permanent until localStorage cleared | ✓ |
| Cookie with 12-month expiry | Standard consent cookie | |
| Session only — show on every new session | Most conservative | |

**User's choice:** localStorage

---

## Claude's Discretion

- Footer layout and link structure
- Metafield definition approach in Shopify admin (type, validation, namespace)
- Shopify account page template styling
- 404 and empty cart visual design
- HTML/Aria patterns for drawer open/close (focus trap, scroll lock)

## Deferred Ideas

None — discussion stayed within phase scope.
