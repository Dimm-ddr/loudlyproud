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
        primary: {
          DEFAULT: "#000000", // Light theme text
          dark: "#ffffff",    // Dark theme text
        },
        secondary: {
          DEFAULT: "#eee7dc", // Light theme section bg
          dark: "#2c2420",    // Dark theme section bg
        },
        background: {
          DEFAULT: "#b7b0a7", // Light theme page bg
          dark: "#1a1614",    // Dark theme page bg
        },
        accent1: {
          DEFAULT: "#E74C3C", // Light theme red
          dark: "#ff6b5b",    // Dark theme red
        },
        accent2: {
          DEFAULT: "#2ECC71", // Light theme green
          dark: "#4ade80",    // Dark theme green
        },
        accent3: {
          DEFAULT: "#3498DB", // Light theme blue
          dark: "#60a5fa",    // Dark theme blue
        },
        text: {
          DEFAULT: "#333333", // Light theme text
          dark: "#ffffff",    // Dark theme text
        },
        "light-gray": {
          DEFAULT: "#eaeaea",
          dark: "#4a4a4a",
        },
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
