#!/usr/bin/env python3
"""Backfill product.metafields.custom.fabric_composition on the live store.

WHY THIS EXISTS
---------------
The PDP renders four metafield accordions (care instructions, fabric
composition, coverage level, model sizing). The definitions were created but no
product ever carried a value, so all four were suppressed on every product and
the PDP had no detail surface below the buy box at all.

Fabric is the one of the four that is already in hand: the supplier importer
writes it into the product body as
`<li><strong>Fabric:</strong> 90% Nylon, 10% Spandex</li>`. This script lifts it
out of the live descriptionHtml and stores it as the metafield, so it is
displayed as structured data rather than buried in a bullet list.

Coverage level and model sizing have no supplier source and are not touched;
they stay hidden until someone curates them.

SCOPE
-----
data/suppliers/** is another owner's tree. This script only *reads* it: it
imports mint_token/Admin from push_products.py and loads its .env. It writes
nothing there and does not modify the importer.

Re-run this after every product import -- build_import.py does not populate
metafields, so new products arrive without one. It is idempotent: products whose
metafield already matches are skipped.

USAGE
-----
    python scripts/backfill-fabric-metafield.py            # dry run
    python scripts/backfill-fabric-metafield.py --apply    # write
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUP = REPO / "data" / "suppliers" / "elegant-moments"
sys.path.insert(0, str(SUP))
import push_products as pp  # noqa: E402

NAMESPACE = "custom"
KEY = "fabric_composition"
MF_TYPE = "single_line_text_field"

FAB = re.compile(r"<strong>\s*Fabric\s*:?\s*</strong>\s*([^<]+)", re.I)

PRODUCTS = """
query($cursor: String) {
  products(first: 100, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    edges { node {
      id handle descriptionHtml
      metafield(namespace: "custom", key: "fabric_composition") { value }
    } }
  }
}
"""

DEFINITIONS = """
query {
  metafieldDefinitions(first: 25, ownerType: PRODUCT, namespace: "custom") {
    edges { node { key name type { name } } }
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


def clean(raw):
    """Whitespace normalisation only -- the wording stays the supplier's.

    Deliberately does not tidy the chemistry. "95% Polyester, 5% Elasthan" is
    what the supplier states and what we are entitled to print; rewriting it to
    "Elastane" would be us making a fibre claim of our own.
    """
    v = re.sub(r"\s+", " ", raw).strip().strip(",;.")
    v = re.sub(r"(\d)\s+%", r"\1%", v)  # supplier typo: "100 % Polyester"
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write to the store; without it this is a dry run")
    args = ap.parse_args()

    pp.load_env_file(SUP / ".env")
    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (client_id and client_secret):
        sys.exit(f"Set SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET, or put them "
                 f"in {SUP / '.env'}")
    admin = pp.Admin(pp.STORE, pp.mint_token(pp.STORE, client_id, client_secret))

    defs = {e["node"]["key"]: e["node"]["type"]["name"]
            for e in admin.query(DEFINITIONS)["metafieldDefinitions"]["edges"]}
    print("custom product metafield definitions:", defs)
    if defs.get(KEY) != MF_TYPE:
        sys.exit(f"definition {KEY} is {defs.get(KEY)!r}, expected {MF_TYPE!r}")

    todo, skipped, unparsed = [], 0, []
    cursor = None
    while True:
        conn = admin.query(PRODUCTS, {"cursor": cursor})["products"]
        for e in conn["edges"]:
            n = e["node"]
            m = FAB.search(n.get("descriptionHtml") or "")
            if not m:
                unparsed.append(n["handle"])
                continue
            value = clean(m.group(1))
            if ((n.get("metafield") or {}).get("value")) == value:
                skipped += 1
                continue
            todo.append({"ownerId": n["id"], "namespace": NAMESPACE,
                         "key": KEY, "type": MF_TYPE, "value": value})
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]

    print(f"to write: {len(todo)}  already correct: {skipped}  "
          f"no Fabric line: {len(unparsed)}")
    if unparsed:
        print("  unparsed:", unparsed[:20])
    for m in todo[:5]:
        print("  sample:", m["value"])

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


if __name__ == "__main__":
    main()
