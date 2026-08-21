# Phase 7: Drop-Ship Order Automation — Research

**Researched:** 2026-08-21
**Domain:** Shopify order lifecycle automation against a no-API supplier (email in, email out)
**Store:** `velvet-tide-2.myshopify.com` — live, public, US-only, USD, Shopify Advanced
**Target Admin API version:** `2026-07` (current latest) [VERIFIED: shopify.dev]
**Confidence:** HIGH on Shopify mechanics · HIGH on supplier spec (read from source PDF) · MEDIUM on margin model (supplier shipping cost is a range, not a number) · LOW on inbound tracking-email parsing (zero real samples exist)

---

## Summary

Elegant Moments has no API, no EDI, and no webhook. The entire order lifecycle runs over
human-read email: we email an order to `dropship@elegantmomentslingerie.com`, a person there
keys it, packs it, and emails a tracking number back. Everything in this phase is about making
that boundary reliable, auditable, and cheap — not about making it disappear. It cannot
disappear.

The good news is that the outbound half is genuinely automatable with zero new
infrastructure. Shopify Flow is free on Advanced, fires on `Order risk analyzed`, renders Liquid
over `order.lineItems`, and sends to arbitrary external addresses. That path is always-on,
Shopify-hosted, and needs no server, no token rotation, and no monthly fee. The inbound half is
the hard half, and the honest answer is that at 5 orders/day a human pasting a tracking number
into Shopify's native fulfilment dialog is faster to build, more reliable, and cheaper than any
parser we could write against an email format we have never seen.

The third thing this research surfaced is not a technical problem at all. **18% of the catalogue
(62 of 330 products) has at least one variant priced at or under $14.95, and every one of those
loses money as a single-item order once Elegant Moments' standard shipping lands at the top of
its $4–12 band.** That is a pricing decision, not an engineering decision, and it should be
settled before any automation ships — otherwise we are automating the efficient production of
losses.

**Primary recommendation:** Ship a Flow-only outbound path plus native Shopify admin fulfilment
for tracking (Stage 1, $0/month, ~45 seconds of human time per order). Instrument it with two
scheduled reconciliation Flows from day one and collect every Elegant Moments tracking email into
a folder. Add Mechanic ($16–99/mo) for PDF packing slips, a Postmark audit trail, and inbound
tracking parsing only once volume passes roughly 15 orders/day *and* we have 20+ real tracking
emails to write a parser against.

**Single biggest risk:** a silently dropped order email. Flow's `Send internal email` action
returns no delivery receipt, and the receiving end is a human inbox. A paid order can sit
un-shipped for days before anyone notices. Every design decision below is downstream of that.

---

## Project Constraints (from CLAUDE.md)

| Directive | Impact on this phase |
|---|---|
| Vanilla JS only; no jQuery | Any theme-side UI (e.g. cart minimum) must be a plain ES module in `assets/` |
| Tailwind utilities inline in Liquid, no custom CSS classes | Applies to any new policy page section |
| Checkout must stay on Shopify hosted checkout | Rules out cart/checkout modification approaches that require Plus |
| USD only, US-only | International drop-ship rules in the supplier PDF are out of scope |
| TCPA: explicit opt-in + quiet hours in Klaviyo | Constrains any SMS shipping notification (see Compliance) |
| CCPA privacy posture, banner already shipped | Constrains the supplier-disclosure language (see Compliance) |
| **GSD workflow enforcement** — no direct repo edits outside a GSD command | Planner must route all edits through phase execution |
| Every section needs a `{% schema %}` block | Applies to a new Shipping & Returns policy section if built as a theme section |

**Additional constraint from `data/suppliers/elegant-moments/README.md`:** the repo is **public**.
Supplier price lists, `liveinventory.csv`, and the wholesale cost basis are gitignored and must
stay that way. Nothing in this phase may commit a cost figure, a supplier price list, or a real
customer address.

**Additional constraint from `.planning/STATE.md` / memory:** the theme repo auto-syncs to the
**published** theme. Any theme file touched in this phase goes live on push. Treat it as a
production deploy.

---

## User Constraints

No `07-CONTEXT.md` exists — `/gsd:discuss-phase` has not been run for this phase. The constraints
below are lifted from `.planning/ROADMAP.md` § Phase 7 and should be treated as provisional until
confirmed with the owner.

### From ROADMAP (locked by prior decision)

- **No Shopify scope grants arbitrary email sending.** Flow is the always-on path; a scheduled
  agent covers tracking write-back and exceptions. An agent alone cannot be relied on — it does
  not run continuously. *(Confirmed correct by this research; see Q1.)*
- Requires `read_orders`, `write_orders`, `write_merchant_managed_fulfillment_orders`.
  *(All already granted per the phase brief.)*
- Customer names and home addresses travel in these emails. The sending path must be a service
  with an audit trail, not a personal mailbox.
- Supplier ships within 24–48h Mon–Fri; expedited orders must reach them by 1 PM Eastern.
  Cancellations are only accepted in writing, by email.

### Open — needs `/gsd:discuss-phase` or direct owner input

See **Decisions Only The Owner Can Make** near the end of this document. There are eleven, and
four of them (price floor, minimum order value, return destination, final-sale scope) block
meaningful parts of the build.

---

## Phase Requirements (proposed)

ROADMAP lists Phase 7 requirements as `TBD`. Proposed IDs for the planner to adopt into
`REQUIREMENTS.md`:

| ID | Description | Research support |
|---|---|---|
| DROP-01 | Every paid, non-high-risk order is emailed to `dropship@elegantmomentslingerie.com` automatically, one order per email, carrying supplier style, colour, size, quantity, and full shipping address | Q1 — Flow `Order risk analyzed` + `Send internal email` |
| DROP-02 | The email presents the supplier style number unambiguously for merged plus-size products | Q2 — style derives from variant SKU, never from title or tags |
| DROP-03 | An order that has been sent is tagged so it is never sent twice | Q1 — `em-sent` tag as both marker and guard condition |
| DROP-04 | A supplier tracking number can be written onto the Shopify order such that Shopify's own shipping-confirmation email fires | Q3 — `fulfillmentCreate` with `notifyCustomer: true`, or native admin |
| DROP-05 | Out-of-stock / discontinued replies have a defined decision policy and a tracked queue with an FTC-compliant clock | Q4 — FTC Mail Order Rule: 30-day ship, 7-working-day refund |
| DROP-06 | A published Shipping & Returns policy exists on the storefront and a PDF copy is on file with the supplier | Q6 |
| DROP-07 | The privacy policy discloses supplier disclosure of customer PI, and a written service-provider term exists with the supplier | Q7 |
| DROP-08 | Monitoring catches a missed send, a supplier non-reply, and a stale inventory count without anyone remembering to look | Q8 — two scheduled Flows + weekly card reconciliation |
| DROP-09 | Catalogue pricing and shipping rules are set so no realistic single-item basket is loss-making | Q5 — price floor and/or minimum order value |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Order trigger + condition evaluation | Shopify platform (Flow) | — | Only Shopify knows when an order is paid and fraud-analysed; nothing else is always-on for free |
| Order → supplier email composition | Shopify platform (Flow Liquid) | Mechanic (Stage 2) | Line-item data lives in the order object; rendering it where it lives avoids a fetch |
| Email transport + delivery audit | External transactional service (Postmark, via Mechanic) | Shopify Flow internal email (Stage 1) | Shopify gives no delivery/bounce visibility; a transactional ESP does |
| PDF packing slip generation | Mechanic file generator (Stage 2) | — | Flow cannot attach files; this capability is the sole reason Stage 2 exists for outbound |
| Tracking number → fulfilment | Shopify Admin GraphQL (`fulfillmentCreate`) | Shopify admin UI (Stage 1, human) | Only the Admin API/UI can create a fulfilment and fire the customer notification |
| Customer shipping notification | Shopify platform (native notification) | — | Never hand-roll; `notifyCustomer: true` is the whole feature |
| Inbound tracking email capture | Mechanic inbound (`mechanic/emails/received`) | Human mailbox (Stage 1) | Requires an inbound-parse endpoint; Shopify has none |
| Exception queue (OOS/discontinued) | Shopify order tags + a scheduled Flow digest | Human judgement | The decision is commercial, not mechanical — the tier owns the *reminder*, not the *choice* |
| Refunds / cancellations | Shopify Admin GraphQL (`refundCreate`, `orderCancel`) | Shopify admin UI | Money movement stays on the platform that holds the payment |
| Inventory truth | Elegant Moments `liveinventory.csv` → `push_products.py --inventory-only` | — | Supplier is the only source of truth; Shopify holds a snapshot |
| Pricing floor / markup | Build pipeline (`build_import.py`) | — | Cheapest place to fix the margin problem is where prices are generated |
| Free-shipping threshold + flat rate | Shopify Settings → Shipping | Theme copy (`ticker.liquid`, cart drawer) | Rate lives in settings; the `$75` string is hardcoded in `sections/ticker.liquid:24,28` |

---

## Verified Supplier Spec

Read directly from `data/suppliers/elegant-moments/source/DROPSHIPINFORMATION.pdf`.
This supersedes the phase brief's summary where they differ.

| Fact | Detail | Confidence |
|---|---|---|
| Order channels | Phone `1-800-876-4363`, fax `570-489-5619`, email `dropship@elegantmomentslingerie.com`, or the online order center at `elegantmomentslingerie.com`. **Online order center and email are their preferred methods.** | [VERIFIED: supplier PDF] |
| Required per-item data | Style number, colour, quantity, size — plus the customer's complete name and address | [VERIFIED: supplier PDF] |
| **Payment** | **"Please have funds available on your credit card before placing your orders."** They charge a card on file. Not net terms. | [VERIFIED: supplier PDF] — *not in the phase brief; material to reconciliation* |
| Drop-ship fee | $3.50 **per order shipped, not per item**, separate from shipping | [VERIFIED: supplier PDF] |
| Shipping estimate (1 lb, continental US) | Standard $4–12 · 2nd Day $10–25 · Overnight $28–38 | [VERIFIED: supplier PDF] |
| Carriers | USPS First Class ≤15 oz; FedEx One Rate or USPS Priority ≥16 oz; expedited via FedEx or UPS | [VERIFIED: supplier PDF] |
| Shipping cost certainty | **"We will not know the exact shipping costs on any order until the order is packed."** Estimates only; may change without notice. | [VERIFIED: supplier PDF] |
| Label | Our company name in **abbreviated or coded form**, plus "Distribution Center" and **their** warehouse address | [VERIFIED: supplier PDF] |
| Packaging | Unmarked USPS/UPS/FedEx boxes, wrapped discreetly | [VERIFIED: supplier PDF] |
| Tracking | Emailed to us when the order ships | [VERIFIED: supplier PDF] |
| Out of stock / discontinued | They email us and **wait** for our reply on how to handle both the unavailable **and the available** items. Changes must go to `dropship@` by email. | [VERIFIED: supplier PDF] |
| Cancellations | Email only. **They will not accept cancellations by phone.** | [VERIFIED: supplier PDF] |
| Packing list | Not included unless we attach our own to the order. If we do attach one, the order **must** be placed by email, one order per email, packing list attached. | [VERIFIED: supplier PDF] |
| **Duplicate warning** | **"Please do not place drop ship orders online and email the invoices/packing lists separately, as that may result in the order being duplicated."** | [VERIFIED: supplier PDF] |
| Returns policy insert | "Please establish your policy and send us a copy if you would like it included in with all of your orders." — reads as a **one-time** file-on-record, not a per-order attachment | [VERIFIED: supplier PDF] · interpretation [ASSUMED] |
| Customer data | "AT NO TIME DO WE CONTACT YOUR CUSTOMERS OR SELL ANY CUSTOMER INFORMATION TO ANYONE!" | [VERIFIED: supplier PDF] — a policy statement, **not a contract** |
| Ship time | Most orders within 24–48 hours, Monday–Friday | [VERIFIED: supplier PDF] |
| Expedited cutoff | Place by **1 PM Eastern** | [VERIFIED: supplier PDF] |
| Office hours | Mon–Fri, 9:00 AM – 4:30 PM Eastern | [VERIFIED: supplier PDF] |

### What the sheet does **not** say

These gaps must be settled with Elegant Moments directly. They are load-bearing.

1. **Nothing about accepting returns.** No RMA process, no restocking fee, no address for returned
   goods, no defective/wrong-item remedy, no credit for returned stock. The only mention of
   returns is an offer to insert *our* policy.
2. **No SLA on the out-of-stock notification.** They say they will email and wait. They do not say
   how quickly, or what happens to the in-stock portion while they wait.
