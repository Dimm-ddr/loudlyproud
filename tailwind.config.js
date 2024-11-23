/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./layouts/**/*.html",
    "./content/**/*.md",
    "./data/**/*.json",
    "./assets/**/*.css",
    "./static/**/*.css",
    "./themes/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#000000",
        secondary: "#eee7dc",
        accent1: "#E74C3C",
        accent2: "#2ECC71",
        accent3: "#3498DB",
        background: "#b7b0a7",
        text: "#333333",
        "light-gray": "#eaeaea",
      },
    }
  },
  darkMode: "media",
  plugins: []
}
