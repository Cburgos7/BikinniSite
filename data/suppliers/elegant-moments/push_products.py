#!/usr/bin/env python3
"""Push the generated Elegant Moments catalog into Shopify via the Admin API.

The CSV importer needs publicly reachable image URLs, and we have none — the
supplier ships a ZIP, not hosted images. So instead of importing the CSV, this
creates each product through the GraphQL Admin API and uploads the image bytes
directly to Shopify's CDN.

Products are created as DRAFT. Nothing is published by this script.

Credentials come from the Dev Dashboard app installed on the store; the token is
minted server-to-server and lasts about 24 hours. Put them in a `.env` file beside
this script (gitignored, never committed):

    SHOPIFY_CLIENT_ID=...
    SHOPIFY_CLIENT_SECRET=...

Then:

    python push_products.py --limit 1        # smoke-test one product first
    python push_products.py                  # full run

Environment variables of the same names take precedence if set.

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

# Set from --out-dir at startup so each catalogue can be pushed from its own
# build directory (out/ for the 2026 collection, out/vivace/ for Vivace).
CSV_PATH = OUT / "shopify_products.csv"
MANIFEST_PATH = OUT / "image_manifest.json"
IMAGE_DIR = OUT / "images"

STORE = "velvet-tide-2.myshopify.com"
API_VERSION = "2025-10"


class ShopifyError(RuntimeError):
    pass


def load_env_file(path=None):
    """Read KEY=VALUE pairs from a local .env without adding a dependency.

    Keeps the client secret out of shell history and out of any transcript.
    Real environment variables win, so CI can override the file.
    """
    path = Path(path) if path else HERE / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


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

PRODUCT_BY_HANDLE_FULL = """
query($handle: String!) {
  productByHandle(handle: $handle) {
    id handle status title descriptionHtml
    media(first: 1) { edges { node { id } } }
  }
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
    # prepare_images.py writes lowercased filenames; workbooks sometimes spell
    # them with capitals. Fall back to a case-insensitive match so a casing
    # difference does not silently cost a product its photo (and, with
    # --publish, leave it stuck in draft).
    paths = []
    for name in filenames:
        p = IMAGE_DIR / name
        if not p.exists():
            p = IMAGE_DIR / name.lower()
        if p.exists():
            paths.append(p)
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


PRODUCT_UPDATE = """
mutation($product: ProductUpdateInput!) {
  productUpdate(product: $product) {
    product { id handle }
    userErrors { field message }
  }
}
"""

PUBLICATIONS = """
query { publications(first: 20) { edges { node { id name } } } }
"""

PUBLISH = """
mutation($id: ID!, $input: [PublicationInput!]!) {
  publishablePublish(id: $id, input: $input) {
    userErrors { field message }
  }
}
"""


def update_copy(admin, items):
    """Refresh title and description on products that already exist.

    Used when the copy rules change — cheaper and safer than recreating, which
    would discard uploaded images and stock levels.
    """
    updated = unchanged = missing = 0
    for i, (handle, p) in enumerate(items, 1):
        head = p["head"]
        data = admin.query(PRODUCT_BY_HANDLE_FULL, {"handle": handle})
        product = data.get("productByHandle")
        if not product:
            missing += 1
            continue
        if (product["title"] == head["Title"]
                and product["descriptionHtml"] == head["Body (HTML)"]):
            unchanged += 1
            continue
        result = admin.query(PRODUCT_UPDATE, {"product": {
            "id": product["id"],
            "title": head["Title"],
            "descriptionHtml": head["Body (HTML)"],
        }})
        errs = result["productUpdate"]["userErrors"]
        if errs:
            print(f"  ! {handle}: {errs}")
        else:
            updated += 1
        if i % 50 == 0:
            print(f"  {i}/{len(items)}  updated={updated} unchanged={unchanged}")
    print(f"\nCopy update done. updated={updated} unchanged={unchanged} "
          f"not_found={missing}")


def publish_products(admin, items, require_image=True):
    """Set products ACTIVE and publish them to the Online Store.

    Products with no image are left as drafts by default — an empty product card
    on a collection grid looks broken, and these have no photo because the
    supplier never shipped one.
    """
    pubs = admin.query(PUBLICATIONS)["publications"]["edges"]
    online = next((p["node"] for p in pubs
                   if p["node"]["name"] == "Online Store"), None)
    if not online:
        sys.exit(f"No Online Store publication found. Available: "
                 f"{[p['node']['name'] for p in pubs]}")
    print(f"Publishing to: {online['name']}")

    published = skipped_noimg = missing = 0
    for i, (handle, _p) in enumerate(items, 1):
        data = admin.query(PRODUCT_BY_HANDLE_FULL, {"handle": handle})
        product = data.get("productByHandle")
        if not product:
            missing += 1
            continue
        if require_image and not product["media"]["edges"]:
            skipped_noimg += 1
            continue

        if product["status"] != "ACTIVE":
            result = admin.query(PRODUCT_UPDATE, {"product": {
                "id": product["id"], "status": "ACTIVE"}})
            errs = result["productUpdate"]["userErrors"]
            if errs:
                print(f"  ! {handle}: {errs}")
                continue

        result = admin.query(PUBLISH, {
            "id": product["id"],
            "input": [{"publicationId": online["id"]}],
        })
        errs = result["publishablePublish"]["userErrors"]
        if errs:
            print(f"  ! {handle}: {errs}")
            continue
        published += 1
        if i % 50 == 0:
            print(f"  {i}/{len(items)}  published={published} "
                  f"no_image_skipped={skipped_noimg}")

    print(f"\nPublish done. published={published} "
          f"left_as_draft_no_image={skipped_noimg} not_found={missing}")


LOCATIONS = """
query { locations(first: 1) { edges { node { id name } } } }
"""

VARIANTS_BY_HANDLE = """
query($handle: String!) {
  productByHandle(handle: $handle) {
    id
    variants(first: 100) {
      edges { node { sku inventoryItem { id } } }
    }
  }
}
"""

SET_QUANTITIES = """
mutation($input: InventorySetQuantitiesInput!) {
  inventorySetQuantities(input: $input) {
    userErrors { field message }
  }
}
"""


def backfill_inventory(admin, items, location_id):
    """Set stock on products that already exist, matching variants by SKU.

    Used when the first push ran without read_locations and the scope was added
    afterwards.
    """
    updated = missing = 0
    for i, (handle, p) in enumerate(items, 1):
        want = {v["Variant SKU"]: int(v["Variant Inventory Qty"] or 0)
                for v in p["variants"]}
        data = admin.query(VARIANTS_BY_HANDLE, {"handle": handle})
        product = data.get("productByHandle")
        if not product:
            missing += 1
            continue

        quantities = []
        for edge in product["variants"]["edges"]:
            node = edge["node"]
            if node["sku"] in want:
                quantities.append({
                    "inventoryItemId": node["inventoryItem"]["id"],
                    "locationId": location_id,
                    "quantity": want[node["sku"]],
                })
        if not quantities:
            continue

        result = admin.query(SET_QUANTITIES, {"input": {
            "name": "available",
            "reason": "correction",
            "ignoreCompareQuantity": True,
            "quantities": quantities,
        }})
        errs = result["inventorySetQuantities"]["userErrors"]
        if errs:
            print(f"  ! {handle}: {errs}")
        else:
            updated += 1
        if i % 25 == 0:
            print(f"  {i}/{len(items)}  updated={updated}")

    print(f"\nInventory backfill done. updated={updated} "
          f"products_not_found={missing}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--out-dir", default=str(OUT),
                    help="build directory holding shopify_products.csv, "
                         "image_manifest.json and images/ (default out/; use "
                         "out/vivace for the Vivace catalogue)")
    ap.add_argument("--limit", type=int, default=0,
                    help="only push the first N products (0 = all)")
    ap.add_argument("--skip-images", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and print payloads without calling Shopify")
    ap.add_argument("--env", default=None,
                    help="path to the env file holding credentials "
                         "(default: .env beside this script)")
    ap.add_argument("--inventory-only", action="store_true",
                    help="do not create products; set stock levels on products "
                         "that already exist (needs read_locations)")
    ap.add_argument("--update-copy", action="store_true",
                    help="refresh title and description on existing products "
                         "without recreating them")
    ap.add_argument("--publish", action="store_true",
                    help="set existing products ACTIVE and publish to the Online "
                         "Store; products with no image stay draft")
    ap.add_argument("--publish-without-images", action="store_true",
                    help="with --publish, also publish products that have no image")
    args = ap.parse_args()

    global CSV_PATH, MANIFEST_PATH, IMAGE_DIR
    out_dir = Path(args.out_dir)
    CSV_PATH = out_dir / "shopify_products.csv"
    MANIFEST_PATH = out_dir / "image_manifest.json"
    IMAGE_DIR = out_dir / "images"

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

    load_env_file(args.env)
    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (client_id and client_secret):
        sys.exit(
            "Missing credentials.\n"
            f"Create {HERE / '.env'} containing:\n"
            "    SHOPIFY_CLIENT_ID=...\n"
            "    SHOPIFY_CLIENT_SECRET=...\n"
            "from dev.shopify.com -> Apps -> Velvet tide -> Client credentials.\n"
            "The file is gitignored."
        )

    token = mint_token(args.store, client_id, client_secret)
    admin = Admin(args.store, token)

    # Setting stock needs a location, which needs read_locations. Without it we
    # can still create everything else, so degrade rather than refuse: a draft
    # product with no stock is recoverable, a failed run is just lost work.
    location_id = None
    try:
        loc = admin.query(LOCATIONS, retries=1)["locations"]["edges"]
        location_id = loc[0]["node"]["id"] if loc else None
        print(f"Location: {loc[0]['node']['name'] if loc else 'NONE'}")
    except ShopifyError as exc:
        if "ACCESS_DENIED" not in str(exc):
            raise
        print("WARNING: no read_locations scope — creating products WITHOUT "
              "stock levels.\n"
              "         Add read_locations + write_inventory to the app, then "
              "re-run with --inventory-only\n"
              "         to backfill quantities onto the products already created.")

    if args.inventory_only:
        if not location_id:
            sys.exit("--inventory-only needs read_locations on the app.")
        backfill_inventory(admin, items, location_id)
        return

    if args.update_copy:
        update_copy(admin, items)
        return

    if args.publish:
        publish_products(admin, items,
                         require_image=not args.publish_without_images)
        return

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
