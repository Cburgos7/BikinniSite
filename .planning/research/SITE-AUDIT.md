# Live storefront audit — velvet-tide-2.myshopify.com

**Date:** 2026-08-22
**Scope:** read-only diagnosis of the public storefront (663 active products, trading as "Velvet Tide").
**Method:** live HTTP fetches (`curl`), the public `products.json` / `collections.json` endpoints,
authenticated Admin GraphQL reads via `data/suppliers/elegant-moments/push_products.py`, and reading
the theme source to attribute causes. No purchase was completed. No theme file was changed.

**Excluded by instruction (already being handled, not re-reported):** the three 404 policy pages and
the footer links to them; the home-page testimonials; `klaviyo_company_id` /`upromote_merchant_id`
placeholders; the 10 imageless draft hosiery products; the empty `sale` collection; shipping rates.

---

## Verdict

**Yes — there are defects that stop a customer completing a purchase, and they are the largest
findings in this audit.**

The single biggest is that **55% of the catalogue (363 of 663 products) cannot be added to the cart
at all**. The second is that **the price shown on a product page is not the price charged**: 204
variants across 88 products cost more than the PDP displays, by up to $16.00. The third is that on
multi-colour products the shopper can be given **a different colour than the one the page says is
selected**.

None of these are edge cases. They are structural, they affect the default path, and a real shopper
hitting the store today will meet at least the first one within a few clicks.

All four Tier 1 findings share one root cause: **variant selection state is split across two
handlers in `assets/pdp.js` that each own half of it, with no single function that recomputes and
re-renders everything after a change.** Fixing that one structural problem addresses 1.1 through 1.4
together. It is one job, not four.

Below Tier 1, the store reads as unfinished rather than broken: the home page prints an
instruction meant for the shop admin, the cart drawer states a false shipping figure on every page,
all four product-detail accordions render on zero of 663 products, and search does nothing at all
when tapped on a phone.

**Structure of this document.** Tier 1 is what stops a sale. Tier 2 is what makes the store look
unfinished or states something untrue. Tier 3 is SEO, accessibility and analytics. A "Checked and
found healthy" section lists everything explicitly verified as working, so the absence of a finding
above is meaningful — including one thing this audit initially got wrong and corrected
(the custom cursor *is* correctly hidden on touch devices).

---

# TIER 1 — Breaks a purchase

## 1.1 — 363 of 663 products (55%) can never be added to the cart

**What is wrong.** On every product that has no `Size` option, the Add to Cart button ships from the
server in the `disabled` state with the label **"Select a Size"**, and there is no size selector on
the page to click. Nothing in the JavaScript can ever enable it. The product is unbuyable from its
own product page.

**Evidence.**

Live markup, identical on `/products/em-8005` (one-size dress), `/products/em-1836b` (hosiery) and
`/products/em-l9997` (leather):

```html
<button id="pdp-add-to-cart" type="button" disabled
  class="w-full bg-deep text-cream ... cursor-not-allowed opacity-60"
  data-variant-id="" aria-label="Add to cart">Select a Size</button>
```

Count of `data-size-swatch` elements on those same pages: **0**. Count of colour swatches: 1.

Catalogue-wide count from `products.json`:

```
NO SIZE OPTION (ATC can never enable): 363 / 663  (55%)
   variants affected: 420
   option names in catalogue: {'Color': 663, 'Size': 300}
```

The variants are real and purchasable — `POST /cart/add.js {"id":53740922765606}` for `em-8005`
returns HTTP 200 and the item appears in `/cart.js`. The product is sellable; the page just refuses
to sell it.

**Likely cause.** `sections/product-main.liquid:151-158` renders the button with a hardcoded
`disabled` attribute and the copy "Select a Size". The only code that ever removes `disabled` is
inside `initSizeSwatches()` (`assets/pdp.js:174-180`), which binds to `[data-size-swatch]` elements.
When `product.options_with_values` contains no option literally named `Size`, the size block at
`sections/product-main.liquid:118-147` does not render, so no size button exists, so the enabling
branch is unreachable. `initColorSwatches()` (`assets/pdp.js:107-140`) resolves and stores
`selectedVariantId` but never touches `addToCartBtn.disabled`.

**Suggested fix.** Move the enable/disable decision into one function that runs on init and after
every selection change, keyed on whether `findVariant()` resolved an available variant — not on
whether a size button was clicked. On a single-variant product it should resolve immediately at page
load and render as enabled. The button's initial server-side label should also branch: "Select a
Size" only when a size selector is actually present.

---

## 1.2 — The price on the product page is not the price charged

**What is wrong.** The PDP prints `product.price` — Shopify's *minimum* variant price — once,
statically. It never updates when the shopper picks a size. On products where plus sizes cost more,
the page advertises the straight-size price and the shopper is charged the plus-size price at
checkout without ever seeing it change.

**Evidence.** `/products/em-11022` renders:

```html
<div class="mt-3">
  <span class="font-body text-sm font-semibold tracking-wide text-deep">$35.95</span>
</div>
```

That is the only price node on the page. The variant data on the same page shows `Black / 4X` at
`$40.95`. Adding that variant confirms the charge:

```
POST /cart/add.js {"id":53740297355558}  -> 200
GET  /cart.js
  Charmeuse kimono robe — Style 11022 - Black / 4X | qty 1 | price 4095
  Charmeuse kimono robe — Style 11022 - Black / S  | qty 1 | price 3595
```

Page said $35.95. Cart says $40.95.

Catalogue-wide:

```
PRICE VARIES BY VARIANT: 88 products
   largest understatement: $16.00 on em-l8103
   total variants sold at a price higher than the one displayed: 204
```

**Likely cause.** `sections/product-main.liquid:72-77` emits `{{ product.price | money }}` with no
`id`/`data-` hook, and `assets/pdp.js` contains no price-update code at all — `initSizeSwatches()`
and `initColorSwatches()` update the button, the label and the ring state, but never the price.

**Suggested fix.** Give the price node an id, and update it from `variant.price` in the same place
`selectedVariantId` is set. Until then, at minimum render `From {{ product.price | money }}` when
`product.price_varies`, so the number is not stated as fact. The product card
(`snippets/product-card.liquid:150-155`) has the same issue and the same fix — a "From" prefix is
the conventional treatment there.

---

## 1.3 — The wrong colour is silently added to the cart

There are two independent paths to this, both live.

### Path A — no colour is actually selected on page load

**What is wrong.** The page renders the first colour as visually selected — swatch ringed, label
filled in — but the JavaScript's `selectedColor` is `null`. If the shopper accepts that apparent
default and just clicks a size, `findVariant()` searches with colour unconstrained and returns the
*first variant in the array* carrying that size, which may be a different colour entirely.

**Evidence.** `/products/em-11022` renders `<span id="selected-color-label">Baby Pink</span>`.
Baby Pink exists only in 1X/2X/3X/4X — there is no Baby Pink S. The size row nonetheless renders
`S` as available. Clicking `S` calls `findVariant('S', null)`:

```js
const findVariant = (size, color) => {
  return variantsData.find((v) => {
    const opts = v.options || [];
    const sizeMatch  = size  ? opts.some((o) => o === size)  : true;
    const colorMatch = color ? opts.some((o) => o === color) : true;   // color is null -> true
    return sizeMatch && colorMatch;
  });
};
```
— `assets/pdp.js:29-36`

