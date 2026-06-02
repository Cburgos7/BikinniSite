# Soleil Noir — Shopify Build Spec

**Purpose:** This file is the build brief for Claude Code. It defines the pages, the tech stack, the data each page needs, and the conventions to follow when scaffolding the Soleil Noir e-commerce store.

**Brand:** Soleil Noir — daring swim, lingerie, and activewear. Inclusive sizing XXS–3XL. Weekly drops. Influencer-driven growth model.

**Market / legal positioning:** **US-based, US-supporting company.** Pricing in USD, US shipping defaults, US tax handling, US compliance (TCPA for SMS, CCPA for privacy). See "US Positioning" below.

> **Open decision for the owner:** The original brand prototype and proposal positioned the brand as *"designed in Australia since 1994."* This spec assumes a US-based company. Decide one of:
> - **Full US rebrand** — drop Australian references, replace with US founding story.
> - **US company, Australian design heritage** — keep "Australian-designed" as a heritage line but operate, ship, bill, and comply as a US entity.
> Until decided, use US copy everywhere and leave the Australian heritage line out. All `[PLACEHOLDER]` brand-story copy is flagged below.

---

## 1. Tech Stack

This is the agreed stack (from the internal technical build doc). Build against it.

| Layer | Service | Role |
| --- | --- | --- |
| Platform | **Shopify** (Advanced at launch; Plus upgrade path) | Store, checkout, payments, inventory, orders, shipping, tax |
| Influencer program | **UpPromote** | Affiliate signup, tracking links + discount codes, tiered commissions, payouts |
| Email / SMS | **Klaviyo** | Automated flows (abandoned cart, welcome, post-purchase, win-back, back-in-stock) |
| Analytics | **GA4** | Traffic, enhanced e-commerce events, influencer attribution via `influencer_code` custom dimension |
| Image pipeline | **Cloudinary** | `f_auto,q_auto` fetch-URL transforms over Shopify CDN |
| Attribution (optional) | **Triple Whale** | Multi-channel attribution, influencer incrementality |
| Support (optional) | **Gorgias** | Unified inbox, order lookup, live chat |

**Theme architecture:**
- Dawn-based Shopify theme, rewritten with custom sections/blocks.
- Liquid (server-rendered) + JSON section schema so the owner can edit via theme editor.
- Tailwind CSS via PostCSS build pipeline; design tokens mapped to CSS custom properties: `--sand #f5ede0`, `--deep #0d0a08`, `--coral #e85d3a`, `--gold #c9a84c`, `--cream #faf6f0`, `--mid #8a7060`.
- Vanilla JS for animations (IntersectionObserver, requestAnimationFrame custom cursor). No jQuery.
- Fonts: Cormorant Garamond + Barlow Condensed, self-hosted subset, preloaded.

**Conventions:**
- All prices USD.
- Use Shopify metafields already defined: `care_instructions`, `model_sizing`, `fabric_composition`, `coverage_level` (product); `hero_subtitle` (collection).
- Mobile-first responsive (desktop, tablet, mobile).
- Build on `staging` branch, PR to `main`, Shopify GitHub auto-deploy.

---

## 2. Pages to Build

> Shopify note: "collections," "products," and "pages" are distinct object types. Mapping is called out per page so Claude Code uses the right template type (`collection.*`, `product.*`, `page.*`, `index`).

### 2.1 Home (`templates/index.json`)
The flagship page. Sections, top to bottom:
1. Announcement bar — free shipping threshold, weekly drops, US-based line.
2. Sticky nav — logo, links (New In, Bikinis, Lingerie, Activewear, Sale), search, account, bag.
3. Hero — split layout, headline, sub, primary CTA to shop.
4. Ticker — rotating brand promises.
5. Category grid — links to collection pages.
6. Featured products — best sellers pulled from a "Best Sellers" collection.
7. **Social media feed block (NEW)** — see §2.9. A presentation/showcase point on the home page embedding recent social posts (shoppable UGC).
8. Brand promise strip — fabric, sizing, weekly drops, US-based.
9. Editorial / testimonial.
10. New arrivals.
11. Sizing banner — size pills + link to sizing page.
12. Footer.

### 2.2 About (`templates/page.about.json`)
Brand story, mission, inclusive-sizing ethos, US founding story `[PLACEHOLDER — brand origin copy]`. Builds trust. Include team/founder section optional.

### 2.3 Models Pages (`templates/page.models.json` + per-model blocks)
A page (or collection of pages) showcasing **up to 10 models**. Each model entry:
- Name / handle
- Portrait image (Cloudinary-optimized)
- Short bio `[PLACEHOLDER]`
- Their height + the size they wear (drive from `model_sizing` metafield logic for honesty/fit context)
- Optional: link to products they're featured in, optional link to their social
- Optional: tie a model to an affiliate/ambassador record in UpPromote

**Build approach:** a metaobject definition `model` with fields (name, photo, bio, height, size_worn, instagram_handle, featured_products), rendered in a grid. Cap display at 10. This keeps it owner-editable without code.

### 2.4 Bikinis (`templates/collection.json` for the `bikinis` collection)
Standard collection/shop page filtered to the Bikinis collection. Filters: style, color, size, price. Product cards with quick-add, wishlist, color dots.

### 2.5 Lingerie (`collection.json` for the `lingerie` collection)
Same collection template, lingerie collection.

