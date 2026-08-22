# Store Policies — Refund, Shipping, Terms of Service

**Researched:** 2026-08-22
**Domain:** US consumer return/refund law, FTC Mail Order Rule, drop-ship fulfilment disclosure
**Store:** `velvet-tide-2.myshopify.com` — trading as **Velvet Tide**. Live, public, US-only, USD, 100% drop-shipped from Elegant Moments (Peckville, PA)
**Confidence:** HIGH on the supplier facts (read from `DROPSHIPINFORMATION.pdf` directly) · HIGH on FTC 16 CFR Part 435 and the two state posting statutes (fetched and quoted this session) · N/A on the three owner decisions below — they are deliberately left open

---

## ⚠ This is a draft for a lawyer to review. It is not legal advice.

Everything below is written by an engineer from primary sources — the supplier's own drop-ship
sheet, the text of 16 CFR Part 435, Cal. Civ. Code § 1723, and NY GBL § 218-a. The citations are
real and were verified this session. That is not the same as legal advice, and a licensed attorney
in the state of incorporation should read the Terms of Service in particular before it is
published. **Said once, here. It is not repeated below, and it must not be pasted into the
storefront text.**

---

## Why this is urgent

Verified live this session with `curl`:

| URL | Status |
|---|---|
| `/policies/privacy-policy` | **200** |
| `/policies/refund-policy` | **404** |
| `/policies/terms-of-service` | **404** |
| `/policies/shipping-policy` | **404** |

`sections/footer.liquid:46-47` links to `/policies/terms-of-service` and `/policies/refund-policy`
on **every page of the store**. Both are dead links, sitewide, right now, on a public storefront.

That is not only a trust problem. Two states convert a missing policy into an affirmative
obligation:

- **NY GBL § 218-a** — Article 12-B is titled *"Online Retailers and Mercantile Establishments"*,
  so it reaches this store explicitly. Where **no refund policy is posted**, the consumer gets
  **30 days from purchase** to take a full refund or credit **at the consumer's option**, provided
  the merchandise is unused and undamaged. Restocking fees must be disclosed in the posted policy.
- **Cal. Civ. Code § 1723** — a seller who does not conspicuously post a policy of *not* giving
  full refunds within 7 days is **liable to the buyer for the purchase amount** if the buyer
  returns the goods within **30 days**.

In other words: with no policy posted, this store is currently operating on a de-facto 30-day
unconditional-return policy in its two largest states, **with no hygiene exclusion available**,
on merchandise it cannot resell. The final-sale designation in Section B below only holds up if it
was visible *before* the customer paid — which today, it is not.

---

# PART 1 — Three questions only the owner can answer

Answer these three and the text below is ready to paste. Each appears in the policy text as a
clearly marked `[[DECISION A]]` / `[[DECISION B]]` / `[[DECISION C]]` block with both variants
written out, so nothing is silently chosen.

---

### 🚩 QUESTION A — Who pays return postage?

**The question:** when a customer returns something because it did not suit them — not our error,
not defective — who pays to ship it back?

| Option | Consequence |
|---|---|
| **A1 — Customer pays** *(recommended)* | Standard for a small merchant. Return economics on this catalogue are already bad: a returned median $34.95 item nets roughly **−$16.90** even with the customer paying postage (`07-RESEARCH.md`, "Return economics"). One return wipes out the profit on about one median order. |
| **A2 — Store pays (prepaid label)** | Better conversion, materially worse unit economics. On a $19.95 item a prepaid label plus the unrecoverable Shopify processing fee exceeds the item's gross margin — every such return is a loss larger than never making the sale. |
| **A3 — Split: customer pays, but we refund postage if the return is our fault** | This is really A1. "Our fault" returns are already free under Section B7 in either variant. |

**Recommendation: A1.** It is what the margin supports, it is lawful, and it is what comparable
independent lingerie retailers do.

---

### 🚩 QUESTION B — Are intimates final sale on hygiene grounds?

**The question:** which categories, if any, cannot be returned at all?

Both California and New York explicitly carve out hygiene from their default-return rules —
§ 1723's posting requirement does not apply to *"goods which cannot be resold due to health
considerations"* or to items conspicuously marked **"All sales final."** So this is lawful. It is
a **business** decision, not a legal one.