3. **No stated daily order volume ceiling** for a single drop-ship account.
4. **No stated tracking-email format**, subject line, or whether it echoes our order reference.
5. **No batching option.** "One order per email" is stated only in the packing-list context; it is
   not clear whether a consolidated manifest is acceptable when no packing list is attached.
6. **No confirmation/acknowledgement of receipt.** Nothing says they reply when an order is
   accepted — only when it ships or when something is unavailable.
7. **Nothing about damaged-in-transit or lost domestic packages** (they disclaim only
   *international* First Class Mail).

---

## System Architecture

### Recommended data flow — Stage 1

```
CUSTOMER
   │  places order, pays via Shopify Payments
   ▼
SHOPIFY ORDER  ──────────────────────────────────────────────┐
   │  (fraud analysis runs, ~seconds to minutes)             │
   ▼                                                         │
FLOW TRIGGER: "Order risk analyzed"                          │
   │                                                         │
   ├── condition: financial status = PAID? ────── no ──►  STOP (tag: em-hold-unpaid)
   ├── condition: risk = HIGH? ─────────────────  yes ─►  STOP (tag: em-hold-risk, alert owner)
   ├── condition: already tagged em-sent? ──────  yes ─►  STOP  (duplicate guard)
   ▼
FLOW ACTION: Send internal email
   │   To:  dropship@elegantmomentslingerie.com
   │   Cc:  orders@<our-domain>            (our own paper copy)
   │   Body: Liquid over order.lineItems
   │         style ← sku split "-" first
   │         size  ← Size option value
   │         colour, qty, full shipping address, order #
   ▼
FLOW ACTION: Add order tag "em-sent" + order note (timestamp)
   │
   ▼
=================  HUMAN BOUNDARY — ELEGANT MOMENTS  =================
   │
   ├──► normal path: they pack & ship (24–48h Mon–Fri)
   │        └──► EMAIL BACK: tracking number
   │
   └──► exception path: item OOS / discontinued
            └──► EMAIL BACK: "how do you want this handled?"  → EXCEPTION QUEUE
======================================================================
   │
   ▼
OWNER MAILBOX  (orders@<our-domain>)
   │
   ├── tracking email ──► open Shopify admin → order → Fulfill items
   │                        paste tracking + carrier, notify customer ✓
   │                        │
   │                        ▼
   │                   SHOPIFY sends native shipping confirmation ──► CUSTOMER
   │
   └── OOS email ──────► decide: substitute / backorder / partial refund / cancel
                            │
                            ├─► reply to dropship@ in writing
                            └─► refundCreate / orderCancel in Shopify + customer email

--------------------------- MONITORING (always on) ---------------------------
SCHEDULED FLOW A (daily 10:00 ET)
   Get order data: paid AND -tag:em-sent AND created >24h ago  ──► alert owner
SCHEDULED FLOW B (daily 10:00 ET)
   Get order data: tag:em-sent AND unfulfilled AND created >96h ──► alert owner
MANUAL (daily)  fresh liveinventory.csv → push_products.py --inventory-only
WEEKLY          Shopify order count  ⟷  Elegant Moments card statement
```

### Stage 2 delta (add only when justified)

```
FLOW  ──HTTP POST──►  MECHANIC TASK  ──► Postmark (attachment: branded packing-slip PDF)
                            │                  └──► delivery + bounce events → audit trail
                            │
EM tracking reply  ──►  velvet-tide-2@mail.usemechanic.com
                            │  event: mechanic/emails/received
                            ▼
                      parse tracking # + match order ref
                            ├── confident ──► fulfillmentCreate(notifyCustomer: true)
                            └── unsure ─────► email owner with a one-click admin link
```

---

## Q1 — Order Capture → Supplier Email

### Verified capabilities

| Capability | Verified finding |
|---|---|
| Flow availability | Free app, available on Basic, Grow, Advanced, Plus. Not on Starter. [CITED: changelog.shopify.com — flow now available to basic plan] |
| Flow → external email | `Send internal email` sends from your configured sender address to one or more comma-separated recipients. **Recipients cannot be a variable** — they must be static, which is fine here (always `dropship@`). [CITED: help.shopify.com/manual/shopify-flow/reference/actions/send-email] |
| Flow attachments | **Not supported.** No attachment option exists on the action. [VERIFIED: help center action reference] |
| Flow Liquid over line items | `{% for li in order.lineItems %} {{ li.sku }} {{ li.quantity }} {% endfor %}`. Direct iteration — **no GraphQL `edges`/`node` wrapper**. camelCase field names because Flow reads the GraphQL Admin API. Arrays cannot be printed directly. [CITED: help.shopify.com/manual/shopify-flow/getting-started/concepts/variables] |
| Flow `Send HTTP request` | Available on **Grow, Advanced, Plus** — this store qualifies. 30-second response timeout. 2xx/3xx = success. On 4xx/5xx/429 you choose retry-for-24h / fail / ignore. Response readable as `sendHttpRequest`. [CITED: help.shopify.com/manual/shopify-flow/reference/actions/send-http-request] |
| Flow scheduled trigger | `Scheduled time` recurs hourly/daily/weekly/monthly, minimum 10-minute interval; pair with `Get order data` (runs the Order query, **max 100 items**). [CITED: help.shopify.com/manual/shopify-flow/reference/triggers/scheduled-time] |
| Correct trigger | Use **`Order risk analyzed`**, not `Order created`. "Fraud analysis takes some time to process. Workflows that start with Order risk analyzed do not run immediately after an order is created." Only fires for Shopify's own risk assessments, not third-party. [CITED: help.shopify.com/manual/shopify-flow/reference/triggers/order-risk-analyzed] |
| Risk API status | `OrderRisk` and `order.riskLevel` are **deprecated** since 2024-04 in favour of the Risk Assessments API (`OrderRiskAssessment`, `RiskAssessmentResult` with `PENDING`/`NONE` granularity). [CITED: shopify.dev/changelog — deprecation of order risk APIs] |
| Mechanic outbound email | `to` accepts arbitrary external addresses (array or comma string). Options: `to`, `subject`, `body`, `cc`, `bcc`, `reply_to`, `from_display_name`, `headers`, `template`, `attachments`. **Attachments supported** via file generator — text files, PDFs rendered from HTML, downloaded files, ZIPs. Sends over **Postmark's transactional stream only**. Default sender `<shop-subdomain>@mail.usemechanic.com`; custom sender domain configurable. [CITED: learn.mechanic.dev/core/actions/email] |
| Mechanic Admin API | The `shopify` action runs arbitrary Admin GraphQL queries and mutations, with `query` + `variables`. 50k-character query limit (use variables). Results readable in follow-up runs. [CITED: learn.mechanic.dev/core/actions/shopify] |
| Mechanic pricing | Basic $16 · Grow $29 · **Advanced $99** · Plus $199 per month, "pay what feels good", no usage fees, 15-day trial. [CITED: apps.shopify.com/mechanic] |

### Option comparison

| Option | Cost/mo | Always-on | Line-item data | Attachments | Delivery audit | Reply-To control | Verdict |
|---|---|---|---|---|---|---|---|
| **Flow — `Send internal email`** | **$0** | Yes (Shopify-hosted) | Full, via Liquid over `order.lineItems` | **No** | Flow run log only — **no bounce or delivery visibility** | Sender address only | ✅ **Stage 1 recommendation** |
| Flow → `Send HTTP request` → own function | $0–5 (hosting) | Yes | Full (send order GID, refetch) | Yes | Yours to build | Yes | ⚠️ Real ops burden for one person; token is 24h client-credentials and must be re-minted |
| **Mechanic** | $16–99 ("pay what feels good") | Yes | Full, via `shopify/orders/*` events | **Yes — PDF from HTML** | **Postmark: delivery, bounce, open; 45-day content retention** | Yes | ✅ **Stage 2 recommendation** — and the only option that also closes the inbound loop |
| `orders/create` webhook → hosted function | $0–20 | Yes | Full | Yes | Yours to build | Yes | ❌ Most control, most maintenance. HMAC verify, retries, token rotation, uptime — all yours |
| Zapier / Make | $20–70 | Yes | Awkward line-item handling | Awkward | Partial | Yes | ❌ Another PI processor, per-task pricing, worst formatting control of the set |
| Browser automation vs. their online order center | — | No | — | — | None | — | ❌❌ Fragile, likely against their ToS, and the PDF explicitly warns that mixing the online center with emailed paperwork causes **duplicate orders** |

### Recommendation

**Stage 1: Flow `Order risk analyzed` → conditions → `Send internal email` → tag `em-sent`.**

Reasoning: it costs nothing, it is hosted by the same platform that holds the order, and it needs
no secret, no server, and no token. Attachments are its only real gap, and attachments are only
needed for a *branded packing slip* — the returns-policy insert is a one-time file-on-record with
the supplier, so Stage 1 does not lose the returns policy.

The three conditions matter more than the send:

1. `financial status = PAID` — never send an unpaid order. The $3.50 fee plus shipping is
   non-recoverable if the payment later fails.
2. `risk result ≠ HIGH` — never send a fraudulent order. A chargeback costs the refund *plus*
   COGS *plus* $3.50 *plus* shipping *plus* the Shopify Payments fee, which is not refunded.
3. `NOT tagged em-sent` — the duplicate guard. Their PDF explicitly warns about duplication, and
   a duplicate means we pay twice and a customer receives two parcels.

**Add `Cc: orders@<our-domain>`** on every order email. It costs nothing and gives the owner a
per-order copy in a mailbox they control — which is also where Elegant Moments' replies will land
when they hit Reply.

**Stage 2 trigger conditions** (build Mechanic when *any* is true): volume exceeds ~15 orders/day;
a branded packing slip becomes a requirement; or 20+ real tracking emails exist to write a parser
against.

⚠️ **Verify in the Flow UI during execution:** the exact condition path for risk result. The
underlying API moved from `OrderRiskLevel` to `RiskAssessmentResult`, and the Flow condition
picker's current field name for this is not documented in a form I could confirm from docs alone.
[ASSUMED] that a risk condition is exposed on the `Order risk analyzed` trigger; the help centre
page "Managing high-risk orders with Shopify Flow" indicates it is, but I could not confirm the
exact variable path.

---

## Q2 — Style-Number Presentation

### The actual data (read from the built catalogue)

This was verified against `data/suppliers/elegant-moments/out/shopify_products.csv`
(330 products / 1,004 variants):

```
HANDLE: em-2987   TITLE: "Lace thong — Style 2987"
  TAGS: Thong, Lingerie, em-style-2987, em-style-2987X, Extended Sizing
  SKU='2987'    Color='Red'        Size='O/S'   $9.95
  SKU='2987X'   Color='Red'        Size='Q/S'   $10.95

HANDLE: em-55065  TITLE: "Lace heart pattern cupless bra — Style 55065"
  SKU='55065'   Color='Black/Red'  Size='O/S'   $31.95
  SKU='55065X'  Color='Black/Red'  Size='Q/S'   $34.95

HANDLE: em-l1162  TAGS: 3 pc. Set, Bra Set, Leather, em-style-L1162
  SKU='L1162-S'  Color='Black'  Size='S'
  SKU='L1162-M'  Color='Black'  Size='M'
  SKU='L1162-L'  Color='Black'  Size='L'
```

### The rule

**The supplier style number is the variant SKU with any `-SIZE` suffix stripped. Nothing else.**

- `2987`     → style **2987**,  size from the Size option (`O/S`)
- `2987X`    → style **2987X**, size from the Size option (`Q/S`)
- `L1162-M`  → style **L1162**, size **M**

The trailing `X` is **part of the style number**, not a size modifier. Elegant Moments treats
`2987` and `2987X` as two separate styles in their system.

### The trap, stated plainly

For merged plus-size products:

- The **product title** says `Style 2987` even when the customer bought variant `2987X`.
- The **tags** list *both* `em-style-2987` and `em-style-2987X`, so tags cannot disambiguate either.
- Only the **variant SKU** identifies which style the customer actually bought.

If the email prints the title's style number, every plus-size order ships the wrong garment.
This is the single most likely correctness bug in the whole phase.

**Rule for the planner: derive the style from `li.sku`. Never from `li.product.title`, never from
`product.tags`.** Put the product title in the email only as a subordinate human sanity-check line,
visually secondary to the style number.

### Recommended email line format

```
  ITEM 1
    STYLE ....... 2987X
    COLOR ....... Red
    SIZE ........ Q/S
    QTY ......... 1
    (our ref: Lace thong — Style 2987 / SKU 2987X)
```

