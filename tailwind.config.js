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
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#000000",
          dark: "#ffffff",
        },
        secondary: {
          DEFAULT: "#eee7dc",
          dark: "#2d2d2d",
        },
        accent1: {
          DEFAULT: "#E74C3C",
          dark: "#ff6b5d",
        },
        accent2: {
          DEFAULT: "#2ECC71",
          dark: "#4fdd91",
        },
        accent3: {
          DEFAULT: "#3498DB",
          dark: "#5dafec",
        },
        background: {
          DEFAULT: "#b7b0a7",
          dark: "#1a1a1a",
        },
        text: {
          DEFAULT: "#333333",
          dark: "#e5e5e5",
        },
        "light-gray": {
          DEFAULT: "#eaeaea",
          dark: "#404040",
        },
        // Tag colors - using Tailwind's default color values for consistency
        tag: {
          amber: {
            light: {
              DEFAULT: "#f59e0b", // amber-500
              hover: "#fbbf24", // amber-400
            },
            dark: {
              DEFAULT: "#fbbf24", // amber-400
              hover: "#fcd34d", // amber-300
            },
          },
          aubergine: {
            light: {
              DEFAULT: "#581c87", // purple-900
              hover: "#6b21a8", // purple-800
            },
            dark: {
              DEFAULT: "#a855f7", // purple-400
              hover: "#d8b4fe", // purple-300
            },
          },
          burgundy: {
            light: {
              DEFAULT: "#991b1b", // red-800
              hover: "#b91c1c", // red-700
            },
            dark: {
              DEFAULT: "#f87171", // red-400
              hover: "#fca5a5", // red-300
            },
          },
          "deep-blue": {
            light: {
              DEFAULT: "#1e3a8a", // blue-900
              hover: "#1e40af", // blue-800
            },
            dark: {
              DEFAULT: "#60a5fa", // blue-400
              hover: "#93c5fd", // blue-300
            },
          },
          forest: {
            light: {
              DEFAULT: "#166534", // green-800
              hover: "#15803d", // green-700
            },
            dark: {
              DEFAULT: "#4ade80", // green-400
              hover: "#86efac", // green-300
            },
          },
          marine: {
            light: {
              DEFAULT: "#155e75", // cyan-800
              hover: "#0e7490", // cyan-700
            },
            dark: {
              DEFAULT: "#22d3ee", // cyan-400
              hover: "#67e8f9", // cyan-300
            },
          },
          plum: {
            light: {
              DEFAULT: "#86198f", // fuchsia-800
              hover: "#a21caf", // fuchsia-700
            },
            dark: {
              DEFAULT: "#e879f9", // fuchsia-400
              hover: "#f0abfc", // fuchsia-300
            },
          },
          rust: {
            light: {
              DEFAULT: "#c2410c", // orange-700
              hover: "#ea580c", // orange-600
            },
            dark: {
              DEFAULT: "#fb923c", // orange-400
              hover: "#fdba74", // orange-300
            },
          },
          slate: {
            light: {
              DEFAULT: "#334155", // slate-700
              hover: "#475569", // slate-600
            },
            dark: {
              DEFAULT: "#94a3b8", // slate-400
              hover: "#cbd5e1", // slate-300
            },
          },
          fallback: {
            light: {
              DEFAULT: "#9ca3af", // gray-400
              hover: "#d1d5db", // gray-300
            },
            dark: {
              DEFAULT: "#4b5563", // gray-600
              hover: "#6b7280", // gray-500
            },
          },
        },
      },
    },
  },
  plugins: [],
};
