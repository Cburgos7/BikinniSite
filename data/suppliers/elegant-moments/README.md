# Elegant Moments → Shopify import

Turns the Elegant Moments B2B wholesale exports into a Shopify product import CSV
for `velvet-tide-2.myshopify.com`.

## ⚠ Supplier data is not committed

`source/` and `out/` are gitignored. **This repo is public**, and the Elegant
Moments licence (the `Information` sheet of the descriptions workbook) states the
data is *"for your sole use as an Elegant Moments wholesale customer. Do not
distribute or redistribute this information without prior written consent."*
The price lists are also our cost basis. Never commit them.

The licence also requires their name to appear in advertising content, which is
why every product body carries a `Brand: Elegant Moments` line and `Vendor` is set
to `Elegant Moments`. Do not strip these. Images may not be distorted or
recropped in a way that changes model proportions.

## Source files

Download from `b2b.elegantmoments.com` → My account → Downloads, into `source/`:

| File | What it gives us |
|---|---|
| `liveinventory.csv` | Live stock and wholesale cost. **Required.** Its `DESCRIPTION` column is truncated to 30 chars and unusable as copy. |
| `2026_Collection_Descriptions.xlsx` | Real product copy, fabric, country of origin, weight, categories, image filenames. **Required.** |
| `2026_Collection_Price_List.xlsx` | Reference only — prices already reconcile with the inventory feed (436/448 styles matched exactly). |
| `DROPSHIPINFORMATION.pdf` | Reference only. |

The two files join on `STYLE` ↔ `Style`.

## Running it

```bash
python -m pip install openpyxl
python build_import.py
```

Options:

| Flag | Default | Notes |
|---|---|---|
| `--markup` | `2.5` | Retail = wholesale × markup, rounded to nearest `.95`. |
| `--image-base` | *(empty)* | Base URL for product images. While empty, `Image Src` is left blank. |
| `--status` | `draft` | Products import unpublished so you can review before they go live. |
| `--out` | `out/shopify_products.csv` | Output path. |

Import via Shopify admin → Products → Import.

## Current output

330 products / 1,004 variants, from 1,539 sellable inventory rows.

Filtered out: discontinued styles (875 rows) and zero-stock rows (251). The 420
sellable styles with no matching copy are skipped — they need the **Holiday**,
**Hosiery**, and **Vivace** description workbooks, which follow the same format
and can be added to `DESC_SHEETS` handling.

### Merged plus sizes

Elegant Moments splits sizing across two styles — `11022` (S–XL) and `11022X`
(1X–4X). Left alone that lists the same garment twice and sends plus shoppers to a
separate page. The builder folds each `X` style into its parent, so one product
carries the full S–4X range.

66 of 67 pairs merged, taking 396 products down to 330. Variant count is unchanged
at 1,004 — nothing is dropped. Supplier SKUs stay distinct per size (`11022-L`,
`11022X-1X`) so drop-ship order entry still identifies the right style, and both
styles are tagged (`em-style-11022`, `em-style-11022X`) plus an `Extended Sizing`
tag for collection filtering. Plus sizes keep their own price, since they cost
about $1 more wholesale.

The one pair left unmerged, `L9859`/`L9859X`, both stock `Q/S` — merging would
create a duplicate Color+Size pair, which Shopify rejects. The builder detects any
such size overlap and skips the merge rather than producing an invalid product.

Pass `--no-merge-plus` to keep the supplier's split structure.

## Images

The *Catalog Images – Download Links* PDF only links four collection ZIPs — there
are **no per-image URLs**, so the Shopify CSV importer (which fetches `Image Src`
over HTTP) cannot be used for images. We upload the bytes ourselves instead.

Extract `em2026collection.zip`, then:

```bash
python prepare_images.py --src /path/to/extracted/Items
```

The supplier ships ~1200×1800 JPEGs at very low compression (448 MB for the 784
images this catalog references). Re-encoding at quality 82 keeps identical pixel
dimensions and cuts that to 81 MB. Dimensions are never altered — the licence
forbids modifying images in a way that distorts proportions. Shopify re-encodes
and serves responsive derivatives from its CDN regardless.

Coverage: 383 of 396 products have images, averaging 2.1 each (front and back).
One referenced file, `l1127_b.jpg`, is absent from the supplier ZIP; that product
still gets its front shot.

## Pushing to Shopify

Create a `.env` beside the scripts (gitignored — never commit it):

```
SHOPIFY_CLIENT_ID=...
SHOPIFY_CLIENT_SECRET=...
```

Both come from **dev.shopify.com → Apps → Velvet tide → Client credentials**. The
store admin's Apps page shows permissions but never reveals credentials.

```bash
python push_products.py --dry-run          # inspect a payload, no API calls
python push_products.py --limit 1          # smoke-test one product end to end
python push_products.py                    # full run
python push_products.py --inventory-only   # backfill stock on existing products
```

Creates each product through the GraphQL Admin API as **draft**, then stages and
attaches its images. Re-running skips products whose handle already exists, so an
interrupted run can simply be restarted. Nothing is published by the script.

### Required scopes

| Scope | Needed for |
|---|---|
| `write_products` | creating products and variants |
| `write_files` | uploading images (already granted) |
| `read_locations`, `write_inventory` | setting stock levels |

Without location access the push still runs, but every variant lands at zero
stock; `--inventory-only` backfills once the scope is added. Scope changes need a
new app version released **and** the install re-approved in the store admin — a
new version alone does not grant them.

## Known gaps

**1. Size range is S–4X, not XXS–3XL.** There is no XXS or XS anywhere in the
inventory feed. Note `O/S` fits roughly dress 2–12 and `Q/S` roughly 14–18 per the
supplier size chart. Brand copy promising XXS is not supportable on this supplier.

**2. Fulfilment is manual.** Per the drop-ship sheet there is no API — orders go by
email to `dropship@elegantmomentslingerie.com`, one order per email, with a $3.50
per-order fee (not per item) and blind packaging. Someone re-keys every order.

## Refreshing

Inventory moves constantly and 498 rows currently hold fewer than 10 units. Re-run
the script against a fresh `liveinventory.csv` and re-import to update stock levels
and drop sold-out styles. The descriptions workbook only changes when a new
collection drops.