Fixed-width, label-per-line, one field per line. Reasons:

- A person is keying this into an order-entry screen field by field. A table forces them to track
  columns; a labelled list does not.
- `STYLE` and `SIZE` are on separate lines so `2987X` can never be misread as "style 2987, size X".
- The raw SKU is repeated in the parenthetical so a mistyped style is recoverable by cross-check.
- Colour values like `Black/Red` contain a slash, and size values like `O/S` and `Q/S` also contain
  a slash. **Never render the variant title (`"Red / O/S"`) as the parseable field** — it is
  slash-ambiguous. Use the individual option values.

⚠️ In Flow Liquid, prefer `li.variant.selectedOptions` (name/value pairs) over splitting
`li.variant.title` on `" / "`, precisely because of the `O/S` collision. [ASSUMED] that
`selectedOptions` is exposed on the Flow line-item variable — verify in the Flow editor's variable
picker during execution and fall back to a `split: " / "` on `variant.title` if not.

### Known catalogue edge cases

| Case | Detail | Handling |
|---|---|---|
| One Shopify order spans two supplier styles | Customer buys `2987` (O/S) and `2987X` (Q/S) from the same product page | Fine — still one supplier order, one email, one $3.50 fee. Just two ITEM blocks. |
| `L9859` / `L9859X` unmerged | Both stock `Q/S`; merging would create a duplicate Color+Size pair which Shopify rejects | Two separate Shopify products. SKU still disambiguates. No special handling needed. |
| Bare numeric SKUs | `2472`, `2473` — no hyphen, no size suffix | `split: "-" \| first` is a no-op and returns the SKU unchanged. Correct. |
| Blank SKU | Should not occur in the current catalogue, but a manually created product could have one | Flow should emit `⚠ SKU MISSING` rather than a blank line, and the order should be tagged for manual review |

---

## Q3 — Tracking Back to the Customer

### Verified API (target version `2026-07`)

**Mutation names — the V2 suffix is gone.** `fulfillmentCreateV2` and
`fulfillmentTrackingInfoUpdateV2` were deprecated in **2024-10** and renamed to
`fulfillmentCreate` and `fulfillmentTrackingInfoUpdate`. Behaviour is unchanged; only the name
changed. [CITED: shopify.dev/changelog/removing-v2-suffix-from-fulfillmentcreatev2-and-fulfillmenttrackinginfoupdatev2]

`fulfillmentCreate` exists in 2026-07 and takes `fulfillment: FulfillmentInput!` plus an optional
`message: String`. [VERIFIED: shopify.dev/docs/api/admin-graphql/2026-07/mutations/fulfillmentCreate]

`FulfillmentInput` fields [VERIFIED: shopify.dev/.../input-objects/FulfillmentInput]:

| Field | Type | Note |
|---|---|---|
| `lineItemsByFulfillmentOrder` | `[FulfillmentOrderLineItemsInput!]!` | **Required.** Pairs of fulfillment order ID + line items |
| `notifyCustomer` | `Boolean` | **Defaults to `false`.** Must be `true` for Shopify's shipping-confirmation email to fire |
| `trackingInfo` | `FulfillmentTrackingInput` | `company`, `number`, `numbers`, `url`, `urls` |
| `originAddress` | `FulfillmentOriginAddressInput` | Optional |

The `notifyCustomer: false` default is the gotcha. Omitting it silently ships the order with no
customer notification — which is exactly the failure this phase exists to prevent.

**Workflow for a merchant-managed location** [CITED: shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/build-fulfillment-solutions]:

1. Query the order for its `fulfillmentOrders` — take `id`, `status` (`OPEN`/`IN_PROGRESS`/`CLOSED`),
   `assignedLocation`, `lineItems { id, remainingQuantity }`, and `supportedActions`.
2. Use `remainingQuantity` — it is the reliable measure of what is still unfulfilled.
3. Check `supportedActions` includes `CREATE_FULFILLMENT`.
4. Call `fulfillmentCreate`.

**Tracking company strings.** Shopify builds a clickable tracking URL by this priority: an explicit
`url` field, then a Shopify-known `company` name, then a guess from the tracking-number format.
USPS, FedEx, and UPS are all recognised — which covers 100% of Elegant Moments' carriers. So
setting `company: "USPS"` (or `"FedEx"` / `"UPS"`) and `number` is sufficient; `url` can be omitted.
[CITED: help.shopify.com/en/manual/fulfillment/setup/order-status-page/order-tracking]

### Honest assessment: parse the email, or paste it by hand?

The phase brief asks for this judgement directly, so here it is without hedging.

**At 5 orders/day, a human pasting into Shopify's native Fulfill-items dialog is the correct
answer.** It is roughly 45 seconds per order — about **4 minutes per day**. The code path is
Shopify's own, already built, already tested, already fires the notification, already handles
partial fulfilment, and cannot corrupt an order by parsing something wrong. There is no build
cost and no maintenance cost.

**Automated inbound parsing is not currently buildable, because we have zero samples of Elegant
Moments' tracking email.** We do not know its subject line, its body format, whether it echoes our
order reference, whether it contains one tracking number or several, or whether it is
machine-generated or typed by a person. Writing a parser now means writing it against an
imagined format. That is not engineering; it is guessing, and the failure mode — fulfilling the
wrong order and emailing the wrong customer a wrong tracking number — is worse than doing nothing.

**Two hard prerequisites before any parser is written:**

1. **20+ real tracking emails collected in a dedicated folder**, so the format is observed rather
   than assumed.
2. **Elegant Moments confirms they will echo our order number** in the tracking reply. Without a
   reliable join key, matching is guesswork on customer name — which breaks the moment two
   customers share a surname or one customer places two orders.

**When both are true, the right implementation is Mechanic**, because it is the only option that
provides an inbound endpoint natively:

- Inbound address `velvet-tide-2@mail.usemechanic.com`, firing the `mechanic/emails/received`
  event. Parsed by Postmark; exposes `subject`, `text_body`, `html_body`, `from`, `from_full`,
  `to_full`, `cc_full`, `attachments[]`, `date`, `headers`, `message_id`, and
  `stripped_text_reply`. [CITED: learn.mechanic.dev/platform/email/receiving-email]
- `stripped_text_reply` is particularly useful — it removes quoted history, so a reply chain does
  not re-parse an old tracking number.
- Route Elegant Moments' replies in by auto-forwarding from `orders@<our-domain>`, which also keeps
  a human-readable copy for the owner.

**Design the parser to fail safe, not to fail silently.** If confidence is low — no order match, an
ambiguous match, an unrecognised tracking format, or more than one candidate order — it must email
the owner with a direct admin link rather than guess. A parser that falls back to manual on 30% of
emails still saves 70% of the work and never creates a wrong fulfilment.

### Comparison

| Approach | Build cost | Ongoing | Failure mode | Right at |
|---|---|---|---|---|
| **Shopify admin, native Fulfill items** | **Zero** | ~45s/order | Human forgets → caught by scheduled Flow B | **≤15 orders/day** |
| Small paste-a-tracking-number tool (form → `fulfillmentCreate`) | Medium — needs hosting + auth + token refresh | ~20s/order | Same as above, plus your own uptime | Rarely worth it — saves 25s/order over free native |
| Mechanic inbound parse → `fulfillmentCreate`, human fallback | Medium — Liquid task, needs real samples | ~0 for matched, manual for unmatched | Falls back to manual by design | **>15 orders/day, after 20+ samples** |
| Mechanic inbound parse, no fallback | Medium | 0 | **Wrong tracking to wrong customer** | ❌ Never |

**Note on the existing token pattern:** `push_products.py` mints a `shpat_` token via the
client-credentials grant, valid roughly 24 hours [VERIFIED: memory + `push_products.py:86`]. Any
long-running service must re-mint rather than hold a static token. Mechanic manages its own OAuth
session and sidesteps this entirely — a real, underrated advantage.

Also note `push_products.py` pins `API_VERSION = "2025-10"`. If this phase adds fulfilment code to
that file, bump it to `2026-07` deliberately and re-test the existing product/inventory paths —
do not bump it as a drive-by.

---

## Q4 — Exception Handling (Out of Stock / Discontinued)

The supplier emails us and **waits**. Nothing ships — including the in-stock items — until we
reply. That waiting period is a legal clock, not just an inconvenience.

### The legal clock

**FTC Mail, Internet, or Telephone Order Merchandise Rule** [CITED: ftc.gov/legal-library/browse/rules/mail-internet-or-telephone-order-merchandise-rule]:

- Ship within the advertised time frame, or within **30 days** if none is advertised.
- If you cannot, you must **obtain the buyer's consent to the delay or refund the unshipped
  merchandise**.
- Delay notices must give the buyer enough time to make a meaningful decision.
- If the revised date is more than 30 days out, or unknown, you must tell customers that
  **non-response cancels the order automatically**.
- **"Prompt refund" is defined as within 7 working days** of the buyer's right to a refund vesting.

This converts the exception queue from a nice-to-have into a compliance control. **Set an internal
SLA of 24 hours to respond to a supplier OOS email, and 7 working days maximum to refund.**

### The four responses

| Response | Shopify mechanics | Supplier action | Customer-facing message |
|---|---|---|---|
| **Ship available, refund unavailable** *(recommended default)* | `refundCreate` for the OOS line items — `orderId`, `refundLineItems: [{lineItemId, quantity}]`, `note`, `notify: true`. **Do not restock** (Shopify inventory is a supplier snapshot, restocking it re-creates the oversell). ⚠️ **As of 2026-04 the `@idempotent(key: "<uuid>")` directive is required on `refundCreate`.** | Email `dropship@`: "Ship the available items, cancel the unavailable ones." | "One item in your order — [name] — has sold out and we've refunded it in full ($X.XX, back within 5–10 business days). The rest is shipping now." Send **before** the shipping confirmation so the two emails read in the right order. |
| **Substitute** | Order edit to swap the variant. ⚠️ [ASSUMED] `orderEditBegin` / `orderEditAddVariant` / `orderEditCommit` are the current mutation names — **not verified in this session.** The planner must confirm against 2026-07 before relying on them. | Email `dropship@` with the replacement style/colour/size | **Requires explicit customer consent first.** Never substitute silently on intimates — size and cut are the entire product. Email, get a yes, then edit. |
| **Backorder** | Leave unfulfilled, tag `em-backorder`, add order note with the expected date | Ask the supplier for a restock date and hold or split the order | FTC delay notice with a definite revised date. If >30 days or unknown, state that no reply cancels the order. |
| **Cancel whole order** | `orderCancel(orderId, reason: OUT_OF_STOCK (or similar enum), refundMethod, restock: false, notifyCustomer: true, staffNote)`. Returns a `job`, so it is async — poll `job.done`. `orderCancelUserErrors` is separate from `userErrors`. [CITED: shopify.dev/docs/api/admin-graphql/latest/mutations/ordercancel] | **Must be emailed** to `dropship@` — they do not accept phone cancellations | Apology + full refund confirmation + a discount code, because this is a bad experience we caused |

### Recommended default policy

Adopt **"ship available, refund unavailable"** as the standing rule, applied automatically, so
the owner does not have to decide per-order in the general case. Escalate to human judgement only
when:

- the OOS item is more than 50% of the order value (the remaining shipment may not be worth the
  $3.50 + shipping), or
- the entire order is unavailable (cancel), or
- the customer explicitly requested a substitution at checkout.

This default is the fastest to communicate to the supplier (a canned reply), the safest under the
FTC rule (refund now, no delay notice needed), and the least likely to produce a return (we never
ship something the customer did not choose).

### Queue mechanics

There is no need for a database. Use Shopify order tags as the queue:

| Tag | Meaning |
|---|---|
| `em-sent` | Order emailed to supplier (also the duplicate guard) |
| `em-exception` | Supplier reported an availability problem; awaiting our decision |
| `em-awaiting-customer` | We asked the customer to consent to a substitution or delay |
| `em-backorder` | Held for restock; carries an order note with the FTC clock start date |
| `em-hold-risk` / `em-hold-unpaid` | Never sent; needs owner review |
| `em-resolved` | Exception closed |

A daily scheduled Flow digests every order tagged `em-exception` or `em-awaiting-customer` that is
more than 24 hours old and emails the owner. Tags are visible, filterable in the admin, free, and
survive without any infrastructure.

---

## Q5 — Margin Model

### Model inputs

