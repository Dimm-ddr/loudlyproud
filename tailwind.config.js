/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './layouts/**/*.html',
    './content/**/*.{html,md}'
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#1a1a1a',
        'secondary': '#ffffff',
        'accent1': '#4338ca',
        'accent2': '#0d9488',
        'accent3': '#2563eb',
        'light-gray': '#e5e7eb'
      }
    }
  },
  darkMode: 'class',
  plugins: []
}