`.find()` returns the first match, which for `em-11022` is `Black / S` (id `53740297158950`). The
page still says "Color: Baby Pink". Add to Cart adds Black.

Products where the default-labelled colour does not cover every offered size — i.e. where this
misfires:

```
DEFAULT-LABELLED COLOUR MISSING SOME OFFERED SIZES: 10 products
  em-11022 Baby Pink missing ['L','M','S']
  em-4333  Baby Pink missing ['2X','3X']
  em-1715  Beige     missing ['Q/S']
  em-1622  Black     missing ['O/S']
  em-1610  Black     missing ['O/S']
  em-1601  Nude      missing ['Q/S']
  em-12106 Black     missing ['Q/S']
  em-v6169 Black     missing ['L']
  ... (10 total)
```

### Path B — switching colour does not re-validate, and leaves the old variant armed

**What is wrong.** `initColorSwatches()` only updates `selectedVariantId` when a variant is found.
When the newly chosen colour has no variant in the currently selected size, the handler updates the
label and the ring but leaves `selectedVariantId` and `data-variant-id` pointing at the **previous
colour's** variant, and leaves the button enabled and reading "Add to Cart".

**Evidence.** `assets/pdp.js:127-137`:

```js
const variant = findVariant(selectedSize, selectedColor);
if (variant) {
  selectedVariantId = variant.id;
  if (addToCartBtn) addToCartBtn.dataset.variantId = selectedVariantId;
  ...
}
// no else branch — nothing is disabled, nothing is cleared
```

Reproduction on `/products/em-11022`: click `S` (resolves Black/S, button enables) → click `Purple`
(resolves Purple/S, fine) → click `Baby Pink` (no Baby Pink S exists; `variant` is `undefined`).
Button still says "Add to Cart", label says "Baby Pink", `data-variant-id` still holds Purple/S.
Clicking adds **Purple**.

**Likely cause (both paths).** Variant resolution is spread across two handlers that each own half
the state, with no shared "recompute and re-render everything" step, and no `else` branch on the
colour path. `findVariant` is also positionally naive — it uses `opts.some()` rather than matching
option index — which is why an unset colour degrades to "any colour" instead of "no match".

**Suggested fix.** Initialise `selectedColor` from the rendered `selected_value` on load so the
JS state matches what the page displays. Collapse both handlers into a single
`updateSelection()` that recomputes the variant, and always applies the full result — price, image,
button state, `data-variant-id` — including clearing it when no variant matches. Match options by
index (`v.options[colorIndex]`) rather than `some()`.

---

## 1.4 — Size buttons advertise sizes the selected colour does not come in

**What is wrong.** The size row is rendered server-side and marks a size available if *any* variant
of the product has it, ignoring colour entirely. The shopper sees seven live size buttons on
`em-11022` when no single colour offers all seven. When they pick a combination that does not exist,
the page tells them it is **"sold out"** — which is false; it was never made in that colour — and
offers a back-in-stock signup for a variant that does not exist.

**Evidence.** `sections/product-main.liquid:125-143`:

```liquid
{%- for variant in product.variants -%}
  {%- if variant.option2 == size_value or variant.option1 == size_value -%}
    {%- if variant.available -%}{%- assign size_available = true -%}{%- endif -%}
```

Live output on `/products/em-11022` — all seven sizes rendered with
`data-size-available="true"`, none disabled:

```html
<button ... data-size-value="1X" data-size-available="true" data-size-swatch>1X</button>
... S, M, L, 1X, 2X, 3X, 4X all identical ...
```

Actual matrix: Baby Pink = 1X–4X only. Burgundy = S,M,L,3X,4X (no 1X, no 2X). Black = all seven.

```
COLOUR x SIZE MATRIX INCOMPLETE: 21 of 300 two-option products
```

The false "sold out" copy comes from `assets/pdp.js:192` — `unavailableMsg.textContent =
selectedSize + ' is sold out'` — which is the catch-all for "no variant resolved", conflating
*out of stock* with *does not exist*.

**Suggested fix.** Recompute size availability client-side against the selected colour on every
colour change, and disable sizes not offered in that colour. Distinguish the two failure modes in
copy: "Not available in <colour>" vs "Sold out".

---

# TIER 2 — Looks unfinished / erodes trust

## 2.1 — The home page prints admin instructions to shoppers

Under the heading **"As Seen On"**, the live home page renders:

> Add social posts in Shopify admin under Content → Metaobjects → Social Post.

**Evidence.** Live `/` HTML, inside `id="shopify-section-template--27881044640038__social-feed"`.
Source: `sections/social-feed.liquid:38`, the empty-state branch of
`{%- assign posts = shop.metaobjects.social_post.values -%}` (`:11`).

**Cause.** The `social_post` metaobject definition **does not exist in the shop at all**. Admin
GraphQL `metaobjectDefinitions` returns only:

```
shopify--care-instructions count=0
model                      count=0
shopify--size              count=6
testimonial                count=1
```

So it can never populate. The same emptiness hollows out `/pages/social` ("Nothing to see yet.").

**Suggested fix.** The empty state must be shopper-facing or the section must render nothing. Given
FTC and brand risk, rendering nothing is the safer default — the same choice
`sections/testimonials.liquid` documents at `:17`.

---

## 2.2 — "You're $0.75 away from free shipping!" on every page

The cart drawer is in the DOM on every page. With an empty cart it reads:

```html
<p id="shipping-bar-text" ...>You're $0.75 away from free shipping!</p>
```

alongside `Subtotal $0.00`. It should say $75.00.

**Cause.** `sections/cart-drawer.liquid:49-50`:

```liquid
{%- assign remaining = threshold | minus: cart_total_dollars -%}
You're ${{ remaining | money_without_currency }} away from free shipping!
```

`remaining` is in **dollars** (75); `money_without_currency` treats its argument as **cents**, so 75
renders as `0.75`. The JS re-render path (`assets/cart-drawer.js:259`) does the arithmetic correctly
with `.toFixed(2)`, so first paint and every subsequent update disagree.

**Suggested fix.** `{{ remaining | times: 100 | money_without_currency }}`, or drop the filter and
format the dollars directly.

**Related, unverified:** the drawer, the announcement bar and the home ticker all promise free
shipping over $75. Shipping rates could not be read (no `read_shipping` scope), so **whether a $75
free-shipping rate actually exists in Shopify Shipping is unconfirmed**. If it does not, checkout
will contradict a promise made on every page. Worth confirming before launch.

---

## 2.3 — All four PDP metafield accordions render on zero products

The Care Instructions / Fabric Composition / Coverage Level / Model Sizing accordions are the PDP's
entire detail surface below the buy box. They render on **none** of the 663 products.

**Evidence.** Zero `data-accordion-trigger` elements on every PDP sampled (`em-11022`, `em-11025`,
`em-8005`, `em-1836b`, `em-l9997`). Admin GraphQL confirms the definitions exist but no product
carries a value:

```
product metafield DEFINITIONS:
  custom.care_instructions  (multi_line_text_field)
  custom.model_sizing       (single_line_text_field)
  custom.fabric_composition (single_line_text_field)
  custom.coverage_level     (single_line_text_field)

metafield VALUES (8-product sample): NO custom METAFIELDS on any
```