| Input | Value | Source |
|---|---|---|
| Retail | Wholesale × 2.5, rounded to nearest `.95` | `build_import.py --markup 2.5` [VERIFIED: README] |
| Shopify Payments, Advanced, US online card | **2.5% + 30¢** | [VERIFIED: shopify.com/pricing] |
| Refund handling | **Original processing fee is NOT returned** on a refund; no extra fee is charged to process it | [CITED: help.shopify.com/manual/payments/shopify-payments/payouts/refunds] |
| Drop-ship fee | $3.50 per order shipped | [VERIFIED: supplier PDF] |
| Supplier shipping | $4–12 standard, **unknown until packed** | [VERIFIED: supplier PDF] |
| Customer shipping charge | $7.95, free over $75 | [VERIFIED: phase brief + `sections/ticker.liquid:24`] |
| Sales tax | Collected and remitted; net zero. Processing fee applies to it (~+$0.03 on a $15 order) — negligible, excluded below | [ASSUMED] |

### Catalogue price reality

Computed from `out/shopify_products.csv` (1,004 variants, 330 products):

| Statistic | Value |
|---|---|
| Minimum retail | **$2.95** |
| 10th percentile | $10.95 |
| **Median** | **$34.95** |
| 90th percentile | $49.95 |
| Maximum | $169.95 |
| Variants ≤ $9.95 | 74 (7%) |
| Variants ≤ $14.95 | **150 (15%)** |
| Variants ≤ $19.95 | 187 (19%) |
| **Products with a variant ≤ $14.95** | **62 of 330 (18%)** |
| Median variant weight | 156 g (5.5 oz) — comfortably under the 15 oz First Class threshold |
| 90th-percentile weight | 352 g (12.4 oz) |

### 🚩 Single-item order profit, $7.95 flat shipping

| Retail | S=$4 | S=$6 | S=$8 | S=$10 | S=$12 |
|---|---|---|---|---|---|
| $2.95 | $1.65 | **−$0.35** | **−$2.35** | **−$4.35** | **−$6.35** |
| **$6.95** *(the g-string)* | $3.95 | $1.95 | **−$0.05** | **−$2.05** | **−$4.05** |
| $9.95 | $5.67 | $3.67 | $1.67 | **−$0.33** | **−$2.33** |
| $12.95 | $7.40 | $5.40 | $3.40 | $1.40 | **−$0.60** |
| $14.95 | $8.55 | $6.55 | $4.55 | $2.55 | $0.55 |
| $19.95 | $11.42 | $9.42 | $7.42 | $5.42 | $3.42 |
| $24.95 | $14.30 | $12.30 | $10.30 | $8.30 | $6.30 |
| $34.95 *(median)* | $20.05 | $18.05 | $16.05 | $14.05 | $12.05 |
| $49.95 | $28.67 | $26.67 | $24.67 | $22.67 | $20.67 |

**Breakeven formula** (single item, retail `P` < $75, supplier shipping `S`):

```
profit = 0.575·P + 3.951 − S        →        breakeven P = (S − 3.951) / 0.575
```

| Supplier ship `S` | Breakeven retail |
|---|---|
| $4 | $0.09 — always profitable |
| $6 | $3.56 |
| $8 | $7.04 |
| $10 | $10.52 |
| **$12** | **$14.00** |

### 🚩 The flagged answer

**A single $6.95 g-string breaks even at $8 supplier shipping and loses $4.05 at $12.** More
broadly: **at the top of the supplier's own stated standard band, every single-item order under
$14.00 retail loses money.** That is 150 of 1,004 variants and 62 of 330 products.

Two things make this worse than the table suggests:

1. **We cannot price the risk away per-order**, because the supplier explicitly will not know the
   shipping cost until the parcel is packed. There is no way to check profitability before
   committing.
2. **The $3.50 fee is fixed per order.** It is 50% of a $6.95 sale before a single other cost.

### Multi-item baskets are fine

| Basket | Charged | Fees | COGS | $3.50 | Ship | **Profit** | Margin |
|---|---|---|---|---|---|---|---|
| $34.95 single | $42.90 | $1.37 | $13.98 | $3.50 | $6 | **$18.05** | 42% |
| $74.90 (2 items, just under free-ship) | $82.85 | $2.37 | $29.96 | $3.50 | $8 | **$39.02** | 47% |
| $79.90 (2 items, free ship) | $79.90 | $2.30 | $31.96 | $3.50 | $8 | **$34.14** | 43% |
| $75.60 (8 cheap items, free ship, ~2.7 lb) | $75.60 | $2.19 | $30.24 | $3.50 | $20 *(over-band, heavy)* | **$19.67** | 26% |

**The $75 free-shipping threshold is safe**, even for a heavy multi-item basket priced well over
the supplier's 1-lb estimate basis. The loss zone is *exclusively* low-value single-item orders.

### Return economics

A returned median ($34.95) item, customer pays return postage, item refunded but not shipping:

| Line | Amount |
|---|---|
| Refund to customer | −$34.95 |
| Processing fee, **not** returned | −$1.37 |
| COGS already paid to supplier | −$13.98 |
| Drop-ship fee already paid | −$3.50 |
| Supplier shipping already paid | −$6.00 |
| Shipping revenue retained | +$7.95 |
| **Net per return** | **≈ −$16.90** |

That assumes the supplier does **not** take the item back — which the drop-ship sheet neither
promises nor mentions. One return wipes out the profit from roughly one median order. At a 10%
return rate, returns cost about 8% of gross profit. Survivable, but it makes the final-sale scope
(Q6) a material commercial lever, not a legal footnote.

**Below roughly $20 retail, a refund-without-return is strictly cheaper than processing a
physical return** — return postage plus handling exceeds the recoverable value of an item we
cannot resell anyway.

### Mitigations, ranked

| # | Mitigation | Effort | Effectiveness | Notes |
|---|---|---|---|---|
| **1** | **Retail price floor** in `build_import.py`: `price = max(round_95(W × 2.5), FLOOR)` with FLOOR = **$14.95** | **Low** — one line in an existing script | **High** — mathematically eliminates the loss zone at S=$12 | A $2.95 item becomes $14.95 (5× wholesale). Entirely normal retail for a thong. **Recommended.** |
| 2 | Raise flat shipping $7.95 → $9.95 | Low — Shopify Settings → Shipping | Medium — moves breakeven from $14.00 to $10.61 | Does not fully close the gap alone. Good belt-and-braces with #1. |
| 3 | Minimum order value (~$25) | Medium | High | Native Shopify cart-validation requires a Shopify Function — ⚠️ [ASSUMED] plan availability outside Plus; **verify before planning**. A vanilla-JS cart-drawer guard is bypassable but adequate. |
| 4 | Bundle cheap items into 3-packs | High — catalogue restructuring | High | Raises AOV and amortises the $3.50. Good long-term, wrong for this phase. |
| 5 | Raise free-shipping threshold above $75 | Low | Low | Threshold is already safe. Would only hurt conversion. **Not recommended.** |

**Recommendation: #1 plus #2.** Together they put every realistic single-item basket in profit
even at the worst quoted standard shipping rate. Both are the owner's call.

⚠️ If the price floor is adopted, note that `sections/ticker.liquid` lines 24 and 28 hardcode
`Free Shipping Over $75` as a literal string, while `announcement-bar.liquid`, `header.liquid`, and
`cart-drawer.liquid` read a `free_shipping_threshold` setting. Any threshold change must touch the
hardcoded string too.

---

## Q6 — Returns

No returns policy document exists anywhere in this repo. `templates/` contains
`page.care-instructions.json` but **no Shipping & Returns template**, and a grep for
`return|refund` across `templates/` and `sections/page-*.liquid` returns nothing. The supplier
will insert our policy in every parcel — but only if we give them one, and we have not.

### What a US intimates policy must cover

There is **no federal law requiring a retailer to accept returns**. But most states impose a
default return window on a retailer who fails to post a policy conspicuously, and a "final sale"
designation holds up **only if it was visible before the customer paid**.
[CITED: privacypolicies.com/blog/return-refund-laws-usa; findlaw.com]

| Element | Requirement | Recommendation |
|---|---|---|
| **Conspicuous placement** | Must be visible before purchase — footer, PDP, and cart/checkout | Footer link + a short line on the PDP + cart drawer |
| **Return window** | State a definite number of days from delivery | 30 days from delivery |
| **Hygiene / final sale** | Intimates and swimwear become non-returnable once protective packaging or the hygienic liner is removed — widely accepted health-code practice | State explicitly: **unworn, unwashed, all tags attached, hygienic liner intact, original packaging.** Say it on the PDP, not only in the policy. |
| **Final-sale categories** | Must be disclosed pre-purchase | Recommend final sale on: thongs, g-strings, panties, bodystockings, hosiery. These are the highest-hygiene-risk and lowest-value items — i.e. exactly the items where a return costs more than it recovers. |
| **Who pays return postage** | Must be stated | Customer pays, **except** for our error or a defective item. Standard for a small merchant on thin margins. |
| **Restocking fee** | Optional; must be disclosed | **Recommend none.** A restocking fee on a $30 garment generates support tickets worth more than the fee. |
| **Refund method + timing** | Must be stated | Original payment method, 5–10 business days after we receive the item |
| **Exchanges** | Optional | **Recommend none at launch.** An exchange requires a second supplier order and a second $3.50 fee against zero new revenue. Offer "return + reorder" instead. |
| **Defective / wrong item** | Should be stated | We pay return postage and replace or refund. Photo evidence by email, no return required for low-value items. |
| **Damaged / lost in transit** | Should be stated | ⚠️ The supplier disclaims liability only for *international* First Class Mail. Domestic loss is **not addressed** — must be confirmed with them. |
| **FTC 30-day shipping** | Legally required | State a delivery estimate ("ships within 2 business days; 3–7 business days delivery") and the delay-notice/refund commitment |
| **How to start a return** | Practical necessity | Email `returns@<our-domain>` with the order number, receive an address and instructions. **Do not print a return address on anything the customer receives** — see below. |

### 🚩 Where does a returned item physically go?

This is the most important unanswered question in this section, and the drop-ship sheet says
nothing about it.

The parcel the customer receives carries **the supplier's warehouse address** under a coded
version of our company name and the words "Distribution Center". A customer who simply writes
"return to sender" sends our merchandise to Elegant Moments' loading dock, with no RMA, no
paperwork, and no agreement that they will do anything with it.

| Option | Viability |
|---|---|
| **Back to Elegant Moments** | ⚠️ **Not agreed.** The sheet contains no return provision at all. **Must be confirmed by phone before the policy is published.** If they accept returns, find out: to which address, whether an RMA is required, whether they credit the wholesale cost, and what restocking fee applies. |
| **To the owner's own address** | ✅ Realistic default. Requires the return instructions to be issued **on request by email**, never pre-printed. Owner then holds unsellable inventory — acceptable at low volume. |
| **Refund without return ("keep it")** | ✅ **Strongly recommended for items under ~$20 retail.** Return postage plus handling exceeds recovery on a garment we cannot resell. Cheaper, faster, and generates goodwill. |
| **Third-party returns processor** | ❌ Not at this volume — fixed monthly cost against a handful of returns |

**Recommended policy shape:** 30 days · unworn/unwashed/tags-on/liner-intact · customer pays return
postage · no restocking fee · **final sale on thongs, g-strings, panties, bodystockings, hosiery**
· return address issued by email on request · refund-without-return at our discretion under $20 ·
no exchanges.

### Deliverable format

Two artefacts, both required:

1. **Storefront page** — a Shopify policy page (Settings → Policies → Refund policy) so it also
   appears in the checkout footer automatically, or a theme page section following the existing
   `page-content.liquid` pattern. The Shopify-native policy is preferable because it is linked from
   checkout without any theme work.
2. **A one-page PDF** emailed once to `dropship@elegantmomentslingerie.com` for them to insert in
   every parcel. Keep it to a single page, brand it, and include the returns email address, the
   window, the condition requirements, and the final-sale categories.
   ⚠️ **Confirm with the supplier** that this is a one-time file-on-record and not a per-order
   attachment — the sheet's wording ("send us a copy if you would like it included in with all of
   your orders") reads as one-time, but it is worth 30 seconds on the phone. If it turns out to be
   per-order, Stage 1 Flow cannot do it and Mechanic becomes mandatory rather than optional.

---

## Q7 — Compliance

### Customer PI leaves the store on every order

Each order email contains a customer's full name and residential address — clearly personal
information — sent to a third party in Pennsylvania.

**CCPA / CPRA.** Transfers to a **service provider** do not trigger consumer opt-out rights, but
only because service providers are *contractually* restricted. Without those written terms, the
same disclosure is treated as a **sale or share to a "third party"**, which does trigger opt-out
rights. The contract must: prohibit selling or sharing the PI; identify the specific business
purposes for processing; and require the same level of privacy protection the CCPA requires of us.
[CITED: iapp.org; california-ccpa.org/cpra/section-7051-contract-requirements-for-service-providers-and-contractors/]

