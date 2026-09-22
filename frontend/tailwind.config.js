/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#05070B',
        surface: {
          50: '#0B1625',
          100: '#091522',
          200: '#07111F',
          300: '#050c17',
          border: 'rgba(30, 58, 102, 0.35)',
          'border-highlight': 'rgba(22, 119, 232, 0.45)',
        },
        brand: {
          dark: '#0F59C5',
          primary: '#1677E8',
          light: '#5DA2F0',
          glow: 'rgba(22, 119, 232, 0.15)',
        },
        text: {
          primary: '#F5F7FA',
          secondary: '#D8DEE8',
          muted: '#9AA6B5',
        },
        risk: {
          low: '#10B981',
          medium: '#F59E0B',
          high: '#F97316',
          critical: '#EF4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'monospace'],
      },
      boxShadow: {
        'cyber': '0 0 25px -5px rgba(22, 119, 232, 0.25)',
        'cyber-lg': '0 0 50px -10px rgba(22, 119, 232, 0.35)',
        'risk-low': '0 0 20px -3px rgba(16, 185, 129, 0.3)',
        'risk-medium': '0 0 20px -3px rgba(245, 158, 11, 0.3)',
        'risk-high': '0 0 20px -3px rgba(249, 115, 22, 0.3)',
        'risk-critical': '0 0 25px -2px rgba(239, 68, 68, 0.4)',
      },
      keyframes: {
        scanline: {
          '0%': { transform: 'translateY(-100%)', opacity: '0.1' },
          '50%': { opacity: '0.8' },
          '100%': { transform: 'translateY(100%)', opacity: '0.1' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '0.3', transform: 'scale(1)' },
          '50%': { opacity: '0.7', transform: 'scale(1.05)' },
        },
        dashDraw: {
          '0%': { strokeDashoffset: '1000' },
          '100%': { strokeDashoffset: '0' },
        }
      },
      animation: {
        'scanline': 'scanline 4s linear infinite',
        'pulse-glow': 'pulseGlow 3s ease-in-out infinite',
        'dash-draw': 'dashDraw 2.5s ease-out forwards',
      }
    },
  },
  plugins: [],
}