**Cause.** The definitions were created but the product import
(`data/suppliers/elegant-moments/push_products.py`) never populates them. Note that the supplier
description already carries fabric composition inline — `<strong>Fabric:</strong> 100% Polyester` —
so `custom.fabric_composition` is derivable from data already in hand.

**Suggested fix.** Backfill `fabric_composition` and a care string from the supplier feed during
import (both are parseable from `body_html`); decide whether `coverage_level` and `model_sizing` are
worth curating or should be dropped from the template. Do not leave four dead accordions in the
theme.

---

## 2.4 — Colour swatches never change the photo, on any product

Clicking a colour on a PDP updates the label and the ring but never the image, even on products that
carry a full per-colour photo set.

**Evidence.** `/products/em-11022` ships **22 images** covering six colours
(`11022_f.jpg`, `11022_f_burgundy.jpg`, `11022_f_fuchsia.jpg`, `11022x_f_white.jpg`, …). Every
colour selection shows the same photo.

The image-swap code is conditional on variant-level images:

```js
if (mainImageWrap && variant.featured_image?.src) { ... }
```
— `assets/pdp.js:133`

and **no variant in the store has one**:

```
VARIANTS WITH NO featured_image: 1485 / 1485
multi-colour products that DO have per-colour photos in the gallery: 70
```

The product card has the same dead wiring —
`data-variant-image="{{ variant.featured_image | image_url: width: 600 }}"`
(`snippets/product-card.liquid:134`) resolves to an empty string on every card, and no JS reads
`data-swatch-color` at all (grep of `assets/` returns nothing), so the card swatches are inert
decoration.

**Suggested fix.** Either assign variant images during import (the filenames already encode the
colour — `11022_f_burgundy.jpg`), or map colour → gallery index client-side from the image alt/filename
and drive the swap from the existing gallery. Also remove the card swatch handlers that nothing
listens to, or wire them up.

---

## 2.5 — "Quick Add" adds an arbitrary size without telling the shopper

Every product card carries a Quick Add button that posts the product's **first available variant**
with no selection UI.

```liquid
{%- assign first_variant = product.first_available_variant -%}
<form action="/cart/add" method="post" class="absolute bottom-0 left-0 right-0">
  <input type="hidden" name="id" value="{{ first_variant.id }}">
```
— `snippets/product-card.liquid:81-93`

On `em-11022` that is **Baby Pink / 1X**. A shopper browsing the Best Sellers rail who clicks Quick
Add gets a specific plus size in a specific colour they never chose. It is also a native form POST,
so it navigates away to `/cart` rather than opening the drawer — inconsistent with every other
add-to-cart path in the theme.

**Suggested fix.** Restrict Quick Add to genuinely single-variant products (which, given 1.1, are
also the ones with no other way to buy), or turn it into a quick-view that surfaces the selectors.

---

## 2.6 — The `/cart` page has no quantity control

The cart drawer has +/− controls; the standalone cart page has only "Remove". A shopper who lands on
`/cart` — from Quick Add, from a bookmark, or with JS disabled — cannot change quantity at all.

**Evidence.** Live `/cart` with three items renders per line only:
`… $40.95  Remove`. Source `sections/main-cart.liquid:25-27` contains a single
`<a href="{{ item.url_to_remove }}">Remove</a>` and no quantity input.

Removal is also a bare `GET` link (`/cart/change?id=…&quantity=0`), which is vulnerable to link
prefetching. `robots.txt` disallows `/cart/` so crawlers are covered, but browser/extension prefetch
is not.

**Suggested fix.** Add a quantity input to the cart line item and submit via the existing form.

---

## 2.7 — Product descriptions render as an unstyled run-on block on all 663 PDPs

Every supplier description is a `<p>` followed by a `<ul>` of Fabric / Made in / Brand. Tailwind's
preflight strips list markers and all margins, and the theme has no typography plugin and no
compensating rules, so the three bullets render flush-left, unmarked, with no space from the
paragraph above.

**Evidence.** Compiled CSS contains `ol,ul,menu{list-style:none;margin:0;padding:0}` and **no**
`.prose` rules. The PDP wrapper (`sections/product-main.liquid:81`) applies only
`font-body text-sm text-mid leading-relaxed`. Markup being rendered:

```html
<p>Charmeuse kimono robe with 3/4 sleeves and detachable belt.</p>
<ul> <li> <strong>Fabric:</strong> 100% Polyester</li>
     <li> <strong>Made in:</strong> Vietnam</li>
     <li> <strong>Brand:</strong> Elegant Moments</li> </ul>
```

The same gap hits `/pages/care-instructions`, which uses `prose-headings:text-deep`,
`prose-headings:font-normal` and `prose-headings:font-display` — **none of which have any rule in the
compiled stylesheet** (they are `@tailwindcss/typography` modifiers and the plugin is not installed;
`tailwind.config.js` has `plugins: []`).

**Suggested fix.** Add a small scoped rich-text rule set (`ul{list-style:disc;padding-left:1.25rem}`,
`p+ul{margin-top:.5rem}`, `li{margin-top:.25rem}`) applied to description and page-content wrappers.
Install the typography plugin or replace the three `prose-headings:*` classes with arbitrary variants.

---

## 2.8 — Header navigation omits Hosiery (184 products) and Costumes

The header nav is driven by
`new-in,lingerie,swimwear,leather-vinyl,plus-size,menswear,sale`
(`sections/header.liquid:41`). The footer is driven by a *different* hardcoded list that includes
`hosiery` and `costumes` (`sections/footer.liquid:18`). So **Hosiery — 184 products, 28% of the
catalogue — has no header entry** on desktop or mobile, while the footer and the home category grid
both link to it.

**Suggested fix.** One shared list. Add `hosiery` and `costumes` to it.

---

## 2.9 — The size chips on the home "Find Your Perfect Fit" banner look clickable but are not

Eight chips (S M L XL 1X 2X 3X 4X) render as `<span>` with `cursor-pointer` and a coral hover state,
with no `href` and no handler.

```liquid
<span class="border border-cream/30 px-3 py-1 ... hover:border-coral hover:text-coral
             transition-colors cursor-pointer">{{ size }}</span>
```
— `sections/sizing-banner.liquid:11-13`

**Suggested fix.** Either link each chip to the corresponding size filter, or drop `cursor-pointer`
and the hover state so they read as a static list.

---

## 2.10 — Four products whose only photograph is a back view

`em-v2306`, `em-l9420`, `em-l9161`, `em-l7136` each have exactly one image and it is a back shot
(`v2306_b.jpg`, `l9420_b.jpg`, `l9161_b_black.jpg`, `l7136_b.jpg`). The card thumbnail, the PDP hero
and the Open Graph image are all the back of the garment; the shopper cannot see the front at any
point.

**Suggested fix.** Same treatment as the 10 imageless hosiery products — set to draft until the
supplier ships a front shot, or accept and annotate.

---

## 2.11 — 8px cream stripe between the header and the announcement bar below 1024px

`<body>` carries `pt-16` (`padding-top: 4rem` = 64px) but the fixed header is `h-14` (56px) until the
`lg` breakpoint, where it becomes `h-16`. Both the header and the announcement bar are `bg-deep`,
so the 8px of uncovered `bg-cream` body reads as a pale stripe across the very top of every page at
**375px and 768px** — both widths named in the audit brief.

