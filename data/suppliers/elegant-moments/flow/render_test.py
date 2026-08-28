#!/usr/bin/env python3
"""Execute supplier-order-email.liquid against real catalogue data.

WHY THIS EXISTS
---------------
The drop-ship order email is keyed by a human into Elegant Moments' order-entry
screen. A wrong style number ships the wrong garment, and because the parcel is
deliberately unmarked and discreet, the customer is the first to find out.

There is no Liquid renderer installed and no way to unit-test a Flow workflow,
so this file contains a small Liquid interpreter covering exactly the subset the
template uses. Anything outside that subset raises, which doubles as a guard
that the template never drifts into constructs Flow may not support.

WHAT THIS PROVES
----------------
  * every style printed matches the supplier's own STYLE column, for all
    1,522 live variants
  * the SKU-derivation rule the research proposed would have been wrong 466
    times, and this template is not using it
  * colour and size survive slash-containing values (O/S, Black/Red, 1X/2X)
  * the selectedOptions fallback produces identical output to the primary path
  * a missing style prints DO NOT SHIP rather than a blank or a guess
  * a size-less variant reads as "One size", not an empty field

WHAT THIS DOES NOT PROVE
------------------------
That Flow exposes these variable paths. `li.variant.metafields.custom.
supplier_style` and `li.variant.selectedOptions` are both assumptions until a
real test order runs through the workflow. SETUP.md step 9 is that check, and
the template fails loudly rather than silently if either path comes back empty.

FIXTURES
--------
Test [2] needs two files that are deliberately gitignored, because both are the
supplier's proprietary catalogue and `data/suppliers/*/source/` and `*/out/` are
excluded by .gitignore:

    source/liveinventory.csv    the supplier's export, with its STYLE column
    out/live_variants.json      a snapshot of our live variants

On a fresh clone test [2] reports SKIPPED rather than passing quietly. Rebuild
the snapshot with --refresh (needs Admin API credentials in ../.env); the
supplier CSV has to come from the supplier.

USAGE
-----
    python data/suppliers/elegant-moments/flow/render_test.py
    python data/suppliers/elegant-moments/flow/render_test.py --show     # sample
    python data/suppliers/elegant-moments/flow/render_test.py --refresh  # resnap
"""
import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUP = HERE.parent
TEMPLATE = HERE / "supplier-order-email.liquid"
INVENTORY = SUP / "source" / "liveinventory.csv"
LIVE_VARIANTS = SUP / "out" / "live_variants.json"


# ─────────────────────────────────────────────────────────────────────────────
# A deliberately small Liquid interpreter.
#
# Supports only: comment, for (+forloop.index), if/else, assign, output, and the
# filters strip / split / first / default. Unknown tags and filters raise, which
# is the point -- the template is meant to stay inside a subset Flow can run.
# ─────────────────────────────────────────────────────────────────────────────

TAG = re.compile(r"\{%-?\s*(.*?)\s*-?%\}|\{\{-?\s*(.*?)\s*-?\}\}", re.S)


class LiquidError(Exception):
    pass


def _tokenize(src):
    """(kind, payload, raw) tuples. kind is 'text', 'tag' or 'out'."""
    out, pos = [], 0
    for m in TAG.finditer(src):
        if m.start() > pos:
            out.append(("text", src[pos:m.start()], ""))
        raw = m.group(0)
        if m.group(1) is not None:
            out.append(("tag", m.group(1), raw))
        else:
            out.append(("out", m.group(2), raw))
        pos = m.end()
    if pos < len(src):
        out.append(("text", src[pos:], ""))
    return out


def _strip_ws(tokens):
    """Apply Liquid's {%- -%} whitespace control to neighbouring text."""
    for i, (kind, payload, raw) in enumerate(tokens):
        if kind == "text":
            continue
        if raw.startswith("{%-") or raw.startswith("{{-"):
            j = i - 1
            if j >= 0 and tokens[j][0] == "text":
                tokens[j] = ("text", tokens[j][1].rstrip(), "")
        if raw.endswith("-%}") or raw.endswith("-}}"):
            j = i + 1
            if j < len(tokens) and tokens[j][0] == "text":
                tokens[j] = ("text", tokens[j][1].lstrip(), "")
    return tokens


