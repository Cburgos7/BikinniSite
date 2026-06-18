/**
 * pdp.js
 * Product Detail Page interactions:
 * - Thumbnail gallery swap
 * - Lightbox via native <dialog>.showModal()
 * - Color/size variant selection state
 * - Add-to-cart AJAX with cart:updated dispatch
 * - One-open-at-a-time accordion logic
 */

import { trackAddedToCart } from './klaviyo-flows.js';
import { trackAddToCart } from './ga4.js';

// Module-level variant selection state
let selectedSize = null;
let selectedColor = null;
let selectedVariantId = null;

// variantsData is populated inside init() after DOMContentLoaded to guarantee
// the #product-variants-json script tag exists when it is read (WR-05).
let variantsData = [];

/**
 * Find a variant matching current size and/or color selection.
 * @param {string|null} size
 * @param {string|null} color
 * @returns {object|undefined}
 */
const findVariant = (size, color) => {
  return variantsData.find((v) => {
    const opts = v.options || [];
    const sizeMatch = size ? opts.some((o) => o === size) : true;
    const colorMatch = color ? opts.some((o) => o === color) : true;
    return sizeMatch && colorMatch;
  });
};

/**
 * THUMBNAIL GALLERY SWAP
 */
const initGallery = () => {
  const mainImageWrap = document.getElementById('pdp-main-image');
  if (!mainImageWrap) return;
  // mainImageWrap is a <div>; the actual <img> is inside (rendered by cloudinary-img snippet)
  const mainImg = mainImageWrap.querySelector('img');

  const thumbnails = document.querySelectorAll('[data-thumbnail]');
  thumbnails.forEach((thumb) => {
    thumb.addEventListener('click', () => {
      // Swap main image src
      if (mainImg) mainImg.src = thumb.dataset.fullSrc;

      // Update active ring state on all thumbnails
      thumbnails.forEach((t) => {
        t.classList.remove('ring-2', 'ring-deep');
      });
      thumb.classList.add('ring-2', 'ring-deep');
    });
  });
};

/**
 * LIGHTBOX via native <dialog>.showModal()
 */
const initLightbox = () => {
  const dialog = document.getElementById('pdp-lightbox');
  const lightboxImg = document.getElementById('pdp-lightbox-img');
  const mainImageWrap = document.getElementById('pdp-main-image');
  const closeBtn = document.getElementById('pdp-lightbox-close');

  if (!dialog || !lightboxImg || !mainImageWrap) return;
  // mainImageWrap is a <div>; the actual <img> is inside (rendered by cloudinary-img snippet)
  const getMainImg = () => mainImageWrap.querySelector('img');

  // Open lightbox when main image wrapper is clicked
  const trigger = document.querySelector('[data-lightbox-trigger]');
  if (trigger) {
    trigger.addEventListener('click', () => {
      const mainImg = getMainImg();
      if (mainImg) {
        lightboxImg.src = mainImg.src;
        lightboxImg.alt = mainImg.alt;
      }
      dialog.showModal();
    });
  }

  // Close button
  if (closeBtn) {
    closeBtn.addEventListener('click', () => dialog.close());
  }

  // Backdrop click closes dialog
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) dialog.close();
  });

  // Escape key safety net (native dialog handles this, but belt-and-suspenders)
  dialog.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') dialog.close();
  });
};

/**
 * COLOR SWATCH SELECTION
 */
const initColorSwatches = () => {
  const swatches = document.querySelectorAll('[data-color-swatch]');
  const colorLabel = document.getElementById('selected-color-label');
  const mainImageWrap = document.getElementById('pdp-main-image');
  const addToCartBtn = document.getElementById('pdp-add-to-cart');

  swatches.forEach((btn) => {
    btn.addEventListener('click', () => {
      selectedColor = btn.dataset.colorValue;

      // Update label
      if (colorLabel) colorLabel.textContent = selectedColor;

      // Update active ring
      swatches.forEach((s) => {
        s.classList.remove('ring-2', 'ring-offset-1', 'ring-deep');
      });
      btn.classList.add('ring-2', 'ring-offset-1', 'ring-deep');

      // Find variant matching new color (and current size if set)
      const variant = findVariant(selectedSize, selectedColor);
      if (variant) {
        selectedVariantId = variant.id;
        if (addToCartBtn) addToCartBtn.dataset.variantId = selectedVariantId;

        // Update main gallery image to first image of matching variant
        if (mainImageWrap && variant.featured_image?.src) {
          const mainImg = mainImageWrap.querySelector('img');
          if (mainImg) mainImg.src = variant.featured_image.src;
        }
      }
    });
  });
};

/**
 * SIZE SWATCH SELECTION
 */
