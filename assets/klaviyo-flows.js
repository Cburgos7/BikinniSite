/**
 * klaviyo-flows.js
 * Standalone ES module — Klaviyo behavioral track helpers.
 * Accesses window.klaviyo directly (no import from klaviyo.js) to keep coupling low.
 *
 * Exports:
 *   trackAddedToCart(cartItem)     — fires Klaviyo "Added to Cart" event
 *   subscribeBackInStock(email, variantId) — POSTs to Klaviyo BIS client API
 */

/**
 * Fire Klaviyo "Added to Cart" track event.
 * @param {object} cartItem  — Response object from Shopify /cart/add.js
 */
export function trackAddedToCart(cartItem) {
  if (!cartItem || typeof window === 'undefined') return;

  const klaviyo = window.klaviyo;
  if (!klaviyo || typeof klaviyo.track !== 'function') return;

  const imageURL =
    cartItem.featured_image?.url ||
    cartItem.featured_image?.src ||
    (cartItem.featured_image ? String(cartItem.featured_image) : '') ||
    '';

  const price = cartItem.price != null ? cartItem.price / 100 : 0;
  const compareAtPrice =
    cartItem.compare_at_price != null ? cartItem.compare_at_price / 100 : 0;

  klaviyo.track('Added to Cart', {
    ProductName: cartItem.product_title || cartItem.title || '',
    ProductID: String(cartItem.variant_id || ''),
    SKU: cartItem.sku || '',
    Categories: cartItem.product_type ? [cartItem.product_type] : [],
    ImageURL: imageURL,
    URL: cartItem.url ? `${window.location.origin}${cartItem.url}` : window.location.href,
    Brand: cartItem.vendor || '',
    Price: price,
    CompareAtPrice: compareAtPrice,
    Quantity: cartItem.quantity || 1,
  });
}

/**
 * Subscribe a visitor to Klaviyo back-in-stock notifications for a variant.
 * Uses the Klaviyo client API — requires only the public company ID.
 *
 * @param {string} email      — visitor email
 * @param {string|number} variantId — Shopify variant ID
 * @returns {Promise<void>}
 */
export async function subscribeBackInStock(email, variantId) {
  if (!email || !variantId) return;

  // Public company ID is safe in browser (not a secret key). (T-06-04 accept)
  const companyId = document.body.dataset.klaviyoCompanyId || '';
  if (!companyId) {
    console.warn('[klaviyo-flows] klaviyoCompanyId not set on <body>; BIS skipped.');
    return;
  }

  const url = 'https://a.klaviyo.com/client/back-in-stock-subscriptions/?company_id=' + companyId;

  const payload = {
    data: {
      type: 'back-in-stock-subscription',
      attributes: {
        channels: ['EMAIL'],
        profile: {
          data: {
            type: 'profile',
            attributes: { email },
          },
        },
      },
      relationships: {
        variant: {
          data: {
            type: 'catalog-variant',
            id: `$shopify:::$default:::${variantId}`,
          },
        },
      },
    },
  };

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      revision: '2023-12-15',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Klaviyo BIS error ${res.status}: ${text}`);
  }
}

/**
 * Wire back-in-stock forms on the page.
 * Finds all [data-bis-variant] containers, attaches submit listener.
 */
function initBackInStockForms() {
  const forms = document.querySelectorAll('[data-bis-form]');
  forms.forEach((form) => {
    const variantId = form.dataset.bisVariant;
    const emailInput = form.querySelector('[data-bis-email]');
    const msgEl = form.querySelector('[data-bis-msg]');

    if (!emailInput || !variantId) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Basic email validation (T-06-05 mitigate)
      const email = emailInput.value.trim();
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        if (msgEl) {
          msgEl.textContent = 'Please enter a valid email address.';
          msgEl.dataset.bisStatus = 'error';
        }
        return;
      }

      const submitBtn = form.querySelector('[data-bis-submit]');
      if (submitBtn) submitBtn.disabled = true;

      try {
        await subscribeBackInStock(email, variantId);
        if (msgEl) {
          msgEl.textContent = "You're on the list! We'll notify you when this is back in stock.";
          msgEl.dataset.bisStatus = 'success';
        }
        emailInput.value = '';
      } catch (_err) {
        if (msgEl) {
          msgEl.textContent = 'Something went wrong. Please try again.';
          msgEl.dataset.bisStatus = 'error';
        }
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', initBackInStockForms);