**The supplier's PDF statement is not a contract.** "AT NO TIME DO WE CONTACT YOUR CUSTOMERS OR
SELL ANY CUSTOMER INFORMATION TO ANYONE!" is a unilateral marketing assertion in a one-page
information sheet. It is helpful evidence of intent, but it is not signed, not mutual, and does not
identify a business purpose or a protection standard.

**Action:** get a short written service-provider addendum from Elegant Moments — email
confirmation with the four required terms is materially better than nothing, a countersigned
one-pager is better still.

⚠️ **Applicability caveat, stated honestly:** CCPA/CPRA obligations attach to a "business" meeting
one of three thresholds — >$25M annual revenue, PI of 100,000+ California consumers/households, or
≥50% of revenue from selling/sharing PI. A newly launched store almost certainly meets none of
them today. [ASSUMED — thresholds from training knowledge, not re-verified this session.] However,
the theme already ships a CCPA cookie banner and `PROJECT.md` asserts CCPA compliance, so the
correct posture is to hold the line we have publicly taken rather than rely on being under
threshold.

### Privacy policy updates required

| Add | Why |
|---|---|
| Category of recipient: **suppliers and fulfilment partners** | Required disclosure of who receives PI |
| Categories disclosed: **identifiers (name, shipping address), commercial information (order contents)** | Required disclosure of what is shared |
| Business purpose: **order fulfilment and shipping** | Required contract/notice element |
| That fulfilment partners are contractually barred from selling or using PI for their own purposes | Supports the service-provider (not third-party) characterisation |
| Retention: how long order emails and their PI persist in the sending system | Directly implicated by the Postmark 45-day content retention below |
| That parcels ship blind, under a coded sender name — **a positive privacy feature worth stating on the storefront** | Genuinely differentiating for a lingerie brand; belongs in FAQ and PDP copy, not only the policy |

### Sending infrastructure

| Path | Audit trail | Suitability |
|---|---|---|
| **Personal Gmail** | ❌ None meaningful | ❌ **Do not use.** No delivery/bounce record, no retention control, ~500/day sending limit, and automated sending from a personal account risks suspension — taking the whole fulfilment pipeline with it. Also puts customer PI in a personal mailbox with no deletion control. |
| **Flow `Send internal email`** | ⚠️ Partial — the Flow run log proves the workflow ran and what data it saw, but there is **no delivery confirmation and no bounce visibility** | ✅ **Acceptable for Stage 1.** Shopify infrastructure, not a personal mailbox, which satisfies the ROADMAP constraint's intent. The gap (no delivery proof) is covered by the scheduled reconciliation Flows and the `Cc:` copy. |
| **Postmark via Mechanic** | ✅ Full — delivery, bounce, and open events; 45 days of rendered message content, extendable to 365 | ✅ **Best.** ⚠️ But note the flip side: 45 days of customer names and home addresses sitting in Postmark's message store. That is a **retention disclosure**, and if we extend to 365 days it becomes a real one. Recommend leaving retention at the 45-day default and saying so in the privacy policy. |
| Dedicated Google Workspace mailbox + SMTP | ⚠️ Partial | Acceptable middle ground if Mechanic is rejected on cost. Better than personal Gmail on control and deletion; still no structured bounce handling. |

**Sender-address requirement (both stages):** the From/Reply-To must be a **real, monitored mailbox
on our own domain** — `orders@<our-domain>` — because that is where every tracking email and every
out-of-stock question will land. Shopify's default sender may render as
`store+<shop-id>@shopifyemail.com` unless the domain is authenticated
[CITED: help.shopify.com/manual/shopify-flow/reference/actions/send-email], and nobody reads that
address. **Authenticate the sending domain (SPF/DKIM) before this phase ships.**

### TCPA

Unchanged by supplier email, but relevant if shipping notifications go by SMS. Shopify's native
fulfilment notification is email. Any Klaviyo SMS shipping alert needs the same explicit opt-in and
9am–9pm-local quiet hours already mandated in `CLAUDE.md`. **Recommendation: keep shipping
notifications on email only for this phase** — it avoids a new TCPA surface and Shopify's native
email is free and already built.

### PCI

Nothing changes. No card data appears in any of these emails. Worth noting separately: the supplier
charges **our** business card on file, which is the owner's payment instrument, not customer data —
but it does mean an unreconciled duplicate order is a real cash loss, which is why the weekly card
reconciliation in Q8 matters.

### Security debt already on record

From memory (`shopify-store-setup-todo`): the store admin password was shared with the Elegant
Moments portal and sent in plaintext email, and the app client secret appeared in a session
transcript. **Both should be rotated and 2FA enabled before this phase goes live**, since Phase 7
is the point at which that account starts moving real customer data and real money.

---

## Q8 — Failure Modes and Monitoring

### At 5 orders/day (≈150/month)

| Failure | Likelihood | Impact | Detection |
|---|---|---|---|
| Flow email silently not delivered | Low-medium | Order never ships; discovered days later by an angry customer | Scheduled Flow B (unfulfilled >96h) |
| Supplier misreads a plus-size style (`2987` vs `2987X`) | **Medium** | Wrong garment shipped; return + reship + two $3.50 fees | Customer complaint only. **Prevented by the SKU-derived format in Q2, not detected.** |
| Duplicate send | Low | Two parcels, two $3.50 fees, one refund | `em-sent` tag guard prevents; weekly card reconciliation detects |
| Oversell (stale inventory) | **High** — 498 rows hold <10 units | OOS exception, refund, FTC clock | Supplier email; reduced by daily inventory refresh |
| Owner forgets to enter tracking | Medium | Customer never notified; support ticket | Scheduled Flow B |
| Supplier does not reply at all | Low | Order in limbo | Scheduled Flow B |
| Fraudulent order shipped | Low | Chargeback + non-refunded processing fee + COGS + fees | Risk condition on the Flow trigger |

Economics at this volume: **$525/month in drop-ship fees alone.** Manual tracking entry is
~2 hours/month. **Automation of the inbound half is not worth building yet.**

### At 50 orders/day (≈1,500/month)

Everything above, plus:

| New failure | Why it appears only at scale |
|---|---|
| **Supplier throughput ceiling** | Their office is staffed 9:00–4:30 ET Mon–Fri — 7.5 hours. 50 orders is one every 9 minutes of staffed time, keyed by hand, every day. ⚠️ **This is the untested assumption most likely to break the business model.** Their sheet states no volume ceiling. **Ask them directly what daily volume a drop-ship account can absorb.** |
| Manual tracking entry becomes real work | 1,500 × 45s ≈ **19 hours/month**. Now Mechanic's $99 is obviously cheap. |
| Weekend pile-up | An order placed Friday 5:01 PM ET does not ship until Tuesday. At 50/day that is ~100 orders queued over a weekend, all with delivery-estimate clocks running. |
| Exception volume | If 3% hit OOS, that is 1–2 exception emails **per day**, each an individually written reply. Needs canned responses, not ad-hoc typing. |
| Email thread confusion | 50 near-identical emails/day from the same sender. Subject lines must be unambiguous and unique — put the order number first. |
| Reconciliation becomes impossible by eye | 1,500 orders vs 1,500 card charges. Needs a scripted comparison. |

Economics: **$5,250/month in drop-ship fees.** Also worth raising with the supplier: at that
volume, is there a negotiated per-order fee or a bulk arrangement?

### Minimum viable monitoring

Five controls. The first three are free and need no infrastructure.

**1. Send-failure detector — Scheduled Flow A (daily 10:00 ET)**
`Scheduled time` → `Get order data` with a query along the lines of
`financial_status:paid AND -tag:em-sent AND created_at:<-1d` → if the result list is non-empty,
`Send internal email` to the owner listing the order numbers.
⚠️ `Get data` actions return **max 100 items** — at 50 orders/day that is fine for a 1-day window
but would truncate on a longer one.

**2. Supplier non-reply detector — Scheduled Flow B (daily 10:00 ET)**
`fulfillment_status:unfulfilled AND tag:em-sent AND created_at:<-4d` → alert.
**96 hours, not 72** — the supplier's 24–48h window is Monday–Friday, so a Friday-evening order
legitimately has no tracking until Tuesday. A 72-hour threshold would page the owner every single
Monday.

**3. Exception-queue ager — Scheduled Flow C (daily)**
`tag:em-exception OR tag:em-awaiting-customer`, created >24h ago → alert. This is the FTC clock.

**4. Inventory freshness**
Download a fresh `liveinventory.csv` from `b2b.elegantmoments.com` and run
`python push_products.py --inventory-only`. There is no supplier API, so the download step is
inherently manual. **Daily.** 498 rows currently hold fewer than 10 units, so a 24-hour-old
snapshot is already meaningfully wrong. This is the single highest-leverage operational habit in
the whole phase — every oversell prevented here is an exception email, a refund, and an FTC clock
avoided.

**5. Weekly financial reconciliation**
Shopify order count and total for the week ⟷ Elegant Moments credit-card charges for the week.
This is the only control that catches **both** directions of failure: an order we sent that they
never charged us for (dropped), and a charge with no matching order (duplicate). Everything else
only catches drops.

**Optional (Stage 2):** Postmark bounce and delivery webhooks → immediate alert. This is the only
control that catches a delivery failure *within minutes* rather than *within 96 hours*, and it is
the strongest single argument for Stage 2 beyond packing slips.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Customer shipping notification | A templated "your order shipped" email | `fulfillmentCreate(notifyCustomer: true)` | Shopify's notification is already branded, already localised, already links to the order status page, and already handles partial fulfilment |
| Tracking URL construction | Carrier URL templates per carrier | `trackingInfo.company: "USPS"` and let Shopify build the URL | Shopify recognises hundreds of carriers and auto-detects from number format |
| Order state machine | A database of order status | Shopify order **tags** + fulfilment orders | The state already exists in Shopify; a parallel store guarantees drift |
| Duplicate-send prevention | A dedupe table | The `em-sent` tag checked as a Flow condition | Atomic enough at this volume, visible in the admin, and free |
| Refund idempotency | A retry ledger | `@idempotent(key: "<uuid>")` on `refundCreate` — **required as of 2026-04** | Shopify enforces it; building your own is both redundant and non-compliant with the API |
| Inbound email parsing infrastructure | An IMAP poller | Mechanic inbound (Postmark-backed) | Postmark already gives `stripped_text_reply`, structured `from_full`/`to_full`, and parsed attachments |
| PDF generation | A PDF library in a custom service | Mechanic's file generator (PDF rendered from HTML) | The only reason to build a service at all would be this; Mechanic includes it |
| Cron / scheduling | A hosted cron job | Flow `Scheduled time` trigger | Free, hosted, no uptime to own; only limit is a 10-minute minimum interval |
| Order query API client | A custom paginated fetcher | Flow `Get order data` | Runs the Order query natively; only constraint is 100 items per run |
| Fraud screening | Custom heuristics | Shopify's own risk assessment via the `Order risk analyzed` trigger | Shopify sees cross-store signal we never will |

**Key insight:** almost every component this phase needs already exists inside Shopify and is free.
The only genuinely missing capabilities are (a) attaching a file to an outbound email and
(b) receiving an inbound email. Those two gaps — and nothing else — are what a paid tool buys.
Scope Stage 2 strictly to them.

---

## Common Pitfalls

### Pitfall 1: Deriving the supplier style from the product title
**What goes wrong:** The merged plus-size product `em-2987` is titled "Lace thong — Style 2987",
but the plus variant's actual supplier style is `2987X`. Every plus-size order ships the wrong
garment.
**Why it happens:** The title looks authoritative and is the most obvious field to reach for.
**How to avoid:** Derive style from `li.sku | split: "-" | first`. Never from the title, never from
tags (which list both styles).
**Warning signs:** Plus-size customers reporting the wrong item; returns clustered on
`Extended Sizing`-tagged products.

### Pitfall 2: `notifyCustomer` defaults to `false`
**What goes wrong:** The fulfilment is created, the order shows as shipped, and the customer is
never told. Silent, and only discovered via support tickets.
**Why it happens:** It is a default, not an error. Nothing fails.
**How to avoid:** Set `notifyCustomer: true` explicitly on every `fulfillmentCreate`.
**Warning signs:** "Where is my order?" tickets on orders the admin shows as fulfilled.

