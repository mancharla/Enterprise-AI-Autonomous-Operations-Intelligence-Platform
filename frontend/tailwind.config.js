/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          950: "#05070d",
          900: "#0a0f1a",
          850: "#0d1422",
          800: "#111827",
          700: "#1e293b",
          600: "#334155",
        },
        accent: {
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        violet: {
          500: "#8b5cf6",
          600: "#7c3aed",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
      },
      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,0.4), 0 8px 24px -8px rgba(0,0,0,0.5)",
        glow: "0 0 0 1px rgba(59,130,246,0.15), 0 8px 30px -8px rgba(37,99,235,0.35)",
      },
    },
  },
  plugins: [],
};
