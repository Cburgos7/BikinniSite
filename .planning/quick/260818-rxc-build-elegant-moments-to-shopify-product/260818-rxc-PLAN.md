---
id: 260818-rxc
slug: build-elegant-moments-to-shopify-product
description: Build Elegant Moments to Shopify product import pipeline
date: 2026-08-19
mode: quick
---

# Quick Task 260818-rxc: Elegant Moments → Shopify import pipeline

## Goal

Turn the Elegant Moments B2B wholesale exports into a Shopify-importable product
CSV for velvet-tide-2.myshopify.com, as a re-runnable script (inventory refreshes
weekly).

## Source data

| File | Rows | Notes |
|---|---|---|
| `liveinventory.csv` | 2,572 (1,237 styles) | Live stock + wholesale price. `DESCRIPTION` truncated to 30 chars — unusable as copy. |
| `2026_Collection_Descriptions.xlsx` | 1,179 (460 styles) | Real copy, fabric, origin, weight, categories, image filenames. Sheets: Lingerie, Leather, Vinyl, Costumes, Hosiery Items. |
| `2026_Collection_Price_List.xlsx` | — | Redundant; prices already reconcile with inventory (436/448 exact). Kept for reference only. |
| `DROPSHIPINFORMATION.pdf` | — | $3.50/order fee, blind label, 24–48hr, manual email ordering. Reference only. |

Join key: `STYLE` (inventory) ↔ `Style` (descriptions). 448/460 description styles
match inventory.

## Decisions (locked)

- **Retail price** = wholesale × 2.5, rounded to nearest `.95`
- **Shipping** = free over $75, else $7.95 (configured in Shopify, not this CSV)
- **Filter** = `DISCONTINUED=No AND QTY_AVAILABLE>0`
- **Attribution** = "Brand: Elegant Moments" required in body HTML by supplier license
- **Images** = deferred; `Image Src` emitted only when a base URL is supplied via
  `--image-base`, pending the Catalog Images download-links manifest
- **Supplier data is NOT committed** — repo is public, license forbids redistribution

## Tasks

### Task 1 — gitignore supplier source data
- **files:** `.gitignore`
- **action:** Ignore `data/suppliers/*/source/` and `data/suppliers/*/out/`. Repo is
  public (github.com/Cburgos7/BikinniSite); the supplier licence forbids
  redistribution, and the wholesale price list is our cost basis.
- **verify:** `git check-ignore data/suppliers/elegant-moments/source/liveinventory.csv`
- **done:** Source files present on disk, invisible to git.

### Task 2 — build the transform script
- **files:** `data/suppliers/elegant-moments/build_import.py`
- **action:** Join inventory + descriptions on STYLE, filter to sellable, group
  variants by style, emit Shopify product import CSV.
  - `STYLE` → handle (slugified, prefixed `em-`)
  - Title cased from description text, style appended for uniqueness
  - Option1 = Color, Option2 = Size (omit Option2 when a style is one-size only)
  - `SKU` → Variant SKU, `UPC` → Variant Barcode
  - `QTY_AVAILABLE` → Variant Inventory Qty, tracked by shopify, policy deny
  - `Weight (oz)` → grams
  - `Category 1` → Product Type; Categories 1–3 + sheet name → Tags
  - Body HTML = description + fabric + origin + attribution line
  - Retail = wholesale × 2.5 → `.95`
  - Size ordering normalised (XS…5X, O/S, Q/S) rather than alphabetical
- **verify:** Run against source; assert row count, no null handles, all prices
  end in `.95`, variant option counts consistent per handle.
- **done:** `out/shopify_products.csv` generated and importable.

### Task 3 — document the refresh procedure
- **files:** `data/suppliers/elegant-moments/README.md`
- **action:** Document source files, licence constraints, the drop-ship ordering
  reality (manual email, no API), the sizing gap (no XXS/XS in stock), pricing
  rule, and how to re-run when inventory updates.
- **verify:** README covers re-run steps and the images blocker.
- **done:** A person who isn't the author can refresh the catalog from it.

## must_haves

- **truths:** Only sellable stock is published; retail = 2.5× wholesale at `.95`;
  supplier data never enters git history.
- **artifacts:** `build_import.py`, `README.md`, generated `out/shopify_products.csv`.
- **key_links:** `.gitignore`, `data/suppliers/elegant-moments/`.

## Out of scope

- Pushing products to Shopify via Admin API (needs images first)
- Image hosting / Cloudinary
- Holiday, Hosiery, Vivace description files (Q4 + category expansion)
