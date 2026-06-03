# Requirements — Soleil Noir Shopify Theme

## v1 Requirements

### THEME — Theme Foundation & Design System
- [ ] **THEME-01**: Theme is Dawn-based with all custom sections/blocks; Liquid + JSON schema; owner can edit in Shopify theme editor
- [ ] **THEME-02**: Tailwind CSS configured via PostCSS build pipeline with design tokens mapped to CSS custom properties (`--sand`, `--deep`, `--coral`, `--gold`, `--cream`, `--mid`)
- [ ] **THEME-03**: Cormorant Garamond + Barlow Condensed fonts self-hosted, subset, and preloaded
- [ ] **THEME-04**: Vanilla JS only (IntersectionObserver, rAF custom cursor); no jQuery
- [ ] **THEME-05**: Mobile-first responsive across desktop, tablet, and mobile breakpoints
- [ ] **THEME-06**: Shopify GitHub auto-deploy wired: `staging` branch for dev, PR to `main` for production

### NAV — Navigation & Global UI
- [ ] **NAV-01**: Announcement bar displays free shipping threshold, weekly drops mention, US-based line
- [ ] **NAV-02**: Sticky nav with logo, links (New In, Bikinis, Lingerie, Sale), search icon, account icon, bag icon
- [ ] **NAV-03**: Cart / mini-cart drawer with item list, quantity controls, checkout CTA
- [ ] **NAV-04**: Cookie/consent banner (CCPA-compliant)
- [ ] **NAV-05**: 404 page and cart empty state with brand-appropriate copy and CTAs

### HOME — Home Page (`templates/index.json`)
- [ ] **HOME-01**: Hero section: split layout, headline, sub-headline, primary CTA to shop
- [ ] **HOME-02**: Ticker / marquee with rotating brand promises
- [ ] **HOME-03**: Category grid linking to collection pages
- [ ] **HOME-04**: Featured products section pulling from "Best Sellers" Shopify collection
- [ ] **HOME-05**: Social media feed block: curated social_post metaobjects displayed as a shoppable strip
- [ ] **HOME-06**: Brand promise strip (fabric quality, sizing, weekly drops, US-based)
- [ ] **HOME-07**: Editorial / testimonial section
- [ ] **HOME-08**: New arrivals section
- [ ] **HOME-09**: Sizing banner with size pills and link to sizing page

### COLL — Collection Pages
- [ ] **COLL-01**: Bikinis collection page (`templates/collection.json`) with product grid, filter sidebar (style, color, size, price), sort options
- [ ] **COLL-02**: Lingerie collection page using same collection template
- [ ] **COLL-03**: All-products catalog page showing full cross-collection catalog with unified filtering
- [ ] **COLL-04**: Product cards include quick-add, wishlist toggle, color swatches/dots

### PDP — Product Detail Page (`templates/product.json`)
- [ ] **PDP-01**: Image gallery with zoom/lightbox
- [ ] **PDP-02**: Size selector and color option picker
- [ ] **PDP-03**: Add-to-cart with variant validation
- [ ] **PDP-04**: Metafield accordions: care_instructions, fabric_composition, coverage_level
- [ ] **PDP-05**: Model sizing note pulled from model_sizing metafield

### META — Metafields & Metaobjects
- [ ] **META-01**: Product metafields defined: care_instructions, model_sizing, fabric_composition, coverage_level
- [ ] **META-02**: Collection metafield defined: hero_subtitle
- [ ] **META-03**: Metaobject definition: `model` (name, photo, bio, height, size_worn, instagram_handle, featured_products)
- [ ] **META-04**: Metaobject definition: `social_post` (image, caption, link, optional product tag)

### PAGE — Content Pages
- [ ] **PAGE-01**: About page with US founding story (placeholder copy flagged for owner); team/founder section
- [ ] **PAGE-02**: Models page (`templates/page.models.json`): metaobject-driven grid of up to 10 models with portrait, bio, height, size worn, optional Instagram link
- [ ] **PAGE-03**: Payment info page (`templates/page.payment.json`): accepted payment methods, SSL trust messaging, US billing/tax note, link to Shopify checkout
- [ ] **PAGE-04**: Size guide page (`templates/page.sizeguide.json`): XXS–3XL chart, measuring instructions, interactive fit recommender (enter measurements → recommended size)
- [ ] **PAGE-05**: Affiliates page (`templates/page.affiliates.json`): commission tiers (10%/12%/15%), perks, how it works, embedded UpPromote registration portal
- [ ] **PAGE-06**: Social page (`templates/page.social.json`): UGC gallery of social_post metaobjects, shoppable where product tags present
- [ ] **PAGE-07**: Contact page with form
- [ ] **PAGE-08**: FAQ page
- [ ] **PAGE-09**: Policy pages: Shipping & Returns, Privacy Policy, Terms of Service, Care Instructions (footer links)

### AUTH — Account & Auth
- [ ] **AUTH-01**: Shopify customer accounts (login, register, order history, address book)

### INT — Third-Party Integrations
- [ ] **INT-01**: Klaviyo: embed signup form, wire abandoned cart, welcome series, post-purchase, win-back, VIP early access, back-in-stock flows; TCPA SMS opt-in at checkout + signup forms
- [ ] **INT-02**: UpPromote: affiliate signup embed, tracking links + discount codes wired, 3-tier commission structure (Standard 10% / Silver 12% / Gold 15%) + Ambassador + Customer Referral 5%; fraud rules (self-referral block, IP clustering, 14-day hold)
- [ ] **INT-03**: GA4: enhanced e-commerce events (view_item, add_to_cart, begin_checkout, purchase, view_item_list, select_item); custom dimension `influencer_code`; UTM convention documented
- [ ] **INT-04**: Cloudinary: image pipeline via fetch-URL transforms (`f_auto,q_auto`) over Shopify CDN URLs

---

## v2 Requirements (Deferred)

- Triple Whale multi-channel attribution — post-launch once ad spend scales
- Gorgias unified support inbox + live chat — post-launch
- Activewear collection page — dropped from launch scope
- Shopify Markets multi-currency — USD-only at launch; Markets config post-launch
- Custom checkout modifications — requires Shopify Plus upgrade
- Live auto-sync Instagram/TikTok feed — app + API token setup deferred; launching with curated metaobjects

---

## Out of Scope

- Custom card-capture payment form — PCI-DSS liability; all payments through Shopify hosted checkout
- Custom affiliate applicant database — UpPromote handles intake, approval, tracking, payouts
- Australian heritage brand copy — full US rebrand; no AU references at launch
- Product photos, model photos, brand copy, pricing — owner-provided content, not a build deliverable
- US legal policy copy (Terms, Privacy, Returns) — owner to obtain via legal counsel

---

## Traceability

| Requirement | Phase |
|-------------|-------|
| THEME-01–06 | Phase 1 |
| NAV-01–05 | Phase 2 |
| HOME-01–09 | Phase 3 |
| COLL-01–04 | Phase 4 |
| PDP-01–05 | Phase 4 |
| META-01–04 | Phase 2 |
| PAGE-01–09 | Phase 5 |
| AUTH-01 | Phase 2 |
| INT-01–04 | Phase 6 |
