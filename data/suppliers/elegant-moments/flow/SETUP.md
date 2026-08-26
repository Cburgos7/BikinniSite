# Drop-ship order forwarding — setup

Builds the outbound half of Phase 7: a paid, fraud-screened order is emailed to
Elegant Moments automatically, formatted for a human to key into their
order-entry screen.

Shopify Flow workflows can only be built in the admin UI — there is no API for
creating them — so steps 5–10 are yours. Everything that *could* be automated
already has been.

---

## What is already done

| Piece | State |
|---|---|
| `custom.supplier_style` variant metafield | **Created and populated on all 1,522 live variants**, admin access `PUBLIC_READ_WRITE` so Flow can read it |
| Email body template | `supplier-order-email.liquid` in this folder |
| Correctness tests | `render_test.py` — 27 checks, all passing |

### Feasibility, checked against Shopify's own docs

No blockers. Verified 2026-08-24:

| Question | Answer |
|---|---|
| Is Flow available on this store? | **Yes** — free, and available on Basic since Shopify extended it beyond higher tiers |
| Can it email a supplier at another company? | **Yes** — the documented limit is that the address can't be a *variable*; a static external address is fine |
| Can it also copy us? | **Yes** — comma-separate a second recipient. There is no Cc field |
| Can it read our style metafield? | Definition exists with admin `PUBLIC_READ_WRITE`. **Variable path still unverified in Flow** — see step 9 |
| Does the plan limit us? | Only `Send HTTP request` (Grow+). Not used here |

Re-run the backfill after every product import, or new variants arrive with no
style and their order lines will print `DO NOT SHIP`:

```bash
python scripts/backfill-supplier-style.py          # dry run
python scripts/backfill-supplier-style.py --apply
```

---

## The thing that nearly went wrong

The Phase 7 research concluded the supplier style could be derived from the SKU:
`sku | split: "-" | first`. Checked against the STYLE column of the supplier's
own `liveinventory.csv`, **that rule is wrong for 466 of our 1,522 live variants
(31%)**:

| SKU | derived | actual STYLE | |
|---|---|---|---|
| `L1249BL` | `L1249BL` | `L1249` | trailing colour code |
| `L2316P` | `L2316P` | `L2316` | |
| `L2316XP` | `L2316XP` | `L2316X` | the `X` **is** style, the `P` is not |
| `L1237SALE` | `L1237SALE` | `L1237` | |
| `82509` | `82509` | `85209` | the supplier's own transposition |

`L2316P → L2316` but `L2316XP → L2316X`. A trailing letter is sometimes part of
the style and sometimes a colour code, and nothing in the SKU says which.

The product title is no better: **220 of 673 titles name a style number that no
orderable variant actually has.** `"Leather heart pasties — Style L1263"` has
exactly one variant, and it is `L1263PU`.

So the style is carried as data, per variant, from the supplier's own column.
Nothing derives it. If you ever edit the email template, do not reintroduce a
derivation — run `render_test.py` and it will catch you.

---

## Build the workflow

### 1. Install Shopify Flow

Apps → search "Flow" → install. Free. **Confirmed available on this store's
Basic plan.**

> The research assumed an Advanced plan. This store is on **Basic**, which means
> Flow's `Send HTTP request` action is *not* available (Grow and up only). It
> makes no difference to this build — Stage 1 uses `Send internal email`, which
> Basic has — but it does rule out the Stage 1.5 "call our own endpoint" option
> if you ever want it. Upgrading to Grow would restore it.

### 2. Create the workflow

Flow → Create workflow.

### 3. Trigger: **Order risk analyzed**

Not `Order created`. Fraud analysis has not finished when an order is created,
and a fraudulent order that ships costs the refund *plus* goods *plus* the $3.50
drop-ship fee *plus* shipping *plus* the Shopify Payments fee, which is not
returned on a chargeback.

### 4. Conditions — all three must pass

| Condition | Why |
|---|---|
| `Order → Financial status` **is** `Paid` | The $3.50 fee and postage are unrecoverable if payment later fails |
| Risk assessment **is not** `High` | See above |
| `Order → Tags` **does not contain** `em-sent` | Duplicate guard — their PDF warns that duplicates get shipped and billed twice |

> The risk condition's exact field name is unverified. Shopify moved from
> `OrderRiskLevel` to `RiskAssessmentResult` in 2024-04 and the Flow picker's
> current label is not documented. Find it in the condition picker under the
> `Order risk analyzed` trigger. **If you cannot find a risk field at all, do not
> skip this — instead add `Order → Risk level is not High` if offered, or hold
> the launch and ask.** Shipping unscreened orders is the expensive failure.

### 5. Action: **Send internal email**

- **To:** `dropship@elegantmomentslingerie.com, <your own orders mailbox>`
- **Subject:** `Drop-ship order {{ order.name }} — Velvet Tide`
- **Body:** everything in `supplier-order-email.liquid` below the SUBJECT
  comment block. Do not paste the `{%- comment -%}` header; it is documentation.

> **There is no Cc field on this action.** Shopify's reference documents `To`
> only. Use a second comma-separated recipient instead — "to send emails to
> multiple people, separate their email addresses with a comma" — which achieves
> the same thing. Your copy is what you paste tracking numbers from, so do not
> skip it.