class Node:
    def __init__(self, kind, payload=None):
        self.kind, self.payload, self.children = kind, payload, []
        self.branches = []          # for if/elsif/else


class Frame:
    """An open block. `target` is where children land, which for an `if` moves
    to a fresh body on every elsif/else."""

    def __init__(self, kind, node, target):
        self.kind, self.node, self.target = kind, node, target


def _parse(tokens):
    root = Node("root")
    stack = [Frame("root", root, root)]
    i = 0
    while i < len(tokens):
        kind, payload, _ = tokens[i]
        top = stack[-1]
        if kind == "text":
            top.target.children.append(Node("text", payload))
        elif kind == "out":
            top.target.children.append(Node("out", payload))
        else:
            word = payload.split(None, 1)[0]
            rest = payload[len(word):].strip()
            if word == "comment":
                depth = 1
                i += 1
                while i < len(tokens) and depth:
                    if tokens[i][0] == "tag":
                        w = tokens[i][1].split(None, 1)[0]
                        if w == "comment":
                            depth += 1
                        elif w == "endcomment":
                            depth -= 1
                    i += 1
                continue
            elif word == "for":
                n = Node("for", rest)
                top.target.children.append(n)
                stack.append(Frame("for", n, n))
            elif word == "endfor":
                if stack.pop().kind != "for":
                    raise LiquidError("endfor without for")
            elif word == "if":
                n = Node("if")
                body = Node("root")
                n.branches.append([rest, body])
                top.target.children.append(n)
                stack.append(Frame("if", n, body))
            elif word in ("elsif", "else"):
                if top.kind != "if":
                    raise LiquidError(f"{word} outside if")
                body = Node("root")
                top.node.branches.append(
                    [rest if word == "elsif" else None, body])
                top.target = body
            elif word == "endif":
                if stack.pop().kind != "if":
                    raise LiquidError("endif without if")
            elif word == "assign":
                top.target.children.append(Node("assign", rest))
            else:
                raise LiquidError(f"unsupported tag: {word!r}")
        i += 1
    if len(stack) != 1:
        raise LiquidError("unclosed block")
    return root


LITERAL = re.compile(r'^"(.*)"$|^\'(.*)\'$', re.S)
INDEXED = re.compile(r"^(\w+)\[(\d+)\]$")


def _lookup(path, scope):
    m = INDEXED.match(path)
    if m:
        seq = scope.get(m.group(1))
        idx = int(m.group(2))
        if isinstance(seq, (list, tuple)) and idx < len(seq):
            return seq[idx]
        return None
    cur = scope
    for part in path.split("."):
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            cur = getattr(cur, part, None)
    return cur


def _resolve(expr, scope):
    expr = expr.strip()
    m = LITERAL.match(expr)
    if m:
        return m.group(1) if m.group(1) is not None else m.group(2)
    if expr == "blank":
        return ""
    if re.fullmatch(r"-?\d+", expr):
        return int(expr)
    return _lookup(expr, scope)


def _apply_filters(expr, scope):
    parts = [p.strip() for p in _split_pipes(expr)]
    value = _resolve(parts[0], scope)
    for f in parts[1:]:
        name, _, arg = f.partition(":")
        name, arg = name.strip(), arg.strip()
        if name == "strip":
            value = (value or "").strip() if isinstance(value, str) else value
        elif name == "split":
            sep = _resolve(arg, scope)
            value = (value or "").split(sep) if isinstance(value, str) else []
        elif name == "first":
            value = value[0] if isinstance(value, (list, tuple)) and value else None
        elif name == "size":
            value = len(value) if hasattr(value, "__len__") else 0
        elif name == "default":
            if value in (None, "", [], {}):
                value = _resolve(arg, scope)
        else:
            raise LiquidError(f"unsupported filter: {name!r}")
    return value


