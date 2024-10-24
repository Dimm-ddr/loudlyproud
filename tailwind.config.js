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
        sans: [
          "Lato",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],
        sm: ["0.875rem", { lineHeight: "1.25rem" }],
        base: ["1rem", { lineHeight: "1.5rem" }],
        lg: ["1.125rem", { lineHeight: "1.75rem" }],
        xl: ["1.25rem", { lineHeight: "1.75rem" }],
        "2xl": ["1.5rem", { lineHeight: "2rem" }],
        "3xl": ["1.875rem", { lineHeight: "2.25rem" }],
        "4xl": ["2.25rem", { lineHeight: "2.5rem" }],
      },
      fontWeight: {
        thin: 100,
        light: 300,
        normal: 400,
        bold: 700,
        black: 900,
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
