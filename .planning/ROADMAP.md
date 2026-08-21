# Roadmap — Soleil Noir Shopify Theme

**7 phases** | **37 requirements mapped** | v1 complete ✓ · Phase 7 added post-v1

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|-----------------|
| 1 | Theme Foundation | 3/3 | Complete    | 2026-06-05 |
| 2 | Global Shell | Nav, cart drawer, metaobjects/metafields, account, CCPA | NAV-01–05, META-01–04, AUTH-01 | 5 |
| 3 | Home Page | 6/6 | Complete   | 2026-06-12 |
| 4 | Collections & PDP | 5/5 | Complete   | 2026-06-14 |
| 5 | Content Pages | 8/8 | Complete   | 2026-06-14 |
| 6 | Integrations | 6/6 | Complete   | 2026-06-18 |
| 7 | Drop-Ship Order Automation | Orders reach the supplier and tracking reaches customers without manual re-keying | TBD | Not planned |

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
**Plans:** 6/6 plans complete

Plans:
- [x] 03-01-PLAN.md — Hero section (HOME-01) + Ticker/Marquee (HOME-02)
- [x] 03-02-PLAN.md — Brand Promise strip (HOME-06) + Sizing Banner (HOME-09)
- [x] 03-03-PLAN.md — Featured Products "Best Sellers" (HOME-04) + New Arrivals (HOME-08)
- [x] 03-04-PLAN.md — Social Feed strip (HOME-05) + Category Grid (HOME-03)
- [x] 03-05-PLAN.md — Testimonials carousel section + JS module (HOME-07)
- [x] 03-06-PLAN.md — Wire all sections into templates/index.json + responsive QA checkpoint

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
**Plans:** 5/5 plans complete

Plans:

**Wave 1** *(parallel — independent)*
- [x] 04-01-PLAN.md — Shared product-card snippet (swatches, wishlist, quick-add) + migrate home sections
- [x] 04-02-PLAN.md — Collection grid section + AJAX filter JS module
- [x] 04-04-PLAN.md — Product main section (gallery, lightbox, selectors, add-to-cart, accordions) + pdp.js

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 04-03-PLAN.md — Wire templates/collection.json
- [x] 04-05-PLAN.md — Wire templates/product.json

Cross-cutting constraints: `{% schema %}` block required on every section; all JS as ES modules in `assets/`; all Tailwind utilities inline in Liquid (no custom CSS classes)

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
**Plans:** 8/8 plans complete

Plans:

**Wave 1** *(parallel — independent sections and JS modules)*
- [x] 05-01-PLAN.md — About page section (page-about.liquid) + Payment info section (page-payment.liquid)
- [x] 05-02-PLAN.md — Models grid section (page-models.liquid) — metaobject iteration, D-01
- [x] 05-03-PLAN.md — Size guide section (page-sizeguide.liquid) + fit recommender JS (size-guide.js)
- [x] 05-04-PLAN.md — Affiliates section (page-affiliates.liquid) — tier cards + UpPromote iframe
- [x] 05-05-PLAN.md — Social UGC gallery section (page-social.liquid) — metaobject grid, D-04
- [x] 05-06-PLAN.md — Contact section (page-contact.liquid) + FAQ section (page-faq.liquid) + faq.js
- [x] 05-07-PLAN.md — Shared policy section (page-content.liquid)

**Wave 2** *(blocked on Wave 1 — all sections must exist before templates)*
- [x] 05-08-PLAN.md — Wire all 12 JSON page templates (8 unique + 4 policy)

**Success Criteria:**
1. Models page renders all model metaobject entries in a grid (up to 10), each with portrait, bio, height, and size worn
2. Size guide fit recommender accepts bust/waist/hip measurements and returns a recommended size
3. Affiliates page embeds or links UpPromote registration portal and displays all 3 commission tiers
4. Social page displays social_post metaobject entries as a shoppable UGC gallery
5. All policy pages and Contact/FAQ pages exist and are linked from the footer

### Phase 6: Integrations
**Goal:** Wire all third-party services — Klaviyo flows, UpPromote affiliate tracking, GA4 enhanced e-commerce, and Cloudinary image transforms — and verify end-to-end data flow.
**Mode:** standard
**Requirements:** INT-01, INT-02, INT-03, INT-04
**Success Criteria:**
1. Klaviyo signup form captures email/SMS with TCPA-compliant opt-in; abandoned cart flow triggers on test checkout abandonment
2. UpPromote affiliate link with `influencer_code` param correctly attributes a test order; discount code works at checkout
3. GA4 registers `view_item`, `add_to_cart`, `begin_checkout`, and `purchase` events with `influencer_code` dimension on a test purchase
4. Cloudinary fetch-URL transforms (`f_auto,q_auto`) serve optimized images; no broken image URLs in production

---

### Phase 7: Drop-Ship Order Automation

**Goal:** Automate the Elegant Moments drop-ship loop so orders reach the supplier and tracking reaches customers without anyone re-keying them by hand.
**Requirements**: TBD
**Depends on:** Phase 6, plus the real catalogue being live in Shopify
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd-plan-phase 7 to break down)

**Scope:**
1. **Order → supplier email.** Shopify Flow rule on order creation, emailing
   `dropship@elegantmomentslingerie.com`. Per their drop-ship sheet: one order per
   email, carrying style number, colour, size, quantity, and the customer's
   shipping address.
2. **Tracking → customer.** Scheduled agent run writing supplier tracking numbers
   back onto Shopify orders and marking fulfilment, so Shopify's own notification
   fires.
3. **Exception handling.** The supplier replies when an item is out of stock or
   discontinued and waits for a decision — substitute, backorder, or refund. Needs
   a defined policy and a queue, not ad-hoc replies.
4. **Returns policy document.** Elegant Moments includes our returns policy in
   packages only if we supply one. Currently we have not.

**Constraints:**
- **No Shopify scope grants arbitrary email sending.** Flow is the always-on path;
  a scheduled agent covers tracking write-back and exceptions. An agent alone
  cannot be relied on — it does not run continuously.
- Requires `read_orders`, `write_orders`,
  `write_merchant_managed_fulfillment_orders`.
- Customer names and home addresses travel in these emails. The sending path must
  be a service with an audit trail, not a personal mailbox.
- Supplier ships within 24–48h Mon–Fri; expedited orders must reach them by 1 PM
  Eastern. Cancellations are only accepted in writing, by email.
