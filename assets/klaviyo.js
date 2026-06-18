/**
 * klaviyo.js — Klaviyo identify + track helpers
 *
 * Reads customer data from <body> data attributes (set by Liquid in theme.liquid)
 * and calls klaviyo.identify() so Klaviyo flows can target logged-in customers.
 *
 * TCPA note: SMS opt-in checkbox is rendered by Klaviyo's form builder when SMS
 * is enabled on the form in the Klaviyo dashboard. No theme code handles the
 * checkbox or pre-checks it. Checkout SMS compliance is configured in Klaviyo's
 * checkout integration settings — no Shopify Additional Scripts required.
 */

/**
 * Identify the current customer with Klaviyo.
 * Called automatically on DOMContentLoaded when customer data is present.
 */
function identifyCustomer() {
  const body = document.body;
  const email = body.dataset.customerEmail;
  const customerId = body.dataset.customerId;

  if (!email) return;

  if (window.klaviyo) {
    window.klaviyo.identify({
      $email: email,
      $id: customerId || undefined,
    });
  } else {
    // Klaviyo loads async — retry once after a short delay
    window.addEventListener('klaviyoForms', function onKlaviyoReady() {
      window.removeEventListener('klaviyoForms', onKlaviyoReady);
      if (window.klaviyo) {
        window.klaviyo.identify({
          $email: email,
          $id: customerId || undefined,
        });
      }
    });
  }
}

/**
 * Track a custom Klaviyo event.
 * Used by GA4 and cart modules to fire unified analytics + Klaviyo events.
 *
 * @param {string} eventName - Klaviyo event name (e.g. 'Added to Cart')
 * @param {Object} [properties={}] - Key/value payload for the event
 */
export function trackEvent(eventName, properties = {}) {
  window.klaviyo?.track(eventName, properties);
}

document.addEventListener('DOMContentLoaded', identifyCustomer);
