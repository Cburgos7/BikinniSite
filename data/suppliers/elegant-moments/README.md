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
| `liveinventory.csv` | Live stock and wholesale cost for **every** catalogue. **Required.** Its `DESCRIPTION` column is truncated to 30 chars and unusable as copy. |
| `2026_Collection_Descriptions.xlsx` | Real product copy, fabric, country of origin, weight, categories, image filenames. |
| `2026-2027_Vivace_Descriptions.xlsx` | Same, for the Vivace catalogue (incl. swimwear). |
| `2026_Holiday_Descriptions.xlsx` | Same, for the Holiday catalogue. |
| `2025-2026_Hosiery_Descriptions.xls` | Same, for hosiery. Legacy binary `.xls` — needs `xlrd`. |
| `*_Price_List.xlsx` | Reference only — prices reconcile with the inventory feed (2026: 436/448 exact; Vivace: 169/172 exact). The inventory feed is the cost basis, since it is the one that moves. |
| `DROPSHIPINFORMATION.pdf` | Reference only. |

Descriptions join to inventory on `STYLE` ↔ `Style`.

## Catalogues

Each supplier release is a **catalogue**: the same layout with different sheet
names, a `Size`/`Sizes` spelling difference, a different number of `Image N`
columns, and a different plus-size style suffix. They are described by the
`CATALOGUES` table at the top of `build_import.py` — adding one is a config
entry, not a new code path.

| Catalogue | Workbook | Sheets | Image cols | Plus suffix | Output |
|---|---|---|---|---|---|
| `2026` (default) | `2026_Collection_Descriptions.xlsx` | Lingerie, Leather, Vinyl, Costumes, Hosiery Items | 1–4 | `X` (11022 / 11022X) | `out/` |
| `vivace` | `2026-2027_Vivace_Descriptions.xlsx` | Swimwear, Vivace, Panties, Menswear | 1–8 | `Q` (8590 / 8590Q) | `out/vivace/` |
| `holiday` | `2026_Holiday_Descriptions.xlsx` | 2026 Holiday | 1–4 | `Q`, `X` | `out/holiday/` |
| `hosiery` | `2025-2026_Hosiery_Descriptions.xls` | 2025-2026 Hosiery | 1–3 | `Q`, `X` | `out/hosiery/` |

Workbooks overlap — 14 of Holiday's sellable styles are already carried by the
2026 and Vivace releases. Each catalogue's `follows` list names the ones imported
before it, and those styles are left to whichever catalogue shipped them first,
so nothing collides on the `em-<style>` product handle.

## Running it

```bash
python -m pip install openpyxl xlrd     # xlrd only for the legacy .xls
python build_import.py                  # the 2026 collection
python build_import.py --catalogue vivace
```

Options:

