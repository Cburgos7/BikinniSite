# Integration Settings — Soleil Noir Go-Live Checklist

All four integration settings live in `config/settings_data.json` under the `"current"` key.
Run `grep -r "PLACEHOLDER" config/settings_data.json` before launch to confirm every real
value is in place.

---

## Theme Settings Reference

### `klaviyo_company_id`

**Placeholder:** `KLAVIYO_COMPANY_ID_PLACEHOLDER`

**Where to find it:**
Klaviyo dashboard → Account → Settings → API Keys → "Public API Key" (6-character alphanumeric string, e.g. `AbCd12`).

**Used by:** `snippets/klaviyo.liquid` (injects `klaviyo.js?company_id=` script tag in `<head>`)

---

### `ga4_measurement_id`

**Placeholder:** `G-XXXXXXXXXX`

**Where to find it:**
Google Analytics → Admin (gear icon) → Data Streams → select your Web stream → Measurement ID (format: `G-XXXXXXXXXX`).

**Used by:** `snippets/ga4.liquid` (injects `gtag.js` script tag and config push)

---

### `cloudinary_cloud_name`

**Placeholder:** `CLOUDINARY_CLOUD_NAME_PLACEHOLDER`

**Where to find it:**
Cloudinary dashboard → top-left corner shows your cloud name (e.g. `my-store-name`).

**Additional required step:**
Allowlist your Shopify CDN domain in Cloudinary → Settings → Security → Allowed fetch domains.
Add: `cdn.shopify.com`

**Used by:** `snippets/cloudinary-image.liquid` (rewrites product image URLs to
`https://res.cloudinary.com/{cloud_name}/image/fetch/f_auto,q_auto,w_{width}/{shopify_cdn_url}`)

When `cloudinary_cloud_name` is blank, all images fall back to direct Shopify CDN URLs — no
broken images during initial setup.

---

### `upromote_merchant_id`

**Placeholder:** `UPROMOTE_MERCHANT_ID_PLACEHOLDER`

**Where to find it:**
UpPromote dashboard (upromote.io) → Settings → Integration → Merchant ID.

**Used by:** `snippets/upromote.liquid` (loads UpPromote tracking script; `assets/upromote.js`
captures `?ref=` param into sessionStorage and appends discount code to checkout URL)

---

## Klaviyo Signup Form — Form ID

The `sections/klaviyo-forms.liquid` section has a `klaviyo_form_id` block setting.

**Where to find the form ID:**
1. Klaviyo dashboard → Sign-up Forms → select your form → Edit
2. In the form editor URL, note the form ID (alphanumeric string, e.g. `XyZ123`)
3. Alternatively: Klaviyo → Sign-up Forms → click the three-dot menu → "Get embed code" — the
   form ID appears in the `data-form-id` attribute of the embed snippet

**To use:** Add a `klaviyo-forms` section to any Shopify page template via the theme editor,
then enter the form ID in the block settings.

---

## GA4 Purchase Event — Shopify Additional Scripts

This snippet must be pasted into:
**Shopify Admin → Settings → Checkout → Additional scripts**

It fires only on the order confirmation page and only on the customer's first visit (preventing
double-counting on refresh), satisfying threat T-06-15.

```liquid
{% if first_time_accessed %}
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('event', 'purchase', {
    transaction_id: '{{ order.order_number }}',
    affiliation: '{{ shop.name }}',
    value: {{ checkout.total_price | money_without_currency }},
    tax: {{ checkout.tax_price | money_without_currency }},
    shipping: {{ checkout.shipping_price | money_without_currency }},
    currency: 'USD',
    items: [
      {% for line_item in checkout.line_items %}
      {
        item_id: '{{ line_item.variant_id }}',
        item_name: '{{ line_item.title | escape }}',
        item_category: '{{ line_item.product.type | escape }}',
        price: {{ line_item.price | money_without_currency }},
        quantity: {{ line_item.quantity }}
      }{% unless forloop.last %},{% endunless %}
      {% endfor %}
    ]
  });
</script>
{% endif %}
```

**Note:** The `checkout` object is available on the order status page. The `order` object
provides `order_number`. Both are Shopify Liquid objects available only in Additional Scripts
context — not in standard theme templates.