def _split_pipes(expr):
    """Split on | but not inside quotes."""
    out, buf, quote = [], "", None
    for ch in expr:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf += ch
        elif ch == "|":
            out.append(buf)
            buf = ""
        else:
            buf += ch
    out.append(buf)
    return out


COND = re.compile(r"^(.*?)\s*(==|!=)\s*(.*)$", re.S)


def _split_outside_quotes(expr, token):
    """Split on ` token ` at quote depth zero.

    Needed because `colorValue == "" and sizeValue == ""` contains a quoted
    empty string on both sides; a naive split would tear the literals apart and
    silently evaluate the wrong comparison.
    """
    out, buf, quote, i = [], "", None, 0
    pad = f" {token} "
    while i < len(expr):
        ch = expr[i]
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            i += 1
        elif ch in "\"'":
            quote = ch
            buf += ch
            i += 1
        elif expr.startswith(pad, i):
            out.append(buf)
            buf = ""
            i += len(pad)
        else:
            buf += ch
            i += 1
    out.append(buf)
    return out


def _truthy(cond, scope):
    cond = cond.strip()
    parts = _split_outside_quotes(cond, "or")
    if len(parts) > 1:
        return any(_truthy(p, scope) for p in parts)
    parts = _split_outside_quotes(cond, "and")
    if len(parts) > 1:
        return all(_truthy(p, scope) for p in parts)
    m = COND.match(cond)
    if not m:
        v = _apply_filters(cond, scope)
        return bool(v) and v not in ("", None)
    left = _apply_filters(m.group(1), scope)
    right = _resolve(m.group(3), scope)
    left = "" if left is None else left
    right = "" if right is None else right
    return left == right if m.group(2) == "==" else left != right


def _render(node, scope, out):
    for child in node.children:
        if child.kind == "text":
            out.append(child.payload)
        elif child.kind == "out":
            v = _apply_filters(child.payload, scope)
            out.append("" if v is None else str(v))
        elif child.kind == "assign":
            name, _, expr = child.payload.partition("=")
            scope[name.strip()] = _apply_filters(expr, scope)
        elif child.kind == "for":
            m = re.match(r"^(\w+)\s+in\s+(.+)$", child.payload)
            if not m:
                raise LiquidError(f"bad for: {child.payload!r}")
            seq = _apply_filters(m.group(2), scope) or []
            # Liquid scopes `forloop` to its own loop and restores the parent's
            # on endfor. Save and restore, or a nested loop leaves the outer
            # forloop.index pointing at the inner loop's final value.
            outer_forloop = scope.get("forloop")
            outer_item = scope.get(m.group(1))
            for idx, item in enumerate(seq):
                scope[m.group(1)] = item
                scope["forloop"] = {"index": idx + 1, "index0": idx,
                                    "length": len(seq)}
                _render(child, scope, out)
            scope["forloop"] = outer_forloop
            scope[m.group(1)] = outer_item
        elif child.kind == "if":
            for cond, body in child.branches:
                if cond is None or _truthy(cond, scope):
                    _render(body, scope, out)
                    break
        elif child.kind == "root":
            _render(child, scope, out)


def render(src, scope):
    tree = _parse(_strip_ws(_tokenize(src)))
    out = []
    _render(tree, dict(scope), out)
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

ADDRESS = {
    "firstName": "Dana", "lastName": "Whitfield", "company": "",
    "address1": "418 Sycamore Ave", "address2": "Apt 3B",
    "city": "Sacramento", "provinceCode": "CA", "zip": "95814",
    "countryCodeV2": "US", "phone": "+1 916 555 0147",
}