| Flag | Default | Notes |
|---|---|---|
| `--catalogue` | `2026` | Which workbook to build. |
| `--markup` | `2.5` | Retail = wholesale × markup, rounded to nearest `.95`. |
| `--image-base` | *(empty)* | Base URL for product images. While empty, `Image Src` is left blank. |
| `--status` | `draft` | Products import unpublished so you can review before they go live. |
| `--out` | *(catalogue's out dir)* | Output path. |
| `--no-follows` | off | Do not skip styles owned by an earlier catalogue. |

## Current output

| Catalogue | Products | Variants | Units | Notes |
|---|---|---|---|---|
| `2026` | 330 | 1,004 | | live |
| `vivace` | 154 | 215 | 80,404 | 38 of them swimwear |
| `holiday` | 9 | 28 | | no images shipped yet |
| `hosiery` | 180 | 275 | | no images shipped yet |

From 1,539 sellable inventory rows; discontinued styles (875 rows) and zero-stock
rows (251) are filtered out. With all four catalogues loaded, only **14** sellable
styles still have no matching copy.

### Merged plus sizes

Elegant Moments splits sizing across two styles — `11022` (S–XL) and `11022X`
(1X–4X). Left alone that lists the same garment twice and sends plus shoppers to a
separate page. The builder folds each plus style into its parent, so one product
carries the full range. The suffix differs by catalogue: the 2026 collection uses
`X`, while Vivace and Holiday use `Q` for Queen (`8590` = O/S, `8590Q` = Q/S).

66 of 67 pairs merged in the 2026 catalogue, taking 396 products down to 330;
13 pairs in Vivace; 4 in Holiday; 46 in hosiery. Variant count is unchanged —
nothing is dropped. Supplier SKUs stay distinct per size (`11022-L`,
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

Extract the collection ZIP, then:

```bash
python prepare_images.py --src /path/to/extracted/Items
python prepare_images.py --catalogue vivace --src /path/to/vivace/Items
```

The supplier ships ~1200×1800 JPEGs at very low compression. Re-encoding at
quality 82 keeps identical pixel dimensions and cuts the payload ~5×. Dimensions
are never altered — the licence forbids modifying images in a way that distorts
proportions. Shopify re-encodes and serves responsive derivatives from its CDN
regardless.

The source tree is searched **recursively**. The 2026 ZIP was flat; the Vivace
ZIP splits its files across `1200pxw/` and `Editorials/` while the workbook still
references bare filenames.

| Catalogue | Referenced | Present | Converted |
|---|---|---|---|
| `2026` | 784 | 783 | 448 MB → 81 MB. `l1127_b.jpg` absent from the ZIP. |
| `vivace` | 492 | 491 | 343 MB → 57 MB. `8005_b.jpg` absent; that product keeps its front shot. |
| `holiday` | 85 | 57 | those 57 belong to styles already live from the 2026 collection; the Holiday image ZIP has not been downloaded. |
| `hosiery` | 597 | 12 | the hosiery image ZIP has not been downloaded. |

Vivace swim styles carry editorial/lifestyle shots as well as front and back,
which is why that layout runs to `Image 8`. Front (`_f`) shots stay in position 1
regardless.

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
python push_products.py --publish          # set ACTIVE + publish to Online Store

# a non-default catalogue:
python push_products.py --out-dir out/vivace --limit 1
```

`--out-dir` points at a catalogue's build directory (`shopify_products.csv`,
`image_manifest.json`, `images/`); it defaults to `out/`, the 2026 collection.

Creates each product through the GraphQL Admin API as **draft**, then stages and
attaches its images. Re-running skips products whose handle already exists, so an
interrupted run can simply be restarted.

`--publish` is a separate pass. It leaves any product with no image as a draft —
an empty card on a collection grid looks broken, and those products have no photo
only because the supplier has not shipped one yet. `--publish-without-images`
overrides that.

## Collections

```bash
python sync_collections.py --dry-run
python sync_collections.py
```

Products land tagged by supplier category; the theme's navigation points at
specific collection handles. `COLLECTION_TAGS` maps tags → collection, with an
`exclude` list (Vivace ships men's thongs and briefs, which match the garment
tags but do not belong in a women's lingerie collection).

`RENAMED_FROM` handles storefront renames: `swimwear` was originally built as
`bikinis`, so the existing collection is renamed in place — handle and title —
with `redirectNewHandle` set, rather than leaving an empty duplicate behind.
Missing collections are created.

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

**1a. Swimwear is effectively One Size.** 37 of the 38 sellable Vivace swim
styles stock only `O/S` (≈ dress 2–12); the 38th (`11025`) is S/M + L/XL. There
is **no Q/S, 1X–4X or any plus swim** in the feed at all. The storefront's
inclusive S–4X positioning holds for lingerie but not for swim, and the swim PDPs
will show a single size option. Either a second swim supplier or softened
category copy is needed.

**2. Fulfilment is manual.** Per the drop-ship sheet there is no API — orders go by
email to `dropship@elegantmomentslingerie.com`, one order per email, with a $3.50
per-order fee (not per item) and blind packaging. Someone re-keys every order.

## Refreshing

Inventory moves constantly and 498 rows currently hold fewer than 10 units. Re-run
the script against a fresh `liveinventory.csv` and re-import to update stock levels
and drop sold-out styles. The descriptions workbook only changes when a new
collection drops.
