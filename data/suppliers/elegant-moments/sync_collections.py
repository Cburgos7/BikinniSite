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
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from push_products import (  # noqa: E402
    load_env_file, mint_token, Admin, ShopifyError, STORE,
)

# Which tags feed which collection handle. A product can appear in several.
#   tags     any of these puts a product in the collection
#   exclude  ...unless it also carries one of these
COLLECTION_TAGS = OrderedDict([
    ("lingerie", {
        "title": "Lingerie",
        "tags": ["Lingerie", "Babydoll", "Teddy", "Bra Set", "Bra", "Thong",
                 "G-String", "Panty", "Bodystocking", "Robe", "Chemise",
                 "Corset", "Bustier", "Camisole", "Slip", "Garter", "Hosiery"],
        # The Vivace catalogue includes men's thongs and briefs. They match the
        # garment tags above but do not belong in a women's lingerie collection.
        "exclude": ["Menswear"],
    }),
    ("swimwear", {
        "title": "Swimwear",
        "tags": ["Swimwear"],
        "exclude": [],
    }),
])

# Collections the storefront already links to under an older name. Renaming in
# place (handle and title) keeps those links resolving and avoids a duplicate
# empty collection sitting next to the real one. Shopify is asked to leave a
# redirect behind for the old handle.
RENAMED_FROM = {
    "swimwear": "bikinis",
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

COLLECTION_UPDATE = """
mutation($input:CollectionInput!){
  collectionUpdate(input:$input){
    collection{ id handle title }
    userErrors{ field message }
  }
}
"""

COLLECTION_CREATE = """
mutation($input:CollectionInput!){
  collectionCreate(input:$input){
    collection{ id handle title }
    userErrors{ field message }
  }
}
"""


def resolve_collection(admin, handle, title, dry_run=False):
    """Find the collection for `handle`, renaming or creating it if needed.

    Order matters: an existing collection under the old handle is renamed rather
    than left behind as an empty duplicate, because the theme's navigation links
    to whichever handle survives.
    """
    col = admin.query(COLLECTION_BY_HANDLE, {"handle": handle}) \
               .get("collectionByHandle")
    if col:
        return col

    old = RENAMED_FROM.get(handle)
    if old:
        prev = admin.query(COLLECTION_BY_HANDLE, {"handle": old}) \
                    .get("collectionByHandle")
        if prev:
            print(f"  /{old} -> /{handle}: renaming existing collection "
                  f"({prev['productsCount']['count']} products)")
            if dry_run:
                return None
            r = admin.query(COLLECTION_UPDATE, {"input": {
                "id": prev["id"], "handle": handle, "title": title,
                # Leave a redirect so any link to the old handle still works.
                "redirectNewHandle": True,
            }})
            errs = r["collectionUpdate"]["userErrors"]
            if errs:
                print(f"    ! rename failed: {errs}")
                return None
            return admin.query(COLLECTION_BY_HANDLE, {"handle": handle}) \
                        .get("collectionByHandle")

    print(f"  /{handle}: does not exist — creating {title!r}")
    if dry_run:
        return None
    r = admin.query(COLLECTION_CREATE, {"input": {
        "handle": handle, "title": title}})
    errs = r["collectionCreate"]["userErrors"]
    if errs:
        print(f"    ! create failed: {errs}")
        return None
    return admin.query(COLLECTION_BY_HANDLE, {"handle": handle}) \
                .get("collectionByHandle")


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
    for handle, spec in COLLECTION_TAGS.items():
        wanted = {t.lower() for t in spec["tags"]}
        banned = {t.lower() for t in spec["exclude"]}
        matches = []
        for p in products:
            tags = {t.lower() for t in p["tags"]}
            if tags & wanted and not tags & banned:
                matches.append(p)
        print(f"  /{handle}: {len(matches)} matching products")
        col = resolve_collection(admin, handle, spec["title"], args.dry_run)
        if not col:
            if not args.dry_run:
                print(f"  ! no collection /{handle} — skipping")
            continue
        if col.get("ruleSet"):
            print(f"  ! /{handle} is a smart collection; leaving its rules alone")
            continue
        print(f"    holds {col['productsCount']['count']} now")
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