**Evidence.** `layout/theme.liquid:97` `class="bg-cream ... pt-16"`; `sections/header.liquid:1`
`class="fixed top-0 ... h-14 lg:h-16"`. Compiled CSS confirms `.pt-16{padding-top:4rem}`,
`.h-14{height:3.5rem}`, and no `md:h-16` rule exists.

**Suggested fix.** `pt-14 lg:pt-16` on the body, matched to the header ladder.

---

## 2.12 — Tapping the search icon does nothing on mobile and tablet

`#nav-search-toggle` renders at every width (`sections/header.liquid:85-93`), but the bar it opens is
`hidden lg:flex` (`:60`). `openSearch()` removes only `hidden`, `opacity-0` and `pointer-events-none`
(`assets/inline-search.js:6`) — below 1024px the `hidden` class is what `lg:flex` overrides, so
removing it has no effect and the bar stays `display:none`. **On phones and tablets the search icon
is a dead control**; search is reachable only by typing `/search` into the address bar.

**Suggested fix.** Give the mobile toggle its own target — a full-width search field in the mobile
nav drawer, or an overlay — rather than the desktop inline bar.

---

## 2.13 — `autofocus` steals focus into an invisible field on every desktop page load

The collapsed inline search input carries `autofocus` (`sections/header.liquid:68`). At 1024px and
up its container is `lg:flex` — **not** `display:none`, just `opacity-0 pointer-events-none` — so the
attribute fires normally and focus lands in a zero-opacity field on every page load.

That field is also one of only two controls in the entire theme that use `focus:outline-none` with
**no replacement indicator**, so nothing is visible anywhere on screen. Consequences: the skip link
is no longer the first Tab stop, keyboard users see no focus at all until they Tab past it, and
screen readers announce "Search products, edit" instead of the page.

**Suggested fix.** Remove `autofocus` from the markup and call `input.focus()` inside `openSearch()`,
which `assets/inline-search.js:9` already does.

---

## 2.14 — Favicon and apple-touch-icon are 404

```
https://velvet-tide-2.myshopify.com/favicon.ico          -> 404
https://velvet-tide-2.myshopify.com/apple-touch-icon.png -> 404
```

There is no `<link rel="icon">`, `rel="apple-touch-icon">` or `rel="manifest">` in any page head —
`layout/theme.liquid` has no favicon block and the theme exposes no `favicon` setting. Every browser
tab, bookmark and home-screen shortcut falls back to a blank page glyph.

---

## 2.15 — Product cards emit invalid HTML: an `<a>` and a `<form>` nested inside an `<a>`

`snippets/product-card.liquid:13` opens `<a href="{{ product.url }}">` and does not close it until
`:103`. Inside that anchor sit the wishlist link (`:68-76`) and the Quick Add form and submit button
(`:83-93`). Live markup from `/collections/lingerie`:

```html
<a href="/products/em-12087" class="block">
  ...
  <a href="/account/login?return_url=%2Fproducts%2Fem-12087"
     aria-label="Add Fence net cami top — Style 12087 to wishlist"> ... </a>
  <form action="/cart/add" method="post" class="absolute bottom-0 left-0 right-0">
    <input type="hidden" name="id" value="53741502562598">
    <button type="submit" ... data-quick-add>Quick Add</button>
  </form>
</a>
```

`<a>` may not contain interactive content. The HTML parser implicitly closes the outer anchor at the
nested one, so the DOM the browser builds differs from the source and the card's clickable region
becomes browser-dependent. This affects **every card on the site** — 24 per collection page, 62 on
the home page, and the entire search grid.

**Suggested fix.** Take the wishlist link and the Quick Add form out of the anchor and position them
as siblings inside the same `relative` container.

---

## 2.16 — Catalogue data blemishes visible to shoppers

- **`Q'S` size value** — one product carries `Q'S` (apostrophe) where every other queen-size product
  uses `Q/S`. It renders as a distinct, mistyped size button.
- **`em-11025` image filenames are merged from two supplier styles** —
  `11025_f_white-82459_f_turquoise.jpg`. The colour option says "White" only. Whether the photo
  actually shows the white garment is unverified; the filename suggests the scrape concatenated two
  products' names and the wrong photo may be attached.
- **Three products offer more colours than they have photos** — `em-3555` (6 colours, 2 images),
  `em-2990` (5 colours, 1 image), `em-2569` (8 colours, 2 images). Combined with 2.4, most colours on
  these are unillustrated.

---

# TIER 3 — SEO, accessibility, analytics, nice to have

## 3.1 — No Open Graph, no Twitter card, no structured data anywhere

Grep of `layout/`, `sections/`, `snippets/` for `og:`, `twitter:`, `canonical`, `application/ld+json`
returns **zero hits**. The theme never renders social meta or schema.org. Confirmed against live HTML:

| Page | Open Graph | Twitter | JSON-LD | microdata |
|---|---|---|---|---|
| `/` | **none** | none | 0 | 0 |
| `/collections/lingerie` | **none** | none | 0 | 0 |
| `/products/em-11022` | `og:image` family only | none | 0 | 0 |
| `/search?q=lace` | none | none | 0 | 0 |
| `/cart` | none | none | 0 | 0 |

The only OG tags anywhere are the five Shopify injects on PDPs via `content_for_header` —
`og:image`, `og:image:secure_url`, `og:image:width`, `og:image:height`, `og:image:alt`. There is no
`og:title`, `og:description`, `og:url`, `og:type` or `og:site_name` on any page, and no `twitter:*`
at all. `BreadcrumbList` returns 0 matches on all four page types.

Consequences. A home-page or collection link shared on Instagram, TikTok, Facebook, WhatsApp, Slack
or iMessage renders **with no image and a scraped fallback title** — directly material for a brand
whose stated growth strategy is influencer-driven. And with no `Product` JSON-LD, none of the 663
products is eligible for price/availability rich results or Google Merchant free listings.

`<link rel="canonical">` **is** present and correct on every page type (Shopify-injected).

**Suggested fix.** Add an OG/Twitter block to `layout/theme.liquid` head branching on
`request.page_type`, and a `Product` + `Offer` JSON-LD block to `sections/product-main.liquid`.
Add `Organization` and `WebSite` on the home page.

## 3.2 — `<meta name="description">` is missing on every page except products

| URL | `<title>` | meta description |
|---|---|---|
| `/` | `Velvet Tide` | **absent** |
| `/collections/lingerie` | `Lingerie – Velvet Tide` | **absent** |
| `/collections/lingerie?page=2` | `Lingerie – Velvet Tide` *(identical to page 1)* | **absent** |
| `/collections/swimwear` | `Swimwear – Velvet Tide` | **absent** |
| `/search?q=lace` | `Search: 164 results found for "lace" – Velvet Tide` | **absent** |
| `/cart` | `Your Shopping Cart – Velvet Tide` | **absent** |
| `/pages/about` | `About Us – Velvet Tide` | **absent** |
| `/pages/contact` | `Contact – Velvet Tide` | **absent** |
| `/products/em-11022` | `Charmeuse kimono robe — Style 11022 – Velvet Tide` | present, auto-derived (see 3.3) |

The theme is behaving correctly — `layout/theme.liquid:16-18` emits the tag only when
`page_description` is non-blank. The *content* is missing: no SEO description has been set on the
shop, the collections or the pages in Shopify admin.

