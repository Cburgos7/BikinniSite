#!/usr/bin/env python3
"""Recompress Elegant Moments catalog images for upload to Shopify.

The supplier ships ~1200x1800 JPEGs at very low compression (~0.6 MB each,
811 MB for the 2026 collection). Re-encoding at quality 82 keeps the same pixel
dimensions but cuts the payload roughly 5x, which matters because every image is
uploaded over the Admin API. Shopify re-encodes and serves responsive derivatives
from its CDN regardless, so nothing is lost in delivered quality.

Dimensions are never changed — the supplier licence forbids modifying images in a
way that distorts the original proportions.

Usage:
    python prepare_images.py --src "F:/CODING/BikinniSite/Files_Site/Items"
    python prepare_images.py --catalogue vivace \
        --src "F:/CODING/BikinniSite/Files_Site/vivace/Items"

The source tree is searched recursively: the 2026 ZIP was flat, but the Vivace
ZIP splits its files across `1200pxw/` and `Editorials/` while the workbook still
references bare filenames.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: python -m pip install Pillow")

# Share the workbook parsing with the importer so a header quirk or a new
# catalogue only has to be described once — the 2026 Hosiery sheet ships blank
# headers for its image columns, and Vivace runs to Image 8 rather than Image 4.
from build_import import (
    CATALOGUES, DEFAULT_CATALOGUE, image_columns, read_sheet, SOURCE,
)


def referenced_images(catalogue):
    """Image filenames the descriptions workbook actually points at."""
    path = SOURCE / catalogue["workbook"]
    names = set()
    for sheet in catalogue["sheets"]:
        header, rows = read_sheet(path, sheet, catalogue["images"])
        if header is None:
            continue
        cols = image_columns(header)
        idx = [header.index(c) for c in cols]
        style_at = header.index("Style")
        for raw in rows:
            if style_at >= len(raw) or raw[style_at] in (None, ""):
                continue
            for i in idx:
                if i < len(raw) and raw[i]:
                    names.add(str(raw[i]).strip().lower())
    return names


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--catalogue", default=DEFAULT_CATALOGUE,
                    choices=list(CATALOGUES))
    ap.add_argument("--src", required=True,
                    help="directory of extracted supplier JPEGs (searched "
                         "recursively)")
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--dest", default=None,
                    help="output directory (default: the catalogue's "
                         "out/images)")
    ap.add_argument("--all", action="store_true",
                    help="convert every JPEG, not just those the workbook references")
    args = ap.parse_args()

    catalogue = CATALOGUES[args.catalogue]
    src = Path(args.src)
    if not src.is_dir():
        sys.exit(f"Not a directory: {src}")
    dest = Path(args.dest) if args.dest else catalogue["out"] / "images"
    dest.mkdir(parents=True, exist_ok=True)

    wanted = None if args.all else referenced_images(catalogue)
    # Recursive: the Vivace ZIP nests product shots under 1200pxw/ and lifestyle
    # shots under Editorials/, but the workbook references bare filenames.
    on_disk = {}
    for p in src.rglob("*.jpg"):
        on_disk.setdefault(p.name.lower(), p)

    if wanted is not None:
        missing = sorted(wanted - set(on_disk))
        if missing:
            print(f"WARNING: {len(missing)} referenced image(s) not in {src}:")
            for name in missing[:10]:
                print(f"  {name}")

    targets = sorted(on_disk) if wanted is None else sorted(wanted & set(on_disk))

    orig_bytes = new_bytes = 0
    for i, name in enumerate(targets, 1):
        srcp = on_disk[name]
        outp = dest / name
        orig_bytes += srcp.stat().st_size
        with Image.open(srcp) as im:
            im = im.convert("RGB")
            im.save(outp, "JPEG", quality=args.quality, optimize=True,
                    progressive=True)
        new_bytes += outp.stat().st_size
        if i % 100 == 0:
            print(f"  {i}/{len(targets)}...")

    saved = 100 * (1 - new_bytes / orig_bytes) if orig_bytes else 0
    print(f"\nConverted {len(targets)} images")
    print(f"  {orig_bytes/1e6:.0f} MB -> {new_bytes/1e6:.0f} MB  ({saved:.0f}% smaller)")
    print(f"  written to {dest}")


if __name__ == "__main__":
    main()
