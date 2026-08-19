#!/usr/bin/env python3
"""Push the generated Elegant Moments catalog into Shopify via the Admin API.

The CSV importer needs publicly reachable image URLs, and we have none — the
supplier ships a ZIP, not hosted images. So instead of importing the CSV, this
creates each product through the GraphQL Admin API and uploads the image bytes
directly to Shopify's CDN.

Products are created as DRAFT. Nothing is published by this script.

Credentials come from the Dev Dashboard app installed on the store; the token is
minted server-to-server and lasts about 24 hours:

    export SHOPIFY_CLIENT_ID=...
    export SHOPIFY_CLIENT_SECRET=...
    python push_products.py --limit 1        # smoke-test one product first
    python push_products.py                  # full run

Re-running is safe: products are matched by handle and skipped if they exist
(use --update to refresh price and inventory on existing products instead).
"""

import argparse
import base64
import csv
import json
import mimetypes
import os
import sys
import time
from collections import OrderedDict
from pathlib import Path
from urllib import request, error

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
CSV_PATH = OUT / "shopify_products.csv"
MANIFEST_PATH = OUT / "image_manifest.json"
IMAGE_DIR = OUT / "images"

STORE = "velvet-tide-2.myshopify.com"
API_VERSION = "2025-10"


class ShopifyError(RuntimeError):
    pass


def post_json(url, payload, headers, timeout=120):
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise ShopifyError(f"HTTP {exc.code} from {url}: {detail}") from exc


def mint_token(store, client_id, client_secret):
    """Client-credentials token exchange. Legacy custom-app tokens are disabled;
    this is the Dev Dashboard path."""
    data = post_json(
        f"https://{store}/admin/oauth/access_token",
        {"client_id": client_id, "client_secret": client_secret,
         "grant_type": "client_credentials"},
        {"Content-Type": "application/json"},
    )
    token = data.get("access_token")
    if not token:
        raise ShopifyError(f"No access_token in response: {data}")
    return token


class Admin:
    def __init__(self, store, token):
        self.url = f"https://{store}/admin/api/{API_VERSION}/graphql.json"
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": token,
        }

    def query(self, query, variables=None, retries=4):
        payload = {"query": query, "variables": variables or {}}
        for attempt in range(retries):
            try:
                data = post_json(self.url, payload, self.headers)
            except ShopifyError as exc:
                # 429/5xx are worth backing off on; anything else is fatal.
                if attempt < retries - 1 and ("HTTP 429" in str(exc)
                                              or "HTTP 5" in str(exc)):
                    time.sleep(2 ** attempt)
                    continue
                raise
            if "errors" in data and data["errors"]:
                msg = json.dumps(data["errors"])[:400]
                # Throttled queries report as a top-level error, not an HTTP code.
                if "THROTTLED" in msg.upper() and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise ShopifyError(f"GraphQL errors: {msg}")
            return data["data"]
        raise ShopifyError("exhausted retries")


PRODUCT_BY_HANDLE = """
query($handle: String!) {
  productByHandle(handle: $handle) { id handle status }
}
"""

PRODUCT_SET = """
mutation($input: ProductSetInput!) {
  productSet(synchronous: true, input: $input) {
    product { id handle }
    userErrors { field message }
  }
}
"""

STAGED_UPLOADS = """
mutation($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets { url resourceUrl parameters { name value } }
    userErrors { field message }
  }
}
"""

CREATE_MEDIA = """
mutation($productId: ID!, $media: [CreateMediaInput!]!) {
  productCreateMedia(productId: $productId, media: $media) {
    media { ... on MediaImage { id } }
    mediaUserErrors { field message }
  }
}
"""


def read_products():
    """Group the generated CSV back into products keyed by handle."""
    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    products = OrderedDict()
    for r in rows:
        handle = r["Handle"]
        if not r.get("Variant SKU"):
            continue  # image-only continuation row
        p = products.setdefault(handle, {"head": None, "variants": []})
        if r.get("Title"):
            p["head"] = r
        p["variants"].append(r)
    return products


def build_product_input(handle, head, variants, location_id):
    has_size = any(v.get("Option2 Value") for v in variants)
    option_names = ["Color"] + (["Size"] if has_size else [])

    colors, sizes = [], []
    for v in variants:
        c = v["Option1 Value"]
        if c and c not in colors:
            colors.append(c)
        s = v.get("Option2 Value")
        if has_size and s and s not in sizes:
            sizes.append(s)

    product_options = [{"name": "Color",
                        "values": [{"name": c} for c in colors]}]
    if has_size:
        product_options.append({"name": "Size",
                                "values": [{"name": s} for s in sizes]})

    variant_inputs = []
    for v in variants:
        opts = [{"optionName": "Color", "name": v["Option1 Value"]}]
        if has_size:
            opts.append({"optionName": "Size", "name": v["Option2 Value"]})
        entry = {
            "optionValues": opts,
            "price": v["Variant Price"],
            "sku": v["Variant SKU"],
            "barcode": v["Variant Barcode"],
            "inventoryPolicy": "DENY",
            "inventoryItem": {
                "tracked": True,
                "requiresShipping": True,
                "measurement": {
                    "weight": {"unit": "GRAMS",
                               "value": float(v["Variant Grams"] or 0)}
                },
            },
        }
        if location_id:
            entry["inventoryQuantities"] = [{
                "locationId": location_id,
                "name": "available",
                "quantity": int(v["Variant Inventory Qty"] or 0),
            }]
        variant_inputs.append(entry)

    return {
        "handle": handle,
        "title": head["Title"],
        "descriptionHtml": head["Body (HTML)"],
        "vendor": head["Vendor"],
        "productType": head["Type"],
        "tags": [t.strip() for t in head["Tags"].split(",") if t.strip()],
        "status": "DRAFT",
        "productOptions": product_options,
        "variants": variant_inputs,
    }


