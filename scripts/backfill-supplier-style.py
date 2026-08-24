#!/usr/bin/env python3
"""Backfill variant.metafields.custom.supplier_style on the live store.

WHY THIS EXISTS
---------------
Elegant Moments has no API. Every order is an email a human keys into their
order-entry screen, and the field they key is the STYLE NUMBER. Get it wrong and
the customer receives the wrong garment.

The Phase 7 research concluded the style could be derived from the SKU:

    "The supplier style number is the variant SKU with any -SIZE suffix
     stripped. Nothing else."

That is wrong for 466 of our 1,522 live variants (31%). Checked against the
supplier's own STYLE column in liveinventory.csv:

    SKU          derived      actual STYLE
    L1249BL      L1249BL      L1249        <- trailing colour code, not style
    L2316P       L2316P       L2316
    L2316XP      L2316XP      L2316X       <- X IS style, P is not
    L1237SALE    L1237SALE    L1237
    82509        82509        85209        <- supplier's own transposition

`L2316P` -> `L2316` but `L2316XP` -> `L2316X` is the killer: a trailing letter is
sometimes part of the style and sometimes a colour code, and nothing in the SKU
says which. There is no string rule. There is only the supplier's STYLE column.

So we carry it as data. Every variant gets the supplier's own STYLE value, and
the drop-ship order email prints that metafield rather than deriving anything.

Re-run after every product import -- build_import.py does not write metafields,
so new variants arrive without one. Idempotent: variants already carrying the
correct value are skipped.

USAGE
-----
    python scripts/backfill-supplier-style.py            # dry run
    python scripts/backfill-supplier-style.py --apply    # write
"""
import argparse
import csv
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUP = REPO / "data" / "suppliers" / "elegant-moments"
sys.path.insert(0, str(SUP))
import push_products as pp  # noqa: E402

NAMESPACE = "custom"
KEY = "supplier_style"
MF_TYPE = "single_line_text_field"
OWNER_TYPE = "PRODUCTVARIANT"
INVENTORY = SUP / "source" / "liveinventory.csv"

VARIANTS = """
query($cursor: String) {
  productVariants(first: 250, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id sku
      product { handle }
      metafield(namespace: "custom", key: "supplier_style") { value }
    }
  }
}
"""

DEFINITIONS = """
query {
  metafieldDefinitions(first: 25, ownerType: PRODUCTVARIANT, namespace: "custom") {
    edges { node { key name type { name } } }
  }
}
"""

DEFINITION_CREATE = """
mutation($def: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $def) {
    createdDefinition { key }
    userErrors { field message code }
  }
}
"""

METAFIELDS_SET = """
mutation($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { key }
    userErrors { field message code }
  }
}
"""


def load_style_map():
    """SKU -> supplier STYLE, read from the supplier's live inventory export.

    Read-only. data/suppliers/** is the importer's tree; this script never
    writes there.
    """
    if not INVENTORY.exists():
        sys.exit(f"missing {INVENTORY}")
    out = {}
    with INVENTORY.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            sku = (row.get("SKU") or "").strip()
            style = (row.get("STYLE") or "").strip()
            if sku and style:
                out[sku] = style
    return out


def resolve(sku, styles):
    """Supplier STYLE for one of our SKUs.

    Our merged plus-size products append "-SIZE" to the supplier SKU for
    multi-size styles (L1162-M), which the supplier's own file does not carry.
    Fall back to the pre-hyphen part for those, which IS a real supplier SKU.
    Never guess beyond that: an unresolved SKU is reported, not invented.
    """
    if sku in styles:
        return styles[sku]
    base = sku.split("-", 1)[0]
    return styles.get(base)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write to the store; without it this is a dry run")
    args = ap.parse_args()

    styles = load_style_map()
    print(f"supplier inventory: {len(styles)} SKU->STYLE pairs")

    pp.load_env_file(SUP / ".env")
    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (client_id and client_secret):
        sys.exit(f"Set SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET, or put them "
                 f"in {SUP / '.env'}")
    admin = pp.Admin(pp.STORE, pp.mint_token(pp.STORE, client_id, client_secret))

    defs = {e["node"]["key"]: e["node"]["type"]["name"]
            for e in admin.query(DEFINITIONS)["metafieldDefinitions"]["edges"]}
    if KEY not in defs:
        print(f"metafield definition {NAMESPACE}.{KEY} missing")
        if args.apply:
            r = admin.query(DEFINITION_CREATE, {"def": {
                "name": "Supplier style",
                "namespace": NAMESPACE,
                "key": KEY,
                "type": MF_TYPE,
                "ownerType": OWNER_TYPE,
                "description": ("Elegant Moments style number, as printed on the "
                                "drop-ship order email. Authoritative: not "
                                "derivable from the SKU."),
                # Access is deliberately left at Shopify's default. Setting
                # admin: MERCHANT_READ_WRITE is rejected for variant-owned
                # definitions created by this app -- the API replies that the
                # only permitted value is public_read_write.
            }})["metafieldDefinitionCreate"]
            if r["userErrors"]:
                sys.exit(f"definition create failed: {json.dumps(r['userErrors'])}")
            print(f"  created definition {NAMESPACE}.{KEY}")
        else:
            print("  would create it (--apply)")
    elif defs[KEY] != MF_TYPE:
        sys.exit(f"definition {KEY} is {defs[KEY]!r}, expected {MF_TYPE!r}")

    todo, skipped, unresolved, derived_would_differ = [], 0, [], 0
    cursor = None
    total = 0
    while True:
        conn = admin.query(VARIANTS, {"cursor": cursor})["productVariants"]
        for n in conn["nodes"]:
            total += 1
            sku = (n.get("sku") or "").strip()
            style = resolve(sku, styles) if sku else None
            if not style:
                unresolved.append(f"{n['product']['handle']}:{sku or '<blank>'}")
                continue
            if sku.split("-", 1)[0] != style:
                derived_would_differ += 1
            if ((n.get("metafield") or {}).get("value")) == style:
                skipped += 1
                continue
            todo.append({"ownerId": n["id"], "namespace": NAMESPACE,
                         "key": KEY, "type": MF_TYPE, "value": style})
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]

    print(f"live variants: {total}")
    print(f"to write: {len(todo)}  already correct: {skipped}  "
          f"unresolved: {len(unresolved)}")
    print(f"variants where the old SKU-derived rule would have been WRONG: "
          f"{derived_would_differ}")
    if unresolved:
        print("  UNRESOLVED (no supplier STYLE; these must not be auto-ordered):")
        for u in unresolved[:20]:
            print("   ", u)

    if not args.apply:
        print("\nDRY RUN -- rerun with --apply to write.")
        return

    written = 0
    for i in range(0, len(todo), 25):
        r = admin.query(METAFIELDS_SET,
                        {"metafields": todo[i:i + 25]})["metafieldsSet"]
        if r["userErrors"]:
            print("USER ERRORS:", json.dumps(r["userErrors"])[:800])
            sys.exit(1)
        written += len(r["metafields"])
        print(f"  wrote {written}/{len(todo)}")
    print(f"DONE: {written} metafields written.")
    if unresolved:
        print(f"WARNING: {len(unresolved)} variants still have no supplier "
              f"style and will print a DO NOT SHIP line in the order email.")


if __name__ == "__main__":
    main()