> **The recipient must be typed literally, not built from a variable.** Shopify:
> *"You can't use variables to customize the email address to which the message
> is sent."* That restriction does not affect us — the supplier address never
> changes — but it does mean you cannot make the destination conditional later.
>
> Some summaries read that limitation as "internal email is staff-only". It is
> not. The constraint is on *variables*, not on the recipient's domain; a static
> external address is fine.

### 6. Fill in the account number

The body carries `{{ account }}` with a placeholder default, because **this repo
is public on GitHub** and the account number identifies us to Elegant Moments'
billing. Flow workflows are not stored in the repo, so type the number straight
into the action body there.

For manual sends, `render_order.py` reads it from `order_config.json`, which is
gitignored. Copy `order_config.example.json` if you need to recreate it.

### 6b. Set the sender address

Settings → Notifications → **sender email**. This is *not* settable through the
Admin API — `emailSenderConfiguration` does not exist on `Shop` — so it is a
manual change.

Target: `chris.velvettide@premierle.com`. The store is still on
`jcarlson2003@gmail.com` as of 2026-08-24.

**Then authenticate the domain, or the mail goes out looking borrowed.** DNS for
`premierle.com`, checked 2026-08-24:

| Record | Value | Verdict |
|---|---|---|
| MX | `mx00.ionos.com`, `mx01.ionos.com` | Real mailbox, hosted at IONOS |
| SPF | `v=spf1 include:_spf-us.ionos.com ~all` | Exists, but **does not include Shopify** |
| DMARC | `v=DMARC1; p=none;` | Exists — meets Shopify's minimum |

The good news is that this domain **can** be authenticated, which `gmail.com`
never could — you have DNS control at IONOS, since SPF and DMARC are already
set. Add Shopify's CNAME records (Settings → Notifications → authenticate) to
the IONOS DNS zone. Shopify's CNAMEs cover DKIM and SPF together.

Until that is done, Shopify sends on your behalf and the supplier sees the mail
as `via shopifyemail.com`. Replies still reach the sender address either way, so
tracking numbers are not at risk — but unauthenticated mail from a domain that
publishes SPF and DMARC is markedly more likely to be filtered, and **Flow's
email action returns no delivery receipt**. A filtered order is a silent one.

> ⚠️ **The sender address is store-wide, not Flow-only.** It is the From on
> customer order confirmations too. Customers will see `premierle.com` on mail
> from a shop called Velvet Tide — a mismatch worth a decision before launch.
> Related: task #13, the Soleil Noir / Velvet Tide brand split, and task #12,
> the personal Gmail still on the legal pages.

### 7. Action: **Add order tags** → `em-sent`

Must come *after* the email action. This is what the step 4 condition checks.

### 8. Turn the workflow on

### 9. Verify with one real order — do not skip this

`render_test.py` proves the formatting and the style logic. It **cannot** prove
that Flow exposes these two variable paths, because there is no way to test a
Flow workflow offline:

- `li.variant.metafields.custom.supplier_style`
- `li.variant.selectedOptions`

Both are assumptions. The template fails *loudly* rather than silently if either
comes back empty — a missing style prints `** MISSING — DO NOT SHIP THIS LINE **`
— but you want to find that out on a test order, not a customer's.

Place a real order (this doubles as task #5, confirming payments work), let the
workflow fire, and check the Cc copy:

- [ ] Every `STYLE` line shows a style number, none show `MISSING`
- [ ] `COLOR` and `SIZE` are populated and not merged into one field
- [ ] Order at least one plus-size item and check its style ends in `X`
- [ ] Line breaks survived. If the email arrived as one run-on paragraph, Flow
      rendered the body as HTML: wrap the whole body in `<pre>` and resend
- [ ] The order picked up the `em-sent` tag
- [ ] Refund the test order — and **untick restock**. Shopify inventory here is
      a supplier snapshot, not stock we hold; restocking oversells the item

### 10. Add a non-reply alarm

Elegant Moments ships in 24–48h **Monday to Friday**. A Friday evening order has
no reply until Tuesday, and Flow's `Send internal email` returns no delivery
receipt — a dropped order email is silent, and a paid order can sit unshipped
for days.

Second workflow: `Scheduled time` (daily) → `Get order data` → for orders tagged
`em-sent`, unfulfilled, and older than 72 hours → send yourself an email.

---

## What this does not cover

**Tracking back to the customer is manual.** Elegant Moments emails a tracking
number to the Cc mailbox; you paste it into the order's fulfilment dialog in
Shopify admin. Roughly 45 seconds per order. Do not build a parser until you have
20+ real tracking emails to write one against — the format is undocumented and
nobody has seen it yet.

When you do fulfil, Shopify's own notification handles the customer email —
just make sure **notify customer** stays ticked. It defaults to off in the API
and that failure is silent.

**Returns are still unresolved (task #8).** Parcels carry Elegant Moments'
warehouse as the return address, so a "return to sender" ships your goods to a
company with no agreement to credit you. That is a commercial conversation, not
an engineering one, and it blocks the refund policy.

**Out-of-stock handling is manual.** They email and wait for your reply. The
email above tells them to hold the whole order rather than part-ship, because
part-shipping means paying the $3.50 fee twice. The FTC Mail Order Rule gives you
30 days to ship or you must offer a refund — so do not let an out-of-stock reply
sit.
