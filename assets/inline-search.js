let searchOpen = false;

/**
 * The bar used to carry `hidden lg:flex`, so removing `hidden` below 1024px
 * left it at display:none and the toggle appeared to do nothing. It now carries
 * `hidden` alone and gets `flex` applied here, which makes it visible at every
 * width. Both classes have to move together or the desktop layout collapses.
 */
const openSearch = (navLinks, searchBar, input) => {
  searchOpen = true;
  navLinks.classList.add('opacity-0', 'pointer-events-none');
  searchBar.classList.remove('hidden', 'opacity-0', 'pointer-events-none');
  searchBar.classList.add('flex', 'opacity-100');
  input.value = '';
  input.focus();
};

const closeSearch = (navLinks, searchBar, toggle) => {
  searchOpen = false;
  searchBar.classList.add('opacity-0', 'pointer-events-none');
  searchBar.classList.remove('opacity-100');
  // Delay hiding to allow fade-out transition
  setTimeout(() => {
    if (!searchOpen) {
      searchBar.classList.add('hidden');
      searchBar.classList.remove('flex');
    }
  }, 200);
  navLinks.classList.remove('opacity-0', 'pointer-events-none');
  toggle.focus();
};

export default function init() {
  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('nav-search-toggle');
    const searchBar = document.getElementById('nav-search-bar');
    const closeBtn = document.getElementById('nav-search-close');
    const navLinks = document.getElementById('nav-links');
    const input = document.getElementById('nav-search-input');

    if (!toggle || !searchBar || !closeBtn || !navLinks || !input) return;

    toggle.addEventListener('click', () => openSearch(navLinks, searchBar, input));
    closeBtn.addEventListener('click', () => closeSearch(navLinks, searchBar, toggle));

    // #nav-search-bar is a GET form pointed at /search, so Enter and a phone
    // keyboard's "Search" key both submit natively. All that is left to do is
    // refuse an empty query, which would otherwise land on a bare results page.
    searchBar.addEventListener('submit', (e) => {
      if (!input.value.trim()) {
        e.preventDefault();
        input.focus();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && searchOpen) {
        closeSearch(navLinks, searchBar, toggle);
      }
    });
  });
}

init();
