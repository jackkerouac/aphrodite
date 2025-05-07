import { fontFamily } from "tailwindcss/defaultTheme";

export default {
  content: [
    "./src/**/*.{ts,tsx,js,jsx}",
    "./components/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary Colors
        primary: {
          white: '#FDFDFD',
          purple: '#4C1D95',
        },
        // Secondary Colors
        secondary: {
          purple: '#7C3AED',
          lilac: '#EDE9FE',
        },
        // Accent Colors
        accent: {
          indigo: '#8B5CF6',
          cyan: '#06B6D4',
        },
        // Functional Colors
        success: '#22C55E',
        warning: '#F59E0B',
        error: '#EF4444',
        neutral: '#9CA3AF',
        dark: '#1F2937',
        // Background Colors
        bg: {
          white: '#FFFFFF',
          light: '#F4F4F5',
          dark: '#1E1B2E',
        },
      },
      borderRadius: {
        DEFAULT: "8px",
        lg: "12px",
      },
      fontFamily: {
        sans: ["Inter", ...fontFamily.sans],
        mono: ["JetBrains Mono", ...fontFamily.mono],
      },
      fontSize: {
        'h1': ['30px', {
          lineHeight: '36px',
          fontWeight: '700',
        }],
        'h2': ['24px', {
          lineHeight: '32px',
          fontWeight: '600',
        }],
        'h3': ['20px', {
          lineHeight: '28px',
          fontWeight: '500',
        }],
        'body-large': ['16px', {
          lineHeight: '24px',
          fontWeight: '400',
        }],
        'body': ['14px', {
          lineHeight: '20px',
          fontWeight: '400',
        }],
        'body-small': ['12px', {
          lineHeight: '18px',
          fontWeight: '500',
        }],
        'code': ['13px', {
          lineHeight: '18px',
          fontWeight: '500',
        }],
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
