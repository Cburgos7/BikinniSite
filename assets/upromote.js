/**
 * upromote.js
 * UpPromote affiliate referral capture and checkout URL wiring.
 *
 * Reads referral state exclusively via getInfluencerCode() from ref-capture.js —
 * does NOT re-read URLSearchParams or sessionStorage for the ref param directly.
 *
 * On DOMContentLoaded:
 *   1. Reads the active referral/influencer code.
 *   2. Stores it as "discount_code" in sessionStorage (UpPromote referral codes are
 *      valid Shopify discount codes).
 *   3. Appends ?discount=CODE (or &discount=CODE) to every checkout link on the page.
 *   4. Dispatches "upromote:ref-captured" on document so cart-drawer.js can apply
 *      the discount to dynamically-updated checkout URLs.
 */

import { getInfluencerCode } from './ref-capture.js';

/**
 * Append discount param to a checkout URL string.
 * Handles URLs that may already have a query string.
 *
 * @param {string} href
 * @param {string} code
 * @returns {string}
 */
function applyDiscountToHref(href, code) {
  if (!href || !code) return href;
  const separator = href.includes('?') ? '&' : '?';
  // Remove any existing discount param to avoid duplicates
  const clean = href.replace(/[?&]discount=[^&]*/g, '').replace(/[?&]$/, '');
  const newSeparator = clean.includes('?') ? '&' : '?';
  return clean + newSeparator + 'discount=' + encodeURIComponent(code);
}

document.addEventListener('DOMContentLoaded', () => {
  const code = getInfluencerCode();

  if (!code) return;

  // Store as discount_code so other modules can read it without re-parsing the URL
  sessionStorage.setItem('discount_code', code);

  // Wire all checkout links present at page load
  document.querySelectorAll('a[href*="/checkout"]').forEach((link) => {
    link.href = applyDiscountToHref(link.getAttribute('href'), code);
  });

  // Notify cart-drawer.js (and any other modules) that a referral code is active
  document.dispatchEvent(
    new CustomEvent('upromote:ref-captured', { detail: { code } })
  );
});