Two specifics worth calling out. The home `<title>` is literally **`Velvet Tide`** with no
descriptor — `layout/theme.liquid:11-13` falls through to `{{ shop.name }}` — so the
highest-authority page on the domain wastes its title tag entirely. And `?page=2` carries a
byte-identical title to page 1, which reads as templated duplication.

## 3.3 — Duplicate content: a ranking ceiling, not a penalty

All 663 descriptions are Elegant Moments supplier copy verbatim, e.g.
`/products/em-11022`: *"Charmeuse kimono robe with 3/4 sleeves and detachable belt."* plus a
Fabric / Made in / Brand list. Every other retailer carrying these SKUs publishes the identical text,
and it is also what Shopify feeds into the auto-generated meta description.

**The exposure is wider than "just the descriptions", for three compounding reasons.**

1. **The meta description is derived from the same duplicated body.** On `em-11022`:
   `<meta name="description" content="Charmeuse kimono robe with 3/4 sleeves and detachable belt.
   Fabric: 100% Polyester Made in: Vietnam Brand: Elegant Moments">` — that is `body_html` with the
   tags stripped, Shopify's fallback because no SEO description was set. Body copy *and* SERP snippet
   are both supplier-identical.
2. **Titles are also supplier-derived.** The pattern is `<supplier product name> — Style <supplier
   SKU>`: `Charmeuse kimono robe — Style 11022`, `Fence net cami top — Style 12087`,
   `Zig zag crochet net cami top and matching leggings — Style 12082`. The style number is the
   Elegant Moments SKU and the descriptive part is their catalogue name, so a competitor searching
   "11022 Elegant Moments" surfaces the identical string. (All 663 titles *are* unique to each other
   — there is no internal duplication — but they are not unique to the web.)
3. **The alt text carries the supplier name too** (3.5), so image search offers no differentiation
   either, and there is no compensating unique signal anywhere: no reviews, no `aggregateRating`, no
   JSON-LD, no editorial copy. Each PDP's only genuinely unique text is its price.

Internal duplication is negligible: only 22 groups share an identical description body, at most 3
products per group.

**Calibrated risk assessment.** This is a **ranking-ceiling problem, not a penalty**. There is no
duplicate-content penalty for reseller copy. What actually happens is canonicalisation and filtering:
for a query like *"charmeuse kimono robe 3/4 sleeves detachable belt"*, Google picks one URL per
cluster of near-identical pages and omits the rest. Selection is driven by domain authority,
backlinks and engagement — a new `.myshopify.com` with none of those loses that selection to every
established retailer carrying the line. Practical outcome: most of the 663 PDPs will be crawled,
indexed, and then never ranked for descriptive queries. They will still rank for brand+SKU queries,
which have essentially no volume. It is an opportunity-cost problem — but at 663 products it is the
entire long tail.

**Suggested fix, ordered by effort-to-impact.** Do not rewrite 663 descriptions; that is not a good
use of effort and is not where the leverage is.
1. **Set a unique SEO meta description per product.** Highest impact per unit of effort — it makes
   the SERP snippet differ even where the body does not, and it can be templated from data already in
   hand (type, fabric, colour range, size range).
2. **Add `Product` + `Offer` JSON-LD** (3.1). Price and availability are genuinely unique to this
   store and give Google a non-duplicated signal.
3. **Drop `Brand: Elegant Moments` from the rendered body** and keep it as a metafield. It is the
   exact string that clusters these pages with every other reseller, and it advertises the supplier
   to competitors.
4. **Rewrite the opening paragraph only, for the ~50 products that carry the merchandising** (Best
   Sellers, the swim range, the category heroes). Two or three unique sentences above the supplier
   spec list is usually enough to break the cluster.
5. Longer term, **add reviews** — user-generated content is the only source of continuously-growing
   unique text, and it feeds `aggregateRating`.

## 3.4 — Colour contrast: nine token pairs fail WCAG AA, three fail even the 3:1 floor

Computed from the actual tokens in `tailwind.config.js`:

| Foreground | Background | Ratio | AA normal (4.5) | AA large / non-text (3.0) |
|---|---|---|---|---|
| `gold` #c9a84c | `cream` #faf6f0 | **2.12:1** | **FAIL** | **FAIL** |
| `border-deep/30` → #b3afaa | `cream` #faf6f0 | **2.03:1** | **FAIL** | **FAIL** |
| `text-deep/40` → #9b9893 | `cream` #faf6f0 | **2.67:1** | **FAIL** | **FAIL** |
| `cream` #faf6f0 | `coral` #e85d3a | **3.22:1** | **FAIL** | pass |
| `coral` #e85d3a | `cream` #faf6f0 | **3.22:1** | **FAIL** | pass |
| `text-mid` #8a7060 | `sand` #f5ede0 | **3.96:1** | **FAIL** | pass |
| `text-mid` #8a7060 | `cream` #faf6f0 | **4.27:1** | **FAIL** | pass |
| `cream` #faf6f0 | `mid` #8a7060 | **4.27:1** | **FAIL** | pass |
| `text-mid` #8a7060 | `deep` #0d0a08 | **4.29:1** | **FAIL** | pass |
| `coral` #e85d3a | `deep` #0d0a08 | 5.69:1 | pass | pass |
| `gold` #c9a84c | `deep` #0d0a08 | 8.64:1 | pass | pass |
| `cream` #faf6f0 | `deep` #0d0a08 | 18.33:1 | pass | pass |

Token values confirmed against `tailwind.config.js:12-19` and against the `:root` custom properties
in the live stylesheet — no drift between source and build.

Where each failure actually bites:

- **`gold` on `cream` at 2.12:1 is the worst.** It fails even the 3:1 large-text floor. This is
  `hover:text-gold`, the hover state for nav and footer links — the moment a user points at a link
  it becomes *less* readable than before.
- **`cream` on `coral` at 3.22:1 is the "PROCEED TO CHECKOUT" button**
  (`sections/cart-drawer.liquid:138`) and the hero primary CTA — the two most important controls on
  the site. Both are 14px semibold, which is *not* "large text" under WCAG (that needs ≥18.66px bold
  or ≥24px), so the 4.5:1 threshold applies and both fail.
- **`text-mid` at 4.27:1** is the body-copy colour for every product description
  (`sections/product-main.liquid:81`, 14px), card subtitles, collection counts and footer copy.
- **`border-deep/30` at 2.03:1** is the border on every text input in the theme, and
  **`text-deep/40` at 2.67:1** is the wishlist heart on every product card. Both fail SC 1.4.11
  Non-text Contrast, which requires 3:1 for UI component boundaries — these are effectively
  invisible to low-vision users.
- The focus ring (`focus-visible:ring-coral`) clears 3:1 on cream at 3.22:1, but with no margin.

**Suggested fix.** Darken `mid` to roughly `#6f5748` (≈6:1 on cream); replace `gold` as a hover token
or reserve it for use on `deep` only; use `text-deep` on coral buttons or darken `coral`; raise the
input border to at least `deep/45` and the wishlist heart to `deep/55`.

## 3.5 — Accessibility defects

**Keyboard operability**

