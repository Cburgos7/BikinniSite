/**
 * cart-drawer.js
 * Cart drawer open/close, quantity updates via Shopify Ajax Cart API,
 * free shipping progress bar, and nav badge update.
 */

import { trackBeginCheckout } from './ga4.js';

const getFocusableElements = (container) => {
  return Array.from(
    container.querySelectorAll(
      'button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
  ).filter((el) => !el.hasAttribute('disabled'));
};

const trapFocus = (e, container) => {
  const focusable = getFocusableElements(container);
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (e.key === 'Tab') {
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }
};

let isOpen = false;

// Most recent cart state — updated on every cart:updated event and quantity change.
// Used by the checkout button handler to fire begin_checkout with accurate cart data.
let _lastCartData = null;

const formatPrice = (cents) => {
  return '$' + (cents / 100).toFixed(2);
};

const escapeHtml = (str) => {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

const buildItemHTML = (item) => {
  const imgSrc = item.image || '';
  const variantTitle =
    item.variant_title && item.variant_title !== 'Default Title'
      ? `<p class="text-mid text-xs mt-0.5">${escapeHtml(item.variant_title)}</p>`
      : '';
  const disabledAttrs =
    item.quantity <= 1 ? 'disabled class="w-6 h-6 flex items-center justify-center border border-mid text-deep font-body text-sm hover:border-deep transition-colors duration-200 opacity-50 cursor-not-allowed"' : 'class="w-6 h-6 flex items-center justify-center border border-mid text-deep font-body text-sm hover:border-deep transition-colors duration-200"';

  return `<div class="flex gap-4 items-start" data-line-item="${item.id}">
    <img src="${escapeHtml(imgSrc)}" alt="${escapeHtml(item.title)}" class="w-16 h-20 object-cover flex-shrink-0" loading="lazy">
    <div class="flex-1 min-w-0">
      <p class="font-body text-sm text-deep truncate">${escapeHtml(item.title)}</p>
      ${variantTitle}
      <div class="flex items-center gap-3 mt-2">
        <button
          ${disabledAttrs}
          data-action="decrease"
          data-variant-id="${item.id}"
          data-qty="${item.quantity}"
          aria-label="Decrease quantity"
        >−</button>
        <span class="font-body text-sm text-deep w-4 text-center" data-qty="${item.quantity}">${item.quantity}</span>
        <button
          class="w-6 h-6 flex items-center justify-center border border-mid text-deep font-body text-sm hover:border-deep transition-colors duration-200"
          data-action="increase"
          data-variant-id="${item.id}"
          data-qty="${item.quantity}"
          aria-label="Increase quantity"
        >+</button>
        <button
          class="ml-auto text-mid hover:text-deep transition-colors duration-200"
          data-action="remove"
          data-variant-id="${item.id}"
          data-qty="0"
          aria-label="Remove ${escapeHtml(item.title)} from cart"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
    <p class="font-body text-sm text-deep flex-shrink-0">${formatPrice(item.final_line_price)}</p>
  </div>`;
};

export default function init() {
  document.addEventListener('DOMContentLoaded', () => {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-drawer-overlay');
    const closeBtn = document.getElementById('cart-drawer-close');
    const toggleBtn = document.getElementById('nav-cart-toggle');
    const badge = document.getElementById('cart-count-badge');
    const cartItems = document.getElementById('cart-items');
    const cartEmpty = document.getElementById('cart-empty');
    const cartFooter = document.getElementById('cart-footer');
    const subtotalEl = document.getElementById('cart-subtotal');
    const shippingFill = document.getElementById('shipping-bar-fill');
    const shippingText = document.getElementById('shipping-bar-text');

    if (!drawer || !overlay || !closeBtn || !toggleBtn) return;

    // Read threshold from data attribute
    const barContainer = document.querySelector('[data-threshold]');
    const threshold = barContainer
      ? parseInt(barContainer.dataset.threshold, 10) || 75
      : 75;

    const openDrawer = () => {
      drawer.classList.remove('translate-x-full');
      drawer.classList.add('translate-x-0');
      overlay.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      isOpen = true;
      closeBtn.focus();
    };

    const closeDrawer = () => {
      drawer.classList.remove('translate-x-0');
      drawer.classList.add('translate-x-full');
      overlay.classList.add('hidden');
      document.body.style.overflow = '';
      isOpen = false;
      if (toggleBtn) toggleBtn.focus();
    };

    toggleBtn.addEventListener('click', openDrawer);
    closeBtn.addEventListener('click', closeDrawer);
    overlay.addEventListener('click', closeDrawer);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && isOpen) {
        closeDrawer();
      }
      if (isOpen) {
        trapFocus(e, drawer);
      }
    });

    /**
     * Update quantity via Shopify Ajax Cart API
     * @param {string|number} variantId
     * @param {number} newQty
     */
    const updateQuantity = (variantId, newQty) => {
      fetch('/cart/change.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        body: JSON.stringify({ id: variantId, quantity: newQty }),
      })
        .then((res) => {
          if (!res.ok) throw new Error('Cart update failed: ' + res.status);
          return res.json();
        })
        .then((cart) => renderCart(cart))
        .catch((err) => console.error('[cart-drawer]', err));
    };

    /**
     * Bind quantity and remove button handlers on #cart-items
     * Uses event delegation so it survives innerHTML re-renders.
     */
    const bindCartItemEvents = () => {
      if (!cartItems) return;
      // Remove old listener by replacing the node (simplest delegation approach)
      const newItems = cartItems.cloneNode(true);
      cartItems.parentNode.replaceChild(newItems, cartItems);
      // Re-query after replace
      const itemsContainer = document.getElementById('cart-items');
      if (!itemsContainer) return;

      itemsContainer.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        const action = btn.dataset.action;
        const variantId = btn.dataset.variantId;
        // Get current qty from sibling span or btn data attribute
        const row = btn.closest('[data-line-item]');
        const qtyEl = row ? row.querySelector('[data-qty]') : null;
        const qty = qtyEl ? parseInt(qtyEl.dataset.qty, 10) : parseInt(btn.dataset.qty, 10);

        if (action === 'decrease') {
          updateQuantity(variantId, Math.max(1, qty - 1));
        } else if (action === 'increase') {
          updateQuantity(variantId, qty + 1);
        } else if (action === 'remove') {
          updateQuantity(variantId, 0);
        }
      });
    };

    /**
     * Re-render cart state in the drawer
     * @param {Object} cart - Shopify cart JSON
     */
    const renderCart = (cart) => {
      // Keep module-level snapshot for begin_checkout tracking
      _lastCartData = cart;
      // Update badge
      if (badge) {
        badge.textContent = cart.item_count;
        if (cart.item_count === 0) {
          badge.classList.add('hidden');
        } else {
          badge.classList.remove('hidden');
        }
      } else if (toggleBtn) {
        // Badge may not exist yet (first time cart has items), dynamically create it
        const existingBadge = document.getElementById('cart-count-badge');
        if (!existingBadge && cart.item_count > 0) {
          const newBadge = document.createElement('span');
          newBadge.id = 'cart-count-badge';
          newBadge.className =
            'absolute -top-1 -right-1 flex items-center justify-center w-4 h-4 rounded-full bg-coral text-cream text-[10px] font-body leading-none';
          newBadge.setAttribute('aria-hidden', 'true');
          newBadge.textContent = cart.item_count;
          toggleBtn.appendChild(newBadge);
        } else if (existingBadge) {
          existingBadge.textContent = cart.item_count;
          if (cart.item_count === 0) {
            existingBadge.classList.add('hidden');
          } else {
            existingBadge.classList.remove('hidden');
          }
        }
      }

      // Update subtotal
      if (subtotalEl) {
        subtotalEl.textContent = formatPrice(cart.total_price);
      }

      // Update free shipping bar
      const totalDollars = cart.total_price / 100;
      const progressPct = Math.min((totalDollars / threshold) * 100, 100);
      if (shippingFill) {
        shippingFill.style.width = progressPct + '%';
      }
      if (shippingText) {
        if (totalDollars >= threshold) {
          shippingText.textContent = "You've unlocked free shipping!";
        } else {
          const remaining = (threshold - totalDollars).toFixed(2);
          shippingText.textContent = `You're $${remaining} away from free shipping!`;
        }
      }

      // Toggle empty/footer states
      const currentCartItems = document.getElementById('cart-items');
      const currentCartEmpty = document.getElementById('cart-empty');
      const currentCartFooter = document.getElementById('cart-footer');

      if (currentCartEmpty) {
        if (cart.item_count === 0) {
          currentCartEmpty.classList.remove('hidden');
        } else {
          currentCartEmpty.classList.add('hidden');
        }
      }
      if (currentCartFooter) {
        if (cart.item_count === 0) {
          currentCartFooter.classList.add('hidden');
        } else {
          currentCartFooter.classList.remove('hidden');
        }
      }

      // Re-render item rows
      if (currentCartItems) {
        // Keep the empty state div, replace item rows only
        const emptyDiv = currentCartItems.querySelector('#cart-empty');
        const itemsHTML = cart.items.map(buildItemHTML).join('');
        currentCartItems.innerHTML = (emptyDiv ? emptyDiv.outerHTML : '') + itemsHTML;

        // Ensure empty state visibility
        const newEmptyDiv = currentCartItems.querySelector('#cart-empty');
        if (newEmptyDiv) {
          if (cart.item_count === 0) {
            newEmptyDiv.classList.remove('hidden');
          } else {
            newEmptyDiv.classList.add('hidden');
          }
        }
      }

      // Rebind events after re-render
      bindCartItemEvents();
    };

    // Initial event binding
    bindCartItemEvents();

    /**
     * Fire GA4 begin_checkout when the checkout button inside the cart drawer is clicked.
     * Uses event delegation so it survives innerHTML re-renders of the cart footer.
     * The button must have data-action="checkout" or href="/checkout".
     */
    if (drawer) {
      drawer.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-action="checkout"], a[href="/checkout"]');
        if (!btn) return;
        trackBeginCheckout(_lastCartData);
      });
    }

    /**
     * Listen for upromote:ref-captured dispatched by upromote.js.
     * Applies the affiliate discount code to the cart drawer checkout button href.
     * This covers the case where upromote.js fires before or after the drawer renders.
     */
    document.addEventListener('upromote:ref-captured', (e) => {
      const code = e.detail && e.detail.code;
      if (!code) return;
      const checkoutBtn = document.getElementById('cart-checkout-btn');
      if (!checkoutBtn) return;
      const href = checkoutBtn.getAttribute('href') || '';
      const separator = href.includes('?') ? '&' : '?';
      // Remove any existing discount param before appending to avoid duplicates
      const clean = href.replace(/[?&]discount=[^&]*/g, '').replace(/[?&]$/, '');
      const newSeparator = clean.includes('?') ? '&' : '?';
      checkoutBtn.href = clean + newSeparator + 'discount=' + encodeURIComponent(code);
    });

    /**
     * Listen for cart:updated dispatched by pdp.js (and other add-to-cart modules).
     * Fetch the current cart state, re-render drawer, and open it.
     */
    document.addEventListener('cart:updated', () => {
      fetch('/cart.js', {
        headers: { 'Content-Type': 'application/json' },
      })
        .then((res) => res.json())
        .then((cart) => {
          renderCart(cart);
          openDrawer();
        })
        .catch((err) => console.error('[cart-drawer] cart:updated fetch failed', err));
    });
  });
}

init();
