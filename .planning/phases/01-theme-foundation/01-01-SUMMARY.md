---
plan: 01-01
phase: 1
status: complete
completed: 2026-06-05
---

# Summary — 01-01: Theme Scaffold, PostCSS Pipeline, GitHub Deploy

## What Was Built

Scaffolded the complete Soleil Noir Shopify theme directory structure from a clean slate (no Dawn CSS/JS carried over). Wired the Tailwind v3 PostCSS build pipeline with `postcss-cli` and confirmed `npm run build` produces `assets/theme.css`. Created the GitHub Actions workflow for `staging` → preview and `main` → live auto-deploy.

## Key Files Created

- `layout/theme.liquid` — minimal layout with `content_for_header`, `content_for_layout`, font preloads
- `layout/password.liquid` — coming-soon placeholder
- `templates/` — index, 404, cart, customers (login/register/account)
- `sections/header.liquid`, `sections/footer.liquid` — placeholders for Phase 2
- `snippets/icon-*.liquid` — SVG icon snippets for account, cart, search
- `snippets/font-faces.liquid` — all 5 `@font-face` declarations via Shopify `asset_url`
- `config/settings_schema.json` — colors, typography, social settings
- `package.json` — build/watch/dev scripts with tailwindcss, postcss-cli, autoprefixer
- `tailwind.config.js` — content paths, extend.colors with 6 brand tokens, fontFamily
- `postcss.config.js` — tailwindcss + autoprefixer plugins
- `shopify.theme.toml` — staging + production environments (owner fills in IDs)
- `.github/workflows/shopify-deploy.yml` — CI: npm ci → npm run build → shopify theme push
- `.gitignore` — node_modules, .env, logs

## Self-Check: PASSED

- `npm run build` exits 0, produces `assets/theme.css` (12KB+)
- All 8 required directories exist
- `content_for_header` and `content_for_layout` present in theme.liquid
- No Dawn CSS or JS files present
- GitHub Actions workflow defined with correct branch triggers