const initSizeSwatches = () => {
  const sizeBtns = document.querySelectorAll('[data-size-swatch]');
  const addToCartBtn = document.getElementById('pdp-add-to-cart');
  const unavailableMsg = document.getElementById('size-unavailable-msg');

  sizeBtns.forEach((btn) => {
    // Skip disabled (sold-out) sizes
    if (btn.disabled) return;

    btn.addEventListener('click', () => {
      selectedSize = btn.dataset.sizeValue;

      // Update active state
      sizeBtns.forEach((s) => {
        s.classList.remove('border-deep', 'bg-deep', 'text-cream');
        if (!s.disabled) {
          s.classList.add('border-deep/30', 'text-deep');
        }
      });
      btn.classList.remove('border-deep/30', 'text-deep');
      btn.classList.add('border-deep', 'bg-deep', 'text-cream');

      // Find matching variant
      const variant = findVariant(selectedSize, selectedColor);

      if (variant && variant.available) {
        selectedVariantId = variant.id;

        // Enable add-to-cart button
        if (addToCartBtn) {
          addToCartBtn.disabled = false;
          addToCartBtn.textContent = 'Add to Cart';
          addToCartBtn.classList.remove('cursor-not-allowed', 'opacity-60');
          addToCartBtn.classList.add('cursor-pointer', 'hover:opacity-90');
          addToCartBtn.dataset.variantId = selectedVariantId;
        }

        // Hide unavailability message
        if (unavailableMsg) {
          unavailableMsg.textContent = '';
          unavailableMsg.classList.add('hidden');
        }
      } else {
        selectedVariantId = null;

        // Show sold-out message
        if (unavailableMsg) {
          unavailableMsg.textContent = selectedSize + ' is sold out';
          unavailableMsg.classList.remove('hidden');
        }

        // Disable add-to-cart
        if (addToCartBtn) {
          addToCartBtn.disabled = true;
          addToCartBtn.textContent = 'Sold Out';
          addToCartBtn.classList.add('cursor-not-allowed', 'opacity-60');
          addToCartBtn.classList.remove('cursor-pointer', 'hover:opacity-90');
          addToCartBtn.dataset.variantId = '';
        }

        // Show back-in-stock form for this variant (if rendered in template)
        const variant = findVariant(selectedSize, selectedColor);
        if (variant) {
          // Hide all BIS forms first
          document.querySelectorAll('[data-bis-variant]').forEach((el) => {
            el.classList.add('hidden');
          });
          const bisEl = document.getElementById(`bis-${variant.id}`);
          if (bisEl) bisEl.classList.remove('hidden');
        }
      }

      // If variant is available, ensure all BIS forms are hidden
      const resolvedVariant = findVariant(selectedSize, selectedColor);
      if (resolvedVariant && resolvedVariant.available) {
        document.querySelectorAll('[data-bis-variant]').forEach((el) => {
          el.classList.add('hidden');
        });
      }
    });
  });
};

/**
 * ADD-TO-CART via Shopify Ajax Cart API
 * @param {string|number} variantId
 */
const addToCart = async (variantId) => {
  if (!variantId) return;

  // Validate variantId is a finite integer (T-04-04-01)
  const parsedId = parseInt(variantId, 10);
  if (!isFinite(parsedId) || isNaN(parsedId)) {
    const errorEl = document.getElementById('pdp-cart-error');
    if (errorEl) errorEl.classList.remove('hidden');
    return;
  }

  const btn = document.getElementById('pdp-add-to-cart');
  const errorEl = document.getElementById('pdp-cart-error');

  // Disable button during fetch to prevent double-submit (T-04-04-04)
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Adding...';
  }

  try {
    const res = await fetch('/cart/add.js', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify({ id: parsedId, quantity: 1 }),
    });

    if (!res.ok) throw new Error('add failed');
    const cartItem = await res.json();

    // Fire Klaviyo abandoned-cart tracking event
    trackAddedToCart(cartItem);

    // Fire GA4 add_to_cart event
    trackAddToCart(cartItem);

    if (errorEl) errorEl.classList.add('hidden');

    // Notify cart drawer (T-04-04-03 pattern)
    document.dispatchEvent(new CustomEvent('cart:updated'));

    if (btn) btn.textContent = 'Add to Cart';
  } catch (err) {
    if (errorEl) errorEl.classList.remove('hidden');
    if (btn) btn.textContent = 'Add to Cart';
  } finally {
    // Re-enable button (T-04-04-04)
    if (btn) btn.disabled = false;
  }
};

/**
 * Wire add-to-cart button
 */
const initAddToCart = () => {
  const btn = document.getElementById('pdp-add-to-cart');
  if (!btn) return;
  btn.addEventListener('click', () => addToCart(selectedVariantId));
};

/**
 * ONE-OPEN-AT-A-TIME ACCORDION (D-13)
 */
const initAccordions = () => {
  const accordions = document.querySelectorAll('[data-accordion]');

  const closeAll = () => {
    accordions.forEach((acc) => {
      const trigger = acc.querySelector('[data-accordion-trigger]');
      const body = acc.querySelector('[data-accordion-body]');
      const icon = acc.querySelector('[data-accordion-icon]');
      if (body) body.style.maxHeight = '0';
      if (trigger) trigger.setAttribute('aria-expanded', 'false');
      if (icon) icon.style.transform = 'rotate(0deg)';
    });
  };

  accordions.forEach((accordion) => {
    const trigger = accordion.querySelector('[data-accordion-trigger]');
    const body = accordion.querySelector('[data-accordion-body]');
    const icon = accordion.querySelector('[data-accordion-icon]');

    if (!trigger || !body) return;

    trigger.addEventListener('click', () => {
      const isOpen = trigger.getAttribute('aria-expanded') === 'true';

      // Close all accordions
      closeAll();

      // If it was closed, open this one
      if (!isOpen) {
        body.style.maxHeight = body.scrollHeight + 'px';
        trigger.setAttribute('aria-expanded', 'true');
        if (icon) icon.style.transform = 'rotate(180deg)';
      }
    });
  });
};

/**
 * Main init — bind all event listeners after DOM is ready
 */
export default function init() {
  document.addEventListener('DOMContentLoaded', () => {
    // Parse variants JSON now that the DOM is guaranteed ready (WR-05)
    variantsData = JSON.parse(
      document.getElementById('product-variants-json')?.textContent || '[]'
    );
    initGallery();
    initLightbox();
    initColorSwatches();
    initSizeSwatches();
    initAddToCart();
    initAccordions();
  });
}

init();
