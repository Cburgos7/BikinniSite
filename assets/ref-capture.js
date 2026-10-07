/**
 * ref-capture.js
 * Shared referral-code utility — consumed by ga4.js and upromote.js.
 *
 * Runs at module evaluation time (top-level, before DOMContentLoaded) so the
 * value is available synchronously to any importer on the same page.
 *
 * Side effects:
 *   - Reads ?ref= query param on first load; writes to sessionStorage under
 *     key "upromote_ref" if the value is non-empty.
 *
 * Exports:
 *   getReferralCode()   — strictly an explicit ?ref= code. Safe to treat as a
 *                         discount code.
 *   getInfluencerCode() — the above, falling back to utm_campaign. Analytics
 *                         only.
 *
 * The two are deliberately separate. UpPromote is installed and tracks with its
 * own `sca_ref` parameter, and it can be configured to append UTM parameters to
 * affiliate links. If the discount path kept the utm_campaign fallback, a
 * campaign name would be appended to checkout as ?discount=<campaign>, which is
 * not a real discount code. A campaign name is a perfectly good analytics
 * dimension and a bad discount code; only one caller should see it.
 */

// Capture ref param on module evaluation (single write path — T-06-06)
const _ref = new URLSearchParams(location.search).get('ref') || '';
if (_ref) {
  sessionStorage.setItem('upromote_ref', _ref);
}

/**
 * An explicit referral code only — the ?ref= value captured this session.
 * Never a utm_campaign. Use this anywhere the value is treated as a Shopify
 * discount code.
 *
 * @returns {string|null}
 */
export function getReferralCode() {
  return sessionStorage.getItem('upromote_ref') || null;
}

/**
 * Referral code for analytics, falling back to utm_campaign so campaign traffic
 * is still attributable. Do NOT use this as a discount code — see the note at
 * the top of the file.
 *
 * @returns {string|null}
 */
export function getInfluencerCode() {
  return (
    getReferralCode() ||
    new URLSearchParams(location.search).get('utm_campaign') ||
    null
  );
}
