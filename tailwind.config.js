/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './layout/**/*.liquid',
    './sections/**/*.liquid',
    './snippets/**/*.liquid',
    './templates/**/*.liquid',
    './templates/customers/**/*.liquid',
  ],
  theme: {
    extend: {
      colors: {
        sand:  '#f5ede0',
        deep:  '#0d0a08',
        coral: '#e85d3a',
        gold:  '#c9a84c',
        cream: '#faf6f0',
        mid:   '#8a7060',
      },
      fontFamily: {
        display: ['Cormorant Garamond', 'Georgia', 'serif'],
        body:    ['Barlow Condensed', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
