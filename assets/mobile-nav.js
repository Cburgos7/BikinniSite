const openDrawer = (hamburger, drawer, overlay) => {
  drawer.classList.remove('-translate-x-full');
  drawer.classList.add('translate-x-0');
  overlay.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  hamburger.setAttribute('aria-expanded', 'true');

  // Focus the close button when drawer opens
  const closeBtn = document.getElementById('mobile-nav-close');
  if (closeBtn) closeBtn.focus();
};

const closeDrawer = (hamburger, drawer, overlay) => {
  drawer.classList.remove('translate-x-0');
  drawer.classList.add('-translate-x-full');
  overlay.classList.add('hidden');
  document.body.style.overflow = '';
  hamburger.setAttribute('aria-expanded', 'false');
  hamburger.focus();
};

const getFocusableElements = (container) => {
  return Array.from(
    container.querySelectorAll(
      'button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
  ).filter((el) => !el.hasAttribute('disabled'));
};

const trapFocus = (e, drawer) => {
  const focusable = getFocusableElements(drawer);
  if (!focusable.length) return;

  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  if (e.key === 'Tab') {
    if (e.shiftKey) {
      // Shift+Tab: if on first, wrap to last
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      // Tab: if on last, wrap to first
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }
};

export default function init() {
  document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.getElementById('nav-hamburger');
    const drawer = document.getElementById('mobile-nav-drawer');
    const closeBtn = document.getElementById('mobile-nav-close');
    const overlay = document.getElementById('mobile-nav-overlay');

    if (!hamburger || !drawer || !closeBtn || !overlay) return;

    hamburger.addEventListener('click', () => openDrawer(hamburger, drawer, overlay));
    closeBtn.addEventListener('click', () => closeDrawer(hamburger, drawer, overlay));
    overlay.addEventListener('click', () => closeDrawer(hamburger, drawer, overlay));

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && hamburger.getAttribute('aria-expanded') === 'true') {
        closeDrawer(hamburger, drawer, overlay);
      }
      if (hamburger.getAttribute('aria-expanded') === 'true') {
        trapFocus(e, drawer);
      }
    });
  });
}

init();