| Option | Consequence |
|---|---|
| **B1 — Everything returnable if unworn, unwashed, tags attached, hygienic liner intact** | Most generous. Highest return rate. Every returned garment is still unsellable to us in practice — we have no warehouse and no way to re-list a single physical unit against a supplier inventory feed. |
| **B2 — Final sale on the highest-risk categories only: thongs, G-strings, panties, bodystockings, hosiery** *(recommended)* | These are precisely the items that are both the least hygienic to return and the lowest value — the ones where return postage plus handling exceeds anything recoverable. Everything else (bras, bodysuits, chemises, leather/vinyl, costumes, swim) stays returnable under strict condition rules. |
| **B3 — All intimates final sale** | Legal, and some retailers do it, but on a store whose swim range is effectively **one size** (`README.md`, Known gap 1a: 37 of 38 sellable swim styles stock only `O/S`) it converts every sizing miss into an angry customer and a chargeback. Chargebacks cost the refund *plus* COGS *plus* the $3.50 drop-ship fee *plus* shipping *plus* the Shopify fee, which is not returned. |

**Recommendation: B2.** And whichever is chosen, the final-sale flag **must appear on the product
page before checkout**, not only in the policy — that is the condition on which the exclusion
survives challenge.

---

### 🚩 QUESTION C — Where does a returned parcel physically go?

**This one is not really a preference. It is an unresolved fact, and it is the single thing in the
supplier relationship that makes a normal returns policy impossible to honour as written.**

The parcel the customer receives is **blind**. Per the drop-ship sheet, it ships with *"your
company name in an abbreviated or coded form (for the purpose of discretion), 'Distribution
Center' and our warehouse address."* The return address on our own outbound parcel is **Elegant
Moments' loading dock in Peckville, PA** — not ours.

And the sheet's *entire* statement on returns is this:

> **Returns/Exchanges:** Please establish your policy and send us a copy if you would like it
> included in with all of your orders.

That is an offer to insert **our** leaflet. It is not an agreement to accept returned goods. There
is **no RMA process, no return address for goods, no restocking arrangement, no credit for
returned stock, and no defective/wrong-item remedy** anywhere in the document.

So today: a customer who writes "return to sender" on the box — the single most natural thing to
do — ships our merchandise to a third party who has never agreed to receive it, will not credit
us for it, and has no paperwork tying it to an order.

| Option | Viability |
|---|---|
| **C1 — Confirm with Elegant Moments that they accept returns** | ⚠️ **Not agreed today. Must be settled by phone (1-800-876-4363, Mon–Fri 9:00–16:30 ET) before this policy is published.** Ask four things: (1) to which address, (2) is an RMA number required, (3) do they credit the wholesale cost, (4) what restocking fee. Get the answer in writing to `dropship@`. |
| **C2 — Returns go to the owner's own address** | ✅ Realistic default, and what the text below assumes. **Requires that the return address is issued by email on request and never pre-printed on anything the customer receives.** The owner then holds unsellable stock — fine at low volume, not fine at scale. |
| **C3 — Refund without return ("keep it") under ~$20 retail** | ✅ **Strongly recommended as a standing internal rule**, alongside C2. Return postage plus handling exceeds anything recoverable on a sub-$20 garment we cannot re-list. Cheaper, faster, generates goodwill. Keep it as discretion, not a published entitlement. |
| **C4 — Third-party returns processor** | ❌ Fixed monthly cost against a handful of returns. Not at this volume. |

**Recommendation: C2 + C3, and make the C1 phone call anyway** — if Elegant Moments *does* accept
returns and credits wholesale cost, the return economics in `07-RESEARCH.md` improve materially and
Question A gets easier.

**Until C is settled, one line in the Refund Policy below is load-bearing and must not be cut:**
*"Do not send anything back before you have emailed us — parcels returned to the address on the
box will not reach us and cannot be refunded."* Without it, refused and undeliverable parcels
vanish into a warehouse in Pennsylvania and the customer is owed a refund for goods we can neither
recover nor prove we did not receive.

---

## Other fill-ins (not decisions — just facts to supply)

Replace every `[[TOKEN]]` before pasting.

