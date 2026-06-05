# Phase 1: Theme Foundation — Context

**Gathered:** 2026-06-02
**Status:** Ready for planning
**Source:** discuss-phase

<domain>
## Phase Boundary

This phase scaffolds the Shopify theme repository. Deliverables:
- Dawn-based theme skeleton, stripped to schema structure only (no Dawn CSS/JS)
- Tailwind CSS via PostCSS build pipeline (in-repo, npm build → assets/)
- Design tokens as CSS custom properties AND Tailwind config named colors
- Cormorant Garamond + Barlow Condensed: WOFF2 subset files in assets/, preloaded in theme.liquid
- Vanilla JS as modular ES modules, one file per feature
- GitHub auto-deploy: `staging` branch → Shopify preview theme; `main` → live published theme

</domain>

<decisions>
## Implementation Decisions

### Dawn Usage
- **Strip Dawn to schema structure only** — keep section/block JSON schemas, theme editor wiring, settings_schema.json, and Shopify Liquid conventions; replace ALL Dawn CSS and JS with custom implementations. Do not import or inherit any Dawn stylesheet.

### Tailwind
- **Utility classes throughout** — Tailwind utility classes used in all Liquid templates and sections (not just layout). No scoping to layout only.
- **Build pipeline:** In-repo `package.json` with a PostCSS build script that compiles `src/css/theme.css` → `assets/theme.css`. Output goes to `assets/` so Shopify CLI picks it up. Add `npm run build` to development workflow docs.

### Design Tokens
- **Dual expression:** CSS custom properties on `:root` AND Tailwind config named colors — both must stay in sync.
- Token values: `--sand: #f5ede0`, `--deep: #0d0a08`, `--coral: #e85d3a`, `--gold: #c9a84c`, `--cream: #faf6f0`, `--mid: #8a7060`
- Tailwind config maps: `colors.sand`, `colors.deep`, `colors.coral`, `colors.gold`, `colors.cream`, `colors.mid` pointing to the CSS var values.

### Fonts
- **WOFF2 subset, self-hosted in assets/:** Generate subset WOFF2 files for Cormorant Garamond (Regular, Italic, SemiBold) and Barlow Condensed (Regular, Medium) covering Latin character set.
- Serve from Shopify CDN via `{{ 'cormorant-garamond-regular.woff2' | asset_url }}`.
- Preload with `<link rel="preload" as="font" type="font/woff2" crossorigin>` in `layout/theme.liquid`.
- No Google Fonts fallback — self-hosted only.

### JavaScript
- **Modular ES modules** — one JS file per feature in `assets/` (e.g., `assets/cart-drawer.js`, `assets/custom-cursor.js`). Imported via `<script type="module" src="{{ 'feature.js' | asset_url }}">` at the section level, not globally bundled.

### Git / Deploy
- `staging` branch → Shopify preview theme (owner can preview before publishing)
- `main` branch → Shopify published live theme (via GitHub auto-deploy integration in Shopify Partners)
- Local dev: `shopify theme dev` with `--store` flag for hot reload

### Claude's Discretion
- Directory structure within the theme (layouts/, sections/, snippets/, templates/, assets/, config/, locales/)
- Which Dawn schema patterns to preserve (section presets, blocks, limit counts)
- Tailwind purge/content config paths
- PostCSS plugin order (tailwindcss, autoprefixer)
- package.json scripts naming (`build`, `watch`, `dev`)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — brand context, constraints, tech stack decisions
- `.planning/REQUIREMENTS.md` — THEME-01 through THEME-06 (Phase 1 requirements)

### Design Tokens
- buildSpec.md §1 — design token values and tech stack spec

</canonical_refs>

<specifics>
## Specific Ideas

- Custom cursor: `requestAnimationFrame`-based cursor animation (Vanilla JS, `assets/custom-cursor.js`)
- IntersectionObserver for scroll-triggered animations — set up the utility in Phase 1 even if sections use it in Phase 3+
- Shopify GitHub integration: configured in Shopify Admin → Online Store → Themes → Add theme → Connect from GitHub
- `shopify.theme.toml` should define the theme name and environment for CLI use
- `tailwind.config.js` content paths: `['./layout/**/*.liquid', './sections/**/*.liquid', './snippets/**/*.liquid', './templates/**/*.liquid']`

</specifics>

<deferred>
## Deferred Ideas

- Section-specific JS (cart drawer, custom cursor full implementation) — scaffolded in Phase 1, implemented in Phase 2+
- Actual section/template content — Phase 2 (global shell) and Phase 3+ (home, collections)
- Klaviyo, UpPromote, GA4 script tags — Phase 6 (Integrations)

</deferred>

---

*Phase: 01-theme-foundation*
*Context gathered: 2026-06-02 via discuss-phase*
