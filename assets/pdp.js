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

// Which option position holds colour and which holds size, resolved from the
// rendered option names. Products vary: most are Color + Size, 363 of 663 are
// colour-only, and reading positions rather than assuming them is what lets one
// code path serve both.
let colorKey = null;
let sizeKey = null;
let hasSizeOption = false;

/**
 * Find the variant matching the current selection.
 *
 * Previously a null selection was treated as "any", so an unset colour matched
 * the first variant of ANY colour — the page could say Baby Pink and add Black.
 * Matching is now exact on every option the product actually has.
 *
 * @param {string|null} size
 * @param {string|null} color
 * @returns {object|undefined}
 */
const findVariant = (size, color) => {
  return variantsData.find((v) => {
    if (colorKey && v[colorKey] !== color) return false;
    if (hasSizeOption && sizeKey && v[sizeKey] !== size) return false;
    return true;
  });
};

/** Format Shopify's integer cents as USD. */
const formatMoney = (cents) =>
  '$' + (Number(cents) / 100).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');

/**
 * Single source of truth for variant state.
 *
 * The add-to-cart button ships disabled and was only ever re-enabled by the size
 * handler, so the 363 products with no size option could never be bought — the
 * handler bound to elements that did not exist. Price, availability and the armed
 * variant are now all recomputed here, and this runs once on load so a product is
 * purchasable before the shopper touches anything.
 */
const syncVariant = () => {
  const addToCartBtn = document.getElementById('pdp-add-to-cart');
  const unavailableMsg = document.getElementById('size-unavailable-msg');
  const priceEl = document.getElementById('pdp-price');
  const variant = findVariant(selectedSize, selectedColor);

  if (variant && priceEl && variant.price != null) {
    priceEl.textContent = formatMoney(variant.price);
  }

  const sellable = Boolean(variant && variant.available);
  selectedVariantId = sellable ? variant.id : null;

  if (addToCartBtn) {
    addToCartBtn.disabled = !sellable;
    addToCartBtn.dataset.variantId = sellable ? String(variant.id) : '';
    addToCartBtn.classList.toggle('cursor-not-allowed', !sellable);
    addToCartBtn.classList.toggle('opacity-60', !sellable);
    addToCartBtn.classList.toggle('cursor-pointer', sellable);
    addToCartBtn.classList.toggle('hover:opacity-90', sellable);
    if (sellable) {
      addToCartBtn.textContent = 'Add to Cart';
    } else if (variant) {
      addToCartBtn.textContent = 'Sold Out';
    } else {
      // No such combination was ever made — saying "sold out" implies it might
      // come back, which is false.
      addToCartBtn.textContent = 'Unavailable';
    }
  }

  if (unavailableMsg) {
    if (sellable) {
      unavailableMsg.textContent = '';
      unavailableMsg.classList.add('hidden');
    } else {
      unavailableMsg.textContent = variant
        ? `${selectedSize || 'This option'} is sold out`
        : 'That combination is not available in this colour';
      unavailableMsg.classList.remove('hidden');
    }
  }

  document.querySelectorAll('[data-bis-variant]').forEach((el) => {
    el.classList.add('hidden');
  });
  if (variant && !variant.available) {
    const bisEl = document.getElementById(`bis-${variant.id}`);
    if (bisEl) bisEl.classList.remove('hidden');
  }
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

      // If the newly chosen colour does not come in the current size, fall back
      // to a size it does come in rather than leaving the previous colour's
      // variant armed — that is how the wrong colour reached the cart.
      if (hasSizeOption && !findVariant(selectedSize, selectedColor)) {
        const firstForColor = variantsData.find(
          (v) => v[colorKey] === selectedColor && v.available
        ) || variantsData.find((v) => v[colorKey] === selectedColor);
        if (firstForColor) {
          selectedSize = firstForColor[sizeKey];
          markSelectedSize(selectedSize);
        }
      }

      const variant = findVariant(selectedSize, selectedColor);
      if (variant && mainImageWrap && variant.featured_image?.src) {
        const mainImg = mainImageWrap.querySelector('img');
        if (mainImg) mainImg.src = variant.featured_image.src;
      }
      syncVariant();
    });
  });
};

/** Paint the active state on the size button matching `size`. */
const markSelectedSize = (size) => {
  document.querySelectorAll('[data-size-swatch]').forEach((s) => {
    const isActive = s.dataset.sizeValue === size;
    s.classList.toggle('border-deep', isActive);
    s.classList.toggle('bg-deep', isActive);
    s.classList.toggle('text-cream', isActive);
    s.classList.toggle('border-deep/30', !isActive);
    s.classList.toggle('text-deep', !isActive);
  });
};

/**
 * SIZE SWATCH SELECTION
 */
const initSizeSwatches = () => {
  const sizeBtns = document.querySelectorAll('[data-size-swatch]');

  sizeBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      // Sizes that exist in another colour are no longer skipped outright: the
      // click reselects and syncVariant() decides whether it is buyable, so the
      // shopper gets an honest message instead of a dead button.
      if (btn.disabled) return;
      selectedSize = btn.dataset.sizeValue;
      markSelectedSize(selectedSize);
      syncVariant();
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

    // Resolve which option position holds colour and which holds size from the
    // rendered swatches, rather than assuming Color is always option1. Products
    // with no size option get hasSizeOption = false, which is what allows them to
    // be purchasable at all.
    const firstColorSwatch = document.querySelector('[data-color-swatch]');
    const firstSizeSwatch = document.querySelector('[data-size-swatch]');
    const sample = variantsData[0] || {};
    ['option1', 'option2', 'option3'].forEach((key) => {
      const value = sample[key];
      if (value == null) return;
      if (firstColorSwatch && !colorKey) {
        const known = [...document.querySelectorAll('[data-color-swatch]')].some(
          (b) => b.dataset.colorValue === value
        );
        if (known) { colorKey = key; return; }
      }
      if (firstSizeSwatch && !sizeKey) {
        const known = [...document.querySelectorAll('[data-size-swatch]')].some(
          (b) => b.dataset.sizeValue === value
        );
        if (known) sizeKey = key;
      }
    });
    hasSizeOption = Boolean(sizeKey && firstSizeSwatch);

    // Seed the selection from the first sellable variant so the page opens on a
    // real, buyable combination instead of an unset state the shopper cannot see.
    const opening = variantsData.find((v) => v.available) || variantsData[0];
    if (opening) {
      if (colorKey) selectedColor = opening[colorKey];
      if (hasSizeOption) selectedSize = opening[sizeKey];
    }

    initGallery();
    initLightbox();
    initColorSwatches();
    initSizeSwatches();
    initAddToCart();
    initAccordions();

    // Paint the seeded selection and arm the button.
    if (colorKey) {
      const label = document.getElementById('selected-color-label');
      if (label && selectedColor) label.textContent = selectedColor;
      document.querySelectorAll('[data-color-swatch]').forEach((s) => {
        const active = s.dataset.colorValue === selectedColor;
        s.classList.toggle('ring-2', active);
        s.classList.toggle('ring-offset-1', active);
        s.classList.toggle('ring-deep', active);
      });
    }
    if (hasSizeOption && selectedSize) markSelectedSize(selectedSize);
    syncVariant();
  });
}

init();