def upload_images(admin, product_id, title, filenames, alt):
    """Stage each JPEG to Shopify's bucket, then attach it as product media."""
    paths = [IMAGE_DIR / n for n in filenames]
    paths = [p for p in paths if p.exists()]
    if not paths:
        return 0

    staged_input = [{
        "filename": p.name,
        "mimeType": mimetypes.guess_type(p.name)[0] or "image/jpeg",
        "httpMethod": "POST",
        "resource": "IMAGE",
    } for p in paths]

    data = admin.query(STAGED_UPLOADS, {"input": staged_input})
    result = data["stagedUploadsCreate"]
    if result["userErrors"]:
        raise ShopifyError(f"stagedUploadsCreate: {result['userErrors']}")

    media = []
    for target, path in zip(result["stagedTargets"], paths):
        _multipart_put(target, path)
        media.append({
            "originalSource": target["resourceUrl"],
            "alt": alt,
            "mediaContentType": "IMAGE",
        })

    data = admin.query(CREATE_MEDIA, {"productId": product_id, "media": media})
    errs = data["productCreateMedia"]["mediaUserErrors"]
    if errs:
        raise ShopifyError(f"productCreateMedia: {errs}")
    return len(media)


def _multipart_put(target, path):
    """POST the file to the staged target using multipart/form-data.

    Shopify's staged targets require the returned parameters to precede the file
    part, in order.
    """
    boundary = "----emupload" + base64.b16encode(os.urandom(8)).decode()
    parts = []
    for param in target["parameters"]:
        parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="{param["name"]}"\r\n\r\n'
            f'{param["value"]}\r\n'.encode()
        )
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f'Content-Type: {mime}\r\n\r\n'.encode()
    )
    parts.append(path.read_bytes())
    parts.append(f'\r\n--{boundary}--\r\n'.encode())
    body = b"".join(parts)

    req = request.Request(
        target["url"], data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with request.urlopen(req, timeout=180) as resp:
            if resp.status not in (200, 201, 204):
                raise ShopifyError(f"staged upload returned {resp.status}")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise ShopifyError(f"staged upload HTTP {exc.code}: {detail}") from exc


LOCATIONS = """
query { locations(first: 1) { edges { node { id name } } } }
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--limit", type=int, default=0,
                    help="only push the first N products (0 = all)")
    ap.add_argument("--skip-images", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and print payloads without calling Shopify")
    args = ap.parse_args()

    if not CSV_PATH.exists():
        sys.exit(f"Missing {CSV_PATH} — run build_import.py first")

    products = read_products()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) \
        if MANIFEST_PATH.exists() else {}
    items = list(products.items())
    if args.limit:
        items = items[:args.limit]

    if args.dry_run:
        handle, p = items[0]
        print(json.dumps(build_product_input(handle, p["head"], p["variants"],
                                             None), indent=2)[:2000])
        print(f"\n{len(items)} products would be pushed.")
        return

    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (client_id and client_secret):
        sys.exit("Set SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET "
                 "(Dev Dashboard -> your app -> credentials)")

    token = mint_token(args.store, client_id, client_secret)
    admin = Admin(args.store, token)

    loc = admin.query(LOCATIONS)["locations"]["edges"]
    location_id = loc[0]["node"]["id"] if loc else None
    print(f"Location: {loc[0]['node']['name'] if loc else 'NONE'}")

    created = skipped = failed = images_up = 0
    for i, (handle, p) in enumerate(items, 1):
        try:
            existing = admin.query(PRODUCT_BY_HANDLE, {"handle": handle})
            if existing.get("productByHandle"):
                skipped += 1
                continue

            payload = build_product_input(handle, p["head"], p["variants"],
                                          location_id)
            data = admin.query(PRODUCT_SET, {"input": payload})
            errs = data["productSet"]["userErrors"]
            if errs:
                print(f"  ! {handle}: {errs}")
                failed += 1
                continue
            product_id = data["productSet"]["product"]["id"]
            created += 1

            if not args.skip_images and handle in manifest:
                entry = manifest[handle]
                images_up += upload_images(
                    admin, product_id, entry["title"], entry["images"],
                    f"{entry['title']} by Elegant Moments")
        except ShopifyError as exc:
            print(f"  ! {handle}: {exc}")
            failed += 1
        if i % 10 == 0:
            print(f"  {i}/{len(items)}  created={created} skipped={skipped} "
                  f"failed={failed} images={images_up}")

    print(f"\nDone. created={created} skipped={skipped} failed={failed} "
          f"images={images_up}")
    print("All products are DRAFT — review, then publish from Shopify admin.")


if __name__ == "__main__":
    main()
