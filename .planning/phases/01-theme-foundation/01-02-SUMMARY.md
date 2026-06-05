---
plan: 01-02
phase: 1
status: complete
completed: 2026-06-05
---

# Summary — 01-02: Design Tokens, CSS Custom Properties, WOFF2 Fonts

## What Was Built

Added all 6 Soleil Noir design tokens as CSS custom properties on `:root` in `src/css/theme.css`. Verified Tailwind config maps the same hex values as named colors. Generated 5 WOFF2 font subset files (Latin range) from Google Fonts TTF sources using fonttools/pyftsubset. Font preload tags wired in `layout/theme.liquid`.

## Key Files Created/Modified

- `src/css/theme.css` — `:root` with 6 tokens, site-container, data-reveal utilities
- `assets/theme.css` — rebuilt output (12KB, all tokens present)
- `assets/cormorant-garamond-regular.woff2` — 16KB
- `assets/cormorant-garamond-italic.woff2` — 17KB
- `assets/cormorant-garamond-semibold.woff2` — 17KB
- `assets/barlow-condensed-regular.woff2` — 11KB
- `assets/barlow-condensed-medium.woff2` — 11KB
- `snippets/font-faces.liquid` — 5 `@font-face` declarations via `asset_url`
- `layout/theme.liquid` — 2 preload tags for primary font weights

## Self-Check: PASSED

- All 6 CSS custom properties in `:root` with correct hex values
- All 5 WOFF2 files present, sizes 11–17KB (well under 60KB threshold)
- `assets/theme.css` contains all 6 token declarations after build
- `font-display: swap` on all `@font-face` declarations
- Preload tags present for both primary weights with `crossorigin="anonymous"`