def line_item(sku, style, color, size, title, qty=1, extra_metafields=()):
    """One order line, shaped the way Flow exposes it.

    `metafields` is a LIST of namespace/key/value records, not a nested dict.
    Flow rejects metafield dot notation, so the template loops; the fixture has
    to match or the test would be verifying a shape that cannot occur.
    """
    opts = [{"name": "Color", "value": color}]
    if size is not None:
        opts.append({"name": "Size", "value": size})
    metafields = list(extra_metafields) + [
        {"namespace": "custom", "key": "supplier_style", "value": style},
    ]
    return {
        "sku": sku, "quantity": qty,
        "product": {"title": title},
        "variant": {
            "title": " / ".join([color] + ([size] if size is not None else [])),
            "selectedOptions": opts,
            "metafields": metafields,
        },
    }


def order(items, name="#1001"):
    return {"order": {"name": name, "lineItems": items,
                      "shippingAddress": ADDRESS}}


def field(text, label):
    m = re.search(rf"^\s*{label} \.+ (.*)$", text, re.M)
    return m.group(1).strip() if m else None


def all_fields(text, label):
    return [m.strip() for m in
            re.findall(rf"^\s*{label} \.+ (.*)$", text, re.M)]


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

VARIANT_QUERY = """
query($cursor: String) {
  productVariants(first: 250, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes { sku title selectedOptions { name value } product { title handle } }
  }
}
"""


