# Soleil Noir — Shopify Theme

## What This Is

Soleil Noir is a US-based e-commerce store selling daring swim, lingerie, and activewear in inclusive sizing (XXS–3XL). This project builds the complete Shopify theme — all templates, sections, blocks, metaobject definitions, and integrations — deployed via GitHub auto-deploy to Shopify. The brand runs a weekly drops model and influencer-driven growth strategy.

## Core Value

A visually striking, conversion-optimized Shopify storefront that lets customers browse and buy across swim/lingerie collections, with seamless influencer attribution and a frictionless US checkout.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Dawn-based custom Shopify theme with Tailwind CSS + design tokens
- [ ] Home page with all 12 sections (announcement bar through footer)
- [ ] Sticky nav: logo, links (New In, Bikinis, Lingerie, Sale), search, account, bag
- [ ] Hero section with split layout, headline, CTA
- [ ] Featured products section pulling from "Best Sellers" collection
- [ ] Social media feed block on home page (curated metaobjects)
- [ ] About page with US founding story (placeholder copy)
- [ ] Models page: metaobject-driven grid, hard cap 10 models
- [ ] Bikinis collection page with filters (style, color, size, price), quick-add, wishlist, color dots
- [ ] Lingerie collection page (same template as Bikinis)
- [ ] Products/catalog page (all-products view with cross-collection filtering)
- [ ] Product detail page: image gallery, size selector, color options, add-to-cart, metafield accordions
- [ ] Payment info content page (trust/accepted methods — NOT custom card capture)
- [ ] Size guide page with interactive fit recommender (XXS–3XL)
- [ ] Affiliates recruitment page with embedded UpPromote registration portal
- [ ] Dedicated social page (UGC gallery, shoppable)
- [ ] Cart / mini-cart drawer
- [ ] Contact page + FAQ page
- [ ] Policy pages: Shipping & Returns, Privacy, Terms, Care Instructions
- [ ] Account / login (Shopify customer accounts)
- [ ] 404 + cart empty states
- [ ] Cookie/consent banner (CCPA-compliant)
- [ ] Klaviyo email/SMS flows wired (Welcome, Abandoned Cart, Browse Abandon, Post-Purchase, Win-Back, VIP Early Access, Back in Stock)
- [ ] UpPromote affiliate integration (3 tiers + customer referral, fraud rules)
- [ ] GA4 enhanced e-commerce events + influencer_code custom dimension
- [ ] Cloudinary image pipeline (f_auto,q_auto fetch-URL transforms)
- [ ] Metafields: care_instructions, model_sizing, fabric_composition, coverage_level (product); hero_subtitle (collection)
- [ ] Metaobject: model (name, photo, bio, height, size_worn, instagram_handle, featured_products)
- [ ] Metaobject: social_post (image, caption, link, optional product tag)
- [ ] Mobile-first responsive (desktop, tablet, mobile)
- [ ] Self-hosted subset fonts: Cormorant Garamond + Barlow Condensed, preloaded

### Out of Scope

- Activewear collection/nav — dropped at launch per owner decision
- Custom card-capture payment form — PCI liability; Shopify hosted checkout handles payments
- Australian heritage branding — full US rebrand; no AU references
- Custom applicant database for affiliates — UpPromote owns intake/approval/payouts
- Live auto-sync social feed — curated metaobjects at launch for reliability
- Triple Whale (attribution) — optional post-launch
- Gorgias (support) — optional post-launch
- Custom checkout modifications — Shopify Plus required; launching on Advanced

## Context

- **Platform:** Shopify Advanced at launch, Plus upgrade path defined
- **Theme base:** Dawn-based, custom sections/blocks, Liquid + JSON schema so owner can edit in theme editor
- **Deployment:** GitHub auto-deploy → Shopify; develop on `staging` branch, PR to `main`
- **Design tokens:** `--sand #f5ede0`, `--deep #0d0a08`, `--coral #e85d3a`, `--gold #c9a84c`, `--cream #faf6f0`, `--mid #8a7060`
- **JS constraint:** Vanilla JS only (IntersectionObserver, rAF custom cursor). No jQuery.
- **US compliance:** CCPA (privacy), TCPA (SMS quiet hours 9am–9pm local, explicit opt-in), US sales tax via Shopify automatic nexus

## Constraints

- **Tech stack:** Shopify Liquid + JSON section schema; Tailwind via PostCSS; Vanilla JS only
- **Pricing:** USD only; Shopify Markets can add currencies post-launch
- **Checkout:** Must flow through Shopify's hosted PCI-DSS Level 1 checkout — no custom payment capture
- **Fonts:** Cormorant Garamond + Barlow Condensed, self-hosted subset with preload
- **SMS compliance:** TCPA — explicit checkbox at checkout + signup, quiet hours enforced in Klaviyo
- **Content:** Product photos, model photos, brand copy, and pricing are owner-provided (out of build scope)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Full US rebrand (no Australian heritage) | Owner decision — use US copy everywhere, placeholder for founding story | — Pending |
| Activewear dropped from launch | Not in requested page scope; reduces build surface | — Pending |
| Social feed via curated metaobjects | Avoids API rate limits and token setup headaches at launch; owner controls content | — Pending |
| UpPromote-hosted affiliates form | UpPromote owns intake, approval, tracking, payouts — no custom DB liability | — Pending |
| Models page metaobject-driven | Owner-editable without code; hard cap at 10 | — Pending |
| Dawn as theme base | Shopify-native, section/block schema, theme editor compatible | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-02 after initialization*
