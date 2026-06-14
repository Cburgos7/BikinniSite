/**
 * collection-filter.js
 * AJAX filter fetch, DOM grid swap, URL pushState, active chip management,
 * filter drawer open/close with focus trap.
 *
 * Follows the ES module + default init() pattern established in mobile-nav.js.
 * Fetch + DOM-swap pattern from cart-drawer.js.
 */

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Escape HTML special characters to prevent XSS when injecting into innerHTML.
 * Identical implementation to cart-drawer.js.
 * @param {string} str
 * @returns {string}
 */
const escapeHtml = (str) => {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

// ---------------------------------------------------------------------------
// Focus trap (mirrors mobile-nav.js implementation)
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Filter drawer open / close
// ---------------------------------------------------------------------------

let drawerOpen = false;
let _trapFocusHandler = null;

const openFilterDrawer = () => {
  const drawer = document.getElementById('filter-drawer');
  const overlay = document.getElementById('filter-drawer-overlay');
  const openBtn = document.getElementById('filter-drawer-open');
  if (!drawer || !overlay) return;

  drawer.classList.remove('-translate-x-full');
  drawer.classList.add('translate-x-0');
  overlay.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  drawerOpen = true;
  if (openBtn) openBtn.setAttribute('aria-expanded', 'true');

  // Focus the close button when drawer opens
  const closeBtn = document.getElementById('filter-drawer-close');
  if (closeBtn) closeBtn.focus();

  // Attach focus trap
  _trapFocusHandler = (e) => trapFocus(e, drawer);
  document.addEventListener('keydown', _trapFocusHandler);
};

const closeFilterDrawer = () => {
  const drawer = document.getElementById('filter-drawer');
  const overlay = document.getElementById('filter-drawer-overlay');
  const openBtn = document.getElementById('filter-drawer-open');
  if (!drawer || !overlay) return;

  drawer.classList.remove('translate-x-0');
  drawer.classList.add('-translate-x-full');
  overlay.classList.add('hidden');
  document.body.style.overflow = '';
  drawerOpen = false;
  if (openBtn) {
    openBtn.setAttribute('aria-expanded', 'false');
    openBtn.focus();
  }

  // Remove focus trap
  if (_trapFocusHandler) {
    document.removeEventListener('keydown', _trapFocusHandler);
    _trapFocusHandler = null;
  }
};

// ---------------------------------------------------------------------------
// Active filter chips
// ---------------------------------------------------------------------------

/**
 * Derive a human-readable label from a URL param name.
 * Strips "filter." prefix and replaces dots/underscores with spaces.
 * @param {string} paramName
 * @returns {string}
 */
const paramToLabel = (paramName) => {
  return paramName
    .replace(/^filter\./i, '')
    .replace(/\./g, ' ')
    .replace(/_/g, ' ');
};

/**
 * Build active filter chips from URLSearchParams and inject into #active-filter-chips.
 * Chip labels and values are XSS-escaped via escapeHtml().
 * @param {URLSearchParams} searchParams
 */
const buildActiveChips = (searchParams) => {
  const container = document.getElementById('active-filter-chips');
  if (!container) return;

  const chips = [];
  searchParams.forEach((value, paramName) => {
    // Only show filter params (skip sort_by, section_id, etc.)
    if (!paramName.startsWith('filter.')) return;
    const label = paramToLabel(paramName) + ': ' + value;
    chips.push(
      `<span class="inline-flex items-center gap-1 bg-sand border border-deep/20 px-2 py-1 font-body text-xs text-deep">` +
        escapeHtml(label) +
        `<button
          aria-label="Remove ${escapeHtml(label)} filter"
          data-remove-param="${escapeHtml(paramName)}"
          data-remove-value="${escapeHtml(value)}"
          class="ml-1 text-mid hover:text-deep"
        >×</button>` +
      `</span>`
    );
  });

  container.innerHTML = chips.join('');
};

// ---------------------------------------------------------------------------
// AJAX grid fetch + DOM swap (mirrors cart-drawer.js fetch pattern)
// ---------------------------------------------------------------------------

/**
 * Fetch the collection page with section_id and swap the product grid innerHTML.
 * Also updates the product count label.
 * @param {string} url - Full URL including ?filter...&section_id=collection-grid
 */
const fetchFilteredGrid = async (url) => {
  try {
    const res = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
    if (!res.ok) throw new Error('Filter fetch failed: ' + res.status);
    const text = await res.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(text, 'text/html');

    const newGrid = doc.querySelector('#product-grid-inner');
    const currentGrid = document.getElementById('product-grid-inner');

    if (newGrid && currentGrid) {
      if (newGrid.children.length === 0) {
        // No products matched — inject the JS no-match message
        currentGrid.innerHTML =
          `<div class="col-span-full py-24 text-center">` +
          `<p class="font-body text-sm text-mid">No products match these filters. Try adjusting or clearing your filters.</p>` +
          `</div>`;
      } else {
        currentGrid.innerHTML = newGrid.innerHTML;
      }
    }

    // Update product count label
    const newCount = doc.querySelector('#product-count');
    const currentCount = document.getElementById('product-count');
    if (newCount && currentCount) {
      currentCount.textContent = newCount.textContent;
    }
  } catch (err) {
    console.error('[collection-filter]', err);
  }
};

// ---------------------------------------------------------------------------
// Read current filter state from the DOM
// ---------------------------------------------------------------------------

/**
 * Collect all checked filter checkboxes and price range inputs.
 * Reads from the desktop sidebar (canonical source); drawer mirrors the same DOM
 * via the Liquid capture, but only the sidebar inputs are used for form reads.
 * @returns {URLSearchParams}
 */
const getFilterParams = () => {
  const params = new URLSearchParams();

  // Checkboxes
  document.querySelectorAll('[data-filter-input]:checked').forEach((input) => {
    params.append(input.name, input.value);
  });

  // Price range
  const minInput = document.querySelector('[data-filter-price-min]');
  const maxInput = document.querySelector('[data-filter-price-max]');
  if (minInput && minInput.value !== '') {
    params.append('filter.v.price.gte', minInput.value);
  }
  if (maxInput && maxInput.value !== '') {
    params.append('filter.v.price.lte', maxInput.value);
  }

  return params;
};

// ---------------------------------------------------------------------------
// Apply filters (read state → build URL → pushState → fetch)
// ---------------------------------------------------------------------------

const applyFilters = () => {
  const params = getFilterParams();

  // Append current sort
  const sortEl = document.getElementById('sort-by');
  if (sortEl && sortEl.value) {
    params.set('sort_by', sortEl.value);
  }

  // Build fetch URL (includes section_id so Shopify returns the section HTML only)
  const fetchParams = new URLSearchParams(params.toString());
  fetchParams.set('section_id', 'collection-grid');
  const fetchUrl = window.location.pathname + '?' + fetchParams.toString();

  // Push clean URL (without section_id) so the address bar stays clean
  const cleanUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
  history.pushState({}, '', cleanUrl);

  // Update active chips from the clean params
  buildActiveChips(params);

  fetchFilteredGrid(fetchUrl);
};

// ---------------------------------------------------------------------------
// Default export: init
// ---------------------------------------------------------------------------

export default function init() {
  document.addEventListener('DOMContentLoaded', () => {
    // --- Drawer open/close ---
    document.getElementById('filter-drawer-open')?.addEventListener('click', openFilterDrawer);
    document.getElementById('filter-drawer-close')?.addEventListener('click', closeFilterDrawer);
    document.getElementById('filter-drawer-overlay')?.addEventListener('click', closeFilterDrawer);

    // "Show Results" in mobile drawer applies filters and closes drawer
    document.getElementById('filter-drawer-apply')?.addEventListener('click', () => {
      applyFilters();
      closeFilterDrawer();
    });

    // Escape key closes drawer
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && drawerOpen) closeFilterDrawer();
    });

    // --- Filter checkbox change (desktop sidebar) ---
    document.querySelectorAll('[data-filter-input]').forEach((input) => {
      input.addEventListener('change', applyFilters);
    });

    // --- Sort change ---
    document.getElementById('sort-by')?.addEventListener('change', applyFilters);

    // --- Clear all ---
    document.getElementById('filter-clear-all')?.addEventListener('click', () => {
      document.querySelectorAll('[data-filter-input]:checked').forEach((cb) => {
        cb.checked = false;
      });
      const minInput = document.querySelector('[data-filter-price-min]');
      const maxInput = document.querySelector('[data-filter-price-max]');
      if (minInput) minInput.value = '';
      if (maxInput) maxInput.value = '';
      applyFilters();
    });

    // --- Active chip removal (event delegation) ---
    document.getElementById('active-filter-chips')?.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-remove-param]');
      if (!btn) return;
      const paramName = btn.dataset.removeParam;
      const paramValue = btn.dataset.removeValue;
      // CSS.escape() prevents injection via data attribute values in querySelector
      const input = document.querySelector(
        `[data-filter-input][name="${CSS.escape(paramName)}"][value="${CSS.escape(paramValue)}"]`
      );
      if (input) {
        input.checked = false;
        applyFilters();
      }
    });

    // --- Hydrate chips on page load (URL may already have filter params) ---
    buildActiveChips(new URLSearchParams(window.location.search));

    // --- Sync sort-by select to current URL param ---
    const currentSort = new URLSearchParams(window.location.search).get('sort_by');
    const sortEl = document.getElementById('sort-by');
    if (sortEl && currentSort) sortEl.value = currentSort;
  });
}

init();