| Token | Notes |
|---|---|
| `[[LEGAL_NAME]]` | The registered entity — e.g. "Velvet Tide LLC". Must match what appears on the customer's card statement. |
| `[[STATE]]` | State of formation / principal place of business. Drives governing law in the Terms. |
| `[[BUSINESS_ADDRESS]]` | Required in the Terms contact block. Does **not** need to be the returns address. |
| `[[SUPPORT_EMAIL]]` | ⚠️ The **published privacy policy currently shows `jcarlson2003@gmail.com`** as the store contact. A personal Gmail on a lingerie store's legal pages is avoidable — set up `support@` on the custom domain and change it in Settings → Store details. |
| `[[RETURNS_EMAIL]]` | Suggest `returns@`. Can be an alias to the same inbox. |
| `[[DOMAIN]]` | Custom domain, once attached. Until then `velvet-tide-2.myshopify.com`. |
| Alaska / Hawaii / PO Box / APO-FPO | The supplier ships USPS, so PO Box and APO/FPO are probably fine and AK/HI are reachable — but the Shopify shipping zone config was not verified this session. Confirm the zone covers what the policy claims. |
| **Brand-name mismatch** | `CLAUDE.md` and `sections/page-social.liquid:37` say **Soleil Noir** (`Tag us @soleilnoir`); the live store and its privacy policy trade as **Velvet Tide**. The text below uses **Velvet Tide** to match what is published and what customers see on their card statement. Reconcile the social handle separately. |

---

# PART 2 — Ready-to-paste policy text

Everything from here to the end of Part 2 is customer-facing copy. Paste as-is after replacing
tokens and resolving the three decision blocks. Do not paste the `[[DECISION]]` scaffolding or the
notes in square brackets.

---

## A. REFUND POLICY

> **Paste into:** Shopify admin → **Settings → Policies → Refund policy**

---

### Returns & Refunds

We want you to love what you ordered. If something is not right, here is exactly how it works —
please read the hygiene section before you order, because intimate apparel has limits that other
categories do not.

#### 1. Return window

You have **30 days from the delivery date** to request a return. Start it by emailing
**[[RETURNS_EMAIL]]** with your order number and what you would like to return. We reply with
instructions and a return address.

> **Do not send anything back before you have emailed us.** Your order ships blind from a
> distribution centre, and the address printed on the box is not ours. Anything posted back to
> that address — including a parcel marked "return to sender" — will not reach us and cannot be
> refunded.

#### 2. Condition

To be accepted, an item must be:

- unworn and unwashed, with no signs of wear, marks, scent, make-up or pet hair;
- with **all original tags still attached** and not removed and re-attached;
- with the **hygienic liner intact** on any swimwear or bottoms; and
- in its original packaging.

Try items on over your own underwear. We cannot accept anything that does not meet all four
conditions, and items that fail inspection are returned to you at your cost.

#### 3. Items that cannot be returned

`[[DECISION B]]`

> **If B2 (recommended) — paste this:**
>
> For health and hygiene reasons, the following are **final sale** and cannot be returned or
> exchanged unless they arrive faulty or incorrect:
>
> - thongs and G-strings
> - panties and briefs
> - bodystockings
> - hosiery, stockings and tights
>
> These items are marked **Final Sale** on their product page before you add them to your bag.
>
> Gift cards, and any item marked **Final Sale** or **Clearance** on its product page, are also
> non-returnable.

> **If B1 — paste this instead:**
>
> Every item can be returned provided it meets the condition requirements in section 2 above. In
> practice this means the hygienic liner and all tags must still be intact — once either has been
> removed, an intimate garment cannot be resold and cannot be accepted back.
>
> Gift cards, and any item marked **Final Sale** or **Clearance** on its product page, are
> non-returnable.

> **If B3 — paste this instead:**
>
> Because every item we sell is intimate apparel, **all sales are final** except where an item
> arrives faulty, damaged, or is not the item you ordered — see sections 7 and 8. This is marked
> on every product page before you add an item to your bag. Please use the size guide, and email
> **[[SUPPORT_EMAIL]]** before you order if you are unsure — we would much rather help you get the
> size right first time.

#### 4. Restocking fee

**None.** We do not charge a restocking fee.

#### 5. Who pays return postage

`[[DECISION A]]`

> **If A1 (recommended) — paste this:**
>
> You cover return postage on a change-of-mind return, and we recommend a tracked service — until
> your parcel reaches us it is your responsibility, and we cannot refund a return we never receive.
>
> **We pay return postage** whenever the fault is ours: a faulty item, the wrong item, or a
> shipping error we made.

> **If A2 — paste this instead:**
>
> We cover return postage. Email **[[RETURNS_EMAIL]]** and we will send you a prepaid label. One
> prepaid label per order.

#### 6. Refunds — method and timing

Once your return arrives and passes inspection, we approve it within **2 business days** and issue
the refund to your **original payment method**. Your bank or card issuer then typically takes a
further **5–10 business days** to post it — that part is out of our hands.

We refund the price you paid for the returned items. **Original shipping charges are not refunded**
unless the return is our fault, in which case they are.