### Pitfall 3: Triggering on `Order created` instead of `Order risk analyzed`
**What goes wrong:** Orders are emailed to the supplier before fraud analysis completes and,
in some payment flows, before payment settles. A fraudulent order ships and the chargeback costs
the refund plus COGS plus $3.50 plus shipping plus a non-refunded processing fee.
**Why it happens:** `Order created` is the obvious trigger and it is listed first.
**How to avoid:** Trigger on `Order risk analyzed`; gate on `financial status = PAID` and
`risk ≠ HIGH`.
**Warning signs:** Chargebacks on orders that shipped within minutes of being placed.

### Pitfall 4: HTTP-retry duplicate orders (Stage 2)
**What goes wrong:** Flow's `Send HTTP request` retries 5xx responses for up to 24 hours. If the
endpoint sent the supplier email and *then* failed, the retry sends a second one. The supplier
ships twice and charges $3.50 twice — the exact duplication their PDF warns about.
**Why it happens:** Retry is on by default and is usually the right behaviour.
**How to avoid:** Key the send on the Shopify order ID, make it idempotent at the endpoint, and
check the `em-sent` tag before sending, not after.
**Warning signs:** Card charges exceeding order count in the weekly reconciliation.

### Pitfall 5: Parsing the variant title to get colour and size
**What goes wrong:** Variant title `"Red / O/S"` splits on `/` into three parts, not two. Colour
values like `"Black/Red"` compound the problem: `"Black/Red / Q/S"` is genuinely ambiguous.
**Why it happens:** `variant.title` is the convenient single field.
**How to avoid:** Use `selectedOptions` name/value pairs. If unavailable in Flow, split on the
literal `" / "` (space-slash-space) and treat any further slashes as data.
**Warning signs:** Emails showing size `S` where the order was `O/S`.

### Pitfall 6: Restocking on refund
**What goes wrong:** Refunding an out-of-stock item with restock enabled adds a unit back to
Shopify's inventory for an item the supplier has confirmed it does not have. The next customer
oversells the same item.
**Why it happens:** Restock-on-refund is a sensible default for merchants who hold their own stock.
**How to avoid:** Never restock. Shopify inventory is a supplier snapshot, not a count of goods we
possess.
**Warning signs:** Repeat OOS exceptions on the same style.

### Pitfall 7: A 72-hour non-reply alert
**What goes wrong:** The supplier ships in 24–48h **Monday–Friday**. A Friday-evening order has no
tracking until Tuesday. A 72-hour alert fires every Monday and is ignored within two weeks — and
then a real failure is ignored too.
**How to avoid:** 96 hours, or exclude weekends.
**Warning signs:** The owner filtering the alert to a folder.

### Pitfall 8: Bumping `API_VERSION` in `push_products.py` as a side effect
**What goes wrong:** That file is pinned to `2025-10` and currently drives product creation, image
upload, and inventory backfill. Bumping it to `2026-07` to add fulfilment code silently changes
behaviour on paths that are working today — including `refundCreate`'s now-mandatory
`@idempotent` directive if refund logic lands there.
**How to avoid:** Put fulfilment/refund code in a **separate module with its own version constant**,
or bump deliberately and re-test the product and inventory paths.

### Pitfall 9: Sending from an address nobody reads
**What goes wrong:** The supplier replies with tracking to whatever address the email came from.
If that is `store+<shop-id>@shopifyemail.com`, the reply vanishes.
**How to avoid:** Authenticate the sending domain and use a real monitored mailbox
(`orders@<our-domain>`) as the sender/reply-to before this phase ships.
**Warning signs:** Orders sent successfully but no tracking ever arrives.

### Pitfall 10: Attaching a packing list while also using the online order center
**What goes wrong:** Their PDF states this explicitly — "may result in the order being
duplicated."
**How to avoid:** Pick one channel and stay on it. **Email only.** Never mix.

---

## Code Examples

### Flow Liquid — supplier order email body (Stage 1)

⚠️ Field paths are drawn from Shopify's Flow variable documentation
[CITED: help.shopify.com/manual/shopify-flow/getting-started/concepts/variables]. `selectedOptions`
availability on the Flow line-item variable is [ASSUMED] — confirm in the Flow editor's variable
picker and fall back to `variant.title` splitting if absent.

```liquid
SOLEIL NOIR — DROP SHIP ORDER {{ order.name }}
Placed: {{ order.createdAt }}

SHIP TO
  {{ order.shippingAddress.firstName }} {{ order.shippingAddress.lastName }}
  {{ order.shippingAddress.address1 }}
  {% if order.shippingAddress.address2 != blank %}{{ order.shippingAddress.address2 }}
  {% endif %}{{ order.shippingAddress.city }}, {{ order.shippingAddress.provinceCode }} {{ order.shippingAddress.zip }}
  {{ order.shippingAddress.countryCodeV2 }}
  {% if order.shippingAddress.phone != blank %}Phone: {{ order.shippingAddress.phone }}{% endif %}

ITEMS
{% for li in order.lineItems %}
  ITEM {{ forloop.index }}
{%- if li.sku == blank %}
    *** SKU MISSING — DO NOT SHIP, CONTACT US ***
{%- else %}
    STYLE ....... {{ li.sku | split: "-" | first }}
{%- endif %}
{%- for opt in li.variant.selectedOptions %}
    {{ opt.name | upcase }} ....... {{ opt.value }}
{%- endfor %}
    QTY ......... {{ li.quantity }}
    (our ref: {{ li.title }} / SKU {{ li.sku }})
{% endfor %}

Reply to this address with tracking. Please include our order
reference {{ order.name }} in your reply.
```

**Subject line — order number first, so 50/day stay sortable and unique:**

```liquid
{{ order.name }} — Soleil Noir drop ship order
```

### `fulfillmentCreate` — write tracking back (Admin GraphQL 2026-07)

Verified shape [CITED: shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/build-fulfillment-solutions].

```graphql
# 1) Find the open fulfillment order
query OrderFulfillmentOrders($id: ID!) {
  order(id: $id) {
    id
    name
    fulfillmentOrders(first: 10, query: "status:open") {
      nodes {
        id
        status
        supportedActions { action }
        lineItems(first: 50) {
          nodes { id remainingQuantity }
        }
      }
    }
  }
}
```

```graphql
# 2) Fulfil it with tracking — notifyCustomer MUST be true
mutation FulfillWithTracking($fulfillment: FulfillmentInput!) {
  fulfillmentCreate(fulfillment: $fulfillment) {
    fulfillment { id status trackingInfo { company number url } }
    userErrors { field message }
  }
}
```

```json
{
  "fulfillment": {
    "notifyCustomer": true,
    "trackingInfo": { "company": "USPS", "number": "9400111899560000000000" },
    "lineItemsByFulfillmentOrder": [
      {
        "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/1234567890",
        "fulfillmentOrderLineItems": [
          { "id": "gid://shopify/FulfillmentOrderLineItem/9876543210", "quantity": 1 }
        ]
      }
    ]
  }
}
```

Omitting `fulfillmentOrderLineItems` fulfils the whole fulfilment order — correct for the common
case where the supplier ships everything.

### `refundCreate` — partial refund for an out-of-stock line

⚠️ **The `@idempotent` directive is mandatory as of 2026-04.**
[CITED: shopify.dev/changelog/making-idempotency-mandatory-for-inventory-adjustments-and-refund-mutations]

```graphql
mutation RefundOutOfStockLine($input: RefundInput!, $key: String!) {
  refundCreate(input: $input) @idempotent(key: $key) {
    refund { id totalRefundedSet { shopMoney { amount currencyCode } } }
    userErrors { field message }
  }
}
```

```json
{
  "key": "b7e2c1a4-3f5d-4e8a-9c1b-2d6f7a8e9c0d",
  "input": {
    "orderId": "gid://shopify/Order/1234567890",
    "note": "Elegant Moments confirmed style 2987X / Red / Q\/S out of stock",
    "notify": true,
    "refundLineItems": [
      { "lineItemId": "gid://shopify/LineItem/1111111111", "quantity": 1 }
    ]
  }
}
```

Note the absence of `restockType` — deliberate. See Pitfall 6.
⚠️ [ASSUMED] `RefundLineItemInput` accepts `restockType`/`locationId`; the 2026-07 doc page did not
enumerate them. Since we do not want restocking, this does not block the build — but do not assume
the fields exist.

### Mechanic — outbound order email with a PDF packing slip (Stage 2)

Shape derived from the documented option names [CITED: learn.mechanic.dev/core/actions/email].

```liquid
{% action "email" %}
  {
    "to": "dropship@elegantmomentslingerie.com",
    "cc": "orders@soleilnoir.example",
    "reply_to": "orders@soleilnoir.example",
    "from_display_name": "Soleil Noir Orders",
    "subject": {{ order.name | append: " — Soleil Noir drop ship order" | json }},
    "body": {{ body_html | json }},
    "attachments": {
      {{ "packing-slip-" | append: order.name | append: ".pdf" | json }}: {
        "pdf": {{ packing_slip_html | json }}
      }
    }
  }
{% endaction %}
```

⚠️ The exact `attachments` map shape for PDF-from-HTML is [ASSUMED] from the prose description
("PDFs rendered from HTML") — verify against `learn.mechanic.dev` file-generator docs during
execution before writing the task.

---

## State of the Art

| Old approach | Current approach | When changed | Impact here |
|---|---|---|---|
| `fulfillmentCreateV2`, `fulfillmentTrackingInfoUpdateV2` | `fulfillmentCreate`, `fulfillmentTrackingInfoUpdate` | **2024-10** | Use the un-suffixed names. Any tutorial older than late 2024 will be wrong. |
| REST Fulfillment API | GraphQL fulfilment orders | 2023 onward | Do not use REST fulfilment endpoints |
| `OrderRisk`, `order.riskLevel`, `OrderRiskLevel` enum | Risk Assessments API — `OrderRiskAssessment`, `RiskAssessmentResult` (adds `PENDING`, `NONE`) | **2024-04** | Affects the Flow risk condition and any direct risk query |
| Optional idempotency on refund/inventory mutations | **Mandatory** `@idempotent(key:)` directive | **2026-04** (optional from 2026-01) | `refundCreate` fails without it |
| Flow exclusive to Plus/Advanced | Flow free on Basic and above | July 2023 | Confirms zero-cost Stage 1 |
| `edges`/`node` traversal in Flow Liquid | Direct iteration: `{% for li in order.lineItems %}` | — | Older community snippets showing `.edges` are outdated |

**Deprecated / avoid:**
- REST Admin API for orders and fulfilment — GraphQL only
- `order.riskLevel` — replaced by risk assessments
- Any `...V2` fulfilment mutation name

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Node.js | Existing theme build (PostCSS/Tailwind) | ✓ | v22.14.0 | — |
| Python | Existing supplier pipeline | ✓ | 3.10.7 | — |
| Shopify Flow | Stage 1 outbound + all monitoring | ✓ (free on Advanced) | — | None needed |
| Flow `Send HTTP request` | Stage 2 only | ✓ (Advanced qualifies) | — | Mechanic native triggers |
| Shopify Admin API token | Tracking write-back, refunds | ✓ (client-credentials, ~24h TTL) | scopes granted per brief | Re-mint per run |
| `read/write orders`, `write_merchant_managed_fulfillment_orders` | `fulfillmentCreate`, `refundCreate` | ✓ per phase brief | — | — |
| `ctx7` (Context7 CLI) | Documentation lookup | ✗ | — | WebFetch against shopify.dev — used throughout this research |
| `slopcheck` | Package legitimacy gate | ✗ (`pip install` failed: no `--break-system-packages` option on this pip) | — | N/A — no packages recommended |
| Mechanic app | Stage 2 only | ✗ not installed | — | Stage 1 needs nothing |
| Postmark account | Stage 2 only (bundled with Mechanic) | ✗ | — | Mechanic includes it |
| Authenticated sending domain (SPF/DKIM) | **Both stages** | ✗ **unverified** | — | **None — this is a blocker** |
| `orders@<our-domain>` mailbox | Both stages — receives tracking + OOS | ✗ **unverified** | — | **None — this is a blocker** |
| `b2b.elegantmoments.com` login | Inventory refresh | ✓ per memory (credentials shared — rotate) | — | None; no supplier API |

**Missing with no fallback (blocking):**
- A real, monitored mailbox on our own domain for sending and receiving supplier mail
- SPF/DKIM authentication on the sending domain
- A published returns policy (nothing exists in `templates/` or `sections/`)
- A written service-provider term with Elegant Moments

**Missing with fallback:**
- `ctx7` → WebFetch against official docs (used throughout)
- Mechanic → Stage 1 requires none of it

---

