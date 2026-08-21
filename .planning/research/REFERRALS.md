# Influencer / Model Referral Program — Research

**Researched:** 2026-08-21
**Domain:** Affiliate attribution, commission economics, and contractor payouts on a thin-margin drop-ship store
**Store:** `velvet-tide-2.myshopify.com` — live, US-only, USD, 663 active products, 100% drop-shipped
**Target Shopify Admin API version:** `2026-07`
**Confidence:** HIGH on the margin arithmetic (computed from this store's own verified cost base) · HIGH on Shopify discount/attribution mechanics · MEDIUM on app pricing (vendor pages change often; all figures dated 2026-08-21) · MEDIUM on the free-shipping/discount interaction (community-sourced, needs a 5-minute live test) · HIGH on FTC and 1099 rules

---

## Recommendation, in four sentences

**Run the program on Shopify Collabs (free to install, 2.9% of commissions actually paid out) using discount codes as the primary attribution mechanism, with the existing `?ref=` link kept as a secondary convenience.** Set the offer at **10% off for the customer and 15% commission to the model, but pay commission only on orders with a merchandise subtotal of $50 or more** — a flat 15% on every order is loss-making on exactly the small single-item orders a new influencer program produces most of. Fix the two live bugs in `assets/ref-capture.js` first (sessionStorage dies when the tab closes; `utm_campaign` is treated as a referral code), because right now the attribution window is roughly *one browser tab*. Do not build a custom affiliate system — the engineering is the cheap part and the 1099/payout/tax-form burden is the expensive part.

**The biggest risk is not technical.** It is that **a 15% commission stacked on a 10% customer discount turns a $19.95 single-item order into a loss of $1.32** once Elegant Moments' postage lands at the top of its own quoted $4–12 band. The store cannot know that postage until the parcel is already packed, so it cannot price the risk away per order. An influencer program that is not gated by basket size will reliably manufacture unprofitable orders, at volume, and the dashboard will show it as growth.

**Second biggest risk:** FTC liability. The brand — not the model — is liable when a model fails to disclose the material connection. The 2023 revision of the Endorsement Guides made monitoring an affirmative brand obligation, and the separate 2024 Consumer Reviews Rule carries civil penalties of up to **$51,744 per violation**. This is a paperwork problem with a real dollar figure attached.

**Third biggest risk:** discount-code leakage. An influencer code posted publicly ends up on RetailMeNot, Honey, and Chrome coupon extensions within days. Every organic customer who would have paid full price now gets 10% off *and* triggers a 15% commission to a model who did nothing. On this margin structure that is the difference between a profitable order and a break-even one, and the only real defences are per-code usage caps and the $50 gate.

---

## Section 0 — What already exists (read this before designing anything)

The store is further along than it looks. Four files already implement most of a link-based referral capture, and they are **live right now** — `settings_data.json` has `upromote_merchant_id: "UPROMOTE_MERCHANT_ID_PLACEHOLDER"`, which is non-blank, so `layout/theme.liquid` is loading `upromote.js` in production today. [VERIFIED: read from repo]

| File | What it actually does | Verdict |
|---|---|---|
| `assets/ref-capture.js` | At module-eval time (before `DOMContentLoaded`), reads `?ref=` from the URL and writes it to **`sessionStorage`** under `upromote_ref`. Exports `getInfluencerCode()`, which returns `sessionStorage.upromote_ref` → else `?utm_campaign` → else `null`. | **Keep the shape, fix the storage.** See the two bugs below. |
| `assets/upromote.js` | On `DOMContentLoaded`: reads the code, mirrors it into `sessionStorage.discount_code`, rewrites every `a[href*="/checkout"]` to append `?discount=CODE`, and dispatches `upromote:ref-captured`. | **Keep.** Swap the URL-append for the documented `/cart/update.js` discount endpoint. |
| `assets/ga4.js` | Calls `gtag('set', { influencer_code: code })` on load so the code rides along on every GA4 hit. | **Keep as-is.** This is the right pattern. |
| `assets/cart-drawer.js` (lines 322–338) | Listens for `upromote:ref-captured` and rewrites `#cart-checkout-btn`'s href with `?discount=`. | **Keep.** Correctly handles the case where the drawer renders after the event fires. |
| `sections/cart-drawer.liquid:137` | Checkout button is `href="{{ routes.cart_url }}/checkout"` → renders as `/cart/checkout`. | Matches `upromote.js`'s `a[href*="/checkout"]` selector. ✅ |
| `sections/page-affiliates.liquid` | Hero + three hardcoded tier cards (**10% / 12% / 15%**) + an optional iframe of a UpPromote registration URL, with an inert `href="#"` "Apply Now" fallback. | **The tier percentages are hardcoded in Liquid and are the numbers this research says are unaffordable ungated.** Must be edited. |
| `sections/page-models.liquid` | Iterates `shop.metaobjects.model.values`, hard `limit: 10`. Reads `model.portrait`, `model.name`, `model.height`, `model.size_worn`, `model.bio`, `model.instagram_handle`. | **The natural home for a `referral_code` field.** Adding one field to the metaobject definition wires model → code with no new datastore. |
| `config/settings_schema.json:107` | `upromote_merchant_id` text setting. Nothing in the JS ever reads it — it is purely a feature flag for script loading. | Rename or repurpose as `affiliate_program_enabled`. |

### 🚩 Two live bugs in the existing capture

**Bug 1 — `sessionStorage` gives you an attribution window of roughly one browser tab.**
`sessionStorage` is scoped per-tab and is destroyed when the tab closes. [CITED: MDN / WHATWG storage spec] That means the current attribution survives: navigating around the site in one tab. It does **not** survive: closing the tab and coming back an hour later; the Instagram in-app browser's "Open in Safari" hand-off, which opens a *new* browsing context; a phone-to-laptop journey; or a customer who saves the link for tomorrow. Every affiliate program on earth advertises a window measured in days (7, 14, 30). This one is measured in tabs. Fix: write to `localStorage` with an explicit `expiresAt` timestamp, and keep `sessionStorage` only as a same-tab fast path.

**Bug 2 — `utm_campaign` is treated as a referral code.**
`getInfluencerCode()` falls back to `new URLSearchParams(location.search).get('utm_campaign')`. Any Klaviyo email, Meta ad, or Google campaign that sets `utm_campaign=summer-drop` will be captured as an influencer code, appended to the checkout URL as `?discount=summer-drop`, and set as the GA4 `influencer_code` dimension. Shopify ignores an invalid discount code, so it will not charge anything wrong — but it **pollutes the attribution dimension with campaign names**, which will make the GA4 influencer report unreadable the moment paid marketing starts. Fix: drop the `utm_campaign` fallback entirely, or namespace it (`utm_campaign` only counts if it starts with `ref-`).

**Minor observation, worth 30 seconds:** `.planning/phases/02-global-shell/02-02-PLAN.md` defines the `model` metaobject's image field as `photo`, but `sections/page-models.liquid:19-20` reads `model.portrait`. One of the two is wrong. The page presumably renders in production, so the live definition is probably `portrait` — but confirm before adding a field to that definition. [ASSUMED]

---

## Section 1 — The margin arithmetic (this is the crux)

Everything else in this document is downstream of this section.

### The cost model

| Input | Value | Source |
|---|---|---|
| Retail | wholesale × 2.5, floored at **$14.95** | Phase 7 research + `build_import.py` [VERIFIED] |
| COGS | retail ÷ 2.5 = **40% of retail** | Same |
| Shopify Payments (US online card) | **2.9% + $0.30** on the amount charged | Coordinator-supplied verified figure |
| Supplier drop-ship fee | **$3.50 per ORDER**, not per item | Elegant Moments drop-ship sheet [VERIFIED: supplier PDF via 07-RESEARCH] |
| Supplier postage | **$4–12 standard**, and *"we will not know the exact shipping costs on any order until the order is packed"* | [VERIFIED: supplier PDF] |
| Customer pays for shipping | $7.95, free over $75 | [VERIFIED] |
| Commission base | post-discount **merchandise subtotal** — never shipping, never tax | Recommended, see §3 |

```
merch      = retail × (1 − customer_discount)
ship_chg   = $7.95  if merch < $75, else $0
revenue    = merch + ship_chg
fees       = 0.029 × revenue + $0.30
net        = revenue − fees − (retail ÷ 2.5) − $3.50 − postage − commission
```

### Baseline: a single-item order with no influencer involved

| Retail | postage $4 | $6 | $8 | $10 | $12 |
|---|---|---|---|---|---|
| $14.95 | +$8.46 | +$6.46 | +$4.46 | +$2.46 | **+$0.46** |
| $19.95 | +$11.31 | +$9.31 | +$7.31 | +$5.31 | +$3.31 |
| $24.95 | +$14.17 | +$12.17 | +$10.17 | +$8.17 | +$6.17 |
| $36.95 | +$21.02 | +$19.02 | +$17.02 | +$15.02 | +$13.02 |
| $59.95 | +$34.15 | +$32.15 | +$30.15 | +$28.15 | +$26.15 |

The $14.95 floor was calibrated so that **a full-price order with no discount** clears zero at worst-case postage, with $0.46 to spare. That is the entire safety margin. It is 46 cents.

### 🚩 The typical influencer deal: 10% off customer + 15% commission

| Retail | postage $4 | $6 | $8 | $10 | $12 |
|---|---|---|---|---|---|
| **$14.95** | +$4.99 | +$2.99 | +$0.99 | **−$1.01** | **−$3.01** |
| **$19.95** | +$6.68 | +$4.68 | +$2.68 | +$0.68 | **−$1.32** |
| $24.95 | +$8.38 | +$6.38 | +$4.38 | +$2.38 | +$0.38 |
| $29.95 | +$10.07 | +$8.07 | +$6.07 | +$4.07 | +$2.07 |
| $36.95 | +$12.44 | +$10.44 | +$8.44 | +$6.44 | +$4.44 |
| $59.95 | +$20.24 | +$18.24 | +$16.24 | +$14.24 | +$12.24 |

**The answer to the owner's question, stated plainly:**

> **At the top of Elegant Moments' own quoted standard postage band, a 10%-off / 15%-commission deal loses money on every single-item order below $23.84 retail. It loses $3.01 on a $14.95 item and $1.32 on a $19.95 item.**

Breakeven retail for a single-item order, by deal shape:

| Deal | postage $6 | $8 | $10 | $12 |
|---|---|---|---|---|
| No deal at all | $3.64 | $7.15 | $10.65 | $14.15 |
| 0% off + 10% commission | $4.42 | $8.66 | $12.91 | $17.16 |
| 0% off + 15% commission | $4.94 | $9.69 | $14.44 | $19.19 |
| **10% off + 15% commission** | $6.14 | $12.04 | $17.94 | **$23.84** |
| 15% off + 15% commission | $6.99 | $13.70 | $20.41 | $27.13 |
| 15% off + 20% commission | $8.15 | $15.98 | $23.81 | $31.64 |
| 20% off + 20% commission | $9.60 | $18.82 | $28.05 | $37.27 |

Breakeven is the wrong target though — nobody runs a business at zero. Here is the retail price needed to clear a **$3 profit** on a single-item order:

| Deal | postage $6 | $8 | $10 | $12 |
|---|---|---|---|---|
| 0% off + 10% commission | $10.79 | $15.03 | $19.28 | $23.53 |
| 0% off + 15% commission | $12.07 | $16.82 | $21.57 | $26.32 |
| 10% off + 10% commission | $13.23 | $18.44 | $23.65 | $28.86 |
| **10% off + 15% commission** | $14.99 | $20.89 | $26.79 | **$32.70** |
| 15% off + 15% commission | $17.06 | $23.77 | $30.49 | $37.20 |

**$32.70.** Given the catalogue median is around $34.95, a 10/15 deal only clears $3 on roughly the top half of the catalogue at worst-case postage — and only when the customer buys exactly one thing.

### The most useful table: what commission rate is actually affordable?

Maximum commission rate (% of post-discount merchandise) that still leaves **zero** profit, assuming a 10% customer discount is also in play:

| Retail | postage $4 | $6 | $8 | $10 | $12 |
|---|---|---|---|---|---|
| $14.95 | 52.1% | 37.2% | 22.3% | 7.5% | **negative** |
| $19.95 | 52.2% | 41.1% | 29.9% | 18.8% | 7.7% |
| $24.95 | 52.3% | 43.4% | 34.5% | 25.6% | 16.7% |
| $36.95 | 52.4% | 46.4% | 40.4% | 34.4% | 28.4% |
| $59.95 | 52.5% | 48.8% | 45.1% | 41.4% | 37.7% |

And the same thing but requiring the store to keep **$5** on the order:

| Retail | postage $4 | $6 | $8 | $10 | $12 |
|---|---|---|---|---|---|
| $19.95 | 24.4% | 13.2% | 2.1% | — | — |
| $24.95 | 30.0% | 21.1% | 12.2% | 3.3% | — |
| $36.95 | 37.4% | 31.4% | 25.3% | 19.3% | 13.3% |
| $59.95 | 43.2% | 39.5% | 35.8% | 32.1% | 28.4% |

Read the shape, not the individual cells. **The affordable commission rate is not a property of the store — it is a property of the basket.** On a $60 basket, 28% is affordable even at worst-case postage. On a $20 basket, nothing above 8% is. A single flat percentage cannot be right for both, and the reason is that the two costs that kill small orders — the $3.50 drop-ship fee and the $4–12 postage — are **per-order, not per-dollar**. A percentage commission is per-dollar. It is the wrong shape of instrument for the wrong shape of cost.

### Percentage commission on low-price single items does not work. Here are the alternatives.

Modelled at postage $10 (mid-band) with a 10% customer discount. Each cell shows **commission paid / store profit retained**.

| Structure | 1 × $19.95 | 1 × $36.95 | 2 × $29.95 = $59.90 | 3 × $29.95 = $89.85 |
|---|---|---|---|---|
| 15% of merch *(the naive default)* | $2.69 / **$0.68** | $4.99 / $6.44 | $8.09 / $14.22 | $12.13 / $14.65 |
| 10% of merch | $1.80 / $1.58 | $3.33 / $8.10 | $5.39 / $16.92 | $8.09 / $18.69 |
| **Flat $4 per referred order** | $4.00 / **−$0.63** | $4.00 / $7.43 | $4.00 / $18.31 | $4.00 / $22.78 |
| **15% of merch, gated at $50 merch** ✅ | $0.00 / $3.37 | $0.00 / $11.43 | $8.09 / $14.22 | $12.13 / $14.65 |
| 15% of (merch − $15 order allowance) | $0.44 / $2.93 | $2.74 / $8.69 | $5.84 / $16.47 | $9.88 / $16.90 |
| 25% of (merch − $15 order allowance) | $0.74 / $2.64 | $4.56 / $6.87 | $9.73 / $12.58 | $16.47 / $10.31 |
| Tiered: 0% <$40, 10% $40–75, 15% >$75 | $0.00 / $3.37 | $0.00 / $11.43 | $5.39 / $16.92 | $12.13 / $14.65 |
| 40% of realised contribution | $1.35 / $2.02 | $4.57 / $6.86 | $8.92 / $13.38 | $10.71 / $16.07 |

Verdicts on each:

| Alternative | Verdict |
|---|---|
| **Flat fee per order** | ❌ **Worst of the set.** It is *inversely* aligned — the store pays the same $4 on a $19.95 order (where it can afford $0) as on a $90 order (where it can afford $12). It also creates a direct incentive to generate many tiny orders, which is the exact failure mode to avoid. |
| **Commission on gross margin instead of revenue** | ❌ Sounds smart, is not. Because retail is *universally* 2.5× wholesale, gross margin is a fixed 60% of retail, so "25% of margin" is arithmetically identical to "15% of revenue." It changes the label and nothing else. |
| **Commission on true contribution** (after the $3.50 and postage) | ❌ **Mathematically perfect, operationally impossible.** It can never go negative — but Elegant Moments cannot quote postage until the parcel is packed, so true contribution is *unknowable* at the moment a commission is approved. Any affiliate app would have to hold every commission until the supplier invoice lands. Not worth it. |
| **Order allowance** — X% of (merch − $15) | ⚠️ Works, and is smoother than a hard gate. But "you earn 25% of everything over $15" is confusing to explain to a 22-year-old on Instagram, and **no off-the-shelf affiliate app supports it** — it would have to be computed manually or in a custom Shopify Function. |
| **Tiered by basket size** (0 / 10 / 15%) | ⚠️ Safe and supported by UpPromote and GoAffPro. But it earns the model only $35.96 on a realistic 20-order month (see below) — too little to motivate anyone. |
| **Minimum order value gate: 15% on orders ≥ $50 merch** | ✅ **Recommended.** One sentence to explain ("you earn 15% on orders of $50 or more"). Supported natively by every affiliate app *and* by Shopify's own `minimumRequirement` on discount codes. It aligns the model's incentive with the store's single most valuable behaviour: **pushing basket size toward the $75 free-shipping threshold.** |

### What the model actually earns — a realistic month

20 referred orders: 8 × $24.95, 7 × $39.90 (two items), 5 × $79.90 (two–three items). 10% customer discount applied. **$790.56 of referred merchandise revenue.**

| Structure | Model earns | Store keeps | Store's share |
|---|---|---|---|
| 15% flat | $118.58 | $166.08 | 58% |
| 25% of (merch − $15) | $122.64 | $162.02 | 57% |
| 40% of contribution | $113.87 | $170.80 | 60% |
| Flat $4/order | $80.00 | $204.66 | 72% |
| 10% flat | $79.06 | $205.61 | 72% |
| 15% of (merch − $15) | $73.58 | $211.08 | 74% |
| **15% gated at $50 merch** ✅ | **$53.93** | **$230.73** | **81%** |
| Tiered 0/10/15 | $35.96 | $248.71 | 87% |

The gate costs the model $65/month versus flat 15% — but it also means the store never books a loss-making referred order. That trade is worth making, and it is honest to tell the model *why*: **"we pay 15% on real baskets, and we'd rather pay you more on fewer, bigger orders than a little on orders that cost us money."** That framing also happens to be true and, unlike most affiliate pitches, defensible.

### Stress test — does the recommended shape ever go negative?

Postage at worst case $12, 10% customer discount, 15% commission gated at $50 merch:

| Cart | postage | ship charged | net before commission | commission | **store net** |
|---|---|---|---|---|---|
| 1 × $19.95 | $8 | $7.95 | $5.37 | $0.00 | **+$5.37** |
| 1 × $24.95 | $8 | $7.95 | $7.74 | $0.00 | **+$7.74** |
| 1 × $36.95 | $10 | $7.95 | $11.43 | $0.00 | **+$11.43** |
| 1 × $49.95 | $10 | $7.95 | $17.59 | $0.00 | **+$17.59** |
| 2 items = $59.90 | $10 | $7.95 | $22.31 | $8.09 | **+$14.22** |
| 3 items = $89.90 | $12 | $0.00 | $26.80 | $12.14 | **+$14.67** |
| 4 items = $119.85 | $14 | $0.00 | $39.00 | $16.18 | **+$22.82** |

Every row positive. The only remaining negative anywhere in the model is the **$14.95 floor product at $12 postage with a 10% discount: −$1.00** — and that is caused by the *discount*, not the commission. See the next finding.

### 🚩 Second finding: the $14.95 price floor does not survive a discount code

The floor was set for full-price orders. Minimum retail needed for a single-item order to clear zero, by customer discount:

| Customer discount | postage $6 | $8 | $10 | $12 |
|---|---|---|---|---|
| 0% (today's floor assumption) | $3.64 | $7.15 | $10.65 | **$14.15** |
| 5% off | $3.98 | $7.81 | $11.64 | $15.47 |
| **10% off** | $4.39 | $8.61 | $12.83 | **$17.05** |
| 15% off | $4.89 | $9.59 | $14.30 | **$19.00** |
| 20% off | $5.52 | $10.83 | $16.14 | $21.45 |
| 25% off | $6.34 | $12.43 | $18.52 | $24.62 |

**If any 10%-off code exists on this store — influencer, welcome offer, Klaviyo abandoned-cart, anything — the price floor needs to move from $14.95 to $17.05.** For a 15% code, $19.00. Rounding to the store's `.95` convention: **$17.95 and $19.95** respectively. This is a one-line change in `build_import.py` and it is arguably more urgent than the referral program itself, because a welcome-discount popup has the same effect and costs nothing to deploy by accident.

### 🚩 Third finding: a 10% code silently switches off free shipping

Shopify evaluates price-based shipping rates on the subtotal **after** discounts are applied. [MEDIUM confidence — community-sourced, contradicted in places; see Assumptions] With a $75 free-shipping threshold and a 10% code:

| Cart | After 10% off | Free shipping? |
|---|---|---|
| $75.00 | $67.50 | ❌ customer suddenly charged $7.95 |
| $79.95 | $71.96 | ❌ |
| $82.95 | $74.66 | ❌ |
| **$83.35** | $75.02 | ✅ |
| $89.90 | $80.91 | ✅ |

So there is a **$75.00–$83.34 dead zone** where a customer who has carefully built a cart to hit free shipping applies the influencer's code, sees the free-shipping promise evaporate at checkout, and gets *less* total value than if they had skipped the code. The cart drawer's progress bar ("You're $X away from free shipping!") will say one thing and checkout will do another, because `assets/cart-drawer.js:250` computes progress from `cart.total_price`, which is pre-code.

Two fixes, pick one:
1. Set the influencer discount to **free shipping** rather than a percentage. Cost is capped at exactly $7.95 and never scales. But on a $19.95 order free shipping costs $7.95 against a 10%-off cost of $2.00 — it is *more* expensive on small baskets and cheaper on nothing. ❌ Not recommended here.
2. **Attach a `minimumRequirement` of $50 subtotal to the influencer discount code itself** (Shopify supports this natively on `discountCodeBasicCreate`). This does not eliminate the dead zone but shrinks the population that hits it, and it aligns the discount with the same $50 gate as the commission — one rule, one number, one sentence. ✅ **Recommended.**

**This behaviour must be verified live before launch.** It is a five-minute test: create a 10%-off code, put $79 of product in the cart, apply the code, and look at the shipping line at checkout.

---

## Section 2 — Mechanism: which system to actually run

### The options, priced

All figures checked 2026-08-21. Vendor pricing changes frequently — re-check before committing.

| Option | Monthly cost | Variable cost | Payouts | Tax forms (W-9 / 1099) | Engineering | Verdict |
|---|---|---|---|---|---|---|
| **Shopify Collabs** | **$0** — free to install, all plans except Starter/Retail | **2.9% of commissions paid out** (≈$3.44/mo at $118 of commissions) | ✅ Automatic, billed onto the Shopify invoice, paid to the creator | ✅ W-9 collection built in; creators without a W-9 are capped at $599.99/yr | Near-zero | ✅ **Recommended** |
| **GoAffPro** | Free (Hobby) / $49 Premium / $99+ Business | **None** — no transaction fee on any tier | PayPal Payouts integration | Manual | Low | ✅ **Strong fallback** if Collabs is unavailable |
| **UpPromote** *(what the theme already assumes)* | Free (reviews up to $3,000 referral sales/mo) / $29.99 Growth / $89.99 Professional / $199.99 Enterprise | **+2% / 1.5% / 1%** of referral sales by tier | PayPal auto-payout from Growth up | Tax-form generation from **Professional ($89.99)** only | Low — page already built | ⚠️ Free tier is viable; paid tiers are poor value here |
| **Refersion** | ~$39 Launch / ~$99 Professional / $249 Business | +3% of affiliate sales on Launch | ✅ | ✅ | Low | ❌ Overbuilt and overpriced for <10 models |
| **Social Snowball** | $249 Snow Day / $499–899 Blizzard | +3% on Snow Day | ✅ | ✅ | Low | ❌❌ $249/mo against ~$230/mo of referred profit |
| **Native Shopify: discount codes + order tags + manual payout** | $0 | $0 | ❌ Manual — PayPal/Venmo/check by hand | ❌ Entirely manual | Low (Flow rule + a spreadsheet) | ✅ **Viable at ≤5 models**; breaks down fast |
| **Fully custom** — metaobject per model, `?ref=`, cookie, order attribution | $0 | $0 | ❌ Manual | ❌ Manual | **High and never finished** | ❌ See below |

### Cost, applied to this store's actual numbers

At the realistic month modelled above — **$790.56 referred revenue, $53.93 of commission under the recommended gate, $230.73 of store profit on referred orders**:

| Option | Monthly cost | As % of referred profit |
|---|---|---|
| **Shopify Collabs** | $1.56 (2.9% of $53.93) | **0.7%** |
| GoAffPro Hobby | $0.00 | 0% |
| Native + manual | $0.00 (plus ~30 min of owner time) | 0% |
| UpPromote Free | $0.00 | 0% |
| UpPromote Growth | $29.99 + $15.81 = **$45.80** | **20%** |
| Refersion Launch | $39 + $23.72 = **$62.72** | **27%** |
| Social Snowball | $249 + $23.72 = **$272.72** | **118%** — the app costs more than the program earns |

The paid tiers are not slightly expensive; they are **structurally** expensive, because a percentage-of-referral-sales fee is levied on *revenue* while this store's profit is a thin slice of that revenue. A 2% fee on referral sales is ≈6% of the profit those sales generate. Any vendor whose pricing is a percentage of GMV is mispriced for a 2.5×-markup drop-shipper.

### Why not fully custom

The `?ref=` link, the cookie, the metaobject, and the order attribution together are maybe two days of work — the existing files are already 60% of it. That is not the expensive part. The expensive part is everything after the sale:

- A dashboard where a model can see her own earnings without emailing the owner
- Payout execution — you cannot send money from Shopify; PayPal Payouts is a separate integration with its own API, its own KYC, and its own failure modes
- **W-9 collection and storage** — you are now holding a contractor's SSN or EIN. That is regulated PII with a real breach cost, in a **public repo** [VERIFIED: `data/suppliers/elegant-moments/README.md` confirms the repo is public]
- **1099-NEC generation and filing in January** — for every model paid $2,000+ in 2026 (see §5), plus state filings at lower thresholds
- Refund/chargeback clawback of already-paid commissions
- Fraud detection — self-referral, a model buying through her own code

Shopify Collabs does all of this for 2.9% of what you actually pay out. Building it costs a January every year, forever.

### Recommendation and the fallback

**Primary: Shopify Collabs.** Free, native, no separate login, W-9 built in, and the fee scales with payouts rather than with GMV.

**Two things to verify before committing** — both are quick and both are genuine unknowns:

1. **Merchant eligibility.** Collabs requires a sales history, and creator eligibility is currently US/Canada/UK. The store is live but new. Install the app and see whether it activates. [ASSUMED that a new store with limited history qualifies — not verified]
2. **🚩 Product-category eligibility.** This catalogue includes cupless bras, crotchless items, and bodystockings. Collabs is a Shopify-operated *creator marketplace* with its own content standards, and Shopify's broader policies restrict "sexually suggestive or explicit" imagery in several surfaces (Shop channel, Managed Markets). Whether Soleil Noir's imagery clears the Collabs bar is genuinely unknown and cannot be resolved from documentation. **This is the single most likely reason the recommendation would have to change.** [ASSUMED — must be tested by installing]

**Fallback if Collabs rejects the store: GoAffPro Hobby (free).** Unlimited affiliates, unlimited referral revenue, no transaction fee, PayPal Payouts integration, tiered and rule-based commissions. It does not do tax forms — at fewer than ten models, W-9s collected by email and a 1099 prepared by the bookkeeper in January is a perfectly reasonable amount of manual work.

**Do not** default to UpPromote just because `sections/page-affiliates.liquid` and `settings_schema.json` already reference it. That is maybe 40 lines of Liquid and one theme setting. Sunk cost, not architecture.

---

## Section 3 — Code vs link: how each attributes, and how each fails

### The two mechanisms

| | **Discount code** (`SOLEIL-MAYA`) | **Referral link** (`?ref=maya`) |
|---|---|---|
| Where attribution lives | On the order itself — `order.discountCodes` / `discountApplications`. Permanent, server-side, queryable. | In browser storage on the customer's device |
| Survives cross-device | ✅ Yes — she posts the code, he types it on any device | ❌ No |
| Survives ad blockers / privacy browsers | ✅ Yes | ❌ Partially |
| Survives Safari ITP | ✅ Yes | ❌ **Script-written storage is capped at 7 days**, and can drop to 24 hours for link-decorated cross-site navigation [CITED: webkit.org/blog/10218] |
| Survives the customer closing the tab | ✅ Yes | ❌ **Not today** — `sessionStorage`, see Bug 1 |
| Requires customer action | ⚠️ Yes — they must remember and type it | ✅ No |
| Attributes when the customer forgets the code | ❌ No | ✅ Yes |
| Leakage risk | 🚩 **High** — publicly posted codes get scraped by RetailMeNot, Honey, Chrome coupon extensions | ✅ Low |
| Gives the customer an incentive to use it | ✅ Yes — it's a discount | ❌ No, it's invisible to them |
| Works from a link in an Instagram bio | ⚠️ Only if also typed | ✅ Yes |

**Neither is sufficient alone. Run both, keyed to the same model.** This is exactly what the existing code already tries to do — `upromote.js` takes the `?ref=` value and applies it *as* a discount code, collapsing the two mechanisms into one identifier. That design is correct and should be kept. It means one string (`SOLEIL-MAYA`) is simultaneously the referral code, the discount code, and the link parameter, and the order carries it in `discountCodes` regardless of which path the customer took.

### What the existing `ref-capture.js` does about the failure modes

Honest answer: **almost nothing, and one thing it does is worse than doing nothing.**

| Failure mode | What `ref-capture.js` currently does |
|---|---|
| Cross-device journey | Nothing — no mechanism can fix this client-side. The **code** covers it. ✅ |
| Safari ITP 7-day storage cap | Irrelevant, because `sessionStorage` already expires far sooner than 7 days |
| Tab closed | ❌ **Loses the attribution entirely.** This is the dominant real-world failure and it is unhandled. |
| Ad blockers | Partially resilient — it is first-party theme JS, not a third-party pixel, so most blockers leave it alone ✅ |
| Instagram in-app browser → "Open in Safari" | ❌ New browsing context, new `sessionStorage`, attribution lost |
| Multiple influencers touching the same customer | ❌ **Last-write-wins, silently.** `ref-capture.js:17-20` overwrites on every page load that carries a `?ref=`. Undocumented and unintentional. |
| A campaign UTM being mistaken for a referral | ❌ Actively broken — see Bug 2 |

### The fix, in the existing architecture

Change `ref-capture.js` to write to `localStorage` with an explicit expiry, and make the first-click/last-click rule an explicit decision rather than an accident:

```js
// assets/ref-capture.js  (sketch — replaces lines 16-20)
const WINDOW_DAYS = 30;                 // <- owner decision, see §4
const KEY = 'soleil_ref';

const incoming = new URLSearchParams(location.search).get('ref') || '';
if (incoming) {
  let existing = null;
  try { existing = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {}
  const live = existing && existing.expiresAt > Date.now();

  // LAST-CLICK: always overwrite. FIRST-CLICK: only write if !live.
  if (!live || LAST_CLICK) {
    localStorage.setItem(KEY, JSON.stringify({
      code: incoming,
      capturedAt: Date.now(),
      expiresAt: Date.now() + WINDOW_DAYS * 864e5
    }));
  }
  sessionStorage.setItem(KEY, incoming);   // same-tab fast path only
}
```

`getInfluencerCode()` then reads the `localStorage` record, checks `expiresAt`, and returns `null` if stale. **Drop the `utm_campaign` fallback.** Everything downstream — `ga4.js`, `upromote.js`, `cart-drawer.js` — is unchanged, because they all already go through `getInfluencerCode()`. That discipline is the reason this fix is a one-file change, and it is worth noting that the original authors got that part right.

One further improvement while in there: `upromote.js` currently appends `?discount=CODE` to checkout hrefs. Shopify's Ajax Cart API supports this directly and more reliably:

```js
fetch('/cart/update.js', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    discount: code,
    attributes: { ref: code }        // rides through to the order
  })
});
```
[CITED: shopify.dev/docs/api/ajax/reference/cart — `{ discount: 'discount_code' }`, comma-separated for multiples, `''` to clear]

This applies the discount to the **cart** rather than to a link, so it survives accelerated checkout buttons (Shop Pay, PayPal Express) that bypass the `/cart/checkout` href entirely. The current implementation loses attribution on every Shop Pay checkout — which on a mobile-heavy lingerie store is likely a large share of orders. **This is the highest-value single change in the whole document after the margin gate.**

The `attributes: { ref: code }` line is belt-and-braces: cart attributes carry through to the order and show as a note in the admin. Note one caveat — there are developer-forum reports of cart attributes set via the *Storefront API* `cartAttributesUpdate` not reliably reaching `Order.customAttributes`. Those reports concern a different API surface than the Ajax `/cart/update.js` used here, so this is probably fine, but treat the discount code as the authoritative attribution and the attribute as a diagnostic only. [MEDIUM confidence]

---

## Section 4 — Attribution rules the owner must decide

These are policy, not code. Every one of them will come up in an argument with a model eventually, and settling them in writing beforehand is the entire point.

| Rule | Options | Recommendation | Why |
|---|---|---|---|
| **Attribution window** | 7 / 14 / 30 / 60 days | **30 days** | Industry-standard, generous enough to feel fair, short enough that a code posted once in March is not still paying out in June. Note Safari will not keep a JS-written cookie 30 days anyway — the *code* is what actually delivers the 30 days. |
| **First-click vs last-click** | | **Last-click** | The overwhelming industry default; every affiliate app defaults to it; and it matches what `ref-capture.js` already does by accident. First-click is defensible but you will be arguing about it forever. |
| **Link says Maya, code says Jess** | Link wins / **code wins** / split | **The code wins, always.** | The code is a deliberate act by the customer at the moment of purchase; the link may be a week-old artefact. It is also the only one that is provable from the order record. **State this in the agreement in exactly these words** — it is the single most likely dispute. |
| **Commission on shipping?** | | **No** | Shipping revenue is a cost recovery, not margin. On a $19.95 order the $7.95 shipping charge is 28% of the transaction and every cent of it is already spoken for by the supplier's postage. |
| **Commission on sales tax?** | | **No — never.** | Tax collected is not revenue; it is money held in trust for a state. Paying commission on it is paying commission on someone else's money. |
| **Commission on the pre- or post-discount subtotal?** | | **Post-discount** | If the customer got 10% off, the store received 10% less. Paying 15% on the pre-discount figure means the effective rate is 16.7%. |
| **Refunds** | | **Full clawback** of the commission on any refunded line | Non-negotiable — the drop-ship return economics in `07-RESEARCH.md` already put a return at roughly −$17. |
| **Supplier out-of-stock cancellation** | | **Full clawback**, no penalty to the model | Nothing shipped, no revenue, no commission. But say so in the agreement so it does not read as arbitrary. |
| **Partial refund** (one line refunded, rest shipped) | | Clawback **proportional to the refunded merchandise**, and re-evaluate against the $50 gate | If a $60 order drops to $38 after a refund it should not have earned commission at all. This is fiddly; Collabs handles proportional clawback automatically, which is a real argument for it. |
| **Holding period before payout** | 1–90 days | **30 days from delivery** | Long enough to cover the 30-day return window from `07-RESEARCH.md` §Q6, so a return never claws back money already sent. Collabs default is 30 days, configurable 1–90. [VERIFIED: help.shopify.com] |
| **Self-referral** | | **Prohibited.** Model's own purchases earn no commission — she gets a separate flat staff/gifting discount instead | Otherwise the commission becomes an unbounded personal discount, and it muddies the 1099. |
| **Code stacking** | | **No stacking.** Set `combinesWith` so influencer codes do not combine with other order-level discounts | Two 10% codes on a $19.95 order is a loss before commission even enters. |
| **Per-code usage cap** | | **Cap each code**, e.g. 500 uses, and set `appliesOncePerCustomer` | The only real defence against a leaked code appearing on Honey. Both are native fields on `discountCodeBasicCreate`. |
| **Minimum order value for commission** | | **$50 merchandise subtotal** | The core finding of §1. |

---

## Section 5 — Implementation sketch

Two paths. Both build on the existing files rather than replacing them.

### Path A — Shopify Collabs (recommended)

Almost no engineering. The work is configuration and copy.

| Step | Where | Detail |
|---|---|---|
| 1 | Shopify admin | Install **Shopify Collabs**. Confirm the store activates and the product catalogue is accepted. **This is the go/no-go gate.** |
| 2 | Collabs | Create one affiliate offer: **10% customer discount, 15% commission, minimum order $50, 30-day holding period.** Enable W-9 collection. |
| 3 | Collabs | Invite the models. Each gets her own code and link automatically. |
| 4 | `assets/ref-capture.js` | Apply the localStorage + expiry fix and drop the `utm_campaign` fallback (§3). |
| 5 | `assets/upromote.js` | Switch from href-rewriting to `POST /cart/update.js { discount, attributes }` so Shop Pay / PayPal Express keep attribution. Rename the file to `referral.js` and the custom event to `referral:captured`; update the import in `cart-drawer.js:327`. |
| 6 | `config/settings_schema.json` | Replace `upromote_merchant_id` with a `checkbox` named `affiliate_program_enabled`; update the two guards in `layout/theme.liquid:134-137`. |
| 7 | `sections/page-affiliates.liquid` | **Rewrite the tier cards.** The hardcoded 10% / 12% / 15% must become the gated structure, and the page must state the $50 minimum, the 30-day window, and the code-beats-link rule. Point the iframe/CTA at the Collabs application. |
| 8 | Shopify admin | Add a `referral_code` field (single-line text) to the **`model` metaobject** so `sections/page-models.liquid` can render "Shop Maya's picks — code MAYA10" on each card. Cosmetic, but it is the whole reason the models page exists. |
| 9 | Shopify Flow | Rule: order created → if `order.discountCodes` contains a code starting with `SOLEIL-` → tag the order `affiliate` + the code. Free reporting with no app. |
| 10 | `build_import.py` | Raise the price floor from $14.95 to **$17.95** so the 10% code cannot push a floor-priced item negative (§1). |

### Path B — Native Shopify, no app (viable at ≤5 models)

Only worth it if Collabs rejects the store *and* GoAffPro is unacceptable. Creating the codes programmatically:

```graphql
# Admin GraphQL, API version 2026-07
# Requires the write_discounts scope — already granted.
mutation createInfluencerCode($basicCodeDiscount: DiscountCodeBasicInput!) {
  discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
    codeDiscountNode { id }
    userErrors { field code message }
  }
}
```

```json
{
  "basicCodeDiscount": {
    "title": "Affiliate — Maya",
    "code": "SOLEIL-MAYA",
    "startsAt": "2026-09-01T00:00:00Z",
    "customerSelection": { "all": true },
    "customerGets": {
      "value": { "percentage": 0.10 },
      "items": { "all": true }
    },
    "minimumRequirement": {
      "subtotal": { "greaterThanOrEqualToSubtotal": "50.00" }
    },
    "usageLimit": 500,
    "appliesOncePerCustomer": true,
    "combinesWith": {
      "orderDiscounts": false,
      "productDiscounts": false,
      "shippingDiscounts": true
    }
  }
}
```

**Verification status of this mutation:** `discountCodeBasicCreate` **exists in 2026-07** and takes a single `basicCodeDiscount: DiscountCodeBasicInput!` argument, requiring the `write_discounts` scope. The fields `title`, `code`, `startsAt`, `endsAt`, `customerSelection`, `customerGets`, `usageLimit`, `appliesOncePerCustomer`, `minimumRequirement`, and `context` are all documented on the input object. [VERIFIED: shopify.dev/docs/api/admin-graphql/2026-07/mutations/discountCodeBasicCreate]

⚠️ **Not verified in this session, and the planner must confirm before writing code:** the exact nested shape of `minimumRequirement.subtotal.greaterThanOrEqualToSubtotal` and of `combinesWith`, and whether `combinesWith` is required or optional on create. Both are shown above from training knowledge of `DiscountMinimumRequirementInput` / `DiscountCombinesWithInput`. [ASSUMED] Also note that `07-RESEARCH.md` found `refundCreate` now requires an `@idempotent(key:)` directive as of 2026-04 — check whether the same requirement has been extended to discount mutations. [ASSUMED — not checked]

Then attribution and payout:

```graphql
# Nightly: pull attributed orders for a payout period
query attributedOrders($q: String!) {
  orders(first: 100, query: $q) {
    edges { node {
      id name createdAt displayFinancialStatus
      currentSubtotalPriceSet { shopMoney { amount } }   # post-discount, ex-shipping, ex-tax
      discountCodes                                       # <- the attribution key
      refunds { id totalRefundedSet { shopMoney { amount } } }
    } }
  }
}
```

`currentSubtotalPriceSet` is the right commission base: post-discount, excluding shipping and tax, and it reflects refunds. [ASSUMED — the "current" prefix on Shopify money fields denotes refund-adjusted values; not re-verified this session]

Payout is then a spreadsheet and a PayPal transfer, monthly. At five models that is perhaps 45 minutes a month. At fifteen it is a weekend, and that is the moment to move to Collabs or GoAffPro.

---

## Section 6 — Payouts and compliance

### Paying the models

| Method | Fit |
|---|---|
| **Shopify Collabs automatic payout** | ✅ Best. Rides on the Shopify bill; 2.9%; no separate money movement to reconcile. |
| PayPal Payouts (GoAffPro / UpPromote Growth+) | ✅ Fine. Fees vary; the model needs a PayPal account. |
| Manual PayPal / Venmo / Zelle | ⚠️ Works at low volume. **Keep a permanent record of every payment** — the 1099 depends on it. |
| **Store credit / gift card instead of cash** | ⚠️ Attractive on thin margins, but it is **still taxable non-employee compensation** and still counts toward the 1099 threshold. It is not a tax loophole. It is also less motivating than cash for someone whose motivation is money. |

### 1099-NEC — the threshold changed for 2026

**For payments made on or after 1 January 2026, the federal Form 1099-NEC reporting threshold rose from $600 to $2,000**, under the One Big Beautiful Bill Act signed July 2025. The first filings under the new threshold are due January 2027, and the threshold is inflation-indexed from 2027 onward. Payments made during calendar 2025 remain subject to the old $600 threshold. [VERIFIED: multiple sources incl. IRS-tracking accounting firms; corroborated across four independent sources]

Practical consequences:

- Collect a **Form W-9 from every model before the first dollar is paid**, not in January. Chasing an SSN from someone who stopped answering DMs in October is the classic 1099 failure. Collabs enforces this by capping non-W-9 creators at $599.99/year — a useful forcing function.
- 🚩 **State thresholds have not all followed the federal change.** Several states still require 1099 filing at $600 or lower, and some have their own direct-filing requirements. [MEDIUM confidence — flagged by Thomson Reuters' 2026 state reporting update; the specific state list was not verified here.] **Ask the bookkeeper which states apply.** Do not assume the $2,000 federal number is the operative one.
- Models are **independent contractors, not employees.** The affiliate agreement should say so explicitly, and the relationship must not drift toward control over hours, methods, or exclusivity — which is exactly the drift that happens when a "model" is also shooting content on a schedule.
- ⚠️ If a model is paid *both* a modelling fee for a shoot *and* affiliate commission, those aggregate into one 1099-NEC. Track them together.

### FTC endorsement rules — the brand is liable, not the influencer

This is the compliance item most likely to be under-weighted, so here it is directly.

**The Endorsement Guides (16 CFR Part 255)** require any endorser with a *material connection* to the brand to disclose it clearly and conspicuously. A material connection is any relationship a consumer would not expect and that could affect the weight given to the endorsement: cash, commission, free product, discounts, event access, trips. **A commission-earning affiliate link is unambiguously a material connection.** [CITED: ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255]

**The brand is liable for its influencers' failures to disclose.** The FTC's June 2023 revision — the first since 2009 — made this sharper: it expanded "endorsement" to cover tags, mentions, and silent product placement, brought AI and virtual influencers into scope, and established monitoring as an affirmative obligation. The brand cannot delegate compliance and plead ignorance.

Separately, the **Rule on the Use of Consumer Reviews and Testimonials (16 CFR Part 465)**, effective **21 October 2024**, is a *rule* rather than guidance — it carries **civil penalties up to $51,744 per violation**. It bans undisclosed insider reviews, incentivised reviews written to a required sentiment, review suppression, and buying fake followers or engagement. [CITED: ftc.gov / federalregister.gov 2024-18519]

**What the affiliate agreement must contain:**

1. A requirement to disclose the material connection in **every** post, story, reel, and video that features or links the product — including organic posts, not just paid ones.
2. **Specified acceptable disclosure language**: `#ad`, `#sponsored`, or "Paid partnership with Soleil Noir." Explicitly forbid `#sp`, `#collab`, `#ambassador`, `#partner`, and thanking the brand as a substitute for disclosure — the FTC has said repeatedly these are inadequate.
3. **Placement rules**: the disclosure must be unavoidable — above the "more" fold in a caption, **superimposed on the screen** in video and Stories, and **spoken aloud** in video where the endorsement is spoken. "In the bio" or "in the linked page" is not a disclosure.
4. **Truthfulness**: no claims the model has not personally verified. For intimates the realistic risk is fit and sizing claims — "runs true to size," "great support for a DD" — from someone who has not worn that garment.
5. A **no-fake-engagement clause** (16 CFR 465): no purchased followers, likes, or comments.
6. A **right to require takedown or correction** within a stated period, and the right to withhold commission on non-compliant content.
7. **Independent contractor status**, W-9 obligation, and no authority to bind the brand.
8. **Content licence** — if the brand will repost the model's content on `page-social.liquid` or in ads, the licence must be explicit. This is separate from the FTC issue and is routinely forgotten.
9. **Code-of-conduct and termination** clause. The brand's reputation attaches to whatever the model posts next.

**And an operational obligation the agreement cannot discharge:** monitoring. The FTC expects the brand to actually check. At the scale of ten models that means a recurring 20-minute monthly review of each model's tagged content, with a dated note that it was done. A written policy nobody checks is worse evidence than no policy, because it proves you knew.

**One brand-specific wrinkle:** this is a lingerie brand with a weekly-drops model and an Instagram-led strategy. Instagram and TikTok both apply stricter content moderation to intimate apparel, and a model's post can be suppressed or removed without either party being notified. That is a commercial risk to the program's throughput, not a legal one — but it means link-based attribution (which requires the post to stay up and stay reachable) is more fragile here than in most categories, and it is another argument for **codes** as the primary mechanism.

---

## Section 7 — Decisions

### 🚩 Blocking — the program cannot launch until these are settled

| # | Decision | Recommended default | Why blocking |
|---|---|---|---|
| **B1** | **Commission structure** | **15% of post-discount merchandise subtotal, on orders of $50+ merch only. 0% below.** | Everything else depends on this. Ungated 15% is loss-making below ~$24 retail at worst-case postage. |
| **B2** | **Customer discount** | **10% off, minimum order $50**, matching the commission gate | Determines what code gets created and what the affiliates page says. |
| **B3** | **Which platform** | **Install Shopify Collabs and see if it activates.** Fallback GoAffPro Hobby (free). | Determines whether steps 2–3 of the implementation are configuration or engineering. |
| **B4** | **Price floor** | **Raise $14.95 → $17.95** in `build_import.py` | With any 10% code live, a $14.95 item is −$1.00 at worst-case postage. This is true today with or without a referral program. |
| **B5** | **Rewrite the affiliates page tiers** | Replace the hardcoded 10/12/15% cards | `sections/page-affiliates.liquid:22-53` currently advertises terms this research says are unaffordable. It is live. |
| **B6** | **Affiliate agreement drafted and signed** | Use the nine points in §6 | FTC liability is the brand's. No model should post before signing. |
| **B7** | **W-9 collection process** | Before first payment, no exceptions | Recovering an SSN retroactively is the classic failure. |
| **B8** | **Verify the free-shipping/discount interaction** | 5-minute live test | If Shopify does evaluate the threshold post-discount, there is a $75.00–$83.34 dead zone where the code makes the customer worse off. |

### Deferrable — can be defaulted now and revisited

| # | Decision | Default | Revisit when |
|---|---|---|---|
| D1 | Attribution window | 30 days | A model disputes an attribution |
| D2 | First- vs last-click | Last-click | Two models start promoting simultaneously |
| D3 | Holding period | 30 days from delivery | Return rate is measured |
| D4 | Tier structure (bonus rates for top performers) | **None at launch — one flat gated rate** | Someone is consistently driving 20+ orders/month |
| D5 | Per-code usage cap | 500 uses | A code appears on a coupon site |
| D6 | Payout cadence | Monthly, on the 15th | Volume makes it tedious |
| D7 | Store credit vs cash | Cash | A model asks |
| D8 | `referral_code` on the `model` metaobject | Add it — it is one field | Never; do it in the same pass |
| D9 | Fixing `sessionStorage` → `localStorage` | Do it now, it is one file | Never; it is the cheapest win available |
| D10 | Whether models get a free product allowance | Separate from commission; a flat gifting discount | The first shoot |
| D11 | International models | Out of scope — store is US-only | Shopify Markets is enabled |
| D12 | Second-tier / sub-affiliate recruiting | **No.** It adds MLM optics to a lingerie brand | Never, realistically |

---

## Assumptions Log

Claims in this document that were **not** verified against authoritative sources in this session. Each should be confirmed before it becomes a locked decision.

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | Shopify evaluates price-based shipping rates on the **post-discount** subtotal | §1, B8 | The $75–$83.34 free-shipping dead zone may not exist. Sources contradicted each other; one community thread asserted the opposite. **Test it.** |
| A2 | Shopify Collabs accepts a new store with limited sales history | §2 | Recommendation falls back to GoAffPro |
| A3 | Shopify Collabs accepts this product category (cupless/crotchless intimates) | §2 | **Most likely reason the primary recommendation changes.** Documentation does not address it. |
| A4 | Collabs commission is computed on the merchandise subtotal excluding shipping and tax | §2, §4 | Would change the effective rate. Shopify's help page does not state the base. **Verify in the app before setting 15%.** |
| A5 | Exact nested shape of `minimumRequirement.subtotal.greaterThanOrEqualToSubtotal` and `combinesWith` on `DiscountCodeBasicInput` | §5 | GraphQL errors on first run — cheap to discover, but do not ship untested |
| A6 | `@idempotent` directive is *not* required on discount mutations in 2026-07 | §5 | 07-RESEARCH found it is now required on `refundCreate`; the pattern may have spread |
| A7 | `currentSubtotalPriceSet` is refund-adjusted and excludes shipping/tax | §5 | Wrong commission base — over- or under-paying every model |
| A8 | The `model` metaobject's image field is `portrait` (page-models.liquid) not `photo` (02-02-PLAN) | §0 | Cosmetic; discovered instantly when adding the `referral_code` field |
| A9 | Cart attributes set via Ajax `/cart/update.js` reliably reach the order | §3 | Diagnostic only — the discount code is the authoritative attribution, so no money is at risk |
| A10 | State-level 1099 thresholds diverge from the new federal $2,000 | §6 | Missed state filings. **Ask the bookkeeper.** |
| A11 | Postage scales roughly $8 → $10 → $12 → $14 for 1 → 2 → 3 → 4 items | §1 | Multi-item basket profits shift, but all are comfortably positive, so the recommendation is robust to this |
| A12 | Vendor pricing (UpPromote, GoAffPro, Refersion, Social Snowball) as of 2026-08-21 | §2 | Re-check before signing anything. Refersion's tiers were reported inconsistently across sources — treat as LOW confidence. |

---

## Open Questions

1. **Does the catalogue clear Shopify Collabs' content standards?** Cannot be resolved from documentation. Resolve by installing — it costs nothing and takes ten minutes, and it determines the whole implementation path.
2. **What is the store's actual average order value and single-item order rate?** All of §1 is a sensitivity analysis because this is unknown. If most orders are already $50+, the gate costs the models almost nothing and the whole problem is theoretical. If most orders are one $19.95 item, the gate is load-bearing. **This is the single most valuable missing number in the document** and it becomes available the moment there are 50 real orders.
3. **What is the real distribution of Elegant Moments postage?** The whole analysis swings on a $4–12 band the supplier will not narrow. After 20 orders, the actual mean is knowable from the card statement, and the commission gate can be tuned rather than guessed.
4. **Will models actually be paid a modelling fee as well as commission?** Changes the 1099 arithmetic and the contractor-status analysis.

---

## Sources

**Primary (HIGH confidence)**
- shopify.dev/docs/api/admin-graphql/2026-07/mutations/discountCodeBasicCreate — mutation existence, signature, `write_discounts` scope
- shopify.dev/docs/api/ajax/reference/cart — `POST /cart/update.js` `attributes` and `discount` parameters
- help.shopify.com/en/manual/promoting-marketing/collabs/merchants/payments — 2.9% processing fee, 30-day default holding period (1–90 configurable), automatic reversal on cancelled/refunded orders, W-9 collection, $599.99/yr cap without W-9
- help.shopify.com/en/manual/promoting-marketing/collabs/merchants — available on all plans except Starter and Retail
- ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 — FTC Endorsement Guides
- ftc.gov / federalregister.gov 2024-18519 — 16 CFR Part 465, effective 21 Oct 2024, civil penalties to $51,744/violation
- webkit.org/blog/10218 — Safari ITP 7-day cap on script-writable storage
- apps.shopify.com/affliate-by-secomapp — UpPromote pricing verbatim (Free / $29.99+2% / $89.99+1.5% / $199.99+1%), 4.9★ / 3,641 reviews
- docs.goaffpro.com/pricing — Hobby free (unlimited affiliates/sales/revenue), Premium $49, Business $99+, no transaction fees
- `.planning/phases/07-drop-ship-order-automation-.../07-RESEARCH.md` — supplier spec, $3.50/order fee, $4–12 postage band, "not known until packed," return economics, price-floor analysis
- This repo: `assets/ref-capture.js`, `assets/upromote.js`, `assets/ga4.js`, `assets/cart-drawer.js`, `sections/page-affiliates.liquid`, `sections/page-models.liquid`, `sections/cart-drawer.liquid`, `layout/theme.liquid`, `config/settings_data.json`, `config/settings_schema.json`, `.planning/phases/02-global-shell/02-02-PLAN.md`

**Secondary (MEDIUM confidence)**
- 1099-NEC $2,000 threshold for 2026 under OBBBA — corroborated across four independent accounting sources (1800accountant, OnPay, Heritage CPA, WhippleWood); state divergence flagged by Thomson Reuters
- Shopify Collabs creator eligibility limited to US/CA/UK — secondary reporting, not Shopify docs
- Refersion and Social Snowball pricing — secondary review sites only; Refersion figures were mutually inconsistent

**Tertiary (LOW confidence — flagged, needs validation)**
- Shopify evaluating free-shipping thresholds on post-discount subtotal — Shopify Community threads, self-contradictory. **A1. Test live.**

---

## Metadata

**Confidence breakdown**
- Margin arithmetic: **HIGH** — computed from this store's own verified cost base; formula reproduces the coordinator's independently supplied worked examples exactly ($14.95 → +$0.46 at $12 postage)
- Existing-code audit: **HIGH** — read directly from the repo
- Shopify discount/attribution mechanics: **HIGH** — verified against 2026-07 docs, with three nested-input details flagged
- App landscape and pricing: **MEDIUM** — vendor pages dated 2026-08-21; Refersion LOW
- FTC and 1099: **HIGH** on the rules, MEDIUM on state-level 1099 divergence
- Free-shipping/discount interaction: **LOW** — flagged as A1

**Research date:** 2026-08-21
**Valid until:** ~2026-09-20 for app pricing (vendors change tiers frequently); ~2027-01 for the tax and FTC content
