import { fontFamily } from "tailwindcss/defaultTheme";

export default {
  content: [
    "./src/**/*.{ts,tsx,js,jsx}",
    "./components/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#4C1D95",
        primaryHover: "#7C3AED",
        secondary: "#EDE9FE",
        accent: "#8B5CF6",
        cyanEdge: "#06B6D4",
        success: "#22C55E",
        warning: "#F59E0B",
        error: "#EF4444",
        neutral: "#9CA3AF",
        darkText: "#1F2937",
        bgLight: "#F4F4F5",
        bgDark: "#1E1B2E",
      },
      borderRadius: {
        DEFAULT: "8px",
        lg: "12px",
      },
      fontFamily: {
        sans: ["Inter", ...fontFamily.sans],
        mono: ["JetBrains Mono", ...fontFamily.mono],
      },
      boxShadow: {
        card: "0 2px 8px rgba(76, 29, 149, 0.08)",
      },
      transitionTimingFunction: {
        spring: "cubic-bezier(0.2, 0.8, 0.2, 1)",
      },
      height: {
        input: "48px",
      },
      spacing: {
        micro: "4px",
        small: "8px",
        default: "16px",
        section: "24px",
        page: "32px",
        modal: "40px",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
  darkMode: "class",
};