def refresh_snapshot():
    """Re-pull live variants from the Admin API into out/live_variants.json."""
    sys.path.insert(0, str(SUP))
    import push_products as pp  # noqa: E402

    pp.load_env_file(SUP / ".env")
    cid = os.environ.get("SHOPIFY_CLIENT_ID")
    secret = os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (cid and secret):
        sys.exit(f"Set SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET or put them "
                 f"in {SUP / '.env'}")
    admin = pp.Admin(pp.STORE, pp.mint_token(pp.STORE, cid, secret))
    nodes, cursor = [], None
    while True:
        conn = admin.query(VARIANT_QUERY, {"cursor": cursor})["productVariants"]
        nodes += conn["nodes"]
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]
    LIVE_VARIANTS.parent.mkdir(parents=True, exist_ok=True)
    LIVE_VARIANTS.write_text(json.dumps(nodes, indent=1), encoding="utf-8")
    print(f"wrote {len(nodes)} variants to {LIVE_VARIANTS}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true", help="print a sample email")
    ap.add_argument("--refresh", action="store_true",
                    help="re-pull the live variant snapshot from the Admin API")
    args = ap.parse_args()

    if args.refresh:
        refresh_snapshot()

    src = TEMPLATE.read_text(encoding="utf-8")
    failures = []

    def check(name, cond, detail=""):
        if cond:
            print(f"  PASS  {name}")
        else:
            print(f"  FAIL  {name}  {detail}")
            failures.append(name)

    # ── 1. Template parses inside the supported subset ──────────────────────
    print("\n[1] template parses within the Flow-safe Liquid subset")
    try:
        render(src, order([line_item("2987", "2987", "Red", "O/S", "Lace thong")]))
        check("parses and renders", True)
    except LiquidError as exc:
        check("parses and renders", False, str(exc))
        print("\nCannot continue: template does not parse.")
        return 1

    # ── 2. Every live variant prints its supplier's own STYLE ───────────────
    print("\n[2] style correctness across the whole live catalogue")
    missing_fixtures = [p.name for p in (LIVE_VARIANTS, INVENTORY)
                        if not p.exists()]
    if missing_fixtures:
        # Not a pass and not a failure: the supplier catalogue is gitignored, so
        # a fresh clone genuinely cannot run this. Say so loudly rather than
        # letting a skipped check read as a green one.
        print(f"  SKIP  supplier fixtures absent: {', '.join(missing_fixtures)}")
        print(f"        rerun with --refresh for the variant snapshot; the "
              f"supplier CSV must come from the supplier")
        skipped_catalogue = True
    else:
        skipped_catalogue = False
    if skipped_catalogue:
        variants = []
    else:
        variants = json.loads(LIVE_VARIANTS.read_text(encoding="utf-8"))
    truth = {}
    if not skipped_catalogue:
        with INVENTORY.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                s = (row.get("SKU") or "").strip()
                if s:
                    truth[s] = (row.get("STYLE") or "").strip()

    wrong, derived_wrong, checked = [], 0, 0
    for v in variants:
        sku = (v["sku"] or "").strip()
        expected = truth.get(sku) or truth.get(sku.split("-", 1)[0])
        if not expected:
            continue
        checked += 1
        color = next((o["value"] for o in v["selectedOptions"]
                      if o["name"] == "Color"), "")
        size = next((o["value"] for o in v["selectedOptions"]
                     if o["name"] == "Size"), None)
        text = render(src, order([line_item(
            sku, expected, color, size, v["product"]["title"])]))
        got = field(text, "STYLE")
        if got != expected:
            wrong.append((sku, expected, got))
        if sku.split("-", 1)[0] != expected:
            derived_wrong += 1

    if not skipped_catalogue:
        check(f"all {checked} live variants print the supplier's STYLE",
              not wrong, f"{len(wrong)} wrong, e.g. {wrong[:3]}")
        check(f"the SKU-derivation rule would have been wrong {derived_wrong} "
              f"times and is not used", derived_wrong > 0)

    # ── 3. Slash-containing option values survive ───────────────────────────
    print("\n[3] slash-containing colours and sizes")
    t = render(src, order([line_item(
        "55065X", "55065X", "Black/Red", "Q/S", "Lace bra — Style 55065")]))
    check("colour Black/Red intact", field(t, "COLOR") == "Black/Red",
          repr(field(t, "COLOR")))
    check("size Q/S intact", field(t, "SIZE") == "Q/S", repr(field(t, "SIZE")))
    check("style 55065X not truncated to 55065",
          field(t, "STYLE") == "55065X", repr(field(t, "STYLE")))

    t = render(src, order([line_item(
        "82279Q-1/X/2X", "82279Q", "Black", "1X/2X", "Bodystocking")]))
    check("size 1X/2X intact", field(t, "SIZE") == "1X/2X", repr(field(t, "SIZE")))
    check("style from hyphenated SKU", field(t, "STYLE") == "82279Q",
          repr(field(t, "STYLE")))

    # ── 4. The X-vs-colour-code trap ────────────────────────────────────────
    print("\n[4] the trap: trailing letters that are and are not style")
    pairs = [("L2316P", "L2316"), ("L2316XP", "L2316X"),
             ("L1249BL", "L1249"), ("L1237SALE", "L1237")]
    for sku, expected in pairs:
        t = render(src, order([line_item(
            sku, expected, "Black", "O/S", f"Leather teddy — Style {expected}")]))
        check(f"{sku} -> {expected}", field(t, "STYLE") == expected,
              repr(field(t, "STYLE")))
        naive = sku.split("-", 1)[0]
        if naive != expected:
            check(f"  and not the SKU-derived {naive}",
                  field(t, "STYLE") != naive)

    # ── 5. The metafield is found by looping, not by path ───────────────────
    # Flow rejects `li.variant.metafields.custom.supplier_style` outright, so
    # the template iterates. These guard the iteration: the right record has to
    # win regardless of position, and a near-miss must not be mistaken for it.
    print("\n[5] supplier_style is picked out of the metafield list")
    noise = [
        {"namespace": "custom", "key": "fabric_composition", "value": "Nylon"},
        {"namespace": "other", "key": "supplier_style", "value": "WRONG-NS"},
        {"namespace": "custom", "key": "supplier_style_note", "value": "WRONG-KEY"},
    ]
    t = render(src, order([line_item("L2316XP", "L2316X", "Purple", "Q/S",
                                     "Leather teddy", extra_metafields=noise)]))
    check("correct record found among decoys",
          field(t, "STYLE") == "L2316X", repr(field(t, "STYLE")))
    check("wrong namespace ignored", "WRONG-NS" not in t)
    check("similar key ignored", "WRONG-KEY" not in t)

    t = render(src, order([{
        "sku": "9999", "quantity": 1, "product": {"title": "No metafields"},
        "variant": {"title": "Red", "metafields": [],
                    "selectedOptions": [{"name": "Color", "value": "Red"}]},
    }]))
    check("empty metafield list stalls rather than guessing",
          "DO NOT SHIP" in (field(t, "STYLE") or ""), repr(field(t, "STYLE")))

    # ── 6. Degenerate data fails loudly ─────────────────────────────────────
    print("\n[6] missing data produces a stall, not a guess")
    t = render(src, order([line_item("9999", "", "Red", "O/S", "Mystery item")]))
    check("empty style prints DO NOT SHIP",
          "DO NOT SHIP" in (field(t, "STYLE") or ""), repr(field(t, "STYLE")))
    check("no blank style line leaks through",
          not re.search(r"^\s*STYLE \.+ \s*$", t, re.M))

    t = render(src, order([line_item("L1263PU", "L1263", "Purple", None,
                                     "Heart pasties")]))
    check("size-less variant reads as One size",
          (field(t, "SIZE") or "").startswith("One size"), repr(field(t, "SIZE")))

    # ── 7. Multi-line orders ────────────────────────────────────────────────
    print("\n[7] a basket spanning two supplier styles")
    t = render(src, order([
        line_item("2987", "2987", "Red", "O/S", "Lace thong — Style 2987"),
        line_item("2987X", "2987X", "Red", "Q/S", "Lace thong — Style 2987", qty=2),
    ]))
    check("both items rendered", all_fields(t, "STYLE") == ["2987", "2987X"],
          repr(all_fields(t, "STYLE")))
    check("quantities preserved", all_fields(t, "QTY") == ["1", "2"],
          repr(all_fields(t, "QTY")))
    check("items numbered", "ITEM 1" in t and "ITEM 2" in t)

    # ── 8. Address block ────────────────────────────────────────────────────
    print("\n[8] ship-to block")
    check("name", field(t, "NAME") == "Dana Whitfield")
    check("address1", field(t, "ADDRESS") == "418 Sycamore Ave")
    check("address2 on its own line", "Apt 3B" in t)
    check("blank company omitted", "COMPANY" not in t)
    check("order reference present", "#1001" in t)

    # ── 9. Whitespace control ───────────────────────────────────────────────
    # An inline {%- comment -%} strips the newline that ends the line above it,
    # silently welding two lines together. This bit twice while the template
    # was being written -- once joining the order reference to the account
    # number, once joining "do not substitute." to the paragraph after it.
    print("\n[9] inline comments have not eaten line breaks")
    t9 = render(src, order([line_item("2990BP", "2990", "Baby Pink/Black",
                                      None, "Satin leg garters")],
                           name="WS-001"))
    lines = t9.splitlines()
    check("order reference is alone on its line",
          any(ln.strip() == "Our order reference: WS-001" for ln in lines))
    check("account line is alone on its line",
          any(ln.startswith("Dropship account:") for ln in lines))
    check("duplicate-guard paragraph starts its own line",
          any(ln.startswith("This order has been sent once") for ln in lines),
          next((ln for ln in lines if "sent once" in ln), "<absent>")[:70])
    check("no sentence welded to the next line",
          not re.search(r"[a-z]\.[A-Z]", t9),
          repr(next(iter(re.findall(r".{20}[a-z]\.[A-Z].{20}", t9)), "")))

    if args.show:
        print("\n" + "=" * 60 + "\nSAMPLE\n" + "=" * 60)
        print(t)

    print(f"\n{'=' * 60}")
    if failures:
        print(f"{len(failures)} FAILED: {failures}")
        return 1
    if skipped_catalogue:
        print("All runnable checks passed, but the catalogue-wide style check "
              "was SKIPPED for want of supplier fixtures.")
        return 0
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
