# Phase 06 — Integrations: Context and Decisions

## Integration Summary

Phase 6 wires four third-party services into the Soleil Noir theme. All API keys and
account IDs use placeholder values in the codebase. The owner must replace them before
go-live.

Run `grep -r "PLACEHOLDER" config/settings_data.json` before launch to confirm all real
values are in place.

---

## Theme Settings Required (config/settings_data.json)

| Setting key | Placeholder value | Where to find real value |
|---|---|---|
| `klaviyo_company_id` | `KLAVIYO_COMPANY_ID_PLACEHOLDER` | Klaviyo → Account → API Keys → "Public API Key" (6-char alphanumeric) |
| `ga4_measurement_id` | `G-XXXXXXXXXX` | Google Analytics → Admin → Data Streams → Web stream → Measurement ID |
| `cloudinary_cloud_name` | `CLOUDINARY_CLOUD_NAME_PLACEHOLDER` | Cloudinary dashboard → top-left cloud name |
| `upromote_merchant_id` | `UPROMOTE_MERCHANT_ID_PLACEHOLDER` | UpPromote → Settings → Integration → Merchant ID |

---

## Klaviyo

### Flows requiring no additional theme code

The following flows are configured entirely in the Klaviyo dashboard. The `klaviyo.js`
snippet + `identify()` call in `assets/klaviyo.js` is all the theme integration needed.

| Flow | Trigger | Notes |
|---|---|---|
| Welcome Series | List subscribe (signup form) | 3-email sequence; 24h / 48h / 72h delays |
| Post-Purchase | Shopify order placed metric | Trigger: `Placed Order`; delay 1 day |
| Win-Back | No purchase in 90 days | Segment filter on `Last Order Date` |
| VIP Early Access | VIP segment join | Segment: total spend > $300 or 3+ orders |

### Abandoned Cart flow

Trigger: `Added to Cart` metric — fired by `assets/klaviyo-flows.js` via `trackAddedToCart()`.
Flow exits if `Started Checkout` or `Placed Order` occurs within 4 hours.
Recommended delays: 1 hour, 24 hours.

### Back-in-Stock

Wired via Klaviyo Client API (`/client/back-in-stock-subscriptions/`) in
`assets/klaviyo-flows.js`. Uses Klaviyo's built-in back-in-stock notification flow.

### TCPA SMS Compliance

- SMS opt-in is managed entirely by Klaviyo's form builder — explicit checkbox is
  required (not pre-checked) with the following consent language:
  > "By checking this box I consent to receive marketing text messages from [Brand Name]
  > at the number provided. Consent is not a condition of purchase. Message and data rates
  > may apply. Reply STOP to unsubscribe."
- This language must be set in the Klaviyo form editor, not in theme code.
- Quiet hours (8pm–8am local) must be enforced in Klaviyo SMS flow settings.

---

## UpPromote

### Commission structure (configure in UpPromote dashboard)

| Tier | Rate | Qualification |
|---|---|---|
| Standard | 10% | Default for all new affiliates |
| Silver | 12% | Set manually or by GMV threshold |
| Gold | 15% | Set manually or by GMV threshold |
| Ambassador | Custom | Individual negotiation |
| Customer Referral | 5% | Customer referral program |

### Fraud rules (configure in UpPromote → Settings → Fraud Detection)

- Self-referral block: enabled
- IP clustering threshold: 3 conversions per IP per 24 hours
- Conversion hold: 14 days before commission is approved

### Affiliate signup

Already embedded in `sections/page-affiliates.liquid` via UpPromote iframe. No changes
in Phase 6.

---

## GA4

### UTM convention

| Parameter | Purpose | Example |
|---|---|---|
| `utm_source` | Traffic source | `instagram`, `email`, `tiktok` |
| `utm_medium` | Channel | `social`, `cpc`, `influencer` |
| `utm_campaign` | Campaign name | `summer-drop-2026`, `ambassador-jane` |
| `utm_content` | Ad variant | `reel-1`, `story-a` |
| `ref` | Affiliate code | same value as UpPromote referral code |

The `influencer_code` custom dimension in GA4 is populated from `utm_campaign` or `ref`
param (whichever is present; `ref` takes precedence). Must be registered in GA4 Admin →
Custom Definitions → Custom Dimensions as a "Session"-scoped dimension.

### GA4 purchase event — Shopify Additional Scripts

Add the following to Shopify Admin → Settings → Checkout → Additional Scripts.
This fires only on the order confirmation page and only on first access.

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

---

## Cloudinary

Transform pattern: `https://res.cloudinary.com/{cloud_name}/image/fetch/f_auto,q_auto,w_{width}/{shopify_cdn_url}`

- `f_auto` — serves WebP to modern browsers, JPEG to older ones
- `q_auto` — Cloudinary perceptual quality compression (typically saves 30–60% vs original)
- `w_{width}` — resize to requested width; height auto-scales

Fetch URL delivery requires the Shopify CDN domain to be allowlisted in Cloudinary
Settings → Security → Allowed fetch domains. Add: `cdn.shopify.com`

When `cloudinary_cloud_name` is blank in theme settings, all images fall back to direct
Shopify CDN URLs — no broken images during initial setup.