### 2.6 Payment Page
Clarify intent — Shopify owns the actual checkout (PCI-compliant, not custom-built). This "payment page" should be a **trust/payment-info content page** (`templates/page.payment.json`):
- Accepted methods (Visa, Mastercard, Amex, Discover, PayPal, Apple Pay, Shop Pay).
- Security/SSL trust messaging.
- US billing, currency, tax note.
- Link into the real Shopify checkout.
> Do NOT build a custom card-capture form. Payments flow through Shopify's hosted, PCI-DSS Level 1 checkout. A custom payment form would be a compliance liability.

### 2.7 Sizing Page (`templates/page.sizeguide.json`)
Size guide XXS–3XL with an **interactive fit recommender** (enter measurements → recommended size). Pull fit context from `model_sizing`. Size chart table + measuring instructions.

### 2.8 Affiliates Page (`templates/page.affiliates.json`)
Public-facing recruitment + **application form**.
- Pitch: commission rates (10% standard, 12% Silver, 15% Gold per the build doc), perks, how it works.
- **Application:** embed the UpPromote registration portal (iframe or hosted subdomain, CSS-matched to brand) — do not build a custom applicant DB; UpPromote owns applicant intake, approval, tracking, payouts.
- Set expectation that applications are reviewed/approved by the owner.

### 2.9 Social Media Page + Home Feed Block (NEW)
Two parts:
- **Dedicated social page** (`templates/page.social.json`) — gallery of social posts / UGC, shoppable where possible.
- **Home page feed block** (§2.1 item 7) — a curated presentation strip of recent Instagram/TikTok posts on the homepage.

**Build approach:** Use a UGC/social app (e.g. a Shopify-compatible Instagram feed app) OR a metaobject `social_post` (image, caption, link, optional product tag) for full owner control without API rate-limit headaches. Recommend the metaobject route at launch for reliability, app route if live auto-sync is required. Flag API/token setup as owner task.

### 2.10 Products Page (`templates/collection.json` — "all products" / catalog)
The master shop page showing the full catalog with filtering across all collections. Distinct from the individual product detail template.

> Also required (implied, standard e-commerce): **Product detail page** (`templates/product.json`) — image gallery, size selector, color options, add-to-cart, care/fabric/coverage accordions from metafields, model-sizing note. This was in the original 5-page scope; keep it.

---

## 3. US Positioning Checklist

Apply across the build:
- **Currency:** USD primary. Shopify Markets can add others later.
- **Shipping:** US domestic defaults; free-shipping threshold in USD (e.g. $75).
- **Tax:** Shopify automatic US sales tax (nexus-based). Owner configures nexus states.
- **Copy:** Replace "Made in Australia since 1994" with US line `[PLACEHOLDER — US founding/positioning copy]` per the Open Decision above.
- **Legal/compliance:** CCPA (and broader US state privacy) for data; TCPA for SMS opt-in (explicit checkout checkbox + signup form, quiet hours enforced); US-compliant Terms, Privacy, and Return policies (owner to obtain via legal counsel — out of build scope).
- **Support hours / contact:** US time zone, US contact details.
- **Payment methods:** include Shop Pay, Apple Pay, PayPal, major US cards + Discover.

---

## 4. Klaviyo Flows to Wire (from build doc)
Welcome Series · Abandoned Cart · Browse Abandon · Post-Purchase · Win-Back · VIP Early Access · Back in Stock. SMS TCPA-compliant, quiet hours 9am–9pm local.

## 5. UpPromote Setup
Tiers: Standard 10% / Silver 12% (auto at $2,500/mo) / Gold 15% (auto at $5,000/mo) / Ambassador 15% + product / Customer Referral 5%. Attribution: cookie (30d) + discount code, code priority. Fraud: self-referral block, IP clustering, 14-day hold.

## 6. GA4
Enhanced e-commerce events (view_item, add_to_cart, begin_checkout, purchase, view_item_list, select_item). Custom dimension `influencer_code`. UTM convention: `utm_source=influencer`, `utm_medium=referral`, `utm_campaign={influencer_name}`.

---

## 7. Things to Confirm With Owner Before / During Build
1. **Australia vs US brand story** (Open Decision above) — blocks About + Home copy.
2. **Activewear**: nav lists it but it's not in your requested page list — keep the collection or drop it?
3. **Models page**: metaobject-driven (recommended) vs hardcoded? Confirm the 10-model cap is a hard cap or just current.
4. **Social feed**: live auto-sync (app + API tokens) vs curated metaobjects (recommended for launch)?
5. **Affiliates intake**: confirm UpPromote-hosted form is acceptable vs a custom-styled embed.
6. **Domain**: which `.com` to register (US-appropriate).
7. **Sale collection**: confirmed as a page/collection.
8. **Content**: product photos, model photos, copy, pricing — owner-provided (out of build scope per proposal).

## 8. Suggested Additions You Didn't List (recommend including)
- **Product detail template** (essential — added in §2.10 note).
- **Cart / mini-cart drawer** (essential UX).
- **Search** (Shopify search or Search & Discovery app).
- **Contact page + FAQ** (footer links to them; reduces support load).
- **Policy pages**: Shipping & Returns, Privacy, Terms, Care Instructions (footer already references these).
- **Account / login** (Shopify customer accounts).
- **404 + cart empty states.**
- **Cookie/consent banner** (CCPA-compliant).