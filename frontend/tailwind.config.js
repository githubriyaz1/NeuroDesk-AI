/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#09090b',
          subtle: '#121215',
          card: '#18181b',
          elevated: '#27272a',
        },
        border: {
          DEFAULT: 'rgba(255, 255, 255, 0.08)',
          subtle: 'rgba(255, 255, 255, 0.05)',
          strong: 'rgba(255, 255, 255, 0.16)',
        },
        accent: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
          muted: 'rgba(99, 102, 241, 0.15)',
        },
        emerald: {
          muted: 'rgba(16, 185, 129, 0.15)',
        },
        slate: {
          850: '#141c2e',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['Fira Code', 'JetBrains Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'glass': '0 4px 30px rgba(0, 0, 0, 0.5)',
        'glow': '0 0 20px rgba(99, 102, 241, 0.15)',
      }
    },
  },
  plugins: [],
}