## Package Legitimacy Audit

**No external packages are required under the recommended architecture.**

Stage 1 is entirely Shopify-native (Flow + admin UI) and installs nothing. The existing supplier
pipeline (`build_import.py`, `push_products.py`) is **pure Python standard library** — `argparse`,
`csv`, `json`, `re`, `sys`, `base64`, `mimetypes`, `os`, `time`, `collections`, `pathlib`,
`urllib` — with a single optional dependency (`openpyxl`) already established in a prior phase and
not touched here. [VERIFIED: direct source inspection]

The theme's `package.json` has **zero runtime dependencies**; devDependencies are `autoprefixer`,
`postcss`, `postcss-cli`, `tailwindcss` — all pre-existing.

`slopcheck` could not be installed in this environment (`pip install slopcheck
--break-system-packages` → "no such option"; plain install also unavailable). Per protocol this
would force every recommended package to `[ASSUMED]` — but since **the recommended architecture
recommends no packages at all, the audit table is empty by construction.**

| Package | Registry | Disposition |
|---|---|---|
| *(none)* | — | Phase requires no new dependencies |

**If the planner deviates toward a custom hosted function** (the Option C path, which this research
recommends against), that decision reintroduces a dependency surface and **must** re-run the
package legitimacy gate with a working `slopcheck` before any install task is written.

---

## Validation Architecture

### Test framework

| Property | Value |
|---|---|
| Framework | **None.** No `tests/`, no `test/`, no test runner in `package.json` (scripts are `build`, `watch`, `dev` only) |
| Config file | none |
| Quick run command | none |
| Full suite command | none |

This is a Liquid theme plus a handful of standard-library Python scripts, and the phase's
deliverables are largely **configuration in the Shopify admin** (Flow workflows, shipping rates,
policies) rather than code in this repo. A unit-test harness would validate almost none of the
actual risk surface.

### Phase requirements → validation map

| Req | Behaviour | Type | Command / procedure | Exists? |
|---|---|---|---|---|
| DROP-01 | Paid order emails supplier | **manual-only** | Place a real $1 test order; confirm arrival at a test address before pointing at `dropship@` | ❌ Wave 0 |
| DROP-02 | Plus-size style renders as `2987X` not `2987` | **unit** | `pytest tests/test_order_email.py::test_plus_size_style_from_sku` — a pure function `style_from_sku(sku)` mirroring the Flow Liquid rule, tested against real SKUs from `out/shopify_products.csv` | ❌ Wave 0 |
| DROP-03 | No duplicate send | manual | Re-run the Flow against an already-tagged order; assert no second email | ❌ Wave 0 |
| DROP-04 | Tracking fires the customer notification | manual | Fulfil a test order with `notifyCustomer: true`; confirm the email lands | ❌ Wave 0 |
| DROP-05 | Exception policy documented + queue tags exist | doc review | Checklist | ❌ Wave 0 |
| DROP-06 | Returns policy published + PDF on file | doc review | 200 on the policy URL; supplier confirms receipt | ❌ Wave 0 |
| DROP-07 | Privacy policy updated; supplier term obtained | doc review | Checklist | ❌ Wave 0 |
| DROP-08 | Monitoring Flows fire | manual | Deliberately leave a test order untagged; confirm the daily alert | ❌ Wave 0 |
| DROP-09 | No loss-making single-item basket | **unit** | `pytest tests/test_margin.py::test_no_single_item_loss` — assert `min_retail_after_floor` clears breakeven at `S=$12`, run against the real price list | ❌ Wave 0 |

### Sampling rate

- **Per task commit:** `python -m pytest tests/ -x -q` (once Wave 0 creates it) — targets DROP-02
  and DROP-09, the only two requirements with meaningful pure-function logic
- **Per wave merge:** full pytest run + manual checklist for the configuration items
- **Phase gate:** one end-to-end live test order through the real supplier, tracking returned and
  written back, **before** the automation is pointed at production traffic

### Wave 0 gaps

- [ ] Framework install: `python -m pip install pytest`
- [ ] `tests/test_order_email.py` — covers DROP-02 (the highest-consequence logic bug in the phase)
- [ ] `tests/test_margin.py` — covers DROP-09
- [ ] `tests/conftest.py` — fixture loading a small **anonymised** SKU sample.
      ⚠️ **The repo is public and the supplier licence forbids redistribution.** Fixtures may
      contain style numbers and sizes (needed for the test) but **must not** contain wholesale
      prices, and must not embed `out/shopify_products.csv` wholesale columns.
- [ ] A test recipient address for DROP-01 dry runs, so no test order ever reaches `dropship@`

---

## Security Domain

### Applicable ASVS categories

| Category | Applies | Standard control |
|---|---|---|
| V2 Authentication | yes | Shopify OAuth client-credentials; ~24h token TTL, re-minted per run. **Rotate the client secret** — memory records it appearing in a session transcript |
| V3 Session Management | no | No custom sessions; no user-facing app in Stage 1 |
| V4 Access Control | yes | Admin API scopes are the boundary. Do not request scopes beyond `read/write orders`, `write_merchant_managed_fulfillment_orders`, `read/write inventory`, `read_locations` for this phase |
| V5 Input Validation | **yes** | **Inbound email is untrusted input.** A parsed tracking number must be validated against expected carrier formats before it reaches `fulfillmentCreate`, and the sender must be verified as the supplier's domain |
| V6 Cryptography | yes | Never hand-roll. Webhook HMAC verification (Stage 2 custom path only) must use a constant-time comparison from the stdlib |
| V7 Error Handling & Logging | yes | Logs will contain customer names and addresses. Scope retention deliberately; do not log full addresses at debug level into anything long-lived |
| V8 Data Protection | **yes** | Customer PI in transit to a third party — the core compliance surface of this phase |
| V9 Communications | yes | TLS everywhere; SPF/DKIM on the sending domain |

### Known threat patterns

| Pattern | STRIDE | Mitigation |
|---|---|---|
| Spoofed "tracking" email injects a fake number, or a forged "cancel this order" | **Spoofing** | Verify the sender domain on inbound. **Never** act on an inbound email that fails SPF/DKIM. Postmark exposes the auth headers |
| Replayed webhook or retried HTTP causes a duplicate supplier order | **Tampering / Repudiation** | Idempotency keyed on Shopify order ID; `em-sent` tag as the guard |
| Customer PI leaked via an over-broad log, a public repo, or an unbounded mail retention window | **Information Disclosure** | Repo is public — never commit an order payload. Cap Postmark retention at the 45-day default and disclose it |
| Fraudulent order ships before risk analysis completes | **Elevation / financial** | `Order risk analyzed` trigger + `risk ≠ HIGH` + `financial_status = PAID` |
| Stale 24h token used by a long-running job → silent auth failure mid-run | **Denial of Service** | Re-mint before each run; alert on 401 rather than swallowing it |
| Supplier account credentials reused from the store admin password (**already true**, per memory) | **Spoofing** | **Rotate both, enable 2FA** before this phase handles real money |
| Injection into the supplier email body via a crafted address or product title | Tampering | Emails are plain text to a human, so injection risk is low — but strip control characters and cap field lengths so a crafted address cannot forge a second ITEM block |

---

## Decisions Only The Owner Can Make

Four of these block meaningful parts of the build and are marked 🔴.

| # | Decision | Why it needs the owner | Blocks |
|---|---|---|---|
| 1 🔴 | **Retail price floor** — adopt a floor (recommended $14.95) or keep straight 2.5× down to $2.95? | Pricing and brand positioning. 62 of 330 products are affected. | DROP-09, and the whole margin position |
| 2 🔴 | **Minimum order value** — impose one (~$25), or accept losses on cheap solo orders? | Conversion vs. margin trade-off | DROP-09 |
| 3 🔴 | **Return destination** — supplier warehouse (needs their agreement), the owner's own address, or refund-without-return? | Requires a physical address the owner controls and is willing to publish on request | DROP-06 |
| 4 🔴 | **Final-sale scope** — which categories are non-returnable? (recommended: thongs, g-strings, panties, bodystockings, hosiery) | Commercial + brand-voice call with real revenue impact | DROP-06 |
| 5 | Flat shipping rate — keep $7.95 or raise to $9.95? | Conversion trade-off | Margin model |
| 6 | Free-shipping threshold — keep $75? (research says it is safe) | Pricing strategy | — |
| 7 | Stage 2 budget — is $16–99/mo for Mechanic acceptable, and at what volume? | Spend | Stage 2 scope |
| 8 | Sending mailbox — which domain and address? Is Google Workspace already in place? | Owns the domain and DNS | **Both stages** |
| 9 | Default out-of-stock policy — adopt "ship available, refund unavailable" as standing? | Customer-experience call | DROP-05 |
| 10 | Return postage — customer pays except for our error? Any restocking fee? | Commercial | DROP-06 |
| 11 | Exchanges — offer them at launch? (research recommends no; each costs a second $3.50 against zero new revenue) | Customer-experience vs. margin | DROP-06 |

---

## Must Be Confirmed With Elegant Moments (phone or email)

Their office is Mon–Fri 9:00 AM–4:30 PM Eastern, `1-800-876-4363` /
`dropship@elegantmomentslingerie.com`. **This is a single 15-minute call.** Items 1–4 are blocking.

| # | Question | Why it matters |
|---|---|---|
| 1 🔴 | **Will you accept returned merchandise, and to what address?** Is an RMA required? Do you credit the wholesale cost? Is there a restocking fee? | The sheet says **nothing** about returns. The parcel's return address is *their* warehouse, so customers will send goods there by default whether or not they have agreed to it. Blocks the returns policy. |
| 2 🔴 | **Will you include our order number in your tracking reply?** | The only reliable join key for automating tracking write-back. Without it, matching relies on customer name. Blocks any Stage 2 parser. |
| 3 🔴 | **Is the returns-policy insert a one-time file-on-record, or must it be attached to every order?** | If per-order, Stage 1 Flow cannot do it (no attachments) and Mechanic becomes mandatory. Changes the architecture. |
| 4 🔴 | **What daily order volume can a drop-ship account absorb?** Is there a ceiling, a cut-off, or a negotiated fee at volume? | A human keys every order in a 7.5-hour staffed day. This is the assumption most likely to break the business model at scale. |
| 5 | Do you send any acknowledgement when an order is **received**, or only when it ships? | Determines whether a "not acknowledged in 24h" alert is possible or whether we are blind until it ships |
| 6 | What is the typical turnaround on an out-of-stock notification? Does the in-stock portion hold while you wait for our reply? | Sets the FTC delay-notice clock and the exception SLA |
| 7 | Can you send a sample tracking email so we can see the format? | Removes the need to guess at parser design |
| 8 | Is a consolidated daily manifest acceptable when no packing list is attached, or is it strictly one order per email? | At 50/day the answer changes the whole outbound design |
| 9 | How is our company name coded on the label, exactly? | Customers ask "who is this from?" — support and FAQ copy need the real string |
| 10 | Domestic packages lost or damaged in transit — what is your remedy? | The sheet disclaims only *international* First Class Mail. Domestic is unaddressed. |
| 11 | Will you countersign a short data-processing / service-provider term? | CCPA service-provider characterisation (Q7) |
| 12 | Do you charge the card at order placement or at ship? Do you itemise the $3.50 and shipping separately on the statement? | Determines whether weekly reconciliation is feasible |
| 13 | Are `-X` styles (e.g. `2987X`) ordered by that exact string, or by base style plus a "queen" flag? | Confirms the Q2 email format matches their order-entry screen |

---

## Proposed Task Breakdown

### Wave 0 — Unblock (no code; can start immediately, all parallel)

| Task | Output | Owner |
|---|---|---|
| 0.1 | 15-minute call with Elegant Moments covering all 13 questions above; write findings into `07-SUPPLIER-ANSWERS.md` | Owner + Claude drafts the script |
| 0.2 | Owner decisions 1–11 captured (run `/gsd:discuss-phase 7`) | Owner |
| 0.3 | Provision `orders@<domain>` mailbox; configure SPF/DKIM; set it as the Shopify sender address | Owner |
| 0.4 | Rotate the store admin password and the app client secret; enable 2FA | Owner |
| 0.5 | Scaffold `pytest` + `tests/conftest.py` with an **anonymised, price-free** SKU fixture | Claude |

### Wave 1 — Margin and policy (parallel; both gated on Wave 0 decisions)

