/**
 * ga4.js
 * GA4 enhanced e-commerce event helpers for Soleil Noir.
 *
 * Imports getInfluencerCode from ref-capture.js — do NOT read location.search
 * or sessionStorage directly here; all referral state flows through ref-capture.js.
 *
 * Events implemented:
 *   - view_item         (product pages, on DOMContentLoaded)
 *   - view_item_list    (collection pages, on DOMContentLoaded)
 *   - select_item       (product card click, via event delegation on document)
 *   - add_to_cart       (exported trackAddToCart — called by pdp.js)
 *   - begin_checkout    (exported trackBeginCheckout — called by cart-drawer.js)
 *
 * NOTE — purchase event:
 *   The purchase event requires Liquid variables only available on the order
 *   status page ({{ checkout.order_id }}, {{ checkout.total_price | money_without_currency }},
 *   {{ checkout.line_items }}). Add the following block to
 *   Shopify Admin → Settings → Checkout → Order status page — Additional scripts:
 *
 *   <script>
 *     if (typeof gtag !== 'undefined') {
 *       gtag('event', 'purchase', {
 *         transaction_id: '{{ checkout.order_id }}',
 *         value: {{ checkout.total_price | money_without_currency }},
 *         currency: 'USD',
 *         items: [
 *           {% for line in checkout.line_items %}
 *           {
 *             item_id: '{{ line.variant_id }}',
 *             item_name: {{ line.title | json }},
 *             price: {{ line.price | money_without_currency }},
 *             quantity: {{ line.quantity }}
 *           }{% unless forloop.last %},{% endunless %}
 *           {% endfor %}
 *         ]
 *       });
 *     }
 *   </script>
 */

import { getInfluencerCode } from './ref-capture.js';

/**
 * Safe gtag wrapper — guards against ad blockers or disabled GA4 setting.
 * @param {...*} args
 */
const safeGtag = (...args) => {
  if (typeof gtag !== 'undefined') {
    gtag(...args);
  }
};

/**
 * Parse the ga4-page-data JSON island injected by theme.liquid.
 * Returns an empty object if the tag is missing or JSON is malformed.
 * @returns {Object}
 */
const readPageData = () => {
  try {
    const el = document.getElementById('ga4-page-data');
    return el ? JSON.parse(el.textContent) : {};
  } catch (e) {
    console.warn('[ga4] Could not parse ga4-page-data:', e);
    return {};
  }
};

/**
 * Set the influencer_code custom dimension so it attaches to all subsequent hits.
 * Called once on DOMContentLoaded.
 */
const setInfluencerDimension = () => {
  const code = getInfluencerCode();
  if (code) {
    safeGtag('set', { influencer_code: code });
  }
};

/**
 * Fire view_item on product page load.
 * @param {Object} pageData - parsed ga4-page-data
 */
const fireViewItem = (pageData) => {
  if (pageData.pageType !== 'product' || !pageData.product) return;

  const p = pageData.product;
  const price = parseFloat(p.price) || 0;

  safeGtag('event', 'view_item', {
    currency: 'USD',
    value: price,
    items: [
      {
        item_id: String(p.id),
        item_name: p.name,
        item_brand: p.brand,
        item_category: p.category,
        item_variant: String(p.variant),
        price: price,
      },
    ],
  });
};

/**
 * Fire view_item_list on collection page load.
 * @param {Object} pageData - parsed ga4-page-data
 */
const fireViewItemList = (pageData) => {
  if (pageData.pageType !== 'collection' || !pageData.collection) return;

  const c = pageData.collection;
  const items = (c.products || []).map((p) => ({
    item_id: String(p.id),
    item_name: p.name,
    item_category: p.category,
    price: parseFloat(p.price) || 0,
    index: p.position,
    item_list_id: String(c.id),
    item_list_name: c.name,
  }));

  safeGtag('event', 'view_item_list', {
    item_list_id: String(c.id),
    item_list_name: c.name,
    items,
  });
};

/**
 * Wire select_item via event delegation on document.
 * Handles AJAX-loaded product cards — delegate on document, match [data-product-card].
 */
const initSelectItem = () => {
  document.addEventListener('click', (e) => {
    const card = e.target.closest('[data-product-card]');
    if (!card) return;

    const itemId = card.dataset.productId || '';
    const itemName = card.dataset.productTitle || '';
    const itemPrice = parseFloat(card.dataset.productPrice) || 0;
    const listId = card.dataset.listId || '';
    const listName = card.dataset.listName || '';
    const index = parseInt(card.dataset.productIndex, 10) || 0;

    safeGtag('event', 'select_item', {
      item_list_id: listId,
      item_list_name: listName,
      items: [
        {
          item_id: itemId,
          item_name: itemName,
          price: itemPrice,
          index,
          item_list_id: listId,
          item_list_name: listName,
        },
      ],
    });
  });
};

/**
 * Fire add_to_cart from the Shopify /cart/add.js response.
 * Called by pdp.js after a successful cart add.
 *
 * @param {Object} cartItem - response from /cart/add.js
 */
export const trackAddToCart = (cartItem) => {
  if (!cartItem) return;

  const price = (cartItem.final_price || cartItem.price || 0) / 100;

  safeGtag('event', 'add_to_cart', {
    currency: 'USD',
    value: price * (cartItem.quantity || 1),
    items: [
      {
        item_id: String(cartItem.variant_id || cartItem.id),
        item_name: cartItem.product_title || cartItem.title || '',
        item_variant: cartItem.variant_title || '',
        price: price,
        quantity: cartItem.quantity || 1,
      },
    ],
  });
};

/**
 * Fire begin_checkout from the current cart state.
 * Called by cart-drawer.js when the checkout button is clicked.
 *
 * @param {Object} cartData - response from /cart.js
 */
export const trackBeginCheckout = (cartData) => {
  if (!cartData) return;

  const value = (cartData.total_price || 0) / 100;
  const items = (cartData.items || []).map((item) => ({
    item_id: String(item.variant_id || item.id),
    item_name: item.product_title || item.title || '',
    item_variant: item.variant_title || '',
    price: (item.final_price || item.price || 0) / 100,
    quantity: item.quantity || 1,
  }));

  safeGtag('event', 'begin_checkout', {
    currency: 'USD',
    value,
    items,
  });
};

/**
 * Module init — runs on DOMContentLoaded.
 */
document.addEventListener('DOMContentLoaded', () => {
  const pageData = readPageData();

  setInfluencerDimension();
  fireViewItem(pageData);
  fireViewItemList(pageData);
  initSelectItem();
});
