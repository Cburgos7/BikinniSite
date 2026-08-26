#!/usr/bin/env python3
"""Produce a ready-to-send Elegant Moments order email for given SKUs.

WHY THIS EXISTS
---------------
Until the Flow workflow is switched on, orders go to the supplier by hand. This
renders the *same* template Flow will use, so a manual order and an automated
one are byte-for-byte identical in format — the person at Elegant Moments keying
them sees one consistent layout from day one, and any formatting problem shows
up now rather than after go-live.

It also removes the chance of hand-typing the wrong style number, which is the
expensive mistake here: SKU 2990BP is style 2990, and SKU L2316XP is style
L2316X. The style comes from the same supplier data the automation uses.

USAGE
-----
    # cheapest item in the catalogue, shipped to the address in ship_to.json
    python render_order.py --sku 2990BP

    # several lines, quantities, explicit reference
    python render_order.py --sku 2990BP --sku 2472:2 --ref TEST-001

    # refresh the local variant snapshot from the live store first
    python render_order.py --sku 2990BP --refresh

CONFIGURATION
-------------
Reads order_config.json beside this script: the Elegant Moments account number
and the ship-to address. Copy order_config.example.json and fill it in.

**That file is gitignored and must stay that way — this repo is public on
GitHub.** The account number identifies us to the supplier's billing, and the
address is a real one.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUP = HERE.parent
TEMPLATE = HERE / "supplier-order-email.liquid"
INVENTORY = SUP / "source" / "liveinventory.csv"
SNAPSHOT = SUP / "out" / "live_variants_full.json"
CONFIG = HERE / "order_config.json"

sys.path.insert(0, str(HERE))
from render_test import render  # noqa: E402  (the Liquid subset interpreter)

PLACEHOLDER_ADDRESS = {
    "firstName": "«FIRST NAME»", "lastName": "«LAST NAME»", "company": "",
    "address1": "«STREET ADDRESS»", "address2": "",
    "city": "«CITY»", "provinceCode": "«ST»", "zip": "«ZIP»",
    "countryCodeV2": "US", "phone": "«PHONE»",
}

VARIANT_QUERY = """
query($cursor: String) {
  productVariants(first: 250, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      sku title price inventoryQuantity availableForSale
      selectedOptions { name value }
      metafield(namespace: "custom", key: "supplier_style") { value }
      product { title handle status }
    }
  }
}
"""


def refresh():
    sys.path.insert(0, str(SUP))
    import os
    import push_products as pp

    pp.load_env_file(SUP / ".env")
    cid, sec = os.environ.get("SHOPIFY_CLIENT_ID"), os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (cid and sec):
        sys.exit(f"Set SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET or put them in {SUP / '.env'}")
    admin = pp.Admin(pp.STORE, pp.mint_token(pp.STORE, cid, sec))
    nodes, cursor = [], None
    while True:
        conn = admin.query(VARIANT_QUERY, {"cursor": cursor})["productVariants"]
        nodes += conn["nodes"]
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(nodes, indent=1), encoding="utf-8")
    print(f"refreshed {len(nodes)} variants", file=sys.stderr)


def load_variants():
    if not SNAPSHOT.exists():
        sys.exit(f"missing {SNAPSHOT} — rerun with --refresh")
    return {v["sku"].strip(): v
            for v in json.loads(SNAPSHOT.read_text(encoding="utf-8"))}


def load_inventory():
    if not INVENTORY.exists():
        return {}
    with INVENTORY.open(encoding="utf-8-sig", newline="") as fh:
        return {r["SKU"].strip(): r for r in csv.DictReader(fh)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sku", action="append", required=True, metavar="SKU[:QTY]",
                    help="repeatable; QTY defaults to 1")
    ap.add_argument("--ref", default="MANUAL-001", help="our order reference")
    ap.add_argument("--refresh", action="store_true",
                    help="re-pull the variant snapshot from the live store")
    args = ap.parse_args()

    if args.refresh:
        refresh()
    variants = load_variants()
    inventory = load_inventory()

    items, notes, cost = [], [], 0.0
    for spec in args.sku:
        sku, _, qty = spec.partition(":")
        sku, qty = sku.strip(), int(qty) if qty else 1
        v = variants.get(sku)
        if not v:
            sys.exit(f"SKU {sku!r} not found in the snapshot. "
                     f"Rerun with --refresh, or check the spelling.")
        style = (v.get("metafield") or {}).get("value")
        if not style:
            notes.append(f"{sku}: NO supplier_style metafield — run "
                         f"scripts/backfill-supplier-style.py")
        if not v["availableForSale"] or v["product"]["status"] != "ACTIVE":
            notes.append(f"{sku}: not currently buyable on the storefront "
                         f"(status {v['product']['status']}, "
                         f"available {v['availableForSale']})")
        row = inventory.get(sku) or inventory.get(sku.split("-", 1)[0])
        if row:
            wholesale = float(row["WHOLESALE_PRICE"])
            cost += wholesale * qty
            if int(row["QTY_AVAILABLE"]) < qty:
                notes.append(f"{sku}: supplier shows only "
                             f"{row['QTY_AVAILABLE']} available")
            if style and row["STYLE"].strip() != style:
                notes.append(f"{sku}: metafield style {style} disagrees with "
                             f"supplier STYLE {row['STYLE']} — DO NOT SEND")
        items.append({
            "sku": sku, "quantity": qty,
            "product": {"title": v["product"]["title"]},
            "variant": {
                "title": v["title"],
                "selectedOptions": v["selectedOptions"],
                "metafields": {"custom": {"supplier_style": style or ""}},
            },
        })

    address = dict(PLACEHOLDER_ADDRESS)
    account, sender = None, None
    if CONFIG.exists():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        address.update(cfg.get("ship_to") or {})
        account = (cfg.get("account_number") or "").strip() or None
        sender = (cfg.get("sender_email") or "").strip() or None
        if not account:
            notes.append(f"{CONFIG.name} has no account_number — the supplier "
                         f"cannot bill the order without it")
    else:
        notes.append(f"no {CONFIG.name} — account number and address left as "
                     f"placeholders. Copy order_config.example.json")

    scope = {"order": {"name": args.ref, "lineItems": items,
                       "shippingAddress": address}}
    if account:
        scope["account"] = account
    body = render(TEMPLATE.read_text(encoding="utf-8"), scope)

    print("=" * 62)
    if sender:
        print("FROM:    %s" % sender)
    print("TO:      dropship@elegantmomentslingerie.com")
    print("SUBJECT: Drop-ship order %s — Velvet Tide" % args.ref)
    print("=" * 62)
    print(body)
    print("=" * 62)
    print("Goods cost: $%.2f  +  $3.50 drop-ship fee  +  shipping ($4-12 est.)"
          % cost)
    print("            = roughly $%.2f to $%.2f charged to the card on file"
          % (cost + 3.50 + 4, cost + 3.50 + 12))
    if notes:
        print("\nCHECK BEFORE SENDING:")
        for n in notes:
            print("  !", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