- **The PDP image gallery is entirely unreachable by keyboard.** Every thumbnail is a `<span>` with
  `aria-label` and a click handler but no `role`, no `tabindex` and no key handler
  (`sections/product-main.liquid:23-29` desktop, `:46-52` mobile). The zoom trigger is a bare `<div>`
  (`:10`). On `em-11022` that is **22 thumbnails rendered twice — 44 elements — none focusable**, and
  the lightbox cannot be opened without a mouse. WCAG 2.1.1 failure. (An `aria-label` on a `<span>`
  with no role is also ignored by most assistive tech, so they are not even announced.)
- **Both off-canvas panels stay in the tab order when closed.** `#cart-drawer`
  (`sections/cart-drawer.liquid:9-15`) and `#mobile-nav-drawer` (`sections/header.liquid:129-135`)
  are permanently `role="dialog" aria-modal="true"` and only translated off-screen — neither gets
  `inert` or `aria-hidden` when closed (`closeDrawer()` toggles classes only,
  `assets/cart-drawer.js:134-141`). Their close buttons, quantity controls and the checkout link are
  tabbable from every page, and a dialog that permanently advertises `aria-modal="true"` is always in
  the accessibility tree. The overlays *do* set `aria-hidden="true"` — the intent was there, it was
  applied to the wrong element.
- **Nothing revealed on hover is revealed on focus.** `group-focus-within` is used zero times and
  compiled zero times. The Quick Add button is `translate-y-full group-hover:translate-y-0`
  (`snippets/product-card.liquid:87`), so a keyboard user tabs onto a control that is translated 100%
  below its own slot — focused, but drawn somewhere else.

**Names, roles and state**

- **The Add to Cart button's accessible name contradicts its visible label.** It renders
  `aria-label="Add to cart"` over the visible text `Select a Size`
  (`sections/product-main.liquid:151-158`), and no JS ever updates the `aria-label`. A voice-control
  user saying "click Select a Size" gets nothing. WCAG 2.5.3 (Label in Name) failure.
- **Colour and size selectors expose no selected state.** The chosen swatch differs from the others
  only by the presence of `ring-2 ring-offset-1 ring-deep` — a purely visual cue. No `aria-pressed`,
  no `role="radio"`/`aria-checked`, no `<fieldset>`/`<legend>` grouping. The current selection is
  simply unavailable to assistive tech. WCAG 4.1.2. (Disabled sizes *are* handled correctly, with
  `disabled aria-disabled="true"` at `:138`.)
- **Accordion triggers** carry `aria-label="Expand Care Instructions"`, which overrides the visible
  label and never flips to "Collapse", and have no `aria-controls`. (`aria-expanded` *is* toggled
  correctly.)
- **The two price-filter inputs have no accessible name at all** —
  `<input type="number" placeholder="Min" data-filter-price-min>` and its Max twin
  (`sections/collection-grid.liquid:55, 64`). Placeholder only: no `<label>`, no `aria-label`, no
  association with the `<p>Price</p>` above. These are the only unlabelled form controls in the theme.

**Announcements**

- **Adding to cart is silent; only failure is announced.** The theme's four `aria-live` regions are
  all in `sections/product-main.liquid` and three of them are error or back-in-stock paths. The cart
  badge is explicitly `aria-hidden="true"` (`assets/cart-drawer.js:231`), so the item count is never
  exposed. Collection filtering replaces 24 cards and the result count with no announcement
  (`assets/collection-filter.js:185-198`).
- **Cart quantity changes destroy the focused element.** `renderCart()` does
  `currentCartItems.innerHTML = …` (`assets/cart-drawer.js:289`) and `bindCartItemEvents()` then does
  `cartItems.parentNode.replaceChild(newItems, cartItems)` (`:182-183`) — two focus-destroying node
  swaps per update. Pressing `+` drops focus to `<body>`; a second press requires re-tabbing from the
  top of the page.

**Structure**

- **Heading order starts at `h2` on every page**, because the cart drawer's `<h2>Your Cart</h2>`
  (`sections/cart-drawer.liquid:19`) is rendered in the layout before `<main>`. Extracted in DOM
  order, every page reads `h2 "Your Cart"` → `h1 …`.
- **Collections, PDPs, search, cart, about and contact skip `h1` → `h3`.** Those templates render no
  section headings at all — the PDP accordion triggers are `<button>`s, the collection filter groups
  are `<p>` styled at heading size — so the next heading encountered is the footer's `h3`. Home is the
  only page with a valid inner outline. `/cart` renders `h2 "Your Cart"` and `h1 "Your Cart"`, the
  same string twice.
- **Product card titles are `<p>`, not headings** (`snippets/product-card.liquid:149`), so a
  screen-reader user cannot navigate a 24-item grid by heading.

**Alt text** — zero images are missing an `alt` attribute anywhere (71 on home, 24 on a collection
page, 46 on `em-11022`). The problem is quality, not presence:

- **Every card image names the supplier.** `alt="Fence net cami top by Elegant Moments"` — 24 of 24
  on `/collections/lingerie`, 62 of 71 on home. `snippets/product-card.liquid:34` uses
  `product.featured_image.alt | default: product.title`, and the import populated Shopify's image alt
  field with `"<name> by Elegant Moments"`, so the fallback never fires. Not a WCAG failure, but it
  announces the supplier relationship to every screen-reader user and every image-search crawler, and
  it near-duplicates the visible card text directly below it.
- **PDP galleries repeat one string N times.** `sections/product-main.liquid:14, 33, 56` all pass
  `alt: product.title`, so `em-11022` emits the identical `alt="Charmeuse kimono robe — Style 11022"`
  **45 times**. A screen-reader user arrowing the gallery cannot tell Baby Pink from Burgundy, or
  front from back — even though the per-image alt *does* carry that information.
- **Category cards double-announce.** `snippets/category-card.liquid:21-39` puts the label on the
  anchor's `aria-label`, the image's `alt` and a visible `<span>`. The anchor's `aria-label` wins, so
  the "415 items" count in the overlay is never announced.

## 3.6 — GA4 is loading with a placeholder measurement ID

`config/settings_data.json` ships `"ga4_measurement_id": "G-XXXXXXXXXX"`, and
`layout/theme.liquid:42` guards only on `!= blank`, so every page loads
`googletagmanager.com/gtag/js?id=G-XXXXXXXXXX` and calls `gtag('config', 'G-XXXXXXXXXX')`. All
analytics are discarded. The same `!= blank` guard is why the Klaviyo and UpPromote scripts also
load with their `…_PLACEHOLDER` values — `snippets/cloudinary-img.liquid:32-34` already implements
the correct `contains 'PLACEHOLDER'` check; the layout does not.

Separately, **`begin_checkout` can never fire**: `assets/cart-drawer.js:316` delegates on
`[data-action="checkout"], a[href="/checkout"]`, but the actual button is
`<a id="cart-checkout-btn" href="/cart/checkout">` with no `data-action`.

## 3.7 — Collections offer no size or colour filter

`/collections/lingerie` (415 products) exposes only **Availability** and **Price**. For a store whose
entire positioning is inclusive sizing S–4X, and where a shopper's first question is "does this come
in my size", there is no way to filter by size or colour. This is configured in Shopify admin
(Search & Discovery), not in the theme.

Note this interacts with 1.4 — filtering by size would be misleading today anyway, since the PDP
cannot honour a colour+size combination.

## 3.8 — Minor

