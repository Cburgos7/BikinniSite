#!/usr/bin/env python3
"""Build a Shopify product import CSV from Elegant Moments wholesale exports.

Joins the live inventory feed (stock + wholesale cost) against the collection
descriptions workbook (copy, fabric, categories, image filenames) on STYLE, keeps
only sellable stock, and emits Shopify's product import format.

Usage:
    python build_import.py
    python build_import.py --markup 2.5 --image-base https://cdn.example.com/em/

Requires: openpyxl
"""

import argparse
import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl is required: python -m pip install openpyxl")

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
OUT = HERE / "out"

INVENTORY = SOURCE / "liveinventory.csv"
DESCRIPTIONS = SOURCE / "2026_Collection_Descriptions.xlsx"

# Sheets holding product rows. "Information" is the licence/terms sheet — skipped.
DESC_SHEETS = ["Lingerie", "Leather", "Vinyl", "Costumes", "Hosiery Items"]

# The supplier licence requires their name to appear in advertising content.
ATTRIBUTION = "Elegant Moments"

# Shopify sorts variant options in the order it first sees them, so emit sizes in
# wearable order rather than the alphabetical order the source happens to use.
SIZE_ORDER = [
    "XS", "S", "S/M", "M", "M/L", "L", "L/XL", "XL",
    "1X", "1X/2X", "2X", "3X", "3X/4X", "4X", "5X",
    "O/S", "OS", "Q/S", "Q'S",
]
SIZE_RANK = {s: i for i, s in enumerate(SIZE_ORDER)}

# Numeric sizes (bra bands: 32, 34, ...) sort after named sizes, numerically.
NUMERIC_SIZE_BASE = len(SIZE_ORDER)

SHOPIFY_COLUMNS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
    "Variant SKU", "Variant Grams", "Variant Inventory Tracker",
    "Variant Inventory Qty", "Variant Inventory Policy",
    "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
    "Variant Requires Shipping", "Variant Taxable", "Variant Barcode",
    "Image Src", "Image Position", "Image Alt Text", "Status",
]


def size_sort_key(size):
    s = (size or "").strip().upper()
    if s in SIZE_RANK:
        return (SIZE_RANK[s], 0)
    if s.isdigit():
        return (NUMERIC_SIZE_BASE, int(s))
    return (NUMERIC_SIZE_BASE + 1, 0)


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return slug or "item"


def titleize(text, style):
    """Build a product title from the description's leading clause.

    Descriptions read as sentences ("Eyelash lace and satin babydoll with
    underwire cups, adjustable straps and hook"). The clause before the first
    comma / "with" is the product name; the rest is detail.
    """
    text = (text or "").strip()
    if not text:
        return f"Style {style}"
    # Costume rows use "Name - description"; keep the name.
    if " - " in text[:60]:
        head = text.split(" - ", 1)[0]
    else:
        head = re.split(r",| with | w/ ", text, maxsplit=1)[0]
    head = head.strip(" .")
    words = head.split()
    if len(words) > 10:
        head = " ".join(words[:10])
    return head[:1].upper() + head[1:] if head else f"Style {style}"


def retail_price(wholesale, markup):
    """wholesale x markup, rounded to the nearest .95 price point (never below .95)."""
    target = wholesale * markup
    whole = int(target)
    # Candidates bracketing the target: X-1.95, X.95, X+0.95
    candidates = [whole - 1 + 0.95, whole + 0.95, whole + 1.95]
    candidates = [c for c in candidates if c >= 0.95]
    return min(candidates, key=lambda c: abs(c - target))


def read_inventory():
    with INVENTORY.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    sellable = []
    for r in rows:
        if (r.get("DISCONTINUED") or "").strip().lower() == "yes":
            continue
        try:
            qty = int(r.get("QTY_AVAILABLE") or 0)
        except ValueError:
            qty = 0
        if qty <= 0:
            continue
        r["_qty"] = qty
        try:
            r["_wholesale"] = float(r.get("WHOLESALE_PRICE") or 0)
        except ValueError:
            r["_wholesale"] = 0.0
        sellable.append(r)
    return rows, sellable


def read_descriptions():
    """Return {style: metadata} and {(style, color, size): row}.

    Metadata is style-level (copy, fabric, categories). Colour/size level rows
    carry the image filenames, which vary by colourway.
    """
    wb = openpyxl.load_workbook(DESCRIPTIONS, read_only=True, data_only=True)
    by_style = {}
    by_variant = {}
    for sheet in DESC_SHEETS:
        if sheet not in wb.sheetnames:
            continue
        ws = wb[sheet]
        it = ws.iter_rows(values_only=True)
        header = [str(h).strip() if h is not None else "" for h in next(it)]
        for raw in it:
            row = dict(zip(header, raw))
            style = row.get("Style")
            if style is None or str(style).strip() == "":
                continue
            style = str(style).strip()
            row["_sheet"] = sheet
            by_style.setdefault(style, row)
            color = str(row.get("Color") or "").strip().upper()
            size = str(row.get("Sizes") or "").strip().upper()
            if size == "ONE SIZE":
                size = "O/S"
            by_variant[(style, color, size)] = row
    return by_style, by_variant


