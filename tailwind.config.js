/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "media",
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
      fontFamily: {
        sans: ["Lato", "sans-serif"],
      },
      colors: {
        primary: "#000000", // Primary text color
        secondary: "#eee7dc", // Secondary (background) color
        accent1: "#E74C3C", // Accent color (red)
        accent2: "#2ECC71", // Accent color (green)
        accent3: "#3498DB", // Accent color (blue)
        background: "#b7b0a7", // General background color
        text: "#333333", // Text color
        "light-gray": "#eaeaea", // Light gray for borders, etc.
      },
      spacing: {
        hero: "4rem", // Spacing for hero sections
        "footer-padding": "2rem", // Footer padding
      },
      container: {
        center: true, // Ensure containers are centered
        padding: "1rem", // Default padding for containers
      },
    },
  },
  plugins: [],
};
