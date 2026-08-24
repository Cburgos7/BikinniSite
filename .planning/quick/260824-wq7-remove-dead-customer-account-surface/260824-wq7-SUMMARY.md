---
id: 260824-wq7
status: complete
date: 2026-08-24
commits: pending
---

# Quick Task 260824-wq7 — Summary

Removed the customer-account surface from the theme. The owner's model is guest
checkout: orders arrive, they are forwarded to Elegant Moments for fulfilment,
and an affiliate is paid when a referral link was used. Nothing in that model
needs a shopper to hold an account, and everything account-shaped in the theme
was already dead.

## What was actually broken

**Accounts were never reachable.** The store runs Shopify's *new* customer
accounts. `/account`, `/account/login`, `/account/register`, `/account/orders`
and `/account/addresses` all return 406 to a direct fetch and redirect a browser
to `shopify.com/101516378406/account`. Shopify intercepts before the theme
renders, so the five templates in `templates/customers/` — 265 lines built in
Phase 2 — could not be reached by any customer under any circumstances.

**The wishlist heart did nothing at all.** `snippets/product-card.liquid`
rendered a heart on every one of the 663 published products, gated on
`customer != blank`:

- signed in → a `<button data-wishlist-toggle>`. Grep across every `.js` and
  `.liquid` file in the repo returned that one markup occurrence and nothing
  else. No listener, no storage, no metafield, no app. The button was inert.
- signed out → a link to `/account/login`, which is the hosted login above.
  A shopper who signed in landed back on the same inert button.

So the control was a dead end down both branches, on the whole catalogue.

## Changes

| File | Change |
|---|---|
| `templates/customers/*.liquid` | Deleted — 5 files, 265 unreachable lines |
| `snippets/product-card.liquid` | Wishlist block removed; comment explains why and points at localStorage if it is ever wanted |
| `sections/header.liquid` | Account icon removed from the right-hand icon row |
| `tailwind.config.js` | Dropped the now-redundant `templates/customers/**` glob (`templates/**` already covers it) |
| `assets/theme.css` | Rebuilt |

## Verification

`npm run build` — 38,875 → 38,792 bytes. The diff is six lines, all deletions:
`.text-right` and `.capitalize`, both of which were used only by the deleted
account templates. Nothing else was dropped and nothing was orphaned, which is
the specific failure this repo has hit before (see the stale-`theme.css` note in
project memory).

Post-change grep for `wishlist`, `/account` and `customers/` across all
`.liquid`, `.js` and `.json` returns only the explanatory comments.

## Order tracking still works

Removing the account icon does not strand anyone. Shopify puts an order-status
link in every order confirmation email, and that link needs no login. Customers
track parcels through the email, which is the normal path for a guest-checkout
store anyway.

## Owner follow-up

Customer-account settings are not writable through the Admin API, so one manual
step remains: **Settings → Customer accounts → don't use accounts** (or leave
them on — the theme is now correct either way, which it was not before).