| Task | Output |
|---|---|
| 1.1 | Add `--price-floor` to `build_import.py`; `tests/test_margin.py::test_no_single_item_loss`; regenerate the CSV; document the delta |
| 1.2 | Update Shopify shipping rates if the flat rate changes; update `sections/ticker.liquid:24,28` and the `free_shipping_threshold` settings if the threshold changes |
| 1.3 | Write the Shipping & Returns policy (Shopify Settings → Policies → Refund policy so it is linked from checkout automatically); footer link; short PDP + cart line |
| 1.4 | Produce the one-page branded returns-policy PDF and email it to `dropship@`; record the confirmation |
| 1.5 | Update the privacy policy with supplier disclosure, categories, purpose, and mail-retention window |
| 1.6 | Obtain the written service-provider term from the supplier; file it |

### Wave 2 — Outbound automation (gated on 0.1, 0.3)

| Task | Output |
|---|---|
| 2.1 | `style_from_sku()` reference implementation + `tests/test_order_email.py` covering `2987`, `2987X`, `L1162-M`, `L9859X`, bare numerics, and blank SKU |
| 2.2 | Build the Flow: `Order risk analyzed` → paid + risk≠HIGH + not `em-sent` → `Send internal email` → tag `em-sent` + order note. **Point it at a test address, not `dropship@`.** |
| 2.3 | Verify the rendered email against ≥6 real orders spanning a merged plus-size product, a multi-style order, and a multi-item order |
| 2.4 | Repoint to `dropship@` with `Cc: orders@<domain>`; place one real end-to-end test order; confirm the supplier ships it |

### Wave 3 — Inbound + exceptions (gated on Wave 2 live)

| Task | Output |
|---|---|
| 3.1 | Document the manual tracking procedure (admin → Fulfill items → carrier + number → notify ✓) and time it |
| 3.2 | Define the exception tag vocabulary; create saved admin views for each |
| 3.3 | Write canned supplier replies (ship-available / cancel-all / substitute-request) and canned customer emails (OOS refund, FTC delay notice, substitution consent) |
| 3.4 | Start a `tracking-samples/` folder; save every supplier tracking email verbatim. **Gate for any Stage 2 parser: 20 samples.** |

### Wave 4 — Monitoring (parallel with Wave 3)

| Task | Output |
|---|---|
| 4.1 | Scheduled Flow A — paid, untagged, >24h → alert |
| 4.2 | Scheduled Flow B — `em-sent`, unfulfilled, **>96h** → alert |
| 4.3 | Scheduled Flow C — exception tags >24h → alert (the FTC clock) |
| 4.4 | Document the daily inventory refresh (`liveinventory.csv` → `push_products.py --inventory-only`) as a standing operating procedure |
| 4.5 | Weekly reconciliation checklist: Shopify order count/total ⟷ supplier card charges |

### Wave 5 — Stage 2, deferred (do not build until the trigger fires)

Trigger: **>15 orders/day**, OR a per-order packing slip turns out to be required (supplier
question 3), OR 20 tracking samples collected **and** the supplier confirms they echo our order
number (question 2).

| Task | Output |
|---|---|
| 5.1 | Install Mechanic; configure the custom sender domain |
| 5.2 | Port outbound to a Mechanic task with a PDF packing slip; verify Postmark delivery events |
| 5.3 | Inbound parser on `mechanic/emails/received` — **fail-safe to a human email, never guess** |
| 5.4 | `fulfillmentCreate(notifyCustomer: true)` from the parsed result; verify partial-fulfilment behaviour |
| 5.5 | Postmark bounce webhook → immediate owner alert |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The returns-policy insert is a **one-time** file-on-record, not a per-order attachment | Q6, Supplier Spec | If per-order, Stage 1 Flow cannot deliver it and Mechanic becomes mandatory — an architecture change, not a tweak. **Supplier question 3.** |
| A2 | Flow exposes a usable **risk condition** on the `Order risk analyzed` trigger, with a current field path post-`OrderRiskLevel` deprecation | Q1 | Fraudulent orders ship. Fallback: gate on `financial_status = PAID` only and accept residual risk. **Verify in the Flow editor.** |
| A3 | `li.variant.selectedOptions` is available on the Flow line-item variable | Q2, Code Examples | Must fall back to splitting `variant.title` on `" / "`, which is ambiguous with `O/S` and `Black/Red`. **Verify in the Flow variable picker.** |
| A4 | `orderEditBegin` / `orderEditAddVariant` / `orderEditCommit` are the current substitution mutations in 2026-07 | Q4 | Substitution path is unbuildable as written. **Not verified this session** — planner must confirm. |
| A5 | `RefundLineItemInput` accepts `restockType` / `locationId` | Code Examples | Non-blocking (we deliberately do not restock), but do not assume the fields exist |
| A6 | Mechanic's `attachments` map uses a `{"filename.pdf": {"pdf": "<html>"}}` shape | Code Examples | Stage 2 packing-slip task needs rework. Verify against the file-generator docs before writing it. |
| A7 | CCPA business thresholds are $25M revenue / 100k CA consumers / 50% revenue from selling PI | Q7 | Understating obligations. Low risk — the recommended posture (comply anyway) is correct either way |
| A8 | Sales tax is net-zero to margin, with only a negligible processing-fee effect | Q5 | Margin overstated by ~$0.03 on a $15 order — immaterial |
| A9 | Wholesale ≈ retail ÷ 2.5 as an inverse of the markup pipeline | Q5 | Prices round to `.95`, so the true wholesale differs by up to a few percent per item. Directionally sound; the loss zone conclusion is robust to it |
| A10 | Supplier shipping on a sub-15 oz single item lands at the **low** end of $4–12 | Q5 | If it routinely lands mid-band, the loss zone is wider than modelled. The recommended $14.95 floor is sized for the **worst** case, so the recommendation holds |
| A11 | Shopify Functions cart-validation availability outside Plus | Q5 mitigation #3 | Minimum-order-value may not be natively enforceable. Fallback: vanilla-JS cart-drawer guard (bypassable) or rely on the price floor alone |
| A12 | The store is on the **Advanced** plan (2.5% + 30¢), per `PROJECT.md` | Q5 | On Basic (2.9% + 30¢) every profit figure drops ~$0.06–0.30. Does not change any conclusion. **Confirm the live plan.** |

---

## Open Questions

1. **Does Elegant Moments' tracking email echo our order number?**
   - Known: they email tracking per order when it ships.
   - Unclear: the format, and whether any join key back to our order exists.
   - Recommendation: ask (supplier question 2) **and** collect 20 real samples regardless. Do not
     write a parser before both.

2. **Where do returned goods physically go?**
   - Known: the parcel's return address is the supplier's warehouse under a coded sender name.
   - Unclear: whether the supplier has agreed to receive anything back. The sheet is silent.
   - Recommendation: **blocking**. Do not publish a returns policy until answered (supplier
     question 1).

3. **Can a human at the supplier absorb 50 orders/day?**
   - Known: 7.5 staffed hours, Mon–Fri; every order keyed by hand.
   - Unclear: their actual capacity per account.
   - Recommendation: ask early. If the answer is "not really", the growth plan needs a second
     supplier or a different fulfilment model, and that is a Phase 8 conversation.

4. **Is a Shopify Function cart-validation available outside Plus?**
   - Unclear; not verified this session.
   - Recommendation: verify before planning minimum-order-value. The price floor (mitigation #1)
     achieves most of the same outcome with none of the platform risk.

5. **Does the store still hold the granted scopes after the last app-version release?**
   - Known: scope changes require releasing a new app version **and** re-approving the install; a
     new version alone does not grant them (memory + README).
   - Recommendation: verify `write_merchant_managed_fulfillment_orders` is actually live with a
     read-only probe before Wave 3.

---

## Sources

### Primary (HIGH confidence)

- `data/suppliers/elegant-moments/source/DROPSHIPINFORMATION.pdf` — read in full; the authoritative
  supplier spec
- `data/suppliers/elegant-moments/out/shopify_products.csv` — 1,004 variants; price, weight, SKU,
  and tag distributions computed directly
- `data/suppliers/elegant-moments/README.md`, `build_import.py`, `push_products.py` — pipeline
  behaviour, merge logic, API version pin, dependency footprint
- https://shopify.dev/docs/api/admin-graphql — current version is `2026-07`
- https://shopify.dev/docs/api/admin-graphql/2026-07/mutations/fulfillmentCreate
- https://shopify.dev/docs/api/admin-graphql/2026-07/input-objects/FulfillmentInput
- https://shopify.dev/docs/api/admin-graphql/2026-07/mutations/refundCreate — `@idempotent`
  mandatory as of 2026-04
- https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/build-fulfillment-solutions
- https://shopify.dev/changelog/removing-v2-suffix-from-fulfillmentcreatev2-and-fulfillmenttrackinginfoupdatev2
- https://shopify.dev/changelog/deprecation-of-order-risk-apis-and-introduction-of-risk-assessments-api
- https://shopify.dev/changelog/making-idempotency-mandatory-for-inventory-adjustments-and-refund-mutations
- https://help.shopify.com/en/manual/shopify-flow/getting-started/concepts/variables
- https://help.shopify.com/en/manual/shopify-flow/reference/actions/send-email
- https://help.shopify.com/en/manual/shopify-flow/reference/actions/send-http-request
- https://help.shopify.com/en/manual/shopify-flow/reference/triggers/order-risk-analyzed
- https://help.shopify.com/en/manual/shopify-flow/reference/triggers/scheduled-time
- https://help.shopify.com/en/manual/fulfillment/setup/order-status-page/order-tracking
- https://help.shopify.com/en/manual/payments/shopify-payments/payouts/refunds
- https://www.shopify.com/pricing — Advanced: $399/mo, 2.5% + 30¢ USD online card
- https://learn.mechanic.dev/core/actions/email
- https://learn.mechanic.dev/core/actions/shopify
- https://learn.mechanic.dev/platform/email/receiving-email
- https://apps.shopify.com/mechanic — plan pricing
- https://www.ftc.gov/legal-library/browse/rules/mail-internet-or-telephone-order-merchandise-rule

### Secondary (MEDIUM confidence)

- https://changelog.shopify.com/posts/shopify-flow-now-available-to-basic-plan — Flow on Basic,
  July 2023
- https://shopify.dev/docs/api/admin-graphql/latest/mutations/ordercancel — argument shape via
  search result summary, not a direct fetch
- https://iapp.org/news/a/analyzing-the-cpras-new-contractual-requirements-for-transfers-of-personal-information
- https://california-ccpa.org/cpra/section-7051-contract-requirements-for-service-providers-and-contractors/
- https://www.privacypolicies.com/blog/return-refund-laws-usa/ · https://www.findlaw.com/consumer/consumer-transactions/do-retail-stores-have-to-accept-returns.html
- https://postmarkapp.com/compare/sendgrid-alternative — Postmark 45-day content retention

### Tertiary (LOW confidence — flagged for validation)

- Flow risk-condition field path post-deprecation (A2) — inferred from
  help.shopify.com/manual/fulfillment/managing-orders/protecting-orders/shopify-flow, not confirmed
- `selectedOptions` availability on the Flow line-item variable (A3)
- Mechanic attachment map shape (A6)
- Order-edit mutation names for the substitution path (A4)

---

## Metadata

**Confidence breakdown**

| Area | Level | Reason |
|---|---|---|
| Supplier spec | **HIGH** | Read the source PDF end to end; every claim traced to a sentence |
| Catalogue data (SKU format, prices, weights) | **HIGH** | Computed directly from the built CSV, not inferred |
| Shopify API mutations | **HIGH** | Verified against 2026-07 docs; the V2 rename and the `@idempotent` requirement both confirmed via changelog |
| Shopify Flow capabilities | **HIGH** | Verified against the help centre, including the Advanced-plan gate on `Send HTTP request` |
| Mechanic capabilities | **HIGH** | Verified against `learn.mechanic.dev`; exact attachment map shape is the one gap |
| Margin model | **MEDIUM** | Arithmetic is sound and inputs are verified, but supplier shipping is a $4–12 range that they explicitly cannot pin down before packing. Conclusions are stated across the full band precisely because of this |
| Legal (FTC, CCPA, returns) | **MEDIUM** | Sourced to the FTC directly and to credible secondary legal commentary. **Not legal advice** — the returns and privacy language should get a lawyer's eye before publication |
| Inbound email parsing | **LOW** | Zero samples of the supplier's tracking email exist. This is why the recommendation is to defer rather than build |

**Research date:** 2026-08-21
**Valid until:** ~2026-09-20 for Shopify API specifics (the next quarterly version, `2026-10`, lands
around then). Supplier facts are valid until Elegant Moments revises their drop-ship sheet.
Margin figures are valid until the catalogue is regenerated or Shopify Payments rates change.
