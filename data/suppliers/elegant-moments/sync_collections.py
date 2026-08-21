#!/usr/bin/env python3
"""Populate storefront collections from the imported catalogue.

Products land in Shopify tagged by supplier category, but the theme's navigation
points at specific collections. Without this step the catalogue is reachable only
at /collections/all and the storefront looks empty.

Usage:
    python sync_collections.py --dry-run
    python sync_collections.py
"""

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from push_products import (  # noqa: E402
    load_env_file, mint_token, Admin, ShopifyError, STORE,
)

# Which tags feed which collection handle. A product can appear in several.
COLLECTION_TAGS = {
    "lingerie": ["Lingerie", "Babydoll", "Teddy", "Bra Set", "Bra", "Thong",
                 "G-String", "Panty", "Bodystocking", "Robe", "Chemise",
                 "Corset", "Bustier", "Camisole", "Slip", "Garter", "Hosiery"],
}

# Everything published is new at launch; the theme's New In collection is a smart
# collection keyed on this tag.
NEW_TAG = "new"

PRODUCTS = """
query($c:String){ products(first:100, after:$c, query:"status:active"){
  pageInfo{hasNextPage endCursor}
  edges{node{ id handle title tags }}}}
"""

COLLECTION_BY_HANDLE = """
query($handle:String!){ collectionByHandle(handle:$handle){
  id title productsCount{count} ruleSet{ rules{column relation condition} } } }
"""

ADD_PRODUCTS = """
mutation($id:ID!, $productIds:[ID!]!){
  collectionAddProductsV2(id:$id, productIds:$productIds){
    userErrors{ field message }
  }
}
"""

ADD_TAGS = """
mutation($id:ID!, $tags:[String!]!){
  tagsAdd(id:$id, tags:$tags){ userErrors{ field message } }
}
"""


def fetch_active_products(admin):
    cur, out = None, []
    while True:
        d = admin.query(PRODUCTS, {"c": cur})["products"]
        out += [e["node"] for e in d["edges"]]
        if not d["pageInfo"]["hasNextPage"]:
            break
        cur = d["pageInfo"]["endCursor"]
    return out


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--env", default=None)
    ap.add_argument("--skip-new-tag", action="store_true",
                    help="do not tag products as new")
    args = ap.parse_args()

    load_env_file(args.env)
    cid, secret = (os.environ.get("SHOPIFY_CLIENT_ID"),
                   os.environ.get("SHOPIFY_CLIENT_SECRET"))
    if not (cid and secret):
        sys.exit("Missing credentials — see push_products.py --help")
    admin = Admin(STORE, mint_token(STORE, cid, secret))

    products = fetch_active_products(admin)
    print(f"active products: {len(products)}")

    # --- collection membership ---
    for handle, tags in COLLECTION_TAGS.items():
        wanted = tags_lower = {t.lower() for t in tags}
        matches = [p for p in products
                   if {t.lower() for t in p["tags"]} & tags_lower]
        col = admin.query(COLLECTION_BY_HANDLE, {"handle": handle})
        col = col.get("collectionByHandle")
        if not col:
            print(f"  ! no collection /{handle} — skipping")
            continue
        if col.get("ruleSet"):
            print(f"  ! /{handle} is a smart collection; leaving its rules alone")
            continue
        print(f"  /{handle}: {col['productsCount']['count']} now -> "
              f"{len(matches)} matching products")
        if args.dry_run or not matches:
            continue
        for batch in chunked([p["id"] for p in matches], 100):
            r = admin.query(ADD_PRODUCTS, {"id": col["id"], "productIds": batch})
            errs = r["collectionAddProductsV2"]["userErrors"]
            if errs:
                print(f"    ! {errs}")

    # --- new tag ---
    if not args.skip_new_tag:
        need = [p for p in products
                if NEW_TAG not in {t.lower() for t in p["tags"]}]
        print(f"\ntagging '{NEW_TAG}': {len(need)} products need it")
        if not args.dry_run:
            for i, p in enumerate(need, 1):
                r = admin.query(ADD_TAGS, {"id": p["id"], "tags": [NEW_TAG]})
                errs = r["tagsAdd"]["userErrors"]
                if errs:
                    print(f"    ! {p['handle']}: {errs}")
                if i % 50 == 0:
                    print(f"    {i}/{len(need)}")

    print("\nDone." if not args.dry_run else "\nDry run — nothing changed.")


if __name__ == "__main__":
    main()
