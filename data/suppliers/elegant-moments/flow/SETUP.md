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
| `custom.supplier_style` variant metafield | **Created and populated on all 1,522 live variants** |
| Email body template | `supplier-order-email.liquid` in this folder |
| Correctness tests | `render_test.py` — 27 checks, all passing |

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

- **To:** `dropship@elegantmomentslingerie.com`
- **Cc:** your own orders mailbox — see step 6
- **Subject:** `Drop-ship order {{ order.name }} — Velvet Tide`
- **Body:** everything in `supplier-order-email.liquid` below the SUBJECT
  comment block. Do not paste the `{%- comment -%}` header; it is documentation.

### 6. Fill in the two placeholders

- **Dropship account number** — replace `«ACCOUNT NUMBER — see SETUP.md step 6»`
  in the body with your Elegant Moments account number.
- **Cc address** — put a mailbox you control here. It costs nothing, gives you a
  per-order copy, and is where Elegant Moments' replies land when they hit
  Reply. Their tracking numbers and out-of-stock notices both arrive this way.

> Blocked on task #12 — the legal pages still carry a personal Gmail. Settle the
> business address once and use it here too.

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