You will get an email when your refund is issued. If more than 10 business days have passed since
that email and you still cannot see it, contact your bank first, then email us at
**[[SUPPORT_EMAIL]]**.

#### 7. Damaged, faulty, or incorrect items

Check your order when it arrives. If anything is damaged, faulty, or simply not what you ordered,
email **[[SUPPORT_EMAIL]]** within **7 days of delivery** with your order number and a photo.

We will replace it or refund it in full — your choice — including any shipping you paid, and **we
cover the return postage**. Depending on the item, we may not need it back at all.

#### 8. Exchanges

We do not offer exchanges. If you need a different size or colour, return the original under this
policy and place a new order — that way you get the size you want immediately, rather than waiting
for a return to clear first.

#### 9. If an item sells out after you order

Our stock figures come from our supplier and can move between the moment you order and the moment
your parcel is packed. If something you ordered turns out to be unavailable:

- we **refund that item in full**, automatically — you do not have to ask;
- the rest of your order **ships as normal**; and
- we email you to explain **before** your shipping confirmation arrives.

If the unavailable item is most of your order, or the whole order, we will contact you first and
ask what you would prefer. **We never substitute a different item, size, or colour without asking
you first** — with lingerie, the size and the cut are the whole product.

Where you are owed a refund, we issue it within **7 working days**, as required by the Federal
Trade Commission's Mail, Internet, or Telephone Order Merchandise Rule.

#### 10. Cancelling an order

Email **[[SUPPORT_EMAIL]]** as soon as possible. We can usually cancel an order that has not yet
been passed to our fulfilment centre, which is generally within a few hours on a business day.
Once it has been passed on, we cannot recall or redirect it — you will need to return it under
this policy.

#### 11. Your legal rights

This policy sits alongside your rights under the consumer law of your state, and does not replace
them.

---

## B. SHIPPING POLICY

> **Paste into:** Shopify admin → **Settings → Policies → Shipping policy**

---

### Shipping

#### 1. Where we ship

We ship within the **United States** only. We do not ship internationally at this time.

#### 2. Cost

| Order value | Shipping |
|---|---|
| Under $75 | **$7.95** flat |
| $75 and over | **Free** |

The free-shipping threshold is calculated on the merchandise subtotal after any discounts, and
before tax.

#### 3. Dispatch time

Orders are processed **Monday to Friday**, excluding public holidays. Most orders leave our
fulfilment centre **within 1–2 business days**. An order placed after **1:00 PM Eastern**, or at a
weekend, starts processing on the next business day.

#### 4. Delivery estimates

Once dispatched, standard delivery typically takes **3–7 business days** depending on your
location. So most orders arrive **within about 4–9 business days of being placed**.

These are estimates, not guarantees. Carrier delays, weather, and peak periods happen and are
outside our control.

#### 5. Carriers and tracking

We ship via **USPS, FedEx, or UPS** — the carrier is chosen by parcel weight and destination. You
will receive a **tracking number by email** as soon as your parcel is dispatched. Tracking can take
up to 24 hours to start showing movement after you receive it.

#### 6. Discreet, unbranded packaging

**Every order ships discreetly.** Parcels are plain, unmarked USPS, UPS or FedEx boxes with no
branding, no product imagery, and nothing on the outside that indicates what is inside. The sender
shows only an abbreviated name and "Distribution Center". No invoice or packing list naming the
contents is included in the box.

#### 7. Get your address right

**Check your shipping address carefully before you pay** — we cannot change it once your order has
been passed to our fulfilment centre, and we cannot redirect a parcel in transit.

If you spot a mistake, email **[[SUPPORT_EMAIL]]** immediately with your order number. If we catch
it in time we will fix it at no charge.

If a parcel is undeliverable or is returned because the address was wrong or incomplete, we cannot
guarantee we will get it back — parcels are returned to a fulfilment centre we do not operate.
Where an undeliverable order can be recovered we will refund the merchandise, less shipping. Where
it cannot, we will work with you on a resolution, but a refund is not automatic. **This is the one
thing worth thirty seconds of your time at checkout.**

#### 8. Lost, stolen, and delayed parcels

If tracking has not updated for **7 business days**, email **[[SUPPORT_EMAIL]]** and we will open
an enquiry with the carrier.

If tracking says **delivered** but the parcel is not with you: check with everyone at the address,
look in your usual safe places, and ask your neighbours — parcels marked delivered do turn up
within a day or two. If it has not appeared after **3 business days**, contact us within **30 days
of the dispatch date** and we will investigate and file a carrier claim.

