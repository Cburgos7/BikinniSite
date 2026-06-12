# Roadmap — Soleil Noir Shopify Theme

**6 phases** | **37 requirements mapped** | All v1 requirements covered ✓

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|-----------------|
| 1 | Theme Foundation | 3/3 | Complete    | 2026-06-05 |
| 2 | Global Shell | Nav, cart drawer, metaobjects/metafields, account, CCPA | NAV-01–05, META-01–04, AUTH-01 | 5 |
| 3 | Home Page | 4/6 | In Progress|  |
| 4 | Collections & PDP | Bikinis, Lingerie, catalog, product detail with all metafields | COLL-01–04, PDP-01–05 | 5 |
| 5 | Content Pages | About, Models, Payment, Size guide, Affiliates, Social, FAQ, Contact, Policies | PAGE-01–09 | 5 |
| 6 | Integrations | Klaviyo, UpPromote, GA4, Cloudinary all wired and verified | INT-01–04 | 4 |

---

### Phase 1: Theme Foundation
**Goal:** Scaffold the Shopify theme repository — Dawn base, Tailwind PostCSS pipeline, design tokens, fonts, and GitHub auto-deploy — so every subsequent phase builds on a solid, deployable base.
**Mode:** standard
**Requirements:** THEME-01, THEME-02, THEME-03, THEME-04, THEME-05, THEME-06
**Success Criteria:**
1. `shopify theme dev` runs locally without errors on the Dawn-based theme
2. Tailwind build pipeline produces scoped CSS with all 6 design token custom properties present
3. Cormorant Garamond and Barlow Condensed load from self-hosted subsets with `<link rel="preload">`
4. A push to `staging` branch triggers Shopify preview; PR to `main` deploys to live theme
5. No jQuery present; Vanilla JS files lint clean

---

### Phase 2: Global Shell
**Goal:** Build everything that wraps every page — sticky nav, cart drawer, metaobject/metafield schema definitions, Shopify customer accounts, and the CCPA cookie banner — so later phases inherit a complete page frame.
**Mode:** standard
**Requirements:** NAV-01, NAV-02, NAV-03, NAV-04, NAV-05, META-01, META-02, META-03, META-04, AUTH-01
**Plans:** 6 plans

Plans:
- [ ] 02-01-PLAN.md — Dev environment setup (Shopify Partner account, dev store, shopify.theme.toml config)
- [ ] 02-02-PLAN.md — Metafields + metaobject definitions in Shopify admin
- [ ] 02-03-PLAN.md — Sticky nav section + mobile drawer + inline search JS modules
- [ ] 02-04-PLAN.md — Cart drawer section + Ajax Cart API JS module
- [ ] 02-05-PLAN.md — CCPA cookie consent banner + 404 page template
- [ ] 02-06-PLAN.md — Footer section + customer account templates (login, register, account, addresses, order)

**Success Criteria:**
1. Announcement bar, sticky nav, and cart drawer render correctly on desktop and mobile
2. All 4 metafields (product) and 1 metafield (collection) are defined in Shopify admin and readable in Liquid
3. Metaobject definitions `model` and `social_post` exist in Shopify admin with all required fields
4. Customer account login, register, order history, and address pages function through Shopify native accounts
5. CCPA cookie banner appears on first visit and respects opt-in/out; 404 and empty cart states display correctly

---

### Phase 3: Home Page
**Goal:** Build the complete home page with all sections from announcement bar to footer, each editable in the Shopify theme editor, including the curated social feed block.
**Mode:** standard
**Requirements:** HOME-01, HOME-02, HOME-03, HOME-04, HOME-05, HOME-06, HOME-07, HOME-08, HOME-09
**Plans:** 4/6 plans executed

Plans:
- [x] 03-01-PLAN.md — Hero section (HOME-01) + Ticker/Marquee (HOME-02)
- [x] 03-02-PLAN.md — Brand Promise strip (HOME-06) + Sizing Banner (HOME-09)
- [x] 03-03-PLAN.md — Featured Products "Best Sellers" (HOME-04) + New Arrivals (HOME-08)
- [x] 03-04-PLAN.md — Social Feed strip (HOME-05) + Category Grid (HOME-03)
- [ ] 03-05-PLAN.md — Testimonials carousel section + JS module (HOME-07)
- [ ] 03-06-PLAN.md — Wire all sections into templates/index.json + responsive QA checkpoint

**Success Criteria:**
1. All 9 content sections render correctly on the home page in the correct order
2. Featured products section pulls live products from the "Best Sellers" Shopify collection
3. Social feed block displays at least one social_post metaobject entry as a shoppable card
4. Every section is editable via the Shopify theme editor without touching code
5. Home page passes mobile-first responsive checks at 375px, 768px, and 1280px

---

### Phase 4: Collections & Product Detail
**Goal:** Build the Bikinis collection, Lingerie collection, all-products catalog, and product detail page — the core shopping flow from browse to add-to-cart.
**Mode:** standard
**Requirements:** COLL-01, COLL-02, COLL-03, COLL-04, PDP-01, PDP-02, PDP-03, PDP-04, PDP-05
**Success Criteria:**
1. Bikinis and Lingerie collection pages display products with working filters (style, color, size, price) and sort
2. All-products catalog aggregates all collections with unified filtering
3. Product cards show quick-add, wishlist toggle, and color swatches
4. Product detail page displays image gallery, size/color selectors, and add-to-cart with variant validation
5. All 4 metafield accordions (care, fabric, coverage, model sizing) render on PDP when populated

---

### Phase 5: Content Pages
**Goal:** Build all standalone content pages — About, Models, Payment info, Size guide with fit recommender, Affiliates with UpPromote embed, Social UGC gallery, Contact, FAQ, and policy pages.
**Mode:** standard
**Requirements:** PAGE-01, PAGE-02, PAGE-03, PAGE-04, PAGE-05, PAGE-06, PAGE-07, PAGE-08, PAGE-09
**Success Criteria:**
1. Models page renders all model metaobject entries in a grid (up to 10), each with portrait, bio, height, and size worn
2. Size guide fit recommender accepts bust/waist/hip measurements and returns a recommended size
3. Affiliates page embeds or links UpPromote registration portal and displays all 3 commission tiers
4. Social page displays social_post metaobject entries as a shoppable UGC gallery
5. All policy pages and Contact/FAQ pages exist and are linked from the footer

---

### Phase 6: Integrations
**Goal:** Wire all third-party services — Klaviyo flows, UpPromote affiliate tracking, GA4 enhanced e-commerce, and Cloudinary image transforms — and verify end-to-end data flow.
**Mode:** standard
**Requirements:** INT-01, INT-02, INT-03, INT-04
**Success Criteria:**
1. Klaviyo signup form captures email/SMS with TCPA-compliant opt-in; abandoned cart flow triggers on test checkout abandonment
2. UpPromote affiliate link with `influencer_code` param correctly attributes a test order; discount code works at checkout
3. GA4 registers `view_item`, `add_to_cart`, `begin_checkout`, and `purchase` events with `influencer_code` dimension on a test purchase
4. Cloudinary fetch-URL transforms (`f_auto,q_auto`) serve optimized images; no broken image URLs in production