- `/search` is fully crawlable (`robots.txt` has no `Disallow: /search`) and search result pages are
  self-canonical — a mild crawl-budget trap.
- `sections/header.liquid:192-197` declares a `free_shipping_threshold` setting the header never
  reads. The $75 figure is independently duplicated in the announcement bar, the ticker (twice) and
  the cart drawer. They agree today; nothing keeps them in sync.
- Cart drawer line items are keyed on `variant_id`, not line-item key — two lines of the same variant
  with different properties would collide.
- `snippets/product-card.liquid:45` and `sections/product-main.liquid:74` both test
  `product.compare_at_price > product.price`. No product in the store has `compare_at_price` set
  (0 of 1485 variants), so the "Sale" badge and strikethrough are permanently unreachable — expected
  while `sale` is empty, but worth knowing they are untested code paths.
- `snippets/cloudinary-img.liquid:46-52` emits a `width` attribute but **no `height`**, so no image
  on the site gives the browser an intrinsic aspect ratio to reserve. This is a cumulative-layout-shift
  source on every page. `assets/carousel.js:87-88` already documents working around the consequence:
  *"Lazy-loaded card images have no height attribute, so the rail's scrollWidth is not final at
  DOMContentLoaded."*
- **No newsletter form renders anywhere on the site** — the home page contains zero email inputs.
  This follows from the placeholder Klaviyo ID (`sections/klaviyo-forms.liquid` has nothing to mount),
  so email capture is not merely inert, it is absent.
- `assets/custom-cursor.js` starts a `requestAnimationFrame` loop that is never cancelled, so a
  desktop page repaints continuously while idle. (The cursor element itself is correctly hidden on
  touch devices — see the healthy list.)

---

# Checked and found healthy

Explicitly verified, so the absence of a finding above is meaningful.

**Build integrity**
- `assets/theme.css` is **not stale**. The live stylesheet was extracted and every class selector
  compared against the committed source: **384 selectors live, 393 local, 0 missing** (the 9-way
  difference is comment/URL noise, not rules). The committed file is byte-identical to the working
  tree and clean in git.
- Every class token appearing in the rendered HTML of 20 live pages was checked for a matching rule:
  **6 unmatched out of 291**, of which 4 are the `prose-headings:*` misuse reported in 2.7 and 2 are
  Shopify's own injected classes (`shopify-section`, `analytics`). Arbitrary values used by the new
  carousel — `w-[42%]`, `sm:w-[30%]`, `md:w-[22%]`, `[&::-webkit-scrollbar]:hidden`,
  `[scrollbar-width:none]`, `aspect-[3/4]`, `line-clamp-2` — all have rules.
- **No broken assets.** All 164 distinct theme asset and CDN URLs across home, PDP, collection and
  About were HEAD-requested: **0 non-200**. Fonts, hero image, product images, JS modules all resolve.
  The `cloudinary_cloud_name` setting is now empty, so `snippets/cloudinary-img.liquid` correctly
  falls back to the Shopify CDN.

**Commerce plumbing**
- `POST /cart/add.js` returns 200 and the correct line item. `GET /cart.js` reflects it. Prices,
  SKUs, grams and currency (`USD`) are all correct in the cart payload.
- `/cart` renders line items, subtotal and a working checkout affordance. The drawer's
  `/cart/checkout` link and the cart page's `<button name="checkout">` both resolve.
- Catalogue integrity: **0 products with zero price, 0 fully sold-out products, 0 products with no
  images, 0 products with an empty description, 0 duplicate titles.** Price range $21.95–$186.95 —
  the $21.95 floor is honoured on every one of 1485 variants.

**Search**
- `/search?q=lace` → 164 results, correct pagination (pages 2..7 linked).
- `/search?q=` → "Enter a search term above to find products."
- `/search?q=zzzznothing` → "No results for 'zzzznothing'. Try a different search term, or browse our
  collections." with a Shop All CTA.
- **Draft products do not leak.** `/products/em-1502`, `/products/em-1721`, `/products/em-1722` all
  return **404**, and searching "knee hi" (which matches draft `em-1502` by title) returns 43 results
  with zero draft handles present.

**Responsive**
- The grid ladder renders as specified: `grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 lg:gap-4`
  on collection pages, and all three rules exist in the compiled CSS.
- The home page carries **3 carousel rails**, all with correct slide widths.
- Carousel arrow suppression below 768px is correctly implemented — `assets/carousel.js:18,63` gate
  on `matchMedia('(min-width: 768px)')` and the buttons ship `hidden` in markup, so they never appear
  on touch widths and nothing dead renders if the module fails. Scrolling is pure CSS scroll-snap and
  needs no JS. `prefers-reduced-motion` is honoured (`:76`).
- The cart drawer is `w-96 max-w-full`, so it does not overflow a 375px viewport.

**Accessibility that is genuinely well built**

Several components are better than the theme's average and should not be touched during fixes:

- **The mobile nav is the best-implemented component in the theme.** `assets/mobile-nav.js` toggles
  `aria-expanded` on the hamburger (`:6`, `:18`), handles Escape (`:68`), moves focus to the close
  button on open (`:10`), **returns focus to the hamburger on close** (`:19`), traps focus with wrap
  (`:30-52`) and locks body scroll. All four keyboard requirements met.
- **The cart drawer's open-state keyboard behaviour is correct** — focus trap with Shift+Tab wrap
  (`assets/cart-drawer.js:17-35`), Escape (`:147-150`), focus to close button on open (`:131`), focus
  returned to the trigger on close (`:140`). Only the *closed* state is wrong (3.5).
- **The collection filter drawer** does the same: focus trap (`:42-55`), `aria-expanded` (`:79`,
  `:102`), focus to close (`:83`), focus returned to opener (`:103`), `aria-controls` on the trigger.
- **Carousel arrows are real `<button type="button">` with descriptive accessible names**
  (`aria-label="Scroll Best sellers left"`), inner SVGs correctly `aria-hidden="true"`, and `hide()`
  applies `display:none` so they leave the tab order when inapplicable rather than lingering as
  invisible focus stops.
- **Off-screen carousel slides behave correctly.** They stay in the tab order, but the rail is
  `overflow-x:auto` with slides merely clipped — not `display:none`, `visibility:hidden` or `inert` —
  so tabbing into an off-screen card triggers the browser's native scroll-into-view and the element
  is visible before it receives focus. This is the right outcome, not a 2.4.7 violation.
- **`prefers-reduced-motion` is honoured** by the carousel (`assets/carousel.js:19, 76`).
- **The contact form is fully labelled** — `for`/`id` pairing on all three fields
  (`contact-name`, `contact-email` with `type="email"`, `contact-body`), all `required`, focus
  indicator replaced via `focus:border-deep`.
- **Both search inputs, the sort dropdown and every cart control have accessible names**
  (`aria-label="Search products"`, `"Sort by"`, `"Decrease quantity"`, `"Remove {title} from cart"`).
  Filter checkboxes use implicit wrapping `<label>`s.
- **Every decorative SVG carries `aria-hidden="true"`** — verified across the header, cart drawer,
  carousel arrows, wishlist heart, empty-cart illustration and accordion chevrons.
- **The PDP lightbox uses a native `<dialog>`** (`sections/product-main.liquid:296-305`), inheriting
  the browser's focus trap, focus restoration and Escape handling, with a labelled close button.
  (It is only reachable by mouse — see 3.5.)
