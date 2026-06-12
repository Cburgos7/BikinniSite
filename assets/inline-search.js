let searchOpen = false;

const openSearch = (navLinks, searchBar, input) => {
  searchOpen = true;
  navLinks.classList.add('opacity-0', 'pointer-events-none');
  searchBar.classList.remove('hidden', 'opacity-0', 'pointer-events-none');
  searchBar.classList.add('opacity-100');
  input.value = '';
  input.focus();
};

const closeSearch = (navLinks, searchBar, toggle) => {
  searchOpen = false;
  searchBar.classList.add('opacity-0', 'pointer-events-none');
  searchBar.classList.remove('opacity-100');
  // Delay hiding to allow fade-out transition
  setTimeout(() => {
    if (!searchOpen) searchBar.classList.add('hidden');
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

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const query = encodeURIComponent(input.value.trim());
        if (query) {
          window.location.href = `/search?q=${query}`;
        }
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