def clean(value):
    return str(value).strip() if value is not None else ""


def build_body_html(meta):
    desc = clean(meta.get("Description"))
    fabric = clean(meta.get("Fabric/Material"))
    origin = clean(meta.get("Country Of Origin"))
    shown_with = clean(meta.get("Shown With"))

    parts = []
    if desc:
        parts.append(f"<p>{desc.rstrip('. ')}.</p>")
    details = []
    if fabric:
        details.append(f"<li><strong>Fabric:</strong> {fabric}</li>")
    if origin:
        details.append(f"<li><strong>Made in:</strong> {origin}</li>")
    # Required by the Elegant Moments wholesale image/content licence.
    details.append(f"<li><strong>Brand:</strong> {ATTRIBUTION}</li>")
    parts.append("<ul>" + "".join(details) + "</ul>")
    if shown_with:
        parts.append(f"<p><em>{shown_with}</em></p>")
    return "".join(parts)


def build_tags(meta, styles):
    tags = []
    for key in ("Category 1", "Category 2", "Category 3"):
        val = clean(meta.get(key))
        if val:
            tags.append(val.rstrip(". "))
    sheet = meta.get("_sheet")
    if sheet:
        tags.append("Hosiery" if sheet == "Hosiery Items" else sheet)
    # One tag per contributing supplier style, so a merged product still traces
    # back to both styles when placing a drop-ship order.
    for style in styles:
        tags.append(f"em-style-{style}")
    if len(styles) > 1:
        tags.append("Extended Sizing")
    seen, out = set(), []
    for t in tags:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return ", ".join(out)


def image_view_rank(name):
    """Front shots first, then back, then anything else.

    The workbook's "Image 1" column is usually the front view but not always —
    for a handful of styles it holds the back shot, which would otherwise become
    the featured image on collection tiles. Filenames follow a reliable
    `<style>_f` / `<style>_b` convention, so order on that instead.
    """
    lowered = name.lower()
    if "_f" in lowered:
        return 0
    if "_b" in lowered:
        return 1
    return 2


