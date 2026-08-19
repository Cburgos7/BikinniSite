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

396 products / 1,004 variants, from 1,539 sellable inventory rows.

Filtered out: discontinued styles (875 rows) and zero-stock rows (251). The 420
sellable styles with no matching copy are skipped — they need the **Holiday**,
**Hosiery**, and **Vivace** description workbooks, which follow the same format
and can be added to `DESC_SHEETS` handling.

## Known gaps

**1. No images.** The workbook's image columns hold bare filenames
(`44224_f.jpg`), not URLs. The **Catalog Images – Download Links** file from the
portal's Product Images section has the actual URLs. Until it's supplied, products
import without photos — do not publish them in that state. Once available, host
the images (Cloudinary is already in the theme's integration config) and re-run
with `--image-base`.

**2. Regular and plus sizes are separate products.** Elegant Moments splits them
into two styles — `11022` (S–XL) and `11022X` (1X–4X) — and the importer follows
that structure. 67 of the 396 products are a plus twin of another product, so a
shopper sees the same robe listed twice. That reads badly against inclusive-sizing
positioning. Merging each `X` style into its parent as additional size variants is
the fix; it is deliberately **not** done automatically because it rewrites product
structure and the two styles carry different wholesale costs (typically $1 apart).

**3. Size range is S–4X, not XXS–3XL.** There is no XXS or XS anywhere in the
inventory feed. Note `O/S` fits roughly dress 2–12 and `Q/S` roughly 14–18 per the
supplier size chart. Brand copy promising XXS is not supportable on this supplier.

**4. Fulfilment is manual.** Per the drop-ship sheet there is no API — orders go by
email to `dropship@elegantmomentslingerie.com`, one order per email, with a $3.50
per-order fee (not per item) and blind packaging. Someone re-keys every order.

## Refreshing

Inventory moves constantly and 498 rows currently hold fewer than 10 units. Re-run
the script against a fresh `liveinventory.csv` and re-import to update stock levels
and drop sold-out styles. The descriptions workbook only changes when a new
collection drops.
