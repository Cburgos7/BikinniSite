/**
 * cookie-consent.js
 * CCPA cookie consent banner — localStorage persistence, slide-out animation.
 */

function dismissBanner(banner) {
  banner.classList.add('translate-y-full');
  setTimeout(() => {
    banner.style.display = 'none';
  }, 300);
}

function init() {
  document.addEventListener('DOMContentLoaded', () => {
    const banner = document.getElementById('cookie-consent-banner');
    if (!banner) return;

    // If consent already given, hide immediately without animation
    if (localStorage.getItem('soleil_noir_cookie_consent') !== null) {
      banner.classList.add('translate-y-full');
      setTimeout(() => {
        banner.style.display = 'none';
      }, 300);
      return;
    }

    const acceptBtn = document.getElementById('cookie-accept');
    const declineBtn = document.getElementById('cookie-decline');

    if (acceptBtn) {
      acceptBtn.addEventListener('click', () => {
        localStorage.setItem('soleil_noir_cookie_consent', 'accepted');
        dismissBanner(banner);
      });
    }

    if (declineBtn) {
      declineBtn.addEventListener('click', () => {
        localStorage.setItem('soleil_noir_cookie_consent', 'declined');
        dismissBanner(banner);
      });
    }
  });
}

export default init;

init();