- **The custom cursor is correctly suppressed on touch devices.** `src/css/theme.css:21-22` compiles
  `@media (pointer: coarse){#custom-cursor{display:none!important}}` into the live stylesheet, and
  the element is `aria-hidden="true"`. It does not appear on tablets.
- **No `outline: none` anywhere** in the compiled CSS — 0 occurrences. The only opt-out is Tailwind's
  `.focus\:outline-none:focus{outline:2px solid transparent;outline-offset:2px}`, which preserves a
  Windows High Contrast Mode indicator. A real `:focus-visible` ring compiles and is applied to 14
  elements per page. Exactly two controls opt out with no replacement (3.5).
- **`escapeHtml()` is applied before every `innerHTML` injection** (`assets/cart-drawer.js:47-54`,
  `assets/collection-filter.js:15`) — no XSS vector via product titles or filter labels.
- **Exactly one `<main>` landmark and exactly one `<h1>` per page**, on all 8 page types checked.
  None missing, none duplicated. Both `<nav>` landmarks are labelled.

**Other**
- `robots.txt` and `sitemap.xml` are Shopify defaults and correct; the sitemap index covers products,
  pages, collections and blogs. `sitemap_products_1.xml` returns 664 `<loc>` entries, matching the
  663-product catalogue.
- `<link rel="canonical">` present and correct on all 9 URLs tested, **including the tricky ones**:
  `/collections/lingerie?page=2` self-canonicalises rather than pointing at page 1 (correct), and
  `/search?q=lace` self-canonicalises. `rel="next"` is present on paginated collections.
- **No stray `noindex`.** `<meta name="robots">` count is 0 on home, collection, PDP and search; no
  `x-robots-tag` header; the store is not password-protected.
- `<html lang="en">` on every page. No `hreflang` — correct for a single-locale store.
- 404 handling works: `/pages/does-not-exist` returns HTTP **404** with a branded page and two
  recovery CTAs.
- **Note for future audits:** the unversioned `/cdn/shop/t/5/assets/theme.css` serves a stale
  16 KB build. Live pages load the versioned `?v=1788816718…` URL (27 KB), which is complete. Audit
  the versioned URL or you will chase phantom regressions.
- `/pages/size-guide` returns **200** and renders the full chart. Every internal link to it
  (`sections/product-main.liquid:122`, `sections/footer.liquid:37`, `sections/sizing-banner.liquid:15`)
  uses the correct `/pages/size-guide` handle. The repo filename `templates/page.sizeguide.json` is a
  *template suffix*, not a handle — the mismatch is cosmetic and there is no broken link.
- Nav and footer collection links are handle-driven and skip empty collections, so the empty `sale`
  collection is correctly absent from both.

---

# Factual accuracy check

**The store does not claim XXS anywhere.** Verified by grep across `sections/`, `templates/`,
`snippets/`, `layout/`, `config/` and by reading the rendered HTML of every live page: no `XXS`,
`XS`, `XXL` or `5X` appears in any customer-facing string. The only occurrence of "XS" in the repo is
a code comment in `assets/size-guide.js:10` explaining why it is *excluded*:

> `XS is charted by the supplier but never stocked, so it is omitted — recommending a size we cannot
> sell just produces a dead end.`

The ticker's `Inclusive Sizing S–4X` and the sizing banner's `S,M,L,XL,1X,2X,3X,4X` both match the
real range. **Correct — no action.**

**Correction to the audit brief:** the brief states "swim is One Size only". That is not what is in
the store. `/collections/swimwear/products.json` returns 38 products, of which **37 have no size
option at all** (a single colour variant — effectively one-size) and **one, `em-11025`, is sized
`S/M` and `L/XL`**. There is no literal "One Size" value on any swim product. If the intent is to
describe swim as one-size in copy, `em-11025` is the exception that breaks it.

**Size claims that are wrong or incomplete:**
- The hero subheading reads *"Swim, lingerie and leather in sizes S to 4X."*
  (`templates/index.json`). Swim does **not** come in S–4X — 37 of 38 swim products have a single
  unsized variant. The sentence attributes the full size range to a category that has none of it.
- The **size guide has no rows for `S/M`, `L/XL`, `1X/2X` or `3X/4X`**, which is what the entire swim
  range and 87 hosiery products actually use, nor for the numeric bra bands 32–44. Real option values
  in the live catalogue: `S, M, L, XL, 1X, 2X, 3X, 4X, O/S, Q/S, S/M, L/XL, 1X/2X, 3X/4X, 32–44`.
- The size guide quotes **numeric US dress sizes** (S → 2–6 … 4X → 20–22) which are not sellable
  values, gives **XL and 1X the same dress size (14–16)**, and leaves a **34–40 inch waist gap**
  between the XL row (32–34) and the 1X row (40–42) that the recommender in `assets/size-guide.js`
  will silently fall through.

**Other factual exposure (surfaced during the copy sweep, outside the size question):**
- `/pages/payment` asserts **"PCI-DSS Level 1"** (`sections/page-payment.liquid:43`) as a property of
  the business. That certification belongs to Shopify, the processor; a Shopify merchant does not
  hold it. This is the most legally exposed line found.
- `/pages/about` asserts **"Built in the US."** (`sections/page-about.liquid:67`). The catalogue is
  100% Elegant Moments wholesale, manufactured in Vietnam, China and Taiwan per the products' own
  descriptions. "US-based business" is defensible; "Built in the US" is not.
- **Wrong brand name shipped to customers.** `/pages/models` is headlined
  **"The Faces of Soleil Noir"** (`sections/page-models.liquid:52`) and `/pages/social` reads
  **"Real bodies. Real styles. All Soleil Noir."** (`:56`) and **"Tag us @soleilnoir"** (`:37`).
  "Soleil Noir" is the *theme's* internal name (`config/settings_schema.json:4`); the store trades as
  Velvet Tide. `@soleilnoir` is a handle the store does not own, and no social link is rendered
  anywhere on the site.
- The footer tagline **"Daring swim. Inclusive sizing."** leads with a category that is 38 of 663
  products (5.7%). Same in the 404 copy, "Looks like this page took a swim."

**Empty or placeholder pages outside the home page:**
`/pages/about` (heading only — the story textarea is unset), `/pages/faq` (**"FAQ items coming
soon."**, and it is linked from every footer), `/pages/models` (**"New faces coming soon."**),
`/pages/social` (**"Nothing to see yet."**), `/pages/care-instructions` (**completely blank** — no
content at all, on a catalogue of lace, vinyl, leather and hosiery), `/pages/payment` (three trust
badges, no body, no payment methods listed). `/pages/affiliates` advertises three hardcoded
commission tiers (10%/12%/15%, "monthly payouts", "dedicated account manager") behind an **Apply Now
button whose href is literally `#`** (`sections/page-affiliates.liquid:68`) — there is no way to
apply.

**No contact details exist anywhere on the site.** No email, no phone, no postal address — grep for
`mailto:` across the entire theme returns zero hits, and `/pages/contact` is a bare form. For a store
making US-based claims this is both a trust gap and a consumer-law exposure.

No lorem ipsum, `TODO`, `TBD`, `example.com`, fake phone numbers, fake addresses, invented press
quotes, invented influencer names or follower counts were found anywhere.