Standard shipping is not sent with signature confirmation. We cannot take responsibility for a
parcel that tracking confirms was delivered to the address you gave us, but we will always help you
pursue a carrier claim, and we will not leave you on your own with it.

#### 9. Our shipping commitment

We will ship your order within the timeframe stated above, and in any event **within 30 days** of
receiving it — the standard set by the Federal Trade Commission's Mail, Internet, or Telephone
Order Merchandise Rule.

If we cannot, we will email you with a revised date and the choice to **wait or cancel for a full
refund**. If we cannot give you a definite revised date, or it is more than 30 days out, your order
is **automatically cancelled and refunded in full** unless you tell us you would like to wait. Any
refund we owe you is issued within **7 working days**.

#### 10. Taxes

Sales tax is calculated at checkout where applicable, based on your delivery address.

---

## C. TERMS OF SERVICE

> **Paste into:** Shopify admin → **Settings → Policies → Terms of service**

---

### Terms of Service

**Last updated: [[DATE]]**

Welcome to Velvet Tide. These Terms of Service ("Terms") govern your use of **[[DOMAIN]]** (the
"Site") and any purchase you make from it. The Site is operated by **[[LEGAL_NAME]]** ("Velvet
Tide", "we", "us", "our").

By using the Site or placing an order, you agree to these Terms. If you do not agree with them,
please do not use the Site.

#### 1. You must be 18 or older

**The Site sells adult intimate apparel and contains imagery of an adult nature.** By using the
Site or placing an order you confirm that you are **at least 18 years old** and legally able to
enter into a binding contract. The Site is not intended for anyone under 18, and we do not
knowingly collect information from or sell to minors. We may cancel any order where we have a
reasonable belief the buyer is under 18.

#### 2. Ordering and acceptance

Your order is an **offer to buy**. It is accepted only when we send you a shipping confirmation.
The order confirmation email you receive immediately after checkout acknowledges that we have your
order — it is not acceptance of it.

We may refuse or cancel any order, in whole or in part, including where:

- the item is out of stock or discontinued at our supplier;
- the price or product description was listed in error;
- the order is flagged as potentially fraudulent, or the billing and shipping details do not
  reconcile;
- the order appears to be for resale rather than personal use; or
- we cannot ship to the address given.

If we cancel an order you have already paid for, we refund it in full.

#### 3. Pricing and payment

All prices are in **US dollars** and exclude sales tax, which is calculated at checkout.

Prices and promotions can change without notice, and change frequently — this does not affect an
order we have already accepted. **If an item is listed at an obviously incorrect price**, we may
cancel the order and refund you in full even after you have received a confirmation.

**Payment is processed by Shopify's hosted checkout.** We never see, handle, or store your full
card number. By placing an order you confirm you are authorised to use the payment method you
provide.

#### 4. Products, colours, and sizing

We describe every product as accurately as we can. Colours vary between screens and cannot be
guaranteed to match exactly. Sizing varies between styles — please use the size guide on each
product page, and email us if you are unsure.

Product measurements, fabric compositions, and care instructions are provided by the manufacturer.

#### 5. Shipping and returns

Our **Shipping Policy** and **Refund Policy** are incorporated into these Terms and form part of
your agreement with us. Please read both before ordering — in particular the hygiene restrictions
on intimate apparel.

#### 6. Intellectual property

**The Site.** The Velvet Tide name and logo, the site design, layout, code, and all original text
are owned by us or licensed to us, and are protected by trademark and copyright law.

**Product photography and descriptions.** Product images and product descriptions on this Site are
**licensed to us by our supplier and are not our property**. They are made available for the sole
purpose of presenting our own catalogue. Nothing on this Site grants you any licence to them.

**What you may not do.** You may not copy, scrape, reproduce, republish, mirror, or use any content
from the Site for commercial purposes without our prior written permission — and in the case of
product photography, we cannot grant that permission, because it is not ours to grant.

**Content you post.** If you tag us on social media or submit a review, photo, or comment, you grant
us a non-exclusive, worldwide, royalty-free licence to reproduce and display that content in
connection with our brand, including on this Site. You confirm you own it or have permission to
grant that licence, that everyone identifiable in it has consented, and that everyone shown is
over 18. We can remove any submitted content at any time, for any reason.

#### 7. Acceptable use

You agree not to:

- use the Site for any unlawful purpose, or in breach of any applicable law;
- place fraudulent orders, or use a payment method you are not authorised to use;
- buy for resale, or place bulk or automated orders;
- use bots, scrapers, crawlers, or any automated means to access, harvest, or monitor the Site;
- attempt to gain unauthorised access to the Site, any account, or any connected system, or probe
  or test its security;
- interfere with the Site's operation, or upload anything containing malicious code;
- infringe our intellectual property or anyone else's; or
- harass, abuse, or threaten our staff, or post content that is unlawful, defamatory,
  discriminatory, or obscene.

We may suspend or terminate your access to the Site for any breach of this section, without notice.

#### 8. Accounts

If you create an account you are responsible for keeping your password confidential and for
everything done under your account. Tell us immediately at **[[SUPPORT_EMAIL]]** if you believe it
has been compromised. We may suspend or close any account at our discretion.

#### 9. Marketing, email, and SMS

You can opt in to marketing emails and SMS at signup or checkout. **We only send marketing SMS to
customers who have expressly opted in**, and message and data rates may apply. Reply **STOP** to
any message to opt out, or **HELP** for help. Unsubscribing from marketing does not stop
transactional messages about an order you have placed.

#### 10. Third-party links and services

The Site links to third-party sites and uses third-party services, including Shopify for checkout
and payment. We are not responsible for the content, policies, or practices of any third party, and
your dealings with them are between you and them.

#### 11. Disclaimer of warranties

The Site and everything on it is provided **"as is" and "as available"**, without warranty of any
kind, express or implied, including implied warranties of merchantability, fitness for a particular
purpose, and non-infringement. We do not warrant that the Site will be uninterrupted, secure, or
error-free, or that any defect will be corrected.

Nothing in this section limits any warranty or right that cannot be excluded under applicable law,
and some states do not allow the exclusion of implied warranties — in which case the exclusions
above apply to you only to the extent permitted.

#### 12. Limitation of liability

To the fullest extent permitted by law, **[[LEGAL_NAME]]**, its owners, officers, employees, and
agents will not be liable for any indirect, incidental, special, consequential, exemplary, or
punitive damages, or for any loss of profits, revenue, data, or goodwill, arising out of or in
connection with your use of the Site or any product bought from it — whether based in contract,
tort, strict liability, or otherwise, and even if we have been advised of the possibility.

**Our total liability to you for any claim relating to the Site or a product will not exceed the
amount you actually paid us for the order giving rise to the claim.**

Some states do not allow the exclusion or limitation of certain damages, so parts of this section
may not apply to you.

#### 13. Indemnity

You agree to indemnify and hold harmless **[[LEGAL_NAME]]** and its owners, officers, employees,
and agents from any claim, demand, loss, liability, or expense (including reasonable legal fees)
arising from your breach of these Terms, your misuse of the Site, or your violation of any law or
third-party right.

#### 14. Governing law and disputes

These Terms are governed by the laws of the **State of [[STATE]]**, without regard to its conflict
of laws rules. You and we agree that any dispute arising out of or relating to these Terms or the
Site will be brought exclusively in the state or federal courts located in **[[STATE]]**, and you
consent to the personal jurisdiction of those courts.

> **[Note for the owner — not for the storefront]** An arbitration clause with a class-action
> waiver is the other common option here and is generally enforceable in the US under the Federal
> Arbitration Act, but it is genuinely a trade-off — it caps class-action exposure while making you
> pay most arbitration filing fees, which for a low-value consumer product can be worse than the
> claim. **Ask the attorney.** Do not add one from a template.

#### 15. Severability, waiver, and entire agreement

If any provision of these Terms is found unenforceable, the rest remain in force. Our failure to
enforce any provision is not a waiver of it. These Terms, together with the Refund Policy, Shipping
Policy, and Privacy Policy, are the entire agreement between you and us regarding the Site.

#### 16. Changes to these Terms

We may update these Terms at any time. The current version is always posted here with its "last
updated" date, and it applies to any order placed after that date. Please check it periodically.

#### 17. Contact

**[[LEGAL_NAME]]**
[[BUSINESS_ADDRESS]]
Email: **[[SUPPORT_EMAIL]]**

---

# PART 3 — Publishing

## Where each one goes

All three are **native Shopify policies**, not theme pages. Native policies are the right home
because Shopify links them from the **checkout footer automatically**, which no theme page can do,
and they populate the `/policies/*` URLs the footer already points at.

Shopify admin → **Settings → Policies**:

| Policy | Field in Settings → Policies | Resulting URL | Footer link that is currently broken |
|---|---|---|---|
| Refund Policy | **Refund policy** | `/policies/refund-policy` | `sections/footer.liquid:47` — "Returns" |
| Shipping Policy | **Shipping policy** | `/policies/shipping-policy` | *(not currently linked — see below)* |
| Terms of Service | **Terms of service** | `/policies/terms-of-service` | `sections/footer.liquid:46` — "Terms" |

Paste, **Save**, then re-run the `curl` check — all four policy URLs should return 200.

**No theme change is needed for Refund or Terms** — the footer already links to both, and they will
start resolving the moment the policies are saved.

**The Shipping Policy has no footer link.** Adding one is a one-line change to
`sections/footer.liquid` alongside the existing three. Out of scope for this task, but it should be
a follow-up — a shipping policy that exists but is unlinked is only marginally better than one that
does not exist.

## ⚠️ These cannot be published through the API

The mutation is `shopPolicyUpdate`, and it requires the **`write_legal_policies`** access scope.
The "Velvet tide" app on this store is granted **products, content, publications, themes** — as
recorded in the store-setup notes and consistent with what `push_products.py` and
`sync_collections.py` actually use. `write_legal_policies` is **not** among them.

Adding it is not a one-liner: a scope change requires **releasing a new app version in the Dev
Dashboard *and* re-approving the install in the store admin** — a new version alone does not grant
it. That is more work, and more risk of disturbing a working product-push credential, than pasting
three blocks of text into an admin form once.

**Recommendation: paste them by hand.** This is a one-time task.

## Two follow-ups this work surfaces

1. **Send the returns policy to the supplier.** The drop-ship sheet offers to insert our policy
   into every parcel. Produce a **one-page** version of the Refund Policy — the returns email
   address, the window, the condition requirements, and the final-sale categories — and email it
   once to `dropship@elegantmomentslingerie.com`. Confirm on that same call whether it is a
   one-time file-on-record or a per-order attachment; the sheet's wording reads as one-time, but
   if it is per-order it changes the fulfilment automation design in Phase 7.
2. **The Privacy Policy needs a fulfilment-partner disclosure.** It is Shopify's stock template and
   does not mention that every order sends the customer's name and full shipping address to a
   third-party supplier in Pennsylvania. `07-RESEARCH.md` § Q7 sets out the six disclosures to add.
   Separate task, but it is the same publishing trip through Settings → Policies.

---

# PART 4 — Legal basis

Every source below was fetched and read this session.

| Requirement | Source | What it actually says | Where it lands |
|---|---|---|---|
| Ship within the stated time, or 30 days if none stated | **16 CFR § 435.2**, FTC Mail, Internet, or Telephone Order Merchandise Rule [CITED: law.cornell.edu/cfr/text/16/435.2] | *"within that time clearly and conspicuously stated in any such solicitation; or… within thirty (30) days after receipt of a properly completed order"* | Shipping Policy § 9 |
| Delay notice must offer a real choice | 16 CFR § 435.2 | Must *"offer to the buyer, clearly and conspicuously and without prior demand, an option either to consent to a delay in shipping or to cancel"* | Shipping Policy § 9 |
| Revised date ≤ 30 days → silence is consent | 16 CFR § 435.2 | Buyer *"deemed to have consented"* absent a rejection before shipment and before the revised date | Shipping Policy § 9 |
| Revised date > 30 days or indefinite → silence cancels | 16 CFR § 435.2 | Order *"automatically deemed to have been cancelled"* unless the buyer specifically consents within 30 days | Shipping Policy § 9 |
| Prompt refund = **7 working days** | 16 CFR Part 435 [CITED: ftc.gov/legal-library/browse/rules/mail-internet-or-telephone-order-merchandise-rule] | Refund *"by any means at least as fast and reliable as first class mail within seven (7) working days"* of the right to a refund vesting | Refund Policy § 9, Shipping Policy § 9 |
| Rule covers all internet orders | FTC final rule, effective 2014-12-08 | Amended and renamed to cover internet and mobile orders | Applies to this store in full |
| Post the refund policy or a 30-day default applies | **NY GBL § 218-a**, Art. 12-B *"Online Retailers and Mercantile Establishments"* [CITED: law.justia.com/codes/new-york/gbs/article-12-b/218-a] | Must *"conspicuously post its refund policy"*; with none posted, 30 days from purchase for a full refund **or credit at the consumer's option** on unused, undamaged goods | Why this is urgent; Refund Policy § 1 |
| Restocking fees must be disclosed | NY GBL § 218-a | The posted policy must state whether a refund is *"subject to any fees including a restocking fee"* | Refund Policy § 4 |
| Post a no-refund/limited-refund policy or be liable for 30 days | **Cal. Civ. Code § 1723** [CITED: codes.findlaw.com/ca/civil-code/civ-sect-1723; oag.ca.gov/consumers/general/refunds] | A seller not giving full refunds for 7 days must conspicuously display the policy; otherwise *"liable to the buyer for the amount of the purchase"* on return within 30 days | Why this is urgent |
| Hygiene exclusion is lawful | Cal. Civ. Code § 1723 | Posting duty does not reach goods that *"cannot be resold due to health considerations"*, or items marked *"All sales final"* | Refund Policy § 3, Decision B |
| Final sale must be visible pre-purchase | Cal. Civ. Code § 1723; general UDAP | The marking must be conspicuous **at or before the point of sale** | **Requires a PDP badge, not just this policy** |
| No federal law compels a retailer to accept returns | FTC / state-law survey [CITED: termsfeed.com/blog/return-refund-laws-usa] | Return acceptance is contractual; the constraint is **disclosure**, not obligation | Decision B is genuinely a business choice |
| `shopPolicyUpdate` needs `write_legal_policies` | [CITED: shopify.dev/docs/api/admin-graphql/latest/mutations/shopPolicyUpdate] | Scope required to write shop policies via the Admin API | Part 3 — paste by hand |

## Supplier facts these policies are written against

All read from `data/suppliers/elegant-moments/source/DROPSHIPINFORMATION.pdf` [VERIFIED].

| Fact | Where it surfaces in the customer-facing text |
|---|---|
| *"Most orders ship within 24 to 48 hours (Monday through Friday)"* | Shipping § 3 — "1–2 business days", Mon–Fri |
| Expedited cutoff **1 PM Eastern** | Shipping § 3 — the 1:00 PM ET cutoff |
| USPS First Class ≤ 15 oz; FedEx One Rate or USPS Priority ≥ 16 oz; expedited via FedEx/UPS | Shipping § 5 — "USPS, FedEx, or UPS" *(deliberately generic: USPS retired First Class Package Service, and naming a product the supplier may no longer buy would date the policy)* |
| *"All items are wrapped and shipped discreetly in unmarked packages"* | Shipping § 6 — the discreet-packaging section. **This is a genuine selling point for this category and deserves to be on the FAQ and PDP too, not buried in a policy** |
| Label shows a coded company name + *"Distribution Center"* + **their** warehouse address | Shipping § 6, and the "do not post it back" warning in Refund § 1 |
| No invoice or packing list unless we supply one | Shipping § 6 |
| *"you will be notified via email when the order ships and receive a tracking number"* | Shipping § 5 |
| OOS: *"You must then reply to advise us as to how you want us to handle both the unavailable and available items"* — **they stop and wait** | Refund § 9 — "ship available, refund unavailable" as the standing rule, disclosed to the customer up front |
| Cancellations by **email only**; never by phone | Refund § 10 — why a cancellation window is short and not guaranteed |
| *"We will not know the exact shipping costs on any order until the order is packed"* | Why the store charges a flat $7.95 rather than live rates |
| Liability disclaimed only for **international** First Class Mail | ⚠️ Domestic loss is **not addressed anywhere in the sheet**. Shipping § 8 therefore has us absorbing it. Worth raising on the same phone call as Decision C. |
| Returns/exchanges: *"Please establish your policy and send us a copy"* — **and nothing else** | Decision C. This is the gap. |

## Consistency check against what the storefront already claims

| Live claim | Source | Matches the policy text? |
|---|---|---|
| "Free Shipping Over $75" | `sections/ticker.liquid:24,28` (hardcoded) | ✅ Shipping § 2 |
| "Free shipping on orders over $X" | `sections/announcement-bar.liquid:5` (schema setting) | ✅ — confirm the setting is `75` |
| Free-shipping progress bar | `sections/cart-drawer.liquid:31-50` (schema setting) | ✅ — confirm the setting is `75` |
| "US-Based" | `sections/ticker.liquid` | ✅ Shipping § 1 |
| "Inclusive Sizing S–4X" | `sections/ticker.liquid` | ⚠️ True for lingerie. **Not true for swim** — 37 of 38 sellable swim styles are `O/S` only (`README.md`, Known gap 1a). Not a policy problem, but it is a claim the store is making that the catalogue cannot support, and a customer who buys swim expecting 4X gets a return — the one thing these policies are designed to reduce. |
| $7.95 flat rate | **Not found in the theme** | ⚠️ Comes from Shopify Settings → Shipping. **Verify the configured rate is $7.95 with a $75 threshold before publishing a policy that states it.** |