def image_names(row):
    names = []
    for key in ("Image 1", "Image 2", "Image 3", "Image 4"):
        val = clean(row.get(key))
        if val:
            names.append(val)
    # Stable sort keeps the supplier's ordering within each view type.
    return sorted(names, key=image_view_rank)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--markup", type=float, default=2.5,
                    help="retail multiplier on wholesale cost (default 2.5)")
    ap.add_argument("--image-base", default="",
                    help="base URL for product images; when empty, Image Src is "
                         "left blank pending the catalog image manifest")
    ap.add_argument("--out", default=str(OUT / "shopify_products.csv"))
    ap.add_argument("--status", default="draft", choices=["draft", "active"],
                    help="Shopify product status (default draft — review before "
                         "publishing)")
    ap.add_argument("--no-merge-plus", dest="merge_plus", action="store_false",
                    help="keep the supplier's split regular/plus styles as "
                         "separate products instead of merging them")
    args = ap.parse_args()

    for path in (INVENTORY, DESCRIPTIONS):
        if not path.exists():
            sys.exit(f"Missing source file: {path}\n"
                     f"Download it from b2b.elegantmoments.com and place it in {SOURCE}")

    all_rows, sellable = read_inventory()
    by_style, by_variant = read_descriptions()

    # Group sellable inventory by style, keeping only styles we have copy for.
    styles = OrderedDict()
    skipped_no_copy = set()
    for r in sellable:
        style = clean(r.get("STYLE"))
        if style not in by_style:
            skipped_no_copy.add(style)
            continue
        styles.setdefault(style, []).append(r)

    # Elegant Moments splits sizing across two styles — 11022 (S–XL) and 11022X
    # (1X–4X) — which would otherwise list the same garment twice. Fold each plus
    # style into its parent as extra size variants. SKUs stay distinct, so
    # drop-ship order entry still identifies the correct supplier style.
    merged_styles = {}  # plus style -> parent style
    if args.merge_plus:
        for style in list(styles):
            if not style.upper().endswith("X"):
                continue
            parent = style[:-1]
            if parent not in styles:
                continue
            plus_sizes = {clean(r.get("SIZE")).upper() for r in styles[style]}
            parent_sizes = {clean(r.get("SIZE")).upper() for r in styles[parent]}
            if plus_sizes & parent_sizes:
                # Overlapping sizes would collide as duplicate option pairs.
                continue
            styles[parent].extend(styles.pop(style))
            merged_styles[style] = parent

    image_base = args.image_base.rstrip("/") + "/" if args.image_base else ""
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    variant_count = 0
    # handle -> [image filename, ...]; consumed by push_products.py, which uploads
    # the bytes directly rather than relying on a public URL (we have none).
    manifest = OrderedDict()
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=SHOPIFY_COLUMNS)
        writer.writeheader()

        for style, rows in styles.items():
            meta = by_style[style]
            handle = f"em-{slugify(style)}"
            title = titleize(meta.get("Description"), style)

            colors = sorted({clean(r.get("COLOR")).upper() for r in rows})
            sizes = {clean(r.get("SIZE")).upper() for r in rows}
            multi_size = not (len(sizes) == 1 and next(iter(sizes)) in ("O/S", "OS"))

            rows.sort(key=lambda r: (clean(r.get("COLOR")).upper(),
                                     size_sort_key(clean(r.get("SIZE")))))

            # Contributing styles: the product's own, plus any merged plus twin.
            # Each ships its own photography, so gather images from both.
            contributing = [style] + [p for p, par in merged_styles.items()
                                      if par == style]

            # Collect images across each style's colourways, de-duplicated.
            imgs, seen_img = [], set()
            for src_style in contributing:
                src_meta = by_style.get(src_style, meta)
                for color in colors:
                    for size in sorted(sizes, key=size_sort_key):
                        vrow = by_variant.get((src_style, color, size)) or \
                               by_variant.get((src_style, color, "O/S"))
                        if vrow:
                            for name in image_names(vrow):
                                if name not in seen_img:
                                    seen_img.add(name)
                                    imgs.append(name)
                            break
                for name in image_names(src_meta):
                    if name not in seen_img:
                        seen_img.add(name)
                        imgs.append(name)

            if imgs:
                manifest[handle] = {"title": title, "images": imgs}

            weight_oz = clean(meta.get("Weight (oz)"))
            try:
                grams = int(round(float(weight_oz) * 28.3495)) if weight_oz else 0
            except ValueError:
                grams = 0

            for i, r in enumerate(rows):
                first = i == 0
                price = retail_price(r["_wholesale"], args.markup)
                record = {c: "" for c in SHOPIFY_COLUMNS}
                record.update({
                    "Handle": handle,
                    "Option1 Name": "Color" if first else "",
                    "Option1 Value": clean(r.get("COLOR")).title(),
                    "Option2 Name": ("Size" if first and multi_size else ""),
                    "Option2 Value": (clean(r.get("SIZE")).upper() if multi_size else ""),
                    "Variant SKU": clean(r.get("SKU")),
                    "Variant Grams": grams,
                    "Variant Inventory Tracker": "shopify",
                    "Variant Inventory Qty": r["_qty"],
                    "Variant Inventory Policy": "deny",
                    "Variant Fulfillment Service": "manual",
                    "Variant Price": f"{price:.2f}",
                    "Variant Requires Shipping": "TRUE",
                    "Variant Taxable": "TRUE",
                    "Variant Barcode": clean(r.get("UPC")),
                })
                if first:
                    record.update({
                        "Title": f"{title} — Style {style}",
                        "Body (HTML)": build_body_html(meta),
                        "Vendor": ATTRIBUTION,
                        "Type": clean(meta.get("Category 1")).rstrip(". ") or "Lingerie",
                        "Tags": build_tags(meta, contributing),
                        "Published": "TRUE" if args.status == "active" else "FALSE",
                        "Status": args.status,
                    })
                    if imgs and image_base:
                        record["Image Src"] = image_base + imgs[0]
                        record["Image Position"] = 1
                        record["Image Alt Text"] = f"{title} by {ATTRIBUTION}"
                writer.writerow(record)
                variant_count += 1

            # Additional images ride on their own rows, keyed by handle.
            if image_base and len(imgs) > 1:
                for pos, name in enumerate(imgs[1:], start=2):
                    extra = {c: "" for c in SHOPIFY_COLUMNS}
                    extra.update({
                        "Handle": handle,
                        "Image Src": image_base + name,
                        "Image Position": pos,
                        "Image Alt Text": f"{title} by {ATTRIBUTION}",
                    })
                    writer.writerow(extra)

    manifest_path = out_path.parent / "image_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    total_styles_seen = len({clean(r.get("STYLE")) for r in sellable})
    print(f"Inventory rows:        {len(all_rows)}")
    print(f"  sellable:            {len(sellable)}  ({total_styles_seen} styles)")
    print(f"Description styles:    {len(by_style)}")
    print(f"Products written:      {len(styles)}")
    if args.merge_plus:
        print(f"  plus styles merged:  {len(merged_styles)} "
              f"(folded into their regular-size parent)")
    print(f"Variant rows written:  {variant_count}")
    print(f"Styles without copy:   {len(skipped_no_copy)} (skipped — need Holiday/"
          f"Hosiery/Vivace description files)")
    if not image_base:
        print("Images:                NONE — rerun with --image-base once the "
              "Catalog Images manifest is available")
    print(f"\nWrote {out_path}")
    print(f"Wrote {manifest_path} ({len(manifest)} products with images)")


if __name__ == "__main__":
    main()
